from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from the environment (and a local .env if present)."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "amanah-ai-gateway"
    environment: str = "local"
    web_origin: str = "http://localhost:3000"
    log_level: str = "INFO"

    # Retrieval
    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "amanah_chunks"
    milvus_enabled: bool = True
    embedding_model: str = "BAAI/bge-m3"
    # LiteLLM model id used for query embeddings, e.g. "huggingface/BAAI/bge-m3".
    # Empty means the offline hash embedder (dev only; it is not semantically meaningful).
    litellm_embedding_model: str = ""
    embedding_dim: int = 1024
    top_k: int = 5

    # Generation. Empty model means the deterministic extractive stub.
    litellm_model: str = ""
    temperature: float = 0.0
    max_tokens: int = 700
    request_timeout_seconds: float = 45.0

    # Privacy
    pii_redaction_enabled: bool = True
    pii_restore_response: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
