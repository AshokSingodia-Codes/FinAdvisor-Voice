"""
setup_neo4j_personal_index.py
-------------------------------
Creates the Neo4j vector index and constraints required for personal document
chunk storage and retrieval (PersonalChunk nodes).

Run once after initial Neo4j Aura setup, or whenever you recreate the database:

    python setup_neo4j_personal_index.py

Safe to re-run — all operations use IF NOT EXISTS.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

# ── Detect embedding dimensions ────────────────────────────────────────────
# FastEmbed "sentence-transformers/all-MiniLM-L6-v2" → 384 dims
# HuggingFaceEmbeddings  "all-MiniLM-L6-v2"          → 384 dims
EMBEDDING_DIM = 384

def main():
    print("\n=============================================")
    print("  FinAdvisor-X — Neo4j Personal Index Setup  ")
    print("=============================================\n")

    try:
        from core.db import kg
    except Exception as e:
        print(f"[ERROR] Could not connect to Neo4j: {e}")
        print("  Make sure NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD are set in .env")
        sys.exit(1)

    steps = [
        # ── Uniqueness constraint (prevents duplicate chunks) ──────────────
        (
            "PersonalChunk unique constraint",
            """
            CREATE CONSTRAINT personalchunk_unique IF NOT EXISTS
            FOR (c:PersonalChunk)
            REQUIRE (c.user_id, c.document_id, c.conversation_id, c.chunk_index)
            IS NODE KEY
            """
        ),
        # ── Lookup indexes for the 3-field isolation filter ────────────────
        (
            "PersonalChunk isolation composite index",
            """
            CREATE INDEX personalchunk_isolation IF NOT EXISTS
            FOR (c:PersonalChunk)
            ON (c.user_id, c.document_id, c.conversation_id)
            """
        ),
        (
            "PersonalChunk document_id index",
            """
            CREATE INDEX personalchunk_docid IF NOT EXISTS
            FOR (c:PersonalChunk)
            ON (c.document_id)
            """
        ),
        # ── Vector index (Neo4j 5.x native vector index) ──────────────────
        # Used by db.index.vector.queryNodes() for approximate nearest-neighbour.
        # Falls back to brute-force cosine similarity if this doesn't exist.
        (
            "PersonalChunk vector index",
            f"""
            CREATE VECTOR INDEX personalchunk_vector IF NOT EXISTS
            FOR (c:PersonalChunk)
            ON c.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {EMBEDDING_DIM},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """
        ),
        # ── Full-text index for keyword search ─────────────────────────────
        (
            "PersonalChunk fulltext index",
            """
            CREATE FULLTEXT INDEX personalchunk_fulltext IF NOT EXISTS
            FOR (c:PersonalChunk)
            ON EACH [c.text]
            """
        ),
    ]

    ok = 0
    for label, cypher in steps:
        try:
            kg.query(cypher)
            print(f"  [OK]  {label}")
            ok += 1
        except Exception as e:
            err = str(e)
            if "already exists" in err.lower() or "equivalent" in err.lower():
                print(f"  [--]  {label} (already exists, skipped)")
                ok += 1
            else:
                print(f"  [ERR] {label}: {err}")

    # ── Verify ─────────────────────────────────────────────────────────────
    print("\n  Verifying indexes in Neo4j...")
    try:
        results = kg.query("SHOW INDEXES YIELD name, type, state WHERE name STARTS WITH 'personalchunk'")
        if results:
            for r in results:
                status = "ONLINE" if r.get("state") == "ONLINE" else r.get("state", "?")
                print(f"    {r['name']:40s} ({r['type']:12s}) [{status}]")
        else:
            print("    (no personalchunk indexes found — check Neo4j version compatibility)")
    except Exception as e:
        print(f"    Could not verify indexes: {e}")

    print(f"\n  {ok}/{len(steps)} steps completed.")
    print("  Neo4j PersonalChunk index setup done.\n")
    print("  You can now start the server:  python main.py")
    print("  Or run tests:                  pytest tests/ -v\n")

if __name__ == "__main__":
    main()
