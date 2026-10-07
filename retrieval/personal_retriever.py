"""
retrieval/personal_retriever.py
--------------------------------
Exclusive retrieval path for personal (user-uploaded) documents.

Security contract:
  Every query MUST supply all three isolation fields:
      user_id, document_id, conversation_id

  The WHERE clause in every Cypher query enforces this triple so that:
    - User A cannot see User B's chunks
    - A document uploaded in Conversation 1 is invisible to Conversation 2
      of the SAME user, unless explicitly re-attached (new upload = new
      document_id bound to the new conversation_id)

Zero-Leakage Policy:
  When PERSONAL_DOCS_EMBEDDING=keyword_only (default) or PERSONAL_CONTEXT_EMBEDDING=off,
  personal document chunks and user queries are NEVER sent to external embedding endpoints.
  Retrieval operates purely via in-memory decrypted keyword search over the isolated chunks.
"""

import re
import math
import base64
import logging
from typing import List, Optional, Dict, Any

from config.settings import settings
from core.crypto import decrypt_text

logger = logging.getLogger("finadvisor.personal_retriever")


def _build_isolation_params(user_id: str, document_id: str, conversation_id: str) -> dict:
    """Return the standard 3-field isolation parameter dict."""
    return {
        "user_id": user_id,
        "document_id": document_id,
        "conversation_id": conversation_id,
    }


def personal_vector_search(
    query: str,
    user_id: str,
    document_id: str,
    conversation_id: str,
    top_k: int = 15,
) -> List[str]:
    """
    Retrieves personal document chunks.
    If PERSONAL_DOCS_EMBEDDING=keyword_only or PERSONAL_CONTEXT_EMBEDDING=off,
    falls back cleanly to private keyword search with zero external API calls.
    """
    mode = getattr(settings, "PERSONAL_DOCS_EMBEDDING", "keyword_only").lower()
    ctx_emb = getattr(settings, "PERSONAL_CONTEXT_EMBEDDING", "off").lower()

    if mode == "keyword_only" or ctx_emb == "off":
        return personal_keyword_search(
            query=query,
            user_id=user_id,
            document_id=document_id,
            conversation_id=conversation_id,
            top_k=top_k,
        )

    # Optional vector search if explicitly enabled
    from core.db import kg, hf
    try:
        query_embedding = hf.embed_query(query)
        if not query_embedding or sum(query_embedding) == 0.0:
            return personal_keyword_search(query, user_id, document_id, conversation_id, top_k)

        cypher = """
        MATCH (c:PersonalChunk {
            user_id:         $user_id,
            document_id:     $document_id,
            conversation_id: $conversation_id
        })
        WHERE c.embedding_v2 IS NOT NULL
        WITH c, vector.similarity.cosine(c.embedding_v2, $query_embedding) AS score
        WHERE score > 0.0
        ORDER BY score DESC
        LIMIT $top_k
        RETURN c.text AS text
        """
        params = {
            **_build_isolation_params(user_id, document_id, conversation_id),
            "query_embedding": query_embedding,
            "top_k": top_k,
        }
        results = kg.query(cypher, params)
        if results:
            decrypted = []
            for row in results:
                enc_b64 = row.get("text")
                if not enc_b64:
                    continue
                try:
                    encrypted_bytes = base64.urlsafe_b64decode(enc_b64.encode())
                    plaintext = decrypt_text(encrypted_bytes)
                    decrypted.append(plaintext)
                except Exception:
                    continue
            if decrypted:
                return decrypted
    except Exception as e:
        logger.warning(f"[personal_retriever] Vector search fallback to keyword: {e}")

    return personal_keyword_search(
        query=query,
        user_id=user_id,
        document_id=document_id,
        conversation_id=conversation_id,
        top_k=top_k,
    )


def personal_keyword_search(
    query: str,
    user_id: str,
    document_id: str,
    conversation_id: str,
    top_k: int = 15,
) -> List[str]:
    """
    Keyword search over PersonalChunk nodes restricted to the 3-field isolation scope.
    Fetches encrypted nodes within the strict user/doc/conversation isolation boundary,
    decrypts them in memory, and scores relevance using term-frequency BM25 heuristics.
    """
    from core.db import kg

    cypher = """
    MATCH (c:PersonalChunk {
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    })
    RETURN c.chunk_id AS chunk_id, c.text AS text, c.chunk_index AS chunk_index
    ORDER BY c.chunk_index ASC
    """
    params = _build_isolation_params(user_id, document_id, conversation_id)

    try:
        results = kg.query(cypher, params)
        if not results:
            return []

        # Extract search tokens
        raw_tokens = re.findall(r'[a-zA-Z0-9_\u20B9$%\.]+', query.lower())
        stop_words = {"what", "when", "where", "which", "how", "the", "and", "for", "with", "from", "that", "this"}
        tokens = [w for w in raw_tokens if len(w) >= 2 and w not in stop_words]

        scored_chunks = []
        for row in results:
            enc_b64 = row.get("text")
            if not enc_b64:
                continue
            try:
                encrypted_bytes = base64.urlsafe_b64decode(enc_b64.encode())
                plaintext = decrypt_text(encrypted_bytes)
            except Exception:
                continue

            plain_lower = plaintext.lower()
            # Calculate match score based on token hits
            score = 0
            if tokens:
                for tok in tokens:
                    if tok in plain_lower:
                        score += 1 + plain_lower.count(tok)
            else:
                score = 1  # If no specific tokens, return sequential chunks

            scored_chunks.append((plaintext, score, row.get("chunk_index", 0)))

        # Sort by score descending, then original index ascending
        scored_chunks.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        return [item[0] for item in scored_chunks[:top_k] if item[1] > 0 or not tokens]

    except Exception as e:
        logger.error(f"[personal_retriever] Keyword search error: {e}")
        return []


def get_all_personal_document_chunks(
    user_id: str,
    document_id: str,
    conversation_id: str,
    limit: int = 20,
) -> List[str]:
    """
    Returns all chunks belonging to the uploaded document within the 3-field isolation scope.
    Used for general questions like 'summarize the pdf', 'what does this statement show', etc.
    """
    from core.db import kg
    cypher = """
    MATCH (c:PersonalChunk {
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    })
    RETURN c.text AS text
    ORDER BY c.chunk_index ASC
    LIMIT $limit
    """
    params = {
        **_build_isolation_params(user_id, document_id, conversation_id),
        "limit": limit,
    }
    try:
        results = kg.query(cypher, params)
        if not results:
            return []
        decrypted = []
        for row in results:
            enc_b64 = row.get("text")
            if not enc_b64:
                continue
            try:
                encrypted_bytes = base64.urlsafe_b64decode(enc_b64.encode())
                plaintext = decrypt_text(encrypted_bytes)
                decrypted.append(plaintext)
            except Exception:
                continue
        return decrypted
    except Exception as e:
        logger.error(f"[personal_retriever] Error reading all personal chunks: {e}")
        return []
