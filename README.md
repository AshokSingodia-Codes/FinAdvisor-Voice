# FinAdvisor-X: Hybrid RAG Financial Intelligence Platform

[![CI](https://github.com/AshokSingodia-Codes/FinAdvisor-Voice/actions/workflows/ci.yml/badge.svg)](https://github.com/AshokSingodia-Codes/FinAdvisor-Voice/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00.svg?logo=langchain&logoColor=white)](https://python.langchain.com/v0.1/docs/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Vector_&_Fulltext-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **FinAdvisor-X**: Hybrid RAG: Neo4j vector + Lucene fulltext, RRF fusion, FlashRank rerank.

FinAdvisor-X is a financial question-answering and calculations system featuring browser Web Speech API voice input, hybrid search combining dense vector embeddings and BM25 fulltext indexing over Neo4j, Reciprocal Rank Fusion (RRF $k=60$), cross-encoder reranking, and deterministic financial math computation.

---

## What It Needs

- **Python**: Version `3.11` or `3.12`
- **Node.js**: Version `18+` or `20+` with `pnpm`
- **Neo4j Aura**: A running Neo4j Aura cloud instance or local Neo4j instance with Vector and Fulltext index support
- **Groq API Key**: `GROQ_API_KEY` for LLM routing, verifier evaluation, and synthesis
- **Optional Services** (documented in `.env.example`):
  - `GOOGLE_API_KEY`: Fallback Gemini model access
  - `OPENROUTER_API_KEY`: Fallback OpenRouter access
  - `DATABASE_URL`: Hosted PostgreSQL connection string (defaults to local SQLite at `data/conversations.db` if unset)
  - `ENCRYPTION_KEY`: Fernet AES-128 key for encrypted personal document storage
  - `BREVO_API_KEY` / `SMTP_*`: Optional email verification notifications

---

## Setup Commands

> *Notice: Commands in this README were taken from the code and `.env.example` and were not re-run on a fresh machine.*

```bash
# 1. Clone repository and checkout branch
git clone https://github.com/AshokSingodia-Codes/FinAdvisor-Voice.git
cd FinAdvisor-Voice
git checkout stage4-fixes

# 2. Backend virtual environment & dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Open .env and add your NEO4J_URI, NEO4J_PASSWORD, and GROQ_API_KEY

# 4. Frontend setup
cd frontend
pnpm install
cd ..
```

---

## How to Ingest Your Own Documents

To index your own corporate disclosures, PDF reports, or text files into Neo4j without relying on bundled data, follow the guide in [docs/BRING_YOUR_OWN_DATA.md](docs/BRING_YOUR_OWN_DATA.md):

```bash
# Ingest your own PDF or markdown documents into Neo4j
python scripts/ingest_sec_10k.py --file path/to/your/document.pdf
```

---

## How to Start Backend and Frontend

```bash
# Terminal 1: Start FastAPI Backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start React Frontend
cd frontend
pnpm run dev
```

---

## How to Ask a First Question

1. Open your browser to `http://localhost:5173`.
2. Register or log in with any test credentials (e.g. `test@example.com` / `password123`).
3. Click the microphone icon to dictate via the browser Web Speech API, or type a financial question into the chat box:
   - Factual 10-K query: *"What were Apple's total net sales in fiscal year 2024?"*
   - Deterministic calculation: *"Calculate the future value of a monthly SIP of ₹10,000 for 10 years at 12% annual return."*
   - Market quote: *"What is the stock price and PE ratio of RELIANCE.NS?"*

---

## Configuration Table (from `.env.example`)

| Variable | Description | Required | Default / Format |
|---|---|---|---|
| `NEO4J_URI` | Neo4j Aura or local connection bolt URI | Yes | `neo4j+s://<instance-id>.databases.neo4j.io` |
| `NEO4J_USERNAME` | Neo4j database user | Yes | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j database password | Yes | *(secret)* |
| `GROQ_API_KEY` | Groq platform API key | Yes | `gsk_...` |
| `DATABASE_URL` | PostgreSQL URI with sslmode=require | No | Fallback: SQLite at `data/conversations.db` |
| `JWT_SECRET` | Secret key for HS256 authentication tokens | Yes | Minimum 32-character secret |
| `ENCRYPTION_KEY` | Fernet key for encrypting user documents | No | Fallback: ephemeral per-process key |
| `BREVO_API_KEY` | Brevo API key for transactional emails | No | `xkeysib-...` |
| `SMTP_HOST` | Fallback SMTP host for email delivery | No | `smtp.gmail.com` |

---

## Empirical Benchmark Results

<!-- BENCHMARK_TABLE_START -->
| Pipeline Stage / Subsystem | Run | n | Precision@5 | Recall@5 | MRR | Avg Latency |
|---|---|---|---|---|---|---|
| **Vector-Only (`bge-small-en-v1.5`)** | `legacy_pre_split` | 34 | `0.3882` | `0.6353` | `0.6529` | `3043.1 ms` |
| **Keyword-Only (Lucene Fulltext)** | `legacy_pre_split` | 34 | `0.4412` | `0.598` | `0.6382` | `976.5 ms` |
| **Hybrid Search (RRF $k=60$)** | `legacy_pre_split` | 34 | `0.3941` | `0.6088` | `0.6765` | `903.1 ms` |
| **Hybrid + FlashRank Cross-Encoder** | `legacy_pre_split` | 34 | `0.4588` | `0.6088` | `0.5735` | `3955.6 ms` |
| **Semantic Router (Clean Holdout V2)** | `holdout_v2` | 30 | `Accuracy: 83.3%` | `N/A` | `N/A` | `N/A` |
| **Semantic Router (Full Test Split)** | `contaminated` | 45 | `Accuracy: 95.6%` | `N/A` | `N/A` | `434.36 ms` |
| **Semantic Router (Test Split, No Traps)** | `contaminated` | 30 | `Accuracy: 93.3%` | `N/A` | `N/A` | `434.36 ms` |
| **Draft Answer (Verifier OFF)** | `legacy_pre_split` | 5 | `Faith: 4.20/5.0` | `Grounded: 80.0%` | `N/A` | `N/A` |
| **Verified Answer (Verifier ON)** | `legacy_pre_split` | 5 | `Faith: 3.40/5.0` | `Grounded: 60.0%` | `N/A` | `N/A` |
| **Adversarial Trap Abstention** | `legacy_pre_split` | 10 | `Abstain: 100.0%` | `Halluc: 0.0%` | `N/A` | `N/A` |
<!-- BENCHMARK_TABLE_END -->

All metrics in this table are drawn directly from `reports/latest/eval_metrics_latest.json`. No numbers are estimated or rounded up. For the complete audit and claims ledger, see [docs/CLAIMS.md](docs/CLAIMS.md).

---

## Known Limitations

1. **Test Split Grounding Audit**: Out of 54 audited retrieval gold questions (`reports/latest/gold_source_audit.json`), **33 are verified**, **1 is unverified conceptual** (`q025`), and **20 failed numeric proximity matching**. All 20 failed items reside in the held-out frozen test split (`tests/eval/gold_set_test.json`) due to parenthetical conversions (e.g. `($... billion)`) that do not appear verbatim within 300 characters of the segment topic in the raw 10-K tables. Because the test split was left unchanged on purpose to maintain SHA-256 freeze integrity, **retrieval benchmark results on the test split are NOT reliable** until a new test split (`gold_set_test_v2.json`) is authored, audited, and frozen. Never assume 54/54 items are verified.
2. **Router Misclassification & Tuning Contamination**: The fallback heuristic achieved 95.6% on the full 45-item test split and 93.3% on the 30-item test split (traps excluded); however, both results are **contaminated** because 9 of the 18 queries inspected during heuristic tuning overlapped with the test split. On the clean, uninspected holdout_v2 dataset (30 questions written by the agent after the fallback rules were designed; not tuned on), overall accuracy was **83.3%** (25/30), with the **calculation route scoring only 2/5 correct (40.0%)** (often misrouted to hybrid_search).
3. **Self-RAG Verifier Regression**: On the evaluated sample ($n=5$), verifier rewrites reduced factual grounding (60.0% vs 80.0%) and lowered faithfulness scores (3.4 vs 4.2). It remains **disabled by default** (`VERIFIER_ENABLED=False`) until prompt calibration and few-shot grounding examples are implemented.
4. **Free-Tier Cold Starts & Rate Limits**: Serverless PostgreSQL (Neon) and cloud container hosts experience cold starts of 30-60 seconds on initial spin-up after inactivity. Provider LLM APIs on free tiers (Groq) are subject to intermittent per-minute rate limits.
5. **FlashRank Latency Cost**: While cross-encoder reranking yields a 16.42% precision gain on top-5 results, it increases total query latency by over 3 seconds (0.9s to 4.0s).

---

## What Is NOT Done and Commands to Finish It

1. **Full Split Retrieval Benchmark on Current Index**:
   - Status: Legacy retrieval numbers ($n=34$) come from an earlier commit and have not been re-run across the full dev/test split.
   - Command to run:
     ```bash
     python -m tests.eval.eval_retrieval
     ```
2. **Faithfulness & Verifier Benchmark on Full Split ($n \ge 27$)**:
   - Status: Measured on $n=5$ only; full split evaluation pending.
   - Command to run:
     ```bash
     python -m tests.eval.eval_faithfulness
     ```
3. **Adversarial Trap Benchmark on Full Split ($n=30$)**:
   - Status: Measured on $n=10$ historical questions; test split has $n=15$ traps.
   - Command to run:
     ```bash
     python -m tests.eval.eval_trap_questions
     ```
4. **Clean Held-Out Test Split (v2) Authoring**:
   - Status: Current test split contains 20 ungrounded numeric parentheticals and 9 queries contaminated during router tuning. A clean `gold_set_test_v2.json` must be written and frozen.

---

## Synthetic Corpus Disclosure

- The finance textbook corpus located in `Annual Report/Ultimate_Finance_Knowledge_Base.md` and generated via `scripts/generate_textbook*.py` is **Synthetic Data** generated using LLM prompts for educational retrieval benchmarking.
- Real-world filings included in this repository (e.g. `NASDAQ_AAPL_2024.pdf`) are public domain U.S. SEC corporate disclosures.

---

## License & Third-Party Materials

- **License**: Released under the [MIT License](LICENSE).
- **Third-Party Copyright Notice**: Commercial or copyrighted books (such as Malkiel's *A Random Walk Down Wall Street* or *Personal Finance for Dummies*) are **NOT included** in this repository and have been purged from the git history. Users wishing to index external materials should consult [docs/BRING_YOUR_OWN_DATA.md](docs/BRING_YOUR_OWN_DATA.md).
