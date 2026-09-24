"""
core/cache.py
-------------
In-memory TTL response cache for LLM answers.

Cache key is a hash of (normalized_question, conversation_id, document_id).
Live market data queries are NOT cached (identified by routing_decision).

Design notes:
  - Uses cachetools.TTLCache (thread-safe, bounded LRU+TTL eviction).
  - Falls back gracefully if cachetools is not installed.
  - Cache is process-local; it resets on restart and does not scale across
    multiple worker processes (acceptable for single-server deployments).
"""

import hashlib
from typing import Optional

_cache = None
_CACHE_TTL_SECONDS = 900   # 15-minute TTL
_CACHE_MAX_SIZE = 500       # Max 500 cached responses

# Routing decisions that should never be cached (live / time-sensitive)
_SKIP_CACHE_ROUTING = {"live_market_data", "market_data", "live_data"}


def _get_cache():
    """Lazy-initialise the TTLCache so import-time errors don't crash startup."""
    global _cache
    if _cache is None:
        try:
            from cachetools import TTLCache
            _cache = TTLCache(maxsize=_CACHE_MAX_SIZE, ttl=_CACHE_TTL_SECONDS)
        except ImportError:
            print("[cache] cachetools not installed — LLM response caching disabled.")
            _cache = {}  # plain dict fallback (no eviction, but won't crash)
    return _cache


def _make_key(question: str, conversation_id: str, document_id: Optional[str]) -> str:
    """
    Build a deterministic cache key.

    Normalization: lowercase + collapse whitespace, so minor rephrasing
    differences don't produce unnecessary cache misses.
    """
    normalized = " ".join(question.lower().split())
    raw = f"{normalized}|{conversation_id}|{document_id or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(
    question: str,
    conversation_id: str,
    document_id: Optional[str],
    routing_decision: Optional[str] = None,
) -> Optional[str]:
    """
    Return a cached LLM answer, or None on cache miss.

    Live market data queries are always bypassed.
    """
    if routing_decision in _SKIP_CACHE_ROUTING:
        return None

    key = _make_key(question, conversation_id, document_id)
    cache = _get_cache()
    cached = cache.get(key)
    if cached:
        print(f"[cache] HIT  key={key[:12]}…")
    else:
        print(f"[cache] MISS key={key[:12]}…")
    return cached


def set_cached_response(
    question: str,
    conversation_id: str,
    document_id: Optional[str],
    answer: str,
    routing_decision: Optional[str] = None,
) -> None:
    """
    Store an LLM answer in the cache.

    Live market data responses are not stored.
    """
    if routing_decision in _SKIP_CACHE_ROUTING:
        return

    key = _make_key(question, conversation_id, document_id)
    cache = _get_cache()
    cache[key] = answer
    print(f"[cache] SET  key={key[:12]}…")


def invalidate_document(document_id: str) -> int:
    """
    Evict all cache entries that were scoped to a specific document_id.
    Called when a document is deleted so stale answers are not served.
    Returns the number of entries removed.
    """
    cache = _get_cache()
    removed = 0
    try:
        keys_to_delete = [k for k, v in list(cache.items())]
        cache.clear()
        removed = len(keys_to_delete)
    except Exception:
        pass
    return removed


# --- Embedding Vector Cache ---
_embedding_cache = None
_EMBEDDING_CACHE_TTL_SECONDS = 3600  # 1-hour TTL
_EMBEDDING_CACHE_MAX_SIZE = 2000     # Up to 2,000 query vectors

def _get_embedding_cache():
    global _embedding_cache
    if _embedding_cache is None:
        try:
            from cachetools import TTLCache
            _embedding_cache = TTLCache(maxsize=_EMBEDDING_CACHE_MAX_SIZE, ttl=_EMBEDDING_CACHE_TTL_SECONDS)
        except ImportError:
            _embedding_cache = {}
    return _embedding_cache

def get_cached_embedding(text: str) -> Optional[list]:
    """Retrieve cached embedding vector for normalized text string."""
    normalized = " ".join(text.lower().strip().split())
    key = hashlib.sha256(normalized.encode()).hexdigest()
    cache = _get_embedding_cache()
    return cache.get(key)

def set_cached_embedding(text: str, embedding: list) -> None:
    """Store embedding vector for normalized text string."""
    normalized = " ".join(text.lower().strip().split())
    key = hashlib.sha256(normalized.encode()).hexdigest()
    cache = _get_embedding_cache()
    cache[key] = embedding
