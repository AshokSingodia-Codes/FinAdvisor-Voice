import os
from dotenv import load_dotenv

# Set memory-efficient thread configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from config.settings import settings
from core.cache import get_cached_embedding, set_cached_embedding

# LangChain fallback environment variables
if settings.NEO4J_URI:
    os.environ["NEO4J_URI"] = settings.NEO4J_URI
if settings.NEO4J_USERNAME:
    os.environ["NEO4J_USERNAME"] = settings.NEO4J_USERNAME
if settings.NEO4J_PASSWORD:
    os.environ["NEO4J_PASSWORD"] = settings.NEO4J_PASSWORD
if settings.GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.embeddings import Embeddings

# ==============================================================================
# Dual-Tier LLM Architecture:
# 1. Fast Chain (fast_chat / fast_structured_chat):
#    Dedicated to Router, Decomposer, Verifier, and Eval Judge.
#    Order: Small/Fast model (Groq Qwen-3.8-27B / OpenRouter DeepSeek/Gemini) -> Fast Fallback.
#    NO 72B model in this chain to keep latency ultra-low (<500ms).
#
# 2. Synthesis Chain (synthesis_chat / chat):
#    Dedicated to Evidence Builder and complex advisory synthesis.
#    Order: OpenRouter Qwen 2.5 72B -> DeepSeek -> Gemini -> Groq.
# ==============================================================================

# --- A. Fast Chain Setup (Sub-second classification & extraction) ---
fast_primary = None
fast_fallbacks = []

if settings.GROQ_API_KEY:
    fast_primary = ChatGroq(
        temperature=0,
        model_name="openai/gpt-oss-20b",
        max_tokens=400,
        max_retries=2,
        api_key=settings.GROQ_API_KEY,
        timeout=6,
    )
    fast_fallbacks.append(ChatGroq(
        temperature=0,
        model_name="qwen/qwen3.8-27b",
        max_tokens=400,
        max_retries=2,
        api_key=settings.GROQ_API_KEY,
        timeout=6,
    ))

if settings.OPENROUTER_API_KEY:
    or_fast = ChatOpenAI(
        model="mistralai/mistral-small-24b-instruct-2501",
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=400,
        temperature=0,
        max_retries=0,
        timeout=6,
    )
    if not fast_primary:
        fast_primary = or_fast
    else:
        fast_fallbacks.append(or_fast)

    fast_fallbacks.append(ChatOpenAI(
        model="deepseek/deepseek-chat",
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=400,
        temperature=0,
        max_retries=0,
        timeout=6,
    ))

if not fast_primary:
    fast_primary = ChatGroq(temperature=0, model_name="dummy", api_key="dummy")

fast_chat = fast_primary.with_fallbacks(fast_fallbacks) if fast_fallbacks else fast_primary


def get_structured_fast_chat(schema, **kwargs):
    primary_structured = fast_primary.with_structured_output(schema, **kwargs)
    if fast_fallbacks:
        fallback_structured = [f.with_structured_output(schema, **kwargs) for f in fast_fallbacks]
        return primary_structured.with_fallbacks(fallback_structured)
    return primary_structured


# --- B. Synthesis Chain Setup ---
synthesis_primary = None
synthesis_fallbacks = []

if settings.GROQ_API_KEY:
    synthesis_primary = ChatGroq(
        temperature=0,
        model_name="openai/gpt-oss-120b",
        max_tokens=1000,
        max_retries=2,
        api_key=settings.GROQ_API_KEY,
        timeout=8,
    )
    synthesis_fallbacks.append(ChatGroq(
        temperature=0,
        model_name="openai/gpt-oss-20b",
        max_tokens=1000,
        max_retries=2,
        api_key=settings.GROQ_API_KEY,
        timeout=8,
    ))
    synthesis_fallbacks.append(ChatGroq(
        temperature=0,
        model_name="qwen/qwen3.8-27b",
        max_tokens=1000,
        max_retries=2,
        api_key=settings.GROQ_API_KEY,
        timeout=8,
    ))

if settings.OPENROUTER_API_KEY:
    or_synth = ChatOpenAI(
        model="qwen/qwen-2.5-72b-instruct",
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=1000,
        temperature=0,
        max_retries=0,
        timeout=12,
    )
    if not synthesis_primary:
        synthesis_primary = or_synth
    else:
        synthesis_fallbacks.append(or_synth)

    synthesis_fallbacks.append(ChatOpenAI(
        model="deepseek/deepseek-chat",
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=1000,
        temperature=0,
        max_retries=0,
        timeout=10,
    ))

