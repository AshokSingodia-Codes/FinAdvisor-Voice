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
        from langchain_huggingface import HuggingFaceEmbeddings
        # Use lightweight MiniLM (80MB) instead of heavy mpnet (450MB) to stay well under 512MB RAM
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
    except Exception as e:
        print(f"Warning: HuggingFaceEmbeddings initialization deferred/failed: {e}")
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

# Lazy proxy instances that won't allocate 500MB on app startup
kg = LazyProxy(init_kg)
hf = LazyProxy(init_hf)
vector_index = LazyProxy(init_vector_index)
