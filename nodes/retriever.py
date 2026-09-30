from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import kg, vector_index, fast_chat, get_structured_fast_chat
from config.settings import settings
from retrieval.hybrid_rrf import reciprocal_rank_fusion, get_personal_rrf_results
from retrieval.reranker import cross_encode_rerank

import re
import os
import concurrent.futures

_LOCAL_GUIDE_CHUNKS = None

def _get_local_guide_chunks():
    global _LOCAL_GUIDE_CHUNKS
    if _LOCAL_GUIDE_CHUNKS is None:
        guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "personal_finance_and_tax_guide.md")
        if os.path.exists(guide_path):
            try:
                with open(guide_path, "r", encoding="utf-8") as f:
                    content = f.read()
                sections = re.split(r'\n(?=#{1,3}\s+)', content)
                _LOCAL_GUIDE_CHUNKS = [s.strip() for s in sections if len(s.strip()) > 40]
            except Exception as e:
                print(f"[retriever] Error loading personal_finance_and_tax_guide.md: {e}")
                _LOCAL_GUIDE_CHUNKS = []
        else:
            _LOCAL_GUIDE_CHUNKS = []
    return _LOCAL_GUIDE_CHUNKS

def _search_local_guide(query: str, top_k: int = 3) -> List[str]:
    chunks = _get_local_guide_chunks()
    if not chunks:
        return []
    q_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) >= 3]
    if not q_words:
        return chunks[:top_k]
    
    scored = []
    for c in chunks:
        c_lower = c.lower()
        score = sum(2 if w in c_lower else 0 for w in q_words)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]] if scored else chunks[:2]

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
    Executes Lucene BM25 full-text search and Graph Entity traversal in PARALLEL.
    """
    results_list: List[str] = []
    seen_texts = set()

    def _lucene_search() -> List[str]:
        items = []
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
                    if txt:
                        items.append(txt)
            except Exception as e:
                print(f"[structured_retriever] Fulltext index search notice: {e}")
        return items

    def _graph_search() -> List[str]:
        items = []
        try:
            # Fast heuristic extraction for potential entity names (capitalized words, tickers, organization names)
            potential_entities = re.findall(r'\b[A-Z][a-zA-Z0-9_\-\.]{2,}\b', question)
            stopwords = {"What", "Where", "When", "Which", "Could", "Would", "Should", "There", "Their", "About", "Calculate", "Explain", "How", "Does", "Show"}
            candidate_names = [e for e in potential_entities if e not in stopwords]

            if not candidate_names:
                return []

            for entity in candidate_names[:3]:
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
                    if out:
                        items.append(out)
        except Exception as e:
            print(f"[structured_retriever] Entity relationship search notice: {e}")
        return items

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f_lucene = executor.submit(_lucene_search)
        f_graph = executor.submit(_graph_search)
        lucene_items = f_lucene.result()
        graph_items = f_graph.result()

    for txt in lucene_items + graph_items:
        if txt not in seen_texts:
            seen_texts.add(txt)
            results_list.append(txt)

    return results_list

def retrieve_shared_corpus_concurrent(query: str, top_k: int = 4, apply_rerank: bool = True) -> List[str]:
    """
    Executes vector, keyword/graph, and local guide retrieval in parallel using ThreadPoolExecutor,
    fuses candidates via Reciprocal Rank Fusion (RRF), and optionally applies FlashRank cross-encoding.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_kw = executor.submit(structured_retriever, query)
        future_vec = executor.submit(vector_index.similarity_search, query, k=15)
        future_guide = executor.submit(_search_local_guide, query, top_k=3)

        graph_list = future_kw.result()
        vector_docs = future_vec.result()
        local_guide_results = future_guide.result()

    fused_results = reciprocal_rank_fusion([vector_docs, graph_list, local_guide_results], k=settings.RRF_K)
    if not apply_rerank:
        return fused_results[:top_k]

    reranked_results = cross_encode_rerank(query=query, documents=fused_results[:15], top_k=top_k)
    if not reranked_results and local_guide_results:
        reranked_results = local_guide_results[:2]
    return reranked_results

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
            queries_to_run = [state.get("resolved_query") or state.get("current_question") or state.get("original_question", "")]

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
    # SHARED CORPUS PATH (Parallelized)
    # Used when no personal document is attached to this conversation.
    # -------------------------------------------------------------------------
    print("  [Mode: SHARED CORPUS]")
    queries_to_run = state.get("decomposed_questions", [])
    if not queries_to_run:
        queries_to_run = [state.get("resolved_query") or state.get("current_question") or state.get("original_question", "")]

    existing_context = state.get("retrieved_context", [])

    for q in queries_to_run:
        if not q: continue
        print(f"  Retrieving for: {q}")
        reranked_results = retrieve_shared_corpus_concurrent(q, top_k=4, apply_rerank=True)
        existing_context.extend(reranked_results)

    return {"retrieved_context": existing_context}

