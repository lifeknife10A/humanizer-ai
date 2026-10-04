---
name: academic-humanizer
description: "Rewrites AI-drafted academic text (papers, theses, reports) into varied, specific prose without the patterns AI detectors key on: uniform sentence length, stock transitions, three-item lists, participial tails, and preachy conclusions. Keeps every number, term, and list item from the source. Added specifics come only from an author-supplied fact sheet, and a bundled checker blocks any invented or dropped number. Includes a detector-feedback phase that rewrites only the sentences ZeroGPT highlighted, for scores under 10%. Use when asked to humanize, de-AI, or rewrite academic text, or when the user returns with highlighted sentences from an AI detector."
metadata:
  version: "7.9.0"
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

# Academic Humanizer (v7.10.0)

Rewrite AI-drafted academic text so it reads like a specific author wrote it, in one run, without changing what it says.

The work happens in four phases. You rewrite the text and reread it against the source (Phase 1). `scripts/check_draft.py` compares your rewrite with the source and fact sheet (Phase 2). You revise what it flags (Phase 3). After the user scans the result, you rewrite only the sentences the detector highlighted (Phase 4), using `flagged_runs.py` and `apply_runs.py`.

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
3. **Rewrite (Phase 1)** paragraph by paragraph, following the hard constraints and then the style rules below. Leave the title unchanged; section headings follow the structured-paper rules below. Save the result as `draft.txt`.

   **Structured papers** (numbered sections, bulleted "Label: description" lists, word-equations): restructure them into prose, unless the user says the format is fixed. On our test paper, a single pass that kept the bullets only got from 96.4% to 69.2%. Nearly every "Label: description" bullet was highlighted, and so were most headings and formula lines, which alone made up about 8 points.
   - **Lists become prose paragraphs.** Every item stays (H4), and each label's concept stays as a phrase in the prose. "- Grid Frequency Instability: Inverter-based plants lack rotational inertia…" becomes "Frequency stability suffers first. Inverter-based plants lack the rotational inertia…". Sub-bullets become sentences in their parent item's paragraph. Vary how the items are introduced (S5); don't open every item with its label.
   - **Section headings are reworded in plain language,** keeping their numbers and meaning. "2. Machine Learning Methodologies for Renewable Generation Forecasting" becomes "2. Forecasting renewable output with machine learning". Keep the paper's title unless the user asks to change it.
   - **Word-equations go into symbolic form,** with the variables defined in the next sentence. "Available Kinetic Power = 0.5 * Air Density * Rotor Area * (Wind Velocity)^3" becomes "P = 0.5 ρ A v^3", followed by "Here ρ is air density, A the rotor area and v the wind velocity." Keep every number and operator; only the names change.
   - **If the user says the format is fixed,** keep the headings, bullets and formula lines, and rewrite only the prose inside the bullets. A bullet's "Label: description" colon is fine then. Tell the user that ZeroGPT still counts those fixed parts, so under 10% is unlikely.
4. **Fidelity reread.** The checker can't see claims or lists, so do this before checking. Put each source paragraph next to its rewrite and confirm:
   - every list item is still there (H4)
   - every claim is still there, and none was added (H3). Check short sentences hardest: if you can't point to the source sentence one comes from ("Pixel perturbations fail here."), delete it
   - each purpose is still a purpose: "implemented to evaluate X" must not become "we compared X"
   - findings are hedged exactly as strongly as in the source
   - no count was added that the source doesn't state ("all three", "two processes")

   Fix `draft.txt` before moving on.
5. **Check (Phase 2).**
   ```bash
   python3 SKILL_DIR/scripts/check_draft.py source.txt draft.txt --facts facts.md
   ```
