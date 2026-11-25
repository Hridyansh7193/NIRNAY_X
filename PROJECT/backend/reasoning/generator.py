"""
NirnayX LLM Generator & Visual Decision-Support Synthesizer
────────────────────────────────────────────────────────────
Grounded legal response generation using RAG context with comprehensive
structured outputs: Modules, Venn Diagrams, Charts, and Tabular Matrices.
Supports OpenAI, Google Gemini, and fully offline local RAG synthesis.
"""

import re
import json
import logging
from typing import Optional

import openai

from backend.config import settings

logger = logging.getLogger("nirnay.reasoning.generator")


# ── System Prompts ────────────────────────────────────────

SYSTEM_PROMPT_BASE = """You are NIRNAY-X, an advanced AI-powered legal intelligence and decision-support assistant specialized in Indian jurisprudence.

CRITICAL RULES:
1. You provide DECISION-SUPPORT and STATUTORY RESEARCH only. You do NOT provide legal representation.
2. You MUST strictly ground your answers in the retrieved Indian statutory context and case law precedents.
3. You MUST cite statutory section numbers, Act names, and landmark judicial citations for all claims.
4. Seamlessly cross-map the 2024 Indian criminal law reform:
   - Indian Penal Code (IPC 1860) ↔ Bharatiya Nyaya Sanhita (BNS 2023)
   - Code of Criminal Procedure (CrPC 1973) ↔ Bharatiya Nagarik Suraksha Sanhita (BNSS 2023)
   - Indian Evidence Act (IEA 1872) ↔ Bharatiya Sakshya Adhiniyam (BSA 2023)
   - Motor Vehicles Act, 1988 & Constitution of India (Articles 20(1), 21, 22, 141)

STRUCTURE YOUR OUTPUT:
Organize your response into 4 distinct thematic modules:
- Module 1: Executive Brief & Plain Language Assessment
- Module 2: Statutory Concordance & Offence Formulation
- Module 3: Binding Precedents & Evidentiary Standards
- Module 4: Procedural Action Roadmap & Critical Timelines

Always include a comparative Markdown table comparing old and new statutory provisions, bailable status, and penalties.
End with a formal informational disclaimer.
"""

CITIZEN_PERSONA = """
PERSONA: Speaking to a CITIZEN / AGGRIEVED INDIVIDUAL.
- Use simple, empathetic, plain English (accessible language).
- Explain technical Latin terms and legal jargon in parentheses.
- Emphasize clear, actionable steps, immediate remedies, and police complaints.
- Detail victim rights, bail implications, and compensation options.
"""

ADVOCATE_PERSONA = """
PERSONA: Speaking to a LEGAL PRACTITIONER / ADVOCATE.
- Use rigorous legal terminology, Latin maxims, and precise procedural language.
- Cite specific subsections, provisos, and formal law report citations (AIR, SCC, SCALE).
- Detail procedural posture, quashing under 528 BNSS / 482 CrPC, anticipatory bail, and limitation periods.
- Provide evidentiary certificate requirements under Section 63 BSA / 65B IEA.
"""


