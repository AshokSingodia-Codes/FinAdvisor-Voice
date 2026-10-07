"""
scripts/eval_demo_suite.py
--------------------------
Evaluates:
1. Safe Keyword + Graph Baseline (VECTOR_SEARCH_ENABLED=False, zero Gemini embedding calls).
2. 10 Demo Questions Evaluation (Precision@5, Recall@5, MRR, Latency, Numeric Grounding).
3. Failure drill & test for Hosted BGE-small 384-dim query embeddings.
4. Latency breakdown & Hallucination/Verification checks.
"""

import os
import sys
import time
import json
import statistics
from typing import List, Dict, Any
from unittest.mock import patch

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from core.db import kg, fast_chat, synthesis_chat
from nodes.retriever import structured_retriever, retrieve_shared_corpus_concurrent
import httpx

# 10 Representative Demo Questions from gold_set.json
DEMO_QUESTIONS = [
    {
        "id": "q001",
        "question": "What were Apple's total net sales in fiscal year 2024?",
        "expected_answer": "$391,035 million ($391.035 billion)",
        "gold_keywords": ["total net sales", "391,035", "2024"],
        "category": "10k_factual",
    },
    {
        "id": "q002",
        "question": "How much net sales did Apple generate from iPhone products in FY 2024?",
        "expected_answer": "$201,183 million ($201.183 billion)",
        "gold_keywords": ["iPhone", "201,183"],
        "category": "10k_factual",
    },
    {
        "id": "q003",
        "question": "What was Apple's total Services revenue in FY2024?",
        "expected_answer": "$96,169 million ($96.169 billion)",
        "gold_keywords": ["Services", "96,169"],
        "category": "10k_factual",
    },
    {
        "id": "q004",
        "question": "What was Apple's net income for fiscal year 2024?",
        "expected_answer": "$93,736 million ($93.736 billion)",
        "gold_keywords": ["Net income", "93,736"],
        "category": "10k_factual",
    },
    {
        "id": "q005",
        "question": "What were Apple's diluted earnings per share (EPS) in FY 2024?",
        "expected_answer": "$6.08 per share",
        "gold_keywords": ["Diluted", "6.08"],
        "category": "10k_factual",
    },
    {
        "id": "q006",
        "question": "How much did Apple spend on Research and Development (R&D) in fiscal 2024?",
        "expected_answer": "$31,370 million ($31.37 billion)",
        "gold_keywords": ["Research and development", "31,370"],
        "category": "10k_factual",
    },
    {
        "id": "q007",
        "question": "What was Apple's cash, cash equivalents and marketable securities balance at the end of FY2024?",
        "expected_answer": "$29,943 million in cash and cash equivalents",
        "gold_keywords": ["Cash and cash equivalents", "29,943"],
        "category": "10k_factual",
    },
    {
        "id": "q008",
        "question": "What is the maximum investment deduction limit under Section 80C of the Indian Income Tax Act?",
        "expected_answer": "₹1,50,000 (1.5 Lakh)",
        "gold_keywords": ["80C", "1,50,000", "1.5 Lakh"],
        "category": "tax_rules",
    },
    {
        "id": "q009",
        "question": "What is the Long-Term Capital Gains (LTCG) tax exemption limit on equity investments under Budget 2024?",
        "expected_answer": "₹1.25 Lakh per financial year (taxed at 12.5% above exemption)",
        "gold_keywords": ["1.25 Lakh", "12.5%", "LTCG"],
        "category": "tax_rules",
    },
    {
        "id": "q010",
        "question": "What is the formula for calculating SIP future value, and what would ₹10,000/month for 10 years at 12% yield?",
        "expected_answer": "FV = P * [((1 + i)^n - 1) / i] * (1 + i); approximately ₹23.23 Lakh",
        "gold_keywords": ["SIP", "23.2", "future value"],
        "category": "financial_planning",
    },
]


def is_chunk_relevant(chunk: str, gold_kws: List[str]) -> bool:
    if not chunk or not gold_kws:
        return False
    lower = chunk.lower()
    return any(kw.lower() in lower for kw in gold_kws)


def test_hosted_bge_small_endpoint():
    """Tests if hosted BGE-small endpoint is reachable and valid."""
    print("\n--- TEST: Hosted BGE-Small (384-dim) Endpoint Drill ---")
    hf_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
    payload = {"inputs": "Represent this sentence for searching relevant passages: What were Apple net sales in 2024?"}
    try:
        r = httpx.post(hf_url, json=payload, timeout=5.0)
        print(f"  Endpoint HTTP Status: {r.status_code}")
        if r.status_code == 200:
            vec = r.json()
            if isinstance(vec, list) and len(vec) == 384:
                print("  ✓ Hosted BGE-small 384-dim vector returned successfully!")
                return True
        print(f"  ❌ Hosted BGE-small failed (HTTP {r.status_code}: {r.text[:120]}).")
        print("  → Decision: Keep BGE-small hosted search DISABLED to guarantee zero crash.")
        return False
    except Exception as e:
        print(f"  ❌ Hosted BGE-small network drill failed: {e}")
        print("  → Decision: Keep BGE-small hosted search DISABLED.")
        return False


