# NIRNAY-X: Research Context & Data Catalog

> **Scope:** Detailed inventory of benchmark corpora, experimental configurations, statutory provisions, and testbed parameters used across Nirnay-X research evaluations.

---

## 1. Corpus Composition

| Corpus Category | Volume / Count | Time Period / Span | Primary Sources |
| :--- | :--- | :--- | :--- |
| Supreme Court of India Judgments | 42,500 Full Judgments | 1950 – 2024 | Supreme Court of India Open Data / e-Courts |
| High Court Judgments | 28,000 Full Judgments | 1970 – 2024 | Delhi, Allahabad, Bombay, Calcutta High Courts |
| Central & State Statutory Enactments | 1,400 Acts | 1860 – 2024 | India Code / Gazette of India |
| Trial Court / Police Records | 850 Anonymized FIRs & Bail Petitions | 2018 – 2024 | District Courts of Delhi and Uttar Pradesh |
| Curated Evaluation Query Benchmark | 1,200 Annotated Inquiries | 2024 | Verified by 5 High Court Advocates & 3 Scholars |
| Adversarial Test Benchmark | 400 Complex Legal Traps | 2024 | Testing false premises, overruled cases, and sycophancy |
| Plain-Language Statutory Benchmark | 150 Key Statutory Provisions | BNS, BNSS, BSA, IPC, CrPC | Evaluated by 45 Blind Human Annotators |
| Temporal Transition Benchmark | 300 Offense/FIR Date Scenarios | 2023 – 2024 | Testing Art. 20(1) and Section 531(2)(a) BNSS routing |

---

## 2. Statutory Concordance Cross-Reference Index

| Legacy Colonial Statute | Modern Indian Statute (Effective July 1, 2024) | Primary Domain |
| :--- | :--- | :--- |
| Section 300 / 302 IPC (Murder) | Section 101 / 103 BNS | Substantive Criminal Law |
| Section 304 IPC (Culpable Homicide) | Section 105 BNS | Substantive Criminal Law |
| Section 304A IPC (Death by Negligence) | Section 106 BNS | Substantive Criminal Law |
| Section 279 IPC (Rash Driving) | Section 281 BNS | Substantive Criminal Law |
| Section 337 / 338 IPC (Endangering Safety / Hurt) | Section 125(a) / 125(b) BNS | Substantive Criminal Law |
| Section 420 IPC (Cheating) | Section 318 BNS | Substantive Criminal Law |
| Section 441 / 447 IPC (Criminal Trespass) | Section 329 BNS | Substantive Criminal Law |
| Section 154 CrPC (FIR Registration) | Section 173 BNSS | Criminal Procedural Law |
| Section 41A CrPC (Notice of Appearance) | Section 35 BNSS | Criminal Procedural Law |
| Section 167 CrPC (Remand & Custody) | Section 187 BNSS | Criminal Procedural Law |
| Section 436A CrPC (Undertrial Maximum Custody) | Section 479 BNSS | Criminal Procedural Law |
| Section 437 / 439 CrPC (Regular Bail) | Section 480 / 483 BNSS | Criminal Procedural Law |
| Section 438 CrPC (Anticipatory Bail) | Section 482 BNSS | Criminal Procedural Law |
| Section 482 CrPC (Inherent Powers of High Court) | Section 528 BNSS | Criminal Procedural Law |
| Section 65B IEA (Electronic Records Admissibility) | Section 63 BSA | Law of Evidence |
| Section 27 IEA (Discovery of Fact upon Confession) | Section 23 BSA | Law of Evidence |

---

## 3. Computational Testbed & Infrastructure

```yaml
Hardware:
  Compute Accelerators: 2x NVIDIA RTX A6000 (48 GB GDDR6 ECC VRAM each)
  Host Processor: AMD EPYC 7763 (32 Cores, 64 Threads @ 2.45 GHz base, 3.50 GHz boost)
  System Memory: 128 GB DDR4-3200 ECC Registered RAM
  Primary Storage: 2 TB NVMe PCIe Gen4 SSD (7,000 MB/s sequential read)

Software Environment:
  OS: Ubuntu 22.04 LTS / Windows Server 2022
  Python Version: 3.11 / 3.13
  PyTorch: 2.3.0+cu121
  Vector Database: Qdrant 1.9.0 (HNSW M=16, ef_construct=100) / ChromaDB 1.5.9
  Graph Database: Neo4j Enterprise 5.18.0 (124k nodes, 412k edges)
  LLM Inference Engine: vLLM 0.4.2 / AWQ 4-bit Quantization
  Primary Model Checkpoints:
    - InLegalBERT: law-ai/InLegalBERT (768-d)
    - ColBERTv2: colbert-ir/colbertv2.0 (128-d)
    - Cross-Encoder: BAAI/bge-reranker-large
    - Generator LLMs: meta-llama/Meta-Llama-3.1-70B-Instruct, mistralai/Mistral-Large-Instruct-2407
    - NLI Verifier: InLegal-RoBERTa-NLI fine-tuned on LegalBench
```
