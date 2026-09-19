import os
from dotenv import load_dotenv

# Set memory-efficient thread configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from config.settings import settings

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

# Shared LLM (Groq primary with smart fallbacks)
primary_chat = ChatGroq(
    temperature=0, 
    model_name=settings.GROQ_MODEL, 
    max_tokens=600,
    max_retries=3,
    api_key=settings.GROQ_API_KEY if settings.GROQ_API_KEY else "dummy_key_for_boot"
)

fallbacks = []

if settings.GITHUB_API_KEY:
    fallbacks.append(ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.GITHUB_API_KEY,
        base_url="https://models.github.ai/inference"
    ))

if settings.OPENROUTER_API_KEY:
    fallbacks.append(ChatOpenAI(
        model="meta-llama/llama-3-8b-instruct:free",
        temperature=0,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    ))

if settings.GOOGLE_API_KEY:
    fallbacks.append(ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    ))

if fallbacks:
    chat = primary_chat.with_fallbacks(fallbacks)
else:
    chat = primary_chat

def get_structured_chat(schema, **kwargs):
    primary_structured = primary_chat.with_structured_output(schema, **kwargs)
    if fallbacks:
        fallback_structured = [f.with_structured_output(schema, **kwargs) for f in fallbacks]
        return primary_structured.with_fallbacks(fallback_structured)
    return primary_structured

# Ultra-lightweight ONNX-based FastEmbed Wrapper (<25MB RAM vs 500MB PyTorch)
class FastEmbedWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
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
        model = self._get_model()
        return list(next(model.embed([text])))

# Lazy Proxy helper to defer heavy memory allocations and connections
class LazyProxy:
    def __init__(self, init_fn):
        self._init_fn = init_fn
        self._obj = None

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
            return None
        return Neo4jGraph(
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_USERNAME
        )
    except Exception as e:
        print(f"Warning: Neo4j connection initialization deferred/failed: {e}")
        return None

def init_hf():
    try:
        # FastEmbed uses ONNX runtime (~25MB RAM) with ZERO PyTorch overhead
        return FastEmbedWrapper(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Warning: Embeddings initialization deferred/failed: {e}")
        return None

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
        print(f"Warning: Neo4jVector initialization deferred/failed: {e}")
        return None

# Lazy proxy instances
kg = LazyProxy(init_kg)
hf = LazyProxy(init_hf)
vector_index = LazyProxy(init_vector_index)
