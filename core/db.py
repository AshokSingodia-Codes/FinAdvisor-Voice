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
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

# Shared LLM (Groq Llama-3 70B)
chat = ChatGroq(
    temperature=0, 
    model_name=settings.GROQ_MODEL, 
    api_key=settings.GROQ_API_KEY,
    max_retries=6
)

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
