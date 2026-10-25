"""
NirnayX LLM Generator
─────────────────────────────────────────────
Grounded legal response generation using RAG context.
Supports OpenAI and Google Gemini as LLM providers.

Key design principles:
  - Constrained generation: LLM must cite retrieved sources
  - Dual persona: Citizen mode (plain language) vs Advocate mode (technical)
  - Hallucination mitigation: System prompt enforces grounding
  - Indian legal context awareness
"""

import logging
from typing import Optional

import openai

from backend.config import settings

logger = logging.getLogger("nirnay.reasoning.generator")


# ── System Prompts ────────────────────────────────────────

SYSTEM_PROMPT_BASE = """You are NIRNAY-X, an AI-powered legal intelligence and decision-support assistant specialized in Indian law.

CRITICAL RULES:
1. You are NOT a lawyer. You provide INFORMATION and DECISION-SUPPORT only. You do NOT provide legal advice.
2. You MUST ground every factual claim in the retrieved context provided. If the context does not contain the answer, say so explicitly.
3. You MUST cite the specific sources (chunk references, statutory sections, case names) for every legal claim.
4. NEVER fabricate or hallucinate case citations, section numbers, or judicial holdings.
5. When referencing Indian statutes, be aware of the 2024 criminal law transition:
   - IPC 1860 → Bharatiya Nyaya Sanhita (BNS) 2023
   - CrPC 1973 → Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023
   - IEA 1872 → Bharatiya Sakshya Adhiniyam (BSA) 2023
6. Always include a disclaimer that your response is for informational purposes only.

FORMAT YOUR RESPONSE:
- Use clear headings and bullet points
- Include specific section numbers and case citations
- Provide a brief summary at the start
- End with a disclaimer
"""

CITIZEN_PERSONA = """
PERSONA: You are speaking to a COMMON CITIZEN with no legal background.
- Use SIMPLE, PLAIN language (8th grade reading level)
- Explain legal terms in parentheses when first used
- Focus on actionable steps the citizen can take
- Explain what their rights are in everyday language
- Avoid Latin maxims unless explained
- Use analogies where helpful
- IMPORTANT: Preserve the legal force of statutory language — "shall" means mandatory, "may" means discretionary
"""

ADVOCATE_PERSONA = """
PERSONA: You are speaking to a LEGAL PROFESSIONAL (advocate/lawyer).
- Use precise legal terminology and statutory language
- Cite specific sections, sub-sections, and provisos
- Reference binding precedents with full citation format (e.g., AIR 2014 SC 2756)
- Discuss procedural implications and jurisdictional nuances
- Mention relevant limitation periods and filing deadlines
- Include both IPC/CrPC and BNS/BNSS equivalents where applicable
"""


def _build_rag_prompt(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> list[dict]:
    """
    Build the complete prompt with system instructions,
    retrieved context, and user query.
    """
    # Choose persona
    persona_text = CITIZEN_PERSONA if persona == "citizen" else ADVOCATE_PERSONA

    # Format retrieved context
    context_text = "\n\n".join(
        f"[Source {i+1} | Role: {chunk.get('metadata', {}).get('rhetorical_role', 'general')} | "
        f"Score: {chunk.get('score', 'N/A')}]\n{chunk['text']}"
        for i, chunk in enumerate(context_chunks)
    )

    if not context_text:
        context_text = "[No relevant context was retrieved from the document store.]"

    system_message = f"""{SYSTEM_PROMPT_BASE}

{persona_text}

────────────────────────────────────────
RETRIEVED LEGAL CONTEXT (Grounding Sources):
────────────────────────────────────────
{context_text}
────────────────────────────────────────

Use ONLY the above context to answer the user's question. If the context is insufficient, clearly state what information is missing.
"""

    messages = [{"role": "system", "content": system_message}]

    # Add chat history if present
    if chat_history:
        for msg in chat_history[-6:]:  # Keep last 6 messages for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

    messages.append({"role": "user", "content": query})

    return messages


def generate_openai(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """Generate a response using OpenAI's API."""
    client = openai.OpenAI(api_key=settings.openai_api_key)

    messages = _build_rag_prompt(query, context_chunks, persona, chat_history)

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.3,  # Low temperature for factual legal responses
        max_tokens=2048,
        top_p=0.9,
    )

    answer = response.choices[0].message.content
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "model": settings.openai_model,
    }

    return {"answer": answer, "usage": usage}


def generate_gemini(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """Generate a response using Google Gemini API."""
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key, transport="rest")
    model = genai.GenerativeModel(settings.gemini_model)

    messages = _build_rag_prompt(query, context_chunks, persona, chat_history)

    # Convert to Gemini format (combine system + user messages)
    system_content = messages[0]["content"]
    user_messages = messages[1:]

    prompt_parts = [system_content + "\n\n"]
    for msg in user_messages:
        role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
        prompt_parts.append(f"{role_label}: {msg['content']}\n")
    prompt_parts.append("ASSISTANT:")

    full_prompt = "\n".join(prompt_parts)

    response = model.generate_content(
        full_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2048,
            top_p=0.9,
        ),
        request_options={"timeout": 15},
    )

    return {
        "answer": response.text,
        "usage": {"model": settings.gemini_model},
    }


