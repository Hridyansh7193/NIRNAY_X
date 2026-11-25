# NirnayX — AI-Powered Legal Intelligence & Decision-Support Platform

> **AKGEC B.Tech Final Year Capstone Project (2023–2027)**  
> **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  
> **Department:** Computer Science & Engineering  
> **Supervisor:** Ms. Bhumica (Assistant Professor, Dept. of CSE)  
> **Team:** Rajat Pandey, Hridyansh Bhadauria, Raghav Mittal, Ragini Goel

---

## 1. Overview

**NirnayX** is a state-of-the-art legal intelligence platform designed to bridge the accessibility gap in the Indian legal ecosystem. Powered by a deterministic **11-step Retrieval-Augmented Generation (RAG)** pipeline and Large Language Models, NirnayX serves two critical personas:

1. **Common Citizens:** Translating complex legal jargon, FIRs, petitions, contracts, and statutory provisions into accessible plain language with actionable legal remedies.
2. **Legal Professionals & Advocates:** Automating statutory research across IPC/BNS, CrPC/BNSS, CPC, indexing case files, extracting procedural facts, and surfacing analogous case precedents with verifiable source citations.

---

## 2. 11-Step RAG Architecture

```
[Legal PDF Upload (FIR / Judgment / Petition)]
                     ↓
         [OCR & Document Parsing]
                     ↓
       [Legally-Coherent Text Chunking]
        (Preserves proviso & clauses)
                     ↓
        [Dense Embedding Generation]
        (OpenAI / Sentence-Transformers)
                     ↓
       [ChromaDB Vector Store Indexing]
                     ↓
[User Natural-Language Query] → [Query Embedding]
                     ↓
     [Top-K Semantic Similarity Search]
                     ↓
       [Grounding Context Formulation]
                     ↓
   [LLM Inference (Citizen / Advocate Mode)]
                     ↓
  [Grounded Answer + Verifiable Source Citations]
```

---

## 3. Platform Modules & Visual Decision Outputs

1. **RAG Legal Assistant (`ChatPanel`):** Multi-turn conversational interface with multi-modal visual decision synthesis:
   - **4 Analytical Modules:** Executive Brief, Statutory Concordance, Precedent Analysis, Procedural Roadmap.
   - **Interactive SVG Venn Diagrams:** Visualizing overlaps between old criminal laws (IPC/CrPC) and new Sanhitas (BNS/BNSS), as well as claims vs. defenses.
   - **Statutory Charts & Timelines:** Statutory penalty horizon bar charts and step-by-step procedural lifecycle tracks.
   - **Comparative Tabular Matrices:** Clean legal concordance tables with color-coded classification badges.
   - **View-Mode Selector Tabs:** Toggle between Comprehensive, Modules, Venn Diagram, Charts, Tables, and Sources views.
2. **Legal Document Processing (`DocumentPanel`):** Act-normalized legal entity extraction (resolving BNS, BNSS, BSA, IPC, CrPC, MVA without "Unknown Act" anomalies) and precise document type classification.
3. **Stage-2 Cross-Scoring Legal Reranker:** Hybrid reranking combining dense cosine similarity (0.55), BM25 lexical overlap (0.25), statutory section matching (0.15), and rhetorical role alignment (0.05).
4. **Dual Persona Mode:**
   - **Citizen Mode:** Plain language explanations, practical remedies, simplified summaries.
   - **Advocate Mode:** Technical statutory rigor, IPC/CrPC/BNS mappings, case citations, procedural posture.
5. **Semantic Provision & Precedent Search (`SearchPanel`):** Concept-driven dense vector retrieval with rhetorical role filtering (Statute, Ruling, Facts, Argument).
6. **Empirical Academic Benchmarking & Telemetry (`StatsPanel`):** Live IR evaluation suite (`POST /api/eval/run`) computing real-time Precision@5, Recall@K, MRR, NDCG, and SDG 16 impact metrics with an interactive "Run Live Benchmark" test harness.
7. **Corpora Management (`UploadModal`):** Multi-case file indexing with automated deduplication by filename, per-document filtering, and vector store management.

---

## 4. Directory Structure

```
PROJECT/
├── backend/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── document_processor.py   # PDF text extraction & legal entity parsing
│   │   └── chunker.py              # Clause-aware & proviso-preserving chunker
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── embeddings.py           # Dual embedding engine (OpenAI / Local / Fallback)
│   │   └── vector_store.py         # ChromaDB vector store wrapper
│   ├── reasoning/
│   │   ├── __init__.py
│   │   └── generator.py            # RAG prompt builder & dual-persona LLM generation
│   ├── app.py                      # FastAPI REST application
│   ├── config.py                   # Pydantic settings configuration
│   └── rag_pipeline.py             # 11-step RAG pipeline orchestrator
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx          # Top navigation & persona switch
│   │   │   ├── Sidebar.jsx         # Module navigation & active corpora filter
│   │   │   ├── ChatPanel.jsx       # RAG conversational assistant with citations
│   │   │   ├── DocumentPanel.jsx   # Case materials & extracted legal entities
│   │   │   ├── SearchPanel.jsx     # Semantic provision retrieval tester
│   │   │   ├── StatsPanel.jsx      # Telemetry & IR evaluation metrics
│   │   │   └── UploadModal.jsx     # PDF dropzone & pipeline stage indicator
│   │   ├── App.jsx                 # Main layout & router
│   │   ├── App.css                 # Premium dark-slate/indigo legal stylesheet
│   │   ├── index.css               # Design system tokens & reset
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── sample_data/
│   └── NirnayX_Legal_Research_Paper.pdf  # Sample document for quick testing
├── requirements.txt                # Python backend dependencies
├── .env.example                    # Environment variable configuration template
└── README.md
```

---

## 5. Quickstart Guide

### Step 1: Backend Setup

1. Open a terminal in `PROJECT/`:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Optional)* Add your `OPENAI_API_KEY` or `GEMINI_API_KEY` in `.env`. If no key is set, the system will use deterministic embeddings and simulated RAG inference.

3. Start the FastAPI backend server:
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```
   Interactive API documentation will be available at: `http://localhost:8000/docs`

---

### Step 2: Frontend Setup

1. Open a terminal in `PROJECT/frontend/`:
   ```bash
   npm install
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 6. Testing Document Ingestion

1. In the NirnayX web app, click **Upload Legal Doc** in the top header.
2. Select or drop `sample_data/NirnayX_Legal_Research_Paper.pdf` (or any legal PDF judgment/FIR).
3. Watch the 5 ingestion stages process (Text Extraction → Clause Chunking → Embeddings → Vector Indexing).
4. Ask legal questions in **Citizen Mode** or **Advocate Mode** and view retrieved citations with exact clause excerpts!
