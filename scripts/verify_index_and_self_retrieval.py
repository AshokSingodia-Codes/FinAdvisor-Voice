"""
scripts/verify_index_and_self_retrieval.py
------------------------------------------
1. Proves vector_markdown_v2 index operates via db.index.vector.queryNodes.
2. Runs a 10-chunk self-retrieval evaluation using RETRIEVAL_QUERY embeddings.
"""

import os
import sys
import re
from dotenv import load_dotenv
from neo4j import GraphDatabase

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from config.settings import settings
from core.embeddings import get_embedding_service


def get_first_sentence(text: str) -> str:
    """Extracts a clean, representative single sentence from chunk text."""
    lines = [l.strip() for l in text.split("\n") if l.strip() and not l.startswith("|") and not l.startswith("#")]
    clean_text = " ".join(lines)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) >= 30 and not s_clean.startswith("---"):
            return s_clean[:200]
    return clean_text[:120]


def main():
    emb_service = get_embedding_service()
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )

    with driver.session() as session:
        # Step 1: Prove index query works via db.index.vector.queryNodes
        test_query = "capital gains tax exemption and deductions"
        q_vec = emb_service.embed_query(test_query)

        native_index_cypher = """
        CALL db.index.vector.queryNodes('vector_markdown_v2', 3, $vec)
        YIELD node, score
        RETURN node.id AS id, score, substring(node.text, 0, 120) AS snippet
        """
        results = list(session.run(native_index_cypher, {"vec": q_vec}))
        print("================================================================")
        print("1. PROOF OF db.index.vector.queryNodes ON vector_markdown_v2:")
        print(f"   Query: '{test_query}'")
        print(f"   Matches returned: {len(results)}")
        for r in results:
            print(f"   - Score: {r['score']:.4f} | ID: {r['id']} | Snippet: {r['snippet'].replace(chr(10), ' ')}...")
        print("================================================================")

        # Step 2: 10-Chunk Self-Retrieval Check
        fetch_chunks_cypher = """
        MATCH (c:Chunk)
        WHERE c.embedding_v2 IS NOT NULL
        RETURN c.id AS id, c.text AS text
        LIMIT 10
        """
        chunks = list(session.run(fetch_chunks_cypher))
        print(f"\n2. RUNNING 10-CHUNK SELF-RETRIEVAL BENCHMARK:")
        print(f"   Total test chunks selected: {len(chunks)}")

        rank_1_count = 0
        top_3_count = 0

        for i, ch in enumerate(chunks, 1):
            target_id = ch["id"]
            sentence = get_first_sentence(ch["text"])
            
            # Embed sentence as RETRIEVAL_QUERY
            query_vec = emb_service.embed_query(sentence)

            query_cypher = """
            CALL db.index.vector.queryNodes('vector_markdown_v2', 5, $vec)
            YIELD node, score
            RETURN node.id AS id, score
            """
            retrieved = list(session.run(query_cypher, {"vec": query_vec}))
            retrieved_ids = [r["id"] for r in retrieved]

            rank = None
            if target_id in retrieved_ids:
                rank = retrieved_ids.index(target_id) + 1

            if rank == 1:
                rank_1_count += 1
                top_3_count += 1
                status_str = "RANK 1 (PERFECT)"
            elif rank is not None and rank <= 3:
                top_3_count += 1
                status_str = f"RANK {rank} (TOP 3)"
            elif rank is not None:
                status_str = f"RANK {rank}"
            else:
                status_str = "NOT IN TOP 5"

            print(f"   [{i}/10] Target ID: {target_id[:16]}... | Status: {status_str}")
            print(f"        Sentence: \"{sentence[:80]}...\"")

        print("----------------------------------------------------------------")
        print("SELF-RETRIEVAL RESULTS SUMMARY:")
        print(f"   Rank 1 Accuracy: {rank_1_count} / {len(chunks)} ({rank_1_count / len(chunks) * 100:.1f}%)")
        print(f"   Top 3 Accuracy:  {top_3_count} / {len(chunks)} ({top_3_count / len(chunks) * 100:.1f}%)")
        print("================================================================")

    driver.close()


if __name__ == "__main__":
    main()
