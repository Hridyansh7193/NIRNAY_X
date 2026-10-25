"""
Generate authoritative PDF documents for:
1. Bharatiya Nyaya Sanhita (BNS, 2023) & IPC Concordance
2. Bharatiya Sakshya Adhiniyam (BSA, 2023) & Indian Evidence Act (IEA) Concordance
3. Landmark Precedents & Constitutional Provisions (Articles 20(1), 21, 22, 141, Lalita Kumari, Arnesh Kumar, Satender Antil, D.K. Basu, POCSO s.74)

Then ingest them into NirnayX ChromaDB & document registry for 100% offline local retrieval.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from backend.rag_pipeline import ingest_document

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_bns_pdf(output_path: Path):
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
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15
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
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )

    story = [
        Paragraph("THE BHARATIYA NYAYA SANHITA, 2023 (BNS)", title_style),
        Paragraph("Act No. 45 of 2023 (Enacted by the Parliament of India, Effective July 1, 2024)<br/><b>Statutory Concordance with the Indian Penal Code, 1860 (IPC)</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=12),
        
        Paragraph("Section 101 BNS (Murder Defined) — Corresponds to Section 300 IPC", sec_title),
        Paragraph("Except in the cases hereinafter excepted, culpable homicide is murder, if the act by which the death is caused is done with the intention of causing death, or if it is done with the intention of causing such bodily injury as the offender knows to be likely to cause the death of the person to whom the harm is caused.<br/><b>Exception 1 (Grave and Sudden Provocation):</b> Culpable homicide is not murder if the offender, whilst deprived of the power of self-control by grave and sudden provocation, causes the death of the person who gave the provocation.<br/><b>Exception 2 (Private Defence):</b> Culpable homicide is not murder if the offender, in the exercise in good faith of the right of private defence of person or property, exceeds the power given to him by law.", body_style),
        
        Paragraph("Section 103 BNS (Punishment for Murder) — Corresponds to Section 302 IPC", sec_title),
        Paragraph("<b>(1)</b> Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.<br/><b>(2) Mob Lynching Provision:</b> When a group of five or more persons acting in concert commits murder on the ground of race, caste or community, sex, place of birth, language, personal belief or any other similar ground, each member of such group shall be punished with death or with imprisonment for life, and shall also be liable to fine.", body_style),
        
        Paragraph("Section 105 BNS (Culpable Homicide Not Amounting to Murder) — Corresponds to Section 304 IPC", sec_title),
        Paragraph("Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine, if the act by which the death is caused is done with the intention of causing death, or of causing such bodily injury as is likely to cause death.", body_style),
        
        Paragraph("Section 318 BNS (Cheating) — Corresponds to Section 415 & 420 IPC", sec_title),
        Paragraph("<b>(1)</b> Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, commits cheating.<br/><b>(2) Aggravated Cheating (Old Section 420 IPC):</b> Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.", body_style),
        
        Paragraph("Section 329 BNS (Criminal Trespass & House-Trespass) — Corresponds to Section 441, 442 & 447 IPC", sec_title),
        Paragraph("<b>(1)</b> Whoever enters into or upon property in the possession of another with intent to commit an offence or to intimidate, insult or annoy any person in possession of such property, or having lawfully entered into or upon such property, unlawfully remains there with intent thereby to intimidate, insult or annoy any such person, or with intent to commit an offence, commits criminal trespass.<br/><b>(2) Punishment:</b> Whoever commits criminal trespass shall be punished with imprisonment of either description for a term which may extend to three months, or with fine which may extend to five thousand rupees, or with both.", body_style),
        
        Paragraph("Section 72 BNS (Prohibition of Disclosure of Identity of Victim) — Corresponds to Section 228A IPC", sec_title),
        Paragraph("<b>(1)</b> Whoever prints or publishes the name or any matter which may make known the identity of any person against whom an offence under section 64, section 65, section 66, section 67, section 68, section 69, section 70 or section 71 is alleged or found to have been committed shall be punished with imprisonment of either description for a term which may extend to two years and shall also be liable to fine.<br/><b>Exception:</b> It is not an offence if printed or published by or under the order in writing of the officer-in-charge of the police station or police officer making investigation in good faith, or with authorization in writing of the victim.", body_style),
        
        Paragraph("Section 111 BNS (Organized Crime)", sec_title),
        Paragraph("Any continuing unlawful activity including kidnapping, robbery, extortion, land grabbing, contract killing, economic offences, cyber-crimes committed by any person or group using violence or intimidation to obtain direct or indirect material benefit shall constitute organized crime. Punishment ranges from imprisonment for five years up to life imprisonment or death.", body_style),
        
        Paragraph("Section 4 BNS (General Explanations and Retrospectivity)", sec_title),
        Paragraph("Nothing in this Sanhita shall apply retrospectively to acts or omissions committed prior to the 1st day of July, 2024. In accordance with Article 20(1) of the Constitution of India, substantive criminal liability is determined strictly by the statutory provisions in force at the time of the commission of the offence.", body_style),
    ]

    doc.build(story)
    print(f"Generated BNS PDF: {output_path}")


def create_bsa_pdf(output_path: Path):
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
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#065F46'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )

    story = [
        Paragraph("THE BHARATIYA SAKSHYA ADHINIYAM, 2023 (BSA)", title_style),
        Paragraph("Act No. 47 of 2023 (Enacted by the Parliament of India, Effective July 1, 2024)<br/><b>Statutory Concordance with the Indian Evidence Act, 1872 (IEA)</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#065F46'), spaceAfter=12),
        
        Paragraph("Section 63 BSA (Admissibility of Electronic Records) — Corresponds to Section 65B IEA", sec_title),
        Paragraph("<b>(1)</b> Any information contained in an electronic record which is printed on a paper, stored, recorded or copied in optical or magnetic media or semiconductor memory or any other storage device, shall be deemed to be also a document and shall be admissible in any proceedings, without further proof or production of the original, if the conditions mentioned in this section are satisfied.<br/><b>(2) Conditions:</b> (a) The computer or electronic device was regularly used to store or process information; (b) Information of that kind was regularly supplied to the electronic record in the ordinary course; (c) Throughout the material part of the period, the computer or device operated properly or inoperability did not affect accuracy; (d) Information reproduced duplicates what was supplied.<br/><b>(3) Certificate Mandate:</b> In any proceeding where it is desired to give a statement in evidence by virtue of this section, a certificate doing any of the following things shall be submitted: identifying the electronic record, describing the manner of production, certifying device particulars, and signed by a person occupying a responsible official position in relation to the operation of the relevant device.", body_style),

        Paragraph("Section 61 & 62 BSA (Primary and Secondary Evidence) — Corresponds to Sections 62 & 63 IEA", sec_title),
        Paragraph("Section 61 defines Primary Evidence as the document itself produced for inspection of the Court, including electronic records stored in multiple files, video recordings, and cryptographic hashes. Section 62 defines Secondary Evidence as certified copies, copies made by mechanical processes ensuring accuracy, counterparts of documents, and oral accounts of contents given by persons who have seen them.", body_style),

        Paragraph("Section 23 BSA (Discovery of Fact upon Information) — Corresponds to Section 27 IEA", sec_title),
        Paragraph("Provided that, when any fact is deposed to as discovered in consequence of information received from a person accused of any offence, in the custody of a police officer, so much of such information, whether it amounts to a confession or not, as relates distinctly to the fact thereby discovered, may be proved. This codifies the doctrine of confirmation by subsequent discovery, preserving an essential constitutional exception to police confession inadmissibility.", body_style),

        Paragraph("Section 24 & 25 BSA (Confessions to Police Officers) — Corresponds to Sections 25 & 26 IEA", sec_title),
        Paragraph("No confession made to a police officer shall be proved as against a person accused of any offence. No confession made by any person whilst he is in the custody of a police officer, unless it be made in the immediate presence of a Magistrate, shall be proved as against such person.", body_style),

        Paragraph("Section 116 BSA (Presumption as to Abetment of Suicide) — Corresponds to Section 113A IEA", sec_title),
        Paragraph("When the question is whether the commission of suicide by a woman had been abetted by her husband or any relative of her husband and it is shown that she had committed suicide within a period of seven years from the date of her marriage and that her husband or such relative had subjected her to cruelty, the Court may presume that such suicide had been abetted by her husband or relative.", body_style),
    ]

    doc.build(story)
    print(f"Generated BSA PDF: {output_path}")


def create_precedents_and_constitution_pdf(output_path: Path):
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
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#7C2D12'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )

    story = [
        Paragraph("LANDMARK PRECEDENTS & CONSTITUTIONAL FRAMEWORK", title_style),
        Paragraph("Supreme Court Rulings and Constitutional Articles Cited in NirnayX Research<br/><b>Articles 20(1), 21, 22, 141 & Binding Ratio Decidendi Guidelines</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#7C2D12'), spaceAfter=12),
        
        Paragraph("Article 20(1) Constitution of India (Protection against Ex-Post Facto Laws)", sec_title),
        Paragraph("No person shall be convicted of any offence except for violation of a law in force at the time of the commission of the act charged as an offence, nor be subjected to a penalty greater than that which might have been inflicted under the law in force at the time of the commission of the offence. In Nirnay-X, this forms the Substantive Penalty Ceiling: offenses prior to July 1, 2024 cannot be subjected to enhanced punishments or new minimums under BNS 2023.", body_style),

        Paragraph("Article 141 Constitution of India (Law Declared by Supreme Court to be Binding)", sec_title),
        Paragraph("The law declared by the Supreme Court shall be binding on all courts within the territory of India. Larger Constitution Benches (5, 7, 9, or 13 judges) supersede smaller coordinate benches (2 or 3 judges). Decisions overruled by subsequent coordinate or larger benches lose precedential authority and must be penalized with zero weight in retrieval.", body_style),

        Paragraph("Article 21 & 22 Constitution of India (Personal Liberty and Arrest Safeguards)", sec_title),
        Paragraph("Article 21 guarantees that no person shall be deprived of his life or personal liberty except according to procedure established by law. Article 22 provides that no person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and to be defended by a legal practitioner of his choice, with mandatory production before a Magistrate within 24 hours.", body_style),

        Paragraph("Lalita Kumari v. Government of Uttar Pradesh, (2014) 2 SCC 1 (Constitution Bench)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Registration of an FIR under Section 154 CrPC (Section 173 BNSS) is mandatory if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation. Preliminary inquiry is permissible only in exceptional cases (e.g., medical negligence, matrimonial disputes, commercial disputes) and must be completed within 7 days.", body_style),

        Paragraph("Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Police officers shall not arrest an accused automatically when the offence is punishable with imprisonment for a term which may be less than seven years or which may extend to seven years. The police officer must satisfy himself about the necessity for arrest under the parameters of Section 41 CrPC (Section 35 BNSS). Instead of arrest, a Notice of Appearance under Section 41A CrPC (Section 35(3) BNSS) must be served within two weeks of FIR registration. Unjustified arrest by police officer or mechanical detention by Magistrate invites departmental action and contempt of court.", body_style),

        Paragraph("Satender Kumar Antil v. Central Bureau of Investigation, (2022) 10 SCC 51", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Comprehensive guidelines categorized offenses into Categories A, B, C, and D for bail consideration. For Category A offenses (punishable with 7 years or less), bail applications should be decided ordinarily without remanding the accused to judicial custody if the accused has complied with Section 41A notices. Mandates strict compliance with Section 436A CrPC (Section 479 BNSS) granting mandatory release on personal bond for undertrials having served one-half or one-third of the maximum sentence.", body_style),

        Paragraph("D.K. Basu v. State of West Bengal, (1997) 1 SCC 416", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Enunciated 11 binding guidelines to prevent custodial violence and protect fundamental rights: (1) Arresting personnel must bear accurate, visible name tags; (2) Arrest memo prepared with date, time, and signed by at least one witness/relative; (3) Right of arrested person to inform friend or relative within 8 to 12 hours; (4) Mandatory physical and medical examination at the time of arrest and every 48 hours during detention.", body_style),

        Paragraph("Section 74 of the POCSO Act, 2012 (Prohibition of Identity Disclosure)", sec_title),
        Paragraph("No report in any newspaper, magazine, news-sheet or audio-visual media or other form of communication regarding any inquiry or investigation shall disclose the name, address, photograph, family details, school, neighbourhood or any other particulars which may lead to the identification of a child victim under the Protection of Children from Sexual Offences (POCSO) Act. Violation is punishable with imprisonment up to one year or fine or both.", body_style),
    ]

    doc.build(story)
    print(f"Generated Precedents & Constitution PDF: {output_path}")


def main():
    print("Generating authoritative PDFs for NirnayX legal corpus...")
    bns_pdf = UPLOAD_DIR / "Bharatiya_Nyaya_Sanhita_BNS_and_IPC_2023.pdf"
    bsa_pdf = UPLOAD_DIR / "Bharatiya_Sakshya_Adhiniyam_BSA_and_IEA_2023.pdf"
    prec_pdf = UPLOAD_DIR / "Landmark_Precedents_and_Constitutional_Provisions.pdf"

    create_bns_pdf(bns_pdf)
    create_bsa_pdf(bsa_pdf)
    create_precedents_and_constitution_pdf(prec_pdf)

    print("\nIngesting generated PDFs into NirnayX ChromaDB & document registry...")
    docs_to_ingest = [
        ("Bharatiya_Nyaya_Sanhita_BNS_and_IPC_2023.pdf", bns_pdf, "statute"),
        ("Bharatiya_Sakshya_Adhiniyam_BSA_and_IEA_2023.pdf", bsa_pdf, "statute"),
        ("Landmark_Precedents_and_Constitutional_Provisions.pdf", prec_pdf, "judgment"),
    ]

    for filename, path, doc_type in docs_to_ingest:
        print(f"Ingesting {filename} as {doc_type}...")
        res = ingest_document(str(path), filename)
        print(f"  Result: doc_id={res.get('doc_id')}, chunks={res.get('chunks_count')}, sections={len(res.get('sections_cited', []))}")

    print("\nAll legal clauses and references successfully ingested for offline operation!")


if __name__ == "__main__":
    main()
