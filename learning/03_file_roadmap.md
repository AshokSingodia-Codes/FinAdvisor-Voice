# 🗺️ 03 — File-by-File Learning Roadmap

> Read files in this exact order. Each section tells you:
> - What the file does
> - Key things to learn from it
> - How it connects to other files

---

## Phase 1: Foundation (Start Here)

### 1. `config/settings.py`
**What it is:** The single source of truth for ALL configuration. Every module imports from here.

**Key things to learn:**
- `pydantic_settings.BaseSettings` — reads from `.env` automatically
- `Field(default, description=...)` — self-documenting settings
- `@property` — computed values like `effective_jwt_secret`
- The `validate_groq_models()` function that fails loudly on bad config

**Connections:** Every single backend file imports `from config.settings import settings`

```python
# This pattern is used everywhere:
from config.settings import settings
model = settings.GROQ_MODEL   # reads from .env or default
```

---

### 2. `core/db.py`
**What it is:** Creates all shared LLM client instances and the embedding model. Think of it as the "wiring closet" — all AI connections are made here, and all nodes import from it.

**Key things to learn:**
- **Dual-tier LLM architecture**: `fast_chat` (router/verifier) vs `synthesis_chat` (evidence builder)
- `.with_fallbacks([...])` — LangChain's automatic retry with next provider
- `FastEmbedWrapper` — wraps ONNX-based `fastembed` model into LangChain's `Embeddings` interface
- `Neo4jVector` — vector store backed by Neo4j

**Connections:** All `nodes/*.py` files import `from core.db import fast_chat, synthesis_chat, kg, fast_embeddings`

---

### 3. `graph/state.py`
**What it is:** Defines `AgentState` — the data structure that flows through every node in the LangGraph pipeline.

**Key things to learn:**
- `TypedDict` — a dict with defined keys and types (Python typing)
- Every field name — these flow through every node
- `total=False` — all fields are optional (no field is required at creation)

```python
class AgentState(TypedDict, total=False):
    original_question: str
    routing_decision: str   # e.g. "hybrid_search"
    retrieved_context: List[str]
    draft_answer: str
    final_answer: str
    verification_passed: bool
    # ... 15+ more fields
```

---

### 4. `graph/workflow.py`
**What it is:** The "blueprint" of the AI agent. Connects all nodes into a directed graph using LangGraph.

**Key things to learn:**
- `StateGraph(AgentState)` — creates a graph that passes AgentState between nodes
- `workflow.add_node("name", function)` — registers a node
- `workflow.add_edge("A", "B")` — always go from A to B
- `workflow.add_conditional_edges(...)` — choose next node based on state
- `workflow.compile()` — creates the final runnable graph

**Visual:** See Mermaid diagram in `02_architecture_HLD.md`

---

## Phase 2: The AI Agent Nodes

All nodes in `/nodes/` follow the same pattern:
```python
def my_node(state: AgentState) -> AgentState:
    # Read from state
    question = state["current_question"]
    # Do work (LLM call, search, etc.)
    result = ...
    # Write back to state
    return {**state, "some_field": result}
```

---

### 5. `nodes/router.py`
**What it is:** The first node every query hits. Decides WHERE to send the query.

**Key things to learn:**
- `classify_depth()` — keyword-based depth detection (quick/summary/deep) using trigger word sets
- `Route` Pydantic model — structured LLM output
- `get_structured_fast_chat(Route)` — makes LLM return a validated `Route` object
- Router cache — 10-minute TTL dict cache for identical queries
- 8 possible routing decisions:

| Decision | Next Node | When |
|---|---|---|
| `hybrid_search` | retriever | General financial QA |
| `financial_table` | retriever | Table/data questions |
| `decompose` | decompose | Multi-part questions |
| `calculation` | math_solver | Formula math |
| `math_calculation` | math_calculation | Arithmetic |
| `live_market_data` | live_data | Stock prices |
| `current_events` | news_node | News queries |
| `direct_answer` | evidence_builder | No retrieval needed |

