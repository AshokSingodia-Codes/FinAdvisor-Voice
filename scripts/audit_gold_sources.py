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
    print("🔍 AUDITING GOLD SOURCES (STRICT VALUE & PHRASE PROXIMITY CHECK)")
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
    print(f"Auditing {len(retrieval_items)} retrieval items under strict numeric & conceptual rules...")

    verified_list = []
    unverified_list = []
    failed_list = []

    stopwords = {
        "where", "which", "their", "there", "about", "these", "those", "after",
        "before", "under", "between", "through", "across", "because", "during",
        "without", "rather", "stated", "state", "retrieve", "exact", "number",
        "calculate", "explain", "from", "with", "over", "into", "than", "more",
        "less", "both", "years", "total", "what", "were", "when", "that", "this",
        "have", "been", "using", "perform", "used"
    }

    for item in retrieval_items:
        qid = item["id"]
        src = item.get("gold_source")
        if not src or src not in corpus_texts:
            failed_list.append({
                "id": qid,
                "question": item["question"],
                "reason": f"Source {src} not found in indexed corpus."
            })
            continue

        doc = corpus_texts[src]
        ans = item.get("expected_answer", "")
        topics = [kw.lower() for kw in item.get("gold_keywords", []) if len(kw) >= 3]

        # Extract numeric values
        ans_nums = re.findall(r"[\$₹]?\d+(?:,\d+)*(?:\.\d+)?%?", ans)
        key_numbers = [n.replace("$", "").replace("₹", "").strip() for n in ans_nums if len(n.strip()) >= 2]

        is_verified = False
        audit_note = ""
        matched_excerpt = ""

        if key_numbers:
            # RULE 1: Numeric answers - every key number must appear within 300 characters of a topic term
            numeric_passes = []
            for num in key_numbers:
                num_matched = False
                for m in re.finditer(re.escape(num), doc, re.IGNORECASE):
                    idx = m.start()
                    window = doc[max(0, idx - 300): min(len(doc), idx + 300)].lower()
                    if any(top in window for top in topics):
                        num_matched = True
                        if not matched_excerpt:
                            matched_excerpt = doc[max(0, idx - 60): min(len(doc), idx + 140)].replace("\n", " ").strip()
                        break
                numeric_passes.append(num_matched)

            if all(numeric_passes):
                is_verified = True
                audit_note = f"All {len(key_numbers)} key numbers matched within 300 chars of topic."
            else:
                audit_note = f"Only {sum(numeric_passes)} of {len(key_numbers)} numbers matched within 300 chars."
        else:
            # RULE 2: Conceptual answers - require at least 3 distinct content terms inside one 500-char window
            content_terms = [
                t.lower() for t in re.findall(r"[a-zA-Z]{4,}", ans)
                if t.lower() not in stopwords
            ]
            unique_terms = list(dict.fromkeys(content_terms))

            if len(unique_terms) >= 3:
                # Find a 500-char window containing at least 3 unique content terms
                # We can iterate through positions of the first term
                found_window = False
                for t1 in unique_terms:
                    for m in re.finditer(r"\b" + re.escape(t1) + r"\b", doc, re.IGNORECASE):
                        idx = m.start()
                        w_start = max(0, idx - 100)
                        w_end = min(len(doc), idx + 400)
                        window = doc[w_start:w_end].lower()

                        matched_in_win = [term for term in unique_terms if re.search(r"\b" + re.escape(term) + r"\b", window)]
                        if len(matched_in_win) >= 3:
                            found_window = True
                            matched_excerpt = doc[w_start:w_end].replace("\n", " ").strip()
                            audit_note = f"Matched {len(matched_in_win)} terms ({matched_in_win[:4]}) in 500-char window."
                            break
                    if found_window:
                        break

                if found_window:
                    is_verified = True
                else:
                    audit_note = "Could not find 3 distinct content terms within a 500-char window."
            else:
                audit_note = f"Too few unique content terms ({len(unique_terms)}) for 3-term conceptual verification."

        record = {
            "id": qid,
            "question": item["question"],
            "expected_answer": ans,
            "gold_source": src,
            "audit_note": audit_note,
            "excerpt": f"...{matched_excerpt}..." if matched_excerpt else None
        }

        if is_verified:
            verified_list.append(record)
        else:
            if not key_numbers:
                record["classification"] = "unverified (conceptual)"
                unverified_list.append(record)
            else:
                record["classification"] = "failed (numeric proximity)"
                failed_list.append(record)

    print("\nAudit completed under strict rules:")
    print(f"  • Verified items:              {len(verified_list)}")
    print(f"  • Unverified (conceptual):     {len(unverified_list)}")
    print(f"  • Failed (numeric proximity):  {len(failed_list)}")

    out_path = os.path.join(ROOT, "reports", "latest", "gold_source_audit.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_retrieval_items_audited": len(retrieval_items),
            "verified_count": len(verified_list),
            "unverified_conceptual_count": len(unverified_list),
            "failed_count": len(failed_list),
            "verified_items": verified_list,
            "unverified_conceptual_items": unverified_list,
            "failed_items": failed_list
        }, f, indent=2)
    print(f"Saved strict audit results to {out_path}")

    # Print sample verified items
    print("\n" + "=" * 60)
    print("📋 SAMPLE VERIFIED RETRIEVAL ITEMS WITH GROUNDED PASSAGES")
    print("=" * 60)
    rng = random.Random(42)
    sample_items = rng.sample(verified_list, min(10, len(verified_list)))
    for i, ex in enumerate(sample_items, 1):
        print(f"\n[{i}] ID: {ex['id']}")
        print(f"    Question: {ex['question']}")
        print(f"    Expected Answer: {ex['expected_answer']}")
        print(f"    Verification Note: {ex['audit_note']}")
        print(f"    Corpus Excerpt: {ex['excerpt']}")

    if unverified_list:
        print("\n" + "=" * 60)
        print("⚠️ UNVERIFIED (CONCEPTUAL) ITEMS")
        print("=" * 60)
        for u in unverified_list:
            print(f"  • {u['id']}: {u['question']} -> {u['audit_note']}")

    if failed_list:
        print("\n" + "=" * 60)
        print("❌ FAILED (NUMERIC PROXIMITY) ITEMS")
        print("=" * 60)
        for fl in failed_list:
            print(f"  • {fl['id']}: {fl['question']} -> {fl['audit_note']}")


if __name__ == "__main__":
    audit_gold_sources()