6. **Revise (Phase 3).** Fix the sentences the report names. Some warnings cover the whole document (`retention`, `short-sentences`, `add-on` without a location); for those, change whichever sentences fix it best. Then run step 5 again. Run at most two revision rounds, each followed by a check.
   - `new-number` FAIL: delete the number, or go back to the source's wording. Never fix it by adding the number to the fact sheet yourself.
   - `missing-number` FAIL: restore the content of the source sentence the report quotes.
   - `new-term` WARN: use the source's wording unless the fact sheet gives the term. To shorten a term the source spells out, define the abbreviation at first use: "electrochemical impedance spectroscopy (EIS)".
   - `retention` FAIL (too short): unpack more sentences, or use more fact-sheet detail. If neither is possible without padding, leave the shortfall and report it.
   - `retention` WARN (too long): cut filler (see H5), define abbreviations for long repeated terms, and merge fragments you over-split. If the extra length comes from fact-sheet detail (the draft minus the words those details added is within 110%), leave it and report it so the author can decide against any word limit.
   - `staccato` WARN: too many short sentences, or an average under 8 words. Merge runs of short sentences into fuller ones of 8–16 words. A list of items can share one sentence ("Solar irradiance, temperature and cloud cover all vary, and so does wind speed.").
   - `short-sentences` WARN: lead with a claim's core in 3–5 words and move its details to the next sentence (see S2). If no claim is left that splits naturally, stop and report the share; never split off a modifier to reach the number.
   - `add-on` WARN: work the item in another way (see S5) instead of tacking it on with "too", "as well", or "also".
   - `restatement` WARN: the short sentence only repeats its neighbours ("Robustness requires fundamental advances." right after "achieving robust LLMs will require fundamental advances"). Delete it; never pad to reach the short-sentence share.
   - `parallel` WARN: three sentences in a row open the same way ("Syntactic attacks manipulate… Semantic attacks exploit… Jailbreak attacks circumvent…"). Change the shape of at least one (S5).
   - `hedge` WARN: the quoted source sentence has a hedge ("may", "often", "suggesting") your draft lost. Put it back in the matching draft sentence.
   - `modal` WARN: use the source's modal; "should" stays "should", never "must".
   - `possible-drop` WARN: most words of the quoted source sentence are gone from the draft. Find where its content went; if it was dropped, restore it.
   - Other style WARNs: fix each one unless the fix would break a hard constraint.

   You may also fix any other error you notice (grammar, a broken reference). Rerun the fidelity reread (step 4) on every sentence you changed.
7. **Deliver:**
   - the final text in one copy-pasteable block
   - the final checker report
   - the fact-sheet details you used
   - anything left unresolved, with the reason (for example, a retention shortfall or a conflict between the source and the fact sheet)
   - **Details you could add**: vague spots in the source where the author's real specifics would help, written as questions. Example: "Spark plasma sintering: what temperature, pressure, and hold time?" Ask these; never answer them yourself.
   - an offer to run Phase 4: scan the text, then send back the highlighted sentences

Never deliver with a `new-number` or `missing-number` failure. Both can always be fixed by deleting an added number or restoring a dropped one.

If you can't run Python, do steps 2 and 5 by hand. List every number, acronym, and formula in the source and fact sheet, then compare your draft against that list sentence by sentence.

## Phase 4: Detector feedback (for scores under 10%)

A single pass (steps 1–7) lands around 27–35% on ZeroGPT in our tests. Nothing you can compute locally predicts which sentences ZeroGPT will flag. Perplexity, token rank, Binoculars-style scores and style features all came out at or near chance on 600 labelled sentences (`research/ZEROGPT_LABEL_STUDY.md`). So going under 10% needs the detector's own feedback. On our test abstract, two feedback rounds took the score from 27.2% to 13.9% to 5.3%, with every fact intact.

What the data showed, and what this procedure relies on:
- **The score is roughly the highlighted share.** ZeroGPT's percentage is close to the share of words in highlighted sentences, so each round's target can be counted.
- **Highlights come in runs.** A sentence right after a highlighted one is highlighted about two thirds of the time, against about one in ten otherwise. The detector judges sentences in context, so a run is rewritten as one unit.
- **Unhighlighted sentences must stay word for word.** They already passed, and rewriting them risks new highlights.
- **Neighbours can still flip.** A kept sentence may become highlighted after the run next to it changes. It then belongs to the next round's runs.
- **The opening framing is the hardest part.** The first few sentences of an abstract were highlighted in every round. The title is always highlighted; titles stay unchanged, and it usually costs one or two points.

Offer this phase at delivery. Run it when the user comes back with a scan. **Never retype the whole document in this phase.** Write only the rewrites, and let `apply_runs.py` splice them in.

