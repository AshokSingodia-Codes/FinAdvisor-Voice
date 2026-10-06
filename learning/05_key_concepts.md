# 💡 05 — Key Concepts Explained Simply

> Every important term in this project, explained from first principles with examples.

---

## 1. RAG — Retrieval-Augmented Generation

**The problem:** LLMs (like GPT, Gemini) don't know YOUR data. If you ask "What was TCS revenue in FY24?", the model might hallucinate or not know.

**The solution RAG provides:**
1. **Retrieve** — Search your documents for relevant chunks
2. **Augment** — Add those chunks to the LLM prompt
3. **Generate** — LLM answers using the provided context (not hallucination)

```
WITHOUT RAG:
"What was TCS revenue FY24?" → GPT → "I think it was around ₹200K crore" (HALLUCINATION)

WITH RAG:
"What was TCS revenue FY24?" → Search Neo4j → "TCS Q4FY24 revenue ₹61,237 crore (Source: 10-K)"
                                             → GPT with context → "TCS revenue was ₹2,40,893 crore" ✅
```

**Where in codebase:** `nodes/retriever.py` retrieves, `nodes/evidence_builder.py` generates.

---

## 2. RRF — Reciprocal Rank Fusion

**The problem:** You have two search results:
- Vector search: `[DocA, DocC, DocB, DocD]`
- Graph search:  `[DocB, DocA, DocD, DocC]`
Which order should the final list be? You can't just concatenate.

**RRF formula:** Score each document from each list and sum them up:
```
Score(doc) = Σ(across all lists)  1 / (k + rank_position)

k = 60  (prevents rank-1 from dominating too much)
```

**Example:**
```
DocA: vector rank=1, graph rank=2
  → Score = 1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03252

DocB: vector rank=3, graph rank=1
  → Score = 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226

Final order: DocA (0.032) > DocB (0.032) > ...
```

**Why k=60?** It's the "damping constant" — prevents a document ranked #1 in ONE list from beating a document ranked #2 in BOTH lists.

**Where in codebase:** `retrieval/hybrid_rrf.py` → `reciprocal_rank_fusion()`

---

## 3. LangGraph — State Machine for AI Agents

**The problem:** Complex AI tasks need multiple steps — route the query, search documents, verify the answer, maybe retry. Just calling an LLM once isn't enough.

**LangGraph solution:** Think of it like a flowchart where each box is a function:

```python
# A node is just a Python function that takes state and returns state
def my_node(state: dict) -> dict:
    result = do_something(state["input"])
    return {**state, "output": result}   # Update state, pass forward

# Wire them together
workflow = StateGraph(dict)
workflow.add_node("step1", my_node)
workflow.add_node("step2", another_node)
workflow.add_edge("step1", "step2")     # Always go step1 → step2
workflow.add_conditional_edges("router_node", decide_fn, {"A": "nodeA", "B": "nodeB"})
```

**The "state" travels through all nodes** — like a shared notebook that each node can read from and write to.

**Where in codebase:**
- `graph/state.py` — defines what's in the notebook (AgentState)
- `graph/workflow.py` — draws the flowchart
- `nodes/*.py` — each box in the flowchart

---

## 4. JWT — JSON Web Tokens

**The problem:** When a user logs in, how does the server remember who they are for future requests? HTTP is stateless (no memory between requests).

**JWT solution:** After login, server creates a signed "pass" and gives it to the user. The user sends this pass with every request. The server verifies the signature without hitting the database.

**Structure:** `header.payload.signature` (base64 encoded)
```json
Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": "user-id-123", "email": "user@example.com", "exp": 1699999999}
Signature: HMACSHA256(header + "." + payload, SECRET_KEY)
```

**Verification flow:**
```python
# Creating (at login):
token = jwt.encode({"sub": user_id, "exp": expiry}, SECRET_KEY, algorithm="HS256")

# Verifying (at each request):
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload["sub"]
# If signature is invalid or expired → raises JWTError → 401 Unauthorized
```

**Why secure?** The `SECRET_KEY` is only known to the server. Attacker can't forge the signature without it.

**Where in codebase:** `core/auth.py` → `create_access_token()`, `get_current_user()`

