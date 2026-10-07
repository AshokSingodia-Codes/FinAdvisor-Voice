"""
core/embeddings.py
------------------
Lightweight, Zero-Local-Memory Hosted Embeddings via Google Gemini REST API.
Implements LangChain's Embeddings interface with:
- Raw httpx HTTP calls (Zero torch / ONNX / FastEmbed memory overhead)
- Exact taskType support (RETRIEVAL_QUERY for queries, RETRIEVAL_DOCUMENT for chunks)
- Output dimensionality truncation (default 768) with manual L2 normalization
- Dedicated query TTLCache (500 entries)
- Dedicated Embedding Circuit Breaker and Exponential Backoff Retries
- Silent fallback to keyword search if embedding API is exhausted or unavailable

Rate Limits (Gemini Embedding 1 Free Tier):
- 100 RPM
- 30,000 TPM
- 1,000 RPD (resets at Midnight Pacific Time)
"""

import os
import math
import time
import random
import logging
from typing import List, Optional, Dict, Any
from cachetools import TTLCache

from langchain_core.embeddings import Embeddings
from config.settings import settings

from datetime import datetime, timezone, timedelta

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("finadvisor.embeddings")

# Thread-safe circuit breaker specifically for Gemini Embeddings API
_EMBEDDING_CIRCUIT_BREAKER_UNTIL: float = 0.0


