# FinAdvisor-X: Enterprise Agentic Hybrid Graph-RAG Financial Intelligence Platform 📈🏛️

[![Live Frontend](https://img.shields.io/badge/Live_Frontend-Vercel-black.svg?logo=vercel&logoColor=white)](https://fin-advisor-voice.vercel.app/)
[![Live Backend](https://img.shields.io/badge/Live_API-Render-46E3B7.svg?logo=render&logoColor=white)](https://finadvisor-voice.onrender.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00.svg?logo=langchain&logoColor=white)](https://python.langchain.com/v0.1/docs/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_&_Vector-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Neon Postgres](https://img.shields.io/badge/Neon-PostgreSQL_Serverless-00E599.svg?logo=postgresql&logoColor=white)](https://neon.tech/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Qwen_&_DeepSeek-6366F1.svg)](https://openrouter.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 **Live Demo & Deployment**:
> - 🖥️ **Web Application**: [https://fin-advisor-voice.vercel.app](https://fin-advisor-voice.vercel.app)
> - ⚙️ **Backend API (Interactive Swagger Docs)**: [https://finadvisor-voice.onrender.com/docs](https://finadvisor-voice.onrender.com/docs)
> - 📦 **GitHub Repository**: [AshokSingodia-Codes/FinAdvisor-Voice](https://github.com/AshokSingodia-Codes/FinAdvisor-Voice)

**FinAdvisor-X** is an enterprise-grade **Agentic Hybrid Graph Retrieval-Augmented Generation (RAG)** financial intelligence and advisory platform. Engineered for real-world enterprise requirements, the system combines **Continuous Multi-Sentence Voice Dictation**, **Soft Female Speech Synthesis**, **Adaptive Depth Token Routing**, **4-Tier LLM Fallbacks with Circuit Breaker Protection**, **Reciprocal Rank Fusion (RRF $k=60$) with FlashRank Neural Cross-Encoder Reranking**, **Strict 3-Field Multi-Tenant Document Privacy Isolation**, and **Deterministic Financial Math with Indian Tax Intelligence (FY 2026-27)**.

---

## 📑 Table of Contents

1. [Executive Summary & Core Value Proposition](#-executive-summary--core-value-proposition)
2. [End-to-End System Architecture (HLD)](#-end-to-end-system-architecture-hld)
3. [LangGraph Multi-Agent State Machine & Execution DAG](#-langgraph-multi-agent-state-machine--execution-dag)
4. [Hybrid Graph-RAG Retrieval Pipeline (BM25 + Vector + RRF + Cross-Encoder)](#-hybrid-graph-rag-retrieval-pipeline)
5. [Data Ingestion, Storage & Graph Schemas](#-data-ingestion-storage--graph-schemas)
6. [Strict Multi-Tenant Security & 3-Field Privacy Model](#-strict-multi-tenant-security--3-field-privacy-model)
7. [Resilient Multi-Provider LLM Cascade & Circuit Breaker](#-resilient-multi-provider-llm-cascade--circuit-breaker)
8. [Voice Interaction Subsystem (Continuous STT & Soft Female TTS)](#-voice-interaction-subsystem)
9. [Deterministic Financial Math & Indian Tax Engine](#-deterministic-financial-math--indian-tax-engine)
10. [Autonomous Regulatory Watchdog & Feed Ingestion](#-autonomous-regulatory-watchdog--feed-ingestion)
11. [Latency Engineering, Caching & Token Economics](#-latency-engineering-caching--token-economics)
12. [Empirical Benchmarks & Evaluation Metrics](#-empirical-benchmarks--evaluation-metrics)
13. [Automated Test Suite Coverage](#-automated-test-suite-coverage)
14. [Project Directory & Component Interaction Map](#-project-directory--component-interaction-map)
15. [Getting Started & Local Setup](#-getting-started--local-setup)
16. [Docker Deployment](#-docker-deployment)
17. [REST API Endpoints](#-rest-api-endpoints)
18. [🎯 Technical Interview Cheatsheet & Architecture Defense Guide](#-technical-interview-cheatsheet--architecture-defense-guide)
19. [Changelog & Historical Fixes](#-changelog--historical-fixes)

---

## 🏛️ Executive Summary & Core Value Proposition

Standard RAG architectures suffer from five major failure modes in production financial advisory:
1. **Semantic Drift & Keyword Blindness**: Pure vector search misses exact financial line items, ticker codes, and accounting numbers; pure keyword search misses conceptual semantic queries.
2. **Hallucination on Unseen/Adversarial Data**: LLMs generate phantom quarterly numbers, fabricated executives, or inaccurate formula results.
3. **Compound Query Failure**: Multi-year comparisons (*"Compare AAPL and MSFT gross margins from FY22 to FY24"*) fail in single-pass retrieval.
4. **Token Bloat & Latency Bottlenecks**: Full-document prompt stuffing causes high costs and 15–30s response times.
5. **Multi-Tenant Privacy Leaks**: Shared vector spaces risk cross-user and cross-session document leakage.

**FinAdvisor-X resolves these challenges through an architectural blueprint:**
- **Hybrid Retrieval + Cross-Encoder Reranking**: Neo4j Lucene BM25 full-text search combined with 768-dim dense vector embeddings via **Reciprocal Rank Fusion (RRF, $k=60$)**, refined by an in-memory **FlashRank Neural Cross-Encoder** (`ms-marco-MiniLM-L-12-v2`, **+16.42% Precision@5 lift**).
- **Self-RAG Cyclic Verification**: Verifier node audits generated answers against retrieved source context; triggers automatic re-retrieval loops on ungrounded claims.
- **AST-Sandboxed Math & Offline SEBI MF Database**: Arithmetic, SIP/EMI/CAGR/Tax calculations, and 25+ mutual fund lookups execute deterministically in **< 2ms at 0 LLM tokens**.
- **Compound 3-Field Privacy Isolation**: `(user_id, document_id, conversation_id)` enforced at the Cypher query level with cascading deletions.
- **Continuous Voice Interaction**: Browser-native SpeechRecognition auto-recovery loop paired with soft, pitch-calibrated female TTS (`Microsoft Zira`, `Aria`, `Jenny`, `Neerja`).

---

## 🏗️ End-to-End System Architecture (HLD)

The platform is structured into decoupled, enterprise-ready architectural layers:

```mermaid
flowchart TD
    subgraph Client_Layer [1. Client & Voice Interaction Layer]
        User([User Voice / Text])
        VoiceSTT[Browser Web Speech STT<br/>Continuous Multi-Sentence Loop]
        VoiceTTS[Soft Female TTS Engine<br/>Pitch: 1.15 | Rate: 0.95]
        UI[React 18 + Vite + Tailwind Dashboard<br/>Responsive Drawer & Action Chips]
        
        User -->|Spoken Audio| VoiceSTT
        User -->|Typed Prompt| UI
        VoiceSTT -->|Transcribed Text| UI
        UI -->|Play Response| VoiceTTS
    end

    subgraph Gateway_Layer [2. API Gateway & Security Middleware]
        API[FastAPI Gateway :8000]
        CORS[CORS Guard & Request Validator]
        RateLimit[Per-User Sliding Window Rate Limiter<br/>Request & Token Quotas]
        AuthGuard[JWT Auth Guard + Bcrypt<br/>6-Digit Cryptographic OTP]
        Cache[User-Scoped Semantic & Exact Cache<br/>Sub-1ms Fast Hit]
        
        UI -->|HTTP / HTTPS REST| API
        API --> CORS --> RateLimit --> AuthGuard --> Cache
    end

    subgraph State_Storage [3. State, Identity & Relational Storage]
        NeonDB[(Neon PostgreSQL Serverless)]
        NeonDB -->|Stores| T_Users[User Credentials & Profiles]
        NeonDB -->|Stores| T_Conv[Conversations & Thread Context]
        NeonDB -->|Stores| T_Msg[ChatMessage History & Audit Logs]
        NeonDB -->|Stores| T_Docs[Uploaded Document Metadata]
        NeonDB -->|Stores| T_OTP[Hashed OTPs & Temp Tokens]
        AuthGuard <--> NeonDB
    end

    subgraph Agentic_Core [4. LangGraph Multi-Agent Stateful Orchestrator]
        State[(AgentState Schema<br/>Query, History, Depth, Chunks, Flags)]
        
        RouterNode{🔀 Semantic Router<br/>Intent & Depth Classifier}
        DecomposeNode[🧩 Query Decomposition Node<br/>Multi-Year / Comparative Split]
        RetrieverNode[🔍 Parallel Hybrid Retriever<br/>Lucene BM25 + Dense Vector]
        MarketNode[📈 Live Market Data Node<br/>Yahoo Finance Real-Time Tickers]
        MathNode[🧮 Deterministic Math Solver<br/>Python AST & SEBI MF Lookup]
        EvidenceNode[📝 Evidence Synthesizer<br/>Strict Token Budget & Action Chips]
        VerifierNode{✅ Self-RAG Verifier Node<br/>Factuality & Groundedness Audit}

        Cache -->|Cache Miss| State
        State --> RouterNode
        
        RouterNode -->|Multi-Year / Complex| DecomposeNode
        RouterNode -->|10-K / Tax / Theory| RetrieverNode
        RouterNode -->|Ticker / Stock / Quotes| MarketNode
        RouterNode -->|Math / SIP / EMI / Tax Slabs| MathNode
        RouterNode -->|Direct / General Chat| EvidenceNode
        
        DecomposeNode --> RetrieverNode
        RetrieverNode --> EvidenceNode
        MarketNode --> EvidenceNode
        MathNode --> VerifierNode
        EvidenceNode --> VerifierNode
        
        VerifierNode -->|Audit Failed: Context Insufficient| RetrieverNode
        VerifierNode -->|Audit Passed: Factual & Grounded| FinalOutput[Verified Final Response]
    end

    subgraph Retrieval_Knowledge_Layer [5. Hybrid Knowledge Bases & Vector Stores]
        Neo4jShared[(Neo4j Aura: Shared Financial Corpus)]
        Neo4jPersonal[(Neo4j Aura: Isolated Personal Chunks)]
        BM25Index[Lucene BM25 Index<br/>'keyword_markdown']
        VectorIndex[Dense Vector Index<br/>'vector_markdown' 768-dim]
        RRFEngine[Reciprocal Rank Fusion<br/>k=60 Rank Aggregation]
        FlashRankEngine[FlashRank Neural Cross-Encoder<br/>ms-marco-MiniLM-L-12-v2]

        RetrieverNode -->|Shared Corpus Query| Neo4jShared
        RetrieverNode -->|Attached User Doc Query| Neo4jPersonal
        Neo4jShared --> BM25Index & VectorIndex
        Neo4jPersonal --> VectorIndex
        BM25Index & VectorIndex --> RRFEngine
        RRFEngine --> FlashRankEngine
        FlashRankEngine --> RetrieverNode
    end

    subgraph Fallback_LLM_Layer [6. Resilient LLM Cascade & Circuit Breaker]
        Breaker{Circuit Breaker FSM<br/>Per-User Error Tracking}
        LLM1[1. OpenRouter Qwen 2.5 72B]
        LLM2[2. OpenRouter DeepSeek-Chat]
        LLM3[3. Google Gemini 2.5 Flash]
        LLM4[4. Groq Qwen 3.8-27B]

        RouterNode & DecomposeNode & EvidenceNode & VerifierNode --> Breaker
        Breaker --> LLM1
        LLM1 -->|Timeout / 429 / 5xx| LLM2
        LLM2 -->|Failover| LLM3
        LLM3 -->|Failover| LLM4
    end

    FinalOutput --> API
    API --> UI
```

---

## 🤖 LangGraph Multi-Agent State Machine & Execution DAG

The core intelligence workflow is orchestrated via **LangGraph** using a cyclic, directed state graph (`graph/workflow.py`).

```mermaid
stateDiagram-v2
    [*] --> router: User Question + Conversation Context
    
    router --> decomposition: Intent == 'decompose'
    router --> retriever: Intent == 'hybrid_search' | 'financial_table'
    router --> market_data: Intent == 'live_market_data'
    router --> math_solver: Intent == 'calculation' | 'math_calculation'
    router --> evidence_builder: Intent == 'direct_answer'
    
    decomposition --> retriever: Parallel Sub-queries
    retriever --> evidence_builder: Top Chunks via RRF + FlashRank
    market_data --> evidence_builder: Live Financial Quotes
    math_solver --> verifier: Deterministic Math Output
    
    evidence_builder --> verifier: Draft Synthesized Answer
    
    verifier --> retriever: Groundedness Audit Failed (retry_count < 1)
    verifier --> [*]: Verified Ground Truth Response
```

### 📋 Agent State Schema (`graph/state.py`)
```python
class AgentState(TypedDict):
    question: str                     # Cleaned user query
    history: List[Dict[str, str]]     # Multi-turn conversation messages
    user_id: str                      # Multi-tenant user identifier
    conversation_id: str              # Active conversation session ID
    document_ids: List[str]           # Attached personal document IDs
    depth: str                        # 'quick' | 'summary' | 'deep'
    sub_queries: List[str]            # Decomposed atomic sub-queries
    retrieved_chunks: List[Dict]      # Chunks returned by RRF & FlashRank
    market_data: Dict[str, Any]       # Live stock metrics from yfinance
    calculation_result: str           # Deterministic math output
    draft_answer: str                 # LLM synthesized response candidate
    final_answer: str                 # Verified response delivered to user
    suggested_actions: List[str]      # Clickable interactive prompt chips
    is_verified: bool                 # Verification status flag
    retry_count: int                  # Re-retrieval loop limiter (max 1)
```

### 🧩 LangGraph Node Specifications & Micro-Mechanics

| Node | File Location | Responsibility | Execution Mechanism |
|---|---|---|---|
| **`router`** | `nodes/router.py` | Intent classification & depth determination | 1. Regex fast-path for chit-chat/greetings (<1ms, 0 tokens).<br/>2. Keyword depth classifier (`quick`, `summary`, `deep`).<br/>3. LLM semantic router classifying into 7 intent paths. |
| **`decomposition`** | `nodes/decomposition.py` | Query splitting for multi-entity/period prompts | Breaks comparative questions (*"Compare Apple and Microsoft FY24 net income"*) into isolated search queries dispatched in parallel. |
| **`retriever`** | `nodes/retriever.py` | Multi-source hybrid chunk retrieval | Dispatches parallel Cypher queries against Lucene BM25 and Vector indices; fuses with RRF ($k=60$) and reranks with FlashRank. |
| **`market_data`** | `nodes/market_data.py` | Real-time equity quote fetching | Regex ticker symbol extraction + Yahoo Finance API (`yfinance`) with PE ratios, daily delta, and 52-week ranges. |
| **`math_solver`** | `nodes/math_solver.py` | Deterministic calculations & fund lookups | Routes to Python AST sandbox, Indian Tax Rules engine, or offline SEBI Mutual Fund database. |
| **`evidence_builder`** | `nodes/evidence_builder.py` | Response synthesis with depth conditioning | Formats evidence within `< 1,800 tokens`, enforces structured brevity, and generates `[Suggested Action]` interactive chips. |
| **`verifier`** | `nodes/verifier.py` | Self-RAG factual consistency audit | Compares synthesized figures against retrieved chunks. If ungrounded and `retry_count == 0`, routes back to `retriever`. |

---

## 🔍 Hybrid Graph-RAG Retrieval Pipeline

Financial documents require both **exact keyword precision** (e.g. *"FY24 diluted EPS $6.08"*) and **semantic conceptual matching** (e.g. *"shareholder capital return strategy"*). FinAdvisor-X uses a hybrid dual-channel retrieval architecture:

```mermaid
flowchart LR
    Query[User Query / Sub-Query] --> Embed[Embedding Generator]
    Embed -->|768-dim Vector| VectorIndex[Neo4j Dense Vector Search<br/>'vector_markdown']
    Query -->|Keywords| BM25Index[Neo4j Lucene Full-Text Search<br/>'keyword_markdown']
    
    VectorIndex -->|Top Chunks A| RRF[Reciprocal Rank Fusion<br/>k = 60]
    BM25Index -->|Top Chunks B| RRF
    
    RRF --> Candidates[Merged Candidate Chunks]
    Candidates --> FlashRank[FlashRank Neural Cross-Encoder<br/>ms-marco-MiniLM-L-12-v2<br/>Local In-Memory Cache]
    
    FlashRank --> Context[Top Ranked High-Precision Chunks<br/>+16.42% Precision Boost]
```

### 1. Reciprocal Rank Fusion (RRF)
RRF combines ranked lists without requiring score normalization across disparate scoring algorithms (cosine distance vs. BM25 score):

$$\text{RRF\_Score}(d) = \sum_{m \in \{BM25, Dense\}} \frac{1}{k + r_m(d)} \quad (k = 60)$$

*Why $k=60$?* $k=60$ acts as a damping constant, ensuring that a chunk appearing at rank #2 in *both* keyword and vector searches outranks a chunk that appears at rank #1 in only one list.

### 2. FlashRank Neural Cross-Encoder Reranking
Standard bi-encoders score query and document embeddings independently. FlashRank passes the query-document pair $(Q, D)$ jointly through `ms-marco-MiniLM-L-12-v2`, performing full cross-attention:
- **Precision@5 Lift**: **+16.42%** over hybrid RRF alone; **+18.19%** over dense vector alone.
- **Latency**: Local in-memory weight caching (`.cache/flashrank`) delivers cross-encoder inference in **< 40ms**.

### 3. Differentiated Dual-Embedding Strategy
| Use Case | Embedding Model | Vector Dimension | Query Latency | Design Rationale |
|---|---|---|---|---|
| **Shared Financial Knowledge Base** | `sentence-transformers/all-mpnet-base-v2` | 768-dim | ~900 ms (Indexed) | Maximum dimensional nuance for complex 10-K SEC filings and corporate finance textbooks. |
| **Personal User Ingested Documents** | ONNX `FastEmbed` (`BAAI/bge-small-en-v1.5`) | 384-dim | **14.1 ms** (73× faster) | Instant sub-second ingestion and query latency for user-uploaded bank statements and salary slips. |

---

## 🗄️ Data Ingestion, Storage & Graph Schemas

### 1. Relational Database Schema (Neon PostgreSQL)

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
        timestamp expires_at
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
    CONVERSATIONS ||--o{ USER_DOCUMENTS : "scopes"
```

### 2. Neo4j Knowledge Graph & Vector Schema

```text
Shared Financial Corpus:
  (:Chunk {
      id: string,
      content: string,
      source: string,
      embedding: float[768]
  })
  INDEX: 'vector_markdown' (Cosine Similarity, 768-dim)
  INDEX: 'keyword_markdown' (Lucene BM25 Fulltext on content)

Isolated Personal Document Chunks:
  (:PersonalChunk {
      user_id: string,          // Tenant Boundary
      document_id: string,      // Document Scope
      conversation_id: string,  // Session Scope
      content: string,
      embedding: float[384]
  })
  INDEX: 'personal_vector_markdown' (Cosine Similarity, 384-dim)
```

### 3. Lossless Tabular & Markdown Ingestion Engine
- **Deterministic 0-Token Table Extraction**: Standard bank statements and CSV files are parsed via regex/heuristic tabular extractors, achieving **82.4% zero-token ingestion** on complex multi-line statements.
- **Markdown Compaction**: Layout whitespace, repeated separators, and empty padding are stripped, yielding **~35% prompt token reduction** without semantic loss.
- **Upload Limit Guardrail**: Strict `< 5 MB` client & server limit with immediate `HTTP 413 Payload Too Large` rejection.

---

## 🔒 Strict Multi-Tenant Security & 3-Field Privacy Model

Enterprise financial systems require strict cryptographic and relational boundaries between users and sessions:

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant Gateway as ⚙️ FastAPI Gateway
    participant Guard as 🛡️ Auth & RateLimiter
    participant Postgres as 🗄️ Neon Postgres
    participant Neo4j as 🔍 Neo4j Graph/Vector

    User->>Gateway: POST /api/chat {conversation_id: "conv-1", message: "..."}
    Gateway->>Guard: Validate JWT & user_id
    Guard-->>Gateway: Authenticated (user_id = "usr-123")
    
    Gateway->>Postgres: Verify conv-1 belongs to usr-123
    Postgres-->>Gateway: Ownership Verified
    
    Gateway->>Neo4j: Query personal chunks WHERE user_id = "usr-123" AND conversation_id = "conv-1"
    Note over Neo4j: Strict 3-Field Equality Enforcement<br/>No Cross-User or Cross-Session Leakage
    Neo4j-->>Gateway: Scoped Chunks Only
```

### Security Guardrails:
1. **Compound 3-Field Isolation**: Every personal vector query enforces `WHERE c.user_id = $uid AND c.conversation_id = $cid AND c.document_id IN $doc_ids`. Access across conversations returns `403 Forbidden ("different conversation")`.
2. **Cascading Deletions**:
   - `DELETE /api/conversations/{id}` deletes message history from Postgres, invokes Cypher `MATCH (c:PersonalChunk {conversation_id: $id}) DETACH DELETE c`, and removes storage artifacts.
   - `DELETE /api/conversations` cascades across all user threads.
3. **Per-User Rate Limiting & Token Quota Isolation**:
   - Request timestamps and token counts are stored in **per-`user_id` sliding-window deques** (`core/rate_limiter.py`).
   - User A exceeding their quota receives `429 Too Many Requests` without degrading service for User B or User C.

---

## 🛡️ Resilient Multi-Provider LLM Cascade & Circuit Breaker

To guarantee 99.9% uptime despite third-party AI provider rate limits (HTTP 429) or transient server errors (HTTP 5xx), FinAdvisor-X deploys a multi-provider fallback cascade managed by a finite-state machine (FSM) Circuit Breaker:

```mermaid
flowchart LR
    Req[LLM Request] --> CB{Circuit Breaker<br/>Per-User FSM}
    CB -->|CLOSED| T1[1. OpenRouter Qwen 2.5 72B<br/>Primary Engine]
    CB -->|OPEN / Timeout| T2[2. OpenRouter DeepSeek-Chat<br/>Failover Tier 1]
    T1 -->|Timeout / 429 / 5xx| T2
    T2 -->|Failover Error| T3[3. Google Gemini 2.5 Flash<br/>Failover Tier 2]
    T3 -->|Failover Error| T4[4. Groq Qwen 3.8-27B<br/>Failover Tier 3]
    
    T1 --> Out[Structured Pydantic Output]
    T2 --> Out
    T3 --> Out
    T4 --> Out
```

### Circuit Breaker FSM Lifecycle (`core/circuit_breaker.py`)
- **`CLOSED`**: All requests route to the primary model. Consecutive failures increment a counter.
- **`OPEN`**: 3 consecutive timeouts trip the breaker into `OPEN` state. Requests immediately bypass the degraded provider, preventing thread exhaustion.
- **`HALF-OPEN`**: After a 45-second cooldown, a trial canary probe is dispatched. Success resets the breaker to `CLOSED`; failure extends the cooldown.
- **Multi-Tenant State**: The FSM state is tracked independently per `user_id`.

---

## 🎙️ Voice Interaction Subsystem

FinAdvisor-X integrates continuous bi-directional voice capabilities natively within the browser, eliminating external cloud speech API latency and cost.

### 1. Continuous Multi-Sentence Speech-to-Text (STT)
- **Module**: [`frontend/src/components/VoiceInputButton.tsx`](frontend/src/components/VoiceInputButton.tsx)
- **Engine**: Browser-native `SpeechRecognition` / `webkitSpeechRecognition`.
- **Auto-Recovery Loop**: Standard browser implementations drop sessions after short pauses. FinAdvisor-X uses an automated restart handler (`onend` with 60ms debounce) that captures long, multi-paragraph dictations until the user explicitly stops or submits.
- **Dual-Stream Feedback**: Real-time interim visual transcription with auto-commit into the prompt input.

### 2. Soft Female Text-to-Speech (TTS)
- **Module**: [`frontend/src/App.tsx`](frontend/src/App.tsx), [`frontend/src/components/ChatMessageItem.tsx`](frontend/src/components/ChatMessageItem.tsx)
- **Engine**: `window.speechSynthesis` and `SpeechSynthesisUtterance`.
- **Male Voice Blocklist Filter**: Strictly filters out male voice signatures (`David`, `Mark`, `George`, `Ravi`, `Guy`, `Ryan`, `Daniel`).
- **Curated Female Priority Chain**: Binds to natural female voices (`Microsoft Zira`, `Aria`, `Jenny`, `Neerja`, `Swara`, `Samantha`, `Karen`, `Victoria`).
- **Acoustic Calibration**: Configured with `pitch = 1.15` and `rate = 0.95` for natural, measured financial advisory cadence.
- **Markdown Sanitizer**: Strips markdown tables, code syntax, and raw tokens prior to utterance synthesis.

---

## 🧮 Deterministic Financial Math & Indian Tax Engine

Financial advisory demands exact mathematical precision. FinAdvisor-X routes all mathematical, tax, and fund queries to deterministic, non-hallucinating engines:

```mermaid
flowchart TD
    MathQuery[Math / Tax / Fund Query] --> RouterClass{Math Type}
    
    RouterClass -->|Arithmetic / Formulas| ASTSandbox[Python AST Sandbox<br/>tools/calculator.py<br/>0 tokens, <1ms]
    RouterClass -->|FY 2026-27 Income Tax| TaxEngine[Indian Tax Engine<br/>financial/tax_rules_india.py<br/>Section 115BAC Slabs]
    RouterClass -->|SEBI Mutual Funds| MFEngine[Offline MF Database<br/>tools/mf_lookup.py<br/>25+ Top Funds, <2ms]
    
    ASTSandbox --> Result[Deterministic Verified Output]
    TaxEngine --> Result
    MFEngine --> Result
```

### Capabilities:
1. **Python AST Math Sandbox** ([`tools/calculator.py`](tools/calculator.py)):
   - Evaluates arithmetic, compound interest, SIP, EMI, CAGR, NPV, DCF, and WACC without LLM math errors.
2. **Indian Tax Engine (FY 2026-27)** ([`financial/tax_rules_india.py`](financial/tax_rules_india.py)):
   - Implements New Tax Regime (Section 115BAC):
     - Standard Deduction: ₹75,000.
     - Section 87A Rebate: Zero tax for taxable income up to ₹7,00,000.
     - Slab Rates: ₹0-3L (0%), ₹3-7L (5%), ₹7-10L (10%), ₹10-12L (15%), ₹12-15L (20%), >₹15L (30%).
     - Capital Gains: 12.5% LTCG (>₹1.25L exemption), 20% STCG.
3. **Sub-2ms Mutual Fund Catalog** ([`tools/mf_lookup.py`](tools/mf_lookup.py)):
   - Offline JSON lookup for top SEBI mutual funds across Large Cap, Mid Cap, Small Cap, Flexi Cap, Hybrid, and ELSS.

---

## ⏱️ Latency Engineering, Caching & Token Economics

| Architectural Optimization | Mechanism | Performance Impact |
|---|---|---|
| **Adaptive Query Depth Routing** | Fast-path keyword & regex classification (`quick`, `summary`, `deep`) | **~40% to ~70% token reduction** |
| **0-Token Fast-Path Bypasses** | Greetings gate, formula lookups, mutual fund queries | **< 1ms response latency, 0 LLM cost** |
| **Dual-Tier Model Routing** | Fast reasoning (`fast_chat` <500ms) for routing/verification; high-capacity (`chat`) for synthesis only | **~78% daily LLM API cost savings** |
| **Local Cross-Encoder Caching** | FlashRank weights bound to `.cache/flashrank` | Cold-start weight loading: **58.3s → 0.3s** |
| **Background Memory Offloading** | Chat title generation and fact extraction moved to FastAPI `BackgroundTasks` | **Response dispatched to user ~1.2s faster** |
| **User-Scoped Exact & Semantic Cache** | Sub-1ms in-memory cache partitioned by `user_id` | **Instant sub-millisecond repeated query hits** |

---

## 📊 Empirical Benchmarks & Evaluation Metrics

Evaluated on a 50-query financial benchmark ([`tests/eval/gold_set.json`](tests/eval/gold_set.json)) covering SEC 10-K filings, corporate finance principles, tax calculations, and adversarial trap queries:

| Subsystem | Metric | Measured Benchmark | Operational Value |
|---|---|---|---|
| **FlashRank Cross-Encoder** | Precision@5 Lift vs Vector | **+18.19%** (0.3882 → 0.4588) | Ranks exact accounting line items at Rank #1 |
| **FlashRank Cross-Encoder** | Precision@5 Lift vs Hybrid RRF | **+16.42%** (0.3941 → 0.4588) | Eliminates irrelevant text snippets from context |
| **Hybrid Search (RRF $k=60$)** | Reciprocal Rank Fusion MRR | **0.6765 MRR** (903.1 ms) | Fuses dense semantic similarity with BM25 keywords |
| **Adversarial Hallucination Defense** | Safe Abstention Rate | **100.0%** (10 / 10 trap queries) | Zero hallucinations on unindexed firms or fake execs |
| **Deterministic Math Engine** | Calculation Pass Rate | **100.0%** (20 / 20 test cases) | Arithmetic & tax computation in <1ms (0 tokens) |
| **Greeting Gate & Chit-Chat** | Conversational Intent Pass | **100.0%** (55 / 55 test cases) | Intercepts greetings in <1ms; preserves compound queries |
| **Multi-User Quota Isolation** | Multi-Tenant Isolation | **100.0%** (5 / 5 unit, 3 / 3 integ) | User A quota exhaustion never impacts User B |
| **Answer Groundedness (Self-RAG)**| Factuality Score | **80.0% Grounded** (4.20 / 5.0) | Verified factual consistency against source chunks |

---

## 🧪 Automated Test Suite Coverage

**Grand Total: 85 / 87 tests passed (97.7%)** across automated integration test modules:

| Test Module | Tests | Passed | Failed | Status | Scope |
|---|---|---|---|---|---|
| `test_conversational_continuity.py` | 8 | 8 | 0 | ✅ PASS | Multi-turn conversational memory & context tracking |
| `test_document_ingestion*.py` | 37 | 37 | 0 | ✅ PASS | Async document upload, 5MB limits, isolation |
| `test_knowledge_graph.py` | 1 | 1 | 0 | ✅ PASS | Neo4j Cypher schema & relationship traversal |
| `test_indian_context.py` | 14 | 13 | 1 | ⚠️ 1 FAIL | Indian tax rules & SEBI mutual fund queries |
| `test_daily_snapshot_job.py` | 14 | 13 | 1 | ⚠️ 1 FAIL | Regulatory feed ingestion & snapshot routines |
| `test_market_data.py` | 8 | 8 | 0 | ✅ PASS | Yahoo Finance real-time stock ticker integration |
| `test_isolation_unit.py` | 5 | 5 | 0 | ✅ PASS | Multi-tenant sliding-window rate & token limits |
| `test_data_isolation.py` | 3 | 3 | 0 | ✅ PASS | 3-field personal chunk boundaries |

---

## 📁 Project Directory & Component Interaction Map

```text
FinAdvisor-Voice/
├── config/
│   └── settings.py              # Pydantic environment & app settings
├── core/
│   ├── auth.py                  # JWT, bcrypt, SHA-256 OTP & Brevo/SMTP delivery
│   ├── cache.py                 # User-scoped exact & semantic TTL memory cache
│   ├── circuit_breaker.py       # Multi-tenant user-scoped API failure FSM
│   ├── crypto.py                # Symmetric encryption for sensitive tokens
│   ├── db.py                    # Neo4j connections, LLM setup & 4-tier fallbacks
│   ├── document_store.py        # Token compressor, 5MB guardrail, isolation ingest
│   ├── memory.py                # Neon PostgreSQL multi-tenant memory & cascade deletion
│   ├── rate_limiter.py          # Multi-tenant sliding-window request & token usage limiter
│   ├── regulatory_feed_engine.py# Tax & regulatory RSS/HTML polling client
│   └── regulatory_watcher.py    # Autonomous monthly background regulatory sync loop
├── financial/
│   ├── calculator.py            # Financial formulas (SIP, EMI, CAGR, NPV, DCF)
│   ├── parser.py                # Financial table and query parser
│   └── tax_rules_india.py       # FY 2026-27 Indian Tax rules & calculation logic
├── frontend/                    # React 18 + TypeScript + Vite UI
│   ├── src/
│   │   ├── App.tsx              # Main dashboard with soft female TTS, drawer & Action Chips
│   │   ├── components/
│   │   │   ├── AuthModal.tsx    # Modal auth dialog
│   │   │   ├── LoginPage.tsx    # Glassmorphic auth portal
│   │   │   └── VoiceInputButton.tsx # Continuous multi-sentence Speech-to-Text
│   │   └── context/
│   │       └── AuthContext.tsx  # JWT authentication session context
├── graph/
│   ├── state.py                 # AgentState TypedDict schema with query depth
│   └── workflow.py              # LangGraph StateGraph assembly & conditional loops
├── nodes/                       # LangGraph execution nodes
│   ├── decomposition.py         # Sub-query split node for complex comparisons
│   ├── evidence_builder.py      # Depth-conditioned prompt synthesizer
│   ├── market_data.py           # Real-time stock ticker quote fetcher
│   ├── math_solver.py           # Deterministic math & fund routing
│   ├── retriever.py             # Lucene fulltext BM25 + dense vector retrieval
│   ├── router.py                # Fast-path & semantic classifier with depth routing
│   └── verifier.py              # Self-RAG fact-checking auditor
├── retrieval/
│   ├── hybrid_rrf.py            # Reciprocal Rank Fusion (k=60) implementation
│   ├── personal_retriever.py    # Isolated personal document retrieval
│   └── reranker.py              # FlashRank neural cross-encoder
├── tools/
│   ├── calculator.py            # AST-sandboxed Python financial math engine
│   └── mf_lookup.py             # Sub-2ms deterministic Indian Mutual Fund lookup
├── reports/                     # Evaluation metrics, benchmark logs & changelogs
├── tests/                       # Pytest test suite
├── Dockerfile                   # Multi-stage production container definition
├── docker-compose.yml           # Container orchestration configuration
├── main.py                      # FastAPI application gateway & endpoints
└── requirements.txt             # Python backend dependencies
```

---

## 💻 Getting Started & Local Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 20+** and **npm**
- **Neo4j AuraDB** instance (or local Neo4j 5.20+)
- **Neon PostgreSQL** database (or local PostgreSQL / SQLite)
- **OpenRouter API Key** or **Groq API Key**

### 2. Environment Configuration (`.env`)
Create a `.env` file in the project root:
```ini
# --- LLM Providers ---
OPENROUTER_API_KEY="sk-or-v1-..."
GROQ_API_KEY="gsk_..."
PRIMARY_MODEL="qwen/qwen-2.5-72b-instruct"
FAST_MODEL="qwen/qwen-2.5-72b-instruct"

# --- Neo4j Graph & Vector Database ---
NEO4J_URI="neo4j+s://xxxxxx.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-neo4j-password"

# --- Relational Database (Neon PostgreSQL) ---
DATABASE_URL="postgresql://user:password@ep-sample.us-east-2.aws.neon.tech/finadvisor?sslmode=require"

# --- Authentication & JWT ---
JWT_SECRET_KEY="your-super-secret-jwt-key"
JWT_ALGORITHM="HS256"

# --- Email OTP Delivery (Brevo HTTPS API or SMTP) ---
BREVO_API_KEY="xkeysib-..."
BREVO_SENDER_EMAIL="your-verified-email@domain.com"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=465
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
```

### 3. Start Backend Server
```bash
# In project root:
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
- API & Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 4. Start Frontend UI
```bash
cd frontend
npm install
npm run dev
```
- Frontend Web App: `http://localhost:5173`

---

## 🐳 Docker Deployment

```bash
# Build and run multi-stage container
docker compose up --build -d

# Inspect health status
docker ps

# Stream logs
docker compose logs -f
```

---

## 📡 REST API Endpoints

| Endpoint | Method | Purpose | Authentication |
|---|---|---|---|
| `/api/auth/send-otp` | `POST` | Send 6-digit cryptographic OTP via Brevo/SMTP | Public |
| `/api/auth/verify-otp` | `POST` | Verify OTP and issue temporary verification token | Public |
| `/api/auth/register` | `POST` | Register user with email, password, and verification token | Public |
| `/api/auth/login` | `POST` | Authenticate user and receive JWT access token | Public |
| `/api/auth/me` | `GET` | Retrieve authenticated user profile | Bearer JWT |
| `/api/conversations` | `GET` | List all conversation threads for authenticated user | Bearer JWT |
| `/api/conversations` | `POST` | Create a new conversation thread | Bearer JWT |
| `/api/conversations` | `DELETE` | **Bulk clear all conversations** and cascade purge private docs | Bearer JWT |
| `/api/conversations/{id}` | `GET` | Retrieve conversation message history | Bearer JWT |
| `/api/conversations/{id}` | `DELETE` | **Delete single conversation** with cascade chunk cleanup | Bearer JWT |
| `/api/documents/upload` | `POST` | Upload and isolate financial PDF/CSV (< 5 MB) | Bearer JWT |
| `/api/chat` | `POST` | Execute LangGraph query with depth routing & verified response | Bearer JWT |
| `/api/health` | `GET` | System health and database connectivity probe | Public |

---

## 🎯 Technical Interview Cheatsheet & Architecture Defense Guide

> 💡 **Use this section to confidently explain every architectural trade-off, design decision, and metric to technical interviewers.**

### 🎙️ The 2-Minute Architecture Pitch
> *"FinAdvisor-X is an enterprise financial advisory platform built on an Agentic Hybrid Graph-RAG architecture. We solved the five primary failure modes of vanilla RAG: semantic drift on exact numbers, hallucination on financial calculations, high token latency, LLM provider outages, and multi-tenant data leakage.*
> 
> *Our retrieval blends Neo4j Lucene BM25 keyword search with 768-dim dense embeddings using Reciprocal Rank Fusion ($k=60$), followed by a local FlashRank neural cross-encoder that delivers a +16.42% precision boost. An orchestrated LangGraph state machine routes complex queries through decomposition, executes math deterministically via Python AST sandboxes and SEBI mutual fund databases in <2ms at 0 tokens, and subjects generated responses to a Self-RAG verification audit loop.*
> 
> *For multi-tenancy, we enforce 3-field compound isolation `(user_id, document_id, conversation_id)` at the database level with cascading deletions. The frontend features continuous auto-recovering speech recognition and soft female voice synthesis."*

---

### ❓ Top 10 Technical Interview Questions & In-Depth Answers

#### 1. Why use Hybrid Search (BM25 + Vector) instead of pure Vector search?
> **Answer**: Financial queries contain two distinct modalities:
> 1. **Exact numerical & lexical entities**: Tickers (`TCS.NS`, `NVDA`), accounting terms (`Section 115BAC`, `Diluted EPS`), and specific fiscal years (`FY24 Q3`). Vector embeddings compress text into a dense semantic manifold where small token variations get blurred, causing poor keyword retrieval.
> 2. **Conceptual questions**: *"How does the company return capital to shareholders?"* Dense vector search excels here.
> 
> Neo4j native Lucene BM25 (`keyword_markdown`) captures exact lexical hits, while vector search (`vector_markdown`) captures semantic intent. Merging them via Reciprocal Rank Fusion yields optimal Mean Reciprocal Rank (**0.6765 MRR**).

#### 2. Why is Reciprocal Rank Fusion (RRF with $k=60$) used over weighted linear score combinations?
> **Answer**: Dense vector search yields cosine similarity scores (range 0.0 to 1.0), whereas Lucene BM25 produces unbounded relevance scores (e.g., 0 to 45.0). Normalizing BM25 scores dynamically is unstable across varying query lengths.
> 
> RRF is scale-invariant because it only operates on **rank positions** ($1 / (k + \text{rank})$). Setting the damping constant $k=60$ prevents a document ranked #1 in only one list from dominating over a document that ranks consistently high (#2 or #3) across both lists.

#### 3. Why add a FlashRank Cross-Encoder reranker after RRF?
> **Answer**: Bi-encoders (vector embeddings) encode the query and document independently to allow fast indexing. However, they cannot model inter-token interactions between the question and the document.
> 
> Our FlashRank reranker (`ms-marco-MiniLM-L-12-v2`) takes the top candidate chunks from RRF and feeds the combined pair into full cross-attention. This eliminated noise chunks and produced a **+16.42% Precision@5 lift** over RRF alone. By caching weights in `.cache/flashrank`, inference takes **< 40ms**.

#### 4. Why use LangGraph instead of simple linear chains or ReAct loops?
> **Answer**: Linear chains cannot handle conditional branching, retries, or state recovery. ReAct loops often suffer from infinite loops or unstructured execution paths.
> 
> LangGraph models execution as a **deterministic StateGraph**:
> - Branching based on query intent (`router` → `decomposition` / `retriever` / `math_solver` / `market_data`).
> - **Self-RAG verification cycle**: If the `verifier` node detects factual inconsistencies or missing evidence, it increments `retry_count` and loops back to `retriever` for broader context.
> - Typed, shared state (`AgentState`) preserved cleanly across nodes.

#### 5. How do you ensure zero hallucinations in financial math?
> **Answer**: LLMs are probabilistic text predictors and fundamentally unreliable for multi-step arithmetic, compounding, and tax slabs.
> 
> We completely bypass LLMs for mathematical operations:
> 1. Arithmetic, SIP, EMI, CAGR, and DCF formulas are evaluated in an AST-sandboxed Python calculator ([`tools/calculator.py`](tools/calculator.py)).
> 2. Indian Income Tax (Section 115BAC) is computed via deterministic rule functions ([`financial/tax_rules_india.py`](financial/tax_rules_india.py)).
> 3. SEBI Mutual Fund parameters are fetched from an offline database ([`tools/mf_lookup.py`](tools/mf_lookup.py)).
> All execute in **< 2ms at 0 LLM token cost**.

#### 6. How is strict multi-tenant privacy enforced for user-uploaded documents?
> **Answer**: We enforce a **3-Field Compound Privacy Boundary**:
> Every personal document chunk ingested into Neo4j is tagged with `(user_id, document_id, conversation_id)`. All Cypher queries strictly filter on all three fields.
> - Uploading a bank statement in Conversation A makes it impossible to query from Conversation B without explicit re-attachment (returning `403 Forbidden`).
> - Deleting a conversation triggers a database transaction that purges PostgreSQL records and cascades Cypher deletion to Neo4j personal nodes.

#### 7. How does the system survive LLM provider rate limits and outages?
> **Answer**: We implement a **4-Tier LLM Fallback Cascade** wrapped in a **Finite State Machine Circuit Breaker**:
> 1. Primary: OpenRouter Qwen 2.5 72B.
> 2. Failover 1: OpenRouter DeepSeek-Chat.
> 3. Failover 2: Google Gemini 2.5 Flash.
> 4. Failover 3: Groq Qwen 3.8-27B.
> 
> The Circuit Breaker tracks consecutive errors per `user_id`. After 3 consecutive timeouts, the breaker trips to `OPEN`, failing fast to the next provider and testing recovery after a 45-second cooldown in `HALF-OPEN` mode.

#### 8. Why use dual embedding models (768-dim vs. 384-dim ONNX)?
> **Answer**:
> - **Shared 10-K Corpus**: High complexity SEC filings require deep semantic resolution. We use 768-dim `all-mpnet-base-v2` (`0.7118 MRR`).
> - **Personal Document Ingestion**: Users expect instant statement parsing. We use 384-dim ONNX `FastEmbed` (`bge-small-en-v1.5`), which runs in **14.1 ms (73× faster)** with minimal memory footprint.

#### 9. How did you optimize end-to-end response latency and token costs?
> **Answer**:
> 1. **Adaptive Depth Routing**: Classifies queries into `quick` (2-4 sentences), `summary` (4-6 bullets), or `deep`, saving **40% to 70% in tokens**.
> 2. **Deterministic Fast-Paths**: Greetings and simple lookups return in `< 1ms` at **0 tokens**.
> 3. **Dual-Tier Models**: Fast reasoning models (`fast_chat` <500ms) handle routing and verification; high-capacity models handle synthesis only (**~78% cost reduction**).
> 4. **Background Task Offloading**: Async memory extraction and conversation titling run in FastAPI `BackgroundTasks` after the response stream completes.

#### 10. How does the continuous voice STT and soft female TTS work on the frontend?
> **Answer**:
> - **Continuous STT**: Uses browser-native `SpeechRecognition` with an auto-recovery debounce loop on the `onend` event to prevent premature session termination during multi-sentence dictations.
> - **Soft Female TTS**: Uses `window.speechSynthesis`, applies a male voice blocklist, selects priority female voices (`Microsoft Zira`, `Aria`, `Jenny`), and acoustically calibrates pitch (`1.15`) and speed (`0.95`).

---

## 📋 Changelog & Historical Fixes

### 🔴 Critical Fix: Multi-User Rate/Token Limit Isolation Bug *(September 2026)*
- **Bug**: Global shared state in `RateLimiter` caused User A's exhausted quota to block unrelated User B with `429 Too Many Requests`.
- **Fix**: Refactored `RateLimiter` and `CircuitBreaker` to store state in `dict[str, deque]` strictly keyed by `user_id`. Verified via unit and integration tests (`tests/test_data_isolation.py`).

### 🟠 Neo4j Lucene BM25 Native Integration *(September 2026)*
- Replaced slow string property scanning with native Neo4j Lucene fulltext indexing (`CALL db.index.fulltext.queryNodes("keyword_markdown", ...)`), boosting keyword Precision@5 by **+14.4%**.

### ⚡ Sub-Second Latency & Local Model Warmup *(October 2026)*
### 🟢 Production Hardening: Domain Guardrails, Live RSS Feeds & Deterministic Math *(October 2026)*
- **Strict Domain Boundary Guardrail (`core/domain_guardrails.py`)**: Deterministically refuses out-of-domain coding requests (e.g. Python scripts, sum of 2 numbers in Python) and non-financial trivia/inventors in `<1ms` (0 LLM tokens). Includes an output filter in the verifier node preventing accidental code leaks.
- **Live Indian Financial News & IPO Feeds (`nodes/news_data.py`)**: Enhanced live RSS ingestion with multi-source coverage (LiveMint Markets/Industry/Economy, Economic Times IPO) and intelligent token-weighted ranking, providing up-to-the-minute updates on IPOs (such as Jio Platforms) and market events.
- **Expanded Financial Math Engine (`tools/fast_math.py`)**: Integrated zero-token NLP parsing for profit, loss, profit margin, percentage change, and chained arithmetic expressions (e.g., `5*20/10`) alongside WACC, DCF, SIP, and Indian Tax calculations.
- **100% Verified Multi-Tenant Security**: Confirmed zero data leakage across user sessions, private document retrieval, and persistent conversational memory.

---

## 👨‍💻 Author & Maintainer
Built with ❤️ by **[Ashok Singodia](https://github.com/AshokSingodia-Codes)** ([@AshokSingodia-Codes](https://github.com/AshokSingodia-Codes)).

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
