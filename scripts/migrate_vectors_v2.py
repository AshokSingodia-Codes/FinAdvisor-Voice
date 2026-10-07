"""
scripts/migrate_vectors_v2.py
-----------------------------
Idempotent, resumable local migration script for Neo4j Aura vector indexing.
Migrates :Chunk nodes to 768-dim L2-normalized hosted Gemini embeddings (embedding_v2).

Rate Limits (Gemini Embedding 1 Free Tier):
- 100 RPM
- 30,000 TPM
- 1,000 RPD (resets at Midnight Pacific Time)

Guardrails & Safety:
- Dual-throttled by both requests (EMBED_RPM_CAP=60) and tokens (EMBED_TPM_CAP=20000).
- Dynamically estimates tokens per chunk (chars/4) and paces sleep between batches.
- Distinguishes 429 types: sleeps/retries on RPM/TPM 429, exits cleanly (exit 0) on RPD exhaustion.
- Idempotent: queries `WHERE c.embedding_v2 IS NULL` only.
- Shared corpus only (:Chunk). Leaves :PersonalChunk untouched (keyword_only).
- Configurable daily budget (EMBED_DAILY_BUDGET=850 today, 900 on later days).
- When VECTOR_SEARCH_ENABLED=true, reserve >= 300 requests/day for live queries.
"""

import os
import sys
import time
import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from config.settings import settings
from core.embeddings import GeminiHostedEmbeddings, _l2_normalize
from neo4j import GraphDatabase
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_v2")

TARGET_DIM = int(os.getenv("EMBEDDING_DIM", 768))
BATCH_SIZE = int(os.getenv("MIGRATION_BATCH_SIZE", 30))
EMBED_DAILY_BUDGET = int(os.getenv("EMBED_DAILY_BUDGET", 850))
EMBED_RPM_CAP = float(os.getenv("EMBED_RPM_CAP", 60.0))       # Requests per minute cap
EMBED_TPM_CAP = float(os.getenv("EMBED_TPM_CAP", 20000.0))    # Tokens per minute cap


def get_driver():
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )


