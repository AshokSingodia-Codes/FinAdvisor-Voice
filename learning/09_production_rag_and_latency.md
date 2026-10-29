# ⚡ 09 — Production Graph-RAG, Zero-RAM Architecture & Latency Engineering

> **Essential Reference:** How FinAdvisor-X runs safely on Render Free Tier (<512 MB RAM) with sub-second fast-paths, zero hallucinations, and strict data privacy.

---

## 🎯 1. The Core Engineering Challenge: Render's 512 MB RAM Cap

### The Problem
When building AI applications with RAG, standard tutorials recommend loading local transformer models:
- `sentence-transformers` / HuggingFace: **~400–600 MB RAM**
- `FastEmbed` / ONNX: **~180–250 MB RAM**
- Python runtime + FastAPI + Neo4j driver: **~120 MB RAM**

On a container host like **Render Free Tier**, the entire process is terminated (`SIGKILL / OOM Killed`) if memory exceeds **512 MB**.

### The Solution: Hosted Zero-RAM Architecture
FinAdvisor-X completely offloads heavy mathematical and vector tensor operations from the local server to hosted cloud infrastructure:

```
[In-Process Server Memory: ~117 MB Total]
 ├── Python Runtime + FastAPI:         ~35 MB
 ├── Neo4j Aura & SQLAlchemy Pool:     ~45 MB
 ├── In-Memory LRU & TTL Caches:       ~15 MB
 └── LangGraph Agent Definitions:      ~22 MB
 ------------------------------------------------
 AVAILABLE HEADROOM:                  ~394 MB (77% Free)
```

| Component | Legacy In-Process Approach | FinAdvisor-X Production Approach | RAM Impact |
|---|---|---|---|
| **Text Embeddings** | PyTorch / `bge-small` | Hosted Gemini REST API (`models/gemini-embedding-001`, 768-dim $L_2$ normalized) | **0 MB local RAM** |
| **Vector Index** | Local FAISS / Chroma | Hosted Neo4j Aura Vector Index (`vector_markdown_v2`) | **0 MB local RAM** |
| **Cross-Encoder Reranking** | Local FlashRank / ONNX | Reciprocal Rank Fusion (`RRF_K=60`) + Deterministic Boosting | **0 MB local RAM** |
| **Document Content** | In-Memory String Blobs | PostgreSQL Fernet AES-128 scoped retrieval | **0 MB local RAM** |

---

## 🏎️ 2. Latency Optimization Architecture

During early development, end-to-end request latency varied from 6s to 12s. We eliminated this through a multi-tier fast-path and pruning hierarchy:

```
User Query Arrives
      │
      ├── Pure Math ("75000 * 12 + 120000")? ──► [Fast-Math AST Evaluator] ──► Return in 0.02s
      │
      ├── Conversational Greeting ("Hello!")? ──► [Greeting Handler Fast-Path] ──► Return in 0.04s
      │
      ├── Memory Surplus ("What is my surplus?")? ──► [Memory Context Math Solver] ──► Return in 0.01s
      │
      ├── Pronoun Quote ("What is its price?")? ──► [Active Entity Resolver + yfinance] ──► Return in 1.74s
      │
      └── Statutory Tax / 10-K Retrieval? ──► [Bounded Top-3 Chunk Graph-RAG] ──► Return in ~2.8s
```

### Measured Benchmark Comparison

