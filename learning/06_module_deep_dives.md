# 🔬 06 — Module Deep Dives

> Code-level explanation of the most important functions, classes, and design decisions.

---

## Module 1: `config/settings.py`

### The `Settings` Class

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NEO4J_URI: str = Field("bolt://localhost:7687")
    GROQ_API_KEY: str = Field("")
    RRF_K: int = Field(60)  # ← YOUR RRF constant!
    JWT_SECRET: str = Field("...")

    model_config = SettingsConfigDict(
        env_file=".env",        # Read from .env file
        case_sensitive=False,   # NEO4J_URI = neo4j_uri = NEO4J_uri
        extra="ignore"          # Ignore unknown env vars (don't crash)
    )
```

**Design decision:** Why use `pydantic_settings` instead of `os.getenv()`?
- **Type safety**: `RRF_K: int` means it's always an integer. `os.getenv("RRF_K")` returns a string.
- **Validation**: Pydantic validates values at startup. Bad config = immediate crash with clear error.
- **Documentation**: Each `Field(description=...)` documents what the setting does.
- **Singleton**: `settings = Settings()` at bottom of file — imported everywhere, evaluated once.

---

## Module 2: `core/db.py` — LLM Architecture

### The Fallback Chain Pattern

```python
# Build primary + fallback list
fast_primary = ChatGroq(model_name="gpt-oss-20b", timeout=4)
fast_fallbacks = [
    ChatGroq(model_name="qwen3.8-27b", timeout=4),
    ChatOpenAI(model="mistral-small-24b", timeout=5),
]

# Wire them together with .with_fallbacks()
fast_chat = fast_primary.with_fallbacks(fast_fallbacks)

# When you call fast_chat.invoke("question"):
# → Tries gpt-oss-20b first
# → If it fails/times out → tries qwen3.8-27b
# → If that fails → tries mistral-small-24b
# All automatic. No try/except needed in node code.
```

**Design decision:** Why two tiers (fast_chat vs synthesis_chat)?
- **Fast chain** (router, verifier, decomposer): Needs < 500ms. Uses small, cheap models.
- **Synthesis chain** (evidence builder): Needs quality, can be 2-5s. Uses large, capable models.
- Mixing them would mean using expensive 120B model just to classify "is this a greeting?" (wasteful).

### FastEmbedWrapper — The Embedding Model

```python
class FastEmbedWrapper(Embeddings):
    """Wraps fastembed (ONNX) to work with LangChain's Embeddings interface."""

    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self._model = None  # Lazy loading — don't load until first use

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed_query(self, text: str) -> List[float]:
        model = self._get_model()
        # fastembed returns generator — convert to list
        return list(model.embed([text]))[0].tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        return [list(vec) for vec in model.embed(texts)]
```

**Design decision:** Why BAAI/bge-small-en-v1.5 (ONNX)?
- Runs on CPU (no GPU needed) — works on Render free tier
- 33MB model, loads in ~2 seconds
- 384-dimensional vectors (good quality/speed tradeoff)
- ONNX = optimized inference format (2-3x faster than PyTorch)

---

## Module 3: `graph/state.py` — AgentState

```python
class AgentState(TypedDict, total=False):
    # Input fields (set at start)
    original_question: str
    current_question: str        # May be rewritten by router (pronoun resolution)
    chat_history: List[Dict]
    memory_context: str          # Pre-formatted history string for LLM
    conversation_id: str
    user_id: str
    document_id: Optional[str]   # None = shared corpus, set = personal PDF

    # Routing fields (set by router node)
    routing_decision: str        # "hybrid_search" | "calculation" | etc.
    depth: str                   # "quick" | "summary" | "deep"
    resolved_query: str          # Pronoun-resolved version of question

    # Retrieval fields (set by retriever node)
    retrieved_context: List[str] # Top chunks from RRF

    # Generation fields
    draft_answer: str            # From evidence_builder
    final_answer: str            # From verifier (or same as draft)

    # Control fields
    verification_passed: bool
    retrieval_retries: int       # Max 1 retry in shared corpus mode
    decomposed_questions: List[str]

    # Entity tracking (Phase 2 — conversational continuity)
    active_entities: Dict[str, Any]   # {"company": "TCS", "ticker": "TCS.NS"}
    conversation_topic: str           # "TCS financials"
    verifier_enabled: bool
```

**Design decision:** Why `total=False`?
- Not all fields exist at all graph stages.
- `total=False` means you can create `AgentState({"original_question": "..."})` without providing ALL fields.
- Nodes use `state.get("field", default)` to safely access optional fields.

---

## Module 4: `nodes/router.py` — Query Routing

### The Route Pydantic Model

```python
class Route(BaseModel):
    decision: str = Field(
        description="Must be one of: decompose | hybrid_search | financial_table | "
                    "calculation | math_calculation | direct_answer | live_market_data | current_events"
    )
    resolved_query: Optional[str] = Field(
        description="Rewrite question resolving pronouns using active entities"
    )
    is_topic_change: bool = Field(
        description="True if question shifts to a new subject"
    )
