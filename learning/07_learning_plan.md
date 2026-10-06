# 📚 07 — Learning Plan: Beginner to Advanced

---

## Prerequisites (Before Anything)

Make sure you know these first:

| Skill | Why Needed | Learn From |
|---|---|---|
| Python basics | 80% of code is Python | Any Python tutorial |
| `async/await` in Python | FastAPI uses async everywhere | Real Python — Async IO |
| React + TypeScript basics | Frontend | React official docs |
| REST APIs (HTTP verbs) | Understanding routes | MDN Web Docs |
| What SQL is | For PostgreSQL | W3Schools SQL |

---

## Phase 1 — Foundation (Week 1)

**Goal:** Understand the project structure, run it locally, and make your first change.

### Day 1-2: Setup and Overview
1. Read `learning/01_project_overview.md` (this folder)
2. Read `learning/02_architecture_HLD.md` (diagrams)
3. Clone the repo and read the root `README.md`
4. Setup `.env` file from `.env_example`

**Exercise 1:** Draw the architecture from memory without looking. Check yourself.

### Day 3-4: Configuration and Database
1. Read `config/settings.py` — understand every setting
2. Read `core/db.py` lines 1-100 (LLM setup)
3. Read `graph/state.py` — memorize all AgentState fields

**Exercise 2:** Add a new setting `MAX_CHUNKS_PER_QUERY: int = Field(10)` to `settings.py` and print it at startup.

### Day 5-7: Run the App Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Start backend: `uvicorn main:app --reload`
3. Start frontend: `cd frontend && npm run dev`
4. Register a test account through the UI
5. Ask a question

**Exercise 3:** Send a manual `curl` request to `/api/auth/send-otp` and observe what happens.

---

## Phase 2 — The AI Agent (Week 2)

**Goal:** Understand how LangGraph works and be able to add/modify nodes.

### Day 8-9: LangGraph Basics
1. Read `graph/workflow.py` — trace every edge
2. Read `graph/state.py` again, now understanding the flow
3. Draw the workflow graph by hand (no looking at HLD)

**Exercise 4:** Add a `print(f"[NODE] routing_decision: {state['routing_decision']}")` to `route_question()` and observe the console when you ask a question.

### Day 10-11: Router Node
1. Read `nodes/router.py` entirely
2. Understand the 8 routing decisions
3. Understand `classify_depth()` trigger word logic
4. Understand structured LLM output with Pydantic

**Exercise 5:** Add a new trigger word set for "regulatory" queries:
```python
REGULATORY_TRIGGERS = {"sebi", "rbi", "regulation", "compliance", "circular"}
```
And return `"regulatory"` from `classify_depth()` if triggered.

### Day 12-13: Retriever + RRF
1. Read `nodes/retriever.py`
2. Read `retrieval/hybrid_rrf.py` — trace through `reciprocal_rank_fusion()`
3. Manually compute RRF on paper:
   - List A: [DocX, DocY, DocZ]
   - List B: [DocY, DocX, DocW]
   - Compute scores for each doc with k=60

**Exercise 6:** Change `top_k=10` to `top_k=15` in `get_hybrid_rrf_results()` and measure if answer quality improves.

### Day 14: Evidence Builder + Verifier
1. Read `nodes/evidence_builder.py`
2. Read `nodes/verifier.py`
3. Understand the retry loop in `graph/workflow.py` lines 87-110

**Exercise 7:** Add a "depth=deep" path to the evidence builder that returns a longer answer with sources cited.

---

## Phase 3 — Authentication & Security (Week 3)

**Goal:** Understand the full auth flow and be able to add/modify security features.

### Day 15-16: Auth Core
1. Read `core/auth.py` entirely
2. Understand bcrypt hashing vs. SHA256
3. Understand OTP generation, hashing, and verification
4. Trace the JWT lifecycle: create → send → verify → expire

**Exercise 8:** Manually create a JWT using python-jose in a Python shell:
```python
from jose import jwt
token = jwt.encode({"sub": "test-user"}, "my-secret", algorithm="HS256")
payload = jwt.decode(token, "my-secret", algorithms=["HS256"])
print(payload)
```

### Day 17-18: Auth Endpoints (main.py)
1. Read `main.py` lines 203-400 (all auth endpoints)
2. Trace the OTP flow step by step using `04_execution_flow.md`
3. Understand FastAPI `Depends()` dependency injection

**Exercise 9:** Using Postman or curl, manually test the complete registration flow:
1. `POST /api/auth/send-otp`
2. Check email for OTP
3. `POST /api/auth/verify-otp`
4. `POST /api/auth/register`
5. `POST /api/auth/login`

### Day 19-20: Rate Limiting + Caching
1. Read `core/rate_limiter.py`
2. Read `core/cache.py`
3. Understand how cache key is computed
4. Read `core/circuit_breaker.py`

**Exercise 10:** Intentionally trigger the rate limiter by sending 20 quick chat requests and observing the 429 response.

---

## Phase 4 — Database Layer (Week 4)

**Goal:** Understand PostgreSQL + Neo4j and be able to write queries.

