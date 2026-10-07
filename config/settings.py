from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Neo4j Settings
    AURA_INSTANCENAME: Optional[str] = Field("Instance01", description="Neo4j Aura Instance Name")
    NEO4J_URI: str = Field("bolt://localhost:7687", description="Neo4j Connection URI")
    NEO4J_USERNAME: str = Field("neo4j", description="Neo4j Username")
    NEO4J_PASSWORD: str = Field("password", description="Neo4j Password")
    
    # LLM Model Configuration
    GROQ_API_KEY: str = Field("", description="Groq API Key")
    GROQ_MODEL: str = Field("openai/gpt-oss-120b", description="Primary Groq Model")
    ROUTER_MODEL: str = Field("openai/gpt-oss-20b", description="Fast Router Groq Model")
    VERIFIER_MODEL: str = Field("openai/gpt-oss-20b", description="Fast Verifier Groq Model")
    SYNTHESIS_MODEL: str = Field("openai/gpt-oss-120b", description="High-capacity Synthesis Groq Model")
    MAX_CHAT_HISTORY_TURNS: int = Field(6, description="Max conversation turns passed into StateGraph")
    
    GITHUB_API_KEY: Optional[str] = Field(None, description="GitHub PAT for Models API fallback")
    OPENROUTER_API_KEY: Optional[str] = Field(None, description="OpenRouter API Key for fallback")
    OPENROUTER_MODEL: str = Field("mistralai/mistral-small-24b-instruct-2501", description="OpenRouter Fallback Model")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Google API Key for Gemini fallback")
    GEMINI_MODEL: str = Field("gemini-3.5-flash-lite", description="Google Gemini Fallback Chat Model (highest free-tier RPD limit)")
    
    # RAG & Embedding Settings
    VECTOR_INDEX_NAME: str = Field("vector_markdown_v2", description="Vector Index Name")
    PERSONAL_VECTOR_INDEX_NAME: str = Field("personalchunk_vector_v2", description="Personal Vector Index Name")
    EMBEDDING_PROVIDER: str = Field("gemini", description="Embedding Provider (gemini, fastembed, openai)")
    EMBEDDING_MODEL: str = Field("models/gemini-embedding-001", description="Hosted Embedding Model Name")
    EMBEDDING_DIM: int = Field(768, description="Vector embedding dimension (768 with L2 normalization)")
    VECTOR_SEARCH_ENABLED: bool = Field(True, description="Enable vector similarity search (false = keyword/graph search only)")
    KEYWORD_INDEX_NAME: str = Field("keyword_markdown", description="Keyword Index Name")
    MAX_RETRIEVAL_ITERATIONS: int = Field(3, description="Max iterative loops in the LangGraph agent")
    RRF_K: int = Field(60, description="RRF constant k")
    
    # Privacy & Personal Document Protection Flags
    PERSONAL_DOCS_EMBEDDING: str = Field("keyword_only", description="Personal Document Embedding Mode (keyword_only | gemini)")
    PERSONAL_CONTEXT_PROVIDERS: str = Field("groq,openrouter", description="Allowed LLM providers for requests containing personal document context")
    PERSONAL_CONTEXT_EMBEDDING: str = Field("off", description="Whether to embed user queries when personal document context is active (off = BM25 fallback)")
    RERANKER_PROVIDER: str = Field("none", description="Reranker Provider (none | flashrank)")
    
    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = Field("false", description="Enable LangSmith Tracing")
    LANGCHAIN_API_KEY: Optional[str] = Field(None, description="LangSmith API Key")
    LANGCHAIN_PROJECT: str = Field("finadvisor-x", description="LangSmith Project Name")
    LANGCHAIN_ENDPOINT: str = Field("https://api.smith.langchain.com", description="LangSmith Endpoint")
    
    # Auth & Security Settings
    JWT_SECRET: str = Field("finadvisor-secure-jwt-secret-key-2026-x", description="JWT Secret Key")
    JWT_SECRET_KEY: Optional[str] = Field(None, description="Alternative JWT Secret Key alias")
    JWT_ALGORITHM: str = Field("HS256", description="JWT Algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, description="JWT Expiration in minutes")
    
    # Database Settings (Neon PostgreSQL / Local SQLite Fallback)
    DATABASE_URL: Optional[str] = Field(None, description="PostgreSQL Connection URI (Neon pooled connection with sslmode=require)")

    # Document Encryption (Fernet AES-128-CBC + HMAC-SHA256)
    ENCRYPTION_KEY: Optional[str] = Field(None, description="Fernet encryption key for personal document content")

    # Brevo (Sendinblue) HTTPS Email API
    BREVO_API_KEY: Optional[str] = Field(None, description="Brevo (Sendinblue) API Key")
    BREVO_SENDER_EMAIL: Optional[str] = Field(None, description="Brevo Verified Sender Email")
    BREVO_SENDER_NAME: str = Field("FinAdvisor-X", description="Brevo Sender Display Name")

    # SMTP / Email Settings (Fallback)
    SMTP_HOST: Optional[str] = Field(None, description="SMTP Server Host (e.g. smtp.gmail.com)")
    SMTP_SERVER: Optional[str] = Field(None, description="Alternative alias for SMTP Server Host")
    SMTP_PORT: int = Field(587, description="SMTP Server Port")
    SMTP_USER: Optional[str] = Field(None, description="SMTP Username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP Password / App Password")
    SMTP_FROM_EMAIL: Optional[str] = Field(None, description="Sender email address")
    SMTP_TLS: bool = Field(True, description="Enable STARTTLS for SMTP")
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=False
    )

    @property
    def effective_jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY or self.JWT_SECRET

    @property
    def effective_smtp_host(self) -> Optional[str]:
        return self.SMTP_HOST or self.SMTP_SERVER

    @property
    def effective_database_url(self) -> Optional[str]:
        if not self.DATABASE_URL:
            return None
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url


KNOWN_GROQ_MODELS = {
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "allam-2-7b",
    "openai/gpt-oss-safeguard-20b",
    "meta-llama/llama-prompt-guard-2-86m",
    "meta-llama/llama-prompt-guard-2-22m",
    "whisper-large-v3-turbo",
    "whisper-large-v3",
}

def validate_groq_models(s: Settings):
    """Permits standard models and custom prefixed model identifiers."""
    if not s.GROQ_API_KEY:
        return
    for name, model_str in [
        ("GROQ_MODEL", s.GROQ_MODEL),
        ("ROUTER_MODEL", s.ROUTER_MODEL),
        ("VERIFIER_MODEL", s.VERIFIER_MODEL),
        ("SYNTHESIS_MODEL", s.SYNTHESIS_MODEL),
    ]:
        if model_str and model_str not in KNOWN_GROQ_MODELS and not (model_str.startswith("llama") or model_str.startswith("meta-") or model_str.startswith("custom/") or model_str.startswith("openai/") or model_str.startswith("qwen/")):
            logger.warning(f"[Settings] Custom Groq model '{model_str}' configured for {name}.")

# Instantiate a singleton settings object
settings = Settings()
validate_groq_models(settings)


