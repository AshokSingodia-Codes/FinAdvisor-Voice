# 📘 FinAdvisor-X: Live Demo Runbook & Architecture Verification

> **Status:** Verified Zero-RAM Hosted Multi-Agent Graph-RAG System  
> **Target Environment:** Render Free Tier (512MB RAM cap)  
> **Current Default Mode:** Safe Keyword + Graph Search (`VECTOR_SEARCH_ENABLED=false`)  
> **Embedding Strategy:** Gemini REST API (768-dim, $L_2$ normalized) on shared corpus; Private BM25 (`keyword_only`) on personal docs.

---

## 🎯 1. System Operating Modes & Safety Defaults

| Configuration Key | Default Value | Purpose / Guarantee |
|---|---|---|
| `VECTOR_SEARCH_ENABLED` | `false` | Operates in safe Zero-Embedding BM25 + Neo4j Graph mode while vector migration is $< 99\%$. |
| `PERSONAL_DOCS_EMBEDDING` | `keyword_only` | Personal documents are never sent to external embedding endpoints. |
| `PERSONAL_CONTEXT_PROVIDERS` | `groq,openrouter` | Personal context requests strictly exclude Google Gemini free tier. |
| `PERSONAL_CONTEXT_EMBEDDING` | `off` | Zero embedding queries on personal document sessions. |
| `RERANKER_PROVIDER` | `none` | Zero local ONNX/FlashRank memory allocation. |

---

## 🚀 2. How to Start FinAdvisor-X for Demo

### Step 1: Start the Backend Server (Terminal 1)
```powershell
cd E:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
- **Live API Documentation:** `http://127.0.0.1:8000/docs`
- **Memory Footprint:** ~130–150 MB RSS (well below the 512MB limit)

### Step 2: Start the React Frontend (Terminal 2)
```powershell
cd E:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main\frontend
npm run dev
```
- **Web Interface:** `http://localhost:5173`

---

## 📊 3. 10 Demo Questions Reference & Benchmark Results

| ID | Query | Expected Grounded Facts | Safe Baseline MRR | Latency (avg) |
|---|---|---|---|---|
| **`q001`** | What were Apple's total net sales in fiscal year 2024? | `$391,035 million` ($391.035B) | `1.00` | 1.9s |
| **`q002`** | How much net sales did Apple generate from iPhone products in FY 2024? | `$201,183 million` | `1.00` | 1.5s |
| **`q003`** | What was Apple's total Services revenue in FY2024? | `$96,169 million` | `1.00` | 1.9s |
| **`q004`** | What was Apple's net income for fiscal year 2024? | `$93,736 million` | `1.00` | 1.7s |
| **`q005`** | What were Apple's diluted earnings per share (EPS) in FY 2024? | `$6.08 per share` | `1.00` | 1.4s |
| **`q006`** | How much did Apple spend on R&D in fiscal 2024? | `$31,370 million` | `1.00` | 2.0s |
| **`q007`** | What was Apple's cash and cash equivalents at end of FY2024? | `$29,943 million` | `1.00` | 2.3s |
| **`q008`** | What is Section 80C maximum investment deduction limit? | `₹1,50,000 (1.5 Lakh)` | `1.00` | 1.7s |
| **`q009`** | What is the LTCG tax exemption limit under Budget 2024? | `₹1.25 Lakh` (12.5% tax above) | `1.00` | 1.6s |
| **`q010`** | What is the SIP future value for ₹10,000/mo at 12% for 10 years? | `₹23.23 Lakh` (deterministic formula) | `1.00` | 2.1s |

---

## 🛡️ 4. Multi-Layer Fallback & Privacy Matrix

```
[User Request]
       │
       ▼
[Personal Doc Attached?]
  ├── YES ──► Route: Groq (gpt-oss-120b) ──► (fail) ──► OpenRouter (ZDR: data_collection='deny')
  │           (Gemini strictly EXCLUDED from personal context)
  │
  └── NO  ──► Route: Groq (gpt-oss-120b) ──► (fail) ──► Gemini (3.5-flash-lite) ──► (fail) ──► OpenRouter
```

---

## 🔄 5. Resuming Vector Migration (After Demo / Reset)

To resume vector indexing once daily Gemini quota resets (Midnight Pacific Time):
```powershell
python scripts/migrate_vectors_v2.py
```
- Total chunks: `2,885`
- Migrated chunks: `1,370` (safely stored as `c.embedding_v2`)
- Remaining unmigrated: `1,515` (~2 daily runs)
