"""
core/llm_manager.py
-------------------
Resilient Multi-Provider LLM Fallback Chain with In-Memory Circuit Breakers
and Conversation-Scoped Privacy Isolation.

Fallback Order:
- Public Queries: Groq -> Gemini -> OpenRouter
- Personal Context Queries: Groq -> OpenRouter (with Zero-Data-Retention: data_collection='deny')

Circuit Breaker:
- Automatically disables a provider for 60s (or Retry-After header duration) upon 429, 5xx, or Timeout.
- Logs answering provider name (strictly no secrets or payload content).
"""

import time
import logging
from typing import Any, List, Optional, Dict, Union, Type
from pydantic import BaseModel, Field

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import Runnable, RunnableConfig

from config.settings import settings

from datetime import datetime, timezone, timedelta

logger = logging.getLogger("finadvisor.llm")

# Global thread-safe circuit breaker tracker: {provider_name: cooldown_until_timestamp}
_CIRCUIT_BREAKER: Dict[str, float] = {}


def _seconds_until_midnight_pacific() -> float:
    """Calculates seconds remaining until midnight Pacific Time (Google Quota Reset)."""
    now_utc = datetime.now(timezone.utc)
    pt_tz = timezone(timedelta(hours=-7))
    now_pt = now_utc.astimezone(pt_tz)
    midnight_pt = (now_pt + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
    return max((midnight_pt - now_pt).total_seconds(), 60.0)


def _is_provider_available(provider: str) -> bool:
    """Checks if a provider is currently open (not in cooldown)."""
    cooldown_until = _CIRCUIT_BREAKER.get(provider, 0.0)
    now = time.time()
    if now < cooldown_until:
        remaining = int(cooldown_until - now)
        logger.debug(f"[CircuitBreaker] Skipping provider '{provider}' (cooldown remaining: {remaining}s)")
        return False
    return True


def _record_provider_failure(provider: str, error: Exception):
    """
    Sets appropriate cooldown:
    - If daily quota (RPD) exhausted: disables provider until midnight Pacific Time.
    - If minute rate limit (RPM) or temporary 5xx: 60-second cooldown (or Retry-After duration).
    """
    err_str = str(error).lower()
    is_daily_limit = any(k in err_str for k in ("perday", "daily", "requestsperday", "quotaexceededfor", "free_tier_daily"))

    if is_daily_limit:
        cooldown_seconds = _seconds_until_midnight_pacific()
        _CIRCUIT_BREAKER[provider] = time.time() + cooldown_seconds
        logger.warning(
            f"[CircuitBreaker] 🚨 Provider '{provider}' hit DAILY RPD QUOTA. "
            f"Disabled until Midnight Pacific (~{cooldown_seconds / 3600:.1f} hours remaining)."
        )
        return

    cooldown_seconds = 60.0
    if hasattr(error, "response") and error.response is not None:
        retry_after = getattr(error.response, "headers", {}).get("retry-after")
        if retry_after:
            try:
                cooldown_seconds = max(float(retry_after), 10.0)
            except (ValueError, TypeError):
                pass

    _CIRCUIT_BREAKER[provider] = time.time() + cooldown_seconds
    logger.warning(
        f"[CircuitBreaker] Tripped for provider '{provider}' (RPM/Transient error: {type(error).__name__}). "
        f"Cooldown set for {cooldown_seconds:.1f}s."
    )


def _record_provider_success(provider: str):
    """Clears cooldown upon successful execution."""
    if provider in _CIRCUIT_BREAKER:
        _CIRCUIT_BREAKER.pop(provider, None)


class ResilientFallbackChat(BaseChatModel):
    """
    Custom LangChain BaseChatModel that implements:
    1. Strict ordered fallback cascade
    2. In-memory circuit breakers (cooldown on 429/5xx/timeout)
    3. Conversation-scoped personal context isolation (excludes Gemini, sets data_collection='deny')
    4. Internal response tagging with 'answered_by' provider
    """

    tier: str = "fast"  # 'fast' or 'synthesis'
    has_personal_context: bool = False
    temperature: float = 0.0
    max_tokens: int = 400
    structured_schema: Optional[Any] = None

    def _llm_type(self) -> str:
        return f"resilient_fallback_chat_{self.tier}"

    def _get_providers_order(self) -> List[str]:
        """Determines the ordered list of providers based on personal context."""
        if self.has_personal_context:
            # Privacy policy: Groq -> OpenRouter only (Gemini excluded)
            raw = getattr(settings, "PERSONAL_CONTEXT_PROVIDERS", "groq,openrouter")
            providers = [p.strip().lower() for p in raw.split(",") if p.strip()]
        else:
            # Standard public policy: Groq -> Gemini -> OpenRouter
            providers = ["groq", "gemini", "openrouter"]
        return providers

    def _instantiate_provider_client(self, provider: str) -> Optional[BaseChatModel]:
        """Instantiates a single LangChain client for the given provider and tier."""
        try:
            if provider == "groq":
                if not settings.GROQ_API_KEY:
                    return None
                from langchain_groq import ChatGroq
                model_name = (
                    settings.ROUTER_MODEL if self.tier == "fast" else settings.SYNTHESIS_MODEL
                ) or settings.GROQ_MODEL or "llama-3.3-70b-versatile"
                return ChatGroq(
                    model_name=model_name,
                    api_key=settings.GROQ_API_KEY,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    max_retries=0,
                    timeout=5 if self.tier == "fast" else 8,
                )

            elif provider == "gemini":
                if self.has_personal_context:
                    return None  # Strictly forbidden for personal context
                if not settings.GOOGLE_API_KEY:
                    return None
                from langchain_google_genai import ChatGoogleGenerativeAI
                gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite") or "gemini-3.5-flash-lite"
                return ChatGoogleGenerativeAI(
                    model=gemini_model,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    max_retries=0,
                    timeout=5 if self.tier == "fast" else 8,
                )

            elif provider == "openrouter":
                if not settings.OPENROUTER_API_KEY:
                    return None
                from langchain_openai import ChatOpenAI
                or_model = getattr(settings, "OPENROUTER_MODEL", None)
                if not or_model:
                    or_model = "mistralai/mistral-small-24b-instruct-2501" if self.tier == "fast" else "qwen/qwen-2.5-72b-instruct"
                
                extra_body = None
                if self.has_personal_context:
                    # Enforce zero data retention / data collection denial on OpenRouter
                    extra_body = {"provider": {"data_collection": "deny", "zdr": True}}

                return ChatOpenAI(
                    model=or_model,
                    openai_api_key=settings.OPENROUTER_API_KEY,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    max_retries=0,
                    timeout=6 if self.tier == "fast" else 10,
                    extra_body=extra_body,
                )
        except Exception as e:
            logger.error(f"[LLMManager] Error instantiating provider client for '{provider}': {e}")
            return None

        return None

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Executes the fallback cascade across available providers."""
        providers = self._get_providers_order()
        last_error = None
        attempted_providers = []

        for provider in providers:
            if not _is_provider_available(provider):
                continue

            client = self._instantiate_provider_client(provider)
            if client is None:
                continue

            attempted_providers.append(provider)
            try:
                if self.structured_schema is not None:
                    structured_client = client.with_structured_output(self.structured_schema)
                    result_obj = structured_client.invoke(messages, **kwargs)
                    _record_provider_success(provider)
                    logger.info(f"[LLM] Success via '{provider}' (tier={self.tier}, personal_context={self.has_personal_context})")
                    gen = ChatGeneration(
                        message=AIMessage(
                            content=str(result_obj),
                            additional_kwargs={"answered_by": provider, "structured_result": result_obj}
                        )
                    )
                    return ChatResult(generations=[gen])
                else:
                    response = client.invoke(messages, stop=stop, **kwargs)
                    _record_provider_success(provider)
                    logger.info(f"[LLM] Success via '{provider}' (tier={self.tier}, personal_context={self.has_personal_context})")
                    
                    if isinstance(response, AIMessage):
                        response.additional_kwargs["answered_by"] = provider
                        return ChatResult(generations=[ChatGeneration(message=response)])
                    else:
                        msg = AIMessage(content=str(response.content), additional_kwargs={"answered_by": provider})
                        return ChatResult(generations=[ChatGeneration(message=msg)])

            except Exception as e:
                last_error = e
                _record_provider_failure(provider, e)
                logger.warning(f"[LLM Fallback] Provider '{provider}' failed: {e}. Moving to next provider in cascade.")
                continue

        # If all providers in the cascade failed
        logger.error(f"[LLM Fallback] All available providers ({providers}) failed. Last error: {last_error}")
        fallback_msg = AIMessage(
            content="I am currently experiencing temporary upstream capacity constraints across all AI providers. Please try again in a moment.",
            additional_kwargs={"answered_by": "fallback_error"}
        )
        return ChatResult(generations=[ChatGeneration(message=fallback_msg)])

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Runnable:
        """Returns a copy configured with the given structured schema."""
        return ResilientFallbackChat(
            tier=self.tier,
            has_personal_context=self.has_personal_context,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            structured_schema=schema,
        )

    def bind_personal_context(self, has_personal: bool) -> "ResilientFallbackChat":
        """Returns a new chat instance with conversation-scoped personal context bound."""
        return ResilientFallbackChat(
            tier=self.tier,
            has_personal_context=has_personal,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            structured_schema=self.structured_schema,
        )