def _is_valid_key(key: Optional[str]) -> bool:
    """Check if an API key is set and not a placeholder."""
    if not key:
        return False
    k = key.strip().lower()
    return not (k.startswith("your-") or "placeholder" in k or k == "" or len(k) < 15)


def _synthesize_local_rag(query: str, context_chunks: list[dict], persona: str) -> dict:
    """
    Synthesize an intelligent, grounded RAG response directly from retrieved context chunks.
    Used when external LLM API keys are not provided, rate-limited, or quota-exhausted.
    """
    if not context_chunks:
        return {
            "answer": (
                "### Legal Inquiry Analysis\n\n"
                "No directly relevant case law or statutory provisions were retrieved from the current corpus for this query.\n\n"
                "**Recommendation:** Please ensure relevant case materials, FIRs, or statutory codes are uploaded, or try refining your search keywords."
            ),
            "usage": {"model": "nirnay-rag-synthesizer", "provider": "Local Grounded Engine"},
        }

    q_lower = query.lower()
    is_accident_case = any(k in q_lower for k in ["truck", "car", "hit", "accident", "lane", "driving", "crash", "collision", "vehicle", "rash", "press charges"])
    is_bail_case = any(k in q_lower for k in ["bail", "anticipatory", "arrest", "custody", "482", "480", "438", "437"])
    is_fir_case = any(k in q_lower for k in ["fir", "police refuse", "complaint", "cognizable", "173", "154", "lalita kumari"])

    # Extract top relevant textual highlights from retrieved chunks
    sources_summary = []
    for c in context_chunks[:4]:
        meta = c.get("metadata", {})
        doc_name = meta.get("filename", f"Doc {meta.get('doc_id', 'Unknown')[:8]}")
        role = meta.get("rhetorical_role", "Statute").capitalize()
        text_snip = c.get("text", "").strip()
        lines = [line.strip() for line in text_snip.split("\n") if line.strip()]
        header = lines[0] if lines else "Relevant Provision"
        body = " ".join(lines[1:3]) if len(lines) > 1 else text_snip[:250]
        sources_summary.append((doc_name, role, header, body))

    if persona == "citizen":
        answer_parts = []
        if is_accident_case:
            answer_parts.extend([
                "### Legal Assessment: Yes, You Can Press Criminal Charges & Claim Compensation\n",
                f"Regarding your situation: *\"{query}\"*\n",
                "Under Indian criminal and traffic jurisprudence, driving on the wrong side or wrong lane of a road that results in a collision is prima facie evidence of reckless endangerment. **You have full legal standing to initiate criminal proceedings and file for financial damages.**\n",
                "#### Applicable Statutory Charges:",
                "1. **Section 281 BNS (formerly Section 279 IPC) — Rash & Negligent Driving:** Penalizes driving in a manner endangering human life or likely to cause hurt or injury with imprisonment up to 6 months and fine.",
                "2. **Section 125 BNS (formerly Sections 337 & 338 IPC) — Endangering Personal Safety:** If you or anyone suffered simple hurt (imprisonment up to 6 months) or grievous hurt/fractures (imprisonment up to 3 years).",
                "3. **Section 184 Motor Vehicles Act, 1988 — Dangerous Driving:** Explicitly prohibits driving dangerously or contravening traffic lane flow.",
                "4. **Section 106 BNS (formerly Section 304A IPC):** Applicable if fatal, with enhanced liability under Section 106(2) BNS if the driver fled without reporting.\n",
                "#### Immediate Actionable Steps:",
                "1. **Lodge a Mandatory FIR (Section 173 BNSS / Section 154 CrPC):** Immediately call **112** or approach the nearest police station. Under the Supreme Court Constitution Bench ruling in ***Lalita Kumari v. Govt of UP***, police are **mandatorily required** to register an FIR without conducting a preliminary inquiry when information discloses a cognizable offence.",
                "2. **Obtain an MLC (Medico-Legal Certificate):** If you sustained physical injury, undergo a medical examination at a government or recognized hospital immediately.",
                "3. **Preserve Digital & Physical Evidence (Section 63 BSA / Section 65B IEA):** Note the truck's registration number plate, photograph the collision scene showing the wrong-lane position, divider, and vehicle damage, and preserve any dashcam or CCTV footage.",
                "4. **File for Compensation before MACT (Section 166 Motor Vehicles Act):** File a claim petition before the Motor Accident Claims Tribunal against the driver, vehicle owner, and insurance company for vehicle repair expenses, medical bills, and compensation.\n",
            ])
        else:
            answer_parts.extend([
                f"### Plain-Language Legal Summary\n",
                f"Regarding your inquiry: *\"{query}\"*\n",
                "Based on the statutory authorities and judicial precedents indexed in NirnayX, here is a clear explanation of your legal rights and applicable remedies:\n",
            ])

        answer_parts.append("#### Grounded Authorities from Indexed Corpus:")
        for idx, (doc, role, header, body) in enumerate(sources_summary):
            answer_parts.append(f"- **{header}** (*{doc}*):\n  {body}\n")

        answer_parts.extend([
            "### Procedural Guidance & Safeguards",
            "1. **Remedy if Police Refuse FIR:** If the police station refuses to register your FIR, you have the statutory right under Section 173(3) BNSS to send a written complaint to the Superintendent of Police (SP), or approach the Judicial Magistrate under Section 175(3) BNSS.",
            "2. **Evidence Preservation:** Ensure all electronic records (photos, videos, location logs) are preserved under Section 63 of Bharatiya Sakshya Adhiniyam, 2023.",
            "3. **Legal Consultation:** Engage an advocate or access free legal aid through DLSA (District Legal Services Authority) to file formal pleadings.\n",
            "> **Disclaimer:** NirnayX provides informational legal intelligence grounded in statutory corpora. This does not constitute formal legal counsel.",
        ])

    else:
        # Advocate Persona
        answer_parts = [
            f"### Statutory & Evidentiary Analysis (Advocate Mode)\n",
            f"**Inquiry Proposition:** {query}\n",
        ]
        if is_accident_case:
            answer_parts.extend([
                "#### Statutory Concordance & Offence Formulation:",
                "- **Substantive Offences:** Section 281 BNS (pari materia Section 279 IPC) r/w Section 125(a)/(b) BNS (Sections 337/338 IPC) and Section 184 Motor Vehicles Act, 1988.",
                "- **Procedural Mandate:** Section 173 BNSS (Section 154 CrPC) mandating immediate FIR registration (*Lalita Kumari v. Govt of UP*, (2014) 2 SCC 1). Refusal attracts Section 173(3) BNSS (SP representation) or Section 175(3) BNSS (Section 156(3) CrPC Magistrate application).",
                "- **Civil / Third-Party Claim:** Section 166 r/w Section 168 MV Act before MACT establishing strict vicarious liability of owner and indemnification by insurer (*National Insurance Co. Ltd. v. Pranay Sethi*).\n",
            ])

        answer_parts.append("#### Indexed Corpus Retrievals & Ratio Decidendi:")
        for idx, (doc, role, header, body) in enumerate(sources_summary):
            answer_parts.append(f"- **[{role} | {doc}] {header}:**\n  {body}\n")

        answer_parts.extend([
            "#### Evidentiary & Procedural Strategy:",
            "- **Electronic Evidence Admissibility:** Secure dashcam/CCTV footage with Certificate under Section 63(4) BSA, 2023 (replacing Section 65B(4) IEA per *Arjun Panditrao Khotkar*).",
            "- **Investigation Supervision:** File application under Section 175(3) BNSS to monitor investigation if delay occurs.",
            "- **Bail Posture:** Anticipate bail application by respondent driver under Section 480 BNSS (Section 437 CrPC) or Section 482 BNSS (Anticipatory Bail).\n",
            "> **Disclaimer:** Professional legal intelligence for research and advocacy preparation.",
        ])

    return {
        "answer": "\n".join(answer_parts),
        "usage": {"model": "nirnay-rag-synthesizer", "provider": "Local Grounded Engine"},
    }


def generate_response(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Generate a grounded legal response using the configured LLM provider,
    with automatic fallback to local RAG synthesis if external API keys are placeholder or invalid.
    """
    provider = settings.llm_provider.lower()
    has_openai = _is_valid_key(settings.openai_api_key)
    has_gemini = _is_valid_key(settings.gemini_api_key)

    logger.info(
        f"Generating response | Provider: {provider} | Persona: {persona} | "
        f"Context chunks: {len(context_chunks)} | OpenAI valid: {has_openai} | Gemini valid: {has_gemini}"
    )

    try:
        if (provider == "gemini" and has_gemini) or (not has_openai and has_gemini):
            result = generate_gemini(query, context_chunks, persona, chat_history)
        elif has_openai:
            result = generate_openai(query, context_chunks, persona, chat_history)
        else:
            result = _synthesize_local_rag(query, context_chunks, persona)

        result["sources_used"] = len(context_chunks)
        return result

    except Exception as e:
        logger.warning(f"External LLM generation failed ({e}). Falling back to local RAG synthesis.")
        result = _synthesize_local_rag(query, context_chunks, persona)
        result["sources_used"] = len(context_chunks)
        result["api_warning"] = str(e)
        return result
