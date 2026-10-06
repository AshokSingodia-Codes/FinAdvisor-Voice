# 🏗️ 02 — High-Level Architecture & Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                           │
│  React 19 + TypeScript + Vite + TailwindCSS                     │
│  ┌──────────┐  ┌─────────────┐  ┌─────────────────────────┐    │
│  │LoginPage │  │ ChatUI/App  │  │ ConversationSidebar      │    │
│  │AuthModal │  │ (App.tsx)   │  │ VoiceInputButton         │    │
│  └──────────┘  └─────────────┘  └─────────────────────────┘    │
│          │            │  ▲                                       │
│          │  HTTP/SSE  │  │ JSON / Event Stream                   │
└──────────┼────────────┼──┼───────────────────────────────────────┘
           │            │  │
           ▼            ▼  │
┌──────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND (main.py)                    │
│                                                                  │
│  Middleware Stack:                                               │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ CORS → Rate Limiter → JWT Auth Guard                 │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  API Endpoints:                                                  │
│  POST /api/auth/send-otp    POST /api/auth/verify-otp           │
│  POST /api/auth/register    POST /api/auth/login                 │
│  POST /api/chat             GET /api/conversations               │
│  POST /api/documents/upload DELETE /api/documents/{id}           │
│  GET /api/health                                                 │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐        │
│  │            LANGGRAPH AI AGENT (graph/workflow.py)   │        │
│  │                                                     │        │
│  │  [router] → [decompose] → [retriever]               │        │
│  │      ↓            ↓           ↓                     │        │
│  │  [math_solver] [live_data] [evidence_builder]       │        │
│  │  [math_calc]  [news_node]      ↓                    │        │
│  │                           [verifier] → END          │        │
│  │                               ↑ (retry loop)        │        │
│  └─────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────┘
           │                 │                    │
           ▼                 ▼                    ▼
┌───────────────┐  ┌──────────────────┐  ┌───────────────────┐
│  NEO4J AURA   │  │   NEON POSTGRES   │  │  EXTERNAL APIs    │
│  (Graph DB)   │  │   (Relational DB) │  │                   │
│               │  │                  │  │  Groq LLM         │
│  - Financial  │  │  - Users         │  │  OpenRouter LLM   │
│    knowledge  │  │  - Conversations │  │  Google Gemini    │
│    graph      │  │  - Messages      │  │  yfinance         │
│  - Vector     │  │  - OTP records   │  │  News API         │
│    index      │  │  - Documents     │  │  Brevo Email      │
│  - Personal   │  │    (metadata)    │  │  LangSmith        │
│    chunks     │  │                  │  │                   │
└───────────────┘  └──────────────────┘  └───────────────────┘
```

---

## LangGraph Agent State Machine

```mermaid
flowchart TD
    START([User Query]) --> ROUTER[🔀 Router Node\nClassifies query type]

    ROUTER -->|hybrid_search\nfinancial_table| RETRIEVER[🔍 Retriever Node\nHybrid RRF Search]
    ROUTER -->|decompose| DECOMPOSE[🧩 Decompose Node\nBreak complex query]
    ROUTER -->|calculation| MATH_SOLVER[🧮 Math Solver\nFormula-based math]
    ROUTER -->|math_calculation| MATH_CALC[➕ Math Calculation\nArithmetic eval]
    ROUTER -->|live_market_data| LIVE_DATA[📈 Live Data Node\nyfinance API]
    ROUTER -->|current_events| NEWS[📰 News Node\nNews API]
    ROUTER -->|direct_answer| EVIDENCE[📝 Evidence Builder\nLLM Synthesis]

    DECOMPOSE --> RETRIEVER
    RETRIEVER --> EVIDENCE
    LIVE_DATA --> EVIDENCE
    NEWS --> EVIDENCE

    EVIDENCE --> VERIFIER[✅ Verifier Node\nQuality Check]
    MATH_SOLVER --> VERIFIER
    MATH_CALC --> VERIFIER

    VERIFIER -->|passed or max retries| END([Final Answer])
    VERIFIER -->|failed, retry < 1| RETRIEVER
```

---

## Retrieval Architecture (Hybrid RRF)

```mermaid
flowchart LR
    QUERY[User Query] --> EMBED[FastEmbed\nBAAI/bge-small-en-v1.5\nONNX embedding]

    EMBED --> VEC[Neo4j Vector Index\nSemantic similarity search\nTop-K chunks]
    QUERY --> GRAPH[Neo4j Graph Traversal\nKeyword + entity search\nCypher queries]

    VEC --> RRF[⚡ RRF Fusion\n1 / k+rank formula\nk=60]
    GRAPH --> RRF

    RRF --> RERANK[FlashRank Reranker\nCross-encoder scoring]
    RERANK --> CONTEXT[Top N chunks\nfor LLM prompt]
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant FastAPI
    participant PostgreSQL
    participant Brevo_Email

    User->>Frontend: Enter email to register
    Frontend->>FastAPI: POST /api/auth/send-otp {email, purpose:"register"}
    FastAPI->>PostgreSQL: Check if email exists
    FastAPI->>FastAPI: generate_otp() → 6-digit code
    FastAPI->>FastAPI: hash_otp() → SHA256 hash
    FastAPI->>PostgreSQL: Save hashed OTP + expiry (5 min)
    FastAPI->>Brevo_Email: Send OTP email
    FastAPI-->>Frontend: {status: "success"}

    User->>Frontend: Enter OTP code
    Frontend->>FastAPI: POST /api/auth/verify-otp {email, otp}
    FastAPI->>PostgreSQL: Fetch OTP record, verify hash
    FastAPI->>FastAPI: generate_verification_token()
    FastAPI-->>Frontend: {verification_token: "xyz..."}

    User->>Frontend: Enter password
    Frontend->>FastAPI: POST /api/auth/register {email, password, verification_token}
    FastAPI->>FastAPI: consume_verification_token() → validate
    FastAPI->>FastAPI: hash_password() → bcrypt
    FastAPI->>PostgreSQL: INSERT user record
    FastAPI->>FastAPI: create_access_token() → JWT
    FastAPI-->>Frontend: {access_token: "eyJ..."}

    User->>Frontend: Now authenticated!
