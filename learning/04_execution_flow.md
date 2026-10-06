# 🔄 04 — Execution Flow: Tracing a Real Request End-to-End

## Example Query: "What was TCS revenue in FY2024?"

We will trace this exact query from the moment the user types it to the moment the answer appears on screen.

---

## Step 1: User Types in Frontend (React)

**File:** `frontend/src/App.tsx`

```tsx
// User presses Enter or clicks Send
const handleSendMessage = async () => {
    const message = "What was TCS revenue in FY2024?";

    // Add user message to UI immediately (optimistic update)
    setMessages(prev => [...prev, { role: "user", content: message }]);

    // POST to backend
    const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`   // JWT from AuthContext
        },
        body: JSON.stringify({
            message: message,
            conversation_id: currentConversationId,
            stream: true
        })
    });

    // Handle streaming response
    const reader = response.body.getReader();
    // ... reads chunks and appends to message as they arrive
};
```

---

## Step 2: Request Hits FastAPI (Middleware Stack)

**File:** `main.py` (lines 126-132, then chat endpoint)

```
Request arrives at: POST /api/chat

1. CORSMiddleware:
   → Checks: Origin header = "http://localhost:5173"
   → Allow-Origin = "*" (configured) → PASS
   → Adds CORS response headers

2. JWT Auth Guard (get_current_user dependency):
   → Extracts "Bearer eyJ..." from Authorization header
   → Decodes JWT: jose.jwt.decode(token, secret, algorithms=["HS256"])
   → Extracts user_id from payload["sub"]
   → Looks up user in PostgreSQL
   → Attaches user object to request → PASS

3. Rate Limiter (chat_rate_limiter):
   → Checks: how many requests has user_id made in last 60 seconds?
   → Under limit → PASS
   → Over limit → raises HTTP 429
```

---

## Step 3: Chat Endpoint Logic Begins

**File:** `main.py` (the `/api/chat` endpoint)

```python
@app.post("/api/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    _: None = Depends(chat_rate_limiter)
):
    user_id = current_user["id"]
    message = "What was TCS revenue in FY2024?"

    # Step 3a: Get or create conversation
    conv_id = request.conversation_id or str(uuid.uuid4())
    # → queries PostgreSQL: SELECT * FROM conversations WHERE id = conv_id

    # Step 3b: Check greeting/chitchat shortcut
    if is_greeting_or_chitchat(message):
        return get_greeting_response(message)  # SHORTCUT - no LLM needed
    # "TCS revenue" is NOT a greeting → continue

    # Step 3c: Check fast math shortcut
    fast_result = try_evaluate_fast_math(message)
    if fast_result is not None:
        return fast_result   # SHORTCUT - no LLM needed
    # "TCS revenue" is NOT math → continue

    # Step 3d: Check response cache
    cache_key = f"{user_id}:{message}"
    cached = get_cached_response(cache_key)
    if cached:
        return cached   # CACHE HIT - no LangGraph needed
    # First time asking → CACHE MISS → continue

    # Step 3e: Load conversation memory
    memory_context = get_conversation_context(conv_id, n=6)
    # → SELECT last 6 messages FROM messages WHERE conversation_id = conv_id
    # → formats as: "User: ...\nAssistant: ..."

    # Step 3f: Invoke LangGraph
    initial_state = AgentState(
        original_question=message,
        current_question=message,
        conversation_id=conv_id,
        user_id=user_id,
        memory_context=memory_context,
        chat_history=[...],
        verifier_enabled=True,
    )
