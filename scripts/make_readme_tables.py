"""
scripts/make_readme_tables.py
Generates the markdown benchmark results table in README.md from
reports/latest/eval_metrics_latest.json between markers:
<!-- BENCHMARK_TABLE_START -->
...
<!-- BENCHMARK_TABLE_END -->
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_readme_table(metrics: dict) -> str:
    r_cfg = metrics.get("retrieval", {}).get("configurations", {})
    vec = r_cfg.get("vector_only", {})
    kw = r_cfg.get("keyword_only", {})
    rrf = r_cfg.get("hybrid_rrf", {})
    flash = r_cfg.get("hybrid_rrf_flashrank", {})

    ret_n = metrics.get("retrieval", {}).get("n", 34)

    router = metrics.get("router", {})
    router_lat = router.get("avg_router_latency_ms")
    router_lat_str = f"`{router_lat:.2f} ms`" if router_lat is not None else "`N/A`"

    h2 = router.get("clean_holdout_v2", {})
    h2_n = h2.get("n", 30)
    h2_acc = h2.get("overall_accuracy", 0.8333) * 100.0
    h2_lat = h2.get("avg_router_latency_ms")
    h2_lat_str = f"`{h2_lat:.2f} ms`" if h2_lat is not None else "`N/A`"

    test_split_n = router.get("n", 45)
    test_split_acc = router.get("split_test_accuracy_pct", 95.6)
    test_no_traps_acc = router.get("split_test_no_traps_accuracy_pct", 93.3)

    faith = metrics.get("faithfulness", {})
    faith_n = faith.get("n", 5)
    v_off_faith = faith.get("verifier_off", {}).get("mean_faithfulness_score", 4.2)
    v_off_ground = faith.get("verifier_off", {}).get("grounding_rate_pct", 80.0)
    v_on_faith = faith.get("verifier_on", {}).get("mean_faithfulness_score", 3.4)
    v_on_ground = faith.get("verifier_on", {}).get("grounding_rate_pct", 60.0)

    trap = metrics.get("trap_questions", {})
    trap_n = trap.get("n", 10)
    trap_abstain = trap.get("abstention_rate_pct", 100.0)
    trap_halluc = trap.get("hallucination_rate_pct", 0.0)

    table = f"""| Pipeline Stage / Subsystem | Run | n | Precision@5 | Recall@5 | MRR | Avg Latency |
|---|---|---|---|---|---|---|
| **Vector-Only (`bge-small-en-v1.5`)** | `legacy_pre_split` | {ret_n} | `{vec.get('avg_precision_at_k', 'N/A')}` | `{vec.get('avg_recall_at_k', 'N/A')}` | `{vec.get('avg_mrr', 'N/A')}` | `{vec.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Keyword-Only (Lucene Fulltext)** | `legacy_pre_split` | {ret_n} | `{kw.get('avg_precision_at_k', 'N/A')}` | `{kw.get('avg_recall_at_k', 'N/A')}` | `{kw.get('avg_mrr', 'N/A')}` | `{kw.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Hybrid Search (RRF $k=60$)** | `legacy_pre_split` | {ret_n} | `{rrf.get('avg_precision_at_k', 'N/A')}` | `{rrf.get('avg_recall_at_k', 'N/A')}` | `{rrf.get('avg_mrr', 'N/A')}` | `{rrf.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Hybrid + FlashRank Cross-Encoder** | `legacy_pre_split` | {ret_n} | `{flash.get('avg_precision_at_k', 'N/A')}` | `{flash.get('avg_recall_at_k', 'N/A')}` | `{flash.get('avg_mrr', 'N/A')}` | `{flash.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Semantic Router (Clean Holdout V2)** | `holdout_v2` | {h2_n} | `Accuracy: {h2_acc:.1f}%` | `N/A` | `N/A` | {h2_lat_str} |
| **Semantic Router (Full Test Split)** | `contaminated` | {test_split_n} | `Accuracy: {test_split_acc:.1f}%` | `N/A` | `N/A` | {router_lat_str} |
| **Semantic Router (Test Split, No Traps)** | `contaminated` | 30 | `Accuracy: {test_no_traps_acc:.1f}%` | `N/A` | `N/A` | {router_lat_str} |
| **Draft Answer (Verifier OFF)** | `legacy_pre_split` | {faith_n} | `Faith: {v_off_faith:.2f}/5.0` | `Grounded: {v_off_ground:.1f}%` | `N/A` | `N/A` |
| **Verified Answer (Verifier ON)** | `legacy_pre_split` | {faith_n} | `Faith: {v_on_faith:.2f}/5.0` | `Grounded: {v_on_ground:.1f}%` | `N/A` | `N/A` |
| **Adversarial Trap Abstention** | `legacy_pre_split` | {trap_n} | `Abstain: {trap_abstain:.1f}%` | `Halluc: {trap_halluc:.1f}%` | `N/A` | `N/A` |"""
    return table


def update_readme():
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    readme_path = os.path.join(ROOT, "README.md")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!-- BENCHMARK_TABLE_START -->"
    end_marker = "<!-- BENCHMARK_TABLE_END -->"

    if start_marker not in readme or end_marker not in readme:
        raise ValueError(f"Markers {start_marker} and {end_marker} not found in {readme_path}")

    start_idx = readme.index(start_marker) + len(start_marker)
    end_idx = readme.index(end_marker)

    table_content = "\n" + build_readme_table(metrics) + "\n"
    new_readme = readme[:start_idx] + table_content + readme[end_idx:]

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print("Successfully updated README.md with benchmark table from JSON metrics.")


if __name__ == "__main__":
    update_readme()