def _seconds_until_midnight_pacific() -> float:
    """Calculates seconds remaining until midnight Pacific Time."""
    now_utc = datetime.now(timezone.utc)
    pt_tz = timezone(timedelta(hours=-7))
    now_pt = now_utc.astimezone(pt_tz)
    midnight_pt = (now_pt + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
    return max((midnight_pt - now_pt).total_seconds(), 60.0)


def _is_embedding_available() -> bool:
    """Checks if the embedding API is currently out of cooldown."""
    global _EMBEDDING_CIRCUIT_BREAKER_UNTIL
    now = time.time()
    if now < _EMBEDDING_CIRCUIT_BREAKER_UNTIL:
        remaining = int(_EMBEDDING_CIRCUIT_BREAKER_UNTIL - now)
        logger.debug(f"[EmbeddingCircuitBreaker] Gemini embedding endpoint in cooldown ({remaining}s remaining)")
        return False
    return True


def _trip_embedding_circuit_breaker(error_text: str = "", duration_sec: float = 60.0):
    """Puts the embedding API into cooldown upon rate limit or server error."""
    global _EMBEDDING_CIRCUIT_BREAKER_UNTIL
    err_lower = error_text.lower()
    if any(k in err_lower for k in ("perday", "daily", "requestsperday", "quotaexceededfor", "free_tier_daily")):
        duration_sec = _seconds_until_midnight_pacific()
        logger.warning(
            f"[EmbeddingCircuitBreaker] 🚨 Embedding API hit DAILY RPD QUOTA. "
            f"Disabled until Midnight Pacific (~{duration_sec / 3600:.1f} hours remaining)."
        )
    else:
        logger.warning(f"[EmbeddingCircuitBreaker] Embedding endpoint tripped (RPM/5xx). Cooldown: {duration_sec}s.")
    _EMBEDDING_CIRCUIT_BREAKER_UNTIL = time.time() + duration_sec


def _clear_embedding_circuit_breaker():
    """Clears the embedding cooldown on successful execution."""
    global _EMBEDDING_CIRCUIT_BREAKER_UNTIL
    _EMBEDDING_CIRCUIT_BREAKER_UNTIL = 0.0


def _l2_normalize(vec: List[float]) -> List[float]:
    """Applies L2 unit normalization to vector for accurate cosine similarity."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm < 1e-9:
        return vec
    return [x / norm for x in vec]


class GeminiHostedEmbeddings(Embeddings):
    """
    High-performance, zero-RAM Gemini hosted embeddings using raw httpx REST calls.
    Sends API key in x-goog-api-key header (never in URL).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "models/gemini-embedding-001",
        dimension: int = 768,
        timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model_name = model_name
        self.dimension = dimension
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Bounded query cache (500 items, 1 hour TTL)
        self._query_cache: TTLCache = TTLCache(maxsize=500, ttl=3600)
        
        # Base endpoint URL (clean, without query params)
        clean_model = model_name.replace("models/", "")
        self._single_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:embedContent"
        self._batch_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:batchEmbedContents"

    def _call_gemini_single(self, text: str, task_type: str = "RETRIEVAL_QUERY") -> Optional[List[float]]:
        """Makes a single embedContent HTTP call with retries and backoff."""
        if not self.api_key or not _is_embedding_available():
            return None

        import httpx

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "model": f"models/{self.model_name.replace('models/', '')}",
            "content": {"parts": [{"text": text[:8000]}]},
            "taskType": task_type,
            "outputDimensionality": self.dimension,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = httpx.post(
                    self._single_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    values = data.get("embedding", {}).get("values", [])
                    if values:
                        _clear_embedding_circuit_breaker()
                        return _l2_normalize(values)

                elif resp.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"[GeminiEmbeddings] HTTP {resp.status_code} on single query (attempt {attempt}/{self.max_retries})"
                    )
                    if attempt == self.max_retries:
                        _trip_embedding_circuit_breaker(error_text=resp.text)
                        return None
                    sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"[GeminiEmbeddings] Non-retriable error {resp.status_code}: {resp.text}")
                    return None

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                logger.warning(f"[GeminiEmbeddings] Network error (attempt {attempt}): {exc}")
                if attempt == self.max_retries:
                    _trip_embedding_circuit_breaker(error_text=str(exc))
                    return None
                time.sleep(1.0 * attempt)
            except Exception as e:
                logger.error(f"[GeminiEmbeddings] Unexpected error in single embed: {e}")
                return None

        return None

    def _call_gemini_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """Makes a batchEmbedContents HTTP call for a list of texts (max 50 per batch)."""
        if not texts:
            return []

        if not self.api_key or not _is_embedding_available():
            return [[0.0] * self.dimension for _ in texts]

        import httpx

        clean_model_id = f"models/{self.model_name.replace('models/', '')}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        requests_body = [
            {
                "model": clean_model_id,
                "content": {"parts": [{"text": t[:8000]}]},
                "taskType": task_type,
                "outputDimensionality": self.dimension,
            }
            for t in texts
        ]

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = httpx.post(
                    self._batch_url,
                    json={"requests": requests_body},
                    headers=headers,
                    timeout=self.timeout + (len(texts) * 0.1),
                )

                if resp.status_code == 200:
                    data = resp.json()
                    embeddings_raw = data.get("embeddings", [])
                    result = []
                    for item in embeddings_raw:
                        vals = item.get("values", [])
                        result.append(_l2_normalize(vals) if vals else [0.0] * self.dimension)
                    _clear_embedding_circuit_breaker()
                    return result

                elif resp.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"[GeminiEmbeddings] HTTP {resp.status_code} on batch of {len(texts)} (attempt {attempt}/{self.max_retries})"
                    )
                    if attempt == self.max_retries:
                        _trip_embedding_circuit_breaker(error_text=resp.text)
                        return [[0.0] * self.dimension for _ in texts]
                    sleep_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"[GeminiEmbeddings] Non-retriable batch error {resp.status_code}: {resp.text}")
                    return [[0.0] * self.dimension for _ in texts]

            except Exception as exc:
                logger.warning(f"[GeminiEmbeddings] Batch network exception (attempt {attempt}): {exc}")
                if attempt == self.max_retries:
                    _trip_embedding_circuit_breaker(30.0)
                    return [[0.0] * self.dimension for _ in texts]
                time.sleep(1.5 * attempt)

        return [[0.0] * self.dimension for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single search query with caching and fallback."""
        clean_text = text.strip()
        if not clean_text:
            return [0.0] * self.dimension

        if clean_text in self._query_cache:
            return self._query_cache[clean_text]

        vec = self._call_gemini_single(clean_text, task_type="RETRIEVAL_QUERY")
        if vec is not None and len(vec) == self.dimension:
            self._query_cache[clean_text] = vec
            return vec

        # Graceful fallback: return zero vector so retriever drops cleanly to BM25 keyword search
        logger.warning(f"[GeminiEmbeddings] Query embedding unavailable for '{clean_text[:40]}...'. Falling back to BM25.")
        return [0.0] * self.dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of document chunks in batches of up to 40."""
        if not texts:
            return []

        batch_size = 40
        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_vecs = self._call_gemini_batch(batch, task_type="RETRIEVAL_DOCUMENT")
            all_embeddings.extend(batch_vecs)

        return all_embeddings


def get_embedding_service() -> Embeddings:
    """
    Factory function returning the configured hosted embedding service.
    Defaults to zero-RAM GeminiHostedEmbeddings.
    """
    provider = getattr(settings, "EMBEDDING_PROVIDER", "gemini").lower()

    if provider == "gemini":
        return GeminiHostedEmbeddings(
            api_key=settings.GOOGLE_API_KEY,
            model_name=getattr(settings, "EMBEDDING_MODEL", "models/gemini-embedding-001"),
            dimension=getattr(settings, "EMBEDDING_DIM", 768),
        )

    elif provider == "fastembed":
        # Optional local fallback (used only if explicitly requested)
        try:
            from fastembed import TextEmbedding
            class LocalFastEmbed(Embeddings):
                def __init__(self):
                    self.model = TextEmbedding("BAAI/bge-small-en-v1.5", threads=1)
                def embed_query(self, text: str) -> List[float]:
                    return list(next(self.model.query_embed([text])))
                def embed_documents(self, texts: List[str]) -> List[List[float]]:
                    return [list(v) for v in self.model.embed(texts)]
            return LocalFastEmbed()
        except ImportError:
            logger.warning("[Embeddings] fastembed not installed; falling back to GeminiHostedEmbeddings")
            return GeminiHostedEmbeddings()

    return GeminiHostedEmbeddings()
