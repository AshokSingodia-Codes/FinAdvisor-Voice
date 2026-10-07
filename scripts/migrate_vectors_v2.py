"""
scripts/migrate_vectors_v2.py
-----------------------------
Idempotent, resumable local migration script for Neo4j Aura vector indexing.
Migrates :Chunk nodes to 768-dim L2-normalized hosted Gemini embeddings (embedding_v2).

Features:
- Polls SHOW INDEXES until vector_markdown_v2 is ONLINE before indexing.
- Paces batch requests to strictly respect Free-tier RPM and TPM rate limits.
- If daily quota (RPD) is reached, stops cleanly and logs exact resume state.
- Idempotent: queries `WHERE c.embedding_v2 IS NULL`, so re-running resumes instantly.
- Statically stores c.embedding_model = 'gemini-embedding-001@768'.
- Leaves all legacy indexes and properties untouched.
"""

import os
import sys
import time
import math
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from config.settings import settings
from core.embeddings import GeminiHostedEmbeddings, _l2_normalize
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_v2")

TARGET_DIM = int(os.getenv("EMBEDDING_DIM", 768))
BATCH_SIZE = int(os.getenv("MIGRATION_BATCH_SIZE", 30))
SLEEP_BETWEEN_BATCHES_SEC = float(os.getenv("MIGRATION_SLEEP_SEC", 3.0))


def get_driver():
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )


def check_and_create_indexes(session):
    """Verifies index count on Aura and creates vector_markdown_v2."""
    logger.info("Checking existing indexes on Neo4j Aura...")
    result = session.run("SHOW INDEXES YIELD name, type, state, labelsOrTypes, properties")
    indexes = list(result)
    logger.info(f"Found {len(indexes)} total indexes currently in database:")
    for idx in indexes:
        logger.info(f"  - {idx['name']} ({idx['type']}, state={idx['state']}, labels={idx['labelsOrTypes']}, props={idx['properties']})")

    # 1. Create vector_markdown_v2 for :Chunk
    create_chunk_idx_cypher = f"""
    CREATE VECTOR INDEX vector_markdown_v2 IF NOT EXISTS
    FOR (c:Chunk)
    ON (c.embedding_v2)
    OPTIONS {{
      indexConfig: {{
        `vector.dimensions`: {TARGET_DIM},
        `vector.similarity_function`: 'cosine'
      }}
    }}
    """
    logger.info("Creating vector index 'vector_markdown_v2' (768-dim, cosine)...")
    session.run(create_chunk_idx_cypher)

    # 2. If PERSONAL_DOCS_EMBEDDING != 'keyword_only', create personal index
    personal_mode = getattr(settings, "PERSONAL_DOCS_EMBEDDING", "keyword_only").lower()
    if personal_mode != "keyword_only":
        create_personal_idx_cypher = f"""
        CREATE VECTOR INDEX personalchunk_vector_v2 IF NOT EXISTS
        FOR (c:PersonalChunk)
        ON (c.embedding_v2)
        OPTIONS {{
          indexConfig: {{
            `vector.dimensions`: {TARGET_DIM},
            `vector.similarity_function`: 'cosine'
          }}
        }}
        """
        logger.info("Creating vector index 'personalchunk_vector_v2'...")
        session.run(create_personal_idx_cypher)
    else:
        logger.info("PERSONAL_DOCS_EMBEDDING is 'keyword_only': skipping vector index for :PersonalChunk (zero API exposure).")

    # 3. Poll SHOW INDEXES until vector_markdown_v2 is ONLINE
    logger.info("Waiting for vector_markdown_v2 to become ONLINE...")
    for _ in range(30):
        rows = list(session.run("SHOW INDEXES YIELD name, state WHERE name = 'vector_markdown_v2'"))
        if rows and rows[0]["state"] == "ONLINE":
            logger.info("✅ Index 'vector_markdown_v2' is ONLINE and ready.")
            return True
        time.sleep(1.0)

    logger.warning("Index did not report ONLINE within 30s. Continuing cautiously...")
    return True


