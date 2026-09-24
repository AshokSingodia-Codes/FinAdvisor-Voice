from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import kg, vector_index, fast_chat, get_structured_fast_chat
from config.settings import settings
from retrieval.hybrid_rrf import reciprocal_rank_fusion, get_personal_rrf_results
from retrieval.reranker import cross_encode_rerank

import re

class Entities(BaseModel):
    names: List[str] = Field(description="List of person, organization, or business entities", default_factory=list)

entity_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract organization and person entities from the text."),
    ("human", "Extract all the entities from the following input: {question}")
])
entity_chain = entity_prompt | get_structured_fast_chat(Entities)

def _build_lucene_search_query(text: str) -> str:
    """Extracts meaningful alphanumeric terms and constructs a Lucene OR query."""
    words = re.findall(r'[a-zA-Z0-9_\u20B9$%\.]+', text)
    stopwords = {"what", "were", "was", "the", "in", "of", "and", "for", "to", "a", "is", "how", "did", "does", "by", "an", "on", "from", "at"}
    meaningful = [w for w in words if w.lower() not in stopwords and len(w) >= 2]
    if not meaningful:
        meaningful = words
    return " OR ".join(meaningful) if meaningful else text

def structured_retriever(question: str, top_k: int = 15) -> List[str]:
    """
    Hybrid Keyword & Graph Retriever:
    1. Executes Lucene full-text BM25 search over Chunk text (index: keyword_markdown).
    2. Traverses graph relationship triples for key extracted entities.
    """
    results_list: List[str] = []
    seen_texts = set()

    # 1. Native Lucene BM25 Fulltext Search over shared Chunk nodes
    lucene_expr = _build_lucene_search_query(question)
    if lucene_expr:
        try:
            cypher_fulltext = """
            CALL db.index.fulltext.queryNodes("keyword_markdown", $query)
            YIELD node, score
            WHERE node.text IS NOT NULL
            RETURN node.text AS text, score
            ORDER BY score DESC
            LIMIT $top_k
            """
            ft_results = kg.query(cypher_fulltext, {"query": lucene_expr, "top_k": top_k})
            for r in ft_results:
                txt = r.get("text", "").strip()
                if txt and txt not in seen_texts:
                    seen_texts.add(txt)
                    results_list.append(txt)
        except Exception as e:
            print(f"[structured_retriever] Fulltext index search notice: {e}")

    # 2. Graph Entity Relationship Traversal
    try:
        entities = entity_chain.invoke({"question": question})
        for entity in entities.names:
            if not entity or len(entity.strip()) < 2:
                continue
            response = kg.query(
                """
                MATCH (node:__Entity__)
                WHERE node.id =~ $query
                MATCH (node)-[r]->(neighbor)
                RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                UNION ALL
                MATCH (node:__Entity__)<-[r]-(neighbor)
                WHERE node.id =~ $query
                RETURN neighbor.id + ' - ' + type(r) + ' -> ' + node.id AS output
                LIMIT 20
                """,
                {"query": f"(?i).*{entity.strip()}.*"}
            )
            for el in response:
                out = el.get("output", "").strip()
                if out and out not in seen_texts:
                    seen_texts.add(out)
                    results_list.append(out)
    except Exception as e:
        print(f"[structured_retriever] Entity relationship search notice: {e}")

    return results_list

def retrieve_context(state: AgentState):
    print("---NODE: RETRIEVER---")

    document_id = state.get("document_id")

    # -------------------------------------------------------------------------
    # EXCLUSIVE PERSONAL DOCUMENT PATH
    # When a document_id is active, we search ONLY the personal document.
    # The shared corpus is never touched in this branch.
    #
    # All three isolation fields are mandatory:
    #   user_id         — prevents cross-user leakage
    #   document_id     — scopes to the specific uploaded document
    #   conversation_id — prevents cross-conversation leakage (same user,
    #                     different conversation → no access to this document)
    # -------------------------------------------------------------------------
    if document_id:
        user_id = state.get("user_id", "")
        conversation_id = state.get("conversation_id", "")
        print(f"  [Mode: PERSONAL DOCUMENT] doc={document_id} user={user_id} conv={conversation_id}")

        queries_to_run = state.get("decomposed_questions", [])
        if not queries_to_run:
            queries_to_run = [state.get("current_question", state.get("original_question", ""))]

        existing_context = state.get("retrieved_context", [])

        for q in queries_to_run:
            if not q:
                continue
            print(f"  Retrieving personal doc context for: {q}")

            # Exclusive personal RRF — 3-field isolation enforced inside
            fused = get_personal_rrf_results(
                query=q,
                user_id=user_id,
                document_id=document_id,
                conversation_id=conversation_id,
                top_k=15,
            )
            # Context-Bounded Top-4 FlashRank neural cross-encoder reranking
            reranked = cross_encode_rerank(query=q, documents=fused[:20], top_k=4)
            existing_context.extend(reranked)

        return {"retrieved_context": existing_context}

    # -------------------------------------------------------------------------
    # SHARED CORPUS PATH (unchanged)
    # Used when no personal document is attached to this conversation.
    # -------------------------------------------------------------------------
    print("  [Mode: SHARED CORPUS]")
    queries_to_run = state.get("decomposed_questions", [])
    if not queries_to_run:
        queries_to_run = [state.get("current_question", state.get("original_question", ""))]

    existing_context = state.get("retrieved_context", [])

    for q in queries_to_run:
        if not q: continue
        print(f"  Retrieving for: {q}")
        graph_list = structured_retriever(q)
        vector_docs = vector_index.similarity_search(q, k=15)

        fused_results = reciprocal_rank_fusion([vector_docs, graph_list], k=settings.RRF_K)
        # Context-Bounded Top-4 FlashRank neural cross-encoder reranking
        reranked_results = cross_encode_rerank(query=q, documents=fused_results[:20], top_k=4)

        existing_context.extend(reranked_results)

    return {"retrieved_context": existing_context}

