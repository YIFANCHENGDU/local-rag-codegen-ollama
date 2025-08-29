from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    ollama_host: str = "http://localhost:11434"
    llm_model: str = "qwen2.5-coder"
    embedding_model: str = "nomic-embed-text"
    chroma_dir: str = ".chroma"
    workspace_dir: str = "workspace"
    collection_name: str = "local_rag"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure workspace directory exists
os.makedirs(settings.workspace_dir, exist_ok=True)