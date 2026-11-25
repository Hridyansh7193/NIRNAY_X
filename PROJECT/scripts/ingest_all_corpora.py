"""
NirnayX Master Corpus Builder & Ingestion Script
Ingests all 9 pre-built legal PDFs from sample_data/ into ChromaDB and registers them:
1. BNSS 2023 (Procedural Sanhita) - statute
2. BNS 2023 & IPC Concordance (Substantive Sanhita) - statute
3. BSA 2023 & IEA Concordance (Evidence Adhiniyam) - statute
4. Landmark Precedents & Constitutional Framework - judgment
5. IPC 1860 Core Provisions (Legacy Penal Code) - statute
6. CrPC 1973 Core Provisions (Legacy Procedure) - statute
7. IEA 1872 & Historic Precedents (Evidence Doctrine) - judgment
8. Motor Accidents, Rash Driving & FIR Remedies - fir
9. NirnayX Legal Research Paper - research_paper
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag_pipeline import ingest_document
from backend.retrieval.vector_store import reset_collection

SAMPLE_DIR = PROJECT_ROOT / "sample_data"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def build_and_ingest_all(clean_reset: bool = True):
    print("=" * 65)
    print("NIRNAY-X UNIFIED LEGAL CORPUS INGESTOR & DEDUPLICATOR")
    print("=" * 65)

    if clean_reset:
        print("[0/2] Resetting vector collection for clean deduplication...")
        reset_collection()
        docs_json = PROJECT_ROOT / "data" / "documents.json"
        if docs_json.exists():
            import json
            with open(docs_json, "w", encoding="utf-8") as f:
                json.dump({}, f)

    corpora = [
        ("Bharatiya_Nagarik_Suraksha_Sanhita_BNSS_2023.pdf", "statute"),
        ("Bharatiya_Nyaya_Sanhita_BNS_and_IPC_2023.pdf", "statute"),
        ("Bharatiya_Sakshya_Adhiniyam_BSA_and_IEA_2023.pdf", "statute"),
        ("Landmark_Precedents_and_Constitutional_Provisions.pdf", "judgment"),
        ("Indian_Penal_Code_IPC_1860_Core_Provisions.pdf", "statute"),
        ("Code_of_Criminal_Procedure_CrPC_1973_Core_Provisions.pdf", "statute"),
        ("Indian_Evidence_Act_IEA_1872_and_Historic_Precedents.pdf", "judgment"),
        ("Motor_Accidents_Rash_Driving_and_FIR_Remedies.pdf", "fir"),
        ("NirnayX_Legal_Research_Paper.pdf", "research_paper"),
    ]

    for filename, doc_type in corpora:
        pdf_path = SAMPLE_DIR / filename
        if not pdf_path.exists():
            print(f"  [!] Missing file: {filename}, skipping...")
            continue

        print(f"\n[Ingesting] {filename} (Type: {doc_type})...")
        res = ingest_document(str(pdf_path), filename, doc_type_override=doc_type)
        print(f"  -> Ingested {res.get('chunks_count', 0)} chunks, {len(res.get('sections_cited', []))} sections cited.")

    print("\n" + "=" * 65)
    print("SUCCESS: Legal corpus deduplicated, parsed, and indexed in ChromaDB!")
    print("=" * 65)


if __name__ == "__main__":
    build_and_ingest_all(clean_reset=True)
