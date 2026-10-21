"""
NirnayX RAG Pipeline Orchestrator
─────────────────────────────────────────────
End-to-end orchestration of the 11-step RAG workflow:

 1. Document Upload
 2. Text Extraction (OCR / PDF parsing)
 3. Legally-Coherent Chunking
 4. Dense Embedding Generation
 5. Vector Database Indexing
 6. User Query Reception
 7. Query Embedding
 8. Semantic Similarity Search (Top-K)
 9. Grounding Context Formulation
10. LLM Inference & Grounded Generation
11. Citation-Verified Response Delivery
"""

import logging
import time
from typing import Optional

from backend.config import settings
from backend.ingestion.document_processor import process_document, DocumentMetadata
from backend.ingestion.chunker import chunk_document, TextChunk
from backend.retrieval.embeddings import embed_texts
from backend.retrieval.vector_store import (
    add_chunks,
    search,
    get_collection_stats,
    delete_document_chunks,
)
from backend.reasoning.generator import generate_response

logger = logging.getLogger("nirnay.pipeline")


# ── Document Registry (Persisted) ─────────────────────────
import json

_DOCS_STORE_PATH = settings.data_path / "documents.json"


def _load_registry() -> dict[str, dict]:
    if _DOCS_STORE_PATH.exists():
        try:
            with open(_DOCS_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load document registry: {e}")
    return {}


def _save_registry():
    try:
        _DOCS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_DOCS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(_document_registry, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save document registry: {e}")


_document_registry: dict[str, dict] = _load_registry()


def ingest_document(file_path: str, filename: str) -> dict:
    """
    Execute RAG pipeline steps 1-5: Ingest a legal document.

    Steps:
      1. Extract text from PDF
      2. Classify document type and extract entities
      3. Chunk text into legally-coherent segments
      4. Generate embeddings for each chunk
      5. Store in vector database

    Returns: Ingestion report with doc_id, chunks count, metadata
    """
    start_time = time.time()

    # Steps 1-2: Document Processing
    logger.info(f"[Pipeline Step 1-2] Processing document: {filename}")
    text, metadata = process_document(file_path, filename)

    # Step 3: Chunking
    logger.info(f"[Pipeline Step 3] Chunking document: {metadata.doc_id}")
    chunks = chunk_document(text, metadata.doc_id)

    if not chunks:
        raise ValueError("Document produced no valid text chunks.")

    # Step 4: Embedding Generation
    logger.info(f"[Pipeline Step 4] Generating embeddings for {len(chunks)} chunks")
    chunk_texts = [chunk.text for chunk in chunks]
    embeddings = embed_texts(chunk_texts)

    # Step 5: Vector Store Indexing
    logger.info(f"[Pipeline Step 5] Indexing {len(chunks)} chunks in vector store")
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    chunk_metadatas = [
        {
            "doc_id": chunk.doc_id,
            "chunk_index": chunk.chunk_index,
            "rhetorical_role": chunk.rhetorical_role,
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
            "filename": filename,
            "doc_type": metadata.doc_type,
        }
        for chunk in chunks
    ]

    added = add_chunks(chunk_ids, chunk_texts, embeddings, chunk_metadatas)

    # Register document
    elapsed = round(time.time() - start_time, 2)
    doc_info = {
        **metadata.to_dict(),
        "chunks_count": len(chunks),
        "chunks_indexed": added,
        "processing_time_sec": elapsed,
        "full_text_preview": text[:500] + "..." if len(text) > 500 else text,
    }
    _document_registry[metadata.doc_id] = doc_info
    _save_registry()

    logger.info(
        f"[Pipeline Complete] Document ingested: {metadata.doc_id} | "
        f"{len(chunks)} chunks | {elapsed}s"
    )

    return doc_info


def query_rag(
    query: str,
    persona: str = "citizen",
    doc_id_filter: Optional[str] = None,
    top_k: int = None,
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Execute RAG pipeline steps 6-11: Answer a legal query.

    Steps:
      6. Receive natural language query
      7. Generate query embedding
      8. Semantic similarity search (Top-K retrieval)
      9. Formulate grounding context
     10. LLM inference with grounded generation
     11. Return answer with source citations

    Returns: Answer dict with response, sources, and metadata
    """
    start_time = time.time()

    # Steps 6-8: Retrieval
    logger.info(f"[Pipeline Steps 6-8] Retrieving context for query: {query[:80]}...")
    retrieved_chunks = search(
        query=query,
        top_k=top_k,
        doc_id_filter=doc_id_filter,
    )

    # Step 9: Context Formulation
    logger.info(f"[Pipeline Step 9] Formulating context from {len(retrieved_chunks)} chunks")

    # Step 10: LLM Generation
    logger.info(f"[Pipeline Step 10] Generating grounded response (persona: {persona})")
    result = generate_response(
        query=query,
        context_chunks=retrieved_chunks,
        persona=persona,
        chat_history=chat_history,
    )

    # Step 11: Response Assembly
    elapsed = round(time.time() - start_time, 2)

    response = {
        "answer": result["answer"],
        "sources": [
            {
                "chunk_id": chunk["chunk_id"],
                "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "relevance_score": chunk["score"],
                "metadata": chunk.get("metadata", {}),
            }
            for chunk in retrieved_chunks
        ],
        "query": query,
        "persona": persona,
        "model_info": result.get("usage", {}),
        "retrieval_count": len(retrieved_chunks),
        "latency_sec": elapsed,
    }

    logger.info(f"[Pipeline Complete] Query answered in {elapsed}s | Sources: {len(retrieved_chunks)}")

    return response


def get_documents() -> list[dict]:
    """Get all ingested documents."""
    return list(_document_registry.values())


def get_document(doc_id: str) -> Optional[dict]:
    """Get a specific document's metadata."""
    return _document_registry.get(doc_id)


def delete_document(doc_id: str) -> bool:
    """Delete a document and its chunks from the system."""
    if doc_id in _document_registry:
        delete_document_chunks(doc_id)
        del _document_registry[doc_id]
        _save_registry()
        logger.info(f"Document deleted: {doc_id}")
        return True
    return False


def get_system_stats() -> dict:
    """Get system-wide statistics."""
    vector_stats = get_collection_stats()
    return {
        "total_documents": len(_document_registry),
        "documents_count": len(_document_registry),
        "total_chunks": vector_stats.get("total_chunks", 0),
        "vector_store": vector_stats,
    }
