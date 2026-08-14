import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from . import ingestion, embeddings, vectorstore, rag
from .models import UploadResponse, QueryRequest, QueryResponse, SourceChunk, DocumentInfo

app = FastAPI(title="DocuChat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = vectorstore.new_doc_id()
    dest_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks = ingestion.process_pdf(dest_path)
    if not chunks:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF.")

    texts = [c.text for c in chunks]
    vectors = embeddings.embed_texts(texts)
    vectorstore.add_chunks(doc_id, file.filename, chunks, vectors)

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        num_chunks=len(chunks),
        message="Document ingested successfully.",
    )


@app.get("/documents", response_model=list[DocumentInfo])
def list_documents():
    return vectorstore.list_documents()


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    vectorstore.delete_document(doc_id)
    return {"message": f"Document {doc_id} deleted."}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = rag.answer_question(req.question, doc_ids=req.doc_ids, top_k=req.top_k)

    sources = [
        SourceChunk(
            doc_id=s["doc_id"],
            filename=s["filename"],
            chunk_index=s["chunk_index"],
            page=s["page"],
            text=s["text"],
            similarity=round(s["similarity"], 4),
        )
        for s in result["sources"]
    ]

    return QueryResponse(answer=result["answer"], sources=sources, used_context=result["used_context"])
