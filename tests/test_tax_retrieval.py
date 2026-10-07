import os, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.retriever import structured_retriever
from core.db import vector_index


def test_tax_retrieval_keyword_and_graph():
    test_queries = [
        "What are the income tax slabs under Section 115BAC for FY 2024-25?",
        "What is the capital gains tax rate on listed equity shares post Budget 2024?",
        "What is the 50/30/20 budgeting rule and emergency fund sizing?"
    ]

    for q in test_queries:
        # 1. Lucene Fulltext / Graph
        kw_results = structured_retriever(q, top_k=2)
        assert isinstance(kw_results, list)

        # 2. Dense Vector Search (if enabled)
        if vector_index is not None:
            vec_results = vector_index.similarity_search(q, k=2)
            assert isinstance(vec_results, list)

