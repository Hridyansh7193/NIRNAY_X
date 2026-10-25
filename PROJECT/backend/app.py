"""
NirnayX FastAPI Application
─────────────────────────────────────────────
REST API for the NirnayX AI-Powered Legal Intelligence Platform.

Endpoints:
  POST /api/documents/upload      — Upload & ingest a legal document
  GET  /api/documents             — List all ingested documents
  GET  /api/documents/{doc_id}    — Get document details
  DELETE /api/documents/{doc_id}  — Delete a document

  POST /api/query                 — Ask a legal question (RAG pipeline)
  POST /api/search                — Semantic search only (no LLM)

  GET  /api/stats                 — System statistics
  GET  /api/health                — Health check
"""

import os
import logging
import shutil
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.rag_pipeline import (
    ingest_document,
    query_rag,
    get_documents,
    get_document,
    delete_document,
    get_system_stats,
)
from backend.retrieval.vector_store import search as vector_search, reset_collection

# ── Logging Setup ────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nirnay.api")


# ── FastAPI App ──────────────────────────────────────────
app = FastAPI(
    title="NirnayX API",
    description=(
        "AI-Powered Legal Intelligence Platform — "
        "RAG-based legal document analysis, semantic search, "
        "and grounded response generation for Indian law."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup Event ────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """
    Ensure baseline legal corpus is pre-embedded on initial boot.
    If already embedded (count > 0), skips immediately with zero overhead.
    """
    from backend.retrieval.vector_store import get_collection
    collection = get_collection()
    if collection.count() == 0:
        logger.info("ChromaDB is empty on first boot. Auto-embedding baseline legal corpus from sample_data/...")
        sample_dir = settings.data_path.parent / "sample_data"
        if sample_dir.exists():
            for pdf_file in sorted(sample_dir.glob("*.pdf")):
                try:
                    logger.info(f"Auto-embedding baseline document: {pdf_file.name}")
                    ingest_document(str(pdf_file), pdf_file.name)
                except Exception as e:
                    logger.warning(f"Failed to auto-embed {pdf_file.name}: {e}")
        logger.info(f"Initial embedding complete! Vector store ready with {collection.count()} chunks.")
    else:
        logger.info(f"Vector store already pre-embedded with {collection.count()} chunks. Ready for offline search & chat.")


# ── Request/Response Models ──────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Legal question to ask")
    persona: str = Field(default="citizen", description="'citizen' or 'advocate'")
    doc_id: Optional[str] = Field(default=None, description="Filter to specific document")
    top_k: Optional[int] = Field(default=None, ge=1, le=50, description="Number of chunks to retrieve")
    chat_history: Optional[list[dict]] = Field(default=None, description="Previous messages for multi-turn")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=10, ge=1, le=50)
    doc_id: Optional[str] = None
    role_filter: Optional[str] = None


# ── Health & Stats ───────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NirnayX API",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
    }


@app.get("/api/stats")
async def system_stats():
    """Get system-wide statistics."""
    stats = get_system_stats()
    return {
        "status": "ok",
        **stats,
        "config": {
            "llm_provider": settings.llm_provider,
            "embedding_provider": settings.embedding_provider,
            "chunk_size": settings.chunk_size,
            "top_k": settings.top_k_retrieval,
        },
    }


# ── Document Endpoints ───────────────────────────────────

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a legal document (PDF).
    Executes RAG pipeline steps 1-5: parse → chunk → embed → index.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb} MB",
        )

    # Save uploaded file
    upload_path = settings.upload_path / file.filename
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Run ingestion pipeline
    try:
        result = ingest_document(str(upload_path), file.filename)
        return {
            "status": "success",
            "message": f"Document ingested successfully: {file.filename}",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    """List all ingested documents."""
    docs = get_documents()
    return {
        "status": "ok",
        "count": len(docs),
        "documents": docs,
    }


@app.get("/api/documents/{doc_id}")
async def get_document_detail(doc_id: str):
    """Get details of a specific document."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "ok", "document": doc}


@app.delete("/api/documents/{doc_id}")
async def delete_document_endpoint(doc_id: str):
    """Delete a document and its chunks."""
    if delete_document(doc_id):
        return {"status": "ok", "message": f"Document {doc_id} deleted"}
    raise HTTPException(status_code=404, detail="Document not found")


# ── Query & Search Endpoints ─────────────────────────────

@app.post("/api/query")
async def query_legal(request: QueryRequest):
    """
    Ask a legal question using the full RAG pipeline.
    Executes steps 6-11: query → embed → search → context → LLM → response.
    """
    try:
        result = query_rag(
            query=request.query,
            persona=request.persona,
            doc_id_filter=request.doc_id,
            top_k=request.top_k,
            chat_history=request.chat_history,
        )
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/api/search")
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search without LLM generation.
    Returns ranked relevant chunks from the vector store.
    """
    try:
        results = vector_search(
            query=request.query,
            top_k=request.top_k,
            doc_id_filter=request.doc_id,
            role_filter=request.role_filter,
        )
        return {
            "status": "ok",
            "query": request.query,
            "results_count": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ── Admin Endpoints ──────────────────────────────────────

@app.post("/api/admin/reset")
async def reset_system():
    """Reset the entire vector store. USE WITH CAUTION."""
    reset_collection()
    return {"status": "ok", "message": "Vector store has been reset"}


# ── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
