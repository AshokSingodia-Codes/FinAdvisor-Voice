"""
core/db.py
----------
Database connections, Vector Stores, and Resilient Multi-Provider LLM Services.

- Vector Index: Neo4j Aura vector_markdown_v2 (768 dimensions, cosine similarity)
- Embeddings: Zero-local-RAM hosted Gemini embeddings (core/embeddings.py)
- LLMs: Dual-tier ResilientFallbackChat (Groq -> Gemini -> OpenRouter) with circuit breakers
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel

from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_core.embeddings import Embeddings

from config.settings import settings
from core.embeddings import get_embedding_service
from core.llm_manager import ResilientFallbackChat

logger = logging.getLogger("finadvisor.db")

# 1. Hosted Embeddings Service (Zero local memory footprint)
hf = get_embedding_service()

# 2. Neo4j Graph Connection (refresh_schema=False to prevent eager connection on import)
kg = Neo4jGraph(
    url=settings.NEO4J_URI,
    username=settings.NEO4J_USERNAME,
    password=settings.NEO4J_PASSWORD,
    database=getattr(settings, "NEO4J_DATABASE", settings.NEO4J_USERNAME),
    refresh_schema=False,
)

# 3. Neo4j Vector Store (points to vector_markdown_v2 if enabled)
vector_index = None
if getattr(settings, "VECTOR_SEARCH_ENABLED", False):
    index_name = getattr(settings, "VECTOR_INDEX_NAME", "vector_markdown_v2")
    try:
        vector_index = Neo4jVector.from_existing_graph(
            embedding=hf,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            database=getattr(settings, "NEO4J_DATABASE", settings.NEO4J_USERNAME),
            index_name=index_name,
            node_label="Chunk",
            text_node_properties=["text"],
            embedding_node_property="embedding_v2",
        )
    except Exception as _v_err:
        logger.warning(f"[core/db] Neo4jVector initialization deferred/warning: {_v_err}")
        vector_index = None
else:
    logger.info("[core/db] VECTOR_SEARCH_ENABLED is False; operating in safe Zero-Embedding Keyword+Graph mode.")

# 4. Resilient LLM Services
# A. Fast Tier (Router, Decomposer, Entities, Verifier, Solver)
fast_chat = ResilientFallbackChat(
    tier="fast",
    has_personal_context=False,
    temperature=0.0,
    max_tokens=256,
)

# B. Synthesis Tier (Evidence Builder, complex advisory response)
synthesis_chat = ResilientFallbackChat(
    tier="synthesis",
    has_personal_context=False,
    temperature=0.0,
    max_tokens=1000,
)
chat = synthesis_chat


def get_structured_fast_chat(schema: Any, **kwargs: Any) -> Any:
    """Returns a fast LLM configured to produce validated structured output."""
    return fast_chat.with_structured_output(schema, **kwargs)


def get_structured_synthesis_chat(schema: Any, **kwargs: Any) -> Any:
    """Returns a synthesis LLM configured to produce validated structured output."""
    return synthesis_chat.with_structured_output(schema, **kwargs)


def get_structured_chat(schema: Any, **kwargs: Any) -> Any:
    """Alias for structured synthesis chat."""
    return get_structured_synthesis_chat(schema, **kwargs)
