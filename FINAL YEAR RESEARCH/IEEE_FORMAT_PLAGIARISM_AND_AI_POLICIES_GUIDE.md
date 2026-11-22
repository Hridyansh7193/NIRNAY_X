# Comprehensive Guide: IEEE Research Paper Format, Plagiarism Allowances, and AI Content Policies

**Target Standard:** IEEE Conference / Transactions (AKTU / AKGEC Final Year Project & Research Standard)  
**Authoring Team:** Nirnay-X Research Initiative  
**Date of Compilation:** November 2026  

---

## 1. IEEE Research Paper Format Specifications

IEEE publications follow strict typographic, structural, and mathematical layout standards. Submissions must adhere to the two-column format defined by the official `IEEEtran.cls` document class.

### 1.1 Page Layout & Dimensions
* **Paper Size:** Standard US Letter ($8.5 \times 11.0\text{ inches}$ / $215.9 \times 279.4\text{ mm}$) or A4.
* **Layout:** Two-column grid with equal column widths.
  * **Top Margin:** $0.75\text{ in}$ ($19\text{ mm}$) on first page; $0.75\text{ in}$ on subsequent pages.
  * **Bottom Margin:** $1.0\text{ in}$ ($25.4\text{ mm}$).
  * **Left / Right Margin:** $0.625\text{ in}$ ($15.9\text{ mm}$) each.
  * **Column Width:** $3.5\text{ in}$ ($88.9\text{ mm}$).
  * **Column Separation (Gutter):** $0.25\text{ in}$ ($6.35\text{ mm}$).
* **Target Page Budget:** 
  * Standard IEEE Conference paper: **6 pages** (often expandable to 8 pages with extra-page fees).
  * Major project final paper / Capstone documentation: **6 to 10 pages**.

### 1.2 Typographic Hierarchy
| Element | Font Type & Style | Size | Alignment | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Paper Title** | Times New Roman, Bold | 24 pt | Centered | Capitalize first letter of all key words. Avoid acronyms unless standard (e.g., IEEE). |
| **Author Names** | Times New Roman, Regular | 11 pt | Centered | Listed horizontally or in multi-author blocks. |
| **Author Affiliations** | Times New Roman, Italic | 10 pt | Centered | Department, Institution, City, Country, Email. |
| **Abstract Heading** | Times New Roman, Bold Italic | 9 pt | Left-aligned | Unnumbered; mandatory single paragraph (150–250 words). |
| **Abstract Body** | Times New Roman, Bold | 9 pt | Justified | No citations, no undefined acronyms, no displayed equations. |
| **Index Terms / Keywords** | Times New Roman, Bold Italic | 9 pt | Justified | 4 to 6 authoritative keywords separated by commas. |
| **Section Headings (Level 1)** | Small Caps, Centered | 10 pt | Centered | Numbered with Roman numerals (`I. INTRODUCTION`). |
| **Subsection Headings (Level 2)** | Times New Roman, Italic | 10 pt | Left-aligned | Numbered with capital letters (`A. System Architecture`). |
| **Sub-subsection (Level 3)** | Times New Roman, Italic | 10 pt | Left-aligned | Indented run-in heading (`1) Vector Indexing:`). |
| **Body Text** | Times New Roman, Regular | 10 pt | Justified | Single-spaced; first line indented by $0.16\text{ in}$ ($4.2\text{ mm}$). |
| **Equations** | Times New Roman Math | 10 pt | Centered | Consecutively numbered on the right margin in parentheses: `(1)`. |
| **Table Headings** | Small Caps | 8 pt | Centered | Centered above table: `TABLE I`, followed by title in small caps. |
| **Figure Captions** | Times New Roman, Regular | 8 pt | Left/Justified | Placed below figure: `Fig. 1. End-to-end architecture...`. |
| **References** | Times New Roman, Regular | 8 pt | Justified | Numbered consecutively in square brackets `[1]`, `[2]`. |

### 1.3 Mathematical Formulations & Notation
* All scalar variables must be italicized: $x, y, \tau, \alpha$.
* Vectors and matrices must be boldface: $\mathbf{x}, \mathbf{W}, \mathbf{\Phi}$.
* Standard operators and functions must be upright: $\min, \max, \operatorname{argmax}, \log, \exp, \operatorname{Tr}$.
* Displayed equations must be punctuated as grammatical parts of the surrounding sentence.

