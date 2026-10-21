"""
NirnayX Embedding Engine
─────────────────────────────────────────────
Generates dense vector embeddings for legal document chunks
using either OpenAI's text-embedding API or local
sentence-transformers models.
"""

import logging
from typing import Optional

import openai

from backend.config import settings

logger = logging.getLogger("nirnay.retrieval.embeddings")

# ── Lazy-loaded local model ─────────────────────────────
_local_model = None


def _get_local_model():
    """Lazy-load a sentence-transformers model."""
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading local embedding model: {settings.local_embedding_model}")
        _local_model = SentenceTransformer(settings.local_embedding_model)
    return _local_model


def embed_texts_openai(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using OpenAI's Embedding API.
    Handles batching automatically (API max = 2048 per request).
    """
    client = openai.OpenAI(api_key=settings.openai_api_key)
    all_embeddings = []
    batch_size = 512  # Safe batch size

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # Truncate very long texts to avoid token limits
        batch = [t[:8000] for t in batch]

        response = client.embeddings.create(
            input=batch,
            model=settings.openai_embedding_model,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def embed_texts_local(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using a local sentence-transformers model.
    """
    model = _get_local_model()
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=64,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def _deterministic_fallback_embed(texts: list[str], dim: int = 384) -> list[list[float]]:
    """Deterministic hash-based embedding fallback when neither OpenAI nor local model is available."""
    import hashlib
    import math

    results = []
    for text in texts:
        vec = [0.0] * dim
        words = text.lower().split()
        if not words:
            results.append(vec)
            continue
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        vec = [x / norm for x in vec]
        results.append(vec)
    return results


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using the configured provider.
    Falls back to local model if OpenAI is not configured, or deterministic hash if local model fails.
    """
    if not texts:
        return []

    provider = settings.embedding_provider.lower()

    if provider == "openai" and settings.openai_api_key:
        try:
            logger.info(f"Embedding {len(texts)} texts via OpenAI ({settings.openai_embedding_model})")
            return embed_texts_openai(texts)
        except Exception as e:
            logger.warning(f"OpenAI embedding failed ({e}), attempting local fallback")

    try:
        logger.info(f"Embedding {len(texts)} texts via local model ({settings.local_embedding_model})")
        return embed_texts_local(texts)
    except Exception as e:
        logger.warning(f"Local embedding model unavailable ({e}). Using deterministic offline embedding fallback.")
        return _deterministic_fallback_embed(texts)


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    embeddings = embed_texts([query])
    return embeddings[0] if embeddings else []
