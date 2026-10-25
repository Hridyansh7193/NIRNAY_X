"""
NirnayX Configuration Module
Centralized settings management using pydantic-settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── LLM Provider ──────────────────────────────────────────
    llm_provider: str = Field(default="openai", description="Active LLM provider: openai or gemini")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")

    # Google Gemini
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-3.8-flash")

    # ── Embedding Configuration ──────────────────────────────
    embedding_provider: str = Field(default="openai", description="openai or local")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    local_embedding_model: str = Field(default="all-MiniLM-L6-v2")

    # ── Vector Database ──────────────────────────────────────
    chroma_persist_dir: str = Field(default="./data/chroma_db")
    chroma_collection_name: str = Field(default="nirnay_legal_docs")

    # ── Application ──────────────────────────────────────────
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    debug: bool = Field(default=True)
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173")

    # ── RAG Pipeline ─────────────────────────────────────────
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=64)
    top_k_retrieval: int = Field(default=10)
    similarity_threshold: float = Field(default=0.65)

    # ── Upload Settings ──────────────────────────────────────
    upload_dir: str = Field(default="./data/uploads")
    max_file_size_mb: int = Field(default=50)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def data_path(self) -> Path:
        path = Path("./data")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_path(self) -> Path:
        path = Path(self.chroma_persist_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
