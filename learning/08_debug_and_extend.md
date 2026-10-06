# 🛠️ 08 — Debug, Test & Extend the Project

---

## Running the Project

### Backend Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill environment variables
cp .env_example .env
# Edit .env with your API keys

# 4. Start the backend
uvicorn main:app --reload --port 8000
# --reload = auto-restart on file changes (dev only)
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# → Available at http://localhost:5173
```

### With Docker

```bash
# Build and run everything
docker compose up --build

# Optional: Also start local Neo4j
docker compose --profile local-neo4j up --build

# Rebuild only the app
docker compose build finadvisor-app
docker compose up finadvisor-app
```

---

## Environment Variables (Must Fill)

Open `.env` and fill these MINIMUM settings to run:

```env
# Neo4j (required)
NEO4J_URI=bolt://localhost:7687          # Or Neo4j Aura URI
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# LLM (at least one required)
GROQ_API_KEY=gsk_...                     # Get free at console.groq.com
# OPENROUTER_API_KEY=sk-or-...           # Optional fallback
# GOOGLE_API_KEY=AIza...                 # Optional fallback

# Database (SQLite fallback if empty)
DATABASE_URL=postgresql://user:pass@host/db  # Neon: neondb.io

# Email (for OTP — optional in dev, required in prod)
BREVO_API_KEY=xkeysib-...
BREVO_SENDER_EMAIL=your@email.com

# Security
JWT_SECRET=your-random-secret-string-here
ENCRYPTION_KEY=  # Leave blank for dev (uses ephemeral key)
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_conversation_system.py -v

# Run a specific test function
pytest tests/test_greeting_gate.py::test_greeting_shortcircuit -v

# Run with coverage report
pip install pytest-cov
pytest --cov=. --cov-report=html
```

### What Each Test File Tests

| File | Tests |
|---|---|
| `test_conversation_system.py` | Create, rename, delete conversations; add messages |
| `test_db_migration_safety.py` | Schema migrations don't break existing data |
| `test_greeting_gate.py` | Greetings bypass LangGraph (performance test) |
| `test_daily_snapshot_job.py` | Background daily snapshot job runs correctly |

---

## Common Debugging Techniques

### 1. Add Print Statements to Trace Flow

```python
# In any node, add temporary prints:
def route_question(state: AgentState) -> AgentState:
    print(f"[ROUTER] Input: {state['current_question']}")
    # ... your logic ...
    print(f"[ROUTER] Decision: {routing_decision}")
    return {**state, "routing_decision": routing_decision}
```

### 2. Check FastAPI's Interactive Docs

The API has built-in documentation at:
- http://localhost:8000/docs — Swagger UI (try all endpoints)
- http://localhost:8000/redoc — ReDoc UI

### 3. Enable LangSmith Tracing

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=my-debug-project
```

Then go to https://smith.langchain.com — see every LLM call, latency, token count, and the exact prompt sent.

### 4. Common Errors and Fixes

| Error | Likely Cause | Fix |
|---|---|---|
| `Connection refused :7687` | Neo4j not running | Start Neo4j or check URI |
| `401 Unauthorized` | JWT expired or missing | Re-login; check Authorization header |
| `429 Too Many Requests` | Rate limit hit | Wait 60s or increase limit in rate_limiter.py |
| `422 Unprocessable Entity` | Pydantic validation failed | Check request body matches the Pydantic model |
| `500 Internal Server Error` | Unhandled exception | Check server console logs |
| `GROQ_API_KEY not set` | Missing env var | Add to .env and restart |
| Frontend CORS error | Backend not running or wrong port | Start backend on port 8000 |
| `ModuleNotFoundError` | Missing package | `pip install -r requirements.txt` |

### 5. Test a Specific Node in Isolation

```python
# Create a test file: scratch/test_router.py
from graph.state import AgentState
from nodes.router import route_question

state = AgentState(
    original_question="What is TCS revenue?",
    current_question="What is TCS revenue?",
    memory_context="",
    conversation_id="test-conv-1",
    user_id="test-user-1",
)

result = route_question(state)
print(f"Routing decision: {result['routing_decision']}")
print(f"Depth: {result.get('depth')}")
```

Run with: `python scratch/test_router.py`

### 6. Test RRF Fusion Manually

```python
# scratch/test_rrf.py
from retrieval.hybrid_rrf import reciprocal_rank_fusion

# Simulate two rankers returning overlapping results
vector_results = ["Doc A", "Doc C", "Doc B", "Doc D"]
graph_results = ["Doc B", "Doc A", "Doc D", "Doc C"]

fused = reciprocal_rank_fusion([vector_results, graph_results])
print("Fused order:", fused)
# Expected: Doc A (high in both) should win
```

---

## How to Add a New Feature

### Example: Add a "Portfolio Tracker" Query Type

**Step 1: Update the Router**

In `nodes/router.py`, add `"portfolio_query"` to the valid decisions in the `Route.decision` field description:

