---
name: academic-humanizer
description: "Rewrites AI-drafted academic text (papers, theses, reports) into varied, specific prose without the patterns AI detectors key on: uniform sentence length, stock transitions, three-item lists, participial tails, and preachy conclusions. Keeps every number, term, and list item from the source. Added specifics come only from an author-supplied fact sheet, and a bundled checker blocks any invented or dropped number. Use when asked to humanize, de-AI, or rewrite academic text."
metadata:
  version: "6.2.0"
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

# Academic Humanizer (v6.2.0)

Rewrite AI-drafted academic text so it reads like a specific author wrote it, in one run, without changing what it says.

The work happens in three phases. You rewrite the text and reread it against the source (Phase 1). `scripts/check_draft.py` compares your rewrite with the source and fact sheet (Phase 2). You revise what it flags (Phase 3). Nothing rewrites your text after you.

## Inputs

| Input | Required | What it is |
| :--- | :--- | :--- |
| Source text | Yes | The text to rewrite. Every number, term, claim, and list item in it must survive. |
| Fact sheet | No | Real details from the author (parameters, instrument settings, results, citations) that may be added. Template: `fact_sheet_template.md` in this skill's directory. |

The fact sheet is the only place added specifics can come from. Without one, you keep length by unpacking sentences and add no new detail.

If no fact sheet was given, don't stop to ask for one. Work from the source alone and list what the author could add at the end (step 7).

## Procedure

`SKILL_DIR` below means this skill's directory. Work in a scratch directory.

1. **Save the inputs** as `source.txt` and, if given, `facts.md`.
2. **Read the fact ledger.**
   ```bash
   python3 SKILL_DIR/scripts/check_draft.py source.txt --facts facts.md
   ```
   It lists every number, acronym, and formula in the source (all must appear in your draft) and in the fact sheet (these may be added). Nothing else may appear in your draft. Drop `--facts facts.md` when there is no fact sheet.
3. **Rewrite (Phase 1)** paragraph by paragraph, following the hard constraints and then the style rules below. Leave titles and headings unchanged. Save the result as `draft.txt`.
4. **Fidelity reread.** The checker can't see claims or lists, so do this before checking. Put each source paragraph next to its rewrite and confirm:
   - every list item is still there (H4)
   - every claim is still there, and none was added (H3)
   - each purpose is still a purpose: "implemented to evaluate X" must not become "we compared X"
   - findings are hedged exactly as strongly as in the source
   - no count was added that the source doesn't state ("all three", "two processes")

   Fix `draft.txt` before moving on.
5. **Check (Phase 2).**
   ```bash
   python3 SKILL_DIR/scripts/check_draft.py source.txt draft.txt --facts facts.md
   ```
6. **Revise (Phase 3).** Fix the sentences the report names. Some warnings cover the whole document (`retention`, `short-sentences`, `add-on` without a location); for those, change whichever sentences fix it best. Then run step 5 again. Stop after two revision rounds.
   - `new-number` FAIL: delete the number, or go back to the source's wording. Never fix it by adding the number to the fact sheet yourself.
   - `missing-number` FAIL: restore the content of the source sentence the report quotes.
   - `new-term` WARN: use the source's wording unless the fact sheet gives the term. To shorten a term the source spells out, define the abbreviation at first use: "electrochemical impedance spectroscopy (EIS)".
   - `retention` FAIL (too short): unpack more sentences, or use more fact-sheet detail. If neither is possible without padding, leave the shortfall and report it.
   - `retention` WARN (too long): cut filler (see H5), define abbreviations for long repeated terms, and merge fragments you over-split. If the extra length comes from fact-sheet detail (the draft minus the words those details added is within 110%), leave it and report it so the author can decide against any word limit.
   - `short-sentences` WARN: lead with a claim's core in 3–5 words and move its details to the next sentence (see S2). If no claim is left that splits naturally, stop and report the share; never split off a modifier to reach the number.
   - `add-on` WARN: work the item in another way (see S5) instead of tacking it on with "too", "as well", or "also".
   - Other style WARNs: fix each one unless the fix would break a hard constraint.

   Rerun the fidelity reread (step 4) on every sentence you changed.
