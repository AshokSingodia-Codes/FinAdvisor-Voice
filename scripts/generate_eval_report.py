"""
Master Evaluation Suite & Report Generator for FinAdvisor-X
Orchestrates:
  1. Retrieval Benchmark (Vector vs Keyword vs Hybrid RRF vs FlashRank Reranker)
  2. Semantic Router Accuracy Benchmark
  3. Answer Faithfulness & Self-RAG Verifier Ablation
  4. Trap / Out-of-Corpus Hallucination Benchmark

Generates `reports/eval_report_latest.md` and `reports/eval_metrics_latest.json`.
"""
import os
import sys
import json
import time
import argparse
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from tests.eval.eval_retrieval import run_retrieval_evaluation
from tests.eval.eval_router import run_router_evaluation
from tests.eval.eval_trap_questions import run_trap_evaluation
from tests.eval.eval_faithfulness import run_faithfulness_evaluation

def generate_markdown_report(
    retrieval_data: Dict[str, Any],
    router_data: Dict[str, Any],
    faithfulness_data: Dict[str, Any],
    trap_data: Dict[str, Any]
) -> str:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    
    # Extract retrieval metrics
    r_cfg = retrieval_data.get("configurations", {})
    vec = r_cfg.get("vector_only", {})
    kw = r_cfg.get("keyword_only", {})
    rrf = r_cfg.get("hybrid_rrf", {})
    flash = r_cfg.get("hybrid_rrf_flashrank", {})
    lift = retrieval_data.get("empirical_lift", {})
    
    # Extract router metrics
    router_acc = router_data.get("overall_accuracy", 0.0) * 100
    router_lat = router_data.get("avg_router_latency_ms", 0.0)
    per_class = router_data.get("per_class_metrics", {})
    
    # Extract faithfulness metrics
    v_off = faithfulness_data.get("verifier_off", {})
    v_on = faithfulness_data.get("verifier_on", {})
    v_lift = faithfulness_data.get("verifier_lift", {})
    
    # Extract trap metrics
    trap_abstain = trap_data.get("abstention_rate_pct", 0.0)
    trap_halluc = trap_data.get("hallucination_rate_pct", 0.0)
    
    md = f"""# FinAdvisor-X Empirical Evaluation & Benchmark Report

**Generated:** `{timestamp}`  
**Architecture:** Hybrid Graph-RAG (Neo4j Aura + FastEmbed) + FlashRank Cross-Encoder + LangGraph Agentic Routing + Self-RAG Fact-Checking Verifier

---

## Executive Summary & Key Highlights

This report quantifies the empirical performance of each core subsystem in the FinAdvisor-X architecture using a standardized 50-query financial benchmark spanning 10-K filings, corporate finance textbooks, market computations, and adversarial out-of-corpus queries.

| Component / Subsystem | Benchmark Metric | Result | Impact / Value |
|---|---|---|---|
| **Hybrid Search (RRF)** | Recall@5 Lift vs Vector-Only | **+{lift.get('recall_lift_vs_vector_pct', 0.0)}%** | Bridges lexical entity gaps and graph connectivity |
| **FlashRank Cross-Encoder** | Precision@5 Lift vs Hybrid RRF | **+{lift.get('precision_lift_from_flashrank_pct', 0.0)}%** | Elevates exact numerical chunks to top-1 rank |
| **Self-RAG Verifier** | Grounding Rate Improvement | **+{v_lift.get('grounding_rate_lift_pct_pts', 0.0)}% pts** | Catches ungrounded numerical claims before user output |
| **Semantic Intent Router** | Multi-Class Routing Accuracy | **{router_acc:.1f}%** | 0-overhead dynamic query routing in <{router_lat:.0f}ms |
| **Hallucination Resistance** | Trap / Out-of-Corpus Abstention | **{trap_abstain:.1f}%** | Safe refusal on non-existent corporate entities |

---

## 1. Retrieval & Reranker Benchmark (k=5)

Evaluated on in-corpus SEC 10-K filings and corporate finance textbook queries.

| Pipeline Stage | Precision@5 | Recall@5 | Mean Reciprocal Rank (MRR) | Avg Latency |
|---|---|---|---|---|
| **1. Vector-Only (Dense FastEmbed)** | `{vec.get('avg_precision_at_k', 0.0):.3f}` | `{vec.get('avg_recall_at_k', 0.0):.3f}` | `{vec.get('avg_mrr', 0.0):.3f}` | `{vec.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **2. Keyword / Graph-Only** | `{kw.get('avg_precision_at_k', 0.0):.3f}` | `{kw.get('avg_recall_at_k', 0.0):.3f}` | `{kw.get('avg_mrr', 0.0):.3f}` | `{kw.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **3. Hybrid Search (RRF Fusion)** | `{rrf.get('avg_precision_at_k', 0.0):.3f}` | `{rrf.get('avg_recall_at_k', 0.0):.3f}` | `{rrf.get('avg_mrr', 0.0):.3f}` | `{rrf.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **4. Hybrid + FlashRank Cross-Encoder** | **`{flash.get('avg_precision_at_k', 0.0):.3f}`** | **`{flash.get('avg_recall_at_k', 0.0):.3f}`** | **`{flash.get('avg_mrr', 0.0):.3f}`** | `{flash.get('avg_latency_sec', 0.0)*1000:.1f} ms` |

### Key Retrieval Takeaways
- **Hybrid RRF Fusion** solves the vocabulary mismatch problem for complex financial line items, lifting Recall@5 by **{lift.get('recall_lift_vs_vector_pct', 0.0)}%**.
- **FlashRank Reranking** re-orders fused candidates with cross-attention scoring, lifting Precision@5 by **{lift.get('precision_lift_from_flashrank_pct', 0.0)}%** while adding minimal latency overhead.

---

## 2. Semantic Intent Router Performance

Evaluated across all 5 routing intents: `hybrid_search`, `decompose`, `calculation`, `live_market_data`, and `direct_answer`.

- **Overall Routing Accuracy:** `{router_acc:.1f}%`
- **Mean Router Latency:** `{router_lat:.1f} ms`

| Intent Class | Support | Precision | Recall | F1-Score |
|---|---|---|---|---|
"""
    for c, m in per_class.items():
        md += f"| `{c}` | {m.get('support', 0)} | `{m.get('precision', 0.0):.3f}` | `{m.get('recall', 0.0):.3f}` | `{m.get('f1_score', 0.0):.3f}` |\n"

    md += f"""
---

## 3. Answer Faithfulness & Self-RAG Verifier Ablation

Evaluated via LLM-as-a-Judge (Qwen-2.5-32B/70B strict financial auditor prompt) measuring factual grounding and hallucination prevention against retrieved evidence chunks.

| Configuration | Mean Faithfulness (1 - 5 Scale) | Factually Grounded Rate (%) |
|---|---|---|
| **Draft Answer (Verifier OFF)** | `{v_off.get('mean_faithfulness_score', 0.0):.2f} / 5.0` | `{v_off.get('grounding_rate_pct', 0.0):.1f}%` |
| **Verified Answer (Self-RAG Verifier ON)** | **`{v_on.get('mean_faithfulness_score', 0.0):.2f} / 5.0`** | **`{v_on.get('grounding_rate_pct', 0.0):.1f}%`** |

- **Grounding Rate Improvement:** `+{v_lift.get('grounding_rate_lift_pct_pts', 0.0)}% pts`

---

## 4. Hallucination Resistance & Adversarial Trap Benchmark

Evaluated on 10 out-of-corpus adversarial queries (fictional corporations, non-existent executive positions, unindexed quarters).

- **Safe Abstention Rate:** `{trap_abstain:.1f}%`
- **Hallucination Incident Rate:** `{trap_halluc:.1f}%`

---

## 5. Resume & Interview Summary Points

```markdown
- Built an enterprise-grade Hybrid Graph-RAG financial intelligence agent combining Neo4j graph traversal with FastEmbed dense vectors via Reciprocal Rank Fusion (RRF).
- Implemented a FlashRank cross-encoder reranker delivering a +{lift.get('precision_lift_from_flashrank_pct', 0.0)}% Precision@5 lift and +{lift.get('recall_lift_vs_vector_pct', 0.0)}% Recall lift over standalone dense retrieval.
- Engineered a LangGraph multi-agent orchestration layer with a {router_acc:.1f}% accurate semantic intent router (<{router_lat:.0f}ms latency).
- Implemented an automated Self-RAG verification harness lifting factually grounded answers to {v_on.get('grounding_rate_pct', 0.0):.1f}% and achieving {trap_abstain:.1f}% safe abstention on out-of-corpus adversarial queries.
```
"""
    return md

