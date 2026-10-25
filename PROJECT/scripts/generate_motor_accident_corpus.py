"""
Generate authoritative PDF for Motor Accidents, Rash Driving, FIR Registration & Accident Claims.
Ingests directly into NirnayX ChromaDB & document registry.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from backend.rag_pipeline import ingest_document

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
SAMPLE_DIR = PROJECT_ROOT / "sample_data"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def create_motor_accidents_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F2942'),
        alignment=1,
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=12
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )

    story = [
        Paragraph("MOTOR ACCIDENTS, RASH DRIVING &amp; LEGAL REMEDIES", title_style),
        Paragraph(
            "Statutory Framework: Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), "
            "Indian Penal Code (IPC), Motor Vehicles Act, 1988 &amp; Landmark Precedents",
            subtitle_style
        ),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=10),

        Paragraph("1. Section 281 BNS (Rash Driving on a Public Way) — Corresponds to Section 279 IPC", sec_title),
        Paragraph(
            "Whoever drives any vehicle, or rides, on any public way in a manner so rash or negligent as to endanger "
            "human life, or to be likely to cause hurt or injury to any other person, shall be punished with imprisonment "
            "of either description for a term which may extend to six months, or with fine which may extend to one thousand rupees, "
            "or with both. Driving a commercial vehicle or truck on the wrong side or wrong lane of a road is prima facie evidence "
            "of rash and negligent driving under Section 281 BNS and Section 279 IPC.",
            body_style
        ),

        Paragraph("2. Section 125 BNS (Act Endangering Life or Personal Safety) — Corresponds to Sections 337 &amp; 338 IPC", sec_title),
        Paragraph(
            "Whoever does any act so rashly or negligently as to endanger human life or the personal safety of others: "
            "(a) if hurt is caused to any person, shall be punished under Section 125(a) BNS (Section 337 IPC) with imprisonment up to six months or fine; "
            "(b) if grievous hurt is caused, shall be punished under Section 125(b) BNS (Section 338 IPC) with imprisonment up to three years or fine. "
            "In vehicular collisions resulting from wrong-lane driving, charges under Section 281 and Section 125 BNS are filed concurrently.",
            body_style
        ),

        Paragraph("3. Section 106 BNS (Causing Death by Negligence) — Corresponds to Section 304A IPC", sec_title),
        Paragraph(
            "Section 106(1) BNS stipulates that whoever causes the death of any person by doing any rash or negligent act not amounting to "
            "culpable homicide, shall be punished with imprisonment of either description for a term which may extend to five years, and fine. "
            "Section 106(2) BNS provides that whoever causes the death of any person by rash and negligent driving of a vehicle and escapes without "
            "reporting it to a police officer or magistrate soon after the incident shall be punished with imprisonment up to ten years and fine.",
            body_style
        ),

        Paragraph("4. Procedure to Press Charges: Mandatory FIR under Section 173 BNSS / Section 154 CrPC", sec_title),
        Paragraph(
            "Any victim of a vehicular accident or any person who witnesses the collision has the legal right to press charges by filing a "
            "First Information Report (FIR) under Section 173 BNSS (formerly Section 154 CrPC) at the nearest police station or via dialling 112. "
            "Because rash driving causing endangerment or hurt is a cognizable offence, police officers are mandatorily bound to register an FIR "
            "without conducting a preliminary inquiry, as conclusively held by the Supreme Court Constitution Bench in Lalita Kumari v. Govt of UP (2014) 2 SCC 1. "
            "If the station house officer refuses to register the FIR, the complainant has the statutory remedy to submit a written complaint to the "
            "Superintendent of Police under Section 173(3) BNSS or file a complaint before the Judicial Magistrate under Section 175(3) BNSS (formerly 156(3) CrPC).",
            body_style
        ),

        Paragraph("5. Motor Vehicles Act, 1988: Dangerous Driving &amp; MACT Compensation Claims", sec_title),
        Paragraph(
            "Section 184 of the Motor Vehicles Act, 1988 penalizes driving dangerously, including contravention of lane discipline or wrong-side driving, "
            "with imprisonment up to one year or fine up to five thousand rupees. Section 134 MV Act mandates that the driver of the motor vehicle must take "
            "all reasonable steps to secure medical attention for the injured person and report the accident details to the nearest police station within 24 hours. "
            "Crucially, under Section 166 of the Motor Vehicles Act, 1988, the victim (or legal heirs) has the right to file an application for financial compensation "
            "before the Motor Accident Claims Tribunal (MACT) against the driver, vehicle owner, and the third-party insurance company for vehicle damages, "
            "hospitalization costs, permanent disability, and loss of earning capacity.",
            body_style
        ),

        Paragraph("6. Evidentiary Requirements: Preserving Collision Evidence under BSA Section 63", sec_title),
        Paragraph(
            "To successfully establish liability for wrong-lane collision in criminal and MACT proceedings, the following evidence must be preserved: "
            "(1) Vehicle details: Registration plate number, vehicle make, commercial permit, and insurance certificate of the offending truck; "
            "(2) Photographic and video evidence of the collision scene showing vehicle positioning on the wrong side, skid marks, divider layout, and debris; "
            "(3) Electronic records: Dashcam footage, traffic CCTV recordings, or mobile phone videos, admissible as primary electronic evidence under Section 63 BSA (formerly Section 65B IEA); "
            "(4) Medico-Legal Certificate (MLC): Immediate medical examination at a hospital documenting nature of blunt injuries or fractures; "
            "(5) Site inspection report and mechanical inspection panchnama prepared by police investigators.",
            body_style
        ),
    ]

    doc.build(story)
    print(f"Generated PDF at: {output_path}")


def main():
    filename = "Motor_Accidents_Rash_Driving_and_FIR_Remedies.pdf"
    pdf_upload = UPLOAD_DIR / filename
    pdf_sample = SAMPLE_DIR / filename

    create_motor_accidents_pdf(pdf_upload)
    import shutil
    shutil.copy(str(pdf_upload), str(pdf_sample))
    print(f"Copied to sample_data: {pdf_sample}")

    print(f"\nIngesting {filename} into NirnayX RAG Pipeline...")
    res = ingest_document(str(pdf_upload), filename)
    print(f"Ingestion complete: {res['chunks_count']} chunks indexed (Doc ID: {res['doc_id']})")


if __name__ == "__main__":
    main()
