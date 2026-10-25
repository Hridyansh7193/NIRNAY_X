"""
Generate and ingest authoritative documents for OLD / LEGACY legal references:
1. Indian Penal Code, 1860 (IPC) - Comprehensive substantive criminal sections
2. Code of Criminal Procedure, 1973 (CrPC) - Core procedural provisions saved under Section 531(2)(a) BNSS
3. Indian Evidence Act, 1872 (IEA) & Historic Precedents (Bhajan Lal, Sibbia, Sushila Aggarwal, Arjun Khotkar, Sharad Birdhichand Sarda, Pulukuri Kottaya)

Ingests all generated PDFs into NirnayX ChromaDB & document registry for full offline backward compatibility.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

from backend.rag_pipeline import ingest_document

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_ipc_legacy_pdf(output_path: Path):
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
        textColor=colors.HexColor('#1E293B'),
        alignment=1,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = [
        Paragraph("THE INDIAN PENAL CODE, 1860 (IPC)", title_style),
        Paragraph("Act No. 45 of 1860 (Pre-July 1, 2024 Substantive Criminal Law)<br/><b>Applicable to Pre-Transition Offences under Article 20(1) Non-Retroactivity Protection</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=10),

        Paragraph("Section 34 IPC (Acts Done by Several Persons in Furtherance of Common Intention)", sec_title),
        Paragraph("When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone. Requires prior meeting of minds and pre-arranged plan, though common intention may develop on the spot.", body_style),

        Paragraph("Section 120B IPC (Punishment of Criminal Conspiracy)", sec_title),
        Paragraph("Whoever is a party to a criminal conspiracy to commit an offence punishable with death, imprisonment for life or rigorous imprisonment for a term of two years or upwards, shall be punished in the same manner as if he had abetted such offence. Section 120A defines agreement between two or more persons to do an illegal act.", body_style),

        Paragraph("Section 149 IPC (Every Member of Unlawful Assembly Guilty of Offence)", sec_title),
        Paragraph("If an offence is committed by any member of an unlawful assembly in prosecution of the common object of that assembly, or such as the members of that assembly knew to be likely to be committed in prosecution of that object, every person who, at the time of the committing of that offence, is a member of the same assembly, is guilty of that offence.", body_style),

        Paragraph("Section 300 IPC (Murder) and Exceptions 1 to 5", sec_title),
        Paragraph("Culpable homicide is murder if the act by which the death is caused is done with the intention of causing death, or with the intention of causing such bodily injury as the offender knows to be likely to cause death, or is sufficient in the ordinary course of nature to cause death.<br/>"
                  "<b>Exception 1:</b> Grave and sudden provocation deprived the offender of self-control.<br/>"
                  "<b>Exception 2:</b> Exceeding the right of private defence in good faith without premeditation.<br/>"
                  "<b>Exception 3:</b> Public servant exceeding powers in good faith believing it lawful.<br/>"
                  "<b>Exception 4:</b> Sudden fight in the heat of passion upon a sudden quarrel without premeditation.<br/>"
                  "<b>Exception 5:</b> When the person whose death is caused, being above 18 years, suffers death with consent.", body_style),

        Paragraph("Section 302 IPC (Punishment for Murder)", sec_title),
        Paragraph("Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. (Corresponds to Section 103 BNS 2023).", body_style),

        Paragraph("Section 304 IPC (Punishment for Culpable Homicide Not Amounting to Murder)", sec_title),
        Paragraph("Part I: If done with intention of causing death or bodily injury likely to cause death — imprisonment for life or up to 10 years and fine. Part II: If done with knowledge that it is likely to cause death, but without any intention to cause death — imprisonment up to 10 years or fine or both.", body_style),

        Paragraph("Section 304B IPC (Dowry Death)", sec_title),
        Paragraph("Where the death of a woman is caused by burns or bodily injury or occurs otherwise than under normal circumstances within seven years of marriage, and it is shown that soon before her death she was subjected to cruelty or harassment by her husband or relatives in connection with dowry, such death is dowry death. Punishment: imprisonment not less than seven years up to life.", body_style),

        Paragraph("Section 307 IPC (Attempt to Murder)", sec_title),
        Paragraph("Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment up to 10 years and fine; if hurt is caused, punishment may extend to imprisonment for life.", body_style),

        Paragraph("Section 375 & 376 IPC (Rape and Punishment for Rape)", sec_title),
        Paragraph("Defines sexual assault against a woman without consent or against will. Section 376 mandates rigorous imprisonment not less than 10 years up to life imprisonment and fine. Section 376D governs gang rape with minimum 20 years up to natural life imprisonment.", body_style),

        Paragraph("Section 415 & 420 IPC (Cheating and Dishonestly Inducing Delivery of Property)", sec_title),
        Paragraph("Section 415 defines cheating. Section 420 IPC penalizes aggravated cheating where the offender dishonestly induces the deceived person to deliver property or make/alter a valuable security. Punishment: imprisonment up to seven years and fine. (Corresponds to Section 318(2) BNS 2023).", body_style),

        Paragraph("Section 441, 442, 447 & 448 IPC (Criminal Trespass and House-Trespass)", sec_title),
        Paragraph("Entering upon property in possession of another with intent to commit an offence, or intimidate, insult, or annoy. Section 447 penalizes criminal trespass with up to 3 months imprisonment or fine up to 500 rupees. Section 448 penalizes house-trespass with up to 1 year imprisonment or fine up to 1000 rupees.", body_style),

        Paragraph("Section 498A IPC (Husband or Relative of Husband Subjecting Woman to Cruelty)", sec_title),
        Paragraph("Whoever, being the husband or relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine. Cruelty includes willful conduct likely to drive woman to commit suicide or harassment for unlawful property demands.", body_style),

        Paragraph("Section 503 & 506 IPC (Criminal Intimidation)", sec_title),
        Paragraph("Threatening another with injury to person, reputation or property with intent to cause alarm. Section 506 punishes criminal intimidation with up to 2 years imprisonment, or up to 7 years if the threat is to cause death or grievous hurt.", body_style),
    ]

    doc.build(story)
    print(f"Generated Legacy IPC PDF: {output_path}")


def create_crpc_legacy_pdf(output_path: Path):
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
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = [
        Paragraph("THE CODE OF CRIMINAL PROCEDURE, 1973 (CrPC)", title_style),
        Paragraph("Act No. 2 of 1974 (Procedural Criminal Code for Pre-July 1, 2024 Proceedings)<br/><b>Preserved for Pending Inquiries, Trials & Appeals under Section 531(2)(a) BNSS</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=10),

        Paragraph("Section 2 CrPC (Definitions: Bailable, Cognizable Offences)", sec_title),
        Paragraph("Section 2(a) defines 'bailable offence' as an offence shown as bailable in the First Schedule, or made bailable by any other law; all other offences are non-bailable. Section 2(c) defines 'cognizable offence' as an offence for which a police officer may arrest without warrant. Section 2(l) defines 'non-cognizable offence'.", body_style),

        Paragraph("Section 41 & Section 41A CrPC (Arrest without Warrant & Mandatory Notice of Appearance)", sec_title),
        Paragraph("Under Section 41, arrest for offences punishable with up to 7 years imprisonment requires recorded reasons of necessity. Under Section 41A, where arrest is not requisite under Section 41(1), the police officer must issue a notice directing the person to appear before him. So long as the person complies, he shall not be arrested (Codified by Arnesh Kumar v. State of Bihar).", body_style),

        Paragraph("Section 50 & Section 57 CrPC (Grounds of Arrest & 24-Hour Detention Limit)", sec_title),
        Paragraph("Section 50 mandates informing the arrested person forthwith of full particulars of the offence and right to bail. Section 57 establishes that no police officer shall detain in custody a person arrested without warrant for a longer period than 24 hours, excluding journey time, without a special order of a Magistrate under Section 167.", body_style),

        Paragraph("Section 154 CrPC (Information in Cognizable Cases - Mandatory FIR Registration)", sec_title),
        Paragraph("Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing and read over to the informant. Pursuant to the 5-Judge Constitution Bench in Lalita Kumari v. Govt of UP, registration of an FIR is mandatory under Section 154 if the information discloses a cognizable offence.", body_style),

        Paragraph("Section 156(3) CrPC (Magistrate's Power to Direct Investigation)", sec_title),
        Paragraph("Any Magistrate empowered under Section 190 may order an investigation by the police into any cognizable case where the police station has failed or refused to register an FIR under Section 154.", body_style),

        Paragraph("Section 161 & Section 164 CrPC (Witness Statements & Confessions before Magistrate)", sec_title),
        Paragraph("Section 161 empowers police to examine witnesses orally during investigation (not signed by witness, not substantive evidence). Section 164 empowers Metropolitan/Judicial Magistrates to record confessions and statements during investigation; confessions must be voluntary after statutory warning that the person is not bound to confess.", body_style),

        Paragraph("Section 167 CrPC (Remand & Default Statutory Bail)", sec_title),
        Paragraph("Limits police custody remand to a maximum period of 15 days in the whole. Total detention in custody cannot exceed 90 days (for offences punishable with death, life, or not less than 10 years) or 60 days (for all other offences). Upon expiry of 60/90 days without chargesheet filing, the accused has an indefeasible right to default statutory bail upon offering bail bonds.", body_style),

        Paragraph("Section 173 CrPC (Report of Police Officer on Completion of Investigation / Chargesheet)", sec_title),
        Paragraph("Investigation must be completed without unnecessary delay. As soon as completed, the police officer forwards a police report (chargesheet or final closure report) to the Magistrate empowered to take cognizance under Section 190(1)(b).", body_style),

        Paragraph("Section 436 & Section 436A CrPC (Bail as of Right & Maximum Undertrial Detention)", sec_title),
        Paragraph("Section 436 provides that bail is a matter of absolute right in bailable offences. Section 436A provides that undertrial prisoners who have undergone detention extending up to one-half of the maximum imprisonment specified for the offence (other than death penalty) shall be released on personal bond.", body_style),

        Paragraph("Section 437 CrPC (Bail in Non-Bailable Offences by Magistrate)", sec_title),
        Paragraph("Discretionary bail by Magistrate; cannot be granted if there are reasonable grounds for believing the accused is guilty of an offence punishable with death or life imprisonment, unless the person is under 16, a woman, or sick or infirm.", body_style),

        Paragraph("Section 438 CrPC (Direction for Grant of Bail to Person Apprehending Arrest / Anticipatory Bail)", sec_title),
        Paragraph("Empowers the High Court or Court of Session to grant anticipatory bail to any person who has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence (Governed by Constitution Benches in Sibbia and Sushila Aggarwal).", body_style),

        Paragraph("Section 439 CrPC (Special Powers of High Court / Sessions Court Regarding Regular Bail)", sec_title),
        Paragraph("Special concurrent powers of High Court or Sessions Court to direct release on bail of any person accused of an offence and in custody, or to modify any conditions imposed by a Magistrate.", body_style),

        Paragraph("Section 482 CrPC (Inherent Powers of the High Court to Quash Proceedings)", sec_title),
        Paragraph("Nothing in this Code shall be deemed to limit or affect the inherent powers of the High Court to make such orders as may be necessary to give effect to any order under this Code, or to prevent abuse of the process of any Court or otherwise to secure the ends of justice (Governed by Bhajan Lal guidelines).", body_style),
    ]

    doc.build(story)
    print(f"Generated Legacy CrPC PDF: {output_path}")


def create_iea_and_historic_precedents_pdf(output_path: Path):
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
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#065F46'),
        spaceBefore=10,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'SecBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = [
        Paragraph("INDIAN EVIDENCE ACT, 1872 & HISTORIC PRECEDENTS", title_style),
        Paragraph("Act No. 1 of 1872 & Foundational Ratio Decidendi for Pre-Transition Cases<br/><b>Admissibility of Electronic Evidence, Section 27 Discovery & Landmark Rulings</b>", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#065F46'), spaceAfter=10),

        Paragraph("Section 25, 26 & 27 IEA (Confessions to Police & Discovery of Fact)", sec_title),
        Paragraph("Section 25 bars proof of confessions made to police officers. Section 26 bars confessions made in police custody unless in immediate presence of Magistrate. Section 27 operates as an exception: when any fact is discovered in consequence of information received from an accused in police custody, so much of such information as relates distinctly to the fact discovered may be proved (Pulukuri Kottaya doctrine).", body_style),

        Paragraph("Section 32(1) IEA (Dying Declaration)", sec_title),
        Paragraph("Statements, written or verbal, of relevant facts made by a person as to the cause of his death, or as to any of the circumstances of the transaction which resulted in his death, in cases in which the cause of that person's death comes into question, are admissible.", body_style),

        Paragraph("Section 65A & 65B IEA (Admissibility of Electronic Records & Mandatory Certificate)", sec_title),
        Paragraph("Electronic records can only be proved in accordance with Section 65B. Section 65B(4) mandates production of a certificate identifying the electronic record, describing the device, and signed by a person occupying a responsible official position. In Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal (2020) 7 SCC 1, a 3-Judge Bench held that a Section 65B(4) certificate is an absolute condition precedent to admissibility when the original optical/electronic device is not produced.", body_style),

        Paragraph("Section 101, 102 & 106 IEA (Burden of Proof)", sec_title),
        Paragraph("Section 101 establishes that whoever desires any court to give judgment as to any legal right dependent on the existence of facts which he asserts, must prove that those facts exist. Section 106 provides that when any fact is especially within the knowledge of any person, the burden of proving that fact is upon him.", body_style),

        Paragraph("Section 113A & 113B IEA (Presumptions: Suicide & Dowry Death)", sec_title),
        Paragraph("Section 113A permits presumption of abetment of suicide of a married woman within 7 years of marriage if cruelty under Section 498A IPC is proved. Section 113B provides a mandatory presumption of dowry death if woman was subjected to cruelty or harassment soon before death in connection with dowry.", body_style),

        Paragraph("State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335 (7 Quashing Guidelines)", sec_title),
        Paragraph("<b>Foundational 7 Categories for Quashing under Section 482 CrPC / Article 226:</b><br/>"
                  "(1) Allegations in FIR, even if taken at face value, do not prima facie constitute any offence.<br/>"
                  "(2) Allegations do not disclose a cognizable offence justifying investigation under Section 156(1).<br/>"
                  "(3) Uncontroverted allegations and evidence do not disclose commission of any offence.<br/>"
                  "(4) Allegations constitute only non-cognizable offence without Magistrate's order under Section 155(2).<br/>"
                  "(5) Allegations are so absurd and inherently improbable that no prudent person can reach a conclusion of ground.<br/>"
                  "(6) Express legal bar engrafted in the Code or Act to the institution/continuance of proceedings.<br/>"
                  "(7) Criminal proceeding is manifestly attended with mala fide and instituted with an ulterior motive for wreaking vengeance.", body_style),

        Paragraph("Gurbaksh Singh Sibbia v. State of Punjab, (1980) 2 SCC 565 (5-Judge Constitution Bench)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Section 438 CrPC confers extraordinary and discretionary power to protect personal liberty guaranteed under Article 21. Anticipatory bail cannot be fettered by conditions not warranted by the statute; it is not confined only to exceptional or rare cases, and broad general principles of judicial discretion must govern each case on its merits.", body_style),

        Paragraph("Sushila Aggarwal v. State (NCT of Delhi), (2020) 5 SCC 1 (5-Judge Constitution Bench)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Reaffirmed Sibbia. Held that anticipatory bail granted under Section 438 CrPC should not ordinarily be restricted or limited to a fixed period of time and can continue till the end of the trial unless special circumstances require temporal limitation.", body_style),

        Paragraph("Sharad Birdhichand Sarda v. State of Maharashtra, (1984) 4 SCC 116 (Panchsheel of Circumstantial Evidence)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Formulated the five golden principles (Panchsheel) governing circumstantial evidence in criminal trials: (1) Circumstances from which the conclusion of guilt is drawn must be fully established; (2) Facts established must be consistent only with the hypothesis of guilt; (3) Circumstances must be of conclusive nature and tendency; (4) Must exclude every possible hypothesis except guilt; (5) Chain of evidence must be so complete as to leave no reasonable ground for innocence.", body_style),

        Paragraph("Pulukuri Kottaya v. King-Emperor, (1947) LR 74 IA 65 (Privy Council)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Settled the scope of Section 27 Evidence Act: only that part of the statement which distinctly leads to the discovery of the physical fact (e.g., hidden weapon or property) is admissible; confessions of past guilt (e.g., 'I killed X with this knife') are severed and excluded.", body_style),

        Paragraph("Maneka Gandhi v. Union of India, (1978) 1 SCC 248 (7-Judge Constitution Bench)", sec_title),
        Paragraph("<b>Core Ratio Decidendi:</b> Landmark expansion of Article 21: 'procedure established by law' must not be arbitrary, fanciful or oppressive; it must be just, fair and reasonable, incorporating the principles of natural justice into criminal procedural actions.", body_style),
    ]

    doc.build(story)
    print(f"Generated IEA & Historic Precedents PDF: {output_path}")


def main():
    print("Generating comprehensive legacy legal reference PDFs...")
    ipc_pdf = UPLOAD_DIR / "Indian_Penal_Code_IPC_1860_Core_Provisions.pdf"
    crpc_pdf = UPLOAD_DIR / "Code_of_Criminal_Procedure_CrPC_1973_Core_Provisions.pdf"
    iea_pdf = UPLOAD_DIR / "Indian_Evidence_Act_IEA_1872_and_Historic_Precedents.pdf"

    create_ipc_legacy_pdf(ipc_pdf)
    create_crpc_legacy_pdf(crpc_pdf)
    create_iea_and_historic_precedents_pdf(iea_pdf)

    print("\nIngesting legacy PDFs into NirnayX ChromaDB & document registry...")
    docs_to_ingest = [
        ("Indian_Penal_Code_IPC_1860_Core_Provisions.pdf", ipc_pdf, "statute"),
        ("Code_of_Criminal_Procedure_CrPC_1973_Core_Provisions.pdf", crpc_pdf, "statute"),
        ("Indian_Evidence_Act_IEA_1872_and_Historic_Precedents.pdf", iea_pdf, "judgment"),
    ]

    for filename, path, doc_type in docs_to_ingest:
        print(f"Ingesting {filename} as {doc_type}...")
        res = ingest_document(str(path), filename)
        print(f"  Result: doc_id={res.get('doc_id')}, chunks={res.get('chunks_count')}, sections={len(res.get('sections_cited', []))}")

    print("\nAll legacy statutory codes and landmark historic precedents successfully ingested!")


if __name__ == "__main__":
    main()
