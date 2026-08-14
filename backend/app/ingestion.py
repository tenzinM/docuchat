"""
Handles turning a raw PDF into a list of (text, page_number) chunks
ready to be embedded and stored.
"""
from dataclasses import dataclass
from pypdf import PdfReader

from .config import settings


@dataclass
class Chunk:
    text: str
    page: int
    chunk_index: int


def extract_pages(file_path: str) -> list[tuple[int, str]]:
    """Returns a list of (page_number, page_text) tuples, 1-indexed pages."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append((i + 1, text))
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple sliding-window character chunker with overlap.

    Character-based chunking is intentionally simple (no external tokenizer
    dependency) and works well enough for MiniLM-scale embedding models.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def process_pdf(file_path: str) -> list[Chunk]:
    """Full pipeline: PDF -> per-page text -> overlapping chunks with page numbers preserved."""
    pages = extract_pages(file_path)
    chunks: list[Chunk] = []
    idx = 0
    for page_num, page_text in pages:
        for piece in chunk_text(page_text, settings.chunk_size, settings.chunk_overlap):
            chunks.append(Chunk(text=piece, page=page_num, chunk_index=idx))
            idx += 1
    return chunks