---

## 5. CORS — Cross-Origin Resource Sharing

**The problem:** Browser security blocks `http://frontend.com` from calling `http://api.backend.com` (different "origin"). This is the Same-Origin Policy.

**CORS solution:** The API server adds headers to its responses:
```
Access-Control-Allow-Origin: https://myapp.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
```
Browser sees these headers and allows the request.

**In this project:**
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Any origin (dev-friendly, tighten in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Where in codebase:** `main.py` lines 126-132

---

## 6. Vector Embeddings + Similarity Search

**The problem:** How do you search documents for "TCS revenue" when a document says "Tata Consultancy Services annual turnover"? Keyword search misses it.

**Embeddings solution:** Convert text to numbers (vectors) that capture semantic meaning:
```
"TCS revenue"          → [0.12, -0.34, 0.87, 0.21, ...]  (384 numbers)
"Tata Consultancy Services annual turnover"
                       → [0.14, -0.31, 0.84, 0.19, ...]  (384 numbers)
```
These two vectors are SIMILAR (close in 384-dimensional space).

**Cosine similarity:** Measure angle between vectors → 0 = identical, 1 = opposite

**Where in codebase:**
- `core/db.py` → `FastEmbedWrapper` uses BAAI/bge-small-en-v1.5 (ONNX model)
- Neo4j stores vectors and handles ANN (Approximate Nearest Neighbor) search

---

## 7. Graph Database (Neo4j)

**The problem:** SQL tables are good for rows of data, but bad at relationships. "Find all companies related to Reliance" requires complex JOINs.

**Graph solution:** Store data as nodes and relationships:
```
(TCS: Company) --[REPORTED]--> (Revenue: ₹2.4L crore: FinancialMetric)
(TCS: Company) --[FILED]--> (10K_Report: Document)
(10K_Report) --[CONTAINS]--> (Chunk1: TextChunk)
(Chunk1) --[NEXT]--> (Chunk2: TextChunk)
```

**Cypher query (Neo4j's SQL):**
```cypher
MATCH (c:Company {name: "TCS"})-[:REPORTED]->(m:FinancialMetric)
WHERE m.year = 2024
RETURN m.revenue
```

**Where in codebase:**
- `core/db.py` → `kg = Neo4jGraph(...)` — graph connection
- `core/db.py` → `vector_store = Neo4jVector(...)` — vector index on Neo4j
- `retrieval/hybrid_rrf.py` → queries both

---

## 8. bcrypt Password Hashing

**The problem:** If you store passwords as plain text ("mypassword123") and your database leaks, everyone's account is compromised.

**bcrypt solution:** One-way hashing with "salt":
```python
# Storing (at registration):
hashed = bcrypt.hashpw("mypassword123".encode(), bcrypt.gensalt())
# → "$2b$12$eImiTXuWVxfM37uY4JANjQ/kJlO9nxOVjV0MQ6z5Xl6/QGID0eM8S"

# Verifying (at login):
bcrypt.checkpw("mypassword123".encode(), hashed)  # → True
bcrypt.checkpw("wrongpassword".encode(), hashed)  # → False
```

**Why can't you reverse it?** bcrypt is a one-way function. Even with the hash, you cannot get back the original password.

**Salt:** Random bytes added before hashing. Two users with the same password get DIFFERENT hashes.

**Where in codebase:** `core/auth.py` → `hash_password()`, `verify_password()`

---

## 9. OTP (One-Time Password)

**Why this project uses OTP:**
- Prevents fake account creation (verify real email ownership)
- Required for password reset without security questions

**Flow:**
```
1. Server generates: OTP = "847291" (6 random digits)
2. Server hashes it:  hash = SHA256("847291:secret_salt")
3. Server stores hash in DB (NOT the raw OTP)
4. Server emails "847291" to user
5. User enters "847291" in UI
6. Server hashes what user entered → compares to stored hash
7. If match + not expired → issue verification_token
```

**Why hash the OTP?** Even if DB leaks, attacker can't use the hash to verify — they need the raw OTP which is only in the user's email.

**Where in codebase:** `core/auth.py` → `generate_otp()`, `hash_otp()`, `verify_otp_hash()`

---

## 10. Circuit Breaker Pattern

**The problem:** If Neo4j is down, every request hangs for 30 seconds waiting to timeout. With 100 concurrent users, the entire app freezes.

**Circuit Breaker solution:** After N failures, "open" the circuit and return immediately without waiting:

```
CLOSED state: Normal operation, all requests go through
  → After 5 failures in 60s → OPEN

OPEN state: All requests fail immediately (fast fail)
  → After 30s timeout → HALF-OPEN

HALF-OPEN state: Allow 1 test request
  → If success → CLOSED (recovered)
  → If failure → OPEN again
```

**Where in codebase:** `core/circuit_breaker.py`

---

## 11. Fernet Encryption (for Personal Documents)

**Why encrypt uploaded PDFs?**
If the database is breached, attacker gets encrypted blobs — useless without the `ENCRYPTION_KEY`.

**Fernet = AES-128-CBC + HMAC-SHA256:**
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Must be kept secret in .env
f = Fernet(key)

# Encrypt:
encrypted = f.encrypt(b"My annual report content...")
# → b'gAAAAABl...' (ciphertext)

# Decrypt:
original = f.decrypt(encrypted)
# → b'My annual report content...'
```

**Where in codebase:** `core/document_store.py` + `core/crypto.py`

---

## 12. FastAPI Dependency Injection

**What it is:** FastAPI's way of reusing logic across multiple endpoints.

```python
# Define a "dependency" — a function FastAPI calls automatically
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> dict:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload["sub"]
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user

# Use it in any endpoint with Depends()
@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)  # ← injected automatically
):
    user_id = current_user["id"]  # Available without writing auth logic again
