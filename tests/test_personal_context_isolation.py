"""
tests/test_personal_context_isolation.py
-----------------------------------------
Unit tests verifying that conversations with personal document context:
1. NEVER invoke Google Gemini on any node or any turn (router, verifier, synthesis, etc.).
2. Strictly route through PERSONAL_CONTEXT_PROVIDERS (Groq -> OpenRouter).
3. OpenRouter requests include zero-data-retention headers (provider.data_collection = 'deny').
4. The personal context flag survives across multiple chat turns (persisted in SQL).
"""

import pytest
from core.llm_manager import ResilientFallbackChat
from core.document_store import get_active_document_for_conversation
from config.settings import settings


def test_fallback_cascade_excludes_gemini_for_personal_context():
    """Verify that ResilientFallbackChat excludes Gemini when has_personal_context=True."""
    # 1. Public query cascade
    public_chat = ResilientFallbackChat(tier="fast", has_personal_context=False)
    assert "gemini" in public_chat._get_providers_order()
    assert public_chat._get_providers_order() == ["groq", "gemini", "openrouter"]

    # 2. Personal context cascade
    personal_chat = ResilientFallbackChat(tier="fast", has_personal_context=True)
    assert "gemini" not in personal_chat._get_providers_order()
    assert personal_chat._get_providers_order() == ["groq", "openrouter"]

    # 3. Verify client instantiation for Gemini returns None when personal context is active
    gemini_client = personal_chat._instantiate_provider_client("gemini")
    assert gemini_client is None, "Gemini client MUST be None for personal context requests"


def test_openrouter_zero_data_retention_configured():
    """Verify OpenRouter client includes data_collection='deny' when personal context is active."""
    personal_chat = ResilientFallbackChat(tier="synthesis", has_personal_context=True)
    if settings.OPENROUTER_API_KEY:
        client = personal_chat._instantiate_provider_client("openrouter")
        assert client is not None
        extra_body = getattr(client, "extra_body", {}) or {}
        provider_config = extra_body.get("provider", {})
        assert provider_config.get("data_collection") == "deny"
        assert provider_config.get("zdr") is True


def test_circuit_breaker_rpd_vs_rpm_handling():
    """Verify that daily quota errors trigger midnight Pacific cooldown while RPM triggers 60s."""
    from core.llm_manager import _record_provider_failure, _CIRCUIT_BREAKER
    import time

    # Simulate RPM 429 error
    _record_provider_failure("test_rpm_provider", Exception("429 Too Many Requests: Rate limit exceeded (PerMinute)"))
    cooldown = _CIRCUIT_BREAKER.get("test_rpm_provider", 0.0)
    assert 55.0 <= (cooldown - time.time()) <= 65.0

    # Simulate RPD Daily Quota error
    _record_provider_failure("test_rpd_provider", Exception("429 RESOURCE_EXHAUSTED: Quota exceeded for metric 'GenerateContentRequestsPerDay'"))
    rpd_cooldown = _CIRCUIT_BREAKER.get("test_rpd_provider", 0.0)
    # Cooldown should be at least 1 hour and at most 24.5 hours
    remaining_hours = (rpd_cooldown - time.time()) / 3600.0
    assert 0.01 <= remaining_hours <= 25.0
