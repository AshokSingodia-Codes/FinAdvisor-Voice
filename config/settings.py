from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Neo4j Settings
    AURA_INSTANCENAME: Optional[str] = Field("Instance01", description="Neo4j Aura Instance Name")
    NEO4J_URI: str = Field("bolt://localhost:7687", description="Neo4j Connection URI")
    NEO4J_USERNAME: str = Field("neo4j", description="Neo4j Username")
    NEO4J_PASSWORD: str = Field("password", description="Neo4j Password")
    
    GROQ_API_KEY: str = Field("", description="Groq API Key")
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
    
    # Auth & Security Settings
    JWT_SECRET: str = Field("finadvisor-secure-jwt-secret-key-2026-x", description="JWT Secret Key")
    JWT_SECRET_KEY: Optional[str] = Field(None, description="Alternative JWT Secret Key alias")
    JWT_ALGORITHM: str = Field("HS256", description="JWT Algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, description="JWT Expiration in minutes")
    
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


# Instantiate a singleton settings object
settings = Settings()

