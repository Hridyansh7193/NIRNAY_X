"""
NirnayX Master Corpus Builder & Ingestion Script
Consolidates all statutory codes and landmark precedents into a single unified runner:
1. BNSS 2023 (Procedural Sanhita)
2. BNS 2023 (Substantive Sanhita) & IPC 1860 Concordance
3. BSA 2023 (Evidence Adhiniyam) & IEA 1872 Concordance
4. Landmark Precedents & Constitutional Provisions (Articles 20(1), 21, 22, 141)
5. IPC 1860 Core Provisions (Legacy Substantive Law)
6. CrPC 1973 Core Provisions (Legacy Procedural Law)
7. IEA 1872 & Historic Rulings (Bhajan Lal, Sibbia, Sushila Aggarwal, Arjun Khotkar, etc.)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_and_ingest_bnss import create_bnss_pdf
from scripts.generate_and_ingest_all_statutes import (
    create_bns_pdf,
    create_bsa_pdf,
    create_precedents_and_constitution_pdf,
)
from scripts.generate_and_ingest_legacy_statutes import (
    create_ipc_legacy_pdf,
    create_crpc_legacy_pdf,
    create_iea_and_historic_precedents_pdf,
)
from backend.rag_pipeline import ingest_document

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def build_and_ingest_all():
    print("=" * 60)
    print("NIRNAY-X UNIFIED LEGAL CORPUS BUILDER & INGESTOR")
    print("=" * 60)

    corpora = [
        # (generator_func, filename, doc_type)
        (create_bnss_pdf, "Bharatiya_Nagarik_Suraksha_Sanhita_BNSS_2023.pdf", "statute"),
        (create_bns_pdf, "Bharatiya_Nyaya_Sanhita_BNS_and_IPC_2023.pdf", "statute"),
        (create_bsa_pdf, "Bharatiya_Sakshya_Adhiniyam_BSA_and_IEA_2023.pdf", "statute"),
        (create_precedents_and_constitution_pdf, "Landmark_Precedents_and_Constitutional_Provisions.pdf", "judgment"),
        (create_ipc_legacy_pdf, "Indian_Penal_Code_IPC_1860_Core_Provisions.pdf", "statute"),
        (create_crpc_legacy_pdf, "Code_of_Criminal_Procedure_CrPC_1973_Core_Provisions.pdf", "statute"),
        (create_iea_and_historic_precedents_pdf, "Indian_Evidence_Act_IEA_1872_and_Historic_Precedents.pdf", "judgment"),
    ]

    for gen_func, filename, doc_type in corpora:
        pdf_path = UPLOAD_DIR / filename
        print(f"\n[1/2] Generating PDF: {filename}...")
        gen_func(pdf_path)

        print(f"[2/2] Ingesting {filename} into vector store...")
        res = ingest_document(str(pdf_path), filename)
        print(f"  -> Ingested {res.get('chunks_count', 0)} chunks, {len(res.get('sections_cited', []))} sections cited.")

    print("\n" + "=" * 60)
    print("SUCCESS: Complete offline legal corpus successfully built and indexed!")
    print("=" * 60)


if __name__ == "__main__":
    build_and_ingest_all()
