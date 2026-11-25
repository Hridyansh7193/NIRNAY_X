"""
NirnayX Cross-Scoring Legal Reranker
─────────────────────────────────────────────
Applies two-stage retrieval refinement:
Stage 1: Dense vector similarity retrieval (ChromaDB HNSW)
Stage 2: Hybrid cross-scoring reranking incorporating statutory section matching,
         lexical keyword density, and rhetorical role alignment.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("nirnay.retrieval.reranker")

# Statutory tokens and landmark cases
SECTION_NUM_PATTERN = re.compile(r"\b(?:section|sec\.?|s\.?|article|art\.?)\s*(\d+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*|\d+)\b", re.IGNORECASE)
BARE_NUM_PATTERN = re.compile(r"\b(\d{1,4}[A-Za-z]?)\b")

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is",
    "are", "was", "were", "be", "been", "me", "my", "i", "you", "your", "can",
    "do", "does", "did", "this", "that", "it", "with", "from", "as", "by", "what",
    "how", "under", "applicable", "who", "which", "when", "where", "why", "tell"
}


def _extract_query_features(query: str) -> dict:
    """Extract sections, act names, case names, and salient query terms."""
    q_lower = query.lower()

    # Extracted explicit sections
    sections = [m.lower() for m in SECTION_NUM_PATTERN.findall(query)]
    # Extracted potential numbers
    numbers = [n.lower() for n in BARE_NUM_PATTERN.findall(query) if n.lower() not in ["1", "2", "3", "4", "5", "10", "2024", "2023", "1860", "1973"]]

    # Query tokens
    raw_tokens = re.findall(r"\w+", q_lower)
    tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) > 2]

    # Desired rhetorical role intent
    desired_role = None
    if any(k in q_lower for k in ["section", "provision", "act", "sanhita", "code", "punishment", "penalty", "offence"]):
        desired_role = "statute"
    elif any(k in q_lower for k in ["ruling", "precedent", "judgment", "held that", "supreme court", "high court", "case law"]):
        desired_role = "precedent"
    elif any(k in q_lower for k in ["facts", "allegation", "complainant", "accident", "hit", "police"]):
        desired_role = "facts"
    elif any(k in q_lower for k in ["procedure", "fir", "bail", "arrest", "remand", "magistrate"]):
        desired_role = "procedure"

    return {
        "sections": set(sections + numbers),
        "tokens": set(tokens),
        "desired_role": desired_role,
        "raw": q_lower,
    }


def rerank_chunks(query: str, candidate_chunks: list[dict], top_k: int = 10) -> list[dict]:
    """
    Reranks candidate chunks retrieved from vector store using hybrid legal scoring.

    Scoring weights:
      - 0.55: Dense vector similarity score (0.0 to 1.0)
      - 0.25: Lexical keyword match ratio (BM25-style term frequency)
      - 0.15: Exact statutory section / article presence bonus
      - 0.05: Rhetorical role alignment bonus
    """
    if not candidate_chunks:
        return []

    features = _extract_query_features(query)
    q_tokens = features["tokens"]
    q_sections = features["sections"]
    desired_role = features["desired_role"]

    reranked = []

    for chunk in candidate_chunks:
        text = chunk.get("text", "")
        text_lower = text.lower()
        meta = chunk.get("metadata", {})
        chunk_role = meta.get("rhetorical_role", "general").lower()
        base_score = float(chunk.get("score", 0.5))

        # 1. Lexical Keyword Overlap
        if q_tokens:
            chunk_tokens = set(re.findall(r"\w+", text_lower))
            overlap_count = len(q_tokens.intersection(chunk_tokens))
            lexical_score = min(1.0, overlap_count / max(1, len(q_tokens)))
        else:
            lexical_score = 0.5

        # 2. Exact Statutory Section Bonus
        section_bonus = 0.0
        if q_sections:
            for sec in q_sections:
                if f"section {sec}" in text_lower or f"sec. {sec}" in text_lower or f"article {sec}" in text_lower or f" {sec} " in text_lower:
                    section_bonus = 1.0
                    break
                elif sec in text_lower:
                    section_bonus = 0.5

        # 3. Rhetorical Role Alignment
        role_bonus = 0.0
        if desired_role:
            if chunk_role == desired_role:
                role_bonus = 1.0
            elif desired_role == "statute" and chunk_role in ["statute", "procedure"]:
                role_bonus = 0.7
            elif desired_role == "precedent" and chunk_role in ["precedent", "ruling"]:
                role_bonus = 0.8

        # Composite Weighted Score
        hybrid_score = (
            0.55 * base_score +
            0.25 * lexical_score +
            0.15 * section_bonus +
            0.05 * role_bonus
        )

        # Keep score in [0.0, 1.0]
        final_score = round(min(0.9999, max(0.01, hybrid_score)), 4)

        chunk_copy = dict(chunk)
        chunk_copy["vector_score"] = round(base_score, 4)
        chunk_copy["score"] = final_score
        chunk_copy["rerank_boosts"] = {
            "lexical": round(lexical_score, 2),
            "section_match": round(section_bonus, 2),
            "role_match": round(role_bonus, 2),
        }
        reranked.append(chunk_copy)

    # Sort descending by hybrid reranked score
    reranked.sort(key=lambda x: x["score"], reverse=True)

    logger.info(f"Reranked {len(candidate_chunks)} candidates -> selected top-{min(top_k, len(reranked))}")
    return reranked[:top_k]
