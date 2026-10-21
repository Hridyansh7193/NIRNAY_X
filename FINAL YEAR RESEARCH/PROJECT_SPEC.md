# NIRNAY-X: Research Specification & System Overview

> **Project:** Nirnay-X (AI-Powered Legal Intelligence Platform)  
> **Institution:** Ajay Kumar Garg Engineering College (AKGEC), Ghaziabad  
> **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  
> **Department:** Computer Science & Engineering (B.Tech 2023–2027)  
> **Supervisor:** Ms. Bhumica (Assistant Professor, Dept. of CSE)  
> **Team Members:**  
> - Rajat Pandey (2300270100138)  
> - Hridyansh Bhadauria (2300270100074)  
> - Raghav Mittal (2300270100133)  
> - Ragini Goel (2300270100134)  

---

## 1. Executive Summary & Core Objective

**Nirnay-X** is an AI-powered legal intelligence and decision-support platform designed to bridge the accessibility gap in the Indian legal ecosystem. The platform leverages Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), and semantic vector search to assist both:
1. **Common Citizens:** By translating complex legal jargon, FIRs, contracts, notices, and statutory provisions into accessible plain language, outlining potential remedies without replacing professional legal counsel.
2. **Legal Professionals:** By automating repetitive research, indexing case documents, retrieving relevant precedents and statutory provisions, summarizing judgments, and managing case hearing timelines.

> **Responsible AI Disclaimer:** Nirnay-X is strictly an informational and decision-support platform; it does not replace advocates, judges, or professional legal counsel.

---

## 2. Problem Statement & Technical Motivation

### Core Challenges Faced by Users:
- **Comprehension:** Difficulty deciphering dense, domain-specific statutory and judicial terminology.
- **Provision & Precedent Identification:** Inability to pinpoint applicable sections (e.g., IPC/BNS, CrPC/BNSS, CPC) and binding precedents.
- **Organization:** Fragmented case files across multiple hearings and proceedings.
- **Verification:** Susceptibility to hallucinated or fabricated legal advice from standalone generative models.

### Technical Gaps in Existing Solutions:
- **Semantic Blindness:** Keyword-based search fails to retrieve legally analogous cases with different phrasing.
- **Context Dependency & Hallucination:** Standalone LLMs lack deterministic grounding in authoritative Indian statutes and judicial records.

---

## 3. System Architecture & 11-Step RAG Pipeline

The technical core of Nirnay-X operates through an 11-stage modular RAG workflow:

```
[User Document Upload (PDF)]
            ↓
[OCR & Document Parsing]
            ↓
[Legally-Coherent Text Chunking]
            ↓
[Dense Embedding Generation]
            ↓
[Vector Database Storage (Indexed with Metadata)]
            ↓
[Natural-Language User Query] → [Query Embedding]
            ↓
[Semantic Similarity Search & Top-K Retrieval]
            ↓
[Grounding Context Formulation]
            ↓
[LLM Inference & Grounded Generation]
            ↓
[Grounded Answer + Verifiable Source Citations]
```

---

## 4. Platform Modules (11 Functional Components)

1. **RAG-Based Legal Assistant:** Context-grounded Q&A against uploaded case materials and legal corpora.
2. **Legal Document Processing:** PDF extraction, OCR handling for scanned files, metadata tagging.
3. **Simplified Legal Explanations:** Conversion of complex statutory texts into plain language for non-lawyers.
4. **Case Analysis & Fact Extraction:** Parsing key facts, dates, parties, and procedural posture.
5. **Legal Provision & Precedent Retrieval:** Surfacing applicable sections and analogous case laws.
6. **Document Summarization:** Abstractive and extractive summaries of lengthy judgments and petitions.
7. **Semantic Search Engine:** Concept-driven search across internal documents and legal statutes.
8. **Case Timeline & Deadline Tracking:** Chronological milestones, statute of limitations tracking.
9. **Hearing & Calendar Management:** Structured court calendar with notification support.
10. **Case Organization:** Multi-case workspace structuring and client record linking.
11. **Conversational Multi-Turn Interface:** Intuitive interactive dialogue interface.

---

## 5. Quantitative Evaluation Framework

Nirnay-X evaluates research outputs across three pillars:

### A. Information Retrieval Quality
- **Precision@K:** Proportion of retrieved chunks that are legally relevant.
- **Recall@K:** Proportion of all relevant case passages successfully retrieved.
- **Mean Reciprocal Rank (MRR):** Position of the first correct statutory provision or precedent.
- **NDCG (Normalized Discounted Cumulative Gain):** Quality of ranked retrieval with relevance weighting.

### B. Generation & Grounding Quality
- **Faithfulness:** Degree to which generated statements are supported by retrieved context (hallucination minimization).
- **Answer Relevance:** Directly addressing the user's explicit legal query.
- **Context Utilization:** Efficiency and completeness of retrieved chunk usage.
- **ROUGE / BLEU:** Lexical overlap benchmark for summarization quality against human-drafted legal summaries.

### C. SDG & Societal Alignment
- **SDG 16 (Primary):** Peace, Justice & Strong Institutions (expanding equitable access to legal knowledge).
- **SDG 9 (Secondary):** Industry, Innovation & Infrastructure (AI-driven digital legal infrastructure).
- **SDG 3 (Indirect):** Reduced acute stress stemming from legal uncertainty.

---

## 6. Target Publications & Dissemination

- **Conferences:** IEEE / Springer international conferences on NLP, AI applications, and Legal Tech.
- **Journals:** Scopus / SCI-indexed journals focusing on Knowledge-Based Systems and Legal Informatics.
