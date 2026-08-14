"""
Thin wrapper around a persistent local ChromaDB collection.
No cloud service, no API key - everything is stored on disk in settings.chroma_dir.
"""
import uuid
import chromadb

from .config import settings

_client = chromadb.PersistentClient(path=settings.chroma_dir)
_collection = _client.get_or_create_collection(
    name=settings.chroma_collection,
    metadata={"hnsw:space": "cosine"},
)


def add_chunks(doc_id: str, filename: str, chunks, embeddings: list[list[float]]) -> None:
    ids = [f"{doc_id}::{c.chunk_index}" for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [
        {
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": c.chunk_index,
            "page": c.page,
        }
        for c in chunks
    ]
    _collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(query_embedding: list[float], top_k: int, doc_ids: list[str] | None = None):
    where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )
    hits = []
    if not results["ids"] or not results["ids"][0]:
        return hits

    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        similarity = 1 - distance  # cosine distance -> similarity
        meta = results["metadatas"][0][i]
        hits.append(
            {
                "doc_id": meta["doc_id"],
                "filename": meta["filename"],
                "chunk_index": meta["chunk_index"],
                "page": meta["page"],
                "text": results["documents"][0][i],
                "similarity": similarity,
            }
        )
    return hits


def list_documents():
    all_items = _collection.get()
    docs = {}
    for meta in all_items["metadatas"]:
        doc_id = meta["doc_id"]
        if doc_id not in docs:
            docs[doc_id] = {"doc_id": doc_id, "filename": meta["filename"], "num_chunks": 0}
        docs[doc_id]["num_chunks"] += 1
    return list(docs.values())


def delete_document(doc_id: str) -> None:
    _collection.delete(where={"doc_id": doc_id})


def new_doc_id() -> str:
    return uuid.uuid4().hex[:12]
