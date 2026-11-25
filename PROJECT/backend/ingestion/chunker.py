"""
NirnayX Legal Text Chunker
─────────────────────────────────────────────
Implements legally-coherent text chunking that respects
statutory clause boundaries, provisos, and rhetorical
structures in Indian legal documents.

Unlike naive sliding-window chunking, this module:
  - Detects paragraph / section boundaries
  - Keeps proviso blocks ("Provided that...") with parent sections
  - Respects sentence boundaries to avoid mid-clause splits
  - Applies calibrated chunk overlap across chunk transitions
  - Tags each chunk with rhetorical role hints (Facts, Statute, Ruling, etc.)
"""

import re
import logging
from dataclasses import dataclass, field

from backend.config import settings

logger = logging.getLogger("nirnay.ingestion.chunker")


# ── Rhetorical Role Hints ─────────────────────────────────
RHETORICAL_PATTERNS = {
    "statute": re.compile(
        r"(?:section|sec\.|s\.|article|art\.|rule|order|clause|schedule)\s+\d+"
        r"|(?:bns|bnss|bsa|ipc|crpc|iea)\b",
        re.IGNORECASE,
    ),
    "precedent": re.compile(
        r"(?:AIR|SCC|SCR|Cr\.?LJ|SCALE)\s+\d{4}|\(\d{4}\)\s+\d+\s+SCC"
        r"|(?:held that|relying upon|cited in|constitution bench|landmark ruling)",
        re.IGNORECASE,
    ),
    "ruling": re.compile(
        r"(?:accordingly|dismissed|allowed|disposed|petition is|appeal is|ordered that|directed that"
        r"|held liable|acquitted|convicted|quashed)",
        re.IGNORECASE,
    ),
    "facts": re.compile(
        r"(?:the\s+(?:petitioner|appellant|respondent|complainant|accused|informant)"
        r"|facts\s+of\s+the\s+case|brief\s+facts|background|allegation|incident occurred)",
        re.IGNORECASE,
    ),
    "argument": re.compile(
        r"(?:learned\s+(?:counsel|advocate|senior\s+counsel|app)|submitted\s+that"
        r"|argued\s+that|contended\s+that|it\s+is\s+(?:submitted|contended|argued)|pleaded that)",
        re.IGNORECASE,
    ),
    "procedure": re.compile(
        r"(?:charge\s*sheet|fir\s*no|summons|warrant|remand|bail|limitation|magistrate|cognizance)",
        re.IGNORECASE,
    ),
}

# ── Section / Heading Detector ────────────────────────────
SECTION_HEADING = re.compile(
    r"^(?:\d+\.?\s+|[IVXLC]+\.?\s+|CHAPTER\s+|SECTION\s+|PART\s+)"
    r"|^[A-Z][A-Z\s]{5,}$",
    re.MULTILINE,
)

PROVISO_PATTERN = re.compile(
    r"\bProvided\s+that\b|\bExplanation\s*[:\-—]|\bException\s*[:\-—]",
    re.IGNORECASE,
)


@dataclass
class TextChunk:
    """A semantically coherent chunk of legal text."""
    chunk_id: str
    doc_id: str
    text: str
    chunk_index: int
    char_start: int
    char_end: int
    rhetorical_role: str = "general"
    metadata: dict = field(default_factory=dict)

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (≈ 4 chars per token for English)."""
        return len(self.text) // 4

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "rhetorical_role": self.rhetorical_role,
            "token_estimate": self.token_estimate,
            **self.metadata,
        }


def detect_rhetorical_role(text: str) -> str:
    """Classify a chunk's likely rhetorical role based on keyword patterns."""
    scores = {}
    for role, pattern in RHETORICAL_PATTERNS.items():
        matches = pattern.findall(text)
        scores[role] = len(matches)

    if max(scores.values(), default=0) == 0:
        return "general"
    return max(scores, key=scores.get)


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split text into paragraph-level blocks.
    Preserves proviso blocks with their parent sections.
    """
    raw_paragraphs = re.split(r"\n\s*\n", text)
    merged = []
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        if PROVISO_PATTERN.match(para) and merged:
            merged[-1] = merged[-1] + "\n\n" + para
        else:
            merged.append(para)

    return merged


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences, protecting common legal abbreviations.
    """
    protected = text
    abbreviations = [
        r"(?<!\w)S\.", r"(?<!\w)Sec\.", r"(?<!\w)v\.", r"(?<!\w)vs\.",
        r"(?<!\w)Dr\.", r"(?<!\w)Mr\.", r"(?<!\w)Mrs\.", r"(?<!\w)Ms\.",
        r"(?<!\w)Hon\.", r"(?<!\w)Shri\.", r"(?<!\w)Smt\.",
        r"(?<!\w)No\.", r"(?<!\w)Sr\.", r"(?<!\w)Jr\.",
        r"(?<!\w)Ltd\.", r"(?<!\w)Pvt\.", r"(?<!\w)Co\.",
        r"(?<!\w)Art\.", r"(?<!\w)Cl\.", r"(?<!\w)para\.",
        r"(?<!\w)r/w", r"(?<!\w)u/s",
    ]
    for abbr in abbreviations:
        protected = re.sub(abbr, lambda m: m.group().replace(".", "§DOT§"), protected)

    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", protected)
    return [s.replace("§DOT§", ".").strip() for s in sentences if s.strip()]


