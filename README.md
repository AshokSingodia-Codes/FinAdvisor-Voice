# FinAdvisor-X: Agentic Hybrid Graph RAG Financial Intelligence Platform 📈🏛️

[![Live Frontend](https://img.shields.io/badge/Live_Frontend-Vercel-black.svg?logo=vercel&logoColor=white)](https://fin-advisor-voice.vercel.app/)
[![Live Backend](https://img.shields.io/badge/Live_API-Render-46E3B7.svg?logo=render&logoColor=white)](https://finadvisor-voice.onrender.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00.svg?logo=langchain&logoColor=white)](https://python.langchain.com/v0.1/docs/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_&_Vector-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Groq](https://img.shields.io/badge/Groq-LPU_Inference-F55036.svg)](https://groq.com/)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.3+-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 **Live Demo & API**:
> - 🖥️ **Web Application**: [https://fin-advisor-voice.vercel.app](https://fin-advisor-voice.vercel.app)
> - ⚙️ **Backend API (Swagger Docs)**: [https://finadvisor-voice.onrender.com/docs](https://finadvisor-voice.onrender.com/docs)
> - 📦 **GitHub Repository**: [AshokSingodia-Codes/FinAdvisor-Voice](https://github.com/AshokSingodia-Codes/FinAdvisor-Voice)

**FinAdvisor-X (v2.0)** is an enterprise-grade, state-of-the-art **Agentic Hybrid Graph Retrieval-Augmented Generation (RAG)** platform with **Isolated Multi-Turn Conversation Memory** and real-time financial intelligence.

FinAdvisor-X combines **Neo4j AuraDB** (Graph & Vector Store), **LangGraph** (Stateful Multi-Agent Orchestration), **FlashRank** (Local Cross-Encoder Reranking), **Groq LPU LLM inference** (with automatic multi-provider fallbacks), and a modern **React 19 + Vite** responsive dashboard. It reasons over SEC 10-K filings (Apple Inc. FY2024), a comprehensive Chartered Accountant (CA) finance knowledge base, classic investment literature, and real-time Yahoo Finance market feeds.

---

## 📑 Table of Contents

1. [Key Features](#-key-features)
2. [Architecture & System Flow](#-architecture--system-flow)
3. [Agentic LangGraph Nodes](#-agentic-langgraph-nodes)
4. [Knowledge Base & Data Sources](#-knowledge-base--data-sources)
5. [Project Structure](#-project-structure)
6. [Tech Stack](#-tech-stack)
7. [Getting Started & Local Setup](#-getting-started--local-setup)
   - [Prerequisites](#prerequisites)
   - [Backend Environment Setup](#1-backend-environment-setup)
   - [Environment Configuration (.env)](#2-environment-configuration-env)
   - [Neo4j Vector & Graph Ingestion](#3-neo4j-vector--graph-ingestion)
   - [Frontend Setup & Launch](#4-frontend-setup--launch)
8. [Running the Application](#-running-the-application)
9. [REST API Documentation](#-rest-api-documentation)
10. [Automated Testing & Evaluation](#-automated-testing--evaluation)
11. [Configuration Reference](#-configuration-reference)

---

## 🌟 Key Features

* **Hybrid Retrieval with Reciprocal Rank Fusion (RRF)**:
  Executes parallel queries against Neo4j Vector Index (`sentence-transformers/all-mpnet-base-v2` dense embeddings) and Lucene Full-Text Index (`keyword_markdown`), blending rank scores via configurable RRF (`k=60`).
* **FlashRank Neural Cross-Encoder Reranker**:
  Passes retrieved chunks through a lightweight, local, ultra-fast FlashRank model (`ms-marco-TinyBERT-L-2-v2`) to eliminate semantic drift before evidence synthesis.
* **Agentic StateGraph Routing & Problem Decomposition**:
  Semantic router dynamically dispatches queries to dedicated execution branches: multi-step sub-query decomposition, hybrid search, deterministic math calculations, live market data, or direct answers.
* **Self-RAG Verifier with Multi-Hop Reflection**:
  An autonomous auditing node checks draft responses against retrieved context for numerical precision, hallucinations, and source attribution. If facts or citations are missing, it autonomously loops back to retrieve targeted additional context (up to `MAX_RETRIEVAL_ITERATIONS`).
* **Deterministic Financial Math & Python REPL**:
  Extracts parameters and executes complex financial calculations—such as Discounted Cash Flow (DCF), Weighted Average Cost of Capital (WACC), Net Present Value (NPV), CAGR, SIP projections, and loan amortization—using verified Python execution tools rather than hallucination-prone LLM arithmetic.
* **Live Market Intelligence (`yfinance`)**:
  Fetches real-time market prices, P/E ratios, market caps, 52-week highs/lows, dividends, balance sheet metrics, and recent corporate news.
* **Modern React 19 + Vite Dashboard**:
  Fast, responsive dark-mode interface featuring real-time chat streaming, execution step indicators, syntax-highlighted Markdown and GFM tables, quick-start financial prompts, and recent query history.
* **Multi-LLM Fallback Resilience**:
  Primary high-speed inference on Groq (`openai/gpt-oss-120b` / `llama-3.3-70b-versatile`) with seamless cascade fallbacks to GitHub Models (`gpt-4o-mini`), OpenRouter, and Google Gemini (`gemini-2.5-flash`).

---

## 🏗️ Architecture & System Flow

```mermaid
graph TD;
    User([User Query]) --> UI[React 19 Vite Dashboard];
    UI -->|HTTP POST /api/chat| API[FastAPI Backend :8000];
    API --> StateGraph[LangGraph StateGraph];

    subgraph LangGraph Agentic Pipeline
        StateGraph --> Router{Semantic Router};
        
        Router -->|Complex / Multi-Hop| Decompose[Decomposition Node];
        Router -->|Tabular / Filing / Theory| Retriever[Hybrid Retriever];
        Router -->|Formula / Arithmetic| MathSolver[Math Solver & Python REPL];
        Router -->|Stocks / Tickers / Live| LiveData[Live Market Data Node];
        Router -->|General Knowledge| DirectAnswer[Evidence Builder];

        Decompose --> Retriever;
        
        subgraph Hybrid Search & Rerank
            Retriever --> Neo4jVec[(Neo4j Vector Search)]
            Retriever --> Neo4jKw[(Neo4j Keyword Search)]
            Neo4jVec --> RRF[Reciprocal Rank Fusion - RRF]
            Neo4jKw --> RRF
            RRF --> FlashRank[FlashRank Neural Reranker]
        end

        FlashRank --> Evidence[Evidence Builder];
        LiveData --> Evidence;
        MathSolver --> Verifier;
        Evidence --> Verifier{Self-RAG Verifier};

        Verifier -->|Audit Failed: Missing / Hallucinated| Retriever;
        Verifier -->|Audit Passed: Factual & Grounded| FinalState[Final Answer];
    end

    FinalState --> API;
    API -->|JSON {answer, intermediate_steps}| UI;
```

---

## 🤖 Agentic LangGraph Nodes

The core intelligence is decoupled into atomic, testable LangGraph nodes located in [`nodes/`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes):

| Node | File | Description |
| :--- | :--- | :--- |
| **`router`** | [`nodes/router.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/router.py) | Structured LLM classifier categorizing query intent into `decompose`, `hybrid_search`, `calculation`, `math_calculation`, `live_market_data`, or `direct_answer`. |
| **`decompose`** | [`nodes/decomposition.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/decomposition.py) | Splits complex multi-faceted questions into atomic sub-questions for parallel retrieval and synthesis. |
| **`retriever`** | [`nodes/retriever.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/retriever.py) | Coordinates dual vector and keyword queries in Neo4j, merges results with RRF, and applies FlashRank reranking. |
| **`math_solver`** | [`nodes/math_solver.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/math_solver.py) | Identifies variables, formulas, and exact numbers, delegating calculations to safe Python arithmetic solvers. |
| **`math_calculation`**| [`nodes/math_calculation.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/math_calculation.py)| High-precision financial formula solver (WACC, DCF, CAGR, loan schedules, annuity, bond yield). |
| **`live_data`** | [`nodes/market_data.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/market_data.py) | Integrates `yfinance` to query real-time equity quotes, analyst targets, balance sheet ratios, and market news. |
| **`evidence_builder`**| [`nodes/evidence_builder.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/evidence_builder.py)| Synthesizes retrieved chunks, market facts, and math outputs into a coherent, citation-backed draft response. |
| **`verifier`** | [`nodes/verifier.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/verifier.py) | The Self-RAG reflection gatekeeper. Evaluates the draft for factual consistency against evidence. If deficient, triggers a re-retrieval loop. |

---

## 📚 Knowledge Base & Data Sources

FinAdvisor-X is grounded on high-fidelity, multimodal financial corpora stored in Neo4j:

1. **Apple Inc. FY2024 Form 10-K (`NASDAQ_AAPL_2024.pdf`)**:
   Full annual report containing audited Consolidated Statements of Operations, Balance Sheets, Statements of Cash Flows, and Segment Disclosures. Tables are converted to structured markdown tables preserving row-column fidelity.
2. **Autonomous 19-Chapter Finance & CA Knowledge Base (`textbook`)**:
   AI-generated, domain-expert curriculum covering bookkeeping, GAAP/IFRS standards, valuation methods, derivatives pricing, working capital management, and forensic financial analysis.
3. **Investment Literature Reference Corpus**:
   - *A Random Walk Down Wall Street* by Burton G. Malkiel (890+ chunks).
   - *Personal Finance for Dummies* (1,300+ chunks).
4. **Live Financial Feeds**:
   Real-time pricing, valuation multiples, and historical prices via Yahoo Finance API.

---

## 📁 Project Structure

```text
Hybrid-Graph-RAG-Financial-Analyser/
├── Annual Report/               # Apple Inc. 2024 10-K report PDF
├── config/
│   ├── __init__.py
│   └── settings.py              # Pydantic BaseSettings loading .env configuration
├── core/
│   ├── __init__.py
│   └── db.py                    # Neo4jGraph, Neo4jVector, HuggingFace embeddings & LLM setup
├── data/                        # Investment reference PDFs (Malkiel, Personal Finance)
├── financial/
│   ├── __init__.py
│   └── parser.py                # FinancialTable & Evidence data schemas
├── frontend/                    # React 19 + TypeScript + Vite + Tailwind CSS Web App
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx              # Main interactive chat UI with financial dashboard
│       ├── App.css
│       ├── index.css            # Tailwind CSS styling tokens
│       └── main.tsx
├── graph/
│   ├── __init__.py
│   ├── state.py                 # AgentState TypedDict definition
│   └── workflow.py              # LangGraph StateGraph assembly and conditional edges
├── nodes/                       # Focused LangGraph execution nodes
│   ├── decomposition.py
│   ├── evidence_builder.py
│   ├── market_data.py
│   ├── math_calculation.py
│   ├── math_solver.py
│   ├── retriever.py
│   ├── router.py
│   └── verifier.py
├── retrieval/
│   ├── hybrid_rrf.py            # Reciprocal Rank Fusion (vector + keyword search)
│   └── reranker.py              # FlashRank neural reranking integration
├── tools/
│   └── calculator.py            # Financial formulas, DCF, WACC, CAGR, and Python REPL
├── scripts/
│   ├── generate_textbook.py     # Script to generate synthetic finance textbook
│   ├── generate_textbook_part2.py
│   ├── inspect_tables.py        # Utility to inspect extracted financial tables
│   └── simulate_conversation.py # Stress testing and conversation simulation runner
├── tests/                       # Pytest test suite
│   ├── conftest.py
│   ├── test_calculator.py
│   ├── test_calculator_extraction.py
│   ├── test_market_data.py
│   ├── test_math_solver.py
│   ├── test_router.py
│   └── test_workflow.py
├── check_db.py                  # Connectivity check and chunk counter for Neo4j
├── main.py                      # FastAPI backend application server (port 8000)
├── rebuild_vector_db.py         # 10-K PDF parsing & vector embedding ingestion
├── rebuild_textbook_db.py       # Textbook embedding ingestion into Neo4j
├── requirements.txt             # Python backend dependencies
└── README.md                    # Project documentation
```

---

## 🛠️ Tech Stack

- **Agent Orchestration**: [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/) & [LangChain Core](https://python.langchain.com/)
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic V2](https://docs.pydantic.dev/)
- **Frontend Dashboard**: [React 19](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vitejs.dev/), [Tailwind CSS v4](https://tailwindcss.com/), [Lucide React](https://lucide.dev/), [React-Markdown](https://github.com/remarkjs/react-markdown)
- **Knowledge Graph & Vector Store**: [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (Cypher, Graph traversal, Vector & Full-Text Lucene indexes)
- **Dense Embeddings**: HuggingFace `sentence-transformers/all-mpnet-base-v2` (768-dim embeddings)
- **Local Reranking**: [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) (`ms-marco-TinyBERT-L-2-v2`)
- **LLM Engine**: [Groq](https://groq.com/) (LPU high-speed inference) with dynamic fallbacks (GitHub Models, OpenRouter, Google Gemini)
- **Financial APIs & Tools**: `yfinance`, custom Python REPL with restricted math execution
- **Testing**: `pytest`, `pytest-asyncio`

---

## 💻 Getting Started & Local Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- A **Neo4j** instance (e.g., [Neo4j AuraDB Free](https://neo4j.com/cloud/aura/))
- A **Groq API Key** (free tier available at [console.groq.com](https://console.groq.com))

---

### 1. Backend Environment Setup

Create and activate a virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

---

### 2. Environment Configuration (`.env`)

Create a `.env` file in the root directory:

```env
# ==============================================================================
# Neo4j Database Settings
# ==============================================================================
AURA_INSTANCENAME="your-neo4j-instance-id"
NEO4J_URI="neo4j+s://<your-instance>.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-neo4j-password"

# ==============================================================================
# LLM Providers (Groq is Primary)
# ==============================================================================
GROQ_API_KEY="gsk_your_groq_api_key_here"
GROQ_MODEL="openai/gpt-oss-120b"   # or "llama-3.3-70b-versatile"

# Optional LLM Fallbacks:
GITHUB_API_KEY=""                  # GitHub PAT for Models API
OPENROUTER_API_KEY=""              # OpenRouter API Key
GOOGLE_API_KEY=""                  # Google Gemini API Key

# ==============================================================================
# RAG Configuration
# ==============================================================================
VECTOR_INDEX_NAME="vector_markdown"
KEYWORD_INDEX_NAME="keyword_markdown"
MAX_RETRIEVAL_ITERATIONS=3
RRF_K=60

# ==============================================================================
# Security & Observability (Optional)
# ==============================================================================
JWT_SECRET="super-secret-key-change-in-production"
LANGCHAIN_TRACING_V2="false"
```

Verify your Neo4j database connection at any time:

```bash
python check_db.py
```

---

### 3. Neo4j Vector & Graph Ingestion

If setting up a fresh Neo4j database, populate it using the built-in data pipeline scripts:

```bash
# 1. (Optional) Generate the 19-chapter finance textbook
python scripts/generate_textbook.py

# 2. Ingest the Apple 2024 10-K Annual Report into the Neo4j vector store
python rebuild_vector_db.py

# 3. Ingest the finance textbook into the Neo4j vector store
python rebuild_textbook_db.py
```

---

### 4. Frontend Setup & Launch

Navigate to the `frontend/` directory and install dependencies:

```bash
cd frontend
npm install
```

---

## 🚀 Running the Application

FinAdvisor-X runs as two coordinated services: the FastAPI backend and the React frontend.

### Option A: Run Both Simultaneously

**Terminal 1 — FastAPI Backend**:
```bash
# From the repository root with .venv active:
python main.py
# Backend runs on: http://localhost:8000
```

**Terminal 2 — React Frontend**:
```bash
# From the repository root:
cd frontend
npm run dev
# Frontend runs on: http://localhost:5173
```

Open your browser and navigate to **`http://localhost:5173`** to access the FinAdvisor-X platform.

---

## 📡 REST API Documentation

The FastAPI backend exposes the following endpoints on `http://localhost:8000`:

### `GET /`
Health check endpoint.
- **Response**: `{"status": "FinAdvisor-X API is running"}`

---

### `POST /api/chat`
Execute a query through the LangGraph agent pipeline.

#### Request Body
```json
{
  "message": "What were Apple's total net sales in FY2024, and what is its current stock price?",
  "chat_history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I assist you with financial analysis today?"
    }
  ]
}
```

#### Response Body
```json
{
  "answer": "According to Apple Inc.'s 2024 Form 10-K, total net sales for fiscal year 2024 were $391,035 million (approximately $391.04 billion), an increase from $383,285 million in 2023.\n\nRegarding live market data, Apple Inc. (AAPL) is currently trading at approximately $237.40 with a market capitalization of ~$3.60 trillion.",
  "intermediate_steps": [
    "router",
    "decompose",
    "retriever",
    "live_data",
    "evidence_builder",
    "verifier"
  ]
}
```

---

## 🧪 Automated Testing & Evaluation

FinAdvisor-X includes comprehensive automated tests covering the routing logic, mathematical tools, market data fetching, and workflow compilation:

### Run the Pytest Suite

```bash
# Run all unit and integration tests
pytest tests/ -v

# Run a specific test module
pytest tests/test_router.py -v
pytest tests/test_calculator.py -v
pytest tests/test_market_data.py -v
pytest tests/test_workflow.py -v
```

### Run Conversation & Hallucination Simulations

To benchmark retrieval accuracy, hallucination rates, and node routing under stress conditions:

```bash
python scripts/simulate_conversation.py
```
Outputs and performance traces are automatically saved to the [`reports/`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/reports) directory.

---

## ⚙️ Configuration Reference

All settings can be customized in [`config/settings.py`](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/config/settings.py) or overridden via `.env`:

| Setting | Default | Description |
| :--- | :--- | :--- |
| `NEO4J_URI` | *Required* | Bolt/Neo4j+s connection URI |
| `NEO4J_USERNAME` | *Required* | Neo4j database username |
| `NEO4J_PASSWORD` | *Required* | Neo4j database password |
| `GROQ_API_KEY` | *Required* | Groq API Key for primary LPU inference |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Model used for router, evidence, and verifier |
| `VECTOR_INDEX_NAME` | `vector_markdown` | Name of the Neo4j dense vector index |
| `KEYWORD_INDEX_NAME`| `keyword_markdown`| Name of the Neo4j Lucene full-text index |
| `MAX_RETRIEVAL_ITERATIONS` | `3` | Maximum Self-RAG loop attempts upon verification failure |
| `RRF_K` | `60` | Rank constant for Reciprocal Rank Fusion blending |
| `JWT_SECRET` | `default_insecure...` | Secret key for future JWT auth token signing |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
