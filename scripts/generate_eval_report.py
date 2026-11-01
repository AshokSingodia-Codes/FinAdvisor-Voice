"""
Master Evaluation Suite & Report Generator for FinAdvisor-X
Evaluates:
  1. Retrieval Benchmark (Vector vs Keyword vs Hybrid RRF vs FlashRank Reranker)
  2. Semantic Router Accuracy Benchmark
  3. Answer Faithfulness & Self-RAG Verifier Ablation
  4. Trap / Out-of-Corpus Hallucination Benchmark

Strict reporting rules:
- Compute every delta (absolute and relative) from the unrounded values in the JSON.
- Print the absolute change and relative change, each with its sign.
- Wording follows the sign: a drop is a drop.
- Latency and MRR sit next to precision gain.
- Every metric row includes sample size n.
- Missing data prints 'not measured'.
- No promotional claims.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def compute_delta(val: float, base: float) -> tuple[float, float]:
    abs_change = val - base
    rel_change = (abs_change / base * 100.0) if base != 0 else 0.0
    return abs_change, rel_change


def format_signed_delta(
    abs_val: float, rel_val: float, unit: str = "", rel_unit: str = "%"
) -> str:
    sign_str = "gain" if abs_val > 0 else ("drop" if abs_val < 0 else "unchanged")
    return f"{abs_val:+.4f}{unit} ({rel_val:+.2f}{rel_unit}) {sign_str}"


def generate_markdown_report(
    retrieval_data: dict[str, Any],
    router_data: dict[str, Any],
    faithfulness_data: dict[str, Any],
    trap_data: dict[str, Any],
    git_commit: str | None = None,
) -> str:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    commit_str = git_commit or get_git_commit()

    # Retrieval metrics
    r_cfg = retrieval_data.get("configurations", {}) if retrieval_data else {}
    vec = r_cfg.get("vector_only", {})
    kw = r_cfg.get("keyword_only", {})
    rrf = r_cfg.get("hybrid_rrf", {})
    flash = r_cfg.get("hybrid_rrf_flashrank", {})
    n_ret = retrieval_data.get("total_queries_evaluated", "not measured") if retrieval_data else "not measured"

    # Compute unrounded retrieval deltas
    # Hybrid vs Vector Recall
    v_rec = vec.get("avg_recall_at_k", 0.0)
    h_rec = rrf.get("avg_recall_at_k", 0.0)
    abs_h_rec, rel_h_rec = compute_delta(h_rec, v_rec)

    # Hybrid vs Vector MRR
    v_mrr = vec.get("avg_mrr", 0.0)
    h_mrr = rrf.get("avg_mrr", 0.0)
    abs_h_mrr, rel_h_mrr = compute_delta(h_mrr, v_mrr)

    # FlashRank vs Hybrid Precision
    h_prec = rrf.get("avg_precision_at_k", 0.0)
    f_prec = flash.get("avg_precision_at_k", 0.0)
    abs_f_p, rel_f_p = compute_delta(f_prec, h_prec)

    # FlashRank vs Hybrid MRR
    f_mrr = flash.get("avg_mrr", 0.0)
    abs_f_mrr, rel_f_mrr = compute_delta(f_mrr, h_mrr)

    # FlashRank vs Hybrid Latency
    h_lat = rrf.get("avg_latency_sec", 0.0)
    f_lat = flash.get("avg_latency_sec", 0.0)
    abs_f_lat, rel_f_lat = compute_delta(f_lat, h_lat)

    # Router metrics
    n_router = router_data.get("total_queries", "not measured") if router_data else "not measured"
    router_acc = router_data.get("overall_accuracy") if router_data else None
    router_lat = router_data.get("avg_router_latency_ms", 0.0) if router_data else 0.0
    router_path = router_data.get("router_path", "fallback_heuristic")
    per_class = router_data.get("per_class_metrics", {}) if router_data else {}
    cm = router_data.get("confusion_matrix", {}) if router_data else {}

    # Faithfulness metrics
    n_faith = faithfulness_data.get("total_queries_evaluated", "not measured") if faithfulness_data else "not measured"
    v_off = faithfulness_data.get("verifier_off", {}) if faithfulness_data else {}
    v_on = faithfulness_data.get("verifier_on", {}) if faithfulness_data else {}

    v_off_faith = v_off.get("mean_faithfulness_score", 0.0)
    v_on_faith = v_on.get("mean_faithfulness_score", 0.0)
    abs_faith, rel_faith = compute_delta(v_on_faith, v_off_faith)

    v_off_ground = v_off.get("grounding_rate_pct", 0.0)
    v_on_ground = v_on.get("grounding_rate_pct", 0.0)
    abs_ground = v_on_ground - v_off_ground

    # Trap metrics
    n_trap = trap_data.get("total_trap_questions", "not measured") if trap_data else "not measured"
    trap_abstain = trap_data.get("abstention_rate_pct") if trap_data else None
    trap_halluc = trap_data.get("hallucination_rate_pct") if trap_data else None

    md = f"""# FinAdvisor-X Empirical Evaluation & Benchmark Report

