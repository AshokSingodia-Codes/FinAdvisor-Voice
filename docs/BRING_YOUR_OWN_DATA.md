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

## 3. Purging Copyrighted Books & Serialized Blobs from Git History

If you maintain a fork or clone of the repository that previously had copyrighted PDF files or binary `.pkl` files committed in history, run `git-filter-repo` to permanently remove them from the entire commit tree.

> **Caution**:
> 1. `git-filter-repo` rewrites git commit history and changes all commit hashes.
> 2. By design, `git-filter-repo` **removes the `origin` remote** to prevent accidental pushes to production before inspection. You will re-add your remote after verifying the filter.
> 3. Always run `git-filter-repo` on a **fresh clone** of your repository. Do not use `--force` unless `git-filter-repo` explicitly requests it.

### Step 1: Install `git-filter-repo`
```bash
pip install git-filter-repo
```

### Step 2: Make a Fresh Clone
```bash
git clone https://github.com/AshokSingodia-Codes/FinAdvisor-Voice.git finadvisor-clean
cd finadvisor-clean
git checkout stage4-fixes
```

### Step 3: Execute History Purge
Purge the specific files removed on this branch (copyrighted book PDFs) and historical binary `.pkl` dumps (`graph_documents.pkl`):
```bash
git filter-repo --invert-paths \
  --path "data/A-random-walk-down-Wall-Street-the-time-tested-strategy-for-successful-investing.-Malkiel-Burton-G.-W.W.-Norton-2006.-ISBN-9780470593219-SA7-Unit-10.pdf" \
  --path "data/personal-finance-for-dummies.pdf" \
  --path "graph_documents.pkl"
```

### Step 4: Re-add Origin Remote & Verify
```bash
# Re-link your remote repository (removed by git-filter-repo for safety)
git remote add origin https://github.com/AshokSingodia-Codes/FinAdvisor-Voice.git

# Verify no copyrighted or pkl files remain in any revision
git log --all --full-history -- "**.pdf" "**.pkl"
```

### Step 5: Force Push Rewritten Tree (Owner Action)
```bash
# Push rewritten branch to origin (requires repository owner access)
git push origin stage4-fixes --force
```
