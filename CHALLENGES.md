# Engineering Challenges, Failures & Architectural Post-Mortem

This document serves as an exhaustive log of all experiments, empirical discoveries, algorithmic failures, and current engineering bottlenecks encountered while building the **Humanizer-AI** pipeline.

---

## 1. The Core Engineering Triad

Building a production-ready academic humanizer is subject to three mutually competing constraints:

```
                  Zero-Truncation
                  (≥95% Word Count)
                       ▲
                      / \
                     /   \
                    /     \
                   /       \
  Zero-Hallucination ◄──────► Single-Pass Turnkey
  (100% Real Facts)          (0 Human Iterations)
```

1. **Zero-Truncation Law**: Academic manuscripts, grants, and reports have strict length requirements. You cannot convert a 15-page paper into an 8-page paper. Word retention must be $\ge 95\%$ ($100\% \pm 5\%$).
2. **Zero-Hallucination Law**: Never invent citations, authors, chemistry, or numbers. Every formula ($\text{Li}_{6.4}\text{La}_3\text{Zr}_{1.4}\text{Ta}_{0.6}\text{O}_{12}$), figure ($3,860\text{ mAh g}^{-1}$, $312\%$, $1.0\text{ mA cm}^{-2}$), and instrument technique (ToF-SIMS, Raman, Synchrotron CT) must be preserved with 100% fidelity.
3. **Single-Pass Turnkey Execution**: The system must take raw AI text and output publication-grade, $<10\%$ AI text in **one pass**. Requiring 6 to 7 rounds of human copyediting is completely unviable.

---

## 2. Chronological Empirical History (The Discovery Benchmarks)

We conducted an empirical benchmark on a 1,037-word academic extended abstract on *All-Solid-State Lithium-Metal Batteries* across 8 manual iterative cycles on ZeroGPT to isolate the exact linguistic features that trigger detection classifiers.

### The Benchmark Trajectory:
| Phase | Action / Intervention | Word Count | ZeroGPT Score | Key Takeaway |
| :--- | :--- | :--- | :--- | :--- |
| **0** | Raw machine baseline (unmodified) | 1,037 words | **100% AI** | Every sentence flagged yellow. Deep red meter. |
| **1** | Initial Gemini 3.6 Low pass | 640 words | **63.1% AI** | Discovered the Compression Trap: model deleted 38% of text. |
| **2** | Python v3.2 Triad Breaker | 623 words | **57.6% AI** | Collapsing $A, B, \text{ and } C \to A \text{ and } B$ broke $n$-gram clusters. |
| **3** | Participial Tail Decoupling | 597 words | **53.6% AI** | Splitting `, cutting...` $\to$ `. This cut...` cleared clause-level yellow. |
| **4** | 15-Word Clamping & Discourse Scrub | 578 words | **41.5% AI** | Removing *Furthermore, Moreover* and clamping sentence length to $\le 15$ words cleared Paragraph 4 completely. |
| **5** | Clause Inversion & Anti-Parallelism | 591 words | **38.4% AI** | Breaking repetitive parallel sentence structures dropped score sub-40%. |
| **6** | Grounding & Anti-Preaching Scrubber | 587 words | **21.3% AI** | Removing policy platitudes (*must deploy, paramount, balanced synergy*) turned Paragraphs 3 & 4 100% white. |
| **7** | Targeted Yellow Sentence Inversion | 587 words | **6.3% AI** | Single-digit threshold breached. |
| **8** | Final Cadence Tuning | 587 words | **2.9% AI** | Reached target ($<5\%$), but text was only 587 words (45% truncated). |

---

## 3. The Three Major Failures Encountered

### Failure 1: The Truncation Trap (Word Butchering)
- **What Happened**: When the pipeline reached **2.9% AI**, the user audited the length and discovered the text had shrunk from **1,037 words (8,791 characters)** down to **587 words (4,572 characters)**.
- **Why It Happened**:
  When LLMs are prompted with negative constraints (*"eliminate fluff, write short sentences, avoid clichés"*), their attention heads take the path of least resistance: **summarizing and dropping supporting detail**.
- **The Impact**: Unacceptable for production. An academic author submitting to *Nature Energy* or *Advanced Materials* cannot lose 45% of their methodology and findings.
- **The Law Formulated**: **Unpacking, Not Condensing**. Long sentences must be unpacked into multiple complete declarative sentences rather than deleted.

---

### Failure 2: The Staccato Flaw (Uniformity = Zero Burstiness)
- **What Happened**: The user tested Phase 1 in Gemini 3.6 with strict sentence-shortening instructions. The output was 686 words and scored **70.5% AI** on ZeroGPT (`media_1791139633217.png`).
- **Why It Happened**:
  The LLM turned almost every sentence into a 6-to-8-word robot:
  > *"Solid-state lithium-metal batteries transform modern electrochemical energy storage. They yield high energy densities and strong safety profiles. Traditional liquid-electrolyte lithium-ion cells fall short. Global transit and grid sectors demand higher storage capacity..."*
  
  Every sentence had the exact same word count ($\mu_L = 7.5, \sigma_L = 0.9$).
  **This resulted in near-zero length burstiness ($B_L \approx 0.12$).**
- **The Takeaway**: Monotonous short sentences trigger AI detectors just as reliably as monotonous long sentences. Human writing requires **burstiness variance**: pairing a 16-word explanatory compound with a 4-word micro-punch (*"Contact loss ruins performance."*, *"That assumption fails."*).

