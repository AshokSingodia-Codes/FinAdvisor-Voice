import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import kg

query_str = "Apple Net sales 2024"
cypher = """
CALL db.index.fulltext.queryNodes("keyword_markdown", $query)
YIELD node, score
RETURN node.text as text, score
LIMIT 5
"""
res = kg.query(cypher, {"query": query_str})
print(f"Fulltext search for '{query_str}' returned {len(res)} results:")
for i, r in enumerate(res, 1):
    print(f"[{i}] Score: {r.get('score', 0):.3f} | Text: {r.get('text', '')[:120]}...")
