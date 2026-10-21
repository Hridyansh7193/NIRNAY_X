# Directory Files Catalog & Resource Index

This file tracks the project resources, reference files, and directory structure for the **Nirnay-X** research workspace.

---

## 1. Project Reference Documents

| File Name | Format | Size | Description & Key Contents |
| :--- | :--- | :--- | :--- |
| **`final synopsis.pdf`** | PDF (42 pages) | ~498 KB | **Comprehensive B.Tech Project Synopsis & Report**<br>• Full literature review, problem formulation, research questions<br>• Detailed methodology, system design, data collection plan<br>• SDG mappings (SDG 16, 9, 3) & Universal Human Values analysis<br>• Evaluation framework and dissemination plan |
| **`NIRNAY-X.pdf.pdf`** | PDF (11 slides) | ~1.04 MB | **Presentation & Architecture Deck**<br>• High-level problem statement & stakeholder breakdown<br>• Visual 11-step RAG architecture & dataflow diagrams<br>• 11 functional modules summary<br>• Evaluation metrics matrix (Precision@K, Recall@K, Faithfulness) |
| **`CLAUDE.md`** | Markdown | ~7.7 KB | **Primary Claude Code Agent Configuration**<br>• Loaded automatically in every Claude Code session<br>• High-priority operating rules, IMRAD standards, and coding conventions |
| **`PROJECT_SPEC.md`** | Markdown | ~4.5 KB | **Technical & Architectural Specification**<br>• Deep-dive into technical components, RAG pipeline, and research objectives |
| **`PLAN.md`** | Markdown | ~4.2 KB | **Nirnay-X Implementation Plan**<br>• 5-phase roadmap, 10-week timeline, architectural modules, and deliverables |

---

## 2. Recommended Workspace Directory Structure

To maintain clean separation between research artifacts, code, and raw materials, organize newly created files according to this layout:

```
FINAL YEAR RESEARCH/
├── CLAUDE.md                 # Primary agent instructions (Always loaded)
├── PROJECT_SPEC.md           # Detailed technical and RAG specifications
├── FILES_CATALOG.md          # This file index and inventory
│
├── docs/                     # Research documentation, drafts, summaries
│   ├── final synopsis.pdf    # Complete B.Tech project synopsis
│   └── NIRNAY-X.pdf.pdf      # Presentation slide deck
│
├── data/                     # Legal datasets and document corpora
│   ├── raw/                  # Immutable original PDFs, judgments, statutes, FIRs
│   └── processed/            # Cleaned, tokenized, and chunked text segments
│
├── code/                     # Implementation codebase
│   ├── ingestion/            # PDF parsing, OCR, and document loader modules
│   ├── embeddings/           # Vectorization & embedding generation pipelines
│   ├── retrieval/            # Vector store indexers and top-k retrieval scripts
│   └── evaluation/           # Scripts computing Precision@K, MRR, Faithfulness
│
├── results/                  # Quantitative experiment outputs (JSON, CSV)
│
└── drafts/                   # Manuscript drafts, LaTeX/DOCX submissions
    ├── sections/             # Individual paper sections (IMRAD format)
    └── figures/              # Vector and high-DPI raster diagrams
```

---

## 3. Usage Protocols for Claude Code

1. **Grounded Writing:** Whenever drafting papers, abstracts, or presentations, always cross-reference the architecture, metrics, and terminology established in `PROJECT_SPEC.md` and `final synopsis.pdf`.
2. **Immutability:** Do not edit or overwrite raw source files (`final synopsis.pdf`, `NIRNAY-X.pdf.pdf`).
3. **Reproducibility:** When writing evaluation code or benchmarks, write scripts into `code/evaluation/` and log outputs into `results/`.
