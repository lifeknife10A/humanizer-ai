# v8.0 Architecture: Deterministic-First Humanization (Design Doc & Critique)

**Status:** Draft / design review. Stage 1 exists as a research prototype
(`research/scripts/ast_clause_splitter.py`); nothing here is wired into the
skill yet.
**Input proposal:** [`MULTI_AGENT_ARCHITECTURAL_BRIEFING.md`](MULTI_AGENT_ARCHITECTURAL_BRIEFING.md)
(Antigravity & Krishna) and [`EMPIRICAL_DETECTION_CASE_STUDY.md`](EMPIRICAL_DETECTION_CASE_STUDY.md).
**Author of this review:** Claude.

This document records (a) a critical review of the v8.0 briefing, and (b) the
architecture we should actually build, which keeps the briefing's correct core
insight while dropping the parts that contradict it or this repo's own evidence.

---

## 1. What the breakthrough did and did not prove

The milestone is real: *Clever AI Humanizer* + restored LaTeX got the IEEE paper
under Turnitin's 20% display threshold with 12% similarity and the 146 metrics
present. Two honest caveats carry into the design:

1. **"Below the 20% threshold" is not "0% AI".** Per [`LITERATURE_TRACKER.md`](LITERATURE_TRACKER.md)
   [P01], Turnitin *suppresses* the score below 20%. Clean pages partly reflect
   that suppression, not a per-sentence human verdict.
2. **The bypass was produced by an external tool whose internals are unknown.**
   Everything in the briefing's §2 is reverse-engineered *after the fact* from a
   diff. That is the central methodological problem below.

---

## 2. Critique of the reverse-engineered diagnosis (briefing §2)

**A diff shows what changed, not what caused the score to drop.** Many features
moved at once between the flagged draft and the evasion output; without an
**ablation** (toggle one feature, re-score), the five "rules" are a plausible
story, not a measured cause. The diagnosis also collides with this repo's own
prior evidence:

- The [case study](EMPIRICAL_DETECTION_CASE_STUDY.md) found style/structure/tone
  changes barely moved this detector (85% → 90%) and concluded they "DO NOT
  change joint token transition probability." The most parsimonious explanation
  for the turnaround is therefore *what the commercial tool does internally*
  (likely a fine-tuned or base-model paraphraser / detector-guided decoding — the
  methods [`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) §2 says actually work),
  not the five surface rules.

Rule-by-rule:

| Rule | Verdict | Reasoning |
| :--- | :--- | :--- |
| 1. Sentence decomposition (8–14 w) | **Plausible, but already ours** | This is style rule S1 (≤16 w). We already do it and it did not break Turnitin. Label study: sentence-length AUC 0.53–0.61 (near chance). A contributor at most. |
| 2. Demonstrative chaining ("This…", "These…") | **Doubtful / risky** | `check_draft.py` already *warns* on repeated openings (S3, parallel frames), and `WIKIPEDIA_SIGNS.md` lists vague demonstratives as a human-reviewer AI tell. Likely exploits one Turnitin snapshot while looking more templated to a reader and the next model. |
| 3. Back-to-back parentheticals `(…) (…)` | **Real mechanism, wrong target, quality cost** | Consecutive parens do spike local perplexity, but Turnitin is a *classifier*, and the case study already showed math/stats/parens scored **0%** — those spans were never the problem. `(94.2 ± 14.6s to 38.6 ± 6.2s) (t(11)=13.42, p<0.001)` is also poor IEEE style. |
| 4. Intentional lexical repetition | **Weakest claim** | "Classifiers read repetition as human" is unsupported in our sources. Deliberate clumsy repetition mostly reads as bad writing. High quality cost, low evidence. |
| 5. Voice wobble (active/passive) | **Plausible, low-risk, already ours** | This is S10. Case study says voice changes alone did not move the detector. |

**Conclusion:** rules 1 and 5 restate what we already do; 2, 3, 4 are post-hoc
and partly counterproductive. **An ablation is a prerequisite** before any of
these is hard-coded into an engine (see §6).

---

## 3. The core insight is correct — and it constrains the architecture

Krishna's question is the right one, and the literature backs it:

> Prompting an autoregressive model to "sound human" still samples from
> `P(wₜ | w₍<ₜ₎)`, which classifiers are trained to detect.

[`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) (Xu 2026): base-model continuations
read as **96.7% human**; the *instruct* model on the same prefix reads **30.3%**.
Instruction tuning is the fingerprint. So "stop relying on instruct-LLM
prompting" is sound.

**But this cuts against Stage 2 of the briefing.** A local Llama-3.2-3B **Instruct**
via Ollama is *still an instruction-tuned autoregressive LLM*. "Local" changes
where it runs, not what it is. And its two proposed escapes fight our hard
constraints:

- **High-temperature + min_p** raises perplexity (helps *perplexity* detectors,
  not necessarily a classifier) and is the direct enemy of **Zero-Hallucination
  (H1–H3)** — hotter sampling invents and drifts. On a paper with 146 locked
  numbers, that is a fidelity landmine.
- **Negative logit bias** on stock tokens is a surface ban we already do.

This is the project's **iron triangle** ([`CHALLENGES.md`](../CHALLENGES.md)),
sharpened: you cannot have all three of

1. locked fidelity (H1–H5),
2. an LLM doing the rewriting,
3. classifier evasion.

Pick two. The briefing's v8.0 reaches for all three and breaks at Stage 2.

---

## 4. The deterministic-first architecture we should build

Keep the briefing's correct parts (deterministic Stage 1, the LaTeX/fidelity
core), demote the LLM to optional, and make fidelity gates mandatory between
every stage.

