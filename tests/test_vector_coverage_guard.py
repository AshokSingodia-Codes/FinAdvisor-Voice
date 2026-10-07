"""
tests/test_vector_coverage_guard.py
-----------------------------------
Tests the safety default (VECTOR_SEARCH_ENABLED=False) and startup coverage guard:
- Ensures vector search is disabled by default until migration >= 99%.
- Verifies that when VECTOR_SEARCH_ENABLED=False, zero embedding API calls occur.
- Verifies that if VECTOR_SEARCH_ENABLED=True but corpus coverage < 99%, it automatically falls back to keyword+graph.
"""

import pytest
from unittest.mock import patch, MagicMock
from config.settings import settings
import nodes.retriever as retriever_module


def test_default_settings_vector_search_disabled():
    """Confirms default setting is False to prevent premature vector queries."""
    assert getattr(settings, "VECTOR_SEARCH_ENABLED", None) is False, (
        "VECTOR_SEARCH_ENABLED must default to False until migration >= 99%"
    )


def test_vector_coverage_guard_below_threshold():
    """Verifies that coverage < 99% (e.g. 1370 / 2885 = 47.5%) triggers fallback."""
    # Reset module state
    retriever_module._VECTOR_COVERAGE_CHECKED = False
    retriever_module._VECTOR_COVERAGE_PASSES = False

    mock_kg = MagicMock()
    mock_kg.query.return_value = [{"total": 2885, "v2_count": 1370}]

    with patch.object(retriever_module, "kg", mock_kg):
        passed = retriever_module.check_vector_coverage(min_coverage=0.99)
        assert passed is False, "Coverage of 47.5% should fail the 99% coverage check."


def test_vector_coverage_guard_above_threshold():
    """Verifies that coverage >= 99% passes."""
    retriever_module._VECTOR_COVERAGE_CHECKED = False
    retriever_module._VECTOR_COVERAGE_PASSES = False

    mock_kg = MagicMock()
    mock_kg.query.return_value = [{"total": 2885, "v2_count": 2880}]  # 99.8%

    with patch.object(retriever_module, "kg", mock_kg):
        passed = retriever_module.check_vector_coverage(min_coverage=0.99)
        assert passed is True, "Coverage >= 99% should pass."


def test_zero_embedding_calls_when_vector_disabled():
    """Verifies that shared corpus retrieval makes zero embedding API calls when VECTOR_SEARCH_ENABLED=False."""
    retriever_module._VECTOR_COVERAGE_CHECKED = False
    retriever_module._VECTOR_COVERAGE_PASSES = False

    # Patch any external embedding call to raise if attempted
    with patch("core.embeddings.GeminiHostedEmbeddings._call_gemini_single", side_effect=RuntimeError("Embedding API must NOT be called when vector search is off")):
        with patch.object(settings, "VECTOR_SEARCH_ENABLED", False):
            # Also mock kg to return some keyword chunks
            with patch.object(retriever_module.kg, "query", return_value=[{"text": "Sample financial chunk"}]):
                results = retriever_module.retrieve_shared_corpus_concurrent("What is SIP?", top_k=2, apply_rerank=False)
                assert isinstance(results, list)
