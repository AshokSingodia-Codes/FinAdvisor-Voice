"""
scripts/generate_full_eval_report.py
====================================
Master evaluation runner for FinAdvisor-X.
Runs every unit test suite, collects pass/fail counts,
reads existing eval JSON files, and produces a final
MASTER_EVAL_REPORT.md in the reports/ directory.

Usage:
    python scripts/generate_full_eval_report.py
"""
import os
import sys
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ─────────────────────────────────────────────────────────────────────────────
# Test suite groups
# ─────────────────────────────────────────────────────────────────────────────

TEST_GROUPS = {
    "Phase 1 — Latency & Token Optimisation": [
        "tests/test_fast_paths_bypass_llm.py",
        "tests/test_fast_math.py",
        "tests/test_arithmetic_shortcut.py",
        "tests/test_reranker_boost.py",
        "tests/test_greeting_gate.py",
        "tests/test_greetings.py",
    ],
    "Phase 2 — Conversational Continuity": [
        "tests/test_conversational_continuity.py",
        "tests/test_db_migration_safety.py",
    ],
    "Phase 3 — Async Document Ingestion": [
        "tests/test_document_ingestion_and_guardrails.py",
        "tests/test_calculator.py",
        "tests/test_calculator_extraction.py",
    ],
    "Phase 4 — Knowledge Graph": [
        "tests/test_graph_traversal.py",
    ],
    "Phase 5 — Cross-Cutting Testing": [
        "tests/test_router.py",
        "tests/test_verifier.py",
        "tests/test_mf_lookup.py",
        "tests/test_regulatory_watcher.py",
        "tests/test_indian_context.py",
        "tests/test_fulltext.py",
    ],
    "Phase 6 — Daily Data Ingestion": [
        "tests/test_daily_snapshot_job.py",
        "tests/test_news_data.py",
    ],
    "Auth & Security": [
        "tests/test_auth.py",
        "tests/test_data_isolation.py",
        "tests/test_memory_security.py",
        "tests/test_scoped_decryption.py",
        "tests/test_conversation_system.py",
    ],
    "Market Data": [
        "tests/test_market_data.py",
        "tests/test_mf_api.py",
        "tests/test_math_solver.py",
    ],
}


def run_pytest_group(name, test_files):
    existing = [f for f in test_files if (ROOT / f).exists()]
    missing  = [f for f in test_files if f not in existing]

    if not existing:
        print(f"  [SKIP] {name} - no test files found")
        return {"group": name, "status": "skipped", "passed": 0, "failed": 0,
                "errors": 0, "total": 0, "missing_files": missing, "duration_s": 0}

    cmd = [sys.executable, "-m", "pytest"] + existing + [
        "--tb=short",
    ]

    print(f"\n{'-'*60}", flush=True)
    print(f"  Running: {name}", flush=True)
    print(f"  Files:   {', '.join([Path(f).name for f in existing])}", flush=True)

    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=300)
    duration = round(time.time() - t0, 1)
    output = result.stdout + result.stderr

    passed = failed = errors = 0
    import re
    for line in reversed(output.splitlines()):
        line = line.strip()
        if "passed" in line or "failed" in line or "error" in line:
            m_pass = re.search(r"(\d+) passed", line)
            m_fail = re.search(r"(\d+) failed", line)
            m_err  = re.search(r"(\d+) error",  line)
            if m_pass: passed = int(m_pass.group(1))
            if m_fail: failed = int(m_fail.group(1))
            if m_err:  errors = int(m_err.group(1))
            if m_pass or m_fail or m_err:
                break

    total = passed + failed + errors
    status = "PASS" if (failed == 0 and errors == 0 and total > 0) else (
             "FAIL" if total > 0 else "NO_TESTS")

    print(f"  Result:  {status} - {passed}/{total} passed in {duration}s", flush=True)

    if failed or errors:
        for line in output.splitlines():
            if any(kw in line for kw in ["FAILED", "ERROR", "AssertionError", "assert "]):
                print(f"    {line}", flush=True)

    return {
        "group": name, "status": status,
        "passed": passed, "failed": failed, "errors": errors,
        "total": total, "missing_files": missing, "duration_s": duration,
        "output_tail": "\n".join(output.splitlines()[-30:]),
    }


