# Bring Your Own Data (BYOD) Guide & Ingestion Instructions

FinAdvisor-X uses a local and vector-augmented retrieval system without distributing copyrighted materials (such as third-party personal finance books). Users supply their own public domain, licensed, or personal financial documents.

---

## 1. Supported Document Types and Directory Setup

Place your reference documents in the `data/` directory or SEC filing reports in the designated directory:

* **PDF Documents**: Financial reports, 10-K filings, mutual fund statements, and personal financial guidebooks.
  * Default location: `data/` or `Annual Report/`
  * Example: Public domain SEC 10-K filings such as `Annual Report/NASDAQ_AAPL_2024.pdf`.
* **Markdown Guides**: Custom notes or financial glossaries.
  * Location: `data/personal_finance_and_tax_guide.md`
* **Structured Data**: JSON datasets (e.g. mutual funds, balance sheets).
  * Location: `data/top_mutual_funds_dataset.json`

> **Note**: `data/*.pdf` is ignored by `.gitignore` so your private or proprietary documents are never committed to version control.

---

## 2. Ingestion Commands

Once you have placed your documents in `data/`, run the ingestion pipeline to parse documents, chunk text, compute embeddings using FastEmbed (`bge-small-en-v1.5`), and index them in Neo4j (Vector + Lucene full-text):

### A. Ingest SEC 10-K / Annual Reports (Apple, etc.)
```bash
python scripts/index_pdf.py --pdf "Annual Report/NASDAQ_AAPL_2024.pdf" --ticker AAPL
```

### B. Ingest Custom PDF Documents
```bash
python scripts/index_pdf.py --pdf "data/your-document.pdf" --category personal_finance
```

### C. Ingest Personal Finance & Tax Knowledge Base
```bash
python scripts/build_hybrid_index.py
```

### D. Verify the Index in Neo4j
```bash
python scripts/verify_index.py
```

---

## 3. Purging Copyrighted Books from Git History

If you maintain a fork or repository that previously had copyrighted PDF files committed in history, run `git-filter-repo` to completely remove them from your commit tree.

> **Caution**: `git-filter-repo` rewrites your local git commit hashes. Coordinate with your team before pushing rewritten branches.

### Install `git-filter-repo`
```bash
pip install git-filter-repo
```

### Execute Purge Commands (Run by repository owner)
Run these commands from the root of your repository:
```bash
# Analyze and verify the files to delete
git filter-repo --invert-paths --path "data/A-random-walk-down-Wall-Street-the-time-tested-strategy-for-successful-investing.-Malkiel-Burton-G.-W.W.-Norton-2006.-ISBN-9780470593219-SA7-Unit-10.pdf" --path "data/personal-finance-for-dummies.pdf"

# Clean up reflogs and prune expired objects
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

To update the remote repository (requires explicit repository owner action):
```bash
# Replace <remote> and <branch> with your destination (e.g., origin stage4-fixes)
git push origin stage4-fixes --force
```