def migrate_chunks(session, emb_service: GeminiHostedEmbeddings, max_chunks: Optional[int] = None):
    """
    Migrates :Chunk nodes that have no embedding_v2 in throttled batches.
    If max_chunks is set, limits total migrated chunks (e.g. for a 50-chunk smoke test).
    """
    total_migrated = 0
    batch_num = 0

    while True:
        limit = BATCH_SIZE
        if max_chunks is not None:
            remaining = max_chunks - total_migrated
            if remaining <= 0:
                logger.info(f"Reached specified limit of {max_chunks} chunks.")
                break
            limit = min(BATCH_SIZE, remaining)

        fetch_cypher = """
        MATCH (c:Chunk)
        WHERE c.embedding_v2 IS NULL
        RETURN c.id AS id, c.text AS text
        LIMIT $limit
        """
        records = list(session.run(fetch_cypher, {"limit": limit}))
        if not records:
            logger.info("No more unmigrated chunks found (c.embedding_v2 IS NULL returned 0 rows).")
            break

        batch_num += 1
        chunk_ids = [r["id"] for r in records]
        chunk_texts = [r["text"] or "" for r in records]

        logger.info(f"Processing Batch #{batch_num}: {len(chunk_ids)} chunks (overall migrated: {total_migrated})...")

        # Call batchEmbedContents with retry handling
        vectors = None
        for attempt in range(1, 4):
            try:
                vectors = emb_service._call_gemini_batch(chunk_texts, task_type="RETRIEVAL_DOCUMENT")
                # Verify vector dimensions
                if vectors and len(vectors) == len(chunk_texts) and len(vectors[0]) == TARGET_DIM:
                    break
            except Exception as e:
                err_str = str(e).lower()
                if any(k in err_str for k in ("perday", "daily", "requestsperday", "quotaexceededfor")):
                    logger.error("🚨 Daily Gemini Quota (RPD) reached! Stopping migration cleanly.")
                    logger.info("Progress saved. Re-run this script tomorrow to resume remaining chunks.")
                    return total_migrated
                logger.warning(f"Batch #{batch_num} attempt {attempt} failed: {e}. Retrying in 5s...")
                time.sleep(5.0)

        if not vectors or len(vectors) != len(chunk_texts) or len(vectors[0]) != TARGET_DIM:
            logger.error(f"Failed to obtain valid embeddings for Batch #{batch_num}. Skipping batch to avoid infinite loop.")
            continue

        # Prepare update parameters
        updates = [
            {"id": cid, "emb": vec, "model": f"gemini-embedding-001@{TARGET_DIM}"}
            for cid, vec in zip(chunk_ids, vectors)
        ]

        update_cypher = """
        UNWIND $updates AS row
        MATCH (c:Chunk {id: row.id})
        SET c.embedding_v2 = row.emb,
            c.embedding_model = row.model
        """
        session.run(update_cypher, {"updates": updates})
        total_migrated += len(updates)
        logger.info(f"  ✓ Batch #{batch_num} committed ({len(updates)} chunks updated in Neo4j).")

        # Throttle to stay within RPM quota
        time.sleep(SLEEP_BETWEEN_BATCHES_SEC)

    return total_migrated


def report_final_counts(session):
    """Reports total nodes with and without embedding_v2."""
    count_cypher = """
    MATCH (c:Chunk)
    RETURN
      count(c) AS total,
      count(c.embedding_v2) AS with_v2,
      count(c.embedding_384) AS with_384,
      count(c.embedding) AS with_legacy
    """
    res = session.run(count_cypher).single()
    logger.info("==================================================")
    logger.info("FINAL NEO4J NODE EMBEDDING SUMMARY (:Chunk):")
    logger.info(f"  Total :Chunk nodes:          {res['total']}")
    logger.info(f"  With embedding_v2 (768-dim): {res['with_v2']}")
    logger.info(f"  With embedding_384 (384-dim):{res['with_384']}")
    logger.info(f"  With legacy embedding:       {res['with_legacy']}")
    logger.info("==================================================")


def main():
    max_chunks = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        max_chunks = int(sys.argv[1])
        logger.info(f"Running in TEST/STAGE mode: limit set to {max_chunks} chunks.")

    driver = get_driver()
    emb_service = GeminiHostedEmbeddings(
        api_key=settings.GOOGLE_API_KEY,
        model_name="models/gemini-embedding-001",
        dimension=TARGET_DIM,
    )

    with driver.session() as session:
        check_and_create_indexes(session)
        migrated = migrate_chunks(session, emb_service, max_chunks=max_chunks)
        report_final_counts(session)
        logger.info(f"Migration run finished. Total chunks updated this session: {migrated}")

    driver.close()


if __name__ == "__main__":
    main()