```

---

## Step 4: LangGraph Starts — Router Node

**File:** `nodes/router.py` → function `route_question(state)`

```python
def route_question(state: AgentState) -> AgentState:
    question = "What was TCS revenue in FY2024?"

    # 4a: Check router cache (TTL=600s)
    cached = _ROUTER_CACHE.get(question)
    if cached and (time.time() - cached[2]) < _ROUTER_CACHE_TTL:
        return {**state, "routing_decision": cached[0]}

    # 4b: Classify depth from keywords
    depth = classify_depth(question)  # → "quick" (no trigger words found)

    # 4c: Build prompt with conversation context
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a query router. Classify this query..."),
        ("human", "Question: {question}\nHistory: {history}")
    ])

    # 4d: Call fast_chat (Groq gpt-oss-20b, ~100ms)
    structured_llm = get_structured_fast_chat(Route)  # Returns a Route Pydantic object
    result: Route = structured_llm.invoke(prompt)

    # result.decision = "hybrid_search"
    # result.resolved_query = "What was TCS revenue in FY2024?" (already self-contained)

    # 4e: Cache the result
    _ROUTER_CACHE[question] = ("hybrid_search", depth, time.time())

    return {
        **state,
        "routing_decision": "hybrid_search",
        "depth": "quick",
        "resolved_query": "What was TCS revenue in FY2024?"
    }
```

---

## Step 5: Conditional Edge → Retriever Node

**File:** `graph/workflow.py`

```python
# The graph checks state["routing_decision"] = "hybrid_search"
# → routes to "retriever" node
```

**File:** `nodes/retriever.py` → function `retrieve_context(state)`

```python
def retrieve_context(state: AgentState) -> AgentState:
    query = "What was TCS revenue in FY2024?"
    document_id = state.get("document_id")  # None — no personal PDF

    if document_id:
        # Personal document path (NOT our case)
        results = get_personal_rrf_results(...)
    else:
        # Shared corpus path (OUR CASE)
        results = get_hybrid_rrf_results(
            query=query,
            vector_index=vector_store,       # Neo4j vector index
            graph_retriever_func=kg.query,   # Neo4j graph search
            top_k=10
        )

    return {**state, "retrieved_context": results}
```

---

## Step 6: Hybrid RRF Retrieval

**File:** `retrieval/hybrid_rrf.py`

```python
def get_hybrid_rrf_results(query, vector_index, graph_retriever_func, top_k=10):

    # Run BOTH searches IN PARALLEL using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Search 1: Neo4j Vector Index (semantic similarity)
        future_vector = executor.submit(
            vector_index.similarity_search,
            "What was TCS revenue in FY2024?",
            k=10
        )
        # Search 2: Neo4j Graph Search (keyword/entity)
        future_graph = executor.submit(
            graph_retriever_func,
            "What was TCS revenue in FY2024?"
        )

        # Wait for both (parallel, so only as slow as the slower one)
        vector_results = future_vector.result()
        # → [Document("TCS Q4FY24 revenue was ₹61,237 crore..."), ...]

        graph_results = future_graph.result()
        # → ["TCS reported ₹240,893 crore total revenue in FY24...", ...]

    # Apply RRF Fusion
    return reciprocal_rank_fusion([vector_results, graph_results])
    # → Merged and ranked list of text chunks
```

**RRF computation example:**

| Chunk | Vector Rank | Graph Rank | RRF Score | Final Rank |
|---|---|---|---|---|
| "TCS FY24 revenue ₹241K crore..." | 1 | 2 | 1/61 + 1/62 = 0.0326 | **1** |
| "TCS Q4 revenue ₹61K crore..." | 2 | 5 | 1/62 + 1/65 = 0.0315 | **2** |
| "Infosys FY24 revenue ₹153K crore" | 3 | 8 | 1/63 + 1/68 = 0.0306 | **3** |

---

## Step 7: Evidence Builder Node

**File:** `nodes/evidence_builder.py`

```python
def build_evidence(state: AgentState) -> AgentState:
    question = "What was TCS revenue in FY2024?"
    context_chunks = state["retrieved_context"]  # Top 10 chunks from RRF
    depth = state.get("depth", "quick")
    memory = state.get("memory_context", "")

    # Build prompt
    formatted_context = "\n\n".join(context_chunks[:5])  # Top 5 chunks

    prompt = f"""
    You are a financial advisor. Answer the user's question using ONLY the provided context.

    CONTEXT:
    {formatted_context}

    CONVERSATION HISTORY:
    {memory}

    QUESTION: {question}
    DEPTH: {depth}

    Provide a {'concise one-paragraph' if depth == 'quick' else 'detailed'} answer.
    """

    # Call synthesis_chat (Groq gpt-oss-120b — the big model)
    response = synthesis_chat.invoke(prompt)
    draft = response.content
    # → "TCS reported a total revenue of ₹2,40,893 crore in FY2024,
    #    representing a 6.2% year-on-year growth. Q4 FY24 revenue
    #    was ₹61,237 crore..."

    return {**state, "draft_answer": draft}
