# 📋 01 — Project Overview

## What Is This Project?

**FinAdvisor Voice** is an AI-powered financial advisor application. Think of it as a smart chatbot that can answer questions like:

- _"What was Reliance's revenue in FY2024?"_
- _"Calculate my SIP returns if I invest ₹5000/month at 12% for 10 years"_
- _"What is the latest news about Nifty?"_
- _"Summarize this PDF annual report I just uploaded"_
- _"What are the tax brackets in India for FY2025?"_

It is NOT just a chatbot — it searches through actual financial documents (stored in a graph database), fetches live market data, runs math calculations, and answers using an AI language model.

---

## Who Built It and With What?

Built with the **Hybrid Graph-RAG** approach:
- **RAG** = Retrieval-Augmented Generation (search documents first, then generate an answer)
- **Graph** = Uses Neo4j graph database to store relationships between financial entities
- **Hybrid** = Combines semantic (vector) search + keyword (graph) search + RRF fusion

---

## What Does It Actually Do? (Feature List)

### User-Facing Features
| Feature | How It Works |
|---|---|
| 🔐 **OTP Registration** | Email OTP → verify → register account |
| 💬 **Chat with AI** | Type a question → AI searches docs → answers in Markdown |
| 🎙️ **Voice Input** | Speak your question → browser transcribes → sends to AI |
| 📂 **Upload PDF** | Upload your own annual report → AI reads & answers from it |
| 🗂️ **Conversation History** | All chats saved to PostgreSQL, browsable in sidebar |
| 🔄 **Streaming Response** | Answers stream word-by-word (like ChatGPT) |

### AI Capabilities
| Capability | Example Query |
|---|---|
| Financial Document QA | "What was TCS revenue in Q3 FY24?" |
| Live Market Data | "What is Infosys stock price right now?" |
| News Retrieval | "Latest news about RBI rate hike?" |
| Math Calculation | "What is 15% of 45,000?" |
| SIP/Tax Calculation | "Calculate my SIP returns" |
| Personal PDF QA | "Summarize section 3 of the uploaded PDF" |
| Conversational Memory | "Tell me more about it" (remembers context) |

---

## Technology Stack (Complete)

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Python web framework, REST API server |
| **LangGraph** | Orchestrates the AI agent as a state machine graph |
| **LangChain** | Connects LLMs, tools, prompts, embeddings |
| **Groq API** | Primary LLM inference: `qwen/qwen3.8-27b` (fast router/verifier) and `openai/gpt-oss-120b` (high-capacity synthesis) |
| **OpenRouter** | Zero-Data-Retention (ZDR) fallback LLM (`mistralai/mistral-small-24b-instruct-2501`) with `data_collection='deny'` |
| **Google Gemini** | Public fallback LLM (`gemini-3.5-flash-lite`) and hosted vector embeddings (`models/gemini-embedding-001`, 768-dim $L_2$ normalized) |
| **Neo4j (Aura)** | Hosted Graph Database: stores financial knowledge, entities, relationships, Lucene fulltext keyword indexes (`keyword_markdown`), and vector index (`vector_markdown_v2`) |
| **PostgreSQL (Neon)** | Relational DB: users, conversations, messages, OTP records, personal document metadata |
| **Zero-RAM Strategy** | In-process ONNX/PyTorch models replaced with hosted APIs (`RERANKER_PROVIDER=none`, `VECTOR_SEARCH_ENABLED=false` until $\ge 99\%$ migration) |
| **yfinance** | Real-time Indian stock market prices (NSE/BSE tickers) & mutual fund NAV snapshots |
| **pdfplumber / PyPDF2** | Extract text from user-uploaded PDFs |
| **bcrypt** | Password hashing (salt rounds) |
| **python-jose** | JWT token creation and validation |
| **Brevo / SMTP** | Email OTP delivery |
| **Fernet (cryptography)** | AES-128 symmetric encryption for user-uploaded personal document content |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **TypeScript** | Type-safe JavaScript |
| **Vite 8** | Build tool + dev server |
| **Tailwind CSS v4** | Styling |
| **Lucide React** | Icons |
| **react-markdown** | Render AI responses as formatted Markdown |

### Infrastructure
| Tool | Purpose |
|---|---|
| **Docker** | Containerize the app |
| **Vercel** | Deploy frontend |
| **Render** | Deploy backend |
| **LangSmith** | Observability/tracing for LLM calls |

---

## End-to-End Workflow (Simple Version)

```
User Types: "What was Reliance revenue FY2024?"
        │
        ▼
[React Frontend]
  → Sends POST /api/chat with message + JWT token
        │
        ▼
[FastAPI Backend]
  → Validates JWT (who is this user?)
  → Checks rate limit (too many requests?)
  → Checks cache (did we answer this before?)
        │
        ▼
[LangGraph Agent]
  → Router decides: "This needs document search"
  → Retriever fetches top chunks from Neo4j (vector + graph)
  → RRF Fusion merges and ranks results
  → Evidence Builder synthesizes an answer using LLM
  → Verifier checks the answer quality
        │
        ▼
[FastAPI Backend]
  → Saves message to PostgreSQL
  → Streams answer back to frontend
        │
        ▼
[React Frontend]
  → Renders answer as Markdown
  → Saves conversation in sidebar
```

---

## What Makes It Special vs. a Simple Chatbot?

| Simple Chatbot | This Project |
|---|---|
| Just calls GPT/Gemini API | Uses a multi-node AI agent graph (LangGraph) |
| No documents | Searches Neo4j graph + vector index |
| Generic answers | Grounded in real financial data (10-K filings) |
| No memory | PostgreSQL-backed conversation memory |
| No verification | Verifier node checks answer quality + retries |
| No live data | Fetches real-time stock prices via yfinance |
| No math | Dedicated math solver and calculation nodes |
| No user accounts | Full OTP registration + JWT auth system |

---

## Project Stats (Actual Files)

| Area | Files | Total Size |
|---|---|---|
| Backend core | 12 files in `/core` | ~150KB |
| AI Agent nodes | 9 files in `/nodes` | ~80KB |
| Retrieval | 3 files in `/retrieval` | ~20KB |
| Graph definition | 2 files in `/graph` | ~6KB |
| Financial tools | 4 files in `/financial` | ~40KB |
| Math/Calculator tools | 5 files in `/tools` | ~45KB |
| Frontend | ~10 files in `/frontend/src` | ~125KB |
| Tests | Multiple files in `/tests` | Various |
| Main API entry | `main.py` | ~40KB, 994 lines |
