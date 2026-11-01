import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import os
import random
import re

import pypdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def audit_gold_sources():
    print("=" * 60)
    print("🔍 AUDITING GOLD SOURCES (VALUE & PHRASE PROXIMITY CHECK)")
    print("=" * 60)

    # 1. Load corpus texts into memory
    corpus_texts = {}

    pdf_path = os.path.join(ROOT, "Annual Report", "NASDAQ_AAPL_2024.pdf")
    if os.path.exists(pdf_path):
        reader = pypdf.PdfReader(pdf_path)
        aapl_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        corpus_texts["Annual Report/NASDAQ_AAPL_2024.pdf"] = aapl_text
        print(f"Loaded Apple 10-K: {len(aapl_text)} characters.")

    kb_path = os.path.join(ROOT, "Annual Report", "Ultimate_Finance_Knowledge_Base.md")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            corpus_texts["Annual Report/Ultimate_Finance_Knowledge_Base.md"] = f.read()
        print(f"Loaded Knowledge Base: {len(corpus_texts['Annual Report/Ultimate_Finance_Knowledge_Base.md'])} characters.")

    # 2. Check all retrieval items
    gold_path = os.path.join(ROOT, "tests", "eval", "gold_set.json")
    with open(gold_path, "r", encoding="utf-8") as f:
        gold = json.load(f)

    retrieval_items = [q for q in gold if not q.get("is_out_of_corpus") and q.get("expected_route") == "hybrid_search"]
    print(f"Auditing {len(retrieval_items)} retrieval items for expected answer VALUE near topic...")

    audit_failures = []
    audited_examples = []

    stopwords = {
        "where", "which", "their", "there", "about", "these", "those", "after",
        "before", "under", "between", "through", "across", "because", "during",
        "without", "rather", "stated", "state", "retrieve", "exact", "number",
        "calculate", "explain", "from", "with", "over", "into", "than", "more",
        "less", "both", "years"
    }

    for item in retrieval_items:
        src = item.get("gold_source")
        if not src or src not in corpus_texts:
            audit_failures.append({
                "id": item["id"],
                "question": item["question"],
                "reason": f"Source {src} not found in indexed corpus."
            })
            continue

        doc = corpus_texts[src]
        ans = item.get("expected_answer", "")
        topics = [kw.lower() for kw in item.get("gold_keywords", []) if len(kw) >= 3]

        ans_nums = re.findall(r"[\$₹]?\d+(?:,\d+)*(?:\.\d+)?%?", ans)
        ans_terms = [
            t.lower() for t in re.findall(r"[a-zA-Z0-9_\-\+]{4,}", ans)
            if t.lower() not in stopwords
        ]

        matched_value = None
        matched_excerpt = None

        candidates = ans_nums + ans_terms
        for cand in candidates:
            cand_clean = cand.replace("$", "").replace("₹", "").replace("%", "").strip()
            if not cand_clean or len(cand_clean) < 3:
                continue

            for m in re.finditer(re.escape(cand_clean), doc, re.IGNORECASE):
                idx = m.start()
                # Check proximity: topic keyword within 500 characters
                window = doc[max(0, idx - 500): min(len(doc), idx + 500)].lower()
                if any(top in window for top in topics):
                    matched_value = cand
                    s = max(0, idx - 60)
                    e = min(len(doc), idx + 120)
                    matched_excerpt = doc[s:e].replace("\n", " ").strip()
                    break
            if matched_value:
                break

        if matched_value:
            audited_examples.append({
                "id": item["id"],
                "question": item["question"],
                "expected_answer": ans,
                "matched_value": matched_value,
                "excerpt": f"...{matched_excerpt}..."
            })
        else:
            audit_failures.append({
                "id": item["id"],
                "question": item["question"],
                "expected_answer": ans,
                "gold_source": src,
                "reason": "Expected answer value or key phrase not found near question topics in gold source."
            })

    print(f"Audit completed: {len(audited_examples)} verified, {len(audit_failures)} failed.")

    # Save audit report
    out_path = os.path.join(ROOT, "reports", "latest", "gold_source_audit.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_retrieval_items_audited": len(retrieval_items),
            "verified_count": len(audited_examples),
            "failure_count": len(audit_failures),
            "failures": audit_failures,
            "verified_items": audited_examples
        }, f, indent=2)
    print(f"Saved audit results to {out_path}")

    # Print 10 review items (seed fixed for reproducible display)
    print("\n" + "=" * 60)
    print("📋 10 AUDITED RETRIEVAL ITEMS WITH GROUNDED VALUE EXCERPTS")
    print("=" * 60)
    rng = random.Random(42)
    sample_10 = rng.sample(audited_examples, 10)
    for i, ex in enumerate(sample_10, 1):
        print(f"\n[{i}] ID: {ex['id']}")
        print(f"    Question: {ex['question']}")
        print(f"    Expected Answer: {ex['expected_answer']}")
        print(f"    Matched Value in Source: '{ex['matched_value']}'")
        print(f"    Corpus Excerpt: {ex['excerpt']}")


if __name__ == "__main__":
    audit_gold_sources()
