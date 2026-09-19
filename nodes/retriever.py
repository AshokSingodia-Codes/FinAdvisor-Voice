from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import kg, vector_index, chat, get_structured_chat
from config.settings import settings
from retrieval.hybrid_rrf import reciprocal_rank_fusion
from retrieval.reranker import cross_encode_rerank

class Entities(BaseModel):
    names: List[str] = Field(description="List of person, organization, or business entities")

entity_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract organization and person entities from the text."),
    ("human", "Extract all the entities from the following input: {question}")
])
entity_chain = entity_prompt | get_structured_chat(Entities)

def structured_retriever(question: str) -> List[str]:
    results_list = []
    entities = entity_chain.invoke({"question": question})
    for entity in entities.names:
        response = kg.query(
            """
            MATCH (node)
            WHERE node.name =~ $query
            OR node.id =~ $query
            WITH node
            MATCH (node)-[r]->(neighbor)
            RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
            UNION ALL
            MATCH (node)<-[r]-(neighbor)
            WHERE node.name =~ $query
            OR node.id =~ $query
            RETURN neighbor.id + ' - ' + type(r) + ' -> ' + node.id AS output
            LIMIT 50
            """,
            {"query": f"(?i).*{entity}.*"}
        )
        results_list.extend([el["output"] for el in response])
    return results_list

def retrieve_context(state: AgentState):
    print("---NODE: RETRIEVER---")
    
    # Process decomposed questions if they exist, otherwise the original question
    queries_to_run = state.get("decomposed_questions", [])
    if not queries_to_run:
        queries_to_run = [state.get("current_question", state.get("original_question", ""))]
        
    existing_context = state.get("retrieved_context", [])
    
    for q in queries_to_run:
        if not q: continue
        print(f"Retrieving for: {q}")
        graph_list = structured_retriever(q)
        vector_docs = vector_index.similarity_search(q, k=15)
        
        fused_results = reciprocal_rank_fusion([vector_docs, graph_list], k=settings.RRF_K)
        reranked_results = cross_encode_rerank(query=q, documents=fused_results[:20], top_k=5)
        
        existing_context.extend(reranked_results)
    
    return {"retrieved_context": existing_context}
