import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from fastembed import TextEmbedding
from neo4j import GraphDatabase

print("Connecting to Neo4j...")
driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
with driver.session(database=settings.NEO4J_USERNAME) as session:
    cnt = session.run("MATCH (c:Chunk) WHERE c.embedding_384 IS NOT NULL RETURN count(c) as cnt").single()["cnt"]
    print("Nodes with embedding_384:", cnt)
    
    print("Generating query embedding with fastembed BAAI/bge-small-en-v1.5 (384-dim)...")
    model = TextEmbedding("BAAI/bge-small-en-v1.5", threads=1)
    query_vec = list(next(model.query_embed(["What was Apple total revenue in 2024?"])))
    print("Vector length:", len(query_vec))
    
    hits = session.run("""
        CALL db.index.vector.queryNodes('vector_markdown_384', 3, $vec)
        YIELD node, score
        RETURN node.chunk_id AS chunk_id, score, substring(node.text, 0, 80) AS text
    """, {"vec": query_vec}).data()
    print("Top 3 Vector Hits:")
    for h in hits:
        print(f"  Chunk: {h['chunk_id']} | Score: {h['score']:.4f} | Preview: {h['text']!r}")
driver.close()