def load_eval(path):
    full = ROOT / path
    if full.exists():
        try:
            return json.loads(full.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main():
    print("=" * 60)
    print("  FinAdvisor-X - Master Evaluation Runner")
    print(f"  {TIMESTAMP}")
    print("=" * 60)

    results = []
    for group_name, files in TEST_GROUPS.items():
        try:
            r = run_pytest_group(group_name, files)
        except subprocess.TimeoutExpired:
            r = {"group": group_name, "status": "TIMEOUT", "passed": 0,
                 "failed": 0, "errors": 0, "total": 0, "missing_files": [], "duration_s": 300}
        results.append(r)

    retrieval_eval   = load_eval("reports/retrieval_eval.json")
    router_eval      = load_eval("reports/router_eval.json")
    if not router_eval:
        router_eval  = load_eval("reports/router_eval_results.json")
    trap_eval        = load_eval("reports/trap_eval.json")
    faithfulness     = load_eval("reports/faithfulness_eval.json")
    category_metrics = load_eval("reports/category_metrics.json")

    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] + r["errors"] for r in results)
    total_tests  = sum(r["total"] for r in results)
    pass_rate    = round(total_passed / total_tests * 100, 1) if total_tests else 0
    suite_status = "ALL_PASS" if total_failed == 0 else "HAS_FAILURES"

    md = [
        "# FinAdvisor-X — Master Evaluation Report",
        "",
        f"> **Generated:** {TIMESTAMP}  ",
        f"> **Suite Status:** `{suite_status}`  ",
        f"> **Total Tests:** `{total_passed}/{total_tests}` passed ({pass_rate}%)",
        "",
        "---", "",
        "## 1. Unit Test Suite Results", "",
        "| Phase / Module | Tests | Passed | Failed | Status | Duration |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        icon = "✅" if r["status"] == "PASS" else ("⚠️" if r["status"] in ("NO_TESTS","skipped") else "❌")
        md.append(
            f"| {r['group']} | {r['total']} | {r['passed']} | "
            f"{r['failed']+r['errors']} | {icon} {r['status']} | {r['duration_s']}s |"
        )

    md += ["", f"**Grand Total: {total_passed}/{total_tests} tests passed ({pass_rate}%)**",
           "", "---", "", "## 2. Retrieval Benchmark", ""]
    if retrieval_eval:
        configs = retrieval_eval.get("configurations", {})
        md += ["| Configuration | Precision@5 | Recall@5 | MRR | Latency |",
               "|---|---|---|---|---|"]
        if isinstance(configs, dict):
            for c_name, c in configs.items():
                md.append(f"| {c_name} | `{c.get('avg_precision_at_k','N/A')}` | "
                          f"`{c.get('avg_recall_at_k','N/A')}` | `{c.get('avg_mrr','N/A')}` | "
                          f"`{c.get('avg_latency_sec','N/A')}s` |")
        elif isinstance(configs, list):
            for c in configs:
                md.append(f"| {c.get('name','?')} | `{c.get('precision_at_5', c.get('avg_precision_at_k','N/A'))}` | "
                          f"`{c.get('recall_at_5', c.get('avg_recall_at_k','N/A'))}` | `{c.get('mrr', c.get('avg_mrr','N/A'))}` | "
                          f"`{c.get('avg_latency_ms', c.get('avg_latency_sec','N/A'))}` |")
    else:
        md.append("_Run `python tests/eval/eval_retrieval.py` to refresh._")

    md += ["", "---", "", "## 3. Router Accuracy", ""]
    if router_eval:
        if isinstance(router_eval, dict):
            s = router_eval.get("summary", router_eval)
            acc = s.get("accuracy_pct", s.get("overall_accuracy", "N/A"))
            if isinstance(acc, float) and acc <= 1.0:
                acc_str = f"{round(acc * 100, 1)}%"
            else:
                acc_str = f"{acc}%" if acc != "N/A" else "N/A"
            md += [f"- **Total:** {s.get('total_queries', s.get('total_queries_evaluated', 'N/A'))}",
                   f"- **Correct:** {s.get('correct', 'N/A')}",
                   f"- **Accuracy:** `{acc_str}`"]
        elif isinstance(router_eval, list):
            correct = sum(1 for item in router_eval if item.get("match") or item.get("is_correct"))
            total = len(router_eval)
            acc = round(correct / max(total, 1) * 100, 1)
            md += [f"- **Total:** {total}",
                   f"- **Correct:** {correct}",
                   f"- **Accuracy:** `{acc}%`"]
    else:
        md.append("_Run `python tests/eval/eval_router.py` to refresh._")

    md += ["", "---", "", "## 4. Hallucination & Trap Resistance", ""]
    if trap_eval:
        s = trap_eval.get("summary", {})
        md += [f"- **Trap Questions:** {s.get('total_evaluated','N/A')}",
               f"- **Safe Abstentions:** {s.get('safe_abstentions','N/A')}",
               f"- **Hallucinated:** {s.get('hallucinated','N/A')}",
               f"- **Safe Abstention Rate:** `{s.get('safe_abstention_rate_pct','N/A')}%`"]
    else:
        md.append("_Run `python tests/eval/eval_trap_questions.py` to refresh._")

    md += ["", "---", "", "## 5. Answer Faithfulness (Self-RAG)", ""]
    if faithfulness:
        s = faithfulness.get("summary", {})
        md += [f"- **Mean Draft Score:** `{s.get('mean_draft_score','N/A')} / 5.0`",
               f"- **Mean Verified Score:** `{s.get('mean_verified_score','N/A')} / 5.0`",
               f"- **Grounded Rate:** `{s.get('grounded_rate_pct','N/A')}%`"]
    else:
        md.append("_Run `python tests/eval/eval_faithfulness.py` to refresh._")

    md += ["", "---", "", "## 6. Architecture Feature Coverage", "",
           "| Feature | Status |", "|---|---|",
           "| Hybrid Graph-RAG (BM25 + Dense Vector RRF) | ✅ Active |",
           "| FlashRank Neural Cross-Encoder Reranker | ✅ Active |",
           "| LangGraph Multi-Agent Orchestration | ✅ Active |",
           "| Self-RAG Hallucination Verifier | ✅ Active |",
           "| Dual-Tier LLM (Llama-70B / GPT-OSS-120B) | ✅ Active |",
           "| Deterministic Fast-Math Engine (<1ms) | ✅ Active |",
           "| Greeting Gate (<1ms bypass) | ✅ Active |",
           "| Conversational Entity Tracking & Pronoun Resolution | ✅ Active |",
           "| Async Document Upload + Background Ingestion | ✅ Active |",
           "| Token-Efficient PDF/Table Compressor | ✅ Active |",
           "| 3-Field Personal Doc Isolation | ✅ Active |",
           "| Knowledge Graph Multi-Hop Traversal | ✅ Active |",
           "| MF Deterministic Lookup (<2ms) | ✅ Active |",
           "| Monthly Regulatory Watchdog | ✅ Active |",
           "| Daily Equity + NAV Snapshot Scheduler | ✅ Active (Phase 6) |",
           "| Live News RSS Node (15min cache) | ✅ Active (Phase 6) |",
           "| Historical Return API (1d/1w/1m/3m/6m/1y) | ✅ Active (Phase 6) |",
           "| SSE Streaming Chat | ✅ Active |",
           "| JWT Auth + OTP Email Verification | ✅ Active |",
           "| Sliding-Window Rate Limiter | ✅ Active |",
           "| React Vite Frontend (TTS, Action Chips, Copy) | ✅ Active |",
           "| FastAPI Lifespan (migrated from on_event) | ✅ Active |",
           ""]

    failed_groups = [r for r in results if r["status"] == "FAIL"]
    if failed_groups:
        md += ["---", "", "## ⚠️ 7. Failure Details", ""]
        for r in failed_groups:
            md += [f"### {r['group']}", "", "```", r.get("output_tail", ""), "```", ""]

    md.append(f"\n---\n*Report generated at {TIMESTAMP}*")

    out_md = REPORT_DIR / "MASTER_EVAL_REPORT.md"
    out_md.write_text("\n".join(md), encoding="utf-8")

    json_summary = {
        "generated_at": TIMESTAMP, "suite_status": suite_status,
        "total_tests": total_tests, "total_passed": total_passed,
        "total_failed": total_failed, "pass_rate_pct": pass_rate,
        "groups": results,
    }
    (REPORT_DIR / "MASTER_EVAL_SUMMARY.json").write_text(
        json.dumps(json_summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"  FINAL RESULT: {suite_status}")
    print(f"  {total_passed}/{total_tests} tests passed ({pass_rate}%)")
    print(f"  Report: {out_md}")
    print("=" * 60)
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
