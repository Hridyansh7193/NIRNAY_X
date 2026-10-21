"""
NirnayX Document Processor
─────────────────────────────────────────────
Handles PDF extraction, text parsing, and OCR
for legal documents (judgments, FIRs, contracts, petitions).
"""

import re
import uuid
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import pdfplumber

logger = logging.getLogger("nirnay.ingestion")


class DocumentMetadata:
    """Metadata extracted from a legal document."""

    def __init__(
        self,
        doc_id: str,
        filename: str,
        total_pages: int,
        doc_type: str = "unknown",
        extracted_at: Optional[str] = None,
        parties: Optional[list[str]] = None,
        dates: Optional[list[str]] = None,
        sections_cited: Optional[list[str]] = None,
    ):
        self.doc_id = doc_id
        self.filename = filename
        self.total_pages = total_pages
        self.doc_type = doc_type
        self.extracted_at = extracted_at or datetime.utcnow().isoformat()
        self.parties = parties or []
        self.dates = dates or []
        self.sections_cited = sections_cited or []

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "filename": self.filename,
            "total_pages": self.total_pages,
            "doc_type": self.doc_type,
            "extracted_at": self.extracted_at,
            "parties": self.parties,
            "dates": self.dates,
            "sections_cited": self.sections_cited,
        }


# ── Legal Entity Patterns ──────────────────────────────────
SECTION_PATTERN = re.compile(
    r"(?:Section|Sec\.|S\.)\s*(\d+[A-Za-z]?)"
    r"(?:\s*(?:of|,)\s*(?:the\s+)?"
    r"(IPC|BNS|CrPC|BNSS|CPC|IEA|BSA|NI Act|IT Act|POCSO"
    r"|Indian Penal Code|Bharatiya Nyaya Sanhita"
    r"|Code of Criminal Procedure|Bharatiya Nagarik Suraksha Sanhita"
    r"|Indian Evidence Act|Bharatiya Sakshya Adhiniyam"
    r"|Transfer of Property Act|Limitation Act))?",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b"
    r"|\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4})\b",
    re.IGNORECASE,
)

PARTY_PATTERN = re.compile(
    r"(?:^|\n)\s*(.+?)\s+(?:v\.|vs\.?|versus)\s+(.+?)(?:\n|$)",
    re.IGNORECASE | re.MULTILINE,
)

# ── Document Type Classifiers ──────────────────────────────
DOC_TYPE_KEYWORDS = {
    "fir": ["first information report", "fir no", "f.i.r", "police station", "complainant"],
    "judgment": ["hon'ble", "judgment", "order", "appeal", "petition", "decided on", "bench"],
    "contract": ["agreement", "whereas", "hereby agree", "party of the first part", "terms and conditions"],
    "notice": ["legal notice", "under section", "hereby called upon", "within 15 days"],
    "petition": ["writ petition", "civil petition", "criminal petition", "prayer", "petitioner"],
    "bail_application": ["bail", "anticipatory bail", "regular bail", "section 438", "section 482"],
}


def classify_document(text: str) -> str:
    """Classify the type of legal document based on keyword frequency."""
    text_lower = text[:5000].lower()
    scores = {}
    for doc_type, keywords in DOC_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(1 for kw in keywords if kw in text_lower)
    if max(scores.values(), default=0) == 0:
        return "legal_document"
    return max(scores, key=scores.get)


def extract_legal_entities(text: str) -> dict:
    """Extract statutory sections, dates, and party names from legal text."""
    sections = []
    for match in SECTION_PATTERN.finditer(text):
        section_num = match.group(1)
        act_name = match.group(2) or "Unknown Act"
        sections.append(f"Section {section_num} {act_name}".strip())

    dates = []
    for match in DATE_PATTERN.finditer(text):
        date_str = match.group(1) or match.group(2)
        if date_str:
            dates.append(date_str.strip())

    parties = []
    for match in PARTY_PATTERN.finditer(text[:3000]):
        parties.append(f"{match.group(1).strip()} v. {match.group(2).strip()}")

    return {
        "sections_cited": list(set(sections))[:30],
        "dates": list(set(dates))[:20],
        "parties": list(set(parties))[:10],
    }


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """
    Extract text from a PDF using pdfplumber.
    Returns (full_text, page_count).
    """
    full_text = []
    page_count = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
                else:
                    # Page might be scanned / image-based
                    full_text.append(f"[Page {page.page_number}: Image/Scanned — OCR required]")
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
        raise ValueError(f"Failed to parse PDF: {e}")

    return "\n\n".join(full_text), page_count


def process_document(file_path: str, filename: str) -> tuple[str, DocumentMetadata]:
    """
    Full document processing pipeline:
    1. Extract text from PDF
    2. Classify document type
    3. Extract legal entities (sections, dates, parties)
    4. Build metadata

    Returns (extracted_text, metadata)
    """
    doc_id = str(uuid.uuid4())
    logger.info(f"Processing document: {filename} (ID: {doc_id})")

    # Step 1: Extract text
    text, page_count = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError("No text could be extracted from the document.")

    # Step 2: Classify
    doc_type = classify_document(text)

    # Step 3: Extract entities
    entities = extract_legal_entities(text)

    # Step 4: Build metadata
    metadata = DocumentMetadata(
        doc_id=doc_id,
        filename=filename,
        total_pages=page_count,
        doc_type=doc_type,
        parties=entities["parties"],
        dates=entities["dates"],
        sections_cited=entities["sections_cited"],
    )

    logger.info(
        f"Document processed: {doc_type} | {page_count} pages | "
        f"{len(entities['sections_cited'])} sections | {len(entities['parties'])} parties"
    )

    return text, metadata
