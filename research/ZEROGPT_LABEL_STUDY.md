# What ZeroGPT Highlights: A Sentence-Label Study

We transcribed ZeroGPT's sentence highlighting for three rewrites of the same Haiku 4.5–written abstract (`data/llm_abstract_source.txt`, raw score 80%) and tested which measurable properties of a sentence predict whether it gets highlighted. Everything here can be reproduced with `python3 research/scripts/label_study.py` (add `--lm` for the language-model features).

## Data

| Rewrite | File | ZeroGPT score | Highlighted / known sentences |
| :--- | :--- | :--- | :--- |
| Gemini 3.6 (low), skill v6.2 | `llm_gemini36low_v6.2.txt` | 35.3% | 41 / 99 (41%) |
| Opus 5.5, skill v6.2 | `llm_opus55_v6.2.txt` | 27.2% | 24 / 94 (26%) |
| Gemini 3.6 (low), skill v6.3 | `llm_gemini36low_v6.3.txt` | 30.5% | 28 / 99 (28%) |

292 labelled sentences in total, 93 highlighted. Sentences hidden behind ads in the screenshots are marked unknown and excluded. Labels are in `data/zerogpt_sentence_labels.json`.

## Findings

1. **The score is roughly the highlighted share.** Each document's score sits close to the share of its sentences that were highlighted. Reaching under 10% means leaving at most about one sentence in ten highlighted.
2. **Highlights come in runs.** A sentence after a highlighted one was highlighted 69% of the time, against 15% after an unhighlighted one. ZeroGPT appears to score windows of text, so a single human-looking sentence inside a run rarely clears it. Runs should be rewritten as units.
3. **Position matters most.** Earlier sentences (the framing and taxonomy sections) are highlighted far more often (AUC 0.73). The results sections, with concrete numbers and named artefacts, mostly pass.
4. **Perplexity-style signals barely predict highlights.** Mean negative log-likelihood, top-10 token share and log-rank from GPT-2 and Qwen2.5-0.5B score AUC 0.41–0.55, and Binoculars-style scores (Qwen2.5-0.5B base vs. instruct) were similar. A local model therefore can't tell us which sentences ZeroGPT will flag. This matches the literature: proxy detectors transfer poorly to commercial ones (see `LITERATURE_REVIEW.md`, sections 2–3).
5. **Surface style features are weak too.** Sentence length, word length, long-word rate, nominalization rate and "-ing" rate all land between 0.53 and 0.61.

## Implications for the pipeline

- **A single pass without a detector has a ceiling.** On this abstract, three runs landed at 27–35% with the facts kept intact.
- **The one reliable signal is the detector itself.** The repo's own history agrees: the 2.9% benchmark came from rewriting exactly the highlighted sentences and rescanning. The skill therefore gains Phase 4, a detector-feedback loop (`scripts/flagged_runs.py`). It groups highlighted sentences into runs, rewrites only those runs, keeps every unhighlighted sentence as is, and gates each round with the fact and hedge checker.

## Phase 4 results on this abstract

| Round | Text | Change | ZeroGPT |
| :--- | :--- | :--- | :--- |
| 1 | `llm_opus55_v6.2.txt` | Single pass, skill v6.2 | 27.2% |
| 2 | `llm_round2_variant_A.txt` | Rewrote the 7 highlighted runs as longer, connected sentences | 19.5% |
| 2 | `llm_round2_variant_B.txt` | Rewrote the same runs in the authors' voice within the 16-word cap | **13.9%** |
| 3 | `llm_round3_variant_C.txt` / `_D.txt` | Rewrote B's 5 remaining runs: C continues B's style, D fronts the predicate ("…is the aim of jailbreaks") | pending |

Observations:
- **Highlight share still tracks the score:** 13.6% estimated against 13.9% for B, 21.0% against 19.5% for A.
- **One round of run-level rewriting cut the score by half (B).** The 16-word cap with the authors' voice beat longer connected prose.
- **Neighbours can flip.** Some sentences kept word for word were unhighlighted in round 1 but highlighted in round 2, for example "Such inputs are designed to elicit unintended or harmful outputs." This is more evidence that ZeroGPT scores context windows.

## Limits

These labels come from one abstract, one detector and single scans. ZeroGPT may change its model at any time, and repeated scans of the same text may differ by a few points.
