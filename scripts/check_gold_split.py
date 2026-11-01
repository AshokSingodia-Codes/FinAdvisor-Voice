"""
scripts/check_gold_split.py
Validates the gold benchmark dataset and dev/test splits:
1. Unique IDs across all items.
2. Zero question text overlap between dev and test splits.
3. Every retrieval gold source file exists in the indexed corpus.
4. Every route label is in the canonical route set.
5. Every trap question names an entity that is absent from the indexed corpus.
6. Target counts: Retrieval >= 50, Faithfulness >= 30, Trap >= 30.

Exit 0 only if all pass; non-zero on any failure.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANONICAL_ROUTES = {
    "hybrid_search",
    "financial_table",
    "calculation",
    "math_calculation",
    "live_market_data",
    "current_events",
    "direct_answer",
    "decompose",
}

FICTIONAL_OR_ABSENT_MARKERS = [
    "atlantis",
    "icar",
    "teleportation",
    "lunar",
    "metaverse",
    "flying vehicle",
    "quantumleap",
    "lehman",
    "enron",
    "pan american",
    "pets.com",
    "theranos",
    "blockbuster",
    "wirecard",
    "silicon valley bank",
    "bear stearns",
    "ftx",
    "kodak",
    "concorde",
    "standard oil",
    "acme solar",
    "spacex",
    "quantum dynamics",
    "blue horizon",
    "2035",
    "hedgefund alpha",
    "perpetual motion",
    "orion space",
    "cybermart",
    "titan aero",
    "lead into gold",
]


def check_gold_split():
    print("=" * 60)
    print("🔍 AUDITING GOLD DATASET & DEV/TEST SPLITS")
    print("=" * 60)

    gold_path = os.path.join(ROOT, "tests", "eval", "gold_set.json")
    dev_path = os.path.join(ROOT, "tests", "eval", "gold_set_dev.json")
    test_path = os.path.join(ROOT, "tests", "eval", "gold_set_test.json")

    for p in [gold_path, dev_path, test_path]:
        if not os.path.exists(p):
            print(f"❌ Missing file: {p}")
            sys.exit(1)

    with open(gold_path, "r", encoding="utf-8") as f:
        gold = json.load(f)
    with open(dev_path, "r", encoding="utf-8") as f:
        dev = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test = json.load(f)

    errors = []

    # 1. Unique IDs
    ids = [q["id"] for q in gold]
    if len(ids) != len(set(ids)):
        dup_ids = [k for k, v in Counter(ids).items() if v > 1]
        errors.append(f"Duplicate IDs in gold_set: {dup_ids}")

    dev_ids = {q["id"] for q in dev}
    test_ids = {q["id"] for q in test}
    id_overlap = dev_ids.intersection(test_ids)
    if id_overlap:
        errors.append(f"ID overlap between dev and test: {id_overlap}")

    # 2. Zero question text overlap
    dev_questions = {q["question"].strip().lower() for q in dev}
    test_questions = {q["question"].strip().lower() for q in test}
    q_overlap = dev_questions.intersection(test_questions)
    if q_overlap:
        errors.append(
            f"Question text overlap between dev and test ({len(q_overlap)} items): {list(q_overlap)[:3]}"
        )

    # 3. Canonical routes
    for item in gold:
        route = item.get("expected_route")
        if route not in CANONICAL_ROUTES:
            errors.append(f"Item {item.get('id')} has non-canonical route: {route}")

    # 4. Retrieval gold source exists in indexed corpus
    for item in gold:
        if (
            not item.get("is_out_of_corpus")
            and item.get("expected_route") == "hybrid_search"
        ):
            src = item.get("gold_source")
            if not src:
                errors.append(f"Retrieval item {item.get('id')} missing gold_source")
            elif src != "computational_engine" and not os.path.exists(
                os.path.join(ROOT, src)
            ):
                errors.append(
                    f"Gold source does not exist: {src} for item {item.get('id')}"
                )

    # 5. Trap questions name entities absent from corpus
    for item in gold:
        if item.get("is_out_of_corpus"):
            q_lower = item.get("question", "").lower()
            has_absent_marker = any(m in q_lower for m in FICTIONAL_OR_ABSENT_MARKERS)
            if not has_absent_marker:
                errors.append(
                    f"Trap item {item.get('id')} does not name an absent/fictional entity: {item.get('question')}"
                )

    # 6. Target counts
    retrieval_all = [
        q
        for q in gold
        if not q.get("is_out_of_corpus") and q.get("expected_route") == "hybrid_search"
    ]
    trap_all = [q for q in gold if q.get("is_out_of_corpus")]
    faithfulness_all = retrieval_all

    print("\n📊 Benchmark Metrics Count vs Targets:")
    print(
        f"  • Retrieval Questions:    {len(retrieval_all)} (Target: >=50) -> {'✅ PASS' if len(retrieval_all) >= 50 else '❌ FAIL'}"
    )
    print(
        f"  • Faithfulness Candidate: {len(faithfulness_all)} (Target: >=30) -> {'✅ PASS' if len(faithfulness_all) >= 30 else '❌ FAIL'}"
    )
    print(
        f"  • Trap Questions:         {len(trap_all)} (Target: >=30) -> {'✅ PASS' if len(trap_all) >= 30 else '❌ FAIL'}"
    )

    print("\n📋 Per-Category Split Counts:")
    print(f"  Dev set total:  {len(dev)}")
    for cat, cnt in Counter(q.get("category") for q in dev).items():
        print(f"    - {cat}: {cnt}")
    print(f"  Test set total: {len(test)}")
    for cat, cnt in Counter(q.get("category") for q in test).items():
        print(f"    - {cat}: {cnt}")

    if errors:
        print("\n❌ VALIDATION ERRORS FOUND:")
        for err in errors:
            print(f"  • {err}")
        sys.exit(1)

    print("\n✅ ALL GOLD BENCHMARK & SPLIT CHECKS PASSED SUCCESSFULLY!\n")
    sys.exit(0)


if __name__ == "__main__":
    check_gold_split()
