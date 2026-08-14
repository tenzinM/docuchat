"""
Local, free embedding generation. No API key, no external calls -
the model runs on your own CPU/GPU via sentence-transformers.
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer

from .config import settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # Cached so the model is only loaded into memory once per process.
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