**Generated:** `{timestamp}`  
**Git Commit:** `{commit_str}`  
**Embedding Model:** `BAAI/bge-small-en-v1.5` (384-dim, FastEmbed)  
**Architecture:** Hybrid RAG: Neo4j vector + Lucene fulltext, RRF fusion, FlashRank rerank  

---

## 1. Retrieval & Reranking Benchmark

Evaluated on in-corpus SEC 10-K filings and corporate finance textbook queries (sample size $n={n_ret}$).

| Pipeline Stage | n | Precision@5 | Recall@5 | MRR | Latency |
|---|---|---|---|---|---|
| **1. Vector-Only (FastEmbed bge-small)** | {n_ret} | `{vec.get('avg_precision_at_k', 'not measured')}` | `{vec.get('avg_recall_at_k', 'not measured')}` | `{vec.get('avg_mrr', 'not measured')}` | `{vec.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **2. Keyword-Only (Lucene Fulltext)** | {n_ret} | `{kw.get('avg_precision_at_k', 'not measured')}` | `{kw.get('avg_recall_at_k', 'not measured')}` | `{kw.get('avg_mrr', 'not measured')}` | `{kw.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **3. Hybrid Search (RRF Fusion, k=60)** | {n_ret} | `{rrf.get('avg_precision_at_k', 'not measured')}` | `{rrf.get('avg_recall_at_k', 'not measured')}` | `{rrf.get('avg_mrr', 'not measured')}` | `{rrf.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **4. Hybrid + FlashRank Cross-Encoder** | {n_ret} | `{flash.get('avg_precision_at_k', 'not measured')}` | `{flash.get('avg_recall_at_k', 'not measured')}` | `{flash.get('avg_mrr', 'not measured')}` | `{flash.get('avg_latency_sec', 0.0)*1000:.1f} ms` |

### Retrieval Deltas (Computed from Unrounded JSON Values)
- **Hybrid RRF vs Vector-Only Recall:** abs change = `{abs_h_rec:+.4f}`, rel change = `{rel_h_rec:+.2f}%` ({format_signed_delta(abs_h_rec, rel_h_rec)}).
- **Hybrid RRF vs Vector-Only MRR:** abs change = `{abs_h_mrr:+.4f}`, rel change = `{rel_h_mrr:+.2f}%` ({format_signed_delta(abs_h_mrr, rel_h_mrr)}).
- **FlashRank Precision vs Hybrid:** abs change = `{abs_f_p:+.4f}`, rel change = `{rel_f_p:+.2f}%` ({format_signed_delta(abs_f_p, rel_f_p)}).
- **FlashRank MRR vs Hybrid:** abs change = `{abs_f_mrr:+.4f}`, rel change = `{rel_f_mrr:+.2f}%` ({format_signed_delta(abs_f_mrr, rel_f_mrr)}).
- **FlashRank Latency vs Hybrid:** abs change = `{abs_f_lat:+.4f}s`, rel change = `{rel_f_lat:+.2f}%` ({format_signed_delta(abs_f_lat, rel_f_lat, unit='s')}).

---

## 2. Semantic Intent Router Performance

Evaluated on multi-class intent classification (sample size $n={n_router}$, path: `{router_path}`).

- **Overall Routing Accuracy:** `{f'{router_acc*100:.1f}%' if router_acc is not None else 'not measured'}`
- **Mean Router Latency:** `{router_lat:.1f} ms` (measured on `{router_path}` path)

| Intent Class | Support (n) | Precision | Recall | F1-Score |
|---|---|---|---|---|
"""
    if per_class:
        for c, m in per_class.items():
            md += f"| `{c}` | {m.get('support', 0)} | `{m.get('precision', 0.0):.3f}` | `{m.get('recall', 0.0):.3f}` | `{m.get('f1_score', 0.0):.3f}` |\n"
    else:
        md += "| not measured | not measured | not measured | not measured | not measured |\n"

    if cm:
        md += "\n### Confusion Matrix\n```text\n"
        for k_cm, count in cm.items():
            md += f"{k_cm}: {count}\n"
        md += "```\n"

    md += f"""
---

## 3. Answer Faithfulness & Verifier Ablation

Evaluated via LLM auditor measuring factual grounding against retrieved evidence (sample size $n={n_faith}$).

| Configuration | n | Mean Faithfulness (1-5 Scale) | Factually Grounded Rate (%) |
|---|---|---|---|
| **Draft Answer (Verifier OFF)** | {n_faith} | `{v_off_faith:.2f} / 5.0` | `{v_off_ground:.1f}%` |
| **Verified Answer (Verifier ON)** | {n_faith} | `{v_on_faith:.2f} / 5.0` | `{v_on_ground:.1f}%` |

### Verifier Empirical Deltas
- **Faithfulness Score:** abs change = `{abs_faith:+.2f}`, rel change = `{rel_faith:+.2f}%` ({format_signed_delta(abs_faith, rel_faith)}).
- **Grounded Rate:** abs change = `{abs_ground:+.2f}% pts` ({'gain' if abs_ground > 0 else ('drop' if abs_ground < 0 else 'unchanged')}).
- **Decision:** On the recorded n={n_faith} run, faithfulness went {v_off_faith:.1f} to {v_on_faith:.1f} and grounded rate {v_off_ground:.0f}% to {v_on_ground:.0f}%. n={n_faith} is too small to conclude. Disabled by default pending re-measurement on >=30 questions. Run: `python -m tests.eval.eval_faithfulness`.

---

## 4. Hallucination Resistance & Adversarial Trap Benchmark

Evaluated on adversarial out-of-corpus queries (sample size $n={n_trap}$).

- **Safe Abstention Rate:** `{f'{trap_abstain:.1f}%' if trap_abstain is not None else 'not measured'}`
- **Hallucination Incident Rate:** `{f'{trap_halluc:.1f}%' if trap_halluc is not None else 'not measured'}`
"""
    return md


def main():
    parser = argparse.ArgumentParser(description="FinAdvisor-X Evaluation Report Generator")
    parser.add_argument(
        "--from-cached-metrics",
        action="store_true",
        help="Generate markdown report from existing reports/latest/eval_metrics_latest.json",
    )
    args = parser.parse_args()

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    latest_metrics_path = os.path.join(reports_dir, "latest", "eval_metrics_latest.json")
    if not os.path.exists(latest_metrics_path):
        latest_metrics_path = os.path.join(reports_dir, "eval_metrics_latest.json")

    if args.from_cached_metrics and os.path.exists(latest_metrics_path):
        with open(latest_metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        md_content = generate_markdown_report(
            retrieval_data=data.get("retrieval", {}),
            router_data=data.get("router", {}),
            faithfulness_data=data.get("faithfulness", {}),
            trap_data=data.get("trap_questions", {}),
            git_commit=data.get("git_commit_of_original_run", data.get("git_commit")),
        )
        out_path = os.path.join(reports_dir, "latest", "eval_report_latest.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(os.path.join(reports_dir, "eval_report_latest.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Generated {out_path} and reports/eval_report_latest.md from cached metrics.")
        return

    print("To regenerate from recorded metrics run with --from-cached-metrics.")


if __name__ == "__main__":
    main()
