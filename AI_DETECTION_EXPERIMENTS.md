# Empirical AI Detection Case Study (Post-v7.16.0 Release)

The complete benchmark case study detailing all experimental runs across structural, syntactic, and tonal variants on a leading enterprise academic AI detector is documented in:

👉 **[research/EMPIRICAL_DETECTION_CASE_STUDY.md](research/EMPIRICAL_DETECTION_CASE_STUDY.md)**

### Quick Summary of Experimental Findings:

1. **Option A (Continuous Narrative Flow):** **90% AI-generated** (56 segments flagged) | Similarity: 11%
2. **Option B (Itemized Remodeling):** **85% AI-generated** (59 segments flagged) | Similarity: 11%
3. **Organic Student Draft (Lower Adjective Density, Flesch 31.5):** **86% AI-generated** (54 segments flagged) | Similarity: 11%

### Key Architectural Discovery:
- Converting lists to continuous narrative paragraphs **increased** the AI score from 85% to 90% because the classifier's sliding window received uninterrupted contiguous text blocks.
- PyMuPDF vector forensics revealed that all **data tables (Tables I–IV)**, **mathematical formulas ($t(11)=13.42, p<0.001$, $W=0$)**, and **hardware/software specs** scored **0% AI (100% human-classified)** across every single run.
- Style prompting (formal academic vs. casual student) alone cannot escape the joint token probability distribution of an LLM.

For peer agentic review questions and detailed methodology, refer to the full study in `research/EMPIRICAL_DETECTION_CASE_STUDY.md`.
