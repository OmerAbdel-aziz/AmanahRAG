from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "local"
    log_level: str = "INFO"

    rabbitmq_url: str = "amqp://amanah:amanah@localhost:5672/"
    queue_name: str = "document.uploaded.v1"
    dead_letter_exchange: str = "amanah.dlx"
    prefetch_count: int = 4

    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "amanah_chunks"

    # "hash" keeps the pipeline runnable offline. "bge-m3" requires the [models] extra.
    embedding_backend: str = "hash"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    embedding_batch_size: int = 16

    chunk_words: int = 220
    chunk_overlap_words: int = 40


@lru_cache
def get_settings() -> Settings:
    return Settings()