```

**Why structured output?** LLMs sometimes return `"I think this should be hybrid_search"` instead of just `"hybrid_search"`. Pydantic structured output forces the LLM to return a valid JSON that matches the schema — no string parsing needed.

```python
# Get a structured LLM that returns a Route object
structured_llm = get_structured_fast_chat(Route)
route: Route = structured_llm.invoke(prompt)
print(route.decision)  # Always a valid string, never garbage
```

### Depth Classification (Pure Code, No LLM)

```python
def classify_depth(question: str) -> str:
    lower_q = question.lower()

    # Check trigger word sets using "any(trigger in lower_q for trigger in set)"
    if any(t in lower_q for t in QUICK_TRIGGERS):   # "briefly", "short answer"
        return "quick"
    if any(t in lower_q for t in DEEP_TRIGGERS):    # "deep dive", "in detail"
        return "deep"
    if any(t in lower_q for t in SUMMARY_TRIGGERS): # "summarize", "overview"
        return "summary"

    return "quick"  # default
```

**Design decision:** Why keywords instead of LLM for depth classification?
- Pure keyword matching takes ~0.1ms vs ~100ms for an LLM call.
- The trigger word sets are carefully curated and cover the vast majority of real queries.
- For depth classification, precision > 99% is achievable with keywords alone.
- Saves money and latency.

---

## Module 5: `retrieval/hybrid_rrf.py` — The Fusion Engine

### Why Parallel Execution?

```python
# SEQUENTIAL (BAD):
vector_results = vector_index.similarity_search(query, k=10)  # 150ms
graph_results = graph_retriever_func(query)                    # 150ms
# Total: 300ms

# PARALLEL (GOOD):
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_vec = executor.submit(vector_index.similarity_search, query, k=10)
    future_graph = executor.submit(graph_retriever_func, query)
    vector_results = future_vec.result()  # Both run simultaneously
    graph_results = future_graph.result()
# Total: ~150ms (as slow as the SLOWER of the two)
```

**Design decision:** `ThreadPoolExecutor` vs `asyncio.gather()`
- Neo4j client is synchronous (blocking I/O), NOT async
- `ThreadPoolExecutor` runs blocking code in separate threads
- `asyncio.gather()` only works with `async def` coroutines
- For blocking I/O, threads are the correct tool

### Personal Document Isolation

```python
def get_personal_rrf_results(
    query: str,
    user_id: str,        # REQUIRED — prevents cross-user leakage
    document_id: str,    # REQUIRED — scopes to specific document
    conversation_id: str # REQUIRED — prevents cross-conversation leakage
) -> List[str]:
    # Every Cypher query inside personal_retriever enforces ALL THREE:
    # WHERE n.user_id = $user_id
    # AND n.document_id = $document_id
    # AND n.conversation_id = $conversation_id
```

**Design decision:** Why 3-field isolation (not just document_id)?
- `user_id` prevents: UserA seeing UserB's document (even if they know the document_id)
- `document_id` prevents: Mixing documents within same user
- `conversation_id` prevents: Document uploaded in Chat-1 leaking into Chat-2
- All three together create a "security perimeter" around each document

---

## Module 6: `core/auth.py` — Authentication

### OTP Security Design

```python
OTP_EXPIRY_MINUTES = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5

def generate_otp() -> str:
    # secrets.randbelow(900000) → random int in [0, 900000)
    # + 100000 → ensures 6 digits (100000 to 999999)
    return f"{secrets.randbelow(900000) + 100000:06d}"

def hash_otp(otp: str) -> str:
    # Use first 16 chars of JWT_SECRET as salt
    # This means same OTP produces different hashes in different environments
    salt = settings.effective_jwt_secret[:16]
    return hashlib.sha256(f"{otp}:{salt}".encode('utf-8')).hexdigest()
```

**Why `secrets.randbelow` instead of `random.randint`?**
- `random` module is NOT cryptographically secure — predictable with enough samples
- `secrets` module uses OS's cryptographically secure random number generator
- For OTPs (security-critical), always use `secrets` or `os.urandom`

### JWT Creation and Verification

```python
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=1440))
    to_encode.update({"exp": expire})  # Expiry claim

    # Signed with secret key — tampering invalidates signature
    return jwt.encode(to_encode, settings.effective_jwt_secret, algorithm="HS256")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.effective_jwt_secret,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

---

## Module 7: `core/memory.py` — Database Operations

### Connection Management Pattern

```python
from contextlib import contextmanager
from sqlalchemy import create_engine

# Connection pool — reuse connections, don't create new one per request
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Keep 5 connections open
    max_overflow=10,       # Allow up to 10 extra in burst
    pool_pre_ping=True,    # Verify connection is alive before using
)

@contextmanager
def get_db_connection():
    """Usage: with get_db_connection() as conn: ..."""
    with engine.connect() as conn:
        yield conn         # conn is available inside the `with` block
        # Auto-commits and auto-closes when block exits
```

