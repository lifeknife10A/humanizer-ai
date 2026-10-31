# How AI Text Detection Works at the Lowest Level

Distilled from the raw paste in [`b.md`](../b.md) (Wikipedia, "Artificial intelligence content
detection"), grounded in [`MATHEMATICS.md`](../MATHEMATICS.md) and
[`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md). Text only; image/audio/video detection is out of
scope. Source labels: **[vendor]**, **[independent]**, **[press]**.

## 1. The one mechanism underneath

Every text detector reduces to the same two steps:

1. **Score.** Convert the document into a scalar (or per-sentence vector) that measures how
   *predictable* or *typical* the text looks to some reference point — a language model, a
   trained classifier, or a known sampling bias.
2. **Threshold.** Compare the score to a cut-off τ chosen to trade false positives against
   false negatives. Everything else — dashboards, percentages, sentence highlighting — is
   presentation built on top of those two steps.

Detection is therefore never proof of authorship. It is a statistical guess whose quality is
bounded by how much the human and machine distributions overlap.

## 2. The five detection families

| Family | Lowest-level mechanism | Used by | Fails when |
| :--- | :--- | :--- | :--- |
| **Perplexity / cross-entropy** | A reference LM scores each token: H(W) = −(1/N)Σ log P(w_i \| w_<i). AI text is low-H (predictable); threshold on the average or on sliding windows PPL_k(t) | Early GPTZero; what third parties attribute to ZeroGPT (unverified) | Any fluent-but-human text (non-native writers, legal/technical formulaic prose); any paraphrase that moves token choices |
| **Burstiness** | Variance of the per-sentence scores: B = σ/μ over sentence perplexities or lengths. Humans spike; models are uniform | GPTZero (pre-2023), ZeroGPT (attributed) | Uniformly measured human prose; models run at high temperature or heavily edited |
| **Rank-based (GLTR, log-rank)** | For each token, its rank in the LM's next-token distribution; AI text concentrates in the top-k ranks | GLTR, DetectGPT (log-prob curvature under perturbation) | Needs a reference LM close to the generator; degrades on short or edited text |
| **Supervised classifiers** | A fine-tuned encoder (RoBERTa/DeBERTa class) learns the human/AI boundary from labelled corpora; sentence probabilities come from the same forward pass as the document label | Turnitin, GPTZero (post-2023), Copyleaks, Originality.ai | New generators or domains it wasn't trained on — M4 found such detectors tend to call unseen machine text *human* [Wang 2024]; accuracy collapses under paraphrase (26% in Weber-Wulff) |
| **Watermarking** | The *generator* biases sampling toward a pseudo-random "green list" of tokens (Kirchenbauer 2023); detection is a z-test on green-token fraction | DeepMind SynthID (images shipped; text experimental) | Only works if the generator cooperates — useless against third-party text; degrades under insertion/deletion/substitution and homoglyph attacks; Wired: "Researchers Tested AI Watermarks — and Broke All of Them" |

A sixth, weaker family — **surface-style heuristics** (stock transitions, uniform sentence
length, triads, rhetorical templates, per the paste's "stylistic and structural regularities") —
is what this repo's S1–S5 rules and the 10 Linguistic Laws attack directly. It is also what
commercial "bypasser" tools scramble.

## 3. Why the threshold step can never be solved

1. **Distributions overlap.** As machine text approaches human text, the sample complexity of
   distinguishing them grows without bound [Chakraborty 2023, in LITERATURE_REVIEW]. No
   threshold separates overlapping distributions; every τ buys false positives at the price of
   false negatives. Turnitin states the asymmetry openly: <1% FPR [vendor] against a stated
   15% false-negative rate [vendor, paste ref 8].
2. **Transformations break calibration.** Paraphrasing shifts the score distribution without
   changing authorship: Originality.ai went from 91.3% to 27.8% mean accuracy after an
   Undetectable.ai pass [Taloni 2023, Eye]; MIT Technology Review found the same for light
   human rearrangement plus a paraphrasing tool.
3. **Base-rate arithmetic.** If 5% of submitted work is AI-assisted and the detector has a 1%
   FPR, false accusations approach 1 in 6 of all accusations. Vendor FPR claims are measured on
   clean benchmarks, not on deployed text — the Washington Post measured ~50% on a small
   real-world sample [press].
## 4. Measured reliability (from the paste, labels preserved)

| Finding | Number | Source |
| :--- | :--- | :--- |
| 14 tools tested (incl. Turnitin, GPTZero) | all < 80% accuracy, only 5 > 70%; biased toward "human"; worse after paraphrasing | Weber-Wulff 2023 [independent] |
| Turnitin document FPR claim | < 1% | [vendor] |
| Washington Post real-world test | up to ~50% FP on a small sample | [press] |
| Turnitin false-negative rate claim | 15% | [vendor] |
| 7 detectors on non-native English essays | **61.3% average false-positive rate** | Liang 2023, Patterns [independent] |
| Detector FP rates by student group (2024) | Black 20% / Latino 10% / White 7% | Common Sense Media [independent survey] |
| Originality.ai on GPT-4 abstracts | 91.3% → 27.8% after Undetectable.ai | Taloni 2023 [independent] |
| Documented false accusations | UC Davis (cleared), Texas A&M-Commerce (professor used ChatGPT itself as a detector; students exonerated), Janelle Shane's own book flagged, freelance writers fired (Gizmodo 2024) | [press] |
| Institutional opt-outs | Cambridge + Russell Group (Apr 2023), UT Austin (Oct 2023), Princeton/Harvard/Yale/Stanford (similarity tool, 2006) | [press] |

The bias findings are mechanical, not incidental: perplexity- and classifier-based scores key
on predictability, and non-native, neurodivergent, and formulaic-technical writing *is* more
predictable. The detector punishes exactly the writers who write plainly.

## 5. Implications for this pipeline

1. **We attack family 6 and the windowing of families 1–2.** The style rules (S1–S5, the 10
   Linguistic Laws) remove exactly the surface features heuristic and windowed-perplexity
   detectors key on. The empirical record (benchmarks 00–07) is consistent with that.
2. **Supervised classifiers (family 4) are why single-pass ceilings exist.** A neural
   classifier trained on LLM corpora sees distributional fingerprints no style rule enumerates
   — which is what the label study measured (local proxies at chance, AUC 0.41–0.55) and why
   Phase 4 needs the detector's own feedback.
3. **Watermarking is not a threat model for this repo.** It requires generator-side
   cooperation and breaks under paraphrase; nothing a post-hoc editor does interacts with it.
4. **Every detector's stated FPR is a floor, not a ceiling.** Vendor numbers come from clean
   benchmarks; deployed numbers (WaPo ~50%, Liang 61.3% on non-native essays) are far worse.
   Any detector score on a heavily edited text should be read as ± large error bars.
5. **The honest framing for users:** a low score means "does not match the patterns this
   detector was built to catch," never "this text is human." The skill's job is fidelity to the
   author's real facts (H1–H5); the score is a side effect.
