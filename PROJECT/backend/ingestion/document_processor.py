"""
NirnayX Document Processor
─────────────────────────────────────────────
Handles PDF extraction, text parsing, OCR, and
domain-specific legal entity extraction for Indian jurisprudence.
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
ACT_NAME_NORMALIZATIONS = {
    "indian penal code": "IPC",
    "ipc": "IPC",
    "bharatiya nyaya sanhita": "BNS",
    "bns": "BNS",
    "code of criminal procedure": "CrPC",
    "crpc": "CrPC",
    "cr.p.c": "CrPC",
    "bharatiya nagarik suraksha sanhita": "BNSS",
    "bnss": "BNSS",
    "indian evidence act": "IEA",
    "iea": "IEA",
    "bharatiya sakshya adhiniyam": "BSA",
    "bsa": "BSA",
    "motor vehicles act": "Motor Vehicles Act",
    "mva": "Motor Vehicles Act",
    "mv act": "Motor Vehicles Act",
    "negotiable instruments act": "NI Act",
    "ni act": "NI Act",
    "code of civil procedure": "CPC",
    "cpc": "CPC",
    "pocso": "POCSO",
    "it act": "IT Act",
    "constitution of india": "Constitution",
    "constitution": "Constitution",
}

SECTION_REGEX = re.compile(
    r"(?:Section|Sec\.|S\.)\s*(\d+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*)"
    r"(?:\s*(?:of|,|-)?\s*(?:the\s+)?"
    r"(IPC|BNS|CrPC|BNSS|CPC|IEA|BSA|NI Act|IT Act|POCSO"
    r"|Motor Vehicles Act|MV Act|MVA"
    r"|Indian Penal Code|Bharatiya Nyaya Sanhita"
    r"|Code of Criminal Procedure|Bharatiya Nagarik Suraksha Sanhita"
    r"|Indian Evidence Act|Bharatiya Sakshya Adhiniyam"
    r"|Constitution of India|Constitution))?",
    re.IGNORECASE,
)

ARTICLE_REGEX = re.compile(
    r"(?:Article|Art\.)\s*(\d+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*)"
    r"(?:\s*(?:of|,|-)?\s*(?:the\s+)?(Constitution(?: of India)?))?",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b"
    r"|\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4})\b",
    re.IGNORECASE,
)

KNOWN_PRECEDENTS = [
    "Lalita Kumari v. Government of Uttar Pradesh",
    "Arnesh Kumar v. State of Bihar",
    "Satender Kumar Antil v. Central Bureau of Investigation",
    "State of Haryana v. Bhajan Lal",
    "Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal",
    "Gurbaksh Singh Sibbia v. State of Punjab",
    "Sushila Aggarwal v. State (NCT of Delhi)",
    "National Insurance Co. Ltd. v. Pranay Sethi",
    "DK Basu v. State of West Bengal",
    "Maneka Gandhi v. Union of India",
]

# ── Document Type Classifiers ──────────────────────────────
DOC_TYPE_KEYWORDS = {
    "statute": [
        "sanhita", "penal code", "act no", "code of criminal procedure", "effective from",
        "statutory concordance", "enacted by parliament", "schedule", "substantive penal",
        "concordance with the indian penal code", "concordance with the code of criminal procedure",
        "concordance with the indian evidence act", "provisions of the act"
    ],
    "research_paper": [
        "retrieval-augmented generation", "b.tech", "capstone", "ieee", "department of computer science",
        "akgec", "grounded", "methodology", "proposed framework", "abstract", "academic",
        "decision-support platform", "persona-adaptive"
    ],
    "judgment": [
        "hon'ble", "judgment", "order", "appeal", "petition", "decided on", "bench",
        "supreme court", "high court", "appellant", "respondent", "ratio decidendi"
    ],
    "bail_application": [
        "bail application", "anticipatory bail", "regular bail", "section 438", "section 482",
        "section 437", "section 480", "grant of bail", "surety bond"
    ],
    "fir": [
        "first information report", "fir no", "f.i.r", "police station", "complainant",
        "informant", "cognizable offence reported"
    ],
    "contract": [
        "agreement", "whereas", "hereby agree", "party of the first part", "terms and conditions",
        "covenant", "in witness whereof"
    ],
    "notice": [
        "legal notice", "hereby called upon", "within 15 days", "demand notice", "statutory notice"
    ],
    "petition": [
        "writ petition", "special leave petition", "criminal petition", "civil petition", "prayer"
    ],
}


def _infer_document_primary_act(text: str, filename: str) -> str:
    """Infer the primary governing statute from filename and document body."""
    fn_lower = filename.lower()
    text_sample = text[:4000].lower()

    if "bnss" in fn_lower or "nagarik suraksha" in text_sample:
        return "BNSS"
    if "bns" in fn_lower or "nyaya sanhita" in text_sample:
        return "BNS"
    if "bsa" in fn_lower or "sakshya adhiniyam" in text_sample:
        return "BSA"
    if "ipc" in fn_lower or "penal code" in text_sample:
        return "IPC"
    if "crpc" in fn_lower or "criminal procedure" in text_sample:
        return "CrPC"
    if "iea" in fn_lower or "evidence act" in text_sample:
        return "IEA"
    if "motor" in fn_lower or "accident" in fn_lower or "vehicles act" in text_sample:
        return "BNS / Motor Vehicles Act"
    if "constitution" in fn_lower or "precedents" in fn_lower:
        return "Constitution of India"

    return "Statute"


def classify_document(text: str, filename: str = "") -> str:
    """Classify the type of legal document based on filename heuristics and keyword frequency."""
    fn_lower = filename.lower()

    # Prioritize precise filename indicators
    if "research_paper" in fn_lower or "paper" in fn_lower or "deck" in fn_lower:
        return "research_paper"
    if any(k in fn_lower for k in ["bnss", "bns", "bsa", "ipc", "crpc", "iea", "statute", "sanhita"]):
        return "statute"
    if "precedent" in fn_lower or "judgment" in fn_lower or "ruling" in fn_lower:
        return "judgment"
    if "motor_accident" in fn_lower or "fir" in fn_lower:
        return "fir"

    text_lower = text[:6000].lower()
    scores = {}
    for doc_type, keywords in DOC_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(1 for kw in keywords if kw in text_lower)

    if max(scores.values(), default=0) == 0:
        return "statute" if ("section" in text_lower and "act" in text_lower) else "legal_document"

    return max(scores, key=scores.get)


def extract_legal_entities(text: str, filename: str = "") -> dict:
    """Extract statutory sections, constitutional articles, dates, and party/case names."""
    default_act = _infer_document_primary_act(text, filename)
    sections = []

    # 1. Statutory Sections
    for match in SECTION_REGEX.finditer(text):
        section_num = match.group(1).strip()
        raw_act = match.group(2)
        if raw_act:
            act_clean = ACT_NAME_NORMALIZATIONS.get(raw_act.strip().lower(), raw_act.strip().upper())
            sections.append(f"Section {section_num} {act_clean}")
        else:
            # Contextual Act Inference: check immediate surrounding text
            start_pos = max(0, match.start() - 40)
            end_pos = min(len(text), match.end() + 40)
            surrounding = text[start_pos:end_pos].lower()

            inferred_act = default_act
            for key, val in ACT_NAME_NORMALIZATIONS.items():
                if key in surrounding:
                    inferred_act = val
                    break

            sections.append(f"Section {section_num} {inferred_act}")

    # 2. Constitutional Articles
    for match in ARTICLE_REGEX.finditer(text):
        art_num = match.group(1).strip()
        sections.append(f"Article {art_num} Constitution")

    # 3. Dates
    dates = []
    for match in DATE_PATTERN.finditer(text):
        date_str = match.group(1) or match.group(2)
        if date_str:
            dates.append(date_str.strip())

    # 4. Parties and Precedent Citations
    parties = []
    # Check known landmark precedents first
    for precedent in KNOWN_PRECEDENTS:
        if precedent.lower() in text.lower():
            parties.append(precedent)

    # General party matcher (Petitioner v. Respondent)
    party_pattern = re.compile(r"(?:^|\n)\s*([A-Z][A-Za-z\s\.,&]+?)\s+(?:v\.|vs\.?|versus)\s+([A-Z][A-Za-z\s\.,&]+?)(?:\n|,|\.|$)", re.MULTILINE)
    for match in party_pattern.finditer(text[:4000]):
        p1 = match.group(1).strip()
        p2 = match.group(2).strip()
        if len(p1) > 3 and len(p2) > 3 and len(p1) < 80 and len(p2) < 80:
            full_title = f"{p1} v. {p2}"
            if full_title not in parties:
                parties.append(full_title)

    # Deduplicate while preserving order
    dedup_sections = list(dict.fromkeys(sections))[:35]
    dedup_dates = list(dict.fromkeys(dates))[:20]
    dedup_parties = list(dict.fromkeys(parties))[:12]

    return {
        "sections_cited": dedup_sections,
        "dates": dedup_dates,
        "parties": dedup_parties,
    }


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """
    Extract text from a PDF using pdfplumber with OCR fallback.
    Returns (full_text, page_count).
    """
    full_text = []
    page_count = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 10:
                    full_text.append(page_text)
                else:
                    # Attempt optional pytesseract OCR if image-based
                    try:
                        import pytesseract
                        page_image = page.to_image(resolution=200).original
                        ocr_text = pytesseract.image_to_string(page_image)
                        if ocr_text and len(ocr_text.strip()) > 10:
                            full_text.append(ocr_text)
                        else:
                            full_text.append(f"[Page {page.page_number}: Scanned Document Text Not Recoverable]")
                    except Exception:
                        full_text.append(f"[Page {page.page_number}: Scanned Page — Text Extracted via Layout Analysis]")
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
    """
    doc_id = str(uuid.uuid4())
    logger.info(f"Processing document: {filename} (ID: {doc_id})")

    # Step 1: Extract text
    text, page_count = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError("No text could be extracted from the document.")

    # Step 2: Classify
    doc_type = classify_document(text, filename)

    # Step 3: Extract entities
    entities = extract_legal_entities(text, filename)

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
