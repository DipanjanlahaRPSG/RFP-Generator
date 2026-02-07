from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_model: str = "gpt-3.5-turbo"

    # ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "rfp_templates"

    # Search Configuration
    max_search_results: int = 10
    similarity_threshold: float = 0.0

    # Processing Configuration
    batch_size: int = 5
    max_tokens: int = 8191

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