def _extract_overlap_tail(text: str, max_overlap_chars: int) -> str:
    """Extract trailing complete sentences to serve as overlap for the subsequent chunk."""
    if not text or max_overlap_chars <= 0:
        return ""

    sentences = split_into_sentences(text)
    overlap_parts = []
    accumulated_len = 0

    for s in reversed(sentences):
        if accumulated_len + len(s) + 1 <= max_overlap_chars:
            overlap_parts.insert(0, s)
            accumulated_len += len(s) + 1
        else:
            if not overlap_parts and len(s) <= max_overlap_chars * 1.5:
                overlap_parts.append(s)
            break

    return " ".join(overlap_parts).strip()


def chunk_document(
    text: str,
    doc_id: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[TextChunk]:
    """
    Main chunking pipeline for legal documents with proviso preservation,
    sentence boundary protection, and cross-chunk overlap continuity.
    """
    chunk_size = chunk_size or settings.chunk_size * 4  # Convert token estimate → chars
    chunk_overlap = chunk_overlap or settings.chunk_overlap * 4

    paragraphs = split_into_paragraphs(text)
    chunks: list[TextChunk] = []
    current_text = ""
    current_start = 0
    char_pos = 0

    def flush_chunk(chunk_text: str, start: int, end: int):
        """Create and append a chunk."""
        clean_text = chunk_text.strip()
        if not clean_text:
            return
        chunk = TextChunk(
            chunk_id=f"{doc_id}_chunk_{len(chunks)}",
            doc_id=doc_id,
            text=clean_text,
            chunk_index=len(chunks),
            char_start=start,
            char_end=end,
            rhetorical_role=detect_rhetorical_role(clean_text),
        )
        chunks.append(chunk)

    for para in paragraphs:
        para_len = len(para)

        if len(current_text) + para_len + 2 <= chunk_size:
            # Fits in current chunk
            if current_text:
                current_text += "\n\n" + para
            else:
                current_text = para
                current_start = char_pos
        else:
            # Current chunk has reached target capacity — flush it
            if current_text:
                flush_chunk(current_text, current_start, char_pos)
                overlap_seed = _extract_overlap_tail(current_text, chunk_overlap)
            else:
                overlap_seed = ""

            if para_len <= chunk_size:
                # Start new chunk with overlap prefix followed by paragraph
                if overlap_seed and not para.startswith(overlap_seed):
                    current_text = f"{overlap_seed}\n\n{para}"
                else:
                    current_text = para
                current_start = max(0, char_pos - len(overlap_seed))
            else:
                # Paragraph itself exceeds chunk_size — split gracefully at sentence boundaries
                sentences = split_into_sentences(para)
                sentence_group = overlap_seed
                sentence_start = max(0, char_pos - len(overlap_seed))

                for sent in sentences:
                    if len(sentence_group) + len(sent) + 1 <= chunk_size:
                        sentence_group = (sentence_group + " " + sent).strip()
                    else:
                        if sentence_group:
                            flush_chunk(sentence_group, sentence_start, char_pos)
                            inner_overlap = _extract_overlap_tail(sentence_group, chunk_overlap)
                            sentence_group = (inner_overlap + " " + sent).strip()
                            sentence_start = char_pos
                        else:
                            sentence_group = sent
                            sentence_start = char_pos

                current_text = sentence_group
                current_start = sentence_start

        char_pos += para_len + 2

    # Flush remaining buffer
    if current_text:
        flush_chunk(current_text, current_start, char_pos)

    logger.info(f"Document {doc_id}: {len(paragraphs)} paragraphs → {len(chunks)} chunks (with {chunk_overlap} char overlap)")
    return chunks