1. **Save the scan.** Save the exact text the user scanned as `draft.txt` (the previous round's output). Put the highlighted sentences in `flagged.txt`, one per line; each line can be just the sentence's opening words. If the user sends screenshots, transcribe the opening words of every highlighted sentence.
2. **Make the runs file.**
   ```bash
   python3 SKILL_DIR/scripts/flagged_runs.py draft.txt flagged.txt --emit runs.txt
   ```
   It prints the estimated score and writes `runs.txt`, with one block per run: the run's ORIGINAL text, its context sentences, and an empty REWRITE slot. If it lists flagged lines that matched no sentence, fix those lines in `flagged.txt` and run it again.
3. **Write the rewrites into `runs.txt`.** Fill in **every** REWRITE slot and leave ORIGINAL and CONTEXT lines untouched. A run left unrewritten stays highlighted, so the score can't fall below its share. On a long paper, 25–30 runs are normal. Work through them in order, about five at a time, and run step 4 after each batch to catch problems early. The result stays REVISE until every slot is filled. Never empty a slot to get past a warning; fix the warning. Only a run made entirely of headings or formula lines may be kept on purpose, by writing KEEP in its slot, and only when the paper's format is fixed. Each rewrite replaces the whole run, so it must carry every claim, number, hedge and list item of that run's ORIGINAL (H1–H5 still apply). How to rewrite a run, in the style that won on our test:
   - **Write in the authors' voice, around what was done:** "We put the adversarial robustness of contemporary LLMs to an empirical test" rather than "This paper presents an empirical investigation into…".
   - **Restructure, don't polish.** Change grammatical subjects, reorder the run's claims, and split or merge sentences inside the run. Swapping synonyms into the same sentence shape doesn't clear a run. On the smart-grid paper, Gemini rewrote runs sentence for sentence with synonyms, and every rewritten sentence of 10 or more words was highlighted again. Only its short sentences cleared. Changing the words isn't enough; change the sentences.
   - **Keep sentences at 16 words or fewer, and mix in short ones.** Longer connected sentences scored worse (19.5% against 13.9%).
   - **Prefer plain verbs and concrete phrasing to abstract nouns:** "Multi-turn exploitation plays a longer game. Its adversarial effects pile up across the conversation history."
   - **Leading with the point also works:** "Getting past safety mechanisms is the aim of jailbreaks." It scored the same as the authors' voice in round 3.
   - **Read the CONTEXT lines** so the rewrite still connects to the sentences around it.
   - **Headings and formula lines can be runs too.** A highlighted section heading is reworded again, keeping its number and meaning ("2. Forecasting renewable output…"). A highlighted word-equation is rewritten in symbolic form with its variables defined in a following sentence, keeping every number and operator. The paper's title never appears in a run and stays unchanged.
   - **Bullets:** if the user kept the paper's bullets, start each rewritten bullet on its own line with the same marker ("- "); `apply_runs.py` keeps those line breaks. A highlighted formula line may be rewritten in symbolic form (see the structured-paper rules), keeping every number and operator.
   - **Add nothing,** not even a harmless-looking modifier ("tested with care", "improves robustness markedly"). Every word of a rewrite must trace to the run's ORIGINAL or the source.
   - **Keep what each sentence does.** An aim stays an aim: "focusing on identifying vulnerability patterns" never becomes "These models showed vulnerability patterns." What the authors introduce stays introduced: "We introduce a novel framework that sorts attacks into four dimensions" never becomes "Four attack dimensions emerged." 
4. **Splice and check.**
   ```bash
   python3 SKILL_DIR/scripts/apply_runs.py draft.txt runs.txt -o draft_next.txt --source source.txt --facts facts.md
   ```
   Drop `--facts facts.md` when there's no fact sheet. It replaces only the runs, copies everything else unchanged, and checks the result against the original source, never the previous draft. Its PHASE 4 REVIEW sorts the findings for you:
   - **Runs still without a rewrite:** fill those REWRITE slots. This blocks READY TO SCAN.
   - **Highlighted sentences barely changed:** your rewrite kept 80% or more of the sentence's words. Restructure it. In rounds that lowered the score, rewrites kept about half of each highlighted sentence's words and never more than 79%; near-copies get flagged again.
   - **Hedges or limiting words lost in your rewrites:** you dropped a "may", "often", "suggests", "some", "strongly" or "only", or added a "must". Restore it. "Some larger models fare worse" is not "Larger models fare worse."
   - **Enumerations broken by your rewrites:** a sentence outside the run still says "Third, …" but your rewrite removed "First" or "Second". Keep the ordinal in the rewrite.
   - **Word stems a run's rewrite no longer has:** not blocking, but read the list. Synonyms are fine; a missing item, claim or qualifier is not.
   - **Warnings inside your rewrites:** fix every one in `runs.txt`. These are problems you introduced.
   - **Whole-document findings:** fix any failure, and check each hedge or drop warning.
   - **Warnings in sentences outside the runs:** ignore them. Those sentences already passed the detector.

   Once every slot is filled, run it again until it says READY TO SCAN, for at most three more tries. If it says a run's ORIGINAL wasn't found, the runs file was edited outside a REWRITE slot; regenerate it in step 2.
5. **Optional second variant.** If the user is willing to scan twice, copy `runs.txt` to `runs_b.txt`, fill it with a different rewrite of the same runs, and splice it to `draft_next_b.txt`. Continue with whichever scans lower.
6. **Deliver** `draft_next.txt` (and the variant, if any), the checker report, and the estimated score. Ask for the next scan.
7. **Stop** when the score is under 10%, after four feedback rounds, or when a round with every run rewritten doesn't lower the score. A round that left runs unrewritten doesn't count; finish those runs and rescan. Report the score history, round by round. Each round has roughly halved the score in our tests, so a text starting near 30% needs two rounds and one starting near 65% needs about four.

## Hard constraints

These are never traded for style.

- **H1. Numbers.** Every number in the draft comes from the source or the fact sheet. Every number in the source appears in the draft, as digits or words. Counts are numbers too: don't write "two processes" or "all three" unless the source states that count, because the checker can't tell a true count from an invented one. "Both" and ordinals ("the first", "the second") are fine when they refer to items the source lists. Don't turn a number into a multiple ("rose by 312%" is not "tripled"). Write ordinals as words ("the first dimension", never "the 1st dimension") and keep the source's choice of words or digits ("four dimensions" stays "four", not "4").
- **H2. Names and terms.** Add no materials, formulas, techniques, instruments, datasets, acronyms, authors, institutions, or citations that aren't in the source or fact sheet. Don't make a generic name more specific. "Lithium lanthanum zirconium tantalum oxide" doesn't become a stoichiometric formula unless the fact sheet gives that formula. Defining a standard abbreviation for a term the source spells out is fine: "lithium lanthanum zirconium tantalum oxide (LLZTO)". So is the standard symbol for a unit the source names ("megapascals" becomes "MPa").
- **H3. Claims.** Add no results, mechanisms, causes, comparisons, or first-person experimental actions that the source or fact sheet doesn't state. "In our load frames, pellets cracked above 6.5 MPa" is an invented experiment if the source never mentions it. Keep purposes as purposes. Keep findings hedged exactly as strongly as the source: "may suggest" stays tentative, "confirmed" stays confirmed. You may turn the source's passive voice into "we" for work it presents as the authors' own. If the fact sheet contradicts the source or describes the same thing differently ("synthesized" vs. "densified"), follow the fact sheet (the author wrote it) and report the difference.
- **H4. Lists.** Keep every item of every list. Restructure a list; never shorten it.
- **H5. Length.** The draft is 95–110% of the source's word count. Unpacking adds words (repeated subjects, new sentence openings), so offset it by cutting filler. Filler is wording that carries no fact, claim, item, or hedge, such as "fundamentally", "inherently", "notoriously", "comprehensive", "successfully", "it is the case that". Keep intensifiers that state size ("dramatically", "exponentially") and "significantly" when it means statistical significance. Cutting filler is not truncation. Never pad with field background, restatement, or invented specifics. An honest shortfall is better than padding. Use the fact-sheet details that make the source's statements specific; you don't have to use all of them. When a fact-sheet value makes a vague word redundant ("high-temperature" next to 1150 °C, "ultra-thin" next to 5 nm), drop the vague word. Fact-sheet detail may still take the draft above 110%; report it rather than cutting details you used.

The checker enforces H1 and the length floor in H5, and flags likely H2 violations. For H3 and H4 it flags lost hedges, a stronger "must", and source sentences that seem to have been dropped, but it can't see an invented claim. That depends on your fidelity reread (step 4).

## Style rules

Apply these within the hard constraints. When a style rule and a hard constraint conflict, the hard constraint wins.

- **S1. Sentence length.** Keep sentences to 16 words or fewer. Unpack longer ones into complete sentences that keep every clause.
- **S2. Short sentences.** Aim for about one sentence in five with 5 words or fewer, placed irregularly. The checker warns below 15% and above 30%, and when the average sentence drops under 8 words. Choppy text fails just as surely as long-winded text: "Solar irradiance fluctuates. Ambient temperature varies. Cloud cover changes." reads as machine-made. Most sentences should be 8–16 words. The natural way to get one is to lead with a claim's core and give its details in the next sentence: "Interfacial impedance escalated rapidly. Over the first fifty cycles at 1.0 mA cm⁻², area-specific resistance rose by 312%." Each short sentence needs its own subject and a verb that states something the source claims. Never make one by:
  - splitting off a modifier ("Protocols should be standardized. These should be rigorous.", "Demand surged. It grew exponentially.")
  - adding a generic slogan ("The math reflects physics.")
  - reusing a short sentence or its wording frame ("Peak currents compound damage." then "Mechanical loads compound stress.")

  If the text runs out of claims that split naturally, stop below the target and report the share. A short sentence that states something the source doesn't is an H3 violation, not a style choice.
- **S3. Sentence openings.** Don't start three sentences in a row with the same word. Front some sentences with a prepositional or adverbial phrase drawn from the content ("At 1.0 mA cm⁻², ...", "During stripping, ...").
- **S4. Paragraph openings.** Start each paragraph with the paper's specific problem or finding (in a methods paragraph, with what was done or why). Background sentences that are in the source are content, so keep them, but move them out of the paragraph's first sentence.
- **S5. Three-item lists.** Break the "A, B, and C" rhythm without dropping an item. Vary the method across the document:
  - Give one item the main clause and the others a phrase ("Microscopic voids form during cycling, accompanied by contact loss and dendrite growth."). Don't imply an order or a cause the source doesn't state.
  - Announce and walk through ("Three strategies were tested. The first deposited..."), only when the source states the count (H1).
  - Give two items one sentence and the third its own sentence with its own verb and angle.

  Splitting a list into one sentence per item is not enough if every sentence has the same shape ("Syntactic attacks manipulate… Semantic attacks exploit… Jailbreak attacks circumvent…"). Give at least one item a different structure: a fronted phrase, a relative clause, or a different subject.

  Never end the split-off item with "too", "as well", or "alongside them", and don't lean on "also". Swapping in "along with", "together with", or "alongside" everywhere just moves the pattern. The checker warns when more than two sentences end with an add-on or when these connectors are overused.
- **S6. Punctuation.** No semicolons. No reveal colons ("The reason is clear: ..."). No em-dash asides ("robustness—specifically, ..."); make the aside its own sentence or part of the main clause. Colons in titles, ratios, and times are fine.
- **S6a. Numbered lists.** Turn inline enumerations ("(1) ..., (2) ..., (3) ...") into prose that keeps every item (H4), using the S5 methods. The markers themselves aren't facts, so the checker doesn't require them.
- **S7. Tails and "however".** Split ", cutting X..." into ". This cut X...". Rewrite "X, however, Y" as "Yet X Y" or as two sentences.
- **S8. Stock phrasing.** Cut: Furthermore, Moreover, Additionally, Notably, Ultimately, In conclusion, In summary, In short, It is important/crucial to note, pivotal, vital role, integral role, tapestry, delve into, testament, paramount, transformative potential, the landscape of, cornerstone, synergy, holistic, and "To address these challenges, we...". When the phrase carries meaning, keep the meaning in plain words: "the transformative potential of X" becomes "how X could transform...".
- **S9. Conclusions.** Rewrite mandates ("must deploy", "is paramount for", "is vital to", "hinges on") as plain recommendations ("should", "we recommend"). These are recommendations, not findings, so H3's hedging rule doesn't apply to them. Don't turn a stated dependency ("success depends on X") into a recommendation, and don't add a mechanism the source doesn't describe.
- **S10. Authors' voice.** Where the source describes the authors' own work, prefer what they did over abstract nouns ("We sorted the attacks into four groups" over "The framework categorizes attacks into four dimensions"). This is the style that cleared the most highlighted runs in Phase 4.

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
- Its three-item-list check needs an Oxford comma ("A, B, and C"), and its add-on check misses connectors like "as do" and "so do". S5 still applies to both.
- It counts hedges by kind and flags source sentences whose words mostly vanished. It can't see an invented claim ("Pixel perturbations fail here."), a hedge moved onto a different claim, a purpose turned into a result, or a list that lost one item. That's the fidelity reread in step 4.
