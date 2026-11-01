"""
Test to ensure README results table matches reports/latest/eval_metrics_latest.json
and is properly formatted between marker comments. Parses every cell and verifies provenance.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_readme_table_matches_json():
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    readme_path = os.path.join(ROOT, "README.md")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    assert "<!-- BENCHMARK_TABLE_START -->" in readme
    assert "<!-- BENCHMARK_TABLE_END -->" in readme

    table_chunk = readme.split("<!-- BENCHMARK_TABLE_START -->")[1].split("<!-- BENCHMARK_TABLE_END -->")[0].strip()
    lines = [line.strip() for line in table_chunk.splitlines() if line.strip().startswith("|")]

    assert len(lines) >= 3, "Table must have header, separator, and data rows"

    # Header and separator
    headers = [c.strip() for c in lines[0].split("|")[1:-1]]
    assert headers == ["Pipeline Stage / Subsystem", "Run", "n", "Precision@5", "Recall@5", "MRR", "Avg Latency"]

    rows = []
    for line in lines[2:]:
        cells = [c.strip().strip("`*") for c in line.split("|")[1:-1]]
        rows.append(cells)

    # 1. Retrieval Vector-Only
    r_cfg = metrics["retrieval"]["configurations"]
    vec = r_cfg["vector_only"]
    vec_row = [r for r in rows if "Vector-Only" in r[0]][0]
    assert vec_row[1] == metrics["retrieval"]["split"]
    assert int(vec_row[2]) == metrics["retrieval"]["n"]
    assert float(vec_row[3]) == vec["avg_precision_at_k"]
    assert float(vec_row[4]) == vec["avg_recall_at_k"]
    assert float(vec_row[5]) == vec["avg_mrr"]
    assert vec_row[6] == f"{vec['avg_latency_sec']*1000:.1f} ms"

    # 2. Hybrid RRF FlashRank
    flash = r_cfg["hybrid_rrf_flashrank"]
    flash_row = [r for r in rows if "FlashRank Cross-Encoder" in r[0]][0]
    assert flash_row[1] == metrics["retrieval"]["split"]
    assert int(flash_row[2]) == metrics["retrieval"]["n"]
    assert float(flash_row[3]) == flash["avg_precision_at_k"]
    assert float(flash_row[4]) == flash["avg_recall_at_k"]
    assert float(flash_row[5]) == flash["avg_mrr"]
    assert flash_row[6] == f"{flash['avg_latency_sec']*1000:.1f} ms"

    # 3. Router rows
    router = metrics["router"]
    full_router_row = [r for r in rows if "Full Test Split" in r[0]][0]
    assert full_router_row[1] == "contaminated"
    assert int(full_router_row[2]) == router["n"]
    assert full_router_row[3] == f"Accuracy: {router['split_test_accuracy_pct']:.1f}%"
    assert full_router_row[6] == f"{router['avg_router_latency_ms']:.2f} ms"

    no_traps_row = [r for r in rows if "No Traps" in r[0]][0]
    assert no_traps_row[1] == "contaminated"
    assert int(no_traps_row[2]) == 30
    assert no_traps_row[3] == f"Accuracy: {router['split_test_no_traps_accuracy_pct']:.1f}%"
    assert no_traps_row[6] == f"{router['avg_router_latency_ms']:.2f} ms"

    # 4. Router Holdout V2
    h2 = router["clean_holdout_v2"]
    h2_row = [r for r in rows if "Clean Holdout V2" in r[0]][0]
    assert h2_row[1] == "holdout_v2"
    assert int(h2_row[2]) == h2["n"]
    assert h2_row[3] == f"Accuracy: {h2['overall_accuracy']*100:.1f}%"
    assert h2_row[6] == "N/A"
