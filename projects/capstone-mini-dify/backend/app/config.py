"""
Mini-Dify - 应用配置管理
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # App
    app_env: str = "development"
    app_secret_key: str = "change-me-in-production"
    app_debug: bool = True

    # Database
    database_url: str = (
        "postgresql+asyncpg://mini_dify:mini_dify_secret@localhost:5432/mini_dify"
    )

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # LLM API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Embedding
    embedding_model: str = "bge-large-zh-v1.5"

    # Upload
    upload_dir: str = "data/uploads"
    max_upload_size_mb: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
