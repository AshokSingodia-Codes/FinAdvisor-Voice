import os
from typing import List

_ranker = None

def get_ranker():
    global _ranker
    if _ranker is None:
        try:
            from flashrank import Ranker
            cache_dir = os.path.join(os.getcwd(), ".cache", "flashrank")
            os.makedirs(cache_dir, exist_ok=True)
            _ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=cache_dir)
        except Exception as e:
            print(f"Warning: FlashRank lazy load deferred: {e}")
            return None
    return _ranker

def cross_encode_rerank(query: str, documents: List[str], top_k: int = 3) -> List[str]:
    """
    Reranks a list of text strings against a query using FlashRank cross-encoder.
    
    Args:
        query: The user's question.
        documents: The list of documents (from RRF) to rerank.
        top_k: How many top documents to return.
    """
    if not documents:
        return []
        
    ranker_instance = get_ranker()
    if ranker_instance is None:
        # Graceful fallback: return top documents as is
        return documents[:top_k]

    try:
        from flashrank import RerankRequest
        passages = []
        for i, doc in enumerate(documents):
            passages.append({
                "id": i,
                "text": doc,
                "meta": {}
            })
            
        rerankrequest = RerankRequest(query=query, passages=passages)
        results = ranker_instance.rerank(rerankrequest)
        
        top_docs = []
        for res in results[:top_k]:
            top_docs.append(res["text"])
        return top_docs
    except Exception as e:
        print(f"Warning: Rerank error: {e}")
        return documents[:top_k]