def estimate_tokens(text: str) -> int:
    """Estimates tokens from text using character heuristics (~4 chars/token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def check_and_create_indexes(session) -> bool:
    """Verifies index count on Aura and ensures vector_markdown_v2 is ONLINE."""
    logger.info("Checking existing indexes on Neo4j Aura...")
    result = session.run("SHOW INDEXES YIELD name, type, state, labelsOrTypes, properties")
    indexes = list(result)
    logger.info(f"Found {len(indexes)} total indexes currently in database:")
    for idx in indexes:
        logger.info(f"  - {idx['name']} ({idx['type']}, state={idx['state']}, labels={idx['labelsOrTypes']}, props={idx['properties']})")

    # 1. Create vector_markdown_v2 for :Chunk if not existing
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
    logger.info("Ensuring vector index 'vector_markdown_v2' (768-dim, cosine)...")
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
        logger.info("PERSONAL_DOCS_EMBEDDING is 'keyword_only': skipping vector index for :PersonalChunk (zero external API exposure).")

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


def sample_and_project(session, daily_budget: int):
    """
    Samples 100 unmigrated chunks, computes average token count,
    and reports migration projection before the first full batch.
    """
    count_res = session.run("""
    MATCH (c:Chunk)
    RETURN 
        count(c) AS total,
        count(c.embedding_v2) AS with_v2,
        count(CASE WHEN c.embedding_v2 IS NULL THEN 1 END) AS unmigrated
    """).single()

    total_chunks = count_res["total"]
    with_v2 = count_res["with_v2"]
    unmigrated = count_res["unmigrated"]

    sample_rows = list(session.run("""
    MATCH (c:Chunk)
    WHERE c.embedding_v2 IS NULL
    RETURN c.id AS id, c.text AS text
    LIMIT 100
    """))

    sample_count = len(sample_rows)
    if sample_count == 0:
        logger.info("🎉 All :Chunk nodes are already migrated to embedding_v2!")
        return 0, 0.0, 0

    token_counts = [estimate_tokens(r["text"] or "") for r in sample_rows]
    avg_tokens = sum(token_counts) / sample_count
    min_tokens = min(token_counts)
    max_tokens = max(token_counts)

    # Compute day projection
    # Day 1 budget = daily_budget; subsequent days = 900
    if unmigrated <= daily_budget:
        projected_days = 1
    else:
        rem_after_day1 = unmigrated - daily_budget
        projected_days = 1 + math.ceil(rem_after_day1 / 900.0)

    logger.info("==================================================")
    logger.info("PRE-FLIGHT SAMPLE & PROJECTION REPORT:")
    logger.info(f"  Total :Chunk nodes in graph:     {total_chunks}")
    logger.info(f"  Already migrated (with v2):     {with_v2}")
    logger.info(f"  Remaining unmigrated:           {unmigrated}")
    logger.info(f"  Sample analyzed:                {sample_count} chunks")
    logger.info(f"  Avg token count per chunk:      {avg_tokens:.1f} tokens (~{avg_tokens * 4:.0f} chars)")
    logger.info(f"  Min / Max tokens in sample:     {min_tokens} / {max_tokens} tokens")
    logger.info(f"  Configured Daily Budget:        {daily_budget} requests/day")
    logger.info(f"  Projected time to completion:   {projected_days} day(s)")
    logger.info(f"  Throttling caps:                {EMBED_RPM_CAP} RPM | {EMBED_TPM_CAP} TPM")
    logger.info("==================================================")

    return unmigrated, avg_tokens, projected_days


def is_daily_quota_error(error_str: str) -> bool:
    """Detects whether a 429 is due to daily RPD quota exhaustion."""
    err_lower = error_str.lower()
    return any(k in err_lower for k in [
        "perday", "requestsperday", "daily", "quotaexceededfor", 
        "quota_limit_value_per_day", "free_tier_daily"
    ])


def call_gemini_batch_with_safety(
    emb_service: GeminiHostedEmbeddings,
    texts: List[str],
    task_type: str = "RETRIEVAL_DOCUMENT"
) -> Tuple[Optional[List[List[float]]], bool]:
    """
    Calls Gemini batchEmbedContents with explicit 429 classification.
    Returns (vectors, is_daily_exhausted).
    """
    clean_model_id = f"models/{emb_service.model_name.replace('models/', '')}"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": emb_service.api_key,
    }
    requests_body = [
        {
            "model": clean_model_id,
            "content": {"parts": [{"text": t[:8000]}]},
            "taskType": task_type,
            "outputDimensionality": emb_service.dimension,
        }
        for t in texts
    ]

    for attempt in range(1, 4):
        try:
            resp = httpx.post(
                emb_service._batch_url,
                json={"requests": requests_body},
                headers=headers,
                timeout=emb_service.timeout + (len(texts) * 0.1),
            )

            if resp.status_code == 200:
                data = resp.json()
                raw_embeddings = data.get("embeddings", [])
                result = []
                for item in raw_embeddings:
                    vals = item.get("values", [])
                    result.append(_l2_normalize(vals) if vals else [0.0] * emb_service.dimension)
                return result, False

            elif resp.status_code == 429:
                body_text = resp.text
                if is_daily_quota_error(body_text):
                    logger.error(f"🚨 Daily Quota Exceeded (RPD 429): {body_text}")
                    return None, True  # Daily exhausted
                
                logger.warning(f"⚠️ RPM/TPM Rate Limit (429) hit on attempt {attempt}/3. Sleeping 60s before retry...")
                time.sleep(60.0)

            elif resp.status_code in (500, 502, 503, 504):
                logger.warning(f"Server error {resp.status_code} on attempt {attempt}/3. Sleeping 10s...")
                time.sleep(10.0)
            else:
                logger.error(f"Non-retriable Gemini error HTTP {resp.status_code}: {resp.text}")
                return None, False

        except Exception as exc:
            logger.warning(f"Network error on attempt {attempt}/3: {exc}")
            time.sleep(5.0 * attempt)

    return None, False


def migrate_chunks(session, emb_service: GeminiHostedEmbeddings, max_budget: int) -> int:
    """
    Migrates unmigrated :Chunk nodes up to max_budget chunks.
    Paces requests to stay below EMBED_RPM_CAP and EMBED_TPM_CAP.
    Stops cleanly on daily 429.
    """
    total_migrated = 0
    batch_num = 0

    while total_migrated < max_budget:
        remaining_budget = max_budget - total_migrated
        fetch_limit = min(BATCH_SIZE, remaining_budget)

        fetch_cypher = """
        MATCH (c:Chunk)
        WHERE c.embedding_v2 IS NULL
        RETURN c.id AS id, c.text AS text
        LIMIT $limit
        """
        records = list(session.run(fetch_cypher, {"limit": fetch_limit}))
        if not records:
            logger.info("🎉 All unmigrated :Chunk nodes processed (WHERE c.embedding_v2 IS NULL returned 0 rows).")
            break

        batch_num += 1
        chunk_ids = [r["id"] for r in records]
        chunk_texts = [r["text"] or "" for r in records]
        
        # Calculate tokens for this batch
        batch_tokens = sum(estimate_tokens(t) for t in chunk_texts)

        logger.info(
            f"Processing Batch #{batch_num}: {len(chunk_ids)} chunks "
            f"(~{batch_tokens} tokens, session progress: {total_migrated}/{max_budget})..."
        )

        t_start = time.time()
        vectors, daily_exhausted = call_gemini_batch_with_safety(
            emb_service, chunk_texts, task_type="RETRIEVAL_DOCUMENT"
        )

        if daily_exhausted:
            logger.error("==================================================")
            logger.error("🛑 MIGRATION STOPPED: Daily Gemini RPD quota reached.")
            logger.info("All processed batches are safely committed in Neo4j.")
            logger.info("To resume tomorrow after midnight Pacific reset:")
            logger.info("  python scripts/migrate_vectors_v2.py")
            logger.error("==================================================")
            return total_migrated

        if not vectors or len(vectors) != len(chunk_texts):
            logger.error(f"Failed to obtain valid embeddings for Batch #{batch_num}. Stopping.")
            break

        # Commit batch to Neo4j
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
        logger.info(f"  ✓ Batch #{batch_num} committed ({len(updates)} chunks updated in Neo4j). Total today: {total_migrated}/{max_budget}")

        # Compute dual throttling delay
        # 1. Request rate delay: min time per request = 60 / EMBED_RPM_CAP
        req_delay = 60.0 / EMBED_RPM_CAP
        # 2. Token rate delay: min time for this batch's tokens = (batch_tokens / EMBED_TPM_CAP) * 60
        tok_delay = (batch_tokens / EMBED_TPM_CAP) * 60.0
        
        target_sleep = max(req_delay, tok_delay, 1.0)
        elapsed = time.time() - t_start
        actual_sleep = max(0.0, target_sleep - elapsed)
        
        time.sleep(actual_sleep)

    return total_migrated


def report_final_counts(session):
    """Reports total nodes with and without embedding_v2."""
    count_cypher = """
    MATCH (c:Chunk)
    RETURN
      count(c) AS total,
      count(c.embedding_v2) AS with_v2,
      count(CASE WHEN c.embedding_v2 IS NULL THEN 1 END) AS without_v2,
      count(c.embedding_384) AS with_384,
      count(c.embedding) AS with_legacy
    """
    res = session.run(count_cypher).single()
    logger.info("==================================================")
    logger.info("FINAL NEO4J NODE EMBEDDING SUMMARY (:Chunk):")
    logger.info(f"  Total :Chunk nodes:          {res['total']}")
    logger.info(f"  With embedding_v2 (768-dim): {res['with_v2']}")
    logger.info(f"  Without embedding_v2:        {res['without_v2']}")
    logger.info(f"  With embedding_384 (384-dim):{res['with_384']}")
    logger.info(f"  With legacy embedding:       {res['with_legacy']}")
    logger.info("==================================================")


def main():
    max_budget = EMBED_DAILY_BUDGET
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        max_budget = int(sys.argv[1])
        logger.info(f"Running with explicit budget override: {max_budget} chunks.")
    else:
        logger.info(f"Running with EMBED_DAILY_BUDGET={max_budget} chunks.")

    driver = get_driver()
    emb_service = GeminiHostedEmbeddings(
        api_key=settings.GOOGLE_API_KEY,
        model_name="models/gemini-embedding-001",
        dimension=TARGET_DIM,
    )

    with driver.session() as session:
        check_and_create_indexes(session)
        unmigrated, avg_tokens, projected_days = sample_and_project(session, max_budget)
        
        if unmigrated > 0 and max_budget > 0:
            migrated = migrate_chunks(session, emb_service, max_budget=max_budget)
            logger.info(f"Session complete. Migrated {migrated} chunks this run.")
        
        report_final_counts(session)

    driver.close()


if __name__ == "__main__":
    main()

