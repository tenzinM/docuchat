"""
Retrieval-augmented generation core.
Retrieves relevant chunks from the vector store, then asks the local
Ollama model to answer strictly using that context, citing sources.
"""
import requests

from .config import settings
from . import embeddings, vectorstore

SYSTEM_PROMPT = """You are a careful document assistant. You must answer the user's \
question using ONLY the context passages provided below. Each passage is labeled \
with a source number like [1], [2].

Rules:
- If the answer is fully or partially contained in the context, answer it and cite \
the relevant source numbers in square brackets, e.g. "Revenue grew 12% [2]."
- If the context does NOT contain enough information to answer, say exactly: \
"I couldn't find that in the provided document(s)." Do not guess or use outside knowledge.
- Be concise and direct.
"""


def build_prompt(question: str, chunks: list[dict]) -> str:
    context_blocks = []
    for i, c in enumerate(chunks, start=1):
        context_blocks.append(f"[{i}] (source: {c['filename']}, page {c['page']})\n{c['text']}")
    context = "\n\n".join(context_blocks)

    return f"""{SYSTEM_PROMPT}

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def call_ollama(prompt: str) -> str:
    resp = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        timeout=settings.ollama_timeout,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def answer_question(question: str, doc_ids: list[str] | None = None, top_k: int | None = None):
    k = top_k or settings.top_k
    query_vec = embeddings.embed_query(question)
    chunks = vectorstore.query(query_vec, top_k=k, doc_ids=doc_ids)

    if not chunks:
        return {
            "answer": "I couldn't find that in the provided document(s).",
            "sources": [],
            "used_context": False,
        }

    prompt = build_prompt(question, chunks)
    answer = call_ollama(prompt)

    return {
        "answer": answer,
        "sources": chunks,
        "used_context": True,
    }
