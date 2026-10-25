"""
NirnayX BNSS (Bharatiya Nagarik Suraksha Sanhita, 2023) Corpus Generator & Ingestor
Generates an authoritative PDF containing the key procedural sections of BNSS 2023
and immediately ingests it into the NirnayX vector store for 100% offline querying.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from backend.rag_pipeline import ingest_document

def create_bnss_pdf(pdf_path: str):
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        spaceAfter=6
    )

    story = []
    story.append(Paragraph("THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS)", title_style))
    story.append(Paragraph("Act No. 46 of 2023 — Effective from 1st July, 2024 (Replaces CrPC 1973)", body_style))
    story.append(Spacer(1, 10))

    sections = [
        ("Section 2 BNSS - Definitions",
         "In this Sanhita, unless the context otherwise requires: "
         "(a) 'bailable offence' means an offence which is shown as bailable in the First Schedule, or which is made bailable by any other law for the time being in force; and 'non-bailable offence' means any other offence. "
         "(g) 'cognizable offence' means an offence for which, and 'cognizable case' means a case in which, a police officer may, in accordance with the First Schedule or under any other law for the time being in force, arrest without warrant. "
         "(h) 'complaint' means any allegation made orally or in writing to a Magistrate, with a view to his taking action under this Sanhita, that some person, whether known or unknown, has committed an offence, but does not include a police report. "
         "(l) 'investigation' includes all the proceedings under this Sanhita for the collection of evidence conducted by a police officer or by any person (other than a Magistrate) who is authorised by a Magistrate in this behalf."),

        ("Section 35 BNSS - When police may arrest without warrant",
         "Any police officer may without an order from a Magistrate and without a warrant, arrest any person who commits, in the presence of a police officer, a cognizable offence; "
         "or against whom a reasonable complaint has been made, or credible information has been received, or a reasonable suspicion exists that he has committed a cognizable offence punishable with imprisonment for a term which may be less than seven years or which may extend to seven years: "
         "Provided that the police officer shall, in all cases where the arrest of a person is not required under the provisions of this sub-section, record the reasons in writing for not making the arrest. "
         "Provided further that the police officer shall serve a notice of appearance directing the person against whom a reasonable complaint has been made to appear before him or at such other place as may be specified in the notice (formerly Section 41A CrPC)."),

        ("Section 173 BNSS - Information in cognizable cases (First Information Report / FIR & Zero FIR)",
         "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; "
         "and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it, and the substance thereof shall be entered in a book to be kept by such officer in such form as the State Government may prescribe in this behalf: "
         "Provided that information relating to the commission of an offence irrespective of the local jurisdiction (Zero FIR) may be given, and shall be registered and transferred to the competent police station having local jurisdiction. "
         "Provided further that information may be given through electronic communication (e-FIR), which shall be taken on record upon being signed within three days by the person giving it. "
         "Provided also that a copy of the information as recorded shall be given forthwith, free of cost, to the informant or the victim."),

        ("Section 175 BNSS - Police officer powers to investigate cognizable case",
         "Any officer in charge of a police station may, without the order of a Magistrate, investigate any cognizable case which a Court having jurisdiction over the local area within the limits of such station would have power to inquire into or try under the provisions of Chapter XIII. "
         "No proceeding of a police officer in any such case shall at any stage be called in question on the ground that the case was one which such officer was not empowered under this section to investigate."),

        ("Section 187 BNSS - Procedure when investigation cannot be completed in twenty-four hours (Police Remand & Judicial Custody)",
         "Whenever any person is arrested and detained in custody, and it appears that the investigation cannot be completed within the period of twenty-four hours fixed by section 58, the officer in charge of the police station shall transmit to the nearest Magistrate a copy of the entries in the case diary and shall at the same time forward the accused to such Magistrate. "
         "The Magistrate may authorise the detention of the accused person in custody, whether police custody or judicial custody, as he thinks fit, for a term not exceeding fifteen days in the whole, or in parts, at any time during the initial forty days (where investigation relates to an offence punishable with imprisonment for less than ten years) or sixty days (where investigation relates to an offence punishable with death, imprisonment for life or imprisonment for a term of ten years or more): "
         "Provided that no Magistrate shall authorise detention of the accused person in police custody unless the accused is produced before him in person. "
         "Provided further that the total period of detention shall not exceed ninety days where the investigation relates to an offence punishable with death, imprisonment for life or imprisonment for not less than ten years, or sixty days where the investigation relates to any other offence; "
         "and on the expiry of the said period of ninety days or sixty days, as the case may be, the accused person shall be released on bail if he is prepared to and does furnish bail (Default Bail / Statutory Bail, replacing Section 167 CrPC)."),

        ("Section 193 BNSS - Report of police officer on completion of investigation (Charge-Sheet / Final Report)",
         "Every investigation under this Chapter shall be completed without unnecessary delay. The investigation in relation to an offence of rape shall be completed within two months from the date on which the information was recorded. "
         "As soon as it is completed, the officer in charge of the police station shall forward to a Magistrate empowered to take cognizance of the offence on a police report, a report in the form prescribed by the State Government, stating the names of the parties, the nature of the information, the names of the persons who appear to be acquainted with the circumstances of the case, and whether any offence appears to have been committed and, if so, by whom: "
         "Provided that the police officer shall submit the report to the Magistrate and also inform the informant or victim of the progress of the investigation within ninety days (replacing Section 173 CrPC)."),

        ("Section 478 BNSS - In what cases bail to be taken (Bailable Offences)",
         "When any person other than a person accused of a non-bailable offence is arrested or detained without warrant by an officer in charge of a police station, or appears or is brought before a Court, and is prepared at any time while in the custody of such officer or at any stage of the proceedings before such Court to give bail, such person shall be released on bail: "
         "Provided that such officer or Court, if he or it thinks fit, may, and shall, if such person is indigent and is unable to furnish surety, instead of taking bail from such person, discharge him on his executing a bond without sureties for his appearance as hereinafter provided (formerly Section 436 CrPC)."),

        ("Section 479 BNSS - Maximum period for which undertrial prisoner can be detained (Undertrial Relief)",
         "Where a person has, during the period of investigation, inquiry or trial under this Sanhita of an offence under any law (not being an offence for which the punishment of death or life imprisonment has been specified) undergone detention for a period extending up to one-half of the maximum period of imprisonment specified for that offence under that law, he shall be released by the Court on bail: "
         "Provided that where such person is a first-time offender (who has never been convicted of any offence in the past), he shall be released on bail by the Court if he has undergone detention for the period extending up to one-third of the maximum period of imprisonment (replacing Section 436A CrPC)."),

        ("Section 480 BNSS - When bail may be taken in case of non-bailable offence (Regular Bail)",
         "When any person accused of, or suspected of, the commission of any non-bailable offence is arrested or detained without warrant by an officer in charge of a police station or appears or is brought before a Court other than the High Court or Court of Session, he may be released on bail, but he shall not be so released if there appear reasonable grounds for believing that he has been guilty of an offence punishable with death or imprisonment for life: "
         "Provided that the Court may direct that a person referred to in this subsection be released on bail if such person is under the age of sixteen years or is a woman or is sick or infirm (formerly Section 437 CrPC)."),

        ("Section 482 BNSS - Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
         "Where any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction under this section that in the event of such arrest he shall be released on bail; "
         "and that Court may, after taking into consideration, inter alia, the nature and gravity of the accusation, the antecedents of the applicant, the possibility of the applicant to flee from justice, and where the accusation has been made with the object of injuring or humiliating the applicant by having him so arrested, either reject the application forthwith or issue an interim order for the grant of anticipatory bail: "
         "Provided that where the High Court or the Court of Session has not passed any interim order under this section or has rejected the application for grant of anticipatory bail, it shall be open to an officer in charge of a police station to arrest without warrant the basis of the accusation. "
         "Provided further that this section shall not apply to any case involving the arrest of any person on accusation of having committed an offence under section 65 and section 70 of the Bharatiya Nyaya Sanhita, 2023 (replacing Section 438 CrPC)."),

        ("Section 528 BNSS - Saving of inherent powers of High Court",
         "Nothing in this Sanhita shall be deemed to limit or affect the inherent powers of the High Court to make such orders as may be necessary to give effect to any order under this Sanhita, or to prevent abuse of the process of any Court or otherwise to secure the ends of justice (formerly Section 482 CrPC)."),

        ("Section 531 BNSS - Repeal and Savings (Transition Regime)",
         "(1) The Code of Criminal Procedure, 1973 is hereby repealed. "
         "(2) Notwithstanding such repeal: (a) if, immediately before the date on which this Sanhita comes into force, there is any appeal, application, trial, inquiry or investigation pending, then, such appeal, application, trial, inquiry or investigation shall be disposed of, continued, held or conducted, as the case may be, in accordance with the provisions of the Code of Criminal Procedure, 1973, as in force immediately before such commencement, as if this Sanhita had not come into force; "
         "(b) all notifications published, proclamations issued, powers conferred, forms prescribed, local jurisdictions defined, sentences passed and orders, rules and appointments, not being inconsistent with the provisions of this Sanhita, made under the repealed Code, shall be deemed to have been respectively published, issued, conferred, prescribed, defined, passed and made under the corresponding provisions of this Sanhita.")
    ]

    for title, text in sections:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"Generated BNSS PDF: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    target_pdf = "data/uploads/Bharatiya_Nagarik_Suraksha_Sanhita_BNSS_2023.pdf"
    create_bnss_pdf(target_pdf)
    print("Ingesting BNSS PDF into NirnayX vector store...")
    result = ingest_document(target_pdf, "Bharatiya_Nagarik_Suraksha_Sanhita_BNSS_2023.pdf")
    print(f"Ingestion Complete! Ingested {result['chunks_count']} chunks, {len(result['sections_cited'])} statutory sections.")