```
[Source prose  (or LaTeX prose view, placeholders intact)]
      │
      ▼
[Stage 1 — Deterministic AST transforms]   ← PRIMARY, no sampling, no fingerprint
  • Dependency parse (spaCy/Stanza).
  • Coordinate-clause splitting; (experimental) participial-tail decoupling.
  • PROPOSE via parse → ACCEPT only if numbers + content lemmas preserved and
    every output sentence is well-formed. Else keep the original.   [prototype ✓]
      │  (check_draft.py gate)
      ▼
[Stage 2 — OPTIONAL local rephraser]        ← only if it can beat the gate
  • NOT an instruct SLM at high temperature (reintroduces the fingerprint and
    breaks fidelity). If used at all: a *base* model with detector-guided
    decoding (Cheng 2025), accepting a measured fidelity cost, OR skip entirely.
      │  (check_draft.py gate — hard FAIL on any new/dropped number)
      ▼
[Stage 3 — Local pre-flight triage]          ← weak signal, never a green light
  • A local score (perplexity window and/or a small classifier proxy) to rank
    risky spans. Treat as triage only: the label study found local proxies at
    chance vs ZeroGPT, and proxy↔commercial transfer is poor (AuthorMist: 2% on
    GPTZero). It cannot predict Turnitin.
      │
      ▼
[Stage 4 — LaTeX & Scientific Invariance]    ← existing core, unchanged
  • latex_prose.py restore + verify + compile. 100% byte-exact protected LaTeX.
```

**The reordering is the point:** value flows from the deterministic and fidelity
machinery (Stages 1 & 4), which are uniquely ours and add no LLM signature. The
generative stage is optional and, if present, must earn its place by passing the
same gate everything else does.

---

## 5. Stage 1 prototype (built, validated)

`research/scripts/ast_clause_splitter.py` implements Stage 1 on a real spaCy
dependency parse. Its contract is **propose via the parse, accept only if
provably faithful**; each candidate must pass three gates or the original
sentence is kept:

