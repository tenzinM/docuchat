from typing import Optional
from pydantic import BaseModel


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    message: str


class QueryRequest(BaseModel):
    question: str
    doc_ids: Optional[list[str]] = None   # restrict search to specific documents; None = search all
    top_k: Optional[int] = None


class SourceChunk(BaseModel):
    doc_id: str
    filename: str
    chunk_index: int
    page: Optional[int] = None
    text: str
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    used_context: bool   # False if no relevant chunks were found and the model said so
