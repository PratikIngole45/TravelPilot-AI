from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8080
    LOG_LEVEL: str = "INFO"

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "data/processed/vector_index"

    NEO4J_URI: Optional[str] = "bolt://localhost:7687"
    NEO4J_USERNAME: Optional[str] = "neo4j"
    NEO4J_PASSWORD: Optional[str] = "password"
    ENABLE_NEO4J: bool = False

    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_AGENT_REVISIONS: int = 2
    TOP_K_RETRIEVAL: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
