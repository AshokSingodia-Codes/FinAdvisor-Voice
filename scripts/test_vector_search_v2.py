"""
scripts/test_vector_search_v2.py
--------------------------------
Quick test to verify cosine similarity search on vector_markdown_v2.
"""

import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from config.settings import settings
from core.embeddings import get_embedding_service


def main():
    emb_service = get_embedding_service()
    query = "What are the rules and limits for capital gains tax?"
    print(f"Embedding query: '{query}'")
    q_vec = emb_service.embed_query(query)
    print(f"Generated query vector dimension: {len(q_vec)}")

    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )

    cypher = """
    MATCH (c:Chunk)
    WHERE c.embedding_v2 IS NOT NULL
    WITH c, vector.similarity.cosine(c.embedding_v2, $vec) AS score
    ORDER BY score DESC
    LIMIT 3
    RETURN c.id AS id, score, substring(c.text, 0, 160) AS snippet
    """

    with driver.session() as session:
        results = list(session.run(cypher, {"vec": q_vec}))
        print("\n--- Top Search Results from Migrated Chunks in vector_markdown_v2 ---")
        for idx, r in enumerate(results, 1):
            clean_snippet = r["snippet"].replace("\n", " ").strip()
            print(f"{idx}. Score: {r['score']:.4f} | ID: {r['id']}")
            print(f"   Snippet: {clean_snippet}...\n")

    driver.close()


if __name__ == "__main__":
    main()
