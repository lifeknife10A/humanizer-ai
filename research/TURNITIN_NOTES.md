# Turnitin: A Research Digest for the Humanizer Pipeline

Distilled from the raw paste in [`a.md`](../a.md) (Wikipedia-sourced), cross-checked against
[`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md). Source labels follow that file's convention:
**[vendor claim]**, **[independent]**, **[press]**, **[legal record]**. The raw paste is the
primary input; treat its numbers as Wikipedia-relayed unless marked otherwise.

## 1. Two products, one brand — do not confuse the reports

| Product | What it measures | Output |
| :--- | :--- | :--- |
| **Similarity Report** | Text overlap with 1.9B student papers, crawled web, licensed databases [Wikipedia paste, Mathewson 2025] | % matched text, source list |
| **AI Writing Detection** (since early 2023) | Probability that prose was machine-generated [Wikipedia paste] | % AI + sentence highlights |

Most "Turnitin flagged my paper" stories mix these up. A high *similarity* score means matched
sources; a high *AI* score means classifier confidence. They share no machinery, and the
similarity engine's known flaws (below) say nothing about the AI detector and vice versa.

## 2. Scale and business facts

- 16,000+ institutions, 71M+ students licensed as of 2025 [Wikipedia paste, press release/Markup].
- Student-paper database: 1.9 billion submissions as of June 2025 [Wikipedia paste, Mathewson 2025].
- Acquired by Advance Publications for $1.75B in 2019; absorbed VeriCite (2018), Unicheck (2020),
  Ouriginal/Urkund/PlagScan (2021) [Wikipedia paste].
- Pricing is negotiated per institution and varies ~3.6x: $1.79/student (CUNY) to $6.50/student
  (UC Irvine continuing ed), 2021–22; AI detection is a paid add-on ($3.19/student extra for
  Cal State in 2024) [Mathewson 2025, The Markup].
- Princeton, Harvard, Yale, Stanford opted out as early as 2006 [Daily Princetonian 2006].

## 3. The AI detector: what is known

- [vendor claim, relayed by Inside Higher Ed 2023-06-01, already in LITERATURE_REVIEW] Document
  FPR <1% for documents scoring above 20% AI; sentence-level FPR ~4%; **54% of false-positive
  (human-written) sentences sit directly next to AI-written sentences** — sentences are judged in
  context, not alone.
- [vendor claim, Wikipedia paste] Turnitin believes ~1% of papers it flags as AI-written were
  human-written, and that a larger share of AI-written papers is never flagged (asymmetric
  errors: misses are cheaper for them than false accusations, but both exist).
- [independent, already in LITERATURE_REVIEW] Weber-Wulff 2023 (14 tools incl. Turnitin): all
  tools below 80% accuracy; ~50% of manually edited AI text went undetected; accuracy on
  machine-paraphrased text 26%. Perkins 2024 (6 tools, 805 samples): mean accuracy 39.5%,
  dropping a further 17.4% after evasion edits.
- [press cluster, Wikipedia paste] Repeated false-accusation cases involved students using
  **Grammarly** — grammar-correction output trips the detector (EdSurge, Fast Company, The Hill,
  FOX 5 Atlanta, Inside Higher Ed, 2023–24). Several schools disabled the feature in 2023
  (The Register; campus papers).
- **Not verified:** the segment/window architecture, minimum length, and the 1–19% handling.
  Turnitin returned HTTP 403 to fetches during the LITERATURE_REVIEW work, and again to ours
  (both the live blog and the Wayback captures returned navigation chrome without the article
  body). The source code is closed, so no independent audit of methodology exists
  [Cortelazzo, via Wikipedia paste].
## 4. Documented technical flaws (similarity engine, peer-reviewed)

- **Turnitoff** [Heather 2010]: ad-hoc encodings, rearranged font glyphs, and text rendered as
  Bézier curves defeat matching.
- **Paraphrase tools** [Rogerson & McCarthy 2017]: free online paraphrasers and article spinning
  were not detected; Turnitin's marketing VP called it "not a big concern" because output
  quality was poor [Straumsheim 2017].
- **Terminology false positives** [Texas Tech, via Jaschik 2009]: much flagged "non-originality"
  is legitimate jargon, course terms, and topic phrases ("the prevalence of childhood obesity
  continues to rise").

## 5. Legal and institutional landscape

- *Vanderhye et al. v. iParadigms LLC* (4th Cir. 2009): archiving student papers is **fair use**
  in the US; click-wrap acceptance defeated the copyright claim [legal record].
- McGill (2004, 2005) and Mount Saint Vincent (2006) ruled/banned in students' favor over
  mandatory submission; MSVU's was Canada's first campus-wide ban, citing PATRIOT Act exposure
  of student data held by a US company [press/legal record].
- Standing criticisms: presumption of guilt, commercial exploitation of student work, closed
  methodology, and the WriteCheck episode (iParadigms sold students pre-checks against the same
  database — "warlords arming both sides" [Tabarrok, via Wikipedia paste]; WriteCheck withdrawn 2020).

## 6. Implications for this pipeline

1. **The runs finding transfers.** Turnitin's own 54% adjacency figure is the same phenomenon
   our label study measured in ZeroGPT (a sentence after a highlighted one is highlighted ~69%
   of the time vs ~15% otherwise). Detector feedback must be consumed as **runs**, which is what
   `flagged_runs.py` does. Phase 4 is detector-agnostic for this reason.
2. **A 0% target is noise-floor chasing.** With a ~4% sentence-level FPR [vendor claim], a
   100-sentence document may show ~4 flagged sentences even when fully human. The skill's
   sub-10% stopping rule is correctly placed; below that you are rewriting Turnitin's errors,
   not the text's tells.
3. **Grammarly-class edits are a flag risk** [press cluster]. Hedge-preserving, fact-locked
   rewrites (H1–H5) stay close to the author's own text; heavy grammar-tool smoothing is what
   the false-accusation cases had in common.
4. **Similarity and AI scores need different responses.** Jargon/topic-phrase matches inflate
   similarity (Texas Tech finding) and are *expected* in technical writing — do not "fix" them
   by rewording standard terminology; that trades an AI-detector gain for a content error (H2).
5. **Score divergence is structural, not a malfunction.** Three detectors with different
   training data, thresholds, and windowing will rank the same document differently. The only
   portable unit of work is the **highlighted sentence**, not the percentage.
