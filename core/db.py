import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import settings

# LangChain fallback
os.environ["NEO4J_URI"] = settings.NEO4J_URI
os.environ["NEO4J_USERNAME"] = settings.NEO4J_USERNAME
os.environ["NEO4J_PASSWORD"] = settings.NEO4J_PASSWORD
if settings.GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

# Shared LLM (Groq)
from langchain_openai import ChatOpenAI

primary_chat = ChatGroq(
    temperature=0, 
    model_name=settings.GROQ_MODEL, 
    max_tokens=600,
    max_retries=3
)

fallbacks = []

from langchain_google_genai import ChatGoogleGenerativeAI

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

from langchain_core.runnables import Runnable

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

# Neo4j Graph Connection
kg = Neo4jGraph(
    url=settings.NEO4J_URI,
    username=settings.NEO4J_USERNAME,
    password=settings.NEO4J_PASSWORD,
    database=settings.NEO4J_USERNAME
)

# HuggingFace Embeddings (Local)
hf = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

# Vector Index Connection
vector_index = Neo4jVector.from_existing_index(
    hf,
    url=settings.NEO4J_URI,
    username=settings.NEO4J_USERNAME,
    password=settings.NEO4J_PASSWORD,
    index_name=settings.VECTOR_INDEX_NAME,
    keyword_index_name=settings.KEYWORD_INDEX_NAME,
    search_type="hybrid",
    database=settings.NEO4J_USERNAME
)
