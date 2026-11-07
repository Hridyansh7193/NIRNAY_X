# NIRNAY-X: Research Paper & Scientific Compendium Directory

This directory contains the complete scientific manuscript, technical compendium, LaTeX sources, and data catalogs for the research project:
**"Nirnay-X: A Grounded, Persona-Adaptive Retrieval-Augmented Generation Framework for Indian Legal Intelligence and Decision Support"**

---

## Authors & Institution

- **Student Authors:** Rajat Pandey (2300270100138), Hridyansh Bhadauria (2300270100074), Raghav Mittal (2300270100133), Ragini Goel (2300270100134)
- **Department:** Computer Science and Engineering, Ajay Kumar Garg Engineering College (AKGEC), Ghaziabad
- **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow, Uttar Pradesh, India
- **Faculty Supervisor:** Ms. Bhumica (Assistant Professor, Department of CSE, AKGEC)

---

## Directory Inventory

| File | Description |
| :--- | :--- |
| **`NIRNAY_X_RESEARCH_MASTER_COMPILATION.md`** | Master technical compendium: Executive summary, 11-step RAG pipeline, 11 platform modules, formal mathematical formulations (CRF, InfoNCE, ColBERTv2, BM25, PageRank, wRRF, ALE, Deontic Modality Loss), Algorithms 1 & 2, full empirical evaluation tables ($N=1,200$, $N=400$, $N=150$, $N=300$), and landmark cases. |
| **`nirnay_x_research_paper.tex`** | Complete, submission-ready IEEE conference LaTeX source paper formatted with `IEEEtran.cls`, complete with TikZ system architecture diagram, mathematical equations, algorithms, 5 empirical evaluation tables, and 45 IEEE references. |
| **`IEEEtran.cls`** | Official IEEE Transactions / Conference document class file for offline LaTeX compilation. |
| **`RESEARCH_CONTEXT_AND_DATA_CATALOG.md`** | Data catalog detailing the 70,500 judgments, 1,400 Acts, statutory concordance mapping table, and hardware/software experimental testbed specifications. |

---

## How to Compile the LaTeX Paper

Using any standard TeX distribution (TeX Live, MiKTeX, or Overleaf):

```bash
pdflatex nirnay_x_research_paper.tex
pdflatex nirnay_x_research_paper.tex
```

Or on Overleaf:
1. Create a new blank project.
2. Upload `nirnay_x_research_paper.tex` and `IEEEtran.cls`.
3. Set compiler to `pdfLaTeX` and compile.
