# Wikipedia's "Signs of AI Writing": A Digest for This Pipeline

Distilled from the raw paste in [`c.md`](../c.md) — the full text of `Wikipedia:Signs of AI
writing` (WP:AISIGNS), the WikiProject AI Cleanup field guide, last edited 2026-10-31. Unlike
the detector research in [`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) and
[`AI_DETECTION_MECHANICS.md`](AI_DETECTION_MECHANICS.md), this is the **human-reviewer side**:
the tells that experienced editors use, with real examples and per-era vocabulary drift.

## 1. What the source is

A descriptive field guide, explicitly *not* prescriptive: "this list is descriptive, not
prescriptive; it consists of observations, not rules." Wikipedia's speedy-deletion criterion G15
accepts only the most objective signs (Markdown artifacts, chatbot correspondence left in the
text), and a detector score alone is never sufficient — their own caveat matches our label
study: detectors "perform better than random chance" but carry "non-trivial error rates".

## 2. The root cause it names — and why the fact sheet is the counter

The guide's framing is the cleanest one-line theory of AI style anywhere in our sources:

> LLMs regress to the mean: they omit specific, unusual, nuanced facts (statistically rare) and
> replace them with generic, positive descriptions (statistically common). RLHF then tunes the
> output toward the most broadly palatable prose. "The subject becomes simultaneously less
> specific and more exaggerated."

That is exactly the failure this repo's fact-sheet design attacks: the model cannot re-inject
specifics on its own (it doesn't have them), so the pipeline gets them from the author and the
checker fails any number that came from anywhere else.

## 3. Human detection ability (the adversary isn't only software)

| Finding | Number | Source |
| :--- | :--- | :--- |
| General population distinguishing LLM vs human text | no better than chance | Cheng et al. 2025 [independent] |
| Humans on German thesis excerpts | 57% recognition for AI texts, 64% for human | Fiedler & Döpke 2025 [independent] |
| "Expert" annotators (frequent LLM users) | **90% of AI text identified, 3.3% of human text misidentified** | Russell, Karpinska & Iyyer 2025 (ACL) [independent] |
| LLM influence on human speech/writing | measurable by 2024, one-directional (human → more like LLM, not vice versa) | Yakura 2024; Geng 2025; Druck 2026 [independent] |

Takeaway: casual reviewers guess; *heavy LLM users* detect reliably. Style-level evasion faces a
competent human adversary exactly when the reviewer knows LLM prose well.

## 4. Sign → pipeline coverage map

| Field-guide sign | Status in this repo |
| :--- | :--- |
| Rule of three ("adjective, adjective, adjective") | `TRIAD` regex + S5 (v5.0.0 era, still active) |
| Superficial "-ing" significance tails ("highlighting its importance...") | `PARTICIPIAL_TAIL` check — the guide independently ranks this a top tell |
| Significance puffery ("a pivotal role", "stands as a testament") | `STOCK_PHRASES` (pivotal, testament, vital role, ...) |
| Didactic disclaimers ("it is important to note") | `STOCK_PHRASES` |
| Em-dash formulaic overuse | `EM_DASH` check — **but see §6: the signal reversed in late 2026** |
| "Challenges and Future Outlook" outline conclusions | partially (anti-preaching rules) |
| AI vocabulary, era-specific | extended in v7.13.1 (see §7) |
| Negative parallelisms ("not only X but also Y", "not X, but Y", "Y rather than X") | added in v7.13.1 |
| Copula avoidance ("serves as" for "is") | not checked — too common in legitimate academic prose |
| Vague attribution ("Experts argue", "Industry reports") | not checked — H3-adjacent; noted as residual risk |
| Vague connection ("associated with", "connected to") | not checked — same reason |
| Operational leaks (Markdown in paste, `utm_source=chatgpt.com`, `↩`, placeholder dates, list-defined-ref errors) | not applicable to our deliverables — but see the citation risk in §8 |

## 5. The inverse list: signs of human writing (WP:HUMANSIGNS)

The guide's most novel content for this repo is what AI text *avoids*. Empirically more common
in 25 years of human Wikipedia writing than in AI text:

- simple **is/has** phrases (there is a, it has a)
- plain verbs: wrote, moved, used, tried, died (vs authored, relocated, utilized, attempted,
  passed away)
- **superlatives and definitive statements**: one of the best, is the only, was the first
- qualifiers and intensifiers: very, perhaps, tends to
- wordy constructions: as a result of, in order to, all of the, the fact that

Tension with our H5: H5 cuts filler ("fundamentally", "it is the case that") while the guide
lists wordy constructions as *human* tells. Reconciliation: H5 targets intensifiers that carry
no fact or hedge; the checker's hedge classes already protect may/often/suggests, and the
guide's own qualifiers (perhaps, tends to) are hedge-adjacent. The wordy connectives remain a
candidate signal, not a rule — our benchmark data governs. No checker change made for this.

## 6. Era drift — stock lists decay

| Era | Signature words | Shape |
| :--- | :--- | :--- |
| 2023–mid-2024 (GPT-4) | delve, tapestry, landscape, meticulous, underscore, testament, pivotal, vibrant, bolster, garner, interplay, intricacies | long flowing sentences, em dashes |
| mid-2024–mid-2025 (GPT-4o) | align with, enhance, foster, showcase, highlight, underscore | smoother, subtler positivity |
| mid-2025–mid-2026 (GPT-5) | emphasizing, enhance, highlighting, showcasing + canned attribution emphasis | fewer obvious words, more source-theater |
| mid-2026+ (GPT-6) | challenge, clearer, dependable, echoed, leverage, matters, multifaceted, practical, prioritize, quietly, steady, universally | **strict 8–20-word sentences, em dashes suppressed, comma/period monotony** |

Two consequences. First, the em-dash tell *reversed* after September 2026: new models avoid
dashes so hard that plain comma/period monotony became the sign — our `EM_DASH` warn stays
(it catches older-model output), but the burstiness/staccato checks are what catch the new
shape. Second, `STOCK_PHRASES` is a per-era artifact and needs periodic refresh; the GPT-6-era
word list above is the refresh candidate queue for when GPT-6-family output shows up in our
test corpus.

## 7. Adopted into `check_draft.py` (v7.13.1)

WARN-only additions to `STOCK_PHRASES`, chosen for being distinctive enough that legitimate
academic prose rarely uses them (stems, so inflections match): interplay, intricacies,
meticulously, garner*, bolster*, showcas*, foster*, underscore(s/d), renowned, nestled,
groundbreaking, deep dive, vibrant, enduring, exemplifies, "valuable insights", boast(s), and
the negative-parallelism pattern "not only ... but also". These are field-guide candidates, not
yet validated against our own benchmarks — they warn, they never fail.

Deliberately rejected (too common in legitimate academic writing; would drown the report):
robust, enhance, crucial, valuable (alone), align with, highlight (verb), serves as, features,
emphasizing.

## 8. Residual risks this source surfaces

1. **Plausible-but-fabricated citations.** The guide documents LLM references whose DOIs resolve
   to *unrelated real articles*, and real books whose cited pages don't contain the claim. Our
   H2/citation rule keeps the model from inventing citations, and the fact sheet is the only
   citation source — but the checker cannot verify that a source-provided citation is real.
   That verification stays with the author.
2. **The guide's deepest caveat applies to us:** "do not merely treat these signs as the
   problems to be fixed; that could just make detection harder." The substantive problems are
   fabrication and emptiness; the style signs are symptoms. This is the repo's standing
   position: the skill's value is the fidelity machinery (H1–H5, fact sheet, checker), not the
   cosmetic rules.
3. **Style consistency over time** is now a human-review signal (the guide's "pronounced shift
   in writing style" sign). Out of scope for a text tool; noted for completeness.
