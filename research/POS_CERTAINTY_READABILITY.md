# Certainty, Readability and POS Signals: Grounding for the v7.14.0 Checks

This note records why the certainty and readability checks were added to
[`check_draft.py`](../skills/academic-humanizer/scripts/check_draft.py) in v7.14.0, and where
the claims behind them come from.

**Status and honesty label.** The grounding below is an **author-supplied gap analysis**
citing papers labelled [P01]–[P05]. Unlike the sources in
[`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md), these have **not yet been checked against their
primary records**, and none of the new checks has been validated against this repo's own ZeroGPT
benchmarks. They follow the same rule the v7.13.1 field-guide additions did
([`WIKIPEDIA_SIGNS.md`](WIKIPEDIA_SIGNS.md) §7): **they WARN, they never FAIL.** When a paper
here is verified or a benchmark is run, update this file and move the confirmed items into
`LITERATURE_REVIEW.md`.

## The author-supplied sources

| Ref | As described by the gap analysis | Used for |
| :--- | :--- | :--- |
| **[P01]** | Turnitin: 5–10 sentence segment windows striding one sentence; AIR-1 (July 2024) targets paraphrase | Already covered: run grouping (`flagged_runs.py`) and the Phase 4 "synonym swaps don't clear a run" guidance |
| **[P02]** | Russell & Iyyer, "StoryScope": AI converges on a ~0.49 centroid, humans occupy a 0.71+ rarity tail; discourse structure alone detects AI at 93.2% F1; AI over-moralizes (~77% vs ~52%) | Reinforces the fact sheet (rarity tail) and the new friction-preservation reread; anti-preaching is already S9 |
| **[P03]** | Ahlawat: commercial humanizers degrade rigor (inject typos, drop content) | Reinforces H1–H5; no new check |
| **[P04]** | Rodrigues et al. (iScience, SAGE log-odds): top AI n-grams match `STOCK_PHRASES`; AI shows +152% "certain" and +67% "cause" markers | **Certainty check** |
| **[P05]** | LASSO study: pronouns are the strongest negative predictor of AI (weight −99.28), auxiliaries −21.30, nouns +21.17; AI packs ~146 difficult words vs ~95, Flesch Reading Ease ~28 vs ~55, FK grade ~13.8 vs ~10.3; passive voice 11% (AI) vs 34% (human) | **Readability check**; **S10 refinement** (passive voice); pronoun/nominalization deferred |

## What was adopted in v7.14.0

1. **Certainty marker check** (`certainty` WARN) — from [P04]. The draft is flagged only when it
   uses **more** unearned certainty adverbs ("clearly", "undeniably", "definitively",
   "certainly", …) than the source, exactly mirroring the existing `modal`/"must" check. It is
   grouped with the fidelity findings because added certainty is overclaiming (H3-adjacent), not
   a style choice.
2. **Flesch readability** (`readability` WARN + two informational stats) — from [P05]. The report
   prints Flesch Reading Ease and Flesch-Kincaid grade (a pure-stdlib syllable heuristic, no new
   dependencies) and warns once when Reading Ease falls below 30 on a draft of 10+ sentences.
   Academic prose is legitimately dense, so this never fails and the guidance explicitly forbids
   swapping out a technical term to raise the score (H2).
3. **S10 passive-voice refinement** — from [P05]. S10 still prefers the authors' active voice for
   claims, because that is the style that cleared the most highlighted runs in this repo's own
   Phase 4 tests ([`ZEROGPT_LABEL_STUDY.md`](ZEROGPT_LABEL_STUDY.md)). The refinement only stops
   *over*-conversion: keep the source's passive for methods and objective results. [P05]'s
   finding (humans use far more passive) and the repo's ZeroGPT result point in opposite
   directions, so the change is deliberately conservative — a clarification, not a reversal.
4. **Scientific-friction reread** — from [P02]. A new bullet in the fidelity reread (SKILL.md
   step 4) asks the rewriter to keep every caveat, limitation, edge case and parameter
   sensitivity the source states, instead of smoothing real science into one tidy story. It is
   bounded by H3: keep the friction that is there, never invent any.

## Deliberately deferred

- **Pronoun deficit / nominalization density / passive-voice ratio as checks.** [P05]'s strongest
  signals, but reliable measurement needs POS tagging. `check_draft.py` is pure-stdlib and
  deterministic by design; regex proxies for these are noisy enough to risk drowning the report.
  Candidate for a future informational-only pass, calibrated against the repo's benchmarks first.
- **Dale-Chall "difficult words."** Requires vendoring a ~3,000-word familiar-word list; Flesch
  Reading Ease already proxies vocabulary density without a data dependency.
- **AIR-1 purple-paraphrase characterization.** Already handled in practice by Phase 4's
  "restructure, don't polish" guidance; no new mechanism added.
