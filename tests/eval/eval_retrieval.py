"""
Step 1 — Retrieval-Only Benchmark & Reranker Lift Evaluation
Compares:
  1. Vector-Only Search
  2. Keyword / Graph Search
  3. Hybrid Search (RRF)
  4. Hybrid Search (RRF + FlashRank Cross-Encoder Reranker)

Calculates Precision@5, Recall@5, MRR, and empirical Reranker Lift.
"""
import os
import sys
import json
import time
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import settings
from core.db import vector_index, kg
from nodes.retriever import structured_retriever
from retrieval.hybrid_rrf import reciprocal_rank_fusion
from retrieval.reranker import cross_encode_rerank

def load_gold_set(filepath: str = None) -> List[Dict[str, Any]]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "gold_set.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def is_chunk_relevant(chunk_text: str, gold_keywords: List[str]) -> bool:
    """Checks if a retrieved text chunk contains key required gold phrases."""
    if not chunk_text or not gold_keywords:
        return False
    lower_chunk = chunk_text.lower()
    # Relevant if at least one multi-word key phrase or majority of keywords match
    matches = sum(1 for kw in gold_keywords if kw.lower() in lower_chunk)
    return matches >= max(1, len(gold_keywords) // 2)

def compute_metrics(retrieved_docs: List[str], gold_keywords: List[str], k: int = 5) -> Dict[str, float]:
    top_k_docs = retrieved_docs[:k]
    if not top_k_docs:
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0}
    
    relevant_retrieved = 0
    first_relevant_rank = 0
    
    for rank, doc in enumerate(top_k_docs, start=1):
        if is_chunk_relevant(doc, gold_keywords):
            relevant_retrieved += 1
            if first_relevant_rank == 0:
                first_relevant_rank = rank
                
    precision_at_k = relevant_retrieved / k
    # Recall against gold keywords present across top-k
    found_keywords = set()
    for doc in top_k_docs:
        for kw in gold_keywords:
            if kw.lower() in doc.lower():
                found_keywords.add(kw.lower())
    recall_at_k = len(found_keywords) / max(len(gold_keywords), 1)
    
    mrr = (1.0 / first_relevant_rank) if first_relevant_rank > 0 else 0.0
    
    return {
        "precision_at_k": precision_at_k,
        "recall_at_k": recall_at_k,
        "mrr": mrr
    }