---

### 6. `nodes/decomposition.py`
**What it is:** Breaks complex multi-part questions into simpler sub-questions.

**Example:**
- Input: _"Compare TCS and Infosys revenue and profit margins"_
- Output: `["TCS revenue FY24?", "Infosys revenue FY24?", "TCS profit margin?", "Infosys profit margin?"]`

---

### 7. `nodes/retriever.py`
**What it is:** Fetches relevant document chunks from Neo4j. The heart of RAG.

**Key things to learn:**
- **Shared corpus path**: calls `get_hybrid_rrf_results()` (Neo4j vector + graph search)
- **Personal document path**: calls `get_personal_rrf_results()` (user's uploaded PDF)
- The two paths are **strictly separate** — no accidental data leakage

---

### 8. `retrieval/hybrid_rrf.py`
**What it is:** Implements Reciprocal Rank Fusion.

**Key things to learn:**
- `reciprocal_rank_fusion(results_lists, k=60)` — the core algorithm
- `concurrent.futures.ThreadPoolExecutor` — runs vector search AND graph search in PARALLEL
- Why parallel? Cut latency in half (both searches run simultaneously)

```python
# The actual RRF formula implemented:
fused_scores[doc_str] += 1 / (k + rank)   # k=60, rank=0-indexed
```

---

### 9. `retrieval/personal_retriever.py`
**What it is:** Handles retrieval from user-uploaded personal documents (PDFs).

**Key things to learn:**
- **3-field isolation**: every Cypher query filters by `user_id AND document_id AND conversation_id`
- `personal_vector_search()` — vector search on PersonalChunk nodes
- `personal_keyword_search()` — keyword/fulltext search on PersonalChunk nodes

---

### 10. `retrieval/reranker.py`
**What it is:** Uses FlashRank (cross-encoder model) to re-rank the RRF results.

**Key things to learn:**
- Cross-encoder vs bi-encoder difference (cross-encoder is slower but more accurate)
- `get_ranker()` — lazy-loaded singleton pattern

---

### 11. `nodes/evidence_builder.py`
**What it is:** Takes retrieved chunks and synthesizes a final answer using the large LLM.

**Key things to learn:**
- Uses `synthesis_chat` (NOT `fast_chat`) — this is the expensive, high-quality LLM
- Adapts prompt based on `depth` field ("quick", "summary", "deep")
- Constructs formatted prompt from retrieved context + conversation memory

---

### 12. `nodes/verifier.py`
**What it is:** A quality gate. Checks if the draft answer actually answers the question.

**Key things to learn:**
- Uses `fast_chat` (cheap/fast LLM) to verify
- If verification fails AND retries < 1 → sends state back to retriever
- This creates the **iterative retrieval loop** in the graph

---

### 13. `nodes/math_solver.py`
**What it is:** Handles formula-based financial calculations (SIP, CAGR, EMI, compound interest, tax).

**Uses:** The financial formulas in `financial/tax_rules_india.py` and `financial/calculator.py`

---

### 14. `nodes/math_calculation.py`
**What it is:** Handles simple arithmetic evaluation.

**Key:** Uses `tools/fast_math.py` which safely evaluates math expressions.

---

### 15. `nodes/market_data.py`
**What it is:** Fetches live stock data using `yfinance`.

```python
import yfinance as yf
ticker = yf.Ticker("RELIANCE.NS")   # .NS = NSE India
info = ticker.info   # dict with price, PE, market cap, etc.
```

---

### 16. `nodes/news_data.py`
**What it is:** Fetches current financial news.

---

## Phase 3: Core Infrastructure

### 17. `core/memory.py`
**What it is:** ALL PostgreSQL database operations. The largest core file (~48KB).

**Key functions to know:**

| Function | What it does |
|---|---|
| `create_user(email, password_hash)` | Insert new user |
| `get_user_by_email(email)` | Find user by email |
| `create_conversation(user_id, title)` | Start new chat |
| `add_message(conversation_id, role, content)` | Save a chat message |
| `get_conversation_context(conversation_id, n=6)` | Get last N turns for memory |
| `extract_and_update_memory(...)` | AI extracts key facts from conversation |
| `save_otp_record(email, otp_hash, purpose, expiry)` | Store hashed OTP |
| `verify_and_claim_otp(email, otp, purpose)` | Validate + consume OTP |

**Key pattern:** Uses SQLAlchemy with `contextmanager`:
```python
@contextmanager
def get_db_connection():
    with engine.connect() as conn:
        yield conn
```

---

### 18. `core/auth.py`
**What it is:** All authentication logic — passwords, OTPs, JWTs.

**Key functions:**

| Function | What it does |
|---|---|
| `hash_password(password)` | bcrypt hash |
| `verify_password(plain, hashed)` | bcrypt compare |
| `generate_otp()` | Cryptographically secure 6-digit OTP |
| `hash_otp(otp)` | SHA256 hash (stored, not raw OTP) |
| `send_otp_email(email, otp, purpose)` | Brevo API or SMTP fallback |
| `create_access_token(data, expires)` | Creates JWT using python-jose |
| `get_current_user(credentials)` | FastAPI dependency — decodes JWT |

---

### 19. `core/rate_limiter.py`
**What it is:** In-memory rate limiter for the `/api/chat` endpoint.

**Key things to learn:**
- Sliding window algorithm
- `asyncio.Lock()` — thread-safe counter update
- Per-user rate limiting (keyed by `user_id`)

---

### 20. `core/cache.py`
**What it is:** TTL-based response cache using `cachetools`.

**Key things to learn:**
- `TTLCache(maxsize=100, ttl=300)` — auto-evicts after 5 minutes
- Why cache? Identical questions (e.g., "What is SEBI?") shouldn't re-run the full LangGraph pipeline

---

### 21. `core/circuit_breaker.py`
**What it is:** Protects external API calls from cascading failures.

**Key things to learn:**
- Circuit states: CLOSED → OPEN → HALF-OPEN
- If Neo4j fails 5 times → circuit opens → returns fast error instead of waiting
- Prevents the entire app from hanging when one service is down

---

### 22. `core/document_store.py`
**What it is:** Handles personal PDF upload, processing, encryption, and Neo4j ingestion.

**Key things to learn:**
- `pdfplumber` + `PyPDF2` for text extraction (with fallback)
- `Fernet` symmetric encryption — encrypts raw PDF content before storing
- Chunking strategy — splits text into overlapping chunks
- Neo4j PersonalChunk node creation with embeddings

---

### 23. `core/greeting_handler.py`
**What it is:** Fast-path handler for non-financial queries (greetings, chitchat).

**Key things to learn:**
- Short-circuits the LangGraph pipeline for simple greetings
- Returns response without touching Neo4j or LLM
- Saves latency and API costs

---

### 24. `core/regulatory_feed_engine.py` + `core/regulatory_watcher.py`
**What it is:** Background worker that monitors for regulatory updates (SEBI, RBI notices).

**Key things to learn:**
- `asyncio.create_task()` — starts background loop at startup
- `monthly_watchdog_background_loop()` — runs indefinitely, wakes up monthly

---

## Phase 4: Financial Domain Logic

### 25. `financial/tax_rules_india.py`
**What it is:** India-specific tax calculation engine.

**Contains:**
- Income tax slabs (Old regime + New regime)
- LTCG/STCG tax rules for stocks/mutual funds
- Surcharge + cess calculation
- Section 80C/80D deduction rules

---

### 26. `financial/transaction_pipeline.py`
**What it is:** Processes financial transactions data.

---

### 27. `financial/calculator.py`
**What it is:** Core financial formulas.

**Formulas included:**
```python
def sip_returns(monthly_investment, rate, years):
    r = rate / 100 / 12
    n = years * 12
    return monthly_investment * ((1 + r) ** n - 1) / r * (1 + r)

def compound_interest(principal, rate, years, n=1):
    return principal * (1 + rate/100/n) ** (n*years) - principal

def emi(principal, rate, years):
    r = rate / 100 / 12
    n = years * 12
    return principal * r * (1+r)**n / ((1+r)**n - 1)
```

---

## Phase 5: Tools

### 28. `tools/fast_math.py`
**What it is:** Safe math expression evaluator. The largest tool file.

**Key things to learn:**
- `try_evaluate_fast_math(query)` — tries to compute without LLM
- Safety: does NOT use `eval()` — uses `ast.literal_eval` + custom parser
- Returns `None` if not a pure math expression (falls through to LLM)

---

### 29. `tools/calculator.py`
**What it is:** Wrapper that exposes financial calculations as LangChain tool.

---

### 30. `tools/mf_lookup.py`
**What it is:** Mutual fund NAV lookup.

---

## Phase 6: The API (main.py)

### 31. `main.py` (994 lines)
**What it is:** The FastAPI application — all HTTP endpoints.

**Key sections to read:**

| Lines | Content |
|---|---|
| 1-80 | Imports and LangGraph compilation |
| 81-133 | Lifespan (startup warmup) + CORS middleware |
| 134-200 | Pydantic request/response models |
| 201-400 | Auth endpoints (OTP, register, login, reset) |
| 400-600 | Chat endpoint with streaming |
| 600-800 | Conversation CRUD endpoints |
| 800-994 | Document upload/delete + background jobs |

---

## Phase 7: Frontend

### 32. `frontend/src/config.ts`
**What it is:** API base URL detection (localhost vs production).

### 33. `frontend/src/context/AuthContext.tsx`
**What it is:** React Context for global auth state. Every component that needs `user` or `token` reads from here.

### 34. `frontend/src/components/AuthModal.tsx`
**What it is:** Login + Registration modal with OTP flow.

### 35. `frontend/src/components/LoginPage.tsx`
**What it is:** Landing page for unauthenticated users.

### 36. `frontend/src/App.tsx` (40KB — largest frontend file)
**What it is:** Main chat application UI. Contains:
- Conversation sidebar
- Chat message list
- Input box + voice button
- Document upload
- Streaming response handler

### 37. `frontend/src/components/ChatMessageItem.tsx`
**What it is:** Renders individual messages with react-markdown.

### 38. `frontend/src/components/VoiceInputButton.tsx`
**What it is:** Web Speech API integration for voice input.

---

## Phase 8: Tests

### 39. `tests/` directory
**Contains tests for:**
- `test_conversation_system.py` — conversation CRUD
- `test_db_migration_safety.py` — DB schema safety
- `test_greeting_gate.py` — greeting short-circuit
- `test_daily_snapshot_job.py` — background job

**Key to learn:** `pytest`, `pytest-mock`, and `pytest-asyncio` patterns.

---

## Dependency Graph (Who imports Who)

```
.env
 └── config/settings.py
      └── core/db.py
           ├── nodes/router.py
           ├── nodes/retriever.py ──── retrieval/hybrid_rrf.py
           │                      └── retrieval/personal_retriever.py
           ├── nodes/evidence_builder.py
           ├── nodes/verifier.py
           ├── nodes/math_solver.py ── financial/calculator.py
           │                       └── financial/tax_rules_india.py
           └── nodes/market_data.py ── yfinance

      core/memory.py (PostgreSQL)
      core/auth.py   (JWT + OTP)
      core/cache.py
      core/rate_limiter.py
      core/document_store.py

 graph/state.py
 graph/workflow.py ←─ all nodes

 main.py ←─ everything above
```
