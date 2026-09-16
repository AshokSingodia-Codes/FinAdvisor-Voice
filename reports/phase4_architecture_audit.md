# Architecture Audit: Phase 4 Preparation

## Current Architecture Overview
The current system successfully implements an Agentic Hybrid Graph RAG architecture built around Neo4j, Gemini 3.6 Flash, and LangGraph.

### Existing Components & Modularity
- **UI Layer (`app.py`)**: A Streamlit application that interfaces with the underlying LangGraph agent (`app_graph`).
- **Core Connections (`core/db.py`)**: Centralized initialization of the Gemini LLM (`ChatGoogleGenerativeAI`), Neo4j vector store, Neo4j graph connection, and HuggingFace local embeddings.
- **Retrieval Engine (`retrieval/`)**:
  - `hybrid_rrf.py`: Implements mathematically sound Reciprocal Rank Fusion (RRF) to merge vector and structured graph search results.
  - `reranker.py`: Employs a local, ultra-lightweight Cross-Encoder (`FlashRank` / `ms-marco-MiniLM-L-12-v2`) to filter down the top RRF results.
- **Agentic LangGraph Logic (`graph/` & `nodes/`)**:
  - `graph/state.py`: Defines the strictly typed `AgentState` containing the query, context, drafts, decisions, and verification results.
  - `nodes/router.py`: LLM-based structured output routing (e.g., hybrid_search, direct_answer, decompose).
  - `nodes/decomposition.py`: Breaks complex queries into parallel sub-queries.
  - `nodes/retriever.py`: Maps sub-queries to the hybrid RRF+Reranker pipeline.
  - `nodes/evidence_builder.py`: Drafts preliminary answers strictly grounded in context.
  - `nodes/verifier.py`: Self-RAG verification engine that prevents hallucinated or unsupported answers.
  - `graph/workflow.py`: The `StateGraph` that orchestrates the flow with conditional edges (including iterative retrieval loops if verification fails).

### Current Data Ingestion
- `hybrid_graph_rag.py` / `hybrid_graph_rag.ipynb`: The original prototype scripts.
- `rebuild_vector_db_plumber.py`: The active ingestion script using `PDFPlumberLoader` to push chunks into the `vector_markdown` index and `keyword_markdown` index in Neo4j.

### Known Technical Debt & Missing Components
- **Configuration**: Hardcoded environmental variable extraction in `db.py` rather than a centralized, validated `config/settings.py` structure (e.g. using `pydantic-settings`).
- **Observability**: Tracing is heavily reliant on manual print statements. LangSmith is installed but not fully configured with run names or robust environmental keys.
- **Evaluation**: Zero automated evaluation infrastructure. Quality is measured heuristically.
- **Financial Table Reasoning**: Ingestion relies on text-splitting. While `PDFPlumber` handles tables better than standard loaders, the system lacks a deterministic Table Parser object to preserve complex column/row hierarchies and perform math.
- **Provenance**: Currently lacks strict tracking of page numbers, section headers, and document names throughout the LangGraph context list.
- **API/Production Layer**: No FastAPI wrapper, Redis caching, JWT auth, or Docker containerization.

## Data Flow
User Query -> Streamlit UI -> LangGraph Orchestrator (Router -> Decomposition? -> Multi-Retrieval -> RRF -> Reranking -> Evidence Builder -> Verifier -> Conditional Loop -> Final Answer) -> Streamlit UI.