def run_retrieval_evaluation(gold_set_path: str = None, top_k: int = 5) -> Dict[str, Any]:
    questions = load_gold_set(gold_set_path)
    # Filter to in-corpus factual, textbook, and literature questions
    eval_subset = [q for q in questions if not q.get("is_out_of_corpus", False) and q.get("category") != "computational_market"]
    
    print(f"\n=======================================================")
    print(f"📊 FinAdvisor-X Retrieval & Reranker Benchmark")
    print(f"=======================================================")
    print(f"Evaluating {len(eval_subset)} in-corpus gold queries across 4 retrieval pipelines...\n")
    
    modes = ["vector_only", "keyword_only", "hybrid_rrf", "hybrid_rrf_flashrank"]
    results = {mode: {"precision": [], "recall": [], "mrr": [], "latencies": []} for mode in modes}
    
    for i, item in enumerate(eval_subset, 1):
        q = item["question"]
        gold_kws = item.get("gold_keywords", [])
        
        # 1. Vector-Only
        t0 = time.time()
        try:
            vec_docs = [d.page_content if hasattr(d, 'page_content') else str(d) for d in vector_index.similarity_search(q, k=15)]
        except Exception:
            vec_docs = []
        t_vec = time.time() - t0
        
        # 2. Keyword/Graph-Only
        t0 = time.time()
        try:
            kw_docs = structured_retriever(q)
        except Exception:
            kw_docs = []
        t_kw = time.time() - t0
        
        # 3. Hybrid RRF (No Reranker)
        t0 = time.time()
        fused_docs = reciprocal_rank_fusion([vec_docs, kw_docs], k=settings.RRF_K)
        t_rrf = (time.time() - t0) + max(t_vec, t_kw)
        
        # 4. Hybrid RRF + FlashRank Reranker
        t0 = time.time()
        reranked_docs = cross_encode_rerank(query=q, documents=fused_docs[:20], top_k=top_k)
        t_rerank = (time.time() - t0) + t_rrf
        
        # Score each
        m_vec = compute_metrics(vec_docs, gold_kws, k=top_k)
        m_kw = compute_metrics(kw_docs, gold_kws, k=top_k)
        m_rrf = compute_metrics(fused_docs, gold_kws, k=top_k)
        m_rerank = compute_metrics(reranked_docs, gold_kws, k=top_k)
        
        for mode, m, lat in [
            ("vector_only", m_vec, t_vec),
            ("keyword_only", m_kw, t_kw),
            ("hybrid_rrf", m_rrf, t_rrf),
            ("hybrid_rrf_flashrank", m_rerank, t_rerank)
        ]:
            results[mode]["precision"].append(m["precision_at_k"])
            results[mode]["recall"].append(m["recall_at_k"])
            results[mode]["mrr"].append(m["mrr"])
            results[mode]["latencies"].append(lat)
            
        print(f"[{i:02d}/{len(eval_subset):02d}] {q[:50]}... | FlashRank P@5: {m_rerank['precision_at_k']:.2f}, R@5: {m_rerank['recall_at_k']:.2f}, MRR: {m_rerank['mrr']:.2f}")

    # Aggregations
    summary = {}
    for mode in modes:
        n = max(len(results[mode]["precision"]), 1)
        summary[mode] = {
            "avg_precision_at_k": round(sum(results[mode]["precision"]) / n, 4),
            "avg_recall_at_k": round(sum(results[mode]["recall"]) / n, 4),
            "avg_mrr": round(sum(results[mode]["mrr"]) / n, 4),
            "avg_latency_sec": round(sum(results[mode]["latencies"]) / n, 4)
        }
        
    # Empirical Reranker Lift
    vec_p = summary["vector_only"]["avg_precision_at_k"]
    vec_r = summary["vector_only"]["avg_recall_at_k"]
    final_p = summary["hybrid_rrf_flashrank"]["avg_precision_at_k"]
    final_r = summary["hybrid_rrf_flashrank"]["avg_recall_at_k"]
    
    lift = {
        "precision_lift_vs_vector_pct": round(((final_p - vec_p) / max(vec_p, 0.001)) * 100, 2),
        "recall_lift_vs_vector_pct": round(((final_r - vec_r) / max(vec_r, 0.001)) * 100, 2),
        "precision_lift_from_flashrank_pct": round(((final_p - summary["hybrid_rrf"]["avg_precision_at_k"]) / max(summary["hybrid_rrf"]["avg_precision_at_k"], 0.001)) * 100, 2)
    }
    
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries_evaluated": len(eval_subset),
        "top_k": top_k,
        "configurations": summary,
        "empirical_lift": lift
    }
    
    # Save results to reports/
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, "retrieval_eval.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print("\n=======================================================")
    print("📈 RETRIEVAL & RERANKER BENCHMARK SUMMARY (k=5)")
    print("=======================================================")
    print(f"| Configuration             | Precision@5 | Recall@5  | MRR     | Latency   |")
    print(f"|---------------------------|-------------|-----------|---------|-----------|")
    for mode, data in summary.items():
        mode_name = mode.replace("_", " ").title()
        print(f"| {mode_name:<25} | {data['avg_precision_at_k']:<11.3f} | {data['avg_recall_at_k']:<9.3f} | {data['avg_mrr']:<7.3f} | {data['avg_latency_sec']*1000:<7.1f}ms |")
    print("-------------------------------------------------------")
    print(f"🚀 Hybrid RRF Recall Lift over Vector-only:    +{lift['recall_lift_vs_vector_pct']}%")
    print(f"🎯 FlashRank Precision Lift over Hybrid RRF:  +{lift['precision_lift_from_flashrank_pct']}%")
    print(f"💾 Report saved to: {report_file}")
    print("=======================================================\n")
    
    return report_data

if __name__ == "__main__":
    run_retrieval_evaluation()