```

---

## Step 8: Verifier Node

**File:** `nodes/verifier.py`

```python
def verify_answer(state: AgentState) -> AgentState:
    question = state["current_question"]
    draft = state["draft_answer"]

    # Fast LLM to verify quality
    verdict = fast_chat.invoke(f"""
    Does this answer correctly address the question?
    Question: {question}
    Answer: {draft}
    Reply with just: PASS or FAIL
    """)

    passed = "PASS" in verdict.content.upper()
    # → "PASS"

    return {**state, "verification_passed": True, "final_answer": draft}
```

**Conditional edge:** `verification_passed=True` → go to END

---

## Step 9: Back in FastAPI — Save & Stream

**File:** `main.py`

```python
# LangGraph returned:
final_state = app_graph.invoke(initial_state)
answer = final_state["final_answer"]
# → "TCS reported a total revenue of ₹2,40,893 crore in FY2024..."

# Save to PostgreSQL
add_message(conv_id, "user", message)    # INSERT user message
add_message(conv_id, "assistant", answer) # INSERT AI answer

# Save to response cache (5-minute TTL)
set_cached_response(cache_key, answer)

# Auto-generate conversation title if first message
if is_first_message:
    title = message[:50]  # "What was TCS revenue in FY2024?"
    rename_conversation(conv_id, title)

# Stream response back to frontend
async def response_generator():
    words = answer.split(" ")
    for word in words:
        yield f"data: {word} \n\n"    # Server-Sent Events format
        await asyncio.sleep(0.02)    # simulate streaming

return StreamingResponse(response_generator(), media_type="text/event-stream")
```

---

## Step 10: Frontend Renders the Answer

**File:** `frontend/src/App.tsx`

```tsx
// SSE stream reader
const reader = response.body.getReader();
const decoder = new TextDecoder();
let accumulated = "";

while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    accumulated += chunk.replace("data: ", "");

    // Update message in real-time as words arrive
    setMessages(prev => prev.map((msg, i) =>
        i === prev.length - 1
            ? { ...msg, content: accumulated }
            : msg
    ));
}
```

**File:** `frontend/src/components/ChatMessageItem.tsx`

```tsx
// Renders the final accumulated text as Markdown
<ReactMarkdown remarkPlugins={[remarkGfm]}>
    {message.content}
</ReactMarkdown>
```

---

## Complete Timeline

```
t=0ms   User presses Enter
t=5ms   POST /api/chat arrives at FastAPI
t=8ms   CORS check passes
t=12ms  JWT decoded, user_id extracted
t=15ms  Rate limit checked (pass)
t=18ms  Cache check (miss)
t=25ms  PostgreSQL: load conversation history
t=30ms  LangGraph starts

t=30ms  Router node starts
t=130ms Groq gpt-oss-20b responds: "hybrid_search"
t=135ms Router node done

t=135ms Retriever node starts
t=135ms ThreadPoolExecutor spawns 2 threads:
  Thread A: Neo4j vector search
  Thread B: Neo4j graph search
t=280ms Both searches complete (parallel!)
t=290ms RRF fusion computed
t=295ms Retriever node done

t=295ms Evidence Builder starts
t=295ms Prompt constructed (~2000 tokens)
t=1800ms Groq gpt-oss-120b responds with full answer
t=1805ms Evidence Builder done

t=1805ms Verifier starts
t=1905ms Groq gpt-oss-20b: "PASS"
t=1910ms Verifier done — LangGraph ends

t=1910ms FastAPI saves messages to PostgreSQL
t=1920ms Streaming starts
t=2500ms Last word streamed to frontend
t=2500ms User sees full answer rendered in Markdown
```

**Total: ~2.5 seconds** for a complex financial retrieval query.
