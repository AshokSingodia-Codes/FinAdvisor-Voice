import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import kg

def clean_lucene_query(query: str) -> str:
    # Keep alphanumeric words and numbers
    words = re.findall(r'[a-zA-Z0-9]+', query)
    # Filter common stop words
    stopwords = {"what", "were", "was", "the", "in", "of", "and", "for", "to", "a", "is", "how", "did"}
    filtered = [w for w in words if w.lower() not in stopwords]
    if not filtered:
        filtered = words
    # Build fuzzy OR query for Lucene BM25
    return " OR ".join(filtered)

test_queries = [
    "What were Apple's total net sales in fiscal year 2024?",
    "What is the formula for Weighted Average Cost of Capital (WACC)?",
    "What were Microsoft's cloud revenues in 2023?"
]

for q in test_queries:
    lucene_q = clean_lucene_query(q)
    print(f"\nQuery: {q}")
    print(f"Lucene Expression: {lucene_q}")
    cypher = """
    CALL db.index.fulltext.queryNodes("keyword_markdown", $query)
    YIELD node, score
    RETURN node.text as text, score
    ORDER BY score DESC
    LIMIT 3
    """
    try:
        res = kg.query(cypher, {"query": lucene_q})
        print(f"Returned {len(res)} chunks:")
        for r in res:
            print(f" - [Score {r.get('score', 0):.2f}] {r.get('text', '')[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