```

**Where in codebase:** `core/auth.py` → `get_current_user()`, used in most protected endpoints in `main.py`

---

## 13. Pydantic Models

**What they do:** Define the shape of request/response data AND validate it automatically.

```python
class ChatRequest(BaseModel):
    message: str               # Required string
    conversation_id: Optional[str] = None   # Optional
    stream: Optional[bool] = False          # Default False

# FastAPI automatically:
# 1. Parses JSON body into ChatRequest
# 2. Validates types (message must be str)
# 3. Returns 422 if validation fails
```

**Where in codebase:** All request/response models in `main.py` lines 134-196

---

## 14. AsyncIO + Background Tasks

**What async means:** FastAPI can handle multiple requests simultaneously without one blocking another.

```python
@app.post("/api/chat")
async def chat_endpoint():   # "async" = non-blocking
    # While waiting for LLM response, FastAPI can handle other requests
    result = await some_async_function()
    return result
```

**Background tasks in this project:**
```python
# Starts at server startup (in lifespan):
asyncio.create_task(monthly_watchdog_background_loop())  # Runs forever in background
asyncio.create_task(_daily_snapshot_background_loop())   # Runs forever in background
```

**Where in codebase:** `main.py` lifespan function, `core/regulatory_watcher.py`

---

## 15. FlashRank (Cross-Encoder Reranker)

**Problem:** Embedding models (bi-encoders) are fast but approximate. They embed query and document SEPARATELY, so miss subtle relationships.

**Cross-encoder solution:** Feed (query, document) PAIR through a small BERT model — gets much better relevance score:
```
Bi-encoder:  embed(query) · embed(doc) = cosine score  (fast, approximate)
Cross-encoder: bert(query + "[SEP]" + doc) → relevance score  (slower, accurate)
```

**Where in codebase:** `retrieval/reranker.py` → `get_ranker()` (FlashRank model)

---

## Quick Reference: When Does Each Concept Apply?

| User Action | Concepts Used |
|---|---|
| Click "Register" | OTP, SHA256, bcrypt, JWT |
| Type a question | CORS, JWT verification, Rate Limiting |
| Financial question | RAG, Vector Embeddings, Graph DB, RRF, LangGraph |
| "What is 15% of 50000" | Fast Math (no LLM), no RAG |
| "Stock price of Infosys" | yfinance API, LangGraph live_data node |
| Upload a PDF | Fernet encryption, PDF parsing, chunking, vector embeddings |
| Server starts up | Background tasks, circuit breaker warmup |
