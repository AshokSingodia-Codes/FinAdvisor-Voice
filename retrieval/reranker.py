from flashrank import Ranker, RerankRequest
import os
from typing import List

# Initialize ranker (this will download a tiny model on first run)
# We use a very lightweight model to save RAM.
cache_dir = os.path.join(os.getcwd(), ".cache", "flashrank")
os.makedirs(cache_dir, exist_ok=True)

ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=cache_dir)

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
        
    # FlashRank expects a list of dictionaries with 'id' and 'text'
    passages = []
    for i, doc in enumerate(documents):
        passages.append({
            "id": i,
            "text": doc,
            "meta": {}
        })
        
    rerankrequest = RerankRequest(query=query, passages=passages)
    
    # Rerank
    results = ranker.rerank(rerankrequest)
    
    # Extract the top_k text strings
    top_docs = []
    for res in results[:top_k]:
        top_docs.append(res['text'])
        
    return top_docs