### 1.4 Figures and Tables
* High-resolution vector graphics (PDF, EPS, or vector TikZ) are strongly preferred over raster images (PNG, JPG) to prevent pixelation during printing.
* Figures spanning both columns must use the `figure*` environment; single-column figures use `figure`.
* Tables must strictly use professional booktabs styling (`\toprule`, `\midrule`, `\bottomrule`), completely avoiding vertical borders.

---

## 2. Plagiarism Allowances, Thresholds, and Screening Metrics

Academic publishers (IEEE, ACM, Springer) and Indian academic bodies (UGC, AKTU) screen all manuscripts using **IEEE CrossCheck** (powered by Turnitin / iThenticate).

### 2.1 Standard Similarity Index Thresholds
| Metric | Safe Benchmark | Risk / Warning Level | Immediate Rejection |
| :--- | :--- | :--- | :--- |
| **Total Similarity Index** | **$< 10\% - 15\%$** | $16\% - 25\%$ (triggers manual review) | **$> 30\%$** (IEEE CrossCheck auto-alert) |
| **Single-Source Similarity** | **$\le 1\% - 2\%$** | $3\% - 5\%$ (requires explanation) | **$> 5\% - 10\%$** (classified as text lifting) |
| **Methodology Section** | $< 12\%$ | $15\% - 20\%$ | $> 25\%$ |
| **Literature Review** | $< 15\%$ | $18\% - 25\%$ | $> 30\%$ |

> **Total Score vs. Single Source:** A total similarity of 14% composed of 14 separate sources at ~1% each (mostly standard terms like *"retrieval-augmented generation"* or statutory names) is completely acceptable. However, a paper with an 8% total score where 7% comes from a single external paper will be flagged and rejected for verbatim text borrowing.

### 2.2 UGC (Promotion of Academic Integrity and Prevention of Plagiarism) Regulations, 2018 / 2023
For AKTU, AKGEC, and Indian university submissions, the University Grants Commission enforces the following statutory tiers:
* **Level 0 (Similarity up to 10%):** Minor similarity; acceptable with no penalty.
* **Level 1 (Similarity 10% to 40%):** Script returned; author must revise and resubmit within a stipulated window.
* **Level 2 (Similarity 40% to 60%):** Debarred from submitting for 1 year; supervisor may face disciplinary action.
* **Level 3 (Similarity > 60%):** Registration cancelled; institutional blacklisting.

### 2.3 Exclusions Permitted Under IEEE and UGC Norms
When running Turnitin / iThenticate, the following filters are legally and procedurally applied:
1. **Exclude Bibliography / References:** Citations and bibliographies naturally match previous papers; these must be excluded from the percentage.
2. **Exclude Direct Quotations:** Verbatim quotes placed in quotation marks with pinpoint page/reporter citations are excluded.
3. **Exclude Small Matches:** Matches below 1% or under 10–14 consecutive words are filtered out to ignore common academic idioms.
4. **Standard Statutory Names:** Common legal phrases (*"Bharatiya Nagarik Suraksha Sanhita, 2023"*, *"Article 20(1) of the Constitution of India"*) are recognized as non-plagiarizable terminology.

### 2.4 Why Citation Lists Cause False-Positive Plagiarism Flags
In student and legal engineering papers, listing 10–15 standard court cases identically formatted (*"Supreme Court of India, Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273"*) triggers a 100% string match against thousands of previous dissertations stored in Turnitin's repository.  
**Best Practice:** In computer science / IEEE engineering papers, cite case law in-text using compact reporter format:  
`"...pursuant to Supreme Court detention limits (Arnesh Kumar, 2014)"` rather than bloating the bibliography with generic legal case listings.

---

## 3. Laws and Policies on AI Content in Research Papers

The integration of Generative AI (LLMs, code generators, automated writing assistants) into academic research is strictly regulated by international publication ethics and intellectual property law.

### 3.1 IEEE Policy on AI-Generated Text (IEEE PSPB Operations Manual)
The IEEE Publication Services and Products Board (PSPB) Operations Manual (Sections 8.2.1.B.10 and 8.2.2) establishes five foundational rules:

1. **Prohibition of AI Co-Authorship:**
   * Generative AI models (e.g., ChatGPT, Claude, Gemini, Copilot) **cannot be named as authors or co-authors** on any IEEE publication.
   * *Rationale:* Authorship implies moral, intellectual, and legal accountability. An AI system cannot sign copyright transfer agreements, assume liability for scientific misconduct, or defend claims in court.
