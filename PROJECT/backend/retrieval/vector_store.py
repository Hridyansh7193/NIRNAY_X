"""
NirnayX Vector Store
─────────────────────────────────────────────
ChromaDB-backed vector database for storing and
retrieving legal document embeddings with metadata filtering.

Supports:
  - Adding document chunks with embeddings and metadata
  - Semantic similarity search (top-K retrieval)
  - Filtering by document ID, rhetorical role, document type
  - Collection management (list, delete, stats)
"""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings
from backend.retrieval.embeddings import embed_texts, embed_query

logger = logging.getLogger("nirnay.retrieval.vector_store")

# ── Singleton ChromaDB Client ─────────────────────────────
_chroma_client: Optional[chromadb.ClientAPI] = None
_collection = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create the persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(settings.chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB initialized at: {settings.chroma_path}")
    return _chroma_client


def get_collection():
    """Get or create the main legal documents collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"Collection '{settings.chroma_collection_name}' ready "
            f"(count: {_collection.count()})"
        )
    return _collection


def add_chunks(
    chunk_ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> int:
    """
    Add document chunks to the vector store.

    Args:
        chunk_ids: Unique IDs for each chunk
        texts: Raw text content of each chunk
        embeddings: Pre-computed embedding vectors
        metadatas: Metadata dict for each chunk (doc_id, role, etc.)

    Returns:
        Number of chunks added
    """
    collection = get_collection()

    # ChromaDB metadata values must be str, int, float, or bool
    sanitized_metadatas = []
    for meta in metadatas:
        sanitized = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)):
                sanitized[k] = v
            elif isinstance(v, list):
                sanitized[k] = ", ".join(str(i) for i in v)
            else:
                sanitized[k] = str(v)
        sanitized_metadatas.append(sanitized)

    # Add in batches (ChromaDB limit = 5461 per batch)
    batch_size = 500
    total_added = 0

    for i in range(0, len(chunk_ids), batch_size):
        end = i + batch_size
        collection.add(
            ids=chunk_ids[i:end],
            documents=texts[i:end],
            embeddings=embeddings[i:end],
            metadatas=sanitized_metadatas[i:end],
        )
        total_added += len(chunk_ids[i:end])

    logger.info(f"Added {total_added} chunks to vector store")
    return total_added


def search(
    query: str,
    top_k: int = None,
    doc_id_filter: Optional[str] = None,
    role_filter: Optional[str] = None,
) -> list[dict]:
    """
    Semantic similarity search against the vector store.

    Args:
        query: Natural language search query
        top_k: Number of results to return (default from settings)
        doc_id_filter: Filter results to a specific document
        role_filter: Filter by rhetorical role (e.g., "statute", "ruling")

    Returns:
        List of result dicts with keys: chunk_id, text, score, metadata
    """
    collection = get_collection()
    top_k = top_k or settings.top_k_retrieval

    if collection.count() == 0:
        logger.warning("Vector store is empty — no results")
        return []

    # Build where filter
    where_filter = None
    filters = []
    if doc_id_filter:
        filters.append({"doc_id": doc_id_filter})
    if role_filter:
        filters.append({"rhetorical_role": role_filter})

    if len(filters) == 1:
        where_filter = filters[0]
    elif len(filters) > 1:
        where_filter = {"$and": filters}

    # Get query embedding
    query_embedding = embed_query(query)

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Format results
    formatted = []
    if results and results["ids"] and results["ids"][0]:
        for idx in range(len(results["ids"][0])):
            distance = results["distances"][0][idx]
            # ChromaDB cosine distance is 0 = identical, 2 = opposite
            # Convert to similarity score (1 = identical, 0 = orthogonal)
            similarity = 1 - (distance / 2)

            formatted.append({
                "chunk_id": results["ids"][0][idx],
                "text": results["documents"][0][idx],
                "score": round(similarity, 4),
                "distance": round(distance, 4),
                "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
            })

    logger.info(f"Search query returned {len(formatted)} results (top-{top_k})")
    return formatted


def get_collection_stats() -> dict:
    """Get statistics about the vector store."""
    collection = get_collection()
    return {
        "collection_name": settings.chroma_collection_name,
        "total_chunks": collection.count(),
        "persist_dir": str(settings.chroma_path),
    }


def delete_document_chunks(doc_id: str) -> int:
    """Delete all chunks belonging to a specific document."""
    collection = get_collection()

    # Get all chunk IDs for this document
    results = collection.get(
        where={"doc_id": doc_id},
        include=[],
    )

    if results and results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks for doc: {doc_id}")
        return len(results["ids"])

    return 0


def reset_collection():
    """Delete and recreate the entire collection."""
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection_name)
    except Exception:
        pass
    _collection = None
    logger.info("Vector store collection reset")
    return get_collection()