### Day 21-22: PostgreSQL (core/memory.py)
1. Read `core/memory.py` (it's big — 48KB)
2. Focus on: `create_user`, `create_conversation`, `add_message`, `get_conversation_context`
3. Understand the SQLAlchemy connection pool

**Exercise 11:** Write a new function `get_user_stats(user_id)` that returns:
- Total conversations
- Total messages
- Last active timestamp

### Day 23-24: Neo4j
1. Read `core/db.py` lines 200+ (Neo4j setup)
2. Read `retrieval/personal_retriever.py` — study the Cypher queries
3. Access Neo4j Browser (localhost:7474) and run the queries manually

**Exercise 12:** Write a Cypher query to find all PersonalChunk nodes for a specific `user_id`.

### Day 25-26: Document Store
1. Read `core/document_store.py`
2. Understand the PDF → text → chunks → embeddings → Neo4j pipeline
3. Read `core/crypto.py` for Fernet encryption

**Exercise 13:** Trace what happens when you upload a PDF:
- Which tables/nodes are created?
- What happens if the PDF has no text?
- What happens if it's not a financial document?

---

## Phase 5 — Financial Domain (Week 5)

### Day 27-28: Tax & Calculations
1. Read `financial/tax_rules_india.py`
2. Read `financial/calculator.py`
3. Run the SIP formula manually with pen and paper

**Exercise 14:** Add a new formula to `financial/calculator.py`:
```python
def cagr(start_value: float, end_value: float, years: int) -> float:
    """Compound Annual Growth Rate"""
    return (end_value / start_value) ** (1 / years) - 1
```

### Day 29-30: Live Data & News
1. Read `nodes/market_data.py`
2. Try: `import yfinance as yf; yf.Ticker("RELIANCE.NS").info`
3. Read `nodes/news_data.py`

---

## Phase 6 — Frontend (Week 6)

### Day 31-32: Auth + Context
1. Read `frontend/src/context/AuthContext.tsx`
2. Read `frontend/src/components/AuthModal.tsx`
3. Understand how OTP flow maps to UI states

**Exercise 15:** Add a "show password" toggle button to `AuthModal.tsx`.

### Day 33-34: Chat UI
1. Read `frontend/src/App.tsx` (largest file)
2. Focus on: message state, send function, streaming reader
3. Read `frontend/src/components/ChatMessageItem.tsx`

**Exercise 16:** Add a "Copy to clipboard" button on each assistant message in `ChatMessageItem.tsx`.

### Day 35: Voice Input
1. Read `frontend/src/components/VoiceInputButton.tsx`
2. Understand `webkitSpeechRecognition` API
3. Test voice input in Chrome

---

## Phase 7 — Advanced: Extending the System (Week 7-8)

**Goal:** Add a meaningful new feature from scratch.

### Project A: Add a New Router Route — "regulatory"
1. Add `"regulatory"` to router's valid decisions
2. Add a `regulatory_node` in `nodes/` that searches SEBI/RBI announcements
3. Wire it in `graph/workflow.py`

### Project B: Add Response Rating
1. Add `POST /api/chat/{message_id}/rate` endpoint
2. Create a `message_ratings` table in PostgreSQL
3. Show thumbs up/down in `ChatMessageItem.tsx`
4. Store rating in DB

### Project C: Export Conversation
1. Add `GET /api/conversations/{id}/export` endpoint
2. Return conversation as formatted PDF or Markdown
3. Add "Export" button in sidebar

### Project D: Add a New Financial Calculator
1. Add `dividend_yield()` formula to `financial/calculator.py`
2. Route "dividend yield" queries through `math_calculation` node
3. Test with: "What is the dividend yield of TCS if price is ₹4000 and annual dividend is ₹72?"

---

## Self-Test Questions

After completing all phases, you should be able to answer:

### Architecture
- [ ] What is the difference between `fast_chat` and `synthesis_chat`?
- [ ] Why does the verifier node create a retry loop?
- [ ] What is the purpose of the 3-field isolation in personal document retrieval?
- [ ] Why is RRF better than just combining two search results?

### Security
- [ ] What is the difference between bcrypt and SHA256? When do you use each?
- [ ] Why is the OTP stored as a hash in the database?
- [ ] What happens if a user's JWT expires? What error do they get?
- [ ] What does `allow_origins=["*"]` mean? Is it safe for production?

### Data Flow
- [ ] What SQL queries run when a user logs in?
- [ ] What Neo4j queries run when a user asks a question?
- [ ] How many LLM API calls does a single chat message trigger?
- [ ] What happens if Neo4j is down? Does the app crash?

### Code Quality
- [ ] What design pattern does `get_db_connection()` use? Why?
- [ ] What is the `.with_fallbacks()` pattern? Why use it instead of try/except?
- [ ] Why does AgentState use `total=False`?
- [ ] What is the difference between `state["field"]` and `state.get("field")`?

---

## Recommended Study Resources

| Topic | Resource |
|---|---|
| FastAPI | https://fastapi.tiangolo.com/tutorial/ |
| LangGraph | https://langchain-ai.github.io/langgraph/ |
| Neo4j Cypher | https://neo4j.com/docs/cypher-manual/current/ |
| JWT | https://jwt.io/introduction |
| SQLAlchemy | https://docs.sqlalchemy.org/en/20/ |
| React Context | https://react.dev/reference/react/createContext |
| pydantic v2 | https://docs.pydantic.dev/latest/ |
| bcrypt | https://pypi.org/project/bcrypt/ |
| yfinance | https://ranaroussi.github.io/yfinance/ |
