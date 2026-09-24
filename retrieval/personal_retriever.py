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

This module is intentionally separate from the shared-corpus retrieval
path (hybrid_rrf.py / core/db.py vector_index).  The two code paths
must NEVER be blended in a single query.  If blended retrieval is ever
required, it must be implemented as a distinct, separately-reviewed
feature with its own security analysis.
"""

from typing import List
from core.db import hf as embeddings


# ---------------------------------------------------------------------------
# Cypher helpers
# ---------------------------------------------------------------------------

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
    Cosine-similarity vector search restricted to PersonalChunk nodes
    that match ALL THREE isolation fields.
    """
    from core.db import kg

    query_embedding = embeddings.embed_query(query)

    # Path 1: Neo4j 5.x native vector similarity
    cypher_native = """
    MATCH (c:PersonalChunk {
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    })
    WHERE c.embedding IS NOT NULL
    WITH c, vector.similarity.cosine(c.embedding, $query_embedding) AS score
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

    try:
        results = kg.query(cypher_native, params)
        if results:
            return [row["text"] for row in results if row.get("text")]
    except Exception:
        # Path 2: GDS cosine similarity procedure
        cypher_gds = """
        MATCH (c:PersonalChunk {
            user_id:         $user_id,
            document_id:     $document_id,
            conversation_id: $conversation_id
        })
        WHERE c.embedding IS NOT NULL
        WITH c, gds.similarity.cosine(c.embedding, $query_embedding) AS score
        WHERE score > 0.0
        ORDER BY score DESC
        LIMIT $top_k
        RETURN c.text AS text
        """
        try:
            results = kg.query(cypher_gds, params)
            if results:
                return [row["text"] for row in results if row.get("text")]
        except Exception:
            pass

    # Path 3: In-memory exact cosine fallback
    return _personal_vector_search_fallback(
        query_embedding=query_embedding,
        user_id=user_id,
        document_id=document_id,
        conversation_id=conversation_id,
        top_k=top_k,
    )


def _personal_vector_search_fallback(
    query_embedding: List[float],
    user_id: str,
    document_id: str,
    conversation_id: str,
    top_k: int,
) -> List[str]:
    """
    Brute-force cosine similarity over PersonalChunk nodes.
    The 3-field isolation filter is strictly enforced.
    """
    import math
    from core.db import kg

    cypher = """
    MATCH (c:PersonalChunk {
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    })
    WHERE c.embedding IS NOT NULL
    RETURN c.text AS text, c.embedding AS embedding
    """
    params = _build_isolation_params(user_id, document_id, conversation_id)
    try:
        rows = kg.query(cypher, params)
    except Exception as e:
        print(f"[personal_retriever] Fallback query error: {e}")
        return []

    def cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    scored = []
    for row in rows:
        text = row.get("text")
        emb = row.get("embedding")
        if text and emb:
            scored.append((text, cosine(query_embedding, emb)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in scored[:top_k]]


def personal_keyword_search(
    query: str,
    user_id: str,
    document_id: str,
    conversation_id: str,
    top_k: int = 15,
) -> List[str]:
    """
    Keyword search over PersonalChunk nodes restricted to the 3-field isolation scope.
    """
    from core.db import kg
    import re

    # Extract tokens with alphanumeric characters
    raw_tokens = re.findall(r'[a-zA-Z0-9_\u20B9$%\.]+', query.lower())
    tokens = [w for w in raw_tokens if len(w) >= 3 and w not in {"what", "when", "where", "which", "how", "the", "and", "for", "with"}]
    if not tokens:
        tokens = [w for w in raw_tokens if len(w) >= 2]
    if not tokens:
        return []

    # Clean tokens for safe cypher string matching
    safe_tokens = [re.sub(r'[^a-zA-Z0-9_\u20B9$%\.]', '', t) for t in tokens[:6] if t]
    if not safe_tokens:
        return []

    token_conditions = " OR ".join(
        f"toLower(c.text) CONTAINS '{tok}'" for tok in safe_tokens
    )

    cypher = f"""
    MATCH (c:PersonalChunk {{
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    }})
    WHERE {token_conditions}
    RETURN c.text AS text
    LIMIT $top_k
    """

    params = {
        **_build_isolation_params(user_id, document_id, conversation_id),
        "top_k": top_k,
    }

    try:
        results = kg.query(cypher, params)
        return [row["text"] for row in results if row.get("text")]
    except Exception as e:
        print(f"[personal_retriever] Keyword search error: {e}")
        return []


def get_all_personal_document_chunks(
    user_id: str,
    document_id: str,
    conversation_id: str,
    limit: int = 20,
) -> List[str]:
    """
    Returns all chunks belonging to the uploaded document within the 3-field isolation scope.
    Used as a fallback for general questions like 'summarize the pdf', 'do you get the file', etc.
    """
    from core.db import kg
    cypher = """
    MATCH (c:PersonalChunk {
        user_id:         $user_id,
        document_id:     $document_id,
        conversation_id: $conversation_id
    })
    RETURN c.text AS text
    LIMIT $limit
    """
    params = {
        **_build_isolation_params(user_id, document_id, conversation_id),
        "limit": limit,
    }
    try:
        results = kg.query(cypher, params)
        return [row["text"] for row in results if row.get("text")]
    except Exception as e:
        print(f"[personal_retriever] get_all_personal_document_chunks error: {e}")
        return []