7. **Deliver:**
   - the final text in one copy-pasteable block
   - the final checker report
   - the fact-sheet details you used
   - anything left unresolved, with the reason (for example, a retention shortfall or a conflict between the source and the fact sheet)
   - **Details you could add**: vague spots in the source where the author's real specifics would help, written as questions. Example: "Spark plasma sintering: what temperature, pressure, and hold time?" Ask these; never answer them yourself.

Never deliver with a `new-number` or `missing-number` failure. Both can always be fixed by deleting an added number or restoring a dropped one.

If you can't run Python, do steps 2 and 5 by hand. List every number, acronym, and formula in the source and fact sheet, then compare your draft against that list sentence by sentence.

## Hard constraints

These are never traded for style.

- **H1. Numbers.** Every number in the draft comes from the source or the fact sheet. Every number in the source appears in the draft, as digits or words. Counts are numbers too: don't write "two processes" or "all three" unless the source states that count, because the checker can't tell a true count from an invented one. "Both" and ordinals ("the first", "the second") are fine when they refer to items the source lists. Don't turn a number into a multiple ("rose by 312%" is not "tripled").
- **H2. Names and terms.** Add no materials, formulas, techniques, instruments, datasets, acronyms, authors, institutions, or citations that aren't in the source or fact sheet. Don't make a generic name more specific. "Lithium lanthanum zirconium tantalum oxide" doesn't become a stoichiometric formula unless the fact sheet gives that formula. Defining a standard abbreviation for a term the source spells out is fine: "lithium lanthanum zirconium tantalum oxide (LLZTO)". So is the standard symbol for a unit the source names ("megapascals" becomes "MPa").
- **H3. Claims.** Add no results, mechanisms, causes, comparisons, or first-person experimental actions that the source or fact sheet doesn't state. "In our load frames, pellets cracked above 6.5 MPa" is an invented experiment if the source never mentions it. Keep purposes as purposes. Keep findings hedged exactly as strongly as the source: "may suggest" stays tentative, "confirmed" stays confirmed. You may turn the source's passive voice into "we" for work it presents as the authors' own. If the fact sheet contradicts the source or describes the same thing differently ("synthesized" vs. "densified"), follow the fact sheet (the author wrote it) and report the difference.
- **H4. Lists.** Keep every item of every list. Restructure a list; never shorten it.
- **H5. Length.** The draft is 95–110% of the source's word count. Unpacking adds words (repeated subjects, new sentence openings), so offset it by cutting filler. Filler is wording that carries no fact, claim, item, or hedge, such as "fundamentally", "inherently", "notoriously", "comprehensive", "successfully", "it is the case that". Keep intensifiers that state size ("dramatically", "exponentially") and "significantly" when it means statistical significance. Cutting filler is not truncation. Never pad with field background, restatement, or invented specifics. An honest shortfall is better than padding. Use the fact-sheet details that make the source's statements specific; you don't have to use all of them. When a fact-sheet value makes a vague word redundant ("high-temperature" next to 1150 °C, "ultra-thin" next to 5 nm), drop the vague word. Fact-sheet detail may still take the draft above 110%; report it rather than cutting details you used.

The checker enforces H1 and the length floor in H5, and flags likely H2 violations. It can't see H3 or H4, so those depend on your fidelity reread (step 4).

## Style rules

Apply these within the hard constraints. When a style rule and a hard constraint conflict, the hard constraint wins.

- **S1. Sentence length.** Keep sentences to 16 words or fewer. Unpack longer ones into complete sentences that keep every clause.
- **S2. Short sentences.** Aim for about one sentence in five with 3–5 words, placed irregularly. The checker warns below 15%. The natural way to get one is to lead with a claim's core and give its details in the next sentence: "Interfacial impedance escalated rapidly. Over the first fifty cycles at 1.0 mA cm⁻², area-specific resistance rose by 312%." Each short sentence needs its own subject and a verb that states something the source claims. Never make one by:
  - splitting off a modifier ("Protocols should be standardized. These should be rigorous.", "Demand surged. It grew exponentially.")
  - adding a generic slogan ("The math reflects physics.")
  - reusing a short sentence or its wording frame ("Peak currents compound damage." then "Mechanical loads compound stress.")

  If the text runs out of claims that split naturally, stop below the target and report the share.
