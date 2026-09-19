"""Application configuration loaded from environment / .env file.

Single source of truth for all runtime tunables. The module exposes a cached
``get_settings()`` accessor so the whole process shares one instance.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "AI RAG Platform"
    ENV: str = "dev"
    VERSION: str = "1.0.0"

    # --- Qdrant vector store ---
    # Memory mode is used when neither QDRANT_URL nor QDRANT_HOST is set.
    QDRANT_URL: str | None = None
    QDRANT_HOST: str = ""
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "rag_documents"
    VECTOR_SIZE: int = 768  # authoritative dim for mock provider / collection fallback

    # --- Embedding provider ---
    EMBEDDING_PROVIDER: str = "ollama"  # ollama | openai | mock
    EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_EMBED_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str | None = None

    # --- LLM provider ---
    LLM_PROVIDER: str = "ollama"  # ollama | openai | mock
    LLM_MODEL: str = "qwen2.5:7b"
    LLM_BASE_URL: str = ""  # openai-compatible base, used when LLM_PROVIDER=openai
    LLM_API_KEY: str | None = None
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

    # --- Ingestion ---
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    MAX_FILE_MB: int = 20

    # --- Retrieval ---
    RETRIEVE_TOP_K: int = 5
    SCORE_THRESHOLD: float | None = None

    # --- Security (optional shared API key) ---
    API_KEY: str | None = None

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
