# 🚀 FinAdvisor-X: Master Project Handover & System Architecture Map

> **Date:** September 24, 2026  
> **Project Name:** FinAdvisor-X (Agentic Hybrid Graph-RAG Financial Intelligence Platform)  
> **Repository:** `AshokSingodia-Codes/FinAdvisor-Voice`  
> **Workspace Root:** `e:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main`

---

## 📌 Executive Summary
FinAdvisor-X is a multi-agent, hybrid Graph-RAG financial advisory platform. It combines:
1. **Neo4j Knowledge Graph & Vector Store** (AuraDB cloud instance) for structured financial entity traversal and vector search.
2. **Neon PostgreSQL Cloud Database** for user authentication (JWT + bcrypt), conversation history, structured financial memory facts, and document metadata.
3. **LangGraph State Graph** with dynamic routing, multi-step financial planning, mathematical verification, web search fallback, and self-RAG answer validation.
4. **FlashRank Neural Cross-Encoder Reranker** for Context-Bounded Top-$K$ retrieval.
5. **Lossless Markdown & Tabular Token Compressor** + **Metadata Manifest Extraction** for $<50$-token conversational routing.
6. **Modern React (Vite + TypeScript) Frontend** with One-Click Copy, Web Speech TTS Voice synthesis, and interactive follow-up Action Chips.

---

## 🗺️ Comprehensive File-to-Task Directory Map

| File / Path | Primary Task & Architectural Responsibility |
|---|---|
| **`main.py`** | **FastAPI Server & Core API Routing**:<br>• Compiles and executes LangGraph workflow.<br>• Manages JWT Auth endpoints (`/api/auth/register`, `/api/auth/login`, OTP flows).<br>• Manages conversation endpoints (`/api/conversations/*`).<br>• Manages document upload (`/api/documents/upload`) and streaming/chat (`/api/chat`).<br>• Enforces per-user rate limiting and session-level active document binding. |
| **`config/settings.py`** | **Central Settings & Environment Variables**:<br>• Loads `.env` configuration (Neo4j, Groq, OpenRouter, Google, Neon Postgres, Brevo SMTP).<br>• Configures token limits, RRF constants ($k=60$), and JWT secret resolution. |
| **`core/db.py`** | **Database & LLM Model Connection Gateway**:<br>• Neo4j Graph & Vector Index connections.<br>• Dual-tier LLM setup: Tier 1 (`openai/gpt-oss-20b`) for ultra-fast high-RPM routing & Tier 2 (`openai/gpt-oss-120b`) for deep synthesis.<br>• Embeddings integration (`FastEmbedWrapper` with `bge-small-en-v1.5`). |
| **`core/memory.py`** | **PostgreSQL Storage, Memory & Security Engine**:<br>• Direct SQLAlchemy engine with `pool_pre_ping=True` and connection pooling.<br>• Tables: `users`, `conversations`, `messages`, `memory_facts`, `otp_verifications`, `user_documents`.<br>• Fast in-memory caching (`_USER_CACHE`, `_CONV_CACHE`) for low database latency.<br>• Extracts and persists user financial profile facts (SIP, income, expenses, goals). |
| **`core/auth.py`** | **Authentication, Security & OTP Service**:<br>• Bcrypt password hashing & verification.<br>• Cryptographic 6-digit OTP generation with SHA-256 salted hashing.<br>• JWT encoding/decoding and FastAPI Bearer security dependency (`get_current_user`).<br>• Brevo HTTPS API and SMTP fallback email delivery. |
| **`core/document_store.py`** | **Document Lifecycle & Token Optimization Engine**:<br>• PDF, CSV, TXT, MD, and Image (receipt/statement) text & table extraction (`pdfplumber` + markdown formatter).<br>• **Domain Gatekeeper**: Rejects non-financial documents.<br>• **Lossless Compressor** (`compress_financial_text`): Strips whitespace padding (~35% token savings).<br>• **Metadata Manifest Extractor** (`extract_statement_manifest`): Extracts `<50` token headers.<br>• Ingests chunk embeddings into Neo4j as isolated `PersonalChunk` nodes with 3-field security (`user_id`, `document_id`, `conversation_id`). |
| **`core/rate_limiter.py`** | **Sliding-Window Rate Limiter**:<br>• Enforces strict per-user RPM/TPM limits to prevent API abuse and 429 quota exhaustion. |
| **`core/cache.py`** | **Semantic & Exact Query Cache**:<br>• In-memory cache for repeated financial queries, document sessions, and common calculations. |
| **`graph/state.py`** | **LangGraph State Schema Definition**:<br>• `AgentState` containing question, memory context, retrieved context, routing decisions, tool outputs, drafts, verification flags, and isolation keys. |
| **`graph/workflow.py`** | **Agentic Graph Workflow Definition**:<br>• Directed Acyclic Graph connecting router, retriever, evidence builder, math solver, web searcher, verifier, and feedback loops. |
| **`nodes/router.py`** | **Dynamic Semantic Query Router**:<br>• Classifies user query into `direct_answer`, `rag_retrieval`, `calculation`, or `web_search`. |
| **`nodes/retriever.py`** | **Context-Bounded Retrieval Orchestrator**:<br>• Dispatches shared vs personal document retrieval.<br>• Integrates **FlashRank Neural Cross-Encoder** (`ms-marco-MiniLM-L-12-v2`) to dynamically select the Top 3–5 most relevant chunks. |
| **`nodes/evidence_builder.py`** | **Evidence Synthesis & Safe Bounding Node**:<br>• AI Financial Assistant persona (Strict non-certified CFP/RIA educational disclaimer rules).<br>• Deduplicates identical chunks and enforces **$<1,800$ token context limit** with newline-boundary safe truncation.<br>• Generates interactive bracketed action chips (`[Suggested Action]`). |
| **`nodes/math_solver.py`** | **Deterministic Financial Math Solver**:<br>• Generates and executes Python formulas for compound interest, SIP future value, loan EMIs, and tax calculations without LLM arithmetic hallucinations. |
| **`nodes/web_searcher.py`** | **Live Market & Regulatory Web Search**:<br>• Live Tavily / Finnhub search fallback for recent stock quotes, interest rate updates, or breaking market news. |
| **`nodes/verifier.py`** | **Self-RAG Hallucination & Fact Checker**:<br>• Validates synthesized answers against reference documents and calculations before sending to user. |
| **`retrieval/hybrid_rrf.py`** | **Reciprocal Rank Fusion (RRF)**:<br>• Fuses dense vector search and sparse keyword BM25 search rankings ($k=60$). |
| **`retrieval/personal_retriever.py`** | **Isolated Personal Document Search**:<br>• Executes vector and keyword search over Neo4j `PersonalChunk` nodes strictly isolated by `(user_id, document_id, conversation_id)`. |
| **`retrieval/reranker.py`** | **FlashRank Cross-Encoder Module**:<br>• Neural reranker (`ms-marco-MiniLM-L-12-v2`) scoring passage relevance with local ONNX acceleration. |
| **`frontend/src/App.tsx`** | **React Frontend UI Application**:<br>• Glassmorphic dark financial intelligence interface.<br>• Document upload drag-and-drop with progress states.<br>• **Interactive Action Chips**: Renders `[Suggested Action]` badges as clickable prompt pills.<br>• **One-Click Copy Button** on assistant messages.<br>• **Web Speech TTS Voice Playback** button (`🔊 Listen` / `⏹️ Stop`). |
| **`frontend/src/index.css`** | **Design System & Styling**:<br>• Polished CSS tokens, animations, custom scrollbars, and glassmorphic cards. |
| **`Dockerfile` & `docker-compose.yml`** | **Containerization & Deployment**:<br>• Multi-stage build with `libgomp1` (ONNX/FastEmbed), health checks, and log rotation. |
| **`scratch/test_suite.py`** | **Automated 8-Module End-to-End Test Suite**:<br>• Tests compressor, manifest extraction, domain guard, FlashRank, evidence builder, live backend chat, compliance disclaimer, and personal doc upload reasoning. |