1. **Numbers preserved** — `check_draft.extract_numbers()` identical before/after
   (the repo's canonical, unit-free, digit==word number set).
2. **Content preserved** — multiset of content-word lemmas (NOUN/PROPN/VERB/ADJ/
   ADV/NUM) identical. This is the guard against the failure that retired
   `humanizer.py`: dropped, glued, or duplicated words. Function words (the
   dropped "and", the added "This") are not content and do not trip it.
3. **Well-formed** — every output sentence re-parses to a finite ROOT verb and an
   explicit subject, so no fragment is emitted.

Transforms:

- **Coordinate-clause split** (default, low risk). Only the coordinating
  conjunction (+ a comma) is dropped; all content stays in order. Verified
  examples:

  ```
  - We evaluated the platform with twelve users, and the results confirmed that scores rose from 2.3 to 12.6.
  + We evaluated the platform with twelve users. The results confirmed that scores rose from 2.3 to 12.6.
  ```

  Correctly **does not** split noun coordination ("images and videos and audio")
  or shared-subject VP coordination ("reduced X and improved Y") — those have no
  standalone right-hand clause.

- **Participial-tail decoupling** (`--participial`, EXPERIMENTAL). Generates a
  present 3sg finite verb from the participle's lemma:

  ```
  - ... across all cohorts, yielding higher conversion rates for the platform.
  + ... across all cohorts. This yields higher conversion rates for the platform.
  ```

  Higher risk: tense can shift (past main clause → present "This yields"), and
  "This" assumes a clear referent. Off by default; gated by well-formedness.

Tests: `tests/test_ast_clause_splitter.py` (16 tests; pure-morphology tests run
everywhere, parse tests skip when spaCy/en_core_web_sm is absent, matching the
pdflatex-skip convention).

**Dependency note:** Stage 1 needs `spacy` + `en_core_web_sm`. That is fine for a
research module (so does `pdf_to_md.py` with PyMuPDF), but it is a real new
dependency to weigh before any skill integration.

---

## 6. Validation plan (do this before building more)

1. **Ablation first.** Apply each of the briefing's five rules *individually* to
   the failing draft and re-score Turnitin. This converts §2 from story to a
   ranked causal measurement and will likely show 2–3 rules do nothing or hurt.
   Build Stage 1 only around rules that measurably matter.
2. **Fidelity regression.** Run Stage 1 over the benchmark + research corpora;
   assert zero `new-number`/`missing-number` and zero content-lemma drift via
   `check_draft.py`. (The gate makes this safe by construction; verify it.)
3. **Human-quality check.** Have the split output read by someone against IEEE
   norms. Splitting that produces choppy 5-word staccato trips our own
   `staccato` warning and reads as machine too — Stage 1 must target the 8–16word
   band, not minimum length.
4. **Detector re-test, per detector.** Score Stage-1 output on the *actual*
   target detector. Do not trust the local Stage-3 triage as a proxy.

---

## 7. Risks, limits, and the honest framing

- **Overfitting to one Turnitin snapshot.** Turnitin retrains; `WIKIPEDIA_SIGNS.md`
  §6 documents a tell (em-dashes) *reversing within a year*. Keep any
  detector-specific rules in swappable config, never in the deterministic core.
- **Deterministic transforms can still break grammar/meaning.** AST beats regex
  but is not infallible; the three gates are mandatory, not optional.
- **Academic quality vs. detector score are different objectives.** Back-to-back
  parentheticals, deliberate repetition, and over-splitting win the classifier
  and lose the reviewer. Optimize for the reader first.
- **Integrity.** This repo's standing position ([`AI_DETECTION_MECHANICS.md`](AI_DETECTION_MECHANICS.md)
  §5, [`TURNITIN_NOTES.md`](TURNITIN_NOTES.md), the case study's Question 4, and
  IEEE/ACM guidance) is that a low score means "does not match this detector's
  patterns," never "human," and that detectors should not be sole rejection
  criteria. With similarity at 12%, transparent disclosure of AI-assisted
  drafting is a defensible path, not only obfuscation. The engineering value of
  v8.0 is **fidelity-preserving structural rewriting**; evasion is a side effect,
  not the stated goal.