---

### Failure 3: The Generic Background Fluff Trap (The 62.0% Benchmark)
- **What Happened**: We attempted to restore full length (980 words / 8,245 characters). ZeroGPT scored it **62.0% AI** (`media_1791139894083.png` through `media_1791139908477.png`).
- **Forensic Inspection of the Screenshots**:
  - **Paragraphs 2, 3, 4, 5, and 6 were 60% to 70% PURE WHITE**:
    - Lines 11–16 of Paragraph 2: 100% white.
    - Symmetrical cell degradation (Paragraph 4): 100% white.
    - Mechanical creep and load frames (Paragraph 5): 100% white.
    - Dendrite plating and void formation (Paragraph 6): 100% white.
  - **Paragraph 1 was 90% BRIGHT YELLOW**:
    Look at the sentences in Paragraph 1:
    > *"Solid-state lithium-metal batteries deliver higher specific energy than conventional liquid-electrolyte cells. They also eliminate flammable organic solvents found in commercial lithium-ion packs... Transportation sectors and grid-scale storage facilities accelerate this transition. Fleet electrification continually increases the demand..."*
- **Why It Happened**:
  To hit 980 words, Paragraph 1 was padded with **standard introductory fluff**. Language models evaluate introductory generalities with near-zero perplexity because millions of battery papers begin with those exact sentences.
- **The Breakthrough Insight**:
  **Word count must NEVER be expanded with thematic background.** It must be expanded with **concrete laboratory parameters**:
  - Spark plasma sintering schedules: $1150^\circ\text{C}$, $50\text{ MPa}$, 15 min.
  - Synchrotron beamline physics: $25\text{ keV}$, $0.65\ \mu\text{m}$ voxel resolution.
  - Constitutive mechanical constants: Lithium shear modulus $3.4\text{ GPa}$, yield strength $0.8\text{ MPa}$, ceramic separator modulus $150\text{ GPa}$, Poisson ratio $0.26$.
  - Exact failure thresholds: Critical overpotential $\eta > 120\text{ mV}$, short-circuit hours (84h vs 600h).
  
  **Detectors cannot flag concrete laboratory parameters because domain constants have high localized entropy.**

- **Correction (v6.0.0)**:
  None of the parameters above appear in the baseline abstract. They were generated during the rewrite, so benchmark 07 reached full length by inventing data, which breaks the Zero-Hallucination Law. The expansion idea still holds, but only for values the author supplies. v6.0.0 adds a fact sheet as the only allowed source of added specifics, and `check_draft.py` fails any number found in neither the source nor the fact sheet. Run against the baseline, it flags 28 unsourced numbers in benchmark 07.

---

## 4. Current Technical Bottlenecks (Why 1-Pass is Unsolved)

### Bottleneck A: The Regex Ceiling in Python
Currently, `humanizer.py` operates via regular expressions (`re.sub`).
- **What regex does well**: Surface-level string replacements (semicolon splitting, removing discourse markers, splitting participial tails).
- **Where regex hits a brick wall**:
  - Regex cannot parse semantic dependency trees.
  - Regex cannot determine if a sentence is an S-V-O construction and automatically invert the clause.
  - If an LLM generates a grammatically clean but predictably structured sentence (*"Solid-state lithium-metal batteries deliver higher specific energy..."*), regex sees nothing syntactically invalid and leaves it untouched.

### Bottleneck B: Stochastic LLM Prompt Adherence
When prompting an LLM (even state-of-the-art models like Gemini 1.5 Pro, Claude 3.5 Sonnet, or GPT-4o):
- Prompting with 15 simultaneous negative and positive constraints causes **attention dilution**.
- The model will reliably follow 70% of instructions (e.g. eliminating semicolons and splitting sentences), but will slip on syntactic inversion or burstiness uniformity unless steered across multiple turns.

---

## 5. What We Are Building Next (The Open Roadmap)

To achieve true, single-pass autonomous humanization without human copyediting, the repository is developing three algorithmic modules:

### 1. NLP AST-Based Syntactic Transformer (`syntactic_transformer.py`)
Replace regex with dependency parsing (via `spaCy` or `Stanza`):
- Parse each sentence into its Dependency Parse Tree.
- Identify sentences where the root subject is a standard nominal phrase at position 0 (`nsubj` $\to$ `ROOT` $\to$ `dobj`).
- Automatically transform prepositional and adverbial modifiers to the sentence head:
  $$\text{Subject} + \text{Verb} + \text{Object} + \text{PP} \implies \text{PP} + \text{,} + \text{Subject} + \text{Verb} + \text{Object}$$

### 2. Algorithmic Burstiness Synthesizer
A post-processing module that calculates the empirical length burstiness coefficient $B_L$:
$$B_L = \frac{\sigma_L}{\mu_L}$$
- If $B_L < 0.45$:
  - Identify spans of 3 or more sentences of similar length ($|L_i - L_{i+1}| \le 2$).
  - Dynamically split at dependent clauses or merge adjacent short clauses to inject forced micro-punches ($\le 5$ words) until $B_L \ge 0.50$ is mathematically guaranteed.

### 3. Automated Perplexity Auditor
An open-source local evaluator (using `transformers` and a lightweight reference model like `gpt2-xl` or `roberta-base`) to calculate running token surprisal and flag high-risk spans locally before uploading to commercial detectors.
