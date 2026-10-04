---
name: academic-humanizer
description: "Rewrites AI-drafted academic text (papers, theses, reports) into varied, specific prose without the patterns AI detectors key on: uniform sentence length, stock transitions, three-item lists, participial tails, and preachy conclusions. Keeps every number, term, and list item from the source. Added specifics come only from an author-supplied fact sheet, and a bundled checker blocks any invented or dropped number. Use when asked to humanize, de-AI, or rewrite academic text."
metadata:
  version: "6.0.0"
  triggers:
    - "/humanizer"
    - "/academic-humanizer"
    - "/humanize"
    - "/hu"
    - "humanize"
    - "humanize text"
    - "academic humanizer"
    - "humanize paper"
---

# Academic Humanizer (v6.0.0)

Rewrite AI-drafted academic text so it reads like a specific author wrote it, in one run, without changing what it says.

The work happens in three phases. You rewrite the text (Phase 1). `scripts/check_draft.py` compares your rewrite with the source and fact sheet (Phase 2). You revise only the sentences it flags (Phase 3). Nothing rewrites your text after you.

## Inputs

| Input | Required | What it is |
| :--- | :--- | :--- |
| Source text | Yes | The text to rewrite. Every number, term, and list item in it must survive. |
| Fact sheet | No | Real details from the author (parameters, instrument settings, results, citations) that may be added. Template: `fact_sheet_template.md` in this skill's directory. |

The fact sheet is the only place added specifics can come from. Without one, you keep length by unpacking sentences and add no new detail.

If no fact sheet was given, don't stop to ask for one. Work from the source alone and list what the author could add at the end (step 6).

## Procedure

`SKILL_DIR` below means this skill's directory. Work in a scratch directory.

1. **Save the inputs** as `source.txt` and, if given, `facts.md`.
2. **Read the fact ledger.**
   ```bash
   python3 SKILL_DIR/scripts/check_draft.py source.txt --facts facts.md
   ```
   It lists every number, acronym, and formula in the source (all must appear in your draft) and in the fact sheet (these may be added). Nothing else may appear in your draft. Drop `--facts facts.md` when there is no fact sheet.
3. **Rewrite (Phase 1)** paragraph by paragraph, following the hard constraints and then the style rules below. Before saving, reread each rewritten paragraph against its source paragraph for H3 and H4. Save the result as `draft.txt`.
4. **Check (Phase 2).**
   ```bash
   python3 SKILL_DIR/scripts/check_draft.py source.txt draft.txt --facts facts.md
   ```
5. **Revise (Phase 3).** Rewrite only the sentences the report names, then run step 4 again. Stop after two revision rounds.
   - `new-number` FAIL: delete the number, or go back to the source's wording. Never fix it by adding the number to the fact sheet yourself.
   - `missing-number` FAIL: restore the content of the source sentence the report quotes.
   - `new-term` WARN: use the source's wording unless the fact sheet gives the term.
   - `retention` FAIL: unpack more sentences, or use more fact-sheet detail. If neither is possible without padding, leave the shortfall and report it.
   - Style WARNs: fix each one unless the fix would break a hard constraint.
6. **Deliver:**
   - the final text in one copy-pasteable block
   - the final checker report
   - the fact-sheet details you used
   - anything left unresolved, with the reason (for example, a retention shortfall)
   - **Details you could add**: vague spots in the source where the author's real specifics would help, written as questions. Example: "Spark plasma sintering: what temperature, pressure, and hold time?" Ask these; never answer them yourself.

Never deliver with a `new-number` or `missing-number` failure. Both can always be fixed by deleting an added number or restoring a dropped one.

If you can't run Python, do steps 2 and 4 by hand. List every number, acronym, and formula in the source and fact sheet, then compare your draft against that list sentence by sentence.

## Hard constraints

These are never traded for style.