- **S3. Sentence openings.** Don't start three sentences in a row with the same word. Front some sentences with a prepositional or adverbial phrase drawn from the content ("At 1.0 mA cm⁻², ...", "During stripping, ...").
- **S4. Paragraph openings.** Start each paragraph with the paper's specific problem or finding (in a methods paragraph, with what was done or why). Background sentences that are in the source are content, so keep them, but move them out of the paragraph's first sentence.
- **S5. Three-item lists.** Break the "A, B, and C" rhythm without dropping an item. Vary the method across the document:
  - Give one item the main clause and the others a phrase ("Microscopic voids form during cycling, accompanied by contact loss and dendrite growth."). Don't imply an order or a cause the source doesn't state.
  - Announce and walk through ("Three strategies were tested. The first deposited...").
  - Give two items one sentence and the third its own sentence with its own verb and angle.

  Never end the split-off item with "too", "as well", or "alongside them", and don't lean on "also". Swapping in "along with", "together with", or "alongside" everywhere just moves the pattern. The checker warns when more than two sentences end with an add-on or when these connectors are overused.
- **S6. Punctuation.** No semicolons. No reveal colons ("The reason is clear: ..."). Colons in titles, ratios, and times are fine.
- **S7. Tails and "however".** Split ", cutting X..." into ". This cut X...". Rewrite "X, however, Y" as "Yet X Y" or as two sentences.
- **S8. Stock phrasing.** Cut: Furthermore, Moreover, Additionally, Notably, Ultimately, In conclusion, In summary, In short, It is important/crucial to note, pivotal, vital role, integral role, tapestry, delve into, testament, paramount, transformative potential, the landscape of, cornerstone, synergy, holistic, and "To address these challenges, we...". When the phrase carries meaning, keep the meaning in plain words: "the transformative potential of X" becomes "how X could transform...".
- **S9. Conclusions.** Rewrite mandates ("must deploy", "is paramount for", "is vital to", "hinges on") as plain recommendations ("should", "we recommend"). These are recommendations, not findings, so H3's hedging rule doesn't apply to them. Don't turn a stated dependency ("success depends on X") into a recommendation, and don't add a mechanism the source doesn't describe.

## Examples

**Unpacking without a fact sheet.**

Source (23 words):
> When solid-state cells undergo prolonged galvanostatic cycling, microscopic void formation, contact loss, and lithium dendrite propagation inherently jeopardize electrochemical performance and structural integrity.

Rewrite (24 words):
> Under prolonged galvanostatic cycling, solid-state cells form microscopic voids. Contact is lost, and lithium dendrites propagate. These changes threaten electrochemical performance and structural integrity.

All three failure modes and both consequences survive, and no detail was added. "Jeopardize" becomes "threaten", not "damage", so the claim keeps its strength. Cutting "inherently" (filler) keeps the length at 104%.

**Using a fact sheet.**

Source:
> Participants completed a validated anxiety questionnaire.

Fact sheet line:
> - Anxiety measure: GAD-7, given at baseline and at week 8

Rewrite:
> Participants completed the GAD-7, a validated anxiety questionnaire, at baseline and again at week 8.

Without that fact sheet line, keep the source's wording and add to "Details you could add": "Which anxiety questionnaire, and when was it given?"

## Known limits of the checker

- It compares numbers without units. "1.0 MPa" passes if the source has "1.0 mA cm⁻²" somewhere.
- It treats counts as numbers. A true count you add ("two processes") fails if the source never uses that number, and passes by coincidence if the number appears elsewhere. H1 bans added counts either way.
- It tracks only acronym- and formula-shaped terms (two or more capitals, or a capital plus a digit). Invented plain-word names, and invented authors without a year, get through.
- It ignores ordinals ("first", "second") and a lone "one".
- It can't judge claims, purposes, hedging, or whether a list kept all its items. That's the fidelity reread in step 4.
