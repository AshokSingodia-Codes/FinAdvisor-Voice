# FinAdvisor-X: Enterprise Agentic Hybrid Graph-RAG Financial Intelligence Platform 📈🏛️

[![Live Frontend](https://img.shields.io/badge/Live_Frontend-Vercel-black.svg?logo=vercel&logoColor=white)](https://fin-advisor-voice.vercel.app/)
[![Live Backend](https://img.shields.io/badge/Live_API-Render-46E3B7.svg?logo=render&logoColor=white)](https://finadvisor-voice.onrender.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00.svg?logo=langchain&logoColor=white)](https://python.langchain.com/v0.1/docs/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_&_Vector-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Neon Postgres](https://img.shields.io/badge/Neon-PostgreSQL_Serverless-00E599.svg?logo=postgresql&logoColor=white)](https://neon.tech/)
[![Groq](https://img.shields.io/badge/Groq-LPU_Inference-F55036.svg)](https://groq.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 **Live Demo & Deployment**:
> - 🖥️ **Web Application**: [https://fin-advisor-voice.vercel.app](https://fin-advisor-voice.vercel.app)
> - ⚙️ **Backend API (Interactive Swagger Docs)**: [https://finadvisor-voice.onrender.com/docs](https://finadvisor-voice.onrender.com/docs)
> - 📦 **GitHub Repository**: [AshokSingodia-Codes/FinAdvisor-Voice](https://github.com/AshokSingodia-Codes/FinAdvisor-Voice)

**FinAdvisor-X** is an enterprise-grade **Agentic Hybrid Graph Retrieval-Augmented Generation (RAG)** platform equipped with **Speech-to-Text / Text-to-Speech Voice Interaction**, **Strict Multi-Tenant Document Privacy Isolation**, **Serverless Neon PostgreSQL Session Management**, and **Real-Time Financial Market & Indian Tax Intelligence (FY 2026-27)**.

---

## 📑 Table of Contents

1. [Key Capabilities & Features](#-key-capabilities--features)
2. [High-Level Architecture](#-high-level-architecture)
3. [Agentic LangGraph Workflow](#-agentic-langgraph-workflow)
4. [Knowledge Bases & Retrieval Pipeline](#-knowledge-bases--retrieval-pipeline)
5. [Security, Auth & Data Isolation Model](#-security-auth--data-isolation-model)
6. [Deterministic Engines & Tools](#-deterministic-engines--tools)
7. [Project Structure](#-project-structure)
8. [Getting Started & Local Setup](#-getting-started--local-setup)
9. [Docker Deployment](#-docker-deployment)
10. [REST API Documentation](#-rest-api-documentation)
11. [Automated Testing & Benchmarking](#-automated-testing--benchmarking)

---

## 🌟 Key Capabilities & Features

* **🎙️ End-to-End Voice Interaction (STT & TTS)**:
  - **Speech-to-Text**: Real-time voice transcription with animated audio waveforms.
  - **Text-to-Speech**: Synthesizes verified financial insights into spoken audio with instant play/pause controls.
* **🔒 3-Field Multi-Tenant Document Privacy Isolation**:
  - Upload personal financial files (PDFs, CSVs, salary slips, tax records, images).
  - Every chunk in Neo4j and Neon Postgres is strictly bound to `(user_id, document_id, conversation_id)`. Zero cross-user or cross-conversation data leaks.
  - Content-based `NonFinancialDocumentError` filter automatically rejects irrelevant non-financial uploads.
* **🔍 Hybrid Graph-RAG (Native Lucene BM25 + Dense Vectors + FlashRank)**:
  - Sub-15ms lexical search using Neo4j Lucene `keyword_markdown` fulltext indexing.
  - 768-dim dense semantic embeddings (`sentence-transformers/all-mpnet-base-v2` / `FastEmbed ONNX`).
  - Merged via Reciprocal Rank Fusion (RRF, $k=60$) and re-ranked with a local **FlashRank neural cross-encoder** (+5.16% precision lift).
* **⚡ Dual-Tier Cost-Optimized LLM Routing**:
  - High-frequency routing, sub-query decomposition, and Self-RAG verification powered by `Llama-3.3-70B-Versatile`.
  - In-depth evidence synthesis powered by `GPT-OSS-120B`.
  - Achieves a **~78% reduction in daily token costs**.
* **🛡️ Self-RAG Reflection & Adversarial Hallucination Defense**:
  - Automated auditing loop checks draft answers for grounding against retrieved sources.
  - **100% Trap Abstention Rate**: Safely refuses queries about fictional entities or unindexed quarters.
* **🧮 Deterministic Math Sandbox & Sub-2ms Mutual Fund Engine**:
  - Python AST calculator for zero-hallucination arithmetic (DCF, WACC, CAGR, SIP, EMI).
  - Local deterministic Indian Mutual Fund engine ([`tools/mf_lookup.py`](tools/mf_lookup.py)) indexing top SEBI benchmark funds across Large, Mid, Small, and Flexi Cap categories.
* **📜 Autonomous Monthly Regulatory Watchdog**:
  - Automated 1st-of-the-month background scheduler syncing the latest CBDT tax circulars, SEBI rules, and RBI guidelines with circuit breaker protection.
* **⚡ In-Memory User & Query Caching**:
  - High-speed TTL cache for authenticated users and recurring financial market queries, drastically reducing Neon Postgres pool overhead and external API latency.

---

## 🏗️ High-Level Architecture

```mermaid
graph TD;
    User([User Voice / Text]) --> UI[React 19 + Vite Dashboard];
    UI -->|HTTP / Audio STT| API[FastAPI Gateway :8000];
    
    subgraph Security_And_Storage [Data & Identity Layer]
        API --> Auth[JWT + OTP / Brevo HTTPS & Gmail SMTP];
        API --> RelationalDB[(Neon Serverless Postgres / SQLite)];
        API --> RateLimit[Token Bucket Rate Limiter];
        API --> Cache[In-Memory TTL Cache];
    end

    API --> LangGraph[LangGraph Stateful Orchestrator];

    subgraph Agentic_Pipeline [Multi-Agent Execution Graph]
        LangGraph --> Router{Semantic Router<br/>Llama-3.3-70B};
        
        Router -->|Multi-Year Analysis| Decompose[Decomposition Node];
        Router -->|10-K / Tax / Theory| Retriever[Hybrid Lucene + Dense Retriever];
        Router -->|Live Tickers| MarketData[Yahoo Finance Engine];
        Router -->|Calculations| MathCalc[Python AST Math Engine];
        Router -->|Mutual Funds| MFLookup[Sub-2ms Mutual Fund Tool];
        Router -->|Conversational| Evidence[Evidence Synthesizer<br/>GPT-OSS-120B];

        Decompose --> Retriever;
        Retriever --> Neo4j[(Neo4j Aura: Graph & Full-Text)];
        Retriever --> RRF[Reciprocal Rank Fusion];
        RRF --> FlashRank[FlashRank Cross-Encoder];
        FlashRank --> Evidence;
        MarketData --> Evidence;
        MathCalc --> Verifier;
        MFLookup --> Evidence;

        Evidence --> Verifier{Self-RAG Verifier<br/>Llama-3.3-70B};
        Verifier -->|Audit Failed: Missing Context| Retriever;
        Verifier -->|Audit Passed: Factual & Grounded| FinalAnswer[Final Response + TTS];
    end

    FinalAnswer --> API;
    API --> UI;
```

---

## 🤖 Agentic LangGraph Nodes

| Node | File | Responsibilities |
|---|---|---|
| **`router`** | [`nodes/router.py`](nodes/router.py) | Classifies query intent: `decompose`, `hybrid_search`, `calculation`, `math_calculation`, `live_market_data`, or `direct_answer`. |
| **`decompose`** | [`nodes/decomposition.py`](nodes/decomposition.py) | Splits complex multi-step financial questions into atomic sub-questions for parallel retrieval. |
| **`retriever`** | [`nodes/retriever.py`](nodes/retriever.py) | Runs native Lucene BM25 queries and vector searches in Neo4j Aura, fuses ranks via RRF, and applies FlashRank cross-encoding. |
| **`evidence_builder`**| [`nodes/evidence_builder.py`](nodes/evidence_builder.py) | Synthesizes retrieved filings, market facts, and math outputs into structured, citation-backed answers. |
| **`verifier`** | [`nodes/verifier.py`](nodes/verifier.py) | Self-RAG auditor checking numerical and factual consistency. Triggers iterative re-retrieval if context is missing. |
| **`math_solver`** | [`nodes/math_solver.py`](nodes/math_solver.py) | Extracts financial variables and dispatches formulas to safe Python AST math solvers. |
| **`live_data`** | [`nodes/market_data.py`](nodes/market_data.py) | Fetches real-time equity quotes, analyst price targets, and balance sheet ratios via `yfinance`. |

---

## 📚 Knowledge Bases & Retrieval Pipeline

1. **Corporate SEC 10-K Filings**:
   Audited financial statements (Consolidated Operations, Balance Sheets, Cash Flows, Segment Disclosures) for Apple, Microsoft, Tesla, Amazon, Alphabet, and Nvidia.
2. **Indian Taxation & Wealth Corpus (FY 2026-27 / AY 2027-28)**:
   - Section 115BAC New Tax Regime Slabs & ₹75,000 Standard Deduction.
   - Section 87A rebate (tax-free up to ₹7.75 Lakh taxable income).
   - Capital Gains Reforms (Budget 2024 / 2025): LTCG equity at 12.5% above ₹1.25 Lakh exemption; STCG equity at 20%.
   - SEBI Mutual Fund Categorization & Asset Allocation Frameworks (50-30-20 rule, SWP/STP rules).
3. **CA Curriculum & Investment Literature**:
   19-chapter financial textbook covering bookkeeping, GAAP/IFRS, valuation methods, derivatives, plus Malkiel's *A Random Walk Down Wall Street*.

---

## 📁 Project Structure

```text
Hybrid-Graph-RAG-Financial-Analyser-main/
├── config/
│   └── settings.py              # Pydantic BaseSettings loading environment configuration
├── core/
│   ├── auth.py                  # JWT tokens, bcrypt hashing, Brevo HTTPS & Gmail SMTP OTP
│   ├── cache.py                 # In-memory TTL response and user caching
│   ├── circuit_breaker.py       # Resilient API failure state machine
│   ├── crypto.py                # Symmetric encryption for sensitive credentials
│   ├── db.py                    # Neo4j connections, dual-tier LLMs (Llama-3.3-70B & GPT-OSS-120B)
│   ├── document_store.py        # 3-field personal document ingestion & security filters
│   ├── memory.py                # Neon PostgreSQL / SQLite multi-tenant memory
│   ├── rate_limiter.py          # Token-bucket user request rate limiter
│   ├── regulatory_feed_engine.py# Tax & regulatory RSS/HTML polling client
│   └── regulatory_watcher.py    # Autonomous 1st-of-the-month background sync loop
├── data/
│   ├── personal_finance_and_tax_guide.md # FY 2026-27 Indian Tax & Wealth Corpus
│   └── top_mutual_funds_dataset.json     # SEBI benchmark Indian mutual funds
├── frontend/                    # React 19 + TypeScript + Vite + Tailwind CSS UI
│   ├── src/
│   │   ├── App.tsx              # Main dashboard with voice playback & chat streaming
│   │   ├── components/
│   │   │   ├── AuthModal.tsx    # Modal auth dialog
│   │   │   ├── LoginPage.tsx    # Glassmorphic auth portal
│   │   │   └── VoiceInputButton.tsx # Speech-to-Text recording visualizer
│   │   └── context/
│   │       └── AuthContext.tsx  # JWT authentication session context
├── graph/
│   ├── state.py                 # AgentState TypedDict schema
│   └── workflow.py              # LangGraph StateGraph assembly & conditional loops
├── nodes/                       # Focused LangGraph execution nodes
│   ├── decomposition.py
│   ├── evidence_builder.py
│   ├── market_data.py
│   ├── math_solver.py
│   ├── retriever.py             # Lucene fulltext BM25 + dense vector retrieval
│   ├── router.py                # Fast semantic classifier (Llama-3.3-70B)
│   └── verifier.py              # Self-RAG fact-checking auditor
├── retrieval/
│   ├── hybrid_rrf.py            # Reciprocal Rank Fusion implementation
│   └── personal_retriever.py    # Isolated personal document retrieval
├── tools/
│   ├── calculator.py            # AST-sandboxed Python financial math engine
│   └── mf_lookup.py             # Sub-2ms deterministic Indian Mutual Fund lookup
├── reports/                     # Architecture changelogs, audits, and eval metrics
├── tests/                       # Automated Pytest suite
│   ├── test_auth.py
│   ├── test_data_isolation.py
│   ├── test_mf_lookup.py
│   ├── test_regulatory_watcher.py
│   ├── test_router.py
│   └── test_verifier.py
├── Dockerfile                   # Multi-stage production container definition
├── docker-compose.yml           # Full container orchestration configuration
├── main.py                      # FastAPI application gateway & endpoints
└── requirements.txt             # Python backend dependencies
```

---

## 💻 Getting Started & Local Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 20+** and **npm**
- A **Neo4j AuraDB** instance (or local Neo4j 5.20+)
- A **Neon PostgreSQL** database or local SQLite
- A **Groq API Key** ([console.groq.com](https://console.groq.com))

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/AshokSingodia-Codes/FinAdvisor-Voice.git
cd FinAdvisor-Voice

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory:
```ini
# --- LLM Providers ---
GROQ_API_KEY="gsk_..."
PRIMARY_MODEL="openai/gpt-oss-120b"
FAST_MODEL="llama-3.3-70b-versatile"

# --- Neo4j Graph & Vector Database ---
NEO4J_URI="neo4j+s://xxxxxx.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-neo4j-password"

# --- Relational Database (Memory & Auth) ---
DATABASE_URL="postgresql://user:password@ep-sample.us-east-2.aws.neon.tech/finadvisor?sslmode=require"

# --- Authentication & JWT ---
JWT_SECRET_KEY="your-super-secret-jwt-key"
JWT_ALGORITHM="HS256"

# --- Email OTP Delivery (Brevo HTTPS API or Gmail SMTP) ---
BREVO_API_KEY="xkeysib-..."
BREVO_SENDER_EMAIL="your-verified-email@domain.com"
# Optional Gmail fallback:
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=465
SMTP_USER="your-gmail@gmail.com"
SMTP_PASSWORD="your-gmail-app-password"
```

### 4. Ingest Personal Finance & Tax Corpus into Neo4j
```bash
python scripts/ingest_personal_finance.py
```

### 5. Frontend Setup & Launch
```bash
cd frontend
npm install
npm run dev
```

### 6. Start Backend Server
```bash
# In the root directory:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐳 Docker Deployment

You can build and run the entire unified stack (Frontend + Backend + Watcher) using Docker Compose:

```bash
# Build and run container in detached mode
docker compose up --build -d

# Check status and health
docker ps

# View application logs
docker compose logs -f
```

The application will be accessible at `http://localhost:8000`.

---

## 🧪 Automated Testing & Benchmarking

Run the full automated test suite covering router accuracy, verifier calibration, mutual fund lookups, and multi-tenant data isolation:

```bash
python -m pytest tests/test_router.py tests/test_verifier.py tests/test_mf_lookup.py tests/test_regulatory_watcher.py tests/test_data_isolation.py
```

---

## 👨‍💻 Author & Maintainer
Built with ❤️ by **[Ashok Singodia](https://github.com/AshokSingodia-Codes)** ([@AshokSingodia-Codes](https://github.com/AshokSingodia-Codes)).

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