2. **Mandatory Disclosure of Generative AI Usage:**
   * If an author uses generative AI tools to draft text, synthesize figures, generate code, or design experiments, this **must be explicitly disclosed**.
   * *Location:* Must be placed in the **Acknowledgments** section or the Methodology section.
   * *Required Information:*
     - Name and version of the AI model / tool.
     - Specific sections of the manuscript where AI assistance was utilized.
     - Brief explanation of the scope and level of assistance.
3. **Exemption for Routine Language Editing:**
   * Using AI strictly for spelling correction, grammar enhancement, or language polishing (especially helpful for non-native English researchers) does **not** require formal disclosure, though disclosing it is recommended as best practice.
4. **Strict Human Author Liability:**
   * Human authors are **100% legally and academically liable** for the complete contents of the paper.
   * If an AI tool introduces a fabricated citation (hallucination), false empirical data, or infringing text, it is treated as deliberate academic misconduct by the human authors.
5. **Confidentiality in Peer Review:**
   * IEEE peer reviewers are strictly prohibited from uploading manuscripts into commercial AI systems, as this breaches author confidentiality and IP rights.

### 3.2 Intellectual Property & Copyright Laws (USCO & Indian Copyright Act)
* **Indian Copyright Act, 1957 (Section 17):** Copyright subsists solely in original works of authorship produced by a natural human being. Purely machine-generated content without human intellectual labor enters the public domain.
* **US Copyright Office (USCO) Guidance (2023/2024):** Only human-authored expressions are eligible for copyright. A human researcher who conceptualizes architectures, derives equations, executes experiments, and curates analysis retains copyright, provided the human input constitutes the core intellectual essence.

---

## 4. How AI Detectors Work & Strategies for Authentic Human Scholarly Writing

AI detectors (Turnitin AI Detector, GPTZero, CopyLeaks) do not "know" what was written by an AI; they evaluate statistical text characteristics:

### 4.1 Key Detection Metrics
* **Perplexity:** A measure of how likely a word is to follow the previous word based on standard language model probability distributions. AI text has very low perplexity (highly predictable, generic word choices). Human text features high perplexity (unusual word pairings, idiosyncratic phrasing, domain jargon).
* **Burstiness:** The variation in sentence length and syntactic structure. AI text exhibits low burstiness (uniform sentences of 18–25 words with identical cadence). Human writing exhibits high burstiness (a short 6-word sentence followed by a complex 35-word explanatory sentence with semi-colons or dashes).

### 4.2 Hallmarks of "AI Agent" Writing to Avoid
1. **Promotional Hype & Buzzwords:** *"stands as a testament to"*, *"pivotal milestone"*, *"delve into"*, *"beacon of hope"*, *"multifaceted tapestry"*, *"unprecedented paradigm"*.
2. **Formulaic Introductions & Conclusions:** *"In an era marked by rapid technological advancements..."*, *"In conclusion, it is imperative to acknowledge that..."*.
3. **Symmetric Enumerations:** Repetitive lists where every bullet has identical length and starts with the exact same grammatical structure.
4. **Absence of Practical Friction:** Real research describes runtime bottlenecks, GPU out-of-memory errors, noisy OCR failures, edge-case misclassifications, and empirical trade-offs. AI text presents an idealized, frictionless system.

### 4.3 Human Academic Transformation Rules ("Stealth" Writing Techniques)
* **Lead with Empirical Data & Engineering Reality:** Rather than stating *"Our system achieves groundbreaking accuracy"*, state *"Empirical evaluation across 1,200 benchmark queries shows an 88.7% Precision@10, representing a 34.9 percentage point increase over unweighted lexical baselines"*.
* **Vary Sentence Cadence:** Mix short active observations with detailed compound clauses.
* **Document Systems Trade-offs:** Mention hardware limits (e.g., dual NVIDIA RTX A6000 48GB VRAM, AWQ 4-bit quantization, 12ms mean Cypher graph traversal).
* **Include Formal AI Disclosure:** Include the standard IEEE-compliant statement in Acknowledgments to ensure 100% institutional compliance and zero ethical vulnerability.

---

*Document compiled and archived in `C:\Users\rajat\Desktop\FINAL YEAR RESEARCH\IEEE_FORMAT_PLAGIARISM_AND_AI_POLICIES_GUIDE.md`.*