```python
class Route(BaseModel):
    decision: str = Field(
        description="Must be one of: decompose | hybrid_search | ... | portfolio_query"
    )
```

**Step 2: Create the Node**

```python
# nodes/portfolio.py
from graph.state import AgentState

def handle_portfolio_query(state: AgentState) -> AgentState:
    """Handles portfolio-related queries."""
    question = state["current_question"]
    user_id = state["user_id"]

    # Your logic here: fetch user's portfolio from DB, calculate returns, etc.
    answer = f"Portfolio analysis for user {user_id}: ..."

    return {**state, "draft_answer": answer}
```

**Step 3: Wire it in the Graph**

```python
# graph/workflow.py
from nodes.portfolio import handle_portfolio_query

workflow.add_node("portfolio", handle_portfolio_query)

# Add to conditional edges:
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        ...existing...,
        "portfolio_query": "portfolio"   # ← add this
    }
)

# Portfolio → verifier (direct path, no retrieval needed)
workflow.add_edge("portfolio", "verifier")
```

**Step 4: Update route_decision function**

```python
def route_decision(state: AgentState):
    decision = state["routing_decision"]
    ...
    elif decision == "portfolio_query":
        return "portfolio_query"    # ← add this
    ...
```

**Step 5: Test**

```python
# scratch/test_portfolio_node.py
from graph.state import AgentState
from nodes.portfolio import handle_portfolio_query

state = AgentState(
    current_question="Show my portfolio performance",
    user_id="test-user-1"
)
result = handle_portfolio_query(state)
print(result["draft_answer"])
```

---

## How to Add a New API Endpoint

### Example: `GET /api/users/me/stats`

```python
# In main.py, after the existing endpoints:

class UserStats(BaseModel):
    total_conversations: int
    total_messages: int
    last_active: Optional[str]

@app.get("/api/users/me/stats", response_model=UserStats)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Return stats for the authenticated user."""
    user_id = current_user["id"]

    with get_db_connection() as conn:
        conv_count = conn.execute(
            text("SELECT COUNT(*) FROM conversations WHERE user_id = :uid"),
            {"uid": user_id}
        ).scalar()

        msg_count = conn.execute(
            text("""
                SELECT COUNT(*) FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.user_id = :uid
            """),
            {"uid": user_id}
        ).scalar()

        last_active = conn.execute(
            text("SELECT MAX(updated_at) FROM conversations WHERE user_id = :uid"),
            {"uid": user_id}
        ).scalar()

    return UserStats(
        total_conversations=conv_count,
        total_messages=msg_count,
        last_active=last_active.isoformat() if last_active else None
    )
```

---

## Performance Profiling

### Find Slow Operations

```python
import time

def route_question(state: AgentState) -> AgentState:
    t0 = time.perf_counter()

    # ... your logic ...

    elapsed = (time.perf_counter() - t0) * 1000
    print(f"[PERF] router: {elapsed:.1f}ms")
    return result
```

### Common Performance Bottlenecks

| Bottleneck | Solution |
|---|---|
| Cold-start embedding model | Pre-warm in lifespan (already done) |
| N+1 database queries | Batch queries or add JOIN |
| Sequential vector + graph search | Already parallelized with ThreadPoolExecutor |
| LLM timeout | Check model timeout settings in core/db.py |
| Large PDF upload | Increase chunking overlap, reduce chunk size |
| Repeated same questions | Response cache (already implemented) |

---

## Technical Debt (Known Issues)

Based on code analysis, these areas need improvement:

| Issue | Location | Severity |
|---|---|---|
| `allow_origins=["*"]` — too permissive | `main.py:128` | Medium — tighten in prod |
| No input sanitization for chat message | `main.py` chat endpoint | Medium — add max length |
| `OTP_MAX_ATTEMPTS = 5` imported but not enforced | `core/auth.py` | Medium — add attempt counter |
| Router cache not invalidated on error | `nodes/router.py` | Low — stale routes possible |
| SQLite fallback has different behavior than PostgreSQL | `core/memory.py` | Medium — test thoroughly |
| No conversation title update after topic change | `main.py` | Low — UX issue |
| Frontend `allow_origins` hardcoded to Render URL | `frontend/src/config.ts` | Low — use env var |

---

## Useful Commands Reference

```bash
# Backend
uvicorn main:app --reload                 # Dev server
uvicorn main:app --port 8000 --workers 2  # Production-like
python init_db.py                         # Initialize PostgreSQL tables
python rebuild_vector_db.py               # Rebuild Neo4j vector index

# Frontend
npm run dev           # Dev server
npm run build         # Production build
npm run lint          # OxLint check
npm run preview       # Preview production build

# Database
python check_db.py    # Check PostgreSQL connection
python sanity_check.py # Check Neo4j connection

# Testing
pytest -v                                 # All tests
pytest tests/test_greeting_gate.py -v    # Specific file
pytest -k "test_create" -v               # Tests matching pattern
pytest --tb=short                        # Short traceback on failure
```
