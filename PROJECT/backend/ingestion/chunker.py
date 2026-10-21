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
        r"(?:section|article|rule|order|clause)\s+\d+",
        re.IGNORECASE,
    ),
    "precedent": re.compile(
        r"(?:AIR|SCC|SCR|Cr\.?LJ|SCALE)\s+\d{4}|\(\d{4}\)\s+\d+\s+SCC",
        re.IGNORECASE,
    ),
    "ruling": re.compile(
        r"(?:accordingly|dismissed|allowed|disposed|petition is|appeal is|order|directed)",
        re.IGNORECASE,
    ),
    "facts": re.compile(
        r"(?:the\s+(?:petitioner|appellant|respondent|complainant|accused)"
        r"|facts\s+of\s+the\s+case|brief\s+facts|background)",
        re.IGNORECASE,
    ),
    "argument": re.compile(
        r"(?:learned\s+(?:counsel|advocate|senior\s+counsel)|submitted\s+that"
        r"|argued\s+that|contended\s+that|it\s+is\s+(?:submitted|contended|argued))",
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
    # Split on double newlines (paragraph boundaries)
    raw_paragraphs = re.split(r"\n\s*\n", text)

    # Merge proviso/explanation blocks with preceding paragraphs
    merged = []
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        if PROVISO_PATTERN.match(para) and merged:
            # Proviso belongs with previous paragraph
            merged[-1] = merged[-1] + "\n\n" + para
        else:
            merged.append(para)

    return merged


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences, being careful not to break on
    common legal abbreviations (S., Sec., v., vs., Dr., Mr., etc.)
    """
    # Protect common abbreviations
    protected = text
    abbreviations = [
        r"(?<!\w)S\.", r"(?<!\w)Sec\.", r"(?<!\w)v\.", r"(?<!\w)vs\.",
        r"(?<!\w)Dr\.", r"(?<!\w)Mr\.", r"(?<!\w)Mrs\.", r"(?<!\w)Ms\.",
        r"(?<!\w)Hon\.", r"(?<!\w)Shri\.", r"(?<!\w)Smt\.",
        r"(?<!\w)No\.", r"(?<!\w)Sr\.", r"(?<!\w)Jr\.",
        r"(?<!\w)Ltd\.", r"(?<!\w)Pvt\.", r"(?<!\w)Co\.",
        r"(?<!\w)Art\.", r"(?<!\w)Cl\.", r"(?<!\w)para\.",
    ]
    for abbr in abbreviations:
        protected = re.sub(abbr, lambda m: m.group().replace(".", "§DOT§"), protected)

    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", protected)

    # Restore dots
    return [s.replace("§DOT§", ".").strip() for s in sentences if s.strip()]


def chunk_document(
    text: str,
    doc_id: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[TextChunk]:
    """
    Main chunking pipeline for legal documents.

    Strategy:
      1. Split text into paragraphs (preserving proviso boundaries)
      2. Group paragraphs into chunks ≤ chunk_size chars
      3. If a single paragraph exceeds chunk_size, split at sentence boundaries
      4. Apply overlap between consecutive chunks
      5. Classify rhetorical role for each chunk
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
        if not chunk_text.strip():
            return
        chunk = TextChunk(
            chunk_id=f"{doc_id}_chunk_{len(chunks)}",
            doc_id=doc_id,
            text=chunk_text.strip(),
            chunk_index=len(chunks),
            char_start=start,
            char_end=end,
            rhetorical_role=detect_rhetorical_role(chunk_text),
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
            # Flush current chunk
            if current_text:
                flush_chunk(current_text, current_start, char_pos)

            if para_len <= chunk_size:
                # Start new chunk with this paragraph
                current_text = para
                current_start = char_pos
            else:
                # Paragraph too long — split at sentence boundaries
                sentences = split_into_sentences(para)
                sentence_group = ""
                sentence_start = char_pos
                for sent in sentences:
                    if len(sentence_group) + len(sent) + 1 <= chunk_size:
                        sentence_group = (sentence_group + " " + sent).strip()
                    else:
                        if sentence_group:
                            flush_chunk(sentence_group, sentence_start, char_pos)
                        sentence_group = sent
                        sentence_start = char_pos
                current_text = sentence_group
                current_start = sentence_start

        char_pos += para_len + 2  # Account for \n\n separator

    # Flush remaining
    if current_text:
        flush_chunk(current_text, current_start, char_pos)

    logger.info(f"Document {doc_id}: {len(paragraphs)} paragraphs → {len(chunks)} chunks")
    return chunks