def main():
    parser = argparse.ArgumentParser(description="FinAdvisor-X Evaluation Report Generator")
    parser.add_argument("--skip-slow", action="store_true", help="Use small sample sizes for fast evaluation")
    args = parser.parse_args()
    
    sample_faith = 10 if args.skip_slow else 15
    
    print("\n" + "="*60)
    print("🚀 STARTING FINADVISOR-X QUANTITATIVE EVALUATION HARNESS")
    print("="*60 + "\n")
    
    t_start = time.time()
    
    # 1. Retrieval Benchmark
    retrieval_results = run_retrieval_evaluation()
    
    # 2. Router Benchmark
    router_results = run_router_evaluation()
    
    # 3. Trap Questions Benchmark
    trap_results = run_trap_evaluation()
    
    # 4. Faithfulness Benchmark
    faithfulness_results = run_faithfulness_evaluation(sample_size=sample_faith)
    
    total_elapsed = time.time() - t_start
    
    # Generate Consolidated Markdown and JSON
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    md_content = generate_markdown_report(
        retrieval_data=retrieval_results,
        router_data=router_results,
        faithfulness_data=faithfulness_results,
        trap_data=trap_results
    )
    
    md_path = os.path.join(reports_dir, "eval_report_latest.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    consolidated_json_path = os.path.join(reports_dir, "eval_metrics_latest.json")
    with open(consolidated_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_eval_duration_sec": round(total_elapsed, 2),
            "retrieval": retrieval_results,
            "router": router_results,
            "faithfulness": faithfulness_results,
            "trap_questions": trap_results
        }, f, indent=2)
        
    print("\n" + "="*60)
    print(f"🎉 EVALUATION COMPLETE (Total Duration: {total_elapsed:.1f}s)")
    print(f"📄 Markdown Report saved: {md_path}")
    print(f"📊 JSON Metrics saved:    {consolidated_json_path}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