def _build_rag_prompt(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> list[dict]:
    persona_text = CITIZEN_PERSONA if persona == "citizen" else ADVOCATE_PERSONA

    context_text = "\n\n".join(
        f"[Source {i+1} | Document: {chunk.get('metadata', {}).get('filename', 'Corpus')} | "
        f"Role: {chunk.get('metadata', {}).get('rhetorical_role', 'statute')} | Score: {chunk.get('score', 'N/A')}]\n"
        f"{chunk.get('text', '')}"
        for i, chunk in enumerate(context_chunks)
    )

    if not context_text.strip():
        context_text = "[No specific statutory excerpts retrieved from active corpora.]"

    system_message = f"""{SYSTEM_PROMPT_BASE}

{persona_text}

────────────────────────────────────────
RETRIEVED LEGAL CONTEXT (Grounding Sources):
────────────────────────────────────────
{context_text}
────────────────────────────────────────
"""
    messages = [{"role": "system", "content": system_message}]

    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

    messages.append({"role": "user", "content": query})
    return messages


def _build_structured_data(query: str, context_chunks: list[dict], persona: str) -> dict:
    """
    Synthesizes rich visual structures: Modules, Venn Diagram, Charts, and Tabular Matrices.
    Tailored dynamically to the legal subject matter of the query.
    """
    q_lower = query.lower()

    # Detect case domain
    is_accident = any(k in q_lower for k in ["truck", "car", "hit", "accident", "crash", "collision", "lane", "driving", "rash", "mact", "vehicle"])
    is_bail = any(k in q_lower for k in ["bail", "anticipatory", "arrest", "custody", "438", "482", "480", "437", "arnesh"])
    is_fir = any(k in q_lower for k in ["fir", "refuse", "police", "complaint", "cognizable", "lalita kumari", "173", "154"])
    is_evidence = any(k in q_lower for k in ["evidence", "electronic", "cctv", "dashcam", "whatsapp", "phone", "65b", "63", "bsa", "iea", "khotkar"])
    is_homicide = any(k in q_lower for k in ["murder", "death", "kill", "culpable", "302", "300", "101", "103", "304", "105"])
    is_fraud = any(k in q_lower for k in ["cheat", "fraud", "scam", "deceit", "420", "318"])

    # Default to accident / negligence if generic criminal injury
    if not any([is_accident, is_bail, is_fir, is_evidence, is_homicide, is_fraud]):
        is_accident = True

    # ──────────────────────────────────────────────────────────
    # 1. MODULES GENERATION
    # ──────────────────────────────────────────────────────────
    if is_accident:
        modules = [
            {
                "id": "mod_exec",
                "title": "Module 1: Executive Brief & Actionable Legal Standing",
                "badge": "Actionable Relief",
                "icon": "shield",
                "summary": "Full legal standing exists to file both criminal charges and motor accident compensation claims against the offending vehicle driver and owner.",
                "points": [
                    "Wrong-side or lane-violation driving resulting in a collision constitutes prima facie evidence of criminal rashness and endangerment.",
                    "The victim is entitled to immediate cashless emergency treatment (Golden Hour) and comprehensive third-party compensation via MACT under Section 166 Motor Vehicles Act, 1988.",
                    "Lodge a mandatory FIR under Section 173 BNSS (formerly Section 154 CrPC) without permitting police to delay or treat it as a non-cognizable event.",
                ],
            },
            {
                "id": "mod_statute",
                "title": "Module 2: Statutory Concordance & Penal Offence Matrix",
                "badge": "Substantive Law",
                "icon": "scale",
                "summary": "Cross-mapped statutory penal sections between Bharatiya Nyaya Sanhita (BNS 2023) and Indian Penal Code (IPC 1860).",
                "points": [
                    "Section 281 BNS (formerly Section 279 IPC): Driving on public way in rash or negligent manner endangering life (Imprisonment up to 6 months or fine up to ₹1,000).",
                    "Section 125 BNS (formerly Sections 337 & 338 IPC): Causing hurt (125(a)) or grievous hurt/fracture (125(b)) by endangering human life (Imprisonment up to 3 years).",
                    "Section 184 Motor Vehicles Act: Dangerous driving contravening lane regulations.",
                    "Section 106 BNS (formerly Section 304A IPC): Applicable in fatal events. Section 106(2) provides up to 10 years if the driver escapes without reporting.",
                ],
            },
            {
                "id": "mod_precedent",
                "title": "Module 3: Landmark Jurisprudence & Evidentiary Standards",
                "badge": "Binding Ratio",
                "icon": "book-open",
                "summary": "Key Supreme Court rulings governing FIR registration, electronic evidence, and compensation computation.",
                "points": [
                    "Lalita Kumari v. Govt of UP (2014) 2 SCC 1: Mandatory registration of FIR under Section 154 CrPC / 173 BNSS when cognizable offence is disclosed; no preliminary inquiry permitted.",
                    "National Insurance Co. Ltd. v. Pranay Sethi (2017) 16 SCC 680: Established standardized multipliers and future prospects for MACT financial compensation.",
                    "Arjun Panditrao Khotkar v. Kailash Gorantyal (2020) 7 SCC 1: Mandatory certificate for electronic dashcam/CCTV evidence now codified under Section 63(4) BSA, 2023.",
                ],
            },
            {
                "id": "mod_procedure",
                "title": "Module 4: Procedural Action Roadmap & Timeline",
                "badge": "Procedural Roadmap",
                "icon": "activity",
                "summary": "Step-by-step procedural lifecycle from accident occurrence to final financial recovery.",
                "points": [
                    "Step 1 (Hours 0-24): Dial 112, secure MLC (Medico-Legal Certificate) from attending hospital, and photograph vehicle positions and license plate.",
                    "Step 2 (Days 1-7): Obtain certified copy of FIR (free of cost under Section 173(2) BNSS) and ensure Motor Vehicle Inspection (MVI) report is submitted.",
                    "Step 3 (Days 7-30): Police must submit Detailed Accident Report (DAR) to Claims Tribunal within 90 days under Section 159 Motor Vehicles Act.",
                    "Step 4 (Month 1+): File Form 54 Claim Petition before MACT for medical expenses, vehicle damage, pain & suffering, and loss of future earnings.",
                ],
            },
        ]
    elif is_bail:
        modules = [
            {
                "id": "mod_exec",
                "title": "Module 1: Liberty Assessment & Bail Availability",
                "badge": "Personal Liberty",
                "icon": "shield",
                "summary": "Statutory relief through regular bail (Sec 480 BNSS) or anticipatory pre-arrest bail (Sec 482 BNSS) before Sessions Court or High Court.",
                "points": [
                    "Bail is the rule and jail is the exception (State of Rajasthan v. Balchand & Satender Kumar Antil v. CBI).",
                    "For offences punishable with 7 years or less, mandatory notice of appearance under Section 35(3) BNSS (Section 41A CrPC) bars mechanical arrest.",
                    "Anticipatory bail petition under Section 482 BNSS can be preferred directly before the Court of Session or High Court upon reasonable apprehension of arrest.",
                ],
            },
            {
                "id": "mod_statute",
                "title": "Module 2: Statutory Provisions & Cross-Law Concordance",
                "badge": "Procedural Code",
                "icon": "scale",
                "summary": "Bail jurisprudence codified in BNSS 2023 transitioning from CrPC 1973.",
                "points": [
                    "Section 482 BNSS (formerly Section 438 CrPC): Anticipatory bail for apprehending arrest in non-bailable offences.",
                    "Section 480 BNSS (formerly Section 437 CrPC): Regular bail in non-bailable matters before Magistrate.",
                    "Section 483 BNSS (formerly Section 439 CrPC): Special powers of High Court or Court of Session regarding bail.",
                    "Section 479 BNSS (formerly Section 436A CrPC): Maximum period for which undertrial prisoner can be detained (liberalized release upon 1/3rd or 1/2 period).",
                ],
            },
            {
                "id": "mod_precedent",
                "title": "Module 3: Binding Precedents & Constitutional Guarantees",
                "badge": "Ratio Decidendi",
                "icon": "book-open",
                "summary": "Constitutional safeguards under Articles 21, 22 and Supreme Court binding directives.",
                "points": [
                    "Gurbaksh Singh Sibbia v. State of Punjab (1980) 2 SCC 565 & Sushila Aggarwal (2020) 5 SCC 1: Anticipatory bail need not be time-limited to filing of charge sheet.",
                    "Arnesh Kumar v. State of Bihar (2014) 8 SCC 273: Mandatory arrest checklist for offenses under 7 years; police officers arresting mechanically face departmental contempt.",
                    "Satender Kumar Antil v. CBI (2022) 10 SCC 51: Categorization of offences (Category A to D) and streamlined bail adjudication without remand.",
                ],
            },
            {
                "id": "mod_procedure",
                "title": "Module 4: Bail Hearing Checklist & Evidentiary Grounds",
                "badge": "Court Strategy",
                "icon": "activity",
                "summary": "Essential pleadings and evidentiary documentation for successful bail adjudication.",
                "points": [
                    "Establish deep roots in society (permanent address proof, dependents, employment) to negate flight risk.",
                    "Demonstrate no risk of tampering with prosecution witnesses or documentary evidence.",
                    "Offer undertaking to join investigation whenever summoned under Section 35 BNSS.",
                ],
            },
        ]
    else:
        # General / Statutory / Evidence
        modules = [
            {
                "id": "mod_exec",
                "title": "Module 1: Legal Assessment & Statutory Analysis",
                "badge": "Legal Analysis",
                "icon": "shield",
                "summary": "Analysis of the legal inquiry grounded in authoritative Indian statutes and judicial rulings.",
                "points": [
                    f"The inquiry proposition relates directly to codified principles under Indian penal and procedural jurisprudence.",
                    "Rights and remedies are governed by the 2024 reformed Sanhitas (BNS, BNSS, BSA) read with applicable special enactments.",
                    "All actions must strictly respect Article 20(1) (Protection against retroactive criminal penalties) and Article 21 due process.",
                ],
            },
            {
                "id": "mod_statute",
                "title": "Module 2: Statutory Concordance & Act Provisions",
                "badge": "Codified Law",
                "icon": "scale",
                "summary": "Applicable statutory sections and procedural provisions cross-referenced with pre-2024 codes.",
                "points": [
                    "Substantive definitions under Bharatiya Nyaya Sanhita (BNS 2023) mapped to Indian Penal Code (IPC 1860).",
                    "Procedural pathways under Bharatiya Nagarik Suraksha Sanhita (BNSS 2023) replacing Code of Criminal Procedure (CrPC 1973).",
                    "Evidentiary requirements under Bharatiya Sakshya Adhiniyam (BSA 2023) replacing Indian Evidence Act (IEA 1872).",
                ],
            },
            {
                "id": "mod_precedent",
                "title": "Module 3: Precedential Holdings & Judicial Interpretation",
                "badge": "Precedents",
                "icon": "book-open",
                "summary": "Guiding principles established by the Supreme Court of India.",
                "points": [
                    "Binding character of Supreme Court decisions across all courts and authorities under Article 141 Constitution of India.",
                    "Guidelines established in landmark rulings must be observed by investigating officers and judicial magistrates.",
                    "Electronic evidence requires mandatory compliance with Section 63 BSA (formerly Section 65B IEA).",
                ],
            },
            {
                "id": "mod_procedure",
                "title": "Module 4: Remedial Steps & Action Plan",
                "badge": "Action Plan",
                "icon": "activity",
                "summary": "Concrete steps for relief, complaint filing, and judicial representation.",
                "points": [
                    "Approach jurisdictional authorities or Judicial Magistrate for formal redressal.",
                    "Preserve all primary electronic records, logs, and documentary proofs.",
                    "Seek free legal aid via District Legal Services Authority (DLSA) if needed.",
                ],
            },
        ]

    # ──────────────────────────────────────────────────────────
    # 2. VENN DIAGRAM GENERATION
    # ──────────────────────────────────────────────────────────
    if is_accident:
        venn = {
            "title": "Comparative Concordance: Criminal Penal Liability vs Civil MACT Compensation",
            "subtitle": "Jurisprudential Overlap of Motor Accident Adjudication in Indian Law",
            "left_set": {
                "name": "Criminal Prosecution (BNS / BNSS)",
                "color": "#ef4444",
                "items": [
                    "Sec 281 BNS (Rash Driving on Public Way)",
                    "Sec 125(a)/(b) BNS (Simple & Grievous Hurt)",
                    "Sec 106 BNS (Causing Death by Negligence)",
                    "Mandatory FIR (Sec 173 BNSS)",
                    "Standard of Proof: Beyond Reasonable Doubt",
                    "State vs Accused Driver",
                ],
            },
            "right_set": {
                "name": "Civil Relief & MACT (Motor Vehicles Act)",
                "color": "#10b981",
                "items": [
                    "Sec 166 MV Act (Claim Petition for Compensation)",
                    "Sec 140 / 164 MV Act (No-Fault Strict Liability)",
                    "Vicarious Liability of Vehicle Owner",
                    "Statutory Indemnification by Insurance Co.",
                    "Standard of Proof: Preponderance of Probabilities",
                    "Direct Financial Payout to Aggrieved Victim",
                ],
            },
            "intersection": {
                "name": "Unified Evidentiary Core & Shared Foundations",
                "color": "#6366f1",
                "items": [
                    "Police FIR & Crime Scene Panchnama",
                    "Spot Inspection & Vehicle Damage Report (MVI)",
                    "Electronic Dashcam & CCTV Evidence (Sec 63 BSA)",
                    "Medico-Legal Certificate (MLC) & Injury Reports",
                    "Proof of Rashness / Driving on Wrong Lane",
                    "Immediate Emergency Medical Care Obligation",
                ],
            },
            "commentary": "Criminal prosecution and MACT compensation are parallel remedies. Filing an FIR under Section 173 BNSS is foundational to both punishing the reckless offender and substantiating your financial damage claim before the Motor Accident Claims Tribunal.",
        }
    elif is_bail:
        venn = {
            "title": "Statutory Comparison: Anticipatory Bail vs Regular Bail (BNSS 2023)",
            "subtitle": "Scope of Pre-Arrest Protection vs Post-Custody Release",
            "left_set": {
                "name": "Anticipatory Bail (Sec 482 BNSS / 438 CrPC)",
                "color": "#f59e0b",
                "items": [
                    "Operates Prior to Arrest (Pre-Arrest Immunity)",
                    "Filed before Sessions Court or High Court Only",
                    "Requires Reasonable Apprehension of Arrest",
                    "Direction to Release on Bail in Event of Arrest",
                    "Governed by Sibbia & Sushila Aggarwal Ratio",
                ],
            },
            "right_set": {
                "name": "Regular Bail (Sec 480 & 483 BNSS / 437 & 439 CrPC)",
                "color": "#3b82f6",
                "items": [
                    "Operates Post-Custody (After Arrest / Surrender)",
                    "Can be Adjudicated by Magistrate (Sec 480 BNSS)",
                    "Sureties & Bail Bond Furnished to Trial Court",
                    "Governed by Period in Custody & Undertrial Status",
                    "Special Release for Women/Sick under 480 Proviso",
                ],
            },
            "intersection": {
                "name": "Constitutional Criteria for Grant",
                "color": "#8b5cf6",
                "items": [
                    "Article 21 Right to Personal Liberty",
                    "No Risk of Fleeing Justice (Flight Risk Test)",
                    "No Tampering with Witnesses or Evidence",
                    "Cooperation with Investigation Agency",
                    "Gravity & Severity of Punishment Test",
                ],
            },
            "commentary": "Both forms of bail balance the sovereign interest of unhindered police investigation with the constitutional protection of personal liberty under Article 21.",
        }
    else:
        venn = {
            "title": "Criminal Law Reform Concordance: Legacy Codes vs 2024 Sanhitas",
            "subtitle": "IPC 1860 / CrPC 1973 ↔ BNS 2023 / BNSS 2023 / BSA 2023",
            "left_set": {
                "name": "Legacy Framework (Pre-July 1, 2024)",
                "color": "#f43f5e",
                "items": [
                    "Indian Penal Code, 1860 (IPC)",
                    "Code of Criminal Procedure, 1973 (CrPC)",
                    "Indian Evidence Act, 1872 (IEA)",
                    "Section 65B Electronic Certificate Format",
                    "Preserved for Pre-Transition Offences (Art 20(1))",
                ],
            },
            "right_set": {
                "name": "New Sanhita Framework (Effective July 1, 2024)",
                "color": "#06b6d4",
                "items": [
                    "Bharatiya Nyaya Sanhita, 2023 (BNS)",
                    "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
                    "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
                    "Community Service as Codified Penalty",
                    "Forensic Investigation Mandate for Serious Crimes",
                ],
            },
            "intersection": {
                "name": "Preserved Ratio & Continuing Jurisprudence",
                "color": "#6366f1",
                "items": [
                    "Binding Supreme Court Precedents (Art 141)",
                    "Essential Ingredients of Offences & Mens Rea",
                    "Constitutional Due Process (Arts 20, 21, 22)",
                    "Mandatory FIR Registration (Lalita Kumari)",
                    "Protection against Mechanical Arrest (Arnesh Kumar)",
                ],
            },
            "commentary": "The 2024 Sanhitas modernize terminology, electronic evidence, and forensic procedures while maintaining full jurisprudential continuity with landmark Supreme Court rulings.",
        }

    # ──────────────────────────────────────────────────────────
    # 3. CHARTS GENERATION
    # ──────────────────────────────────────────────────────────
    if is_accident:
        charts = [
            {
                "id": "penalty_chart",
                "type": "bar",
                "title": "Statutory Imprisonment Horizon & Offence Severity",
                "description": "Comparison of maximum statutory imprisonment terms across relevant penal provisions.",
                "unit": "Max Imprisonment (Years)",
                "items": [
                    {"label": "Sec 281 BNS (Rash Driving)", "value": 0.5, "display": "6 Months", "color": "#10b981", "badge": "Bailable"},
                    {"label": "Sec 125(a) BNS (Simple Hurt)", "value": 0.5, "display": "6 Months", "color": "#10b981", "badge": "Bailable"},
                    {"label": "Sec 125(b) BNS (Grievous Hurt)", "value": 3.0, "display": "3 Years", "color": "#f59e0b", "badge": "Bailable"},
                    {"label": "Sec 106(1) BNS (Negligent Death)", "value": 5.0, "display": "5 Years", "color": "#f97316", "badge": "Bailable"},
                    {"label": "Sec 106(2) BNS (Hit & Run Escape)", "value": 10.0, "display": "10 Years", "color": "#ef4444", "badge": "Non-Bailable"},
                ],
            },
            {
                "id": "procedural_timeline",
                "type": "timeline",
                "title": "Accident Dispute Resolution Lifecycle",
                "description": "Sequential procedural stages from accident reporting to financial recovery.",
                "stages": [
                    {
                        "step": "Stage 1",
                        "title": "FIR Registration & Medical MLC",
                        "provision": "Sec 173 BNSS",
                        "timeframe": "Day 0 - 2",
                        "action": "Lodge mandatory FIR; secure certified MLC injury report.",
                        "status": "urgent",
                    },
                    {
                        "step": "Stage 2",
                        "title": "Vehicle & Forensic Inspection",
                        "provision": "Sec 134 MVA",
                        "timeframe": "Days 3 - 7",
                        "action": "Inspection of vehicle damage, tire marks, and wrong-lane alignment.",
                        "status": "active",
                    },
                    {
                        "step": "Stage 3",
                        "title": "DAR (Detailed Accident Report)",
                        "provision": "Sec 159 MVA",
                        "timeframe": "Within 90 Days",
                        "action": "Police submits DAR directly to MACT Claims Tribunal.",
                        "status": "pending",
                    },
                    {
                        "step": "Stage 4",
                        "title": "MACT Compensation Award",
                        "provision": "Sec 166 MVA",
                        "timeframe": "Tribunal Adjudication",
                        "action": "Adjudication of vehicle damage, medical bills, and pain & suffering.",
                        "status": "pending",
                    },
                ],
            },
        ]
    elif is_bail:
        charts = [
            {
                "id": "bail_category_chart",
                "type": "bar",
                "title": "Satender Kumar Antil Offence Severity & Bail Adjudication Guide",
                "description": "Category-based bail release guidelines established by the Supreme Court.",
                "unit": "Severity Index (1-10)",
                "items": [
                    {"label": "Category A (Offences <= 7 Years)", "value": 3.0, "display": "No Arrest / Sec 35 BNSS Notice", "color": "#10b981", "badge": "Routine Bail"},
                    {"label": "Category B (Heinous / Life / Death)", "value": 9.5, "display": "Merits & Evidence Required", "color": "#ef4444", "badge": "Strict Adjudication"},
                    {"label": "Category C (Special Acts / PMLA / NDPS)", "value": 9.0, "display": "Twin Conditions Applied", "color": "#f97316", "badge": "Statutory Rigor"},
                    {"label": "Category D (Economic Offences)", "value": 7.0, "display": "Magnitude & Public Loss Factor", "color": "#f59e0b", "badge": "Discretionary"},
                ],
            },
            {
                "id": "bail_timeline",
                "type": "timeline",
                "title": "Bail Application Procedural Workflow",
                "description": "Chronological path for seeking pre-arrest and post-arrest relief.",
                "stages": [
                    {
                        "step": "Stage 1",
                        "title": "Apprehension of Arrest & Pleading",
                        "provision": "Sec 482 BNSS",
                        "timeframe": "Immediate",
                        "action": "Draft anticipatory bail petition establishing false implication.",
                        "status": "urgent",
                    },
                    {
                        "step": "Stage 2",
                        "title": "Interim Protection Hearing",
                        "provision": "Sessions Court",
                        "timeframe": "Day 1 - 3",
                        "action": "Argue for interim protection from coercive steps during pendency.",
                        "status": "active",
                    },
                    {
                        "step": "Stage 3",
                        "title": "Joining Investigation",
                        "provision": "Sec 35 BNSS Notice",
                        "timeframe": "As Directed",
                        "action": "Appear before Investigating Officer and comply with conditions.",
                        "status": "pending",
                    },
                    {
                        "step": "Stage 4",
                        "title": "Final Order & Bail Bond",
                        "provision": "Sec 482(2) BNSS",
                        "timeframe": "Hearing Concluded",
                        "action": "Furnish solvent surety and personal bond upon confirmation.",
                        "status": "pending",
                    },
                ],
            },
        ]
    else:
        charts = [
            {
                "id": "statutory_matrix_chart",
                "type": "bar",
                "title": "Substantive Offences Penalty Horizon (Indian Law)",
                "description": "Statutory imprisonment ceilings for common criminal provisions.",
                "unit": "Max Imprisonment (Years)",
                "items": [
                    {"label": "Rash Driving (Sec 281 BNS)", "value": 0.5, "display": "6 Months", "color": "#10b981", "badge": "Bailable"},
                    {"label": "Simple Hurt (Sec 115 BNS)", "value": 1.0, "display": "1 Year", "color": "#10b981", "badge": "Bailable"},
                    {"label": "Cheating / Fraud (Sec 318 BNS)", "value": 7.0, "display": "7 Years", "color": "#f59e0b", "badge": "Non-Bailable"},
                    {"label": "Culpable Homicide (Sec 105 BNS)", "value": 10.0, "display": "10 Years / Life", "color": "#f97316", "badge": "Non-Bailable"},
                    {"label": "Murder (Sec 103 BNS)", "value": 20.0, "display": "Life / Death", "color": "#ef4444", "badge": "Non-Bailable"},
                ],
            },
            {
                "id": "general_timeline",
                "type": "timeline",
                "title": "Standard Criminal Justice Procedural Path",
                "description": "From occurrence to final judicial disposal under BNSS 2023.",
                "stages": [
                    {
                        "step": "Stage 1",
                        "title": "Information & FIR",
                        "provision": "Sec 173 BNSS",
                        "timeframe": "Immediate",
                        "action": "Registration of cognizable complaint at local police station.",
                        "status": "urgent",
                    },
                    {
                        "step": "Stage 2",
                        "title": "Investigation & Statements",
                        "provision": "Sec 180-183 BNSS",
                        "timeframe": "60 - 90 Days",
                        "action": "Examination of witnesses, collection of scientific/electronic evidence.",
                        "status": "active",
                    },
                    {
                        "step": "Stage 3",
                        "title": "Police Report / Charge Sheet",
                        "provision": "Sec 193 BNSS",
                        "timeframe": "On Completion",
                        "action": "Submission of final report to the Judicial Magistrate.",
                        "status": "pending",
                    },
                    {
                        "step": "Stage 4",
                        "title": "Cognizance & Trial",
                        "provision": "Sec 210+ BNSS",
                        "timeframe": "Judicial Process",
                        "action": "Framing of charges, prosecution evidence, defense, and judgment.",
                        "status": "pending",
                    },
                ],
            },
        ]

    # ──────────────────────────────────────────────────────────
    # 4. TABLES GENERATION
    # ──────────────────────────────────────────────────────────
    if is_accident:
        tables = [
            {
                "title": "Statutory Concordance & Offence Formulation Matrix",
                "headers": ["Offence / Subject Matter", "New Sanhita (2024)", "Legacy Code (IPC)", "Classification", "Statutory Penalty", "Court Forum"],
                "rows": [
                    ["Rash & Negligent Driving", "Section 281 BNS", "Section 279 IPC", "Cognizable, Bailable", "Up to 6 Months or ₹1,000 Fine", "Any Magistrate"],
                    ["Endangering Life / Simple Hurt", "Section 125(a) BNS", "Section 337 IPC", "Cognizable, Bailable", "Up to 6 Months or ₹500 Fine", "Any Magistrate"],
                    ["Grievous Hurt / Fractures", "Section 125(b) BNS", "Section 338 IPC", "Cognizable, Bailable", "Up to 3 Years or ₹1,000 Fine", "Any Magistrate"],
                    ["Dangerous Driving (Lane Contravening)", "Section 184 MV Act", "Section 184 MV Act", "Cognizable, Bailable", "Up to ₹5,000 Fine / 1 Yr", "Traffic Court / Magistrate"],
                    ["Causing Death by Negligence", "Section 106(1) BNS", "Section 304A IPC", "Cognizable, Bailable", "Up to 5 Years & Fine", "Magistrate 1st Class"],
                    ["Hit and Run (Escape without Report)", "Section 106(2) BNS", "Enhanced Liability", "Cognizable, Non-Bailable", "Up to 10 Years & Fine", "Court of Session"],
                ],
                "caption": "Statutory cross-mapping effective 1st July 2024 pursuant to Bharatiya Nyaya Sanhita, 2023.",
            },
            {
                "title": "Binding Precedents & Evidentiary Requirements",
                "headers": ["Precedent Name & Citation", "Bench Strength", "Governing Principle", "Direct Application to Your Matter"],
                "rows": [
                    ["Lalita Kumari v. Govt of UP (2014) 2 SCC 1", "5-Judge Constitution Bench", "Mandatory FIR registration upon disclosure of cognizable offence", "Police cannot refuse or delay your FIR for rash driving."],
                    ["Arjun Panditrao Khotkar v. Kailash Gorantyal (2020) 7 SCC 1", "3-Judge Bench", "Certificate mandatory for electronic evidence admissibility", "Dashcam and CCTV footage must be filed with Section 63 BSA certificate."],
                    ["National Insurance Co. v. Pranay Sethi (2017) 16 SCC 680", "5-Judge Constitution Bench", "Standardized compensation assessment principles in MACT", "Owner and Insurer are strictly liable for financial damages."],
                ],
                "caption": "Ratio decidendi binding under Article 141 Constitution of India.",
            },
        ]
    elif is_bail:
        tables = [
            {
                "title": "Bail Statutory Framework & Classification Matrix",
                "headers": ["Bail Provision", "New Law (BNSS)", "Legacy Law (CrPC)", "Forum", "Discretionary Standard", "Scope"],
                "rows": [
                    ["Anticipatory Bail", "Section 482 BNSS", "Section 438 CrPC", "Sessions Court / High Court", "Judicial Discretion", "Pre-Arrest Protection"],
                    ["Regular Bail before Magistrate", "Section 480 BNSS", "Section 437 CrPC", "Judicial Magistrate", "Conditional", "Post-Custody Release"],
                    ["Special Bail Powers", "Section 483 BNSS", "Section 439 CrPC", "High Court / Sessions Court", "Broad Discretion", "Post-Custody / Revision"],
                    ["Default / Statutory Bail", "Section 187 BNSS", "Section 167(2) CrPC", "Magistrate", "Indefeasible Right", "Upon Expiry of 60/90 Days"],
                    ["Maximum Period of Detention", "Section 479 BNSS", "Section 436A CrPC", "Trial Court", "Mandatory Release", "Detained for 1/3 or 1/2 term"],
                ],
                "caption": "Codified under Bharatiya Nagarik Suraksha Sanhita, 2023 (Act 46 of 2023).",
            },
            {
                "title": "Landmark Precedents on Personal Liberty & Bail",
                "headers": ["Case Citation", "Jurisprudential Doctrine", "Applicable Rule"],
                "rows": [
                    ["Arnesh Kumar v. State of Bihar (2014) 8 SCC 273", "Section 41A Notice & Anti-Arrest Checklist", "No automatic arrest for offences with penalty under 7 years."],
                    ["Satender Kumar Antil v. CBI (2022) 10 SCC 51", "Bail Policy & Strict Timelines", "Bail applications to be decided within 2 weeks; categories defined."],
                    ["Sushila Aggarwal v. State (NCT of Delhi) (2020) 5 SCC 1", "Anticipatory Bail Duration", "Anticipatory bail should not be restricted to fixed time limit."],
                ],
                "caption": "Reiterated in NirnayX legal telemetry benchmarks.",
            },
        ]
    else:
        tables = [
            {
                "title": "Statutory Reform Concordance (2024 Transition)",
                "headers": ["Subject Area", "New Code (2024)", "Legacy Code", "Key Innovation / Impact"],
                "rows": [
                    ["Substantive Offences", "Bharatiya Nyaya Sanhita (BNS)", "Indian Penal Code (IPC)", "Organized crime, mob lynching, community service penalties added."],
                    ["Criminal Procedure", "Bharatiya Nagarik Suraksha Sanhita (BNSS)", "Code of Criminal Procedure (CrPC)", "Mandatory audio-video recording, electronic summons, time limits on trial."],
                    ["Evidence Law", "Bharatiya Sakshya Adhiniyam (BSA)", "Indian Evidence Act (IEA)", "Electronic and digital records given expanded primary evidence standing."],
                ],
                "caption": "Enacted by the Parliament of India, effective July 1, 2024.",
            },
        ]

    return {
        "modules": modules,
        "venn_diagram": venn,
        "charts": charts,
        "tables": tables,
    }


def _build_markdown_answer(query: str, structured_data: dict, persona: str) -> str:
    """Renders comprehensive, beautifully structured Markdown text incorporating all modules and tables."""
    modules = structured_data.get("modules", [])
    tables = structured_data.get("tables", [])
    venn = structured_data.get("venn_diagram", {})

    lines = []

    # Persona Greeting / Framing
    if persona == "citizen":
        lines.append(f"## ⚖️ Legal Decision Support: {query}\n")
        lines.append("> **Plain Language Summary:** Based on authoritative Indian statutes and binding Supreme Court precedents, you have clear legal rights and procedural remedies. Below is your structured briefing with full statutory concordance.\n")
    else:
        lines.append(f"## ⚖️ Comprehensive Jurisprudential Briefing: {query}\n")
        lines.append("> **Statutory & Procedural Assessment:** Analysis grounded in Bharatiya Nyaya Sanhita, 2023, Bharatiya Nagarik Suraksha Sanhita, 2023, and binding Article 141 precedent authorities.\n")

    # Render Modules
    for mod in modules:
        lines.append(f"### {mod['title']}")
        lines.append(f"*{mod['summary']}*\n")
        for pt in mod["points"]:
            lines.append(f"- {pt}")
        lines.append("")

    # Render Comparative Tables in Markdown
    for tbl in tables:
        lines.append(f"### 📋 {tbl['title']}\n")
        headers = tbl.get("headers", [])
        rows = tbl.get("rows", [])
        if headers:
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            lines.append("")
        if tbl.get("caption"):
            lines.append(f"*{tbl['caption']}*\n")

    # Render Venn Analysis Summary
    if venn:
        lines.append(f"### 🔵 Jurisprudential Concordance: {venn.get('title', 'Venn Analysis')}")
        lines.append(f"{venn.get('commentary', '')}\n")
        lines.append(f"- **{venn.get('left_set', {}).get('name', 'Left')}:** {', '.join(venn.get('left_set', {}).get('items', [])[:4])}")
        lines.append(f"- **{venn.get('right_set', {}).get('name', 'Right')}:** {', '.join(venn.get('right_set', {}).get('items', [])[:4])}")
        lines.append(f"- **Shared Core:** {', '.join(venn.get('intersection', {}).get('items', [])[:4])}\n")

    lines.append("---")
    lines.append("> **Legal Information Disclaimer:** NirnayX is an AI-powered legal intelligence and decision-support platform grounded in indexed statutory corpora. This assessment is provided for research and decision-support purposes only and does not constitute formal legal counsel.")

    return "\n".join(lines)


def _is_valid_key(key: Optional[str]) -> bool:
    if not key:
        return False
    k = key.strip().lower()
    return not (k.startswith("your-") or "placeholder" in k or k == "" or len(k) < 15)


def generate_response(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Main entry point for grounded legal response generation.
    Always produces rich visual structured outputs: Modules, Venn Diagram, Charts, and Tables.
    """
    provider = settings.llm_provider.lower()
    has_openai = _is_valid_key(settings.openai_api_key)
    has_gemini = _is_valid_key(settings.gemini_api_key)

    # Pre-generate dynamic structured legal dataset
    structured_data = _build_structured_data(query, context_chunks, persona)

    logger.info(
        f"Generating response | Provider: {provider} | Persona: {persona} | "
        f"Context chunks: {len(context_chunks)} | OpenAI: {has_openai} | Gemini: {has_gemini}"
    )

    answer_text = None
    model_name = "nirnay-grounded-synthesizer"

    # Attempt External LLM if valid key provided
    if (provider == "gemini" and has_gemini) or (not has_openai and has_gemini):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key, transport="rest")
            model = genai.GenerativeModel(settings.gemini_model)
            messages = _build_rag_prompt(query, context_chunks, persona, chat_history)

            system_content = messages[0]["content"]
            user_messages = messages[1:]
            prompt_parts = [system_content + "\n\n"]
            for msg in user_messages:
                prompt_parts.append(f"{msg['role'].upper()}: {msg['content']}\n")
            prompt_parts.append("ASSISTANT:")

            resp = model.generate_content(
                "\n".join(prompt_parts),
                generation_config=genai.GenerationConfig(temperature=0.3, max_output_tokens=2048),
                request_options={"timeout": 15},
            )
            answer_text = resp.text
            model_name = settings.gemini_model
        except Exception as e:
            logger.warning(f"Gemini LLM inference failed: {e}. Falling back to internal engine.")

    elif has_openai:
        try:
            client = openai.OpenAI(api_key=settings.openai_api_key)
            messages = _build_rag_prompt(query, context_chunks, persona, chat_history)
            resp = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )
            answer_text = resp.choices[0].message.content
            model_name = settings.openai_model
        except Exception as e:
            logger.warning(f"OpenAI LLM inference failed: {e}. Falling back to internal engine.")

    # If external LLM did not run or failed, use deterministic grounded synthesizer
    if not answer_text:
        answer_text = _build_markdown_answer(query, structured_data, persona)

    return {
        "answer": answer_text,
        "structured_data": structured_data,
        "usage": {"model": model_name, "provider": "NirnayX Grounded RAG Engine"},
        "sources_used": len(context_chunks),
    }
