# Agent & Collaborator Onboarding Guide

Welcome to **Humanizer-AI**. This guide is designed for autonomous AI coding agents (Antigravity, Cline, Claude Code, Cursor, Devin, etc.) and human research engineers joining this codebase to solve the **Single-Pass Academic Humanization Challenge**.

---

## 1. Project Directory Layout

```
humanizer-ai/
├── .claude/skills/academic-humanizer  # Symlink to skills/academic-humanizer (auto-loads in Claude Code)
├── README.md               # Main project overview, architecture & quickstart
├── MATHEMATICS.md          # Theoretical & information-theoretic formulas (PPL, Burstiness, Zipf)
├── CHALLENGES.md           # Engineering log of all iterations, failures, and bottlenecks
├── AGENT_GUIDE.md          # This onboarding guide for agents & contributors
├── humanizer.py            # v5.0.0 regex engine (no longer used by the skill)
├── skills/
│   └── academic-humanizer/
│       ├── SKILL.md                  # The skill: procedure, hard constraints, style rules
│       ├── fact_sheet_template.md    # Author fact sheet: the only source of added specifics
│       └── scripts/
│           └── check_draft.py        # Phase 2 checker (fact ledger, fact & style checks)
├── benchmarks/             # Historical test cases with exact ZeroGPT scores
│   ├── 00_baseline_raw_1037w_100pct_ai.txt
│   ├── 01_gemini_pass_640w_63pct_ai.txt
│   ├── 02_intermediate_pass_38pct_ai.txt
│   ├── 03_sub_10pct_pass_6_3pct_ai.txt
│   ├── 04_breakthrough_pass_587w_2_9pct_ai.txt
│   ├── 05_user_phase1_staccato_686w_70_5pct_ai.txt
│   ├── 06_full_1000w_fluff_mixed_980w_62_0pct_ai.txt
│   └── 07_master_empirical_untruncated_952w.txt
└── tests/
    ├── test_humanizer.py   # Tests for the v5.0.0 regex engine
    └── test_check_draft.py # Tests for the Phase 2 checker
```

---

## 2. Core CLI Commands

### Run the Phase 2 Checker:
```bash
# Fact ledger: every number, acronym and formula a draft may use
python3 skills/academic-humanizer/scripts/check_draft.py source.txt --facts facts.md

# Check a draft against its source and fact sheet (exit code 1 on any FAIL)
python3 skills/academic-humanizer/scripts/check_draft.py source.txt draft.txt --facts facts.md
```

### Run the v5.0.0 Regex Engine (standalone, not used by the skill):
```bash
# Process a text file and output to stdout
python3 humanizer.py benchmarks/00_baseline_raw_1037w_100pct_ai.txt

# Process with full forensic quality audit
python3 humanizer.py benchmarks/00_baseline_raw_1037w_100pct_ai.txt --stats

# Save output to a file
python3 humanizer.py benchmarks/00_baseline_raw_1037w_100pct_ai.txt -o cleaned.txt --stats
```

### Run the Unit Test Suite:
```bash
python3 -m unittest discover -s tests
```

---

## 3. The 3 Non-Negotiable Laws for Any Agent Modifying Code

Whenever an agent writes code or rewrites text in this repository, it MUST adhere to these three laws:

1. **The Zero-Truncation Law ($\ge 95\%$ Word Retention)**:
   - Never compress or summarize text.
   - If an input text is 1,000 words, the output must be $\ge 950$ words.
   - If breaking a 30-word compound sentence, **unpack** it into two complete declarative sentences ($14\text{w} + 12\text{w}$) plus a 4-word micro-punch, preserving 100% of the facts.
2. **The Zero-Hallucination Law (100% Factual Fidelity)**:
   - Never invent fake citations, author names, or fabricated numbers.
   - All real values ($3,860\text{ mAh g}^{-1}$, $312\%$, $1.0\text{ mA cm}^{-2}$, $18.4\ \Omega\cdot\text{cm}^2$, $82.6\%$, $1.2\text{--}3.8\text{ mA cm}^{-2}$, $0.5\text{--}7.0\text{ MPa}$, LLZTO, ToF-SIMS, Raman) must be preserved.
3. **The Single-Pass Mandate**:
   - The user cannot perform 7 rounds of manual trial-and-error.
   - All transformations must execute in a single turnkey pipeline: Phase 1 (LLM rewrite) $\to$ Phase 2 (deterministic checker) $\to$ Phase 3 (LLM revises flagged sentences).

---

## 4. Current High-Priority Workstreams

If you are an agent tasked with extending this repository, focus on these three open engineering tasks:

### Task 1: Build `syntactic_transformer.py` (Beyond Regex)
- **Problem**: Regex cannot detect Subject-Verb-Object structures and invert them.
- **Goal**: Implement dependency parsing (using `spacy` or lightweight POS rule sets) to automatically convert:
  $$\text{Subject} + \text{Verb} + \text{Object} + \text{Prepositional Phrase} \implies \text{Prepositional Phrase} + \text{,} + \text{Subject} + \text{Verb} + \text{Object}$$
- **Impact**: Eliminates the #1 remaining cause of yellow highlights in Phase 1 outputs.

### Task 2: Build `burstiness_optimizer.py`
- **Problem**: LLMs generate uniform sentence lengths (e.g. all 7–8 words), causing burstiness $B_L < 0.20$.
- **Goal**: Write an algorithmic optimizer that computes $B_L = \sigma_L / \mu_L$. If $B_L < 0.45$, automatically split or merge sentences until $B_L \ge 0.50$.

### Task 3: Local Classifier Pre-flight Check
- **Goal**: Add a script (`evaluator.py`) that loads a local small model (`gpt2` or `distilroberta-base`) to calculate token-level cross-entropy loss, giving an instant local preview of AI score before submitting to external web detectors.
