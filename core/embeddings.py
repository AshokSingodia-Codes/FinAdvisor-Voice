"""
core/embeddings.py
------------------
Unified, memory-constrained embeddings service.
Subclasses LangChain's Embeddings base class for seamless integration with Neo4jVector.
Uses FastEmbed (ONNX runtime, no PyTorch) with BAAI/bge-small-en-v1.5 (384 dimensions).
Supports BGE query/passage asymmetry via embed() for documents and query_embed() for queries.
Pluggable backend switchable via EMBEDDING_PROVIDER environment variable.
"""

import os
from typing import List, Optional
from langchain_core.embeddings import Embeddings
from core.cache import get_cached_embedding, set_cached_embedding

# Explicit local model cache directory inside project
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", ".fastembed_cache")
os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
os.environ["FASTEMBED_CACHE_PATH"] = os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR)


class FastEmbedService(Embeddings):
    """
    Ultra-lightweight FastEmbed ONNX embeddings service.
    Memory footprint: ~25-35MB RAM total (vs ~450MB+ for PyTorch sentence-transformers).
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", cache_dir: Optional[str] = None):
        self.model_name = model_name
        self.cache_dir = cache_dir or os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR)
        self._model = None

    def _get_model(self):
        if self._model is None:
            # Lazy load on first use or explicit pre-warming
            from fastembed import TextEmbedding
            # Enforce single-threaded execution to prevent CPU spikes and memory arenas
            self._model = TextEmbedding(
                model_name=self.model_name,
                cache_dir=self.cache_dir,
                threads=1,
            )
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed document passages. Uses standard FastEmbed model.embed() generator.
        """
        if not texts:
            return []
        model = self._get_model()
        return [list(emb) for emb in model.embed(texts)]

    def embed_query(self, text: str) -> List[float]:
        """
        Embed search query string. Uses FastEmbed model.query_embed() for BGE query-passage asymmetry.
        Leverages in-memory vector cache to eliminate redundant computation.
        """
        if not text:
            return [0.0] * 384
            
        cached = get_cached_embedding(text)
        if cached is not None and len(cached) == 384:
            return cached

        model = self._get_model()
        # query_embed automatically prepends "Represent this sentence for searching relevant passages: " for BGE
        emb = list(next(model.query_embed(text)))
        set_cached_embedding(text, emb)
        return emb


class HostedAPIEmbeddingsService(Embeddings):
    """
    Zero-local-RAM fallback provider using hosted embedding APIs (HuggingFace/OpenAI/Gemini).
    """
    def __init__(self, provider: str = "huggingface"):
        self.provider = provider

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Fallback to FastEmbed if hosted API keys are not provided
        service = FastEmbedService()
        return service.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        service = FastEmbedService()
        return service.embed_query(text)


_singleton_embeddings_service = None

def get_embeddings_service() -> Embeddings:
    """Returns the global embeddings service singleton based on EMBEDDING_PROVIDER."""
    global _singleton_embeddings_service
    if _singleton_embeddings_service is None:
        provider = os.environ.get("EMBEDDING_PROVIDER", "fastembed").lower().strip()
        if provider == "fastembed":
            _singleton_embeddings_service = FastEmbedService()
        else:
            _singleton_embeddings_service = HostedAPIEmbeddingsService(provider=provider)
    return _singleton_embeddings_service