---

## 🔒 Security & Privacy Model
1. **Three-Tier Document Isolation:**
   - Every uploaded document chunk stored in Neo4j contains `user_id`, `document_id`, and `conversation_id`.
   - Cross-user and cross-conversation leakage is mathematically impossible at the Cypher query level.
2. **AI Identity Compliance:**
   - The assistant explicitly identifies as **FinAdvisor-X AI Assistant**, never falsely claiming to be a human CFP or SEBI-registered RIA.
3. **Data Protection:**
   - Passwords hashed with `bcrypt`.
   - OTP codes hashed with `SHA-256` + secret salt.
   - Non-financial files are instantly rejected by the domain classifier.

---

## ⚡ How to Resume Tomorrow (Step-by-Step)

### 1. Start the Backend API Server
In PowerShell / terminal:
```powershell
# Navigate to workspace root
cd e:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main

# Run backend with uvicorn
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
- API Swagger Documentation will be live at: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend UI Server
In a second PowerShell / terminal:
```powershell
cd e:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main\frontend
npm run dev
```
- UI will be live at: `http://localhost:5173`

### 3. Run the Automated Verification Suite
```powershell
python scratch/test_suite.py
```

---

## 💡 Notes on LLM API Quotas
- **Groq Free Tier (On-Demand):** Has a 200,000 tokens-per-day rolling limit on the user key. It resets continuously every rolling minute.
- **Configured Models in `core/db.py`:**
  - `openai/gpt-oss-120b` (Deep advisory reasoning)
  - `openai/gpt-oss-20b` (Ultra-low token fast routing & decomposer)
  - Multi-tier fallback cascades prevent 500 errors if quota thresholds are reached.
