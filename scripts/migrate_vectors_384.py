"""
scripts/migrate_vectors_384.py
------------------------------
Safe, idempotent, and resumable vector migration script (768-dim -> 384-dim).
Creates side-by-side vector indexes:
  - vector_markdown_384 (on Chunk.embedding_384)
  - personalchunk_vector_384 (on PersonalChunk.embedding_384)
Backfills embedding_384 in batches of 50 without modifying existing embedding properties.
Includes retry logic (max 3 retries per batch) and polls SHOW INDEXES until ONLINE.
"""

import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from core.embeddings import get_embeddings_service
from neo4j import GraphDatabase


def wait_for_indexes_online(session, index_names, timeout_sec=120):
    """Polls SHOW INDEXES until all specified indexes are in ONLINE state."""
    print(f"\n⏳ Polling index status for: {index_names}...")
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        records = session.run("SHOW INDEXES YIELD name, state, type").data()
        index_map = {r["name"]: r["state"] for r in records}
        
        all_online = True
        for name in index_names:
            state = index_map.get(name, "NOT_FOUND")
            if state != "ONLINE":
                all_online = False
                break
                
        if all_online:
            print(f"✅ All target vector indexes are ONLINE! ({time.time() - start_time:.1f}s)")
            return True
        time.sleep(2)
        
    print(f"⚠️ Warning: Timeout reached waiting for indexes {index_names} to become ONLINE.")
    return False


def migrate_label(session, emb_service, label="Chunk", batch_size=50):
    """
    Idempotent batch backfill for a given node label.
    Queries nodes where embedding_384 IS NULL and text IS NOT NULL.
    Stops when 0 rows remain. Retries failed batches up to 3 times.
    """
    print(f"\n=======================================================")
    print(f"  Starting 384-dim Vector Migration for (:{label})")
    print(f"=======================================================")

    # Initial count
    init_stats = session.run(f"""
        MATCH (c:{label})
        RETURN 
            count(c) AS total,
            count(c.embedding_384) AS done_384,
            count(c) - count(c.embedding_384) AS pending
    """).single()
    
    total = init_stats["total"]
    done_384 = init_stats["done_384"]
    pending = init_stats["pending"]
    print(f"Node Stats for (:{label}): Total={total}, Already 384-dim={done_384}, Pending={pending}")

    if pending == 0:
        print(f"🎉 All {total} (:{label}) nodes already have embedding_384. Skipping backfill.")
        return

    processed = 0
    skipped_ids = []
    
    # Query to fetch next pending batch
    fetch_query = f"""
        MATCH (c:{label})
        WHERE c.text IS NOT NULL AND c.embedding_384 IS NULL
        RETURN elementId(c) AS id, c.text AS text
        LIMIT $batch_size
    """

    # Query to apply embeddings
    update_query = f"""
        UNWIND $batch AS item
        MATCH (c) WHERE elementId(c) = item.id
        SET c.embedding_384 = item.vector
    """

    while True:
        # Exclude skipped_ids if any
        if skipped_ids:
            batch_records = session.run(f"""
                MATCH (c:{label})
                WHERE c.text IS NOT NULL AND c.embedding_384 IS NULL AND NOT elementId(c) IN $skipped
                RETURN elementId(c) AS id, c.text AS text
                LIMIT $batch_size
            """, {"batch_size": batch_size, "skipped": skipped_ids}).data()
        else:
            batch_records = session.run(fetch_query, {"batch_size": batch_size}).data()

        if not batch_records:
            print(f"🏁 Completed (:{label}) migration! No more pending rows.")
            break

        batch_ids = [r["id"] for r in batch_records]
        batch_texts = [r["text"] for r in batch_records]

        success = False
        for attempt in range(1, 4):
            try:
                # Generate embeddings in single ONNX batch
                vectors = emb_service.embed_documents(batch_texts)
                
                # Format payload
                update_payload = [{"id": bid, "vector": vec} for bid, vec in zip(batch_ids, vectors)]
                
                # Write to Neo4j
                session.run(update_query, {"batch": update_payload})
                processed += len(batch_records)
                print(f"  [Progress] Migrated {processed}/{pending} nodes (Batch size: {len(batch_records)})...")
                success = True
                break
            except Exception as e:
                print(f"  ⚠️ [Attempt {attempt}/3] Error on batch: {e}")
                time.sleep(1)

        if not success:
            print(f"  ❌ Skipping failed batch after 3 attempts. Node IDs: {batch_ids}")
            skipped_ids.extend(batch_ids)

    print(f"Finished processing (:{label}). Total successfully updated this run: {processed}.")


def main():
    print("\n=======================================================")
    print("  FinAdvisor-X — 384-dim Vector Migration & Index Setup")
    print("=======================================================\n")

    emb_service = get_embeddings_service()
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )

    with driver.session(database=settings.NEO4J_USERNAME) as session:
        # 1. Create side-by-side 384-dim vector indexes
        print("1. Creating side-by-side 384-dim vector indexes...")
        
        session.run("""
            CREATE VECTOR INDEX vector_markdown_384 IF NOT EXISTS
            FOR (c:Chunk)
            ON c.embedding_384
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }
            }
        """)
        print("  - vector_markdown_384: CREATED / VERIFIED")

        session.run("""
            CREATE VECTOR INDEX personalchunk_vector_384 IF NOT EXISTS
            FOR (c:PersonalChunk)
            ON c.embedding_384
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }
            }
        """)
        print("  - personalchunk_vector_384: CREATED / VERIFIED")

        # 2. Wait for indexes to become ONLINE
        wait_for_indexes_online(session, ["vector_markdown_384", "personalchunk_vector_384"])

        # 3. Migrate :Chunk nodes (2,872 nodes)
        migrate_label(session, emb_service, label="Chunk", batch_size=50)

        # 4. Migrate :PersonalChunk nodes (18 nodes)
        migrate_label(session, emb_service, label="PersonalChunk", batch_size=50)

        # 5. Final verification & count reporting
        print("\n=======================================================")
        print("  FINAL DATABASE VERIFICATION & AUDIT REPORT")
        print("=======================================================")
        
        for label in ["Chunk", "PersonalChunk"]:
            stats = session.run(f"""
                MATCH (c:{label})
                RETURN 
                    count(c) AS total,
                    count(c.embedding_384) AS with_384,
                    count(c.embedding) AS with_768,
                    count(c) - count(c.embedding_384) AS missing_384
            """).single()
            print(f"\nLabel (:{label}):")
            print(f"  - Total Nodes:            {stats['total']}")
            print(f"  - With embedding_384:     {stats['with_384']} (384-dim)")
            print(f"  - With legacy embedding:  {stats['with_768']} (768-dim, preserved)")
            print(f"  - Missing embedding_384:  {stats['missing_384']}")

        print("\nIndex Status in Neo4j Aura:")
        idx_records = session.run("SHOW INDEXES YIELD name, type, properties, state").data()
        for idx in idx_records:
            print(f"  - {idx['name']:28s} | {idx['type']:8s} | {str(idx['properties']):20s} | {idx['state']}")

    driver.close()
    print("\n✅ 384-dim Vector Migration complete!\n")


if __name__ == "__main__":
    main()