if not synthesis_primary:
    synthesis_primary = fast_primary

synthesis_chat = synthesis_primary.with_fallbacks(synthesis_fallbacks) if synthesis_fallbacks else synthesis_primary

def get_structured_synthesis_chat(schema, **kwargs):
    primary_structured = synthesis_primary.with_structured_output(schema, **kwargs)
    if synthesis_fallbacks:
        fallback_structured = [f.with_structured_output(schema, **kwargs) for f in synthesis_fallbacks]
        return primary_structured.with_fallbacks(fallback_structured)
    return primary_structured

# Backwards compatibility aliases
chat = synthesis_chat
get_structured_chat = get_structured_synthesis_chat


# --- C. Ultra-lightweight ONNX-based FastEmbed Wrapper with Vector Caching ---
class FastEmbedWrapper(Embeddings):
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed_documents(self, texts):
        model = self._get_model()
        return [list(emb) for emb in model.embed(texts)]

    def embed_query(self, text):
        cached = get_cached_embedding(text)
        if cached is not None:
            return cached
        model = self._get_model()
        emb = list(next(model.embed([text])))
        set_cached_embedding(text, emb)
        return emb


# --- D. Lazy Proxy helper to defer heavy memory allocations ---
class LazyProxy:
    def __init__(self, init_fn):
        self._init_fn = init_fn
        self._obj = None
        self._attempted = False

    def _get_obj(self):
        if self._obj is None:
            self._obj = self._init_fn()
        return self._obj

    def __getattr__(self, name):
        obj = self._get_obj()
        if obj is None:
            raise RuntimeError("Database component is not initialized.")
        return getattr(obj, name)

    def __bool__(self):
        return self._get_obj() is not None


def init_kg():
    try:
        from langchain_neo4j import Neo4jGraph
        if not settings.NEO4J_URI:
            print("🚨 [NEO4J ERROR] NEO4J_URI is not set in environment!")
            return None
        return Neo4jGraph(
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_USERNAME
        )
    except Exception as e:
        print(f"\n🚨 [NEO4J UNREACHABLE] Could not connect to Neo4j database ({settings.NEO4J_URI}): {e}\n"
              f"   👉 Check if your Neo4j Aura instance is PAUSED in the Aura console or if credentials in .env are correct.\n")
        return None

class CachedHuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        from langchain_huggingface import HuggingFaceEmbeddings
        self._hf = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False}
        )

    def embed_documents(self, texts):
        return self._hf.embed_documents(texts)

    def embed_query(self, text):
        cached = get_cached_embedding(text)
        if cached is not None and len(cached) == 768:
            return cached
        emb = self._hf.embed_query(text)
        set_cached_embedding(text, emb)
        return emb

_cached_embeddings = None
def init_hf():
    global _cached_embeddings
    if _cached_embeddings is not None:
        return _cached_embeddings
    try:
        _cached_embeddings = CachedHuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        return _cached_embeddings
    except Exception as e:
        print(f"🚨 [EMBEDDINGS ERROR] Embeddings initialization failed: {e}")
        return None

# Export FastEmbed ONNX wrapper instance
fast_embeddings = FastEmbedWrapper(model_name="BAAI/bge-small-en-v1.5")

def init_vector_index():
    try:
        from langchain_neo4j import Neo4jVector
        curr_hf = init_hf()
        if not curr_hf or not settings.NEO4J_URI:
            return None
        return Neo4jVector.from_existing_index(
            curr_hf,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            index_name=settings.VECTOR_INDEX_NAME,
            keyword_index_name=settings.KEYWORD_INDEX_NAME,
            search_type="hybrid",
            database=settings.NEO4J_USERNAME
        )
    except Exception as e:
        print(f"\n🚨 [NEO4J VECTOR INDEX UNREACHABLE] Failed to initialize Neo4jVector ({settings.NEO4J_URI}): {e}\n")
        return None

# Lazy proxy instances
kg = LazyProxy(init_kg)
hf = LazyProxy(init_hf)
vector_index = LazyProxy(init_vector_index)