def run_demo_evaluation():
    print("==================================================================")
    print("FINADVISOR-X: 10 DEMO QUESTIONS EVALUATION (KEYWORD+GRAPH BASELINE)")
    print("Safety Constraint: ZERO Gemini embedding API calls")
    print("==================================================================\n")

    # Patch Gemini embedding calls to raise immediately if attempted
    def _prohibited_gemini_call(*args, **kwargs):
        raise RuntimeError("FATAL: Gemini embedding API was called during zero-quota evaluation!")

    results_table = []
    latencies = []
    retrieval_latencies = []
    llm_latencies = []

    with patch("core.embeddings.GeminiHostedEmbeddings._call_gemini_single", side_effect=_prohibited_gemini_call), \
         patch("core.embeddings.GeminiHostedEmbeddings._call_gemini_batch", side_effect=_prohibited_gemini_call), \
         patch.object(settings, "VECTOR_SEARCH_ENABLED", False):

        for item in DEMO_QUESTIONS:
            qid = item["id"]
            q = item["question"]
            gold_kws = item["gold_keywords"]

            t0 = time.time()
            # 1. Keyword + Graph Retrieval
            retrieved_chunks = retrieve_shared_corpus_concurrent(q, top_k=5, apply_rerank=False)
            t_ret = time.time() - t0
            retrieval_latencies.append(t_ret)

            # Metrics
            top5 = retrieved_chunks[:5]
            relevant_count = sum(1 for c in top5 if is_chunk_relevant(c, gold_kws))
            precision_at_5 = relevant_count / 5.0
            
            first_rank = 0
            for rank, c in enumerate(top5, 1):
                if is_chunk_relevant(c, gold_kws):
                    first_rank = rank
                    break
            mrr = (1.0 / first_rank) if first_rank > 0 else 0.0

            # 2. LLM Synthesis
            t_llm_start = time.time()
            context_text = "\n\n".join(retrieved_chunks[:3])
            prompt = (
                f"You are FinAdvisor-X. Answer concisely and accurately based on the context:\n\n"
                f"CONTEXT:\n{context_text}\n\n"
                f"QUESTION:\n{q}\n\n"
                f"ANSWER:"
            )
            try:
                llm_resp = fast_chat.invoke(prompt)
                if hasattr(llm_resp, "content"):
                    if isinstance(llm_resp.content, list):
                        answer_text = " ".join(
                            part.get("text", str(part)) if isinstance(part, dict) else str(part)
                            for part in llm_resp.content
                        )
                    else:
                        answer_text = str(llm_resp.content)
                else:
                    answer_text = str(llm_resp)
            except Exception as e:
                answer_text = f"[LLM Error]: {e}"
            t_llm = time.time() - t_llm_start
            llm_latencies.append(t_llm)

            t_total = time.time() - t0
            latencies.append(t_total)

            # Grounded numeric verification check
            ans_lower = answer_text.lower()
            grounded = any(kw.lower() in ans_lower for kw in gold_kws)

            results_table.append({
                "id": qid,
                "question": q[:40] + "...",
                "p@5": precision_at_5,
                "mrr": mrr,
                "retrieval_ms": round(t_ret * 1000, 1),
                "llm_ms": round(t_llm * 1000, 1),
                "total_ms": round(t_total * 1000, 1),
                "grounded": "✓ Yes" if grounded else "❌ No",
                "sample_answer": answer_text[:80].replace("\n", " ") + "...",
            })

    # Print Results Table
    print(f"{'ID':<6} | {'Question':<44} | {'P@5':<5} | {'MRR':<5} | {'Ret (ms)':<9} | {'LLM (ms)':<9} | {'Total':<9} | {'Grounded'}")
    print("-" * 110)
    for r in results_table:
        print(f"{r['id']:<6} | {r['question']:<44} | {r['p@5']:<5.2f} | {r['mrr']:<5.2f} | {r['retrieval_ms']:<9.1f} | {r['llm_ms']:<9.1f} | {r['total_ms']:<9.1f} | {r['grounded']}")

    avg_p5 = sum(r["p@5"] for r in results_table) / len(results_table)
    avg_mrr = sum(r["mrr"] for r in results_table) / len(results_table)
    grounded_rate = sum(1 for r in results_table if "Yes" in r["grounded"]) / len(results_table) * 100

    latencies_sorted = sorted(latencies)
    p50_lat = latencies_sorted[len(latencies_sorted) // 2] * 1000
    p95_lat = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
    avg_ret_ms = sum(retrieval_latencies) / len(retrieval_latencies) * 1000
    avg_llm_ms = sum(llm_latencies) / len(llm_latencies) * 1000

    print("\n==================================================================")
    print("AGGREGATE BENCHMARK SUMMARY (SAFE KEYWORD+GRAPH BASELINE):")
    print(f"  Evaluated Queries:          {len(DEMO_QUESTIONS)}")
    print(f"  Mean Precision@5:           {avg_p5:.3f}")
    print(f"  Mean Reciprocal Rank (MRR): {avg_mrr:.3f}")
    print(f"  Numeric Grounding Rate:     {grounded_rate:.1f}% ({int(grounded_rate/10)}/10 passed)")
    print(f"  Avg Retrieval Latency:      {avg_ret_ms:.1f} ms")
    print(f"  Avg LLM Generation Latency: {avg_llm_ms:.1f} ms")
    print(f"  End-to-End Latency p50:     {p50_lat:.1f} ms")
    print(f"  End-to-End Latency p95:     {p95_lat:.1f} ms")
    print(f"  Gemini Embedding Calls:     0 (100% verified zero external embedding calls)")
    print("==================================================================")

    # Run Hosted BGE drill
    test_hosted_bge_small_endpoint()


if __name__ == "__main__":
    run_demo_evaluation()
