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

    genai.configure(api_key=settings.gemini_api_key)
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
    )

    return {
        "answer": response.text,
        "usage": {"model": settings.gemini_model},
    }


def generate_response(
    query: str,
    context_chunks: list[dict],
    persona: str = "citizen",
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Generate a grounded legal response using the configured LLM provider.

    Args:
        query: User's natural language legal question
        context_chunks: Retrieved chunks from vector store (grounding context)
        persona: "citizen" for plain language, "advocate" for technical
        chat_history: Previous conversation messages for multi-turn context

    Returns:
        Dict with keys: answer, usage, sources_used
    """
    provider = settings.llm_provider.lower()

    logger.info(
        f"Generating response | Provider: {provider} | Persona: {persona} | "
        f"Context chunks: {len(context_chunks)} | Query length: {len(query)}"
    )

    try:
        if provider == "gemini" and settings.gemini_api_key:
            result = generate_gemini(query, context_chunks, persona, chat_history)
        elif provider == "openai" and settings.openai_api_key:
            result = generate_openai(query, context_chunks, persona, chat_history)
        else:
            # Fallback: try OpenAI first, then Gemini
            if settings.openai_api_key:
                result = generate_openai(query, context_chunks, persona, chat_history)
            elif settings.gemini_api_key:
                result = generate_gemini(query, context_chunks, persona, chat_history)
            else:
                return {
                    "answer": (
                        "⚠️ **No LLM API key configured.**\n\n"
                        "Please set either `OPENAI_API_KEY` or `GEMINI_API_KEY` in your `.env` file "
                        "to enable AI-powered legal analysis.\n\n"
                        "The retrieval pipeline is working correctly — the following context was found:\n\n"
                        + "\n---\n".join(
                            f"**Source {i+1}** (Score: {c.get('score', 'N/A')}):\n{c['text'][:300]}..."
                            for i, c in enumerate(context_chunks[:3])
                        )
                    ),
                    "usage": {"model": "none"},
                    "sources_used": len(context_chunks),
                }

        result["sources_used"] = len(context_chunks)
        return result

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return {
            "answer": f"❌ Error generating response: {str(e)}",
            "usage": {"model": "error"},
            "sources_used": len(context_chunks),
            "error": str(e),
        }
