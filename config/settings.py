from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Neo4j Settings
    AURA_INSTANCENAME: str = Field(..., description="Neo4j Aura Instance Name")
    NEO4J_URI: str = Field(..., description="Neo4j Connection URI")
    NEO4J_USERNAME: str = Field(..., description="Neo4j Username")
    NEO4J_PASSWORD: str = Field(..., description="Neo4j Password")
    
    GROQ_API_KEY: str = Field(..., description="Groq API Key")
    GROQ_MODEL: str = Field("qwen/qwen3.8-27b", description="Groq Model to use")
    GITHUB_API_KEY: Optional[str] = Field(None, description="GitHub PAT for Models API fallback")
    OPENROUTER_API_KEY: Optional[str] = Field(None, description="OpenRouter API Key for fallback")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Google API Key for Gemini fallback")
    
    # RAG Settings
    VECTOR_INDEX_NAME: str = Field("vector_markdown", description="Vector Index Name")
    KEYWORD_INDEX_NAME: str = Field("keyword_markdown", description="Keyword Index Name")
    MAX_RETRIEVAL_ITERATIONS: int = Field(3, description="Max iterative loops in the LangGraph agent")
    RRF_K: int = Field(60, description="RRF constant k")
    
    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = Field("false", description="Enable LangSmith Tracing")
    LANGCHAIN_API_KEY: Optional[str] = Field(None, description="LangSmith API Key")
    LANGCHAIN_PROJECT: str = Field("finadvisor-x", description="LangSmith Project Name")
    LANGCHAIN_ENDPOINT: str = Field("https://api.smith.langchain.com", description="LangSmith Endpoint")
    
    # Redis / API Settings
    REDIS_URL: Optional[str] = Field(None, description="Redis Connection URL")
    JWT_SECRET: str = Field("default_insecure_secret_change_me", description="JWT Secret Key")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiate a singleton settings object
settings = Settings()
