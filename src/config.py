"""Configuration management for the RAG chatbot."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration (using free Hugging Face models)
    llm_provider: str = "huggingface"  # "huggingface" or "claude"
    huggingface_api_key: str = ""  # Optional, not required for free tier
    huggingface_model: str = "mistral"  # mistral, llama, phi, or flan
    anthropic_api_key: str = ""  # Only needed if using Claude
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 2048
    temperature: float = 0.7

    # Vector Database
    vector_db_type: str = "faiss"  # "faiss" or "pinecone"
    vector_db_path: str = "./data/vector_store"
    pinecone_api_key: str = ""
    pinecone_environment: str = ""

    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Retrieval Configuration
    top_k_documents: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Session Management
    session_memory_type: str = "memory"  # "memory" or "redis"
    redis_host: str = "localhost"
    redis_port: int = 6379
    max_conversation_history: int = 10

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
