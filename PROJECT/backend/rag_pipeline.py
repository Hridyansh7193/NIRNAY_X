"""
NirnayX RAG Pipeline Orchestrator
─────────────────────────────────────────────
End-to-end orchestration of the 11-step RAG workflow:

 1. Document Upload
 2. Text Extraction (OCR / PDF parsing)
 3. Legally-Coherent Chunking (with overlap & proviso preservation)
 4. Dense Embedding Generation (3-tier resilient fallback)
 5. Vector Database Indexing (ChromaDB HNSW)
 6. User Query Reception
 7. Query Embedding
 8. Semantic Similarity Search (Top-K with Hybrid Reranking)
 9. Grounding Context Formulation
10. Dual-Persona LLM Inference with Structured Synthesis
11. Citation-Verified Response Delivery (Modules, Venn, Charts, Tables)
"""

import json
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
from backend.reasoning.evaluator import get_benchmark_metrics, run_evaluation_suite

logger = logging.getLogger("nirnay.pipeline")


# ── Document Registry (Persisted) ─────────────────────────
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


def ingest_document(file_path: str, filename: str, doc_type_override: Optional[str] = None) -> dict:
    """
    Execute RAG pipeline steps 1-5: Ingest a legal document.
    Includes automated deduplication by filename to prevent redundant chunks.
    """
    start_time = time.time()
    registry = _get_registry()

    # Deduplication: purge previous version if filename already exists
    existing_id = None
    for did, dinfo in list(registry.items()):
        if dinfo.get("filename") == filename:
            existing_id = did
            break

    if existing_id:
        logger.info(f"Existing document '{filename}' detected (ID: {existing_id}). Purging prior chunks before re-indexing.")
        delete_document(existing_id)

    # Steps 1-2: Document Processing & Classification
    logger.info(f"[Pipeline Step 1-2] Processing document: {filename}")
    text, metadata = process_document(file_path, filename)

    if doc_type_override:
        metadata.doc_type = doc_type_override

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
        f"{len(chunks)} chunks | {elapsed}s | Type: {metadata.doc_type}"
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
    Execute RAG pipeline steps 6-11: Answer a legal query with
    structured output (Modules, Venn diagram, Charts, and Tabular matrices).
    """
    start_time = time.time()

    # Steps 6-8: Retrieval & Hybrid Reranking
    logger.info(f"[Pipeline Steps 6-8] Retrieving context for query: {query[:80]}...")
    retrieved_chunks = search(
        query=query,
        top_k=top_k,
        doc_id_filter=doc_id_filter,
    )

    # Step 9: Context Formulation
    logger.info(f"[Pipeline Step 9] Formulating grounding context from {len(retrieved_chunks)} chunks")

    # Step 10: LLM Inference with Structured Generation
    logger.info(f"[Pipeline Step 10] Generating grounded response (persona: {persona})")
    result = generate_response(
        query=query,
        context_chunks=retrieved_chunks,
        persona=persona,
        chat_history=chat_history,
    )

    # Step 11: Response Assembly with Visual Data Structures
    elapsed = round(time.time() - start_time, 2)

    response = {
        "answer": result["answer"],
        "structured_data": result.get("structured_data", {}),
        "sources": [
            {
                "chunk_id": chunk["chunk_id"],
                "text_preview": chunk["text"][:220] + "..." if len(chunk["text"]) > 220 else chunk["text"],
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


def _get_registry() -> dict[str, dict]:
    """Get the current document registry, refreshing from disk."""
    global _document_registry
    _document_registry = _load_registry()
    return _document_registry


def get_documents() -> list[dict]:
    """Get all ingested documents."""
    return list(_get_registry().values())


def get_document(doc_id: str) -> Optional[dict]:
    """Get a specific document's metadata."""
    return _get_registry().get(doc_id)


def delete_document(doc_id: str) -> bool:
    """Delete a document and its chunks from the system."""
    registry = _get_registry()
    if doc_id in registry:
        delete_document_chunks(doc_id)
        del registry[doc_id]
        _save_registry()
        logger.info(f"Document deleted: {doc_id}")
        return True
    return False


def get_system_stats() -> dict:
    """Get system-wide statistics including real evaluation benchmark telemetry."""
    docs = _get_registry()
    vector_stats = get_collection_stats()
    eval_metrics = get_benchmark_metrics()

    return {
        "total_documents": len(docs),
        "documents_count": len(docs),
        "total_chunks": vector_stats.get("total_chunks", 0),
        "vector_store": vector_stats,
        "evaluation": eval_metrics.get("metrics", {}),
        "benchmark_summary": {
            "queries_evaluated": eval_metrics.get("total_test_queries", 5),
            "timestamp": eval_metrics.get("timestamp"),
            "status": eval_metrics.get("status", "ok"),
        },
    }
