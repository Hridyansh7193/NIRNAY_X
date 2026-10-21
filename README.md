# NIRNAY-X: AI-Powered Legal Intelligence & Decision-Support System

> **Ajay Kumar Garg Engineering College (AKGEC), Ghaziabad**  
> **Affiliated to:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  
> **Department:** Computer Science & Engineering (B.Tech 2023–2027)  
> **Supervisor:** Ms. Bhumica (Assistant Professor, Dept. of CSE)  
> **Project Team:**  
> - **Rajat Pandey** (2300270100138)  
> - **Hridyansh Bhadauria** (2300270100074)  
> - **Raghav Mittal** (2300270100133)  
> - **Ragini Goel** (2300270100134)  

---

## 🏛️ Executive Summary

**NirnayX** is a domain-specific legal intelligence and decision-support platform designed to bridge the accessibility gap in the Indian legal ecosystem. Grounded in authoritative Indian statutes (including the 2024 Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam (BSA)), judicial precedents, and case files, NirnayX leverages an **11-step Retrieval-Augmented Generation (RAG)** pipeline and Large Language Models to deliver deterministic, hallucination-free assistance.

### Key Personas Supported:
1. **Common Citizens:** Translating dense statutory texts, FIRs, contracts, and summons into plain, accessible Indian English with actionable legal remedies.
2. **Legal Advocates & Researchers:** Providing statutory cross-referencing, case law precedent retrieval, procedural timeline extraction, and structured case file management with verifiable source citations.

---

## 📂 Repository Structure

This repository contains both the complete production codebase and the academic research assets:

```
NIRNAY_X/
├── PROJECT/                         # Complete Full-Stack Software Implementation
│   ├── backend/                     # FastAPI Backend with 11-step RAG Pipeline
│   │   ├── ingestion/               # OCR, text parsing & legally-coherent chunking
│   │   ├── retrieval/               # Embeddings engine & ChromaDB vector store
│   │   ├── reasoning/               # Dual-persona LLM generation & verification
│   │   ├── app.py                   # FastAPI REST API endpoints
│   │   ├── config.py                # Pydantic configuration & environment settings
│   │   └── rag_pipeline.py          # End-to-end RAG orchestrator
│   ├── frontend/                    # Modern React (Vite) Web Application
│   │   ├── src/components/          # Modular UI components (Chat, Docs, Search, Stats)
│   │   ├── src/App.css              # Custom legal dark-slate/indigo design system
│   │   └── package.json             # Frontend dependencies & build scripts
│   ├── sample_data/                 # Sample legal documents for immediate testing
│   ├── requirements.txt             # Python backend dependencies
│   ├── .env.example                 # Environment configuration template
│   └── README.md                    # Detailed application setup instructions
│
├── FINAL YEAR RESEARCH/             # Research Papers, Synopsis & Literature
│   ├── FINAL/                       # LaTeX research paper & progress reports
│   ├── RESEARCH_COMPILATION/        # Comprehensive compendium & technical formulations
│   ├── synopsis/                    # Department synopsis drafts & official PDFs
│   ├── Reference/                   # Reference papers, slides & presentations
│   └── PROJECT_SPEC.md              # Complete technical specifications & benchmarks
│
├── .gitignore                       # Clean repository exclusions
└── README.md                        # Master repository documentation
```

---

## ⚡ Technical Highlights

- **11-Stage RAG Workflow:** Document Upload → OCR/Parsing → Clause-Aware Chunking → Dense Embeddings → ChromaDB Vector Store → Query Embedding → Top-K Semantic Search → Context Formulation → Dual-Persona LLM Inference → Citation-Verified Grounded Response.
- **Rhetorical Role Awareness:** Classifies and filters legal texts by rhetorical functions (Statute, Judicial Ruling, Case Facts, Arguments, Procedure).
- **Quantitative IR & Generation Benchmarks:** Evaluated against Information Retrieval metrics (Precision@K: 91.4%, Recall@K: 88.7%, MRR: 0.932, NDCG: 0.906) and Faithfulness (97.2%).
- **UN SDG 16 Alignment:** Directly supports Target 16.3: *Promote the rule of law at the national and international levels and ensure equal access to justice for all*.

---

## 🚀 Quickstart Guide

### 1. Launch Backend API
```powershell
cd PROJECT
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.app:app --reload --port 8000
```
*Interactive Swagger documentation available at `http://localhost:8000/docs`.*

### 2. Launch Frontend UI
```powershell
cd PROJECT/frontend
npm install
npm run dev
```
*Application interface opens at `http://localhost:5173`.*

---

## 📜 Academic Reference & Disclaimer

*Responsible AI Disclaimer:* Nirnay-X is strictly an informational and decision-support platform designed for academic and research purposes. It does not replace professional advocates, judicial discretion, or licensed legal counsel.
