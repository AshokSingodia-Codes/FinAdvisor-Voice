import os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.retriever import structured_retriever
from core.db import vector_index

test_queries = [
    "What are the income tax slabs under Section 115BAC for FY 2024-25?",
    "What is the capital gains tax rate on listed equity shares post Budget 2024?",
    "What is the 50/30/20 budgeting rule and emergency fund sizing?"
]

print("="*60)
print("🔍 Testing Live Retrieval on Newly Ingested Corpus")
print("="*60)

for q in test_queries:
    print(f"\nQuery: {q}")
    # 1. Lucene Fulltext / Graph
    kw_results = structured_retriever(q, top_k=2)
    print(f"  [Lucene BM25 Matches]: {len(kw_results)}")
    if kw_results:
        print(f"   -> Snippet: {kw_results[0][:140]}...")
    
    # 2. Dense Vector Search
    vec_results = vector_index.similarity_search(q, k=2)
    print(f"  [Dense Vector Matches]: {len(vec_results)}")
    if vec_results:
        print(f"   -> Snippet: {vec_results[0].page_content[:140]}...")
