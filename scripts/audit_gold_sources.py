import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import os
import pypdf
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit_gold_sources():
    print("=" * 60)
    print("🔍 AUDITING GOLD SOURCES FOR RETRIEVAL ITEMS")
    print("=" * 60)

    # 1. Load corpus texts into memory
    corpus_texts = {}

    # Apple 10-K
    pdf_path = os.path.join(ROOT, "Annual Report", "NASDAQ_AAPL_2024.pdf")
    if os.path.exists(pdf_path):
        reader = pypdf.PdfReader(pdf_path)
        aapl_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                aapl_text += "\n" + t
        corpus_texts["Annual Report/NASDAQ_AAPL_2024.pdf"] = aapl_text
        print(f"Loaded Apple 10-K: {len(aapl_text)} characters.")

    # Ultimate Finance Knowledge Base
    kb_path = os.path.join(ROOT, "Annual Report", "Ultimate_Finance_Knowledge_Base.md")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            corpus_texts["Annual Report/Ultimate_Finance_Knowledge_Base.md"] = f.read()
        print(f"Loaded Knowledge Base: {len(corpus_texts['Annual Report/Ultimate_Finance_Knowledge_Base.md'])} characters.")

    # 2. Check gold items
    gold_path = os.path.join(ROOT, "tests", "eval", "gold_set.json")
    with open(gold_path, "r", encoding="utf-8") as f:
        gold = json.load(f)

    retrieval_items = [q for q in gold if not q.get("is_out_of_corpus") and q.get("expected_route") == "hybrid_search"]
    print(f"Auditing {len(retrieval_items)} retrieval items...")

    audit_failures = []
    audited_examples = []

    for item in retrieval_items:
        src = item.get("gold_source")
        if not src or src not in corpus_texts:
            continue

        c_text = corpus_texts[src].lower()
        # Find match for answer or keywords
        ans = item.get("expected_answer", "")
        keywords = item.get("gold_keywords", [])

        # Check which keywords or numbers appear
        found_matches = []
        for kw in keywords:
            clean_kw = kw.lower().replace(",", "").replace("$", "").replace("₹", "").strip()
            if clean_kw and (clean_kw in c_text or kw.lower() in c_text):
                found_matches.append(kw)

        if not found_matches:
            audit_failures.append({
                "id": item["id"],
                "question": item["question"],
                "gold_source": src,
                "gold_keywords": keywords,
                "reason": "None of the gold keywords or numbers found in source document."
            })
        else:
            # Capture excerpt around first match
            first_kw = found_matches[0].lower()
            idx = c_text.find(first_kw)
            excerpt = corpus_texts[src][max(0, idx - 60): min(len(corpus_texts[src]), idx + 120)].replace("\n", " ").strip()
            audited_examples.append({
                "id": item["id"],
                "question": item["question"],
                "matched_keyword": found_matches[0],
                "all_matches": found_matches,
                "excerpt": f"...{excerpt}..."
            })

    print(f"Audit completed: {len(audited_examples)} verified, {len(audit_failures)} failed.")

    # Save audit report
    out_path = os.path.join(ROOT, "reports", "latest", "gold_source_audit.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_retrieval_items_audited": len(retrieval_items),
            "verified_count": len(audited_examples),
            "failure_count": len(audit_failures),
            "failures": audit_failures
        }, f, indent=2)
    print(f"Saved audit results to {out_path}")

    # Print 10 review items
    print("\n" + "=" * 60)
    print("📋 10 REVIEW RETRIEVAL ITEMS WITH GROUNDED MATCHING EXCERPTS")
    print("=" * 60)
    sample_10 = audited_examples[:10]
    for i, ex in enumerate(sample_10, 1):
        print(f"\n[{i}] ID: {ex['id']}")
        print(f"    Question: {ex['question']}")
        print(f"    Matched Answer/Keyword: '{ex['matched_keyword']}'")
        print(f"    Corpus Excerpt: {ex['excerpt']}")

if __name__ == "__main__":
    audit_gold_sources()
