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
| **Groq API** | Primary LLM inference (fast, cheap) |
| **OpenRouter** | Fallback LLM provider |
| **Google Gemini** | Second fallback LLM |
| **Neo4j (Aura)** | Graph database: stores financial knowledge + vector index |
| **PostgreSQL (Neon)** | Relational DB: users, conversations, messages, OTPs |
| **FastEmbed (BAAI/bge-small)** | ONNX-based embedding model (lightweight, no GPU) |
| **FlashRank** | Cross-encoder reranker for retrieved chunks |
| **yfinance** | Live stock market data (Yahoo Finance) |
| **pdfplumber / PyPDF2** | Extract text from uploaded PDFs |
| **bcrypt** | Password hashing |
| **python-jose** | JWT token creation and validation |
| **Brevo / SMTP** | Email OTP delivery |
| **Fernet (cryptography)** | AES-128 encryption for uploaded document content |

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
