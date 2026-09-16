from typing import List, Union
from langchain_core.documents import Document

def reciprocal_rank_fusion(results_lists: List[List[Union[str, Document]]], k: int = 60) -> List[str]:
    """
    Applies Reciprocal Rank Fusion (RRF) to multiple lists of search results.
    
    Args:
        results_lists: A list containing lists of results. For example: [vector_results, graph_results]
        k: A constant to prevent highly ranked documents from dominating. Default is 60.
        
    Returns:
        A single list of fused, ranked text strings.
    """
    fused_scores = {}
    
    for results in results_lists:
        for rank, doc in enumerate(results):
            # Normalize to string to use as dictionary key
            doc_str = doc if isinstance(doc, str) else doc.page_content
            
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
                
            # RRF Formula: 1 / (k + rank), where rank is 0-indexed
            fused_scores[doc_str] += 1 / (k + rank)
            
    # Sort the dictionary by the RRF score in descending order
    reranked_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return just the text content in the new ranked order
    return [doc for doc, score in reranked_results]

import concurrent.futures

def get_hybrid_rrf_results(query: str, vector_index, graph_retriever_func, top_k: int = 10) -> List[str]:
    """
    Executes both vector and graph retrieval in PARALLEL, then combines them using RRF.
    """
    vector_results = []
    graph_results = []
    
    # Run Neo4j Vector Search and Graph Search simultaneously to cut latency in half
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_vector = executor.submit(vector_index.similarity_search, query, k=top_k)
        future_graph = executor.submit(graph_retriever_func, query)
        
        try:
            vector_results = future_vector.result()
        except Exception as e:
            print(f"Vector search error: {e}")
            
        try:
            graph_results = future_graph.result()
        except Exception as e:
            print(f"Graph search error: {e}")
    
    # 3. Apply Reciprocal Rank Fusion
    fused_results = reciprocal_rank_fusion([vector_results, graph_results])
    
    return fused_results