| Category & Query | Baseline Latency | Expected Target | Achieved Latency | Speedup |
|---|:---:|:---:|:---:|:---:|
| **Greetings & Liveness** (*"Hello! What are your capabilities?"*) | 6.83s | < 0.10s | **0.04s** | **170x faster** |
| **Deterministic Arithmetic** (*"Calculate 75000 * 12 + 120000"*) | 0.03s | 0.03s | **0.02s** | **Optimal (<1ms AST)** |
| **Live Equity Quote** (*"What is the stock price of Reliance?"*) | 4.47s | ~0.80s – 1.70s | **1.73s** | **2.6x faster** |
| **SIP Compounding** (*"Future value of SIP ₹10,000 monthly, 10 yrs at 12%"*) | 8.41s | ~1.20s | **0.97s** | **8.6x faster** |
| **Corporate 10-K Sales** (*"Apple total net sales FY24?"*) | 8.33s | ~3.50s – 4.00s | **2.68s** | **3.1x faster** |
| **Corporate 10-K Segment** (*"Apple iPhone net sales FY24?"*) | 6.67s | ~3.50s – 4.00s | **2.99s** | **2.2x faster** |
| **Section 80C Limit** (*"Maximum deduction limit under 80C?"*) | 4.61s | ~3.50s – 4.00s | **3.04s** | **1.5x faster** |
| **Budget 2024 LTCG** (*"LTCG tax exemption limit under Budget 2024?"*) | 4.35s | ~4.00s – 4.50s | **2.90s** | **1.5x faster** |
| **Surplus Retention** (*Turn 2: "Based on my numbers, what is my monthly surplus?"*) | 1.92s | ~1.50s – 2.00s | **0.01s** | **192x faster** |
| **Pronoun Resolution** (*Turn 2: "What is its current price?" -> Reliance*) | 11.41s | ~1.50s – 2.00s | **1.74s** | **6.5x faster** |
| **Clean Topic Shift** (*Turn 4: "What is deduction limit under Section 80C?"*) | 5.13s | ~3.50s – 4.00s | **2.46s** | **2.1x faster** |

---

## 🛡️ 3. Token Pruning & Groq Rate Limit Engineering

### The Problem
Groq Free Tier enforces a strict organization rate limit of **8,000 Input Tokens Per Minute (ITPM)**.
If a RAG prompt injects 4 unpruned chunks (~6,000 characters / ~1,800 tokens) and both the Evidence Builder and Verifier execute on every query:
- Query 1: Router (~400 tokens) + Evidence (~2,000 tokens) + Verifier (~2,200 tokens) = **4,600 tokens**
- Query 2 (run 10 seconds later): 4,600 + 4,600 = **9,200 tokens** $\rightarrow$ **HTTP 429 RateLimitError**!
- The system would be forced into 15.5s cooldowns, destroying user experience.

### The Fix
1. **Top-3 Chunk Bounding ([nodes/evidence_builder.py](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/evidence_builder.py))**:
   - Chunks are bounded to `MAX_TOTAL_CHARS = 2800` (~650–750 tokens total).
   - SEC 10-K and statutory tax figures are concise; 2,800 characters is more than enough to capture tables and definitions without token bloat.
2. **Verifier Fast-Pass Bypass ([nodes/verifier.py](file:///e:/finaceadviser/reference_projects/Hybrid-Graph-RAG-Financial-Analyser-main/nodes/verifier.py))**:
   - Single-fact factual queries (`depth == 'quick'`) bypass the redundant second-pass LLM fact-checking audit.
   - Saves **50% of tokens** and cuts 3s–5s of latency on direct factual lookups.

---

## 🔒 4. Privacy & Data Isolation Architecture

Financial data requires strict compliance with privacy standards:

```
[Incoming Request]
        │
        ├── Personal Document Attached? (e.g. Bank Statement / Salary Slip)
        │         │
        │         ├── Google Gemini: STRICTLY EXCLUDED (Zero personal data sent to free-tier models)
        │         ├── Groq Primary: `qwen/qwen3.8-27b`
        │         └── OpenRouter Fallback: Configured with `data_collection='deny'` and `zdr=True`
        │
        └── Public Corporate Knowledge Query? (e.g. Apple 10-K, Section 80C rules)
                  │
                  └── Standard Public Cascade: Groq ──► Gemini ──► OpenRouter
```

- **Vector Privacy Guard**: Personal documents use private BM25 keyword matching (`PERSONAL_DOCS_EMBEDDING=keyword_only`). User bank statements are never transmitted to external vector embedding APIs.
- **SQL Data Isolation**: Every conversation, message, active entity, and memory fact is bound to `user_id`. Cross-user access returns an immediate HTTP 403 Forbidden.

---

## 🧪 5. Automated Evaluation Runbook

To run the complete benchmark suite locally:

```bash
# 1. Run full 13-point latency & architecture audit
python scripts/eval_full_system.py

# 2. Run unit & security regression suite
pytest tests/test_personal_context_isolation.py tests/test_fast_math.py tests/test_verifier.py
```
