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
    - If credit balance exhausted (402): 24h cooldown so provider isn't repeatedly queried.
    - If daily quota (RPD) exhausted: disables provider until midnight Pacific Time.
    - If minute rate limit (RPM/TPM): parses provider's wait hint (e.g. 'try again in 2.8s') or sets 3-5s cooldown.
    - If transient 5xx or read timeout: 5.0s cooldown.
    - If 400 Bad Request / tool_use_failed / validation error: do NOT trip the circuit breaker.
    """
    err_str = str(error).lower()

    # Client-side / schema errors (e.g. model returned text instead of tool call) must not disable provider globally
    if any(k in err_str for k in ("tool_use_failed", "bad request", "400", "invalid_request_error", "validation_error")):
        logger.warning(f"[CircuitBreaker] Skipping cooldown for '{provider}' on client/format error: {error}")
        return

    # Check 402 / credit exhaustion
    if any(k in err_str for k in ("402", "openrouter_credits", "more credits", "adjust the key's total limit")):
        cooldown_seconds = 86400.0
        _CIRCUIT_BREAKER[provider] = time.time() + cooldown_seconds
        logger.warning(f"[CircuitBreaker] Provider '{provider}' has no credits (402). Cooldown set for 24h.")
        return

    is_daily_limit = any(k in err_str for k in ("perday", "daily", "requestsperday", "quotaexceededfor", "free_tier_daily"))

    if is_daily_limit:
        cooldown_seconds = _seconds_until_midnight_pacific()
        _CIRCUIT_BREAKER[provider] = time.time() + cooldown_seconds
        logger.warning(
            f"[CircuitBreaker] 🚨 Provider '{provider}' hit DAILY RPD QUOTA. "
            f"Disabled until Midnight Pacific (~{cooldown_seconds / 3600:.1f} hours remaining)."
        )
        return

    # Check for specific retry hint like 'try again in 2.8875s'
    import re
    match = re.search(r"try again in (\d+(?:\.\d+)?)s", err_str)
    if match:
        cooldown_seconds = max(float(match.group(1)) + 0.5, 2.0)
    elif hasattr(error, "response") and error.response is not None:
        retry_after = getattr(error.response, "headers", {}).get("retry-after")
        if retry_after:
            try:
                cooldown_seconds = max(float(retry_after), 10.0)
            except (ValueError, TypeError):
                cooldown_seconds = 60.0
        else:
            cooldown_seconds = 60.0
    else:
        cooldown_seconds = 60.0

    _CIRCUIT_BREAKER[provider] = time.time() + cooldown_seconds
    logger.warning(
        f"[CircuitBreaker] Tripped for provider '{provider}' (Error: {type(error).__name__}). "
        f"Cooldown set for {cooldown_seconds:.1f}s."
    )


def _record_provider_success(provider: str):
    """Clears cooldown upon successful execution."""
    if provider in _CIRCUIT_BREAKER:
        _CIRCUIT_BREAKER.pop(provider, None)


class StructuredFallbackRunnable(Runnable):
    """
    Executes structured output with resilient multi-provider fallback.
    Returns the parsed Pydantic / structured object directly to match LangChain's contract.
    """
    def __init__(self, parent_chat: "ResilientFallbackChat", schema: Any):
        self.parent_chat = parent_chat
        self.schema = schema

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:
        providers = self.parent_chat._get_providers_order()
        # Find providers that are not in cooldown
        available_providers = [p for p in providers if _is_provider_available(p)]
        if not available_providers:
            # All providers are in cooldown! Pick the one whose cooldown expires earliest.
            # If the remaining cooldown is small (<= 4s), wait briefly to allow the window to clear.
            best = min(providers, key=lambda p: _CIRCUIT_BREAKER.get(p, 0.0))
            remaining = _CIRCUIT_BREAKER.get(best, 0.0) - time.time()
            if 0 < remaining <= 4.0:
                logger.info(f"[StructuredLLM] All in cooldown. Waiting {remaining:.1f}s for '{best}' window to clear...")
                time.sleep(remaining + 0.1)
            available_providers = [best]
            logger.info(f"[StructuredLLM] Resuming attempt with provider '{best}'.")

        last_error = None
        for provider in available_providers:
            client = self.parent_chat._instantiate_provider_client(provider)
            if client is None:
                continue
            try:
                structured_client = client.with_structured_output(self.schema)
                res = structured_client.invoke(input, config=config, **kwargs)
                _record_provider_success(provider)
                logger.info(f"[StructuredLLM] Success via '{provider}' (tier={self.parent_chat.tier})")
                return res
            except Exception as e:
                last_error = e
                _record_provider_failure(provider, e)
                # If provider is groq and it's a minor minute/token rate limit with short retry hint (<= 5s), wait and retry once
                import re
                match = re.search(r"try again in (\d+(?:\.\d+)?)s", str(e).lower())
                if match and float(match.group(1)) <= 5.0 and provider == "groq":
                    wait_s = float(match.group(1)) + 0.3
                    logger.info(f"[StructuredLLM] Groq TPM limit: waiting {wait_s:.1f}s for bucket to drain...")
                    time.sleep(wait_s)
                    try:
                        structured_client = client.with_structured_output(self.schema)
                        res = structured_client.invoke(input, config=config, **kwargs)
                        _record_provider_success(provider)
                        logger.info(f"[StructuredLLM] Success on retry via '{provider}' (tier={self.parent_chat.tier})")
                        return res
                    except Exception as e2:
                        last_error = e2
                        _record_provider_failure(provider, e2)
                logger.warning(f"[StructuredLLM] Provider '{provider}' failed: {e}. Cascading...")
                continue

        logger.error(f"[StructuredLLM] All providers ({providers}) failed for schema {self.schema}: {last_error}")
        if isinstance(self.schema, type) and issubclass(self.schema, BaseModel):
            try:
                return self.schema()
            except Exception:
                pass
        raise last_error or RuntimeError(f"All structured LLM providers failed for {self.schema}")


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
                    timeout=25 if self.tier == "fast" else 35,
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
        available_providers = [p for p in providers if _is_provider_available(p)]
        if not available_providers:
            # All providers are in cooldown! Pick the one whose cooldown expires earliest.
            best = min(providers, key=lambda p: _CIRCUIT_BREAKER.get(p, 0.0))
            remaining = _CIRCUIT_BREAKER.get(best, 0.0) - time.time()
            if 0 < remaining <= 4.0:
                logger.info(f"[LLM] All providers in cooldown. Waiting {remaining:.1f}s for '{best}' window to clear...")
                time.sleep(remaining + 0.1)
            available_providers = [best]
            logger.info(f"[LLM] Resuming attempt with provider '{best}'.")

        last_error = None
        attempted_providers = []

        for provider in available_providers:
            client = self._instantiate_provider_client(provider)
            if client is None:
                continue

            attempted_providers.append(provider)
            try:
                response = client.invoke(messages, stop=stop, **kwargs)
                _record_provider_success(provider)
                logger.info(f"[LLM] Success via '{provider}' (tier={self.tier}, personal_context={self.has_personal_context})")

                raw_content = response.content if isinstance(response, AIMessage) else getattr(response, "content", str(response))
                if isinstance(raw_content, list):
                    text_parts = []
                    for part in raw_content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
                        elif isinstance(part, str):
                            text_parts.append(part)
                        else:
                            text_parts.append(str(part))
                    content_str = "\n".join(text_parts)
                else:
                    content_str = str(raw_content)

                msg = AIMessage(content=content_str, additional_kwargs={"answered_by": provider})
                return ChatResult(generations=[ChatGeneration(message=msg)])

            except Exception as e:
                last_error = e
                _record_provider_failure(provider, e)
                # If provider is groq and it's a minor minute/token rate limit with short retry hint (<= 5s), wait and retry once
                import re
                match = re.search(r"try again in (\d+(?:\.\d+)?)s", str(e).lower())
                if match and float(match.group(1)) <= 5.0 and provider == "groq":
                    wait_s = float(match.group(1)) + 0.3
                    logger.info(f"[LLM] Groq TPM limit: waiting {wait_s:.1f}s for bucket to drain...")
                    time.sleep(wait_s)
                    try:
                        response = client.invoke(messages, stop=stop, **kwargs)
                        _record_provider_success(provider)
                        logger.info(f"[LLM] Success on retry via '{provider}' (tier={self.tier})")
                        raw_content = response.content if isinstance(response, AIMessage) else getattr(response, "content", str(response))
                        if isinstance(raw_content, list):
                            text_parts = []
                            for part in raw_content:
                                if isinstance(part, dict) and "text" in part:
                                    text_parts.append(part["text"])
                                elif isinstance(part, str):
                                    text_parts.append(part)
                                else:
                                    text_parts.append(str(part))
                            content_str = "\n".join(text_parts)
                        else:
                            content_str = str(raw_content)
                        msg = AIMessage(content=content_str, additional_kwargs={"answered_by": provider})
                        return ChatResult(generations=[ChatGeneration(message=msg)])
                    except Exception as e2:
                        last_error = e2
                        _record_provider_failure(provider, e2)
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
        """Returns a StructuredFallbackRunnable configured with the given structured schema."""
        return StructuredFallbackRunnable(self, schema)

    def bind_personal_context(self, has_personal: bool) -> "ResilientFallbackChat":
        """Returns a new chat instance with conversation-scoped personal context bound."""
        return ResilientFallbackChat(
            tier=self.tier,
            has_personal_context=has_personal,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            structured_schema=self.structured_schema,
        )
