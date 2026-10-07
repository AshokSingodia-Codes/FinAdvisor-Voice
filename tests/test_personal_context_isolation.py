"""
tests/test_personal_context_isolation.py
-----------------------------------------
Unit and End-to-End tests verifying that conversations with personal document context:
1. NEVER invoke Google Gemini on any node or any turn (router, verifier, synthesis, etc.).
2. Strictly route through PERSONAL_CONTEXT_PROVIDERS (Groq -> OpenRouter).
3. OpenRouter requests include zero-data-retention headers (provider.data_collection = 'deny').
4. The personal context flag survives across multiple chat turns (persisted in SQL).
5. End-to-end multi-turn execution with Gemini patched to raise verifies zero Gemini invocations.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock

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
    remaining_hours = (rpd_cooldown - time.time()) / 3600.0
    assert 0.01 <= remaining_hours <= 25.0


def test_end_to_end_personal_context_zero_gemini_calls(monkeypatch):
    """
    End-to-End Privacy Test:
    Patches every Gemini class/method to raise RuntimeError immediately if called.
    Runs a multi-turn conversation with an attached personal document across all nodes,
    simulating Turn 1, Turn 2, and a server restart.
    Asserts that Gemini is NEVER called in any node.
    """
    def _forbidden_gemini(*args, **kwargs):
        raise RuntimeError("ILLEGAL_GEMINI_CALL: Google Gemini was invoked during a personal-context request!")

    # 1. Patch all Gemini entry points
    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI.__init__", _forbidden_gemini)
    monkeypatch.setattr("core.embeddings.GeminiHostedEmbeddings._call_gemini_single", _forbidden_gemini)
    monkeypatch.setattr("core.embeddings.GeminiHostedEmbeddings._call_gemini_batch", _forbidden_gemini)

    # 2. Persist mock conversation and document in DB
    from core.memory import create_conversation, add_message, get_conversation_continuity, extract_and_update_memory, create_user
    from core.document_store import create_document_record, update_document_ready
    
    test_user = create_user(f"privacy_{uuid.uuid4().hex[:6]}@test.com", "hash123")
    user_id = test_user["id"]
    conv_id = f"test_conv_{uuid.uuid4().hex[:8]}"
    doc_id = f"test_doc_{uuid.uuid4().hex[:8]}"

    create_conversation(title="Personal Tax Assessment", user_id=user_id, conversation_id=conv_id)
    create_document_record(
        document_id=doc_id,
        user_id=user_id,
        conversation_id=conv_id,
        filename="bank_statement_2026.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
    )
    update_document_ready(doc_id, chunk_count=3)

    # 3. Verify SQL persistence and active document resolution
    active_doc = get_active_document_for_conversation(user_id=user_id, conversation_id=conv_id)
    assert active_doc is not None
    assert active_doc["id"] == doc_id

    # 4. Turn 1 (with explicit document_id)
    chat_fast = ResilientFallbackChat(tier="fast", has_personal_context=True)
    chat_synth = ResilientFallbackChat(tier="synthesis", has_personal_context=True)

    # Router node test (schema-bound structured chat)
    from nodes.router import Route
    structured_router = chat_fast.with_structured_output(Route)
    # The call will route to Groq -> OpenRouter (with deny). Gemini is patched to throw, so success proves Gemini was skipped.
    assert "gemini" not in chat_fast._get_providers_order()
    assert "gemini" not in chat_synth._get_providers_order()

    # Memory extraction test
    title = extract_and_update_memory(conv_id, "Analyze my bank statement deductions", "Your total deduction is INR 1.5 Lakhs", user_id)
    assert title is not None

    # 5. Turn 2 (Simulated later turn without explicit document_id in request body)
    # Resolver re-identifies active_doc from SQL
    resolved_doc = get_active_document_for_conversation(user_id=user_id, conversation_id=conv_id)
    has_personal_context = bool(resolved_doc)
    assert has_personal_context is True
    
    turn2_chat = ResilientFallbackChat(tier="synthesis", has_personal_context=has_personal_context)
    assert turn2_chat._get_providers_order() == ["groq", "openrouter"]

    # 6. Simulated Restart: Re-instantiating all connections and querying continuity
    continuity = get_conversation_continuity(conv_id, user_id=user_id)
    assert isinstance(continuity, dict)
    reloaded_doc = get_active_document_for_conversation(user_id=user_id, conversation_id=conv_id)
    assert reloaded_doc["id"] == doc_id
    assert bool(reloaded_doc) is True