- **H1. Numbers.** Every number in the draft comes from the source or the fact sheet. Every number in the source appears in the draft, as digits or words.
- **H2. Names and terms.** Add no materials, formulas, techniques, instruments, datasets, acronyms, authors, institutions, or citations that aren't in the source or fact sheet. Don't make a generic name more specific. "Lithium lanthanum zirconium tantalum oxide" doesn't become a stoichiometric formula unless the fact sheet gives that formula.
- **H3. Claims.** Add no results, mechanisms, causes, comparisons, or first-person experimental actions that the source or fact sheet doesn't state. "In our load frames, pellets cracked above 6.5 MPa" is an invented experiment if the source never mentions it. Keep hedges exactly as strong as the source: "may suggest" stays tentative.
- **H4. Lists.** Keep every item of every list. Restructure a list; never shorten it.
- **H5. Length.** The draft has at least 95% of the source's word count. Get there by unpacking long sentences into several complete ones and by using fact-sheet details. Never pad with field background, restatement, or invented specifics. An honest shortfall is better than padding.

The checker enforces H1 and the length floor in H5, and flags likely H2 violations. It can't see H3 or H4, so those depend on your reread in step 3.

## Style rules

Apply these within the hard constraints. When a style rule and a hard constraint conflict, the hard constraint wins.

- **S1. Sentence length.** Keep sentences to 16 words or fewer. Unpack longer ones into complete sentences that keep every clause. Don't compress.
- **S2. Short sentences.** Use 3–5 word sentences regularly, at irregular intervals. Each one states something specific from this text ("Resistance tripled.", "Coated cells survived."). No generic slogans, and never reuse a short sentence or its pattern ("Peak currents compound damage." followed later by "Mechanical loads compound stress.").
- **S3. Sentence openings.** Don't start three sentences in a row with the same word. Front some sentences with a prepositional or adverbial phrase drawn from the content ("At 1.0 mA cm⁻², ...", "During stripping, ...").
- **S4. Paragraph openings.** Start with the paper's specific problem or finding, not field background ("As demand for energy storage grows...").
- **S5. Three-item lists.** Avoid the "A, B, and C" rhythm by splitting items across sentences, or by grouping two and giving the third its own sentence. Never drop an item (H4).
- **S6. Punctuation.** No semicolons. No reveal colons ("The reason is clear: ..."). Colons in titles, ratios, and times are fine.
- **S7. Tails and "however".** Split ", cutting X..." into ". This cut X...". Rewrite "X, however, Y" as "Yet X Y" or as two sentences.
- **S8. Stock phrasing.** Cut: Furthermore, Moreover, Additionally, Notably, Ultimately, In conclusion, In summary, In short, It is important/crucial to note, pivotal, vital role, integral role, tapestry, delve into, testament, paramount, transformative potential, the landscape of, cornerstone, synergy, holistic, and "To address these challenges, we...".
- **S9. Conclusions.** Replace mandates ("must deploy", "is paramount for", "hinges on") with what the results show. If the source makes a recommendation, keep it as a plain recommendation. Don't turn it into a mechanism the source doesn't describe.

## Examples

**Unpacking without a fact sheet.**

Source (23 words):
> When solid-state cells undergo prolonged galvanostatic cycling, microscopic void formation, contact loss, and lithium dendrite propagation inherently jeopardize electrochemical performance and structural integrity.

Rewrite (24 words):
> Prolonged galvanostatic cycling endangers solid-state cells. Microscopic voids form and contact is lost. Lithium dendrites also propagate. Electrochemical performance and structural integrity both suffer.

All three failure modes and both consequences survive, and no detail was added.

**Using a fact sheet.**

Source:
> Participants completed a validated anxiety questionnaire.

Fact sheet line:
> - Anxiety measure: GAD-7, given at baseline and at week 8

Rewrite:
> Participants completed the GAD-7 anxiety questionnaire at baseline and again at week 8.

Without that fact sheet line, keep the source's wording and add to "Details you could add": "Which anxiety questionnaire, and when was it given?"

## Known limits of the checker

- It compares numbers without units. "1.0 MPa" passes if the source has "1.0 mA cm⁻²" somewhere.
- It tracks only acronym- and formula-shaped terms (two or more capitals, or a capital plus a digit). Invented plain-word names, and invented authors without a year, get through.
- It ignores ordinals ("first", "second") and a lone "one".
- It can't judge claims, hedging, or whether a list kept all its items. That's H3 and H4, and it's on you.
