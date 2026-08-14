"""
Central configuration for DocuChat.
All values can be overridden via environment variables (see docker-compose.yml).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Where uploaded PDFs are stored on disk
    upload_dir: str = "/data/uploads"

    # Where the persistent Chroma vector store lives
    chroma_dir: str = "/data/chroma"
    chroma_collection: str = "docuchat"

    # Embedding model (runs locally via sentence-transformers, no API key needed)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Chunking
    chunk_size: int = 800          # characters per chunk
    chunk_overlap: int = 150       # characters of overlap between chunks

    # Retrieval
    top_k: int = 4                 # number of chunks to retrieve per query

    # Ollama (local LLM server)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120

    class Config:
        env_prefix = "DOCUCHAT_"


settings = Settings()