**Design decision:** Why `engine.connect()` instead of `Session`?
- SQLAlchemy sessions track object state (ORM pattern)
- This project uses raw SQL (text queries) — sessions add overhead without benefit
- `engine.connect()` is simpler and more efficient for raw SQL workloads

### Conversation Context for LLM Memory

```python
def get_conversation_context(conversation_id: str, n: int = 6) -> str:
    """Get last N message turns and format as memory string for LLM."""
    with get_db_connection() as conn:
        rows = conn.execute(text("""
            SELECT role, content FROM messages
            WHERE conversation_id = :conv_id
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"conv_id": conversation_id, "limit": n * 2}).fetchall()

    # Reverse to get chronological order (we fetched DESC)
    rows = list(reversed(rows))

    # Format as: "User: ...\nAssistant: ...\nUser: ..."
    return "\n".join(f"{row.role.capitalize()}: {row.content}" for row in rows)
```

---

## Module 8: `core/document_store.py` — PDF Upload Pipeline

### PDF Processing Pipeline

```python
def ingest_document(
    file_bytes: bytes,
    filename: str,
    user_id: str,
    conversation_id: str
) -> str:
    """Full pipeline: validate → extract → chunk → embed → store"""

    # Step 1: Validate file type and size
    if len(file_bytes) > MAX_FILE_BYTES:  # 10MB limit
        raise ValueError("File too large")

    # Step 2: Extract text (pdfplumber primary, PyPDF2 fallback)
    text = extract_pdf_text(file_bytes)
    if not text.strip():
        raise ValueError("Could not extract text from PDF")

    # Step 3: Verify it's financial content (LLM-based classifier)
    if not is_financial_document(text[:2000]):
        raise NonFinancialDocumentError("Upload only financial documents")

    # Step 4: Encrypt raw content
    encrypted_content = encrypt_content(file_bytes)

    # Step 5: Save metadata to PostgreSQL
    doc_id = str(uuid.uuid4())
    save_document_record(doc_id, user_id, conversation_id, filename, encrypted_content)

    # Step 6: Chunk the text
    chunks = chunk_text(text, chunk_size=800, overlap=100)

    # Step 7: Embed each chunk + store in Neo4j as PersonalChunk nodes
    embedder = get_embedder()
    embeddings = embedder.embed_documents(chunks)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        kg.query("""
            CREATE (n:PersonalChunk {
                document_id: $doc_id,
                user_id: $user_id,
                conversation_id: $conv_id,
                content: $content,
                embedding: $embedding,
                chunk_index: $idx
            })
        """, params={...})

    return doc_id
```

---

## Module 9: `core/circuit_breaker.py`

### States and Transitions

```python
class CircuitBreaker:
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking all requests (fast fail)
    HALF_OPEN = "half_open" # Testing if service recovered

    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == self.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN
            else:
                raise Exception("Circuit OPEN — service unavailable")

        try:
            result = func(*args, **kwargs)
            # Success — reset
            if self.state == self.HALF_OPEN:
                self.state = self.CLOSED
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = self.OPEN
            raise
```

---

## Module 10: Frontend — `AuthContext.tsx`

### React Context Pattern

```tsx
// 1. Create the context with type
interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (token: string, user: User) => void;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

// 2. Create the Provider (wraps the entire app)
export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);

    // Rehydrate from localStorage on page load
    useEffect(() => {
        const savedToken = localStorage.getItem("token");
        const savedUser = localStorage.getItem("user");
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
    }, []);

    const login = (newToken: string, newUser: User) => {
        setToken(newToken);
        setUser(newUser);
        localStorage.setItem("token", newToken);    // Persist
        localStorage.setItem("user", JSON.stringify(newUser));
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

// 3. Custom hook for easy access
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
}

// 4. Usage in any component:
function ChatComponent() {
    const { token, user, logout } = useAuth();
    // token is automatically available — no prop drilling
}
```

---

## Common Code Patterns Across the Project

### Pattern 1: State Spreading in Nodes
```python
# Every node returns: {**state, "new_field": new_value}
# This creates a NEW dict with all old fields + the updated one
# Old fields are NOT lost

def my_node(state: AgentState) -> AgentState:
    result = compute_something(state["input"])
    return {**state, "output": result}  # All original state preserved
```

### Pattern 2: .get() for Optional State Fields
```python
# Safe access — returns None if field doesn't exist yet
doc_id = state.get("document_id")       # None if not set
retries = state.get("retrieval_retries", 0)  # 0 if not set
```

### Pattern 3: Structured LLM Output
```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    decision: str
    confidence: float

llm = get_structured_fast_chat(MyOutput)
result: MyOutput = llm.invoke(prompt)
# result.decision → always a valid string
# result.confidence → always a float
# No JSON parsing, no if/else checks on raw string output
```

### Pattern 4: FastAPI Dependency for Auth
```python
# Once defined, reuse everywhere:
@app.post("/any-protected-endpoint")
async def endpoint(current_user = Depends(get_current_user)):
    user_id = current_user["id"]
    # FastAPI automatically runs get_current_user() before this function
    # If token is invalid → 401 is raised automatically, this function never runs
```