```

---

## Chat Request Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant FastAPI
    participant LangGraph
    participant Neo4j
    participant Groq_LLM
    participant PostgreSQL

    User->>Frontend: Type "What was TCS revenue FY24?"
    Frontend->>FastAPI: POST /api/chat {message, conversation_id, JWT}

    FastAPI->>FastAPI: JWT validation (get_current_user)
    FastAPI->>FastAPI: Rate limit check
    FastAPI->>FastAPI: Cache check (miss → proceed)
    FastAPI->>PostgreSQL: Get conversation memory/history

    FastAPI->>LangGraph: invoke(AgentState{question, history})

    LangGraph->>Groq_LLM: Router: classify query type
    Groq_LLM-->>LangGraph: "hybrid_search"

    LangGraph->>Neo4j: Vector search (top-10 semantic chunks)
    LangGraph->>Neo4j: Graph search (entity traversal)
    LangGraph->>LangGraph: RRF Fusion → ranked chunks

    LangGraph->>Groq_LLM: Evidence Builder: synthesize answer from chunks
    Groq_LLM-->>LangGraph: Draft answer

    LangGraph->>Groq_LLM: Verifier: is this answer correct?
    Groq_LLM-->>LangGraph: "verified"

    LangGraph-->>FastAPI: {final_answer: "TCS revenue was ₹2.41 lakh crore..."}

    FastAPI->>PostgreSQL: Save message + answer
    FastAPI->>FastAPI: Update response cache
    FastAPI-->>Frontend: Stream answer tokens

    Frontend->>User: Renders Markdown answer
```

---

## Database Schema (PostgreSQL — Neon)

```mermaid
erDiagram
    USERS {
        text id PK
        text email UK
        text password_hash
        timestamp created_at
    }

    OTP_RECORDS {
        int id PK
        text email
        text otp_hash
        text purpose
        text expires_at
        bool claimed
        text verification_token
        timestamp created_at
    }

    CONVERSATIONS {
        text id PK
        text user_id FK
        text title
        timestamp created_at
        timestamp updated_at
    }

    MESSAGES {
        int id PK
        text conversation_id FK
        text role
        text content
        timestamp created_at
    }

    USER_DOCUMENTS {
        text id PK
        text user_id FK
        text conversation_id FK
        text filename
        text content_hash
        text status
        int chunk_count
        timestamp created_at
    }

    USERS ||--o{ CONVERSATIONS : "has"
    CONVERSATIONS ||--o{ MESSAGES : "contains"
    USERS ||--o{ USER_DOCUMENTS : "uploads"
    CONVERSATIONS ||--o{ USER_DOCUMENTS : "has"
```

---

## Neo4j Graph Schema

```
Shared Corpus (Financial Knowledge Base):
  (Chunk {id, content, embedding[]})
    ← stored in vector index "vector_markdown"
    ← stored in keyword index "keyword_markdown"

Personal Documents (User Uploads):
  (PersonalChunk {
      user_id,          ← security isolation
      document_id,      ← document isolation
      conversation_id,  ← conversation isolation
      content,
      embedding[]
  })
```

---

## LLM Dual-Tier Architecture

```
Fast Chain (< 500ms)          Synthesis Chain (< 5s)
─────────────────────         ──────────────────────────
Used for:                     Used for:
  Router classification         Evidence Builder
  Decomposer                    Complex synthesis
  Verifier                      Full answer generation

Models (priority order):      Models (priority order):
  1. Groq gpt-oss-20b           1. Groq gpt-oss-120b
  2. Groq Qwen-3.8-27B          2. Groq gpt-oss-20b
  3. OpenRouter Mistral-24B     3. OpenRouter Qwen-72B
  4. Google Gemini Flash         4. Google Gemini Flash

Each tier uses .with_fallbacks() — if primary fails,
automatically tries next in chain. Zero manual retry code needed.
```

---

## Component Interaction Map

```
config/settings.py          ← ALL modules read from here
        │
        ▼
core/db.py                  ← Creates LLM chains + embeddings + Neo4j connection
        │
        ├──► nodes/router.py
        ├──► nodes/retriever.py
        ├──► nodes/evidence_builder.py
        ├──► nodes/verifier.py
        ├──► nodes/math_solver.py
        ├──► nodes/math_calculation.py
        ├──► nodes/market_data.py
        └──► nodes/news_data.py
                │
                ▼
        graph/state.py      ← Defines AgentState TypedDict
        graph/workflow.py   ← Wires nodes into LangGraph
                │
                ▼
        main.py             ← FastAPI endpoints invoke workflow
                │
        ┌───────┤
        │       │
        ▼       ▼
core/memory.py  core/auth.py
(PostgreSQL)    (JWT+OTP)
```
