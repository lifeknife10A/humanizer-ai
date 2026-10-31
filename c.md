# Wikipedia:Signs of AI writing — raw research paste (absorbed 2026, source: Wikipedia advice page WP:AISIGNS, WikiProject AI Cleanup, last edited 31 Oct 2026)

From Wikipedia, the free encyclopedia. This is an advice page from WikiProject AI Cleanup. This page is not an encyclopedia article or a Wikipedia policy. Shortcuts: WP:AISIGNS, WP:AITELLS, WP:LLMSIGNS.

This is a list of writing and formatting conventions typical of AI chatbots such as ChatGPT, with real examples taken from Wikipedia articles, drafts, comments, and other content. It is a field guide to help detect undisclosed AI-generated content on Wikipedia: while some of the signs may be broadly applicable, some may not apply in a non-Wikipedia context. Not all text featuring these indicators is AI-generated, as the large language models that power AI chatbots are trained on human writing, including Wikipedia. Many elements of AI writing can be found in editorials, blogs, or fan fiction.

Moreover, this list is descriptive, not prescriptive; it consists of observations, not rules. The patterns listed here are also only potential signs of a problem, not the problem itself. While many of these issues are immediately obvious and easy to fix—e.g., excessive boldface, broken markup, citation style quirks—they can point to less outwardly visible problems that carry much more serious policy risks. Please do not merely treat these signs as the problems to be fixed; that could just make detection harder.

The speedy deletion policy criterion G15 (Unambiguously LLM-generated pages) lists some signs of AI writing, but is limited to the most objective ones. The remaining signs covered here are not sufficient on their own for speedy deletion.

As of October 2026, the most common signs of newly AI-generated text on Wikipedia (besides the unambiguous indicators above) are Markdown presence, AI edit summaries, hedging disclaimers about source availability and usage, vague expression of connection or association, and canned emphasis on source attribution and media coverage.

## Caveats

### AI detection tools (WP:AIDETECTION)

Do not solely rely on artificial intelligence content detection tools (such as GPTZero and Pangram). While they perform better than random chance, these tools have non-trivial error rates.[1][2] Detectors can be susceptible to factors such as text modifications (e.g. paraphrasing, markup, and spacing changes) and the use of models not seen during detector training.[3] A high percentage of detected AI writing from the results of a detection tool is not a valid criterion for speedy deletion under G15.

### Your detection ability (WP:AIDETECTIVE)

Do not rely too much on your own judgment. Humans are notoriously bad at distinguishing human and LLM-generated text. While research on humans' abilities to detect AI-generated text is still limited, a 2025 study has shown that human ability to distinguish LLM text from human is no better than random chance.[4] Another 2025 study on German theses has shown that humans managed a "recognition rate of 57 % for AI texts and 64 % for human-generated texts".[5]

In a 2025 preprint, a subset of 'expert' annotators correctly identified 90% of AI-generated text (and misidentified 3.3% of human-written text) as AI-generated. Study participants who didn't use LLMs much did only slightly better than random chance (in both directions).[1]

Note, also, that human speech and writing is being influenced by LLMs, and thus they are becoming more similar. This was already evident in 2024, as shown by a study that detected a significant LLM influence in spoken content (e.g. conversational podcasts).[6] Further studies seem to confirm this influence on language,[7] including semantics and word choices.[8] However, this is a lagging and patchwork process, and the reverse is not true: LLM output is not becoming more similar to that of human writing.[9]

## Content (WP:AIWTW / WP:LLMISM)

LLMs (and artificial neural networks in general) use statistical algorithms to guess (infer) what should come next based on a large corpus of training material. It thus tends to regress to the mean; that is, the result tends toward the most statistically likely result that applies to the widest variety of cases. Most LLM-based tools then undergo another round of adjustment, called reinforcement learning from human feedback, to tailor its output toward the most broadly palatable prose. This can simultaneously be a strength and a "tell" for detecting AI-generated content.

For example, LLMs are usually trained on data from the internet in which famous people are generally described with positive, important-sounding language. Consequently, the LLM tends to omit specific, unusual, nuanced facts (which are statistically rare) and replace them with more generic, positive descriptions (which are statistically common). Thus the highly specific "inventor of the first train-coupling device" might become "a revolutionary titan of industry". It is like shouting louder and louder that a portrait shows a uniquely important person, while the portrait itself is fading from a sharp photograph into a blurry, generic sketch. The subject becomes simultaneously less specific and more exaggerated.

This statistical regression to the mean, a smoothing over of specific facts into generic statements, that could equally apply to many topics, makes AI-generated content easier to detect.

### Undue emphasis on significance, legacy, and broader trends (WP:AILEGACY / WP:AITREND)

Words to watch: stands/serves as, is a testament/reminder, a crucial/pivotal/vital/significant/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted, distinction [matters/is important] because...

LLM writing often puffs up the importance of the subject matter by adding statements about how arbitrary aspects of the topic represent or contribute to a broader topic. There is a distinct and easily identifiable repertoire of ways that it writes these statements. Another common manifestation is AI chatbots situating an article subject amid broader "debates," or noting that a subject has "participated in public discussions". LLMs may even include these statements for the most mundane of subjects like etymology or population data. Sometimes they add hedging preambles acknowledging that the subject is of relatively low importance, before talking about its importance anyway. When talking about biology, LLMs tend to over-emphasize connections to the broader ecosystem or environment, and belabor conservation status and research efforts, even if unknown. As of mid-2026, LLMs frequently include these alongside hedging disclaimers, editorializing about how a particular distinction or nuance is important.

### Canned emphasis on notability, attribution, and media coverage (WP:OVERATTRIBUTION / WP:AIATTR)

Words to watch: independent coverage, local/regional/national/[country name] media outlets, music/business/tech outlets, trade publications, cited/featured/profiled in, written by a leading expert, active social media presence, was identified by

LLMs act as if the best way to prove that a subject is notable is to hit readers over the head with claims of notability, often by detailing sources that a subject has been covered in and specifying what kind of sources they are. They often inaccurately attribute their own superficial analyses to the source. More common in text from AI tools released in 2025 or later. The result often echoes the exact wording of Wikipedia's guidelines like "independent coverage," as if the LLM has collapsed the context between the edit and its justification. LLMs will often note that subjects "maintain an active social media presence" — wording idiosyncratic to AI text and relatively uncommon on Wikipedia before ~2024.

### Superficial analyses (WP:SUPERFICIAL)

Words to watch: highlighting/underscoring/emphasizing ..., ensuring ..., reflecting/symbolizing ..., contributing to ..., cultivating/fostering ..., encompassing ..., enhancing ..., valuable insights, align/resonate with,

AI chatbots tend to insert superficial analysis of information, often in relation to its significance, recognition, or impact. This is often done by attaching a present participle ("-ing") phrase at the end of sentences, sometimes with vague attributions to third parties. For the purpose of Wikipedia, such comments are usually synthesis or unattributed opinions. Newer chatbots with retrieval-augmented generation may attach these statements to named sources regardless of whether those sources say anything close.

### Promotional and advertisement-like language (WP:AIPUFFERY / WP:AIPEACOCK)

Words to watch: boasts a, vibrant, rich, profound, enhancing, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking, renowned, featuring, diverse array

LLMs have serious problems keeping a neutral tone. Even when prompted to use an encyclopedic style, their output will often tend toward advertisement-like writing, or like the prose of a travel guide. LLMs tend to over-use the same set of promotional phrases no matter what the topic. Older LLMs (e.g., GPT-4) tend to output more blatantly positive text than newer LLMs, which are more subtly positive. When writing about "cultural heritage," LLMs constantly remind the reader of its importance; when writing about people or companies, they adopt a press-release tone.

### Vague expression of connection or association (WP:AICONNECT / WP:AIASSOCIATION)

Words to watch: in connection with/to ..., connected with/to, in association with ..., associated with

Rather than directly stating a connection or relationship between two subjects, LLMs will often allude vaguely to the two subjects being "connected to" or "associated with" each other. Often combined with promotional buzzspeak, e.g. particularly/widely associated.

### Vague attributions and overgeneralization of opinions (WP:AIWEASEL)

Words to watch: Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when only few sources are cited), such as (before exhaustive word lists)

AI chatbots tend to attribute opinions or claims to some vague authority — a practice called weasel wording. They commonly exaggerate the quantity of sources, present views from one or two sources as widely held, mention multiple "reviewers" or "scholars" while citing one person, or imply lists of examples are non-exhaustive when sources give no indication of that.

### Outline-like conclusions about challenges and future prospects (WP:FACESCHALLENGES)

Words to watch: Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

Many LLM-generated Wikipedia articles include a "Challenges" section, typically beginning "Despite its [positive words], [subject] faces challenges..." and ending with a vaguely positive assessment or speculation about future initiatives. Such paragraphs appear at the end of articles with a rigid outline structure, possibly including a separate "Future Prospects" section. This sign is about the rigid formula, not simply the mention of challenges.

### "Awards and recognition" section

Section or subsection headers in the format of "X and Y" are common in AI generated articles. An "Awards and recognition" section is particularly common — a manifestation of AI text's focus on legacy and its tendency to vaguely allude to "coverage" or "recognition". The specific wording is nearly ubiquitous in AI generated articles, and much more common than in human writing even compared against articles tagged as promotional.

## Language and grammar

AI-generated text displays consistent patterns in syntax, word choice, and sentence construction that human writing does not display to nearly the same degree. Conversely, it often struggles to match some syntactic and linguistic patterns characteristic of human writing. Some LLMs deviate more from human writing than others; for example, GPT-4o produces output with more variation from human writing than other contemporaneous language models. Since these are linguistic patterns, they occur consistently regardless of the subject matter, which often gives AI-generated text an identifiable "voice".

### High density of "AI vocabulary" words (WP:AIVOCAB / WP:AIWORDS)

Words to watch: Additionally (especially beginning a sentence), align with, boasts (meaning "has"), bolstered, crucial, deep dive, delve, emphasizing, enduring, enhance, fostering, garner, highlight (as a verb), interplay, intricate/intricacies, landscape (as an abstract noun), meticulous/meticulously, pivotal, robust, showcase, tapestry (as an abstract noun), testament, underscore (as a verb), valuable, vibrant

Many studies have demonstrated that LLMs overuse specific words. These words started appearing far more frequently in text produced after 2022. They often co-occur in LLM output: where there is one, there are likely others. One or two of these words appearing in an edit may be coincidental, but an edit (post-2022) introducing lots of them, lots of times, is one of the strongest tells for AI use.

The words that LLMs overuse have changed over time ("delve" was famously overused 2023–early 2024, dropped off sharply in 2025). Rough era breakdown:

- 2023 to mid-2024 (GPT-4): Additionally, boasts, bolstered, crucial, delve, emphasizing, enduring, garner, intricate/intricacies, interplay, key, landscape, meticulously, pivotal, underscore, tapestry, testament, valuable, vibrant
- Mid-2024 to mid-2025 (GPT-4o): align with, bolstered, crucial, emphasizing, enhance, enduring, fostering, highlighting, pivotal, showcasing, underscore, vibrant
- Mid-2025 to mid-2026 (GPT-5): emphasizing, enhance, highlighting, showcasing (plus canned emphasis on notability/attribution/media coverage)
- Mid-2026 and on (GPT-6): challenge, clearer, dependable, echoed, foster, leverage, matters, multifaceted, practical, prioritize, quietly, steady, universally (with much more period and comma usage and shorter sentences around a strict 8–20 word limit)

The distribution differs by chatbot: Grok overuses superficially "scientific" words like causal, empirical, correlate, and continued to overuse underscore as of 2026.

A word being overused by AI does not imply that its synonyms are also overused.

### Avoidance of basic copulatives ("is"/"are" phrases) (WP:AINOCOPULA / WP:AIREPRESENTS)

Words to watch: serves as/stands as/marks/functions as/operates as/represents [a], boasts/features/maintains/offers [a], refers to

LLM-generated text often replaces simple constructions that use copulas such as is or are with constructions such as serves as a or mark the, observed in GPT and Gemini models. One study documented an over 10% decrease in the usage of the words is and are in academic writing in 2023. LLMs prefer marketing-related verbs like features, offers to their neutral synonym has. In lead sentences, LLMs sometimes avoid is by writing refers to as though the article were about the word instead of the subject.

Example diff: "Gallery 825 ... is LAAA's exhibition arm" → "Gallery 825 ... serves as LAAA's exhibition space ... The gallery features four separate spaces" (August 2023, Los Angeles Art Association).

### Negative parallelisms (WP:AIPARALLEL)

When LLMs describe a subject, their output may seem as though it is clearing up a common misconception, retroactively challenging such thinking by pointing out another characteristic. Common among human writers ("myths busted" listicles) but stereotypically an AI sign.

- Not just X, but also Y: "Not only ... but ..." or "It is not just ..., it's ..."
- Not X, but Y: "It's not ..., it's ..." or "no ..., no ..., just ..."
- Y rather than X: reversed construction, particularly common in recent LLM output.

### Leads treating lists or broad article titles as proper nouns

In AI-generated articles about topics whose title is not a proper name, the first sentence may introduce or define the article's title as if it were a standalone real-world entity.

### Rule of three (WP:RO3)

LLMs overuse the rule of three, from "adjective, adjective, adjective" to "short phrase, short phrase, and short phrase". LLMs often use this structure to make superficial analyses appear more comprehensive. The sign is stronger in contexts where most people would not bother with such flourishes, like edit summaries.

## Style

AI-generated text tends to exhibit stylistic features not expected as often in human-made articles: title case instead of sentence case in section titles; overuse of boldface, sometimes misusing asterisks; inline-header vertical lists; incorrect heading levels; emoji at the beginning of section titles or list entries; curly quotation marks and apostrophes instead of straight ones.

## Communication intended for the user (WP:CERTAINLY / WP:COLLABCOMM)

Words to watch: a Wikipedia-style article, I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., is there anything else, let me know, more detailed breakdown, here is a ..., [check/verify/confirm]... before [publishing/publication/submitting]

Editors sometimes paste text from an AI chatbot that was meant as correspondence, prewriting or advice, rather than article content. This may appear in article text or within comments (<!-- -->).

### Hedging disclaimers about source availability and recommended usage (WP:AIDISCLAIMER)

Words to watch: While specific details are limited/scarce..., not widely available/documented/disclosed, ...in the provided/available sources / search results..., [claim] should be [treated/presented] as... rather than..., based on available information, ...does not by itself establish...

Chatbots will often attempt to fill perceived gaps by drawing attention to the fact that there are gaps, or otherwise include cautionary disclaimers.

- 2023-24 (WP:DIDACTIC): Older LLMs added didactic disclaimers about topics being "important to note", often advice to an imagined reader about safety or controversial topics. Several appear in OpenAI's GPT-4 system card as "partial refusals".
- 2024-25: Chatbots with retrieval-augmented generation that fail to find sources often output statements claiming information is not publicly available, paired with speculation about what it "likely" may be. For individuals: "maintains a low profile", "keeps personal details private".
- Mid-2026-present: disclaimers about how sources should be used, "corrective framings": (1) negative parallelism with "rather than" warning a claim should be treated as [speculative/symbolic] rather than [definitive/verified]; (2) cautioning that available information does not establish [some firm conclusion]; (3) disambiguating a topic by stating it "should not be confused" with another. This pattern is extremely uncommon before mid-2026 (roughly the July release of GPT-5.6).

### Phrasal templates and placeholder text (WP:AIPLACEHOLDER)

AI chatbots may generate fill-in-the-blank phrasal templates (Mad Libs style) for the user to replace; some users forget to fill in the blanks. Also date placeholders like "2026-xx-xx" in citation access-date fields; historically URL placeholders like INSERT_SOURCE_URL_## or example.com links (though example.com may be an ineffective indicator in isolation as templates use it).

## Markup irregularities

AI chatbots prompted to write content for Wikipedia tend to make errors that wouldn't be expected in human-written text: using Markdown (asterisks for bold, number signs for headings, --- or ---- as dividers, [url](text) links, and most unambiguous of all wrapping text in triple backticks, often prefaced with "wikitext"); failing to convert citations and exposing internal data structures (e.g. ChatGPT's contentReference[oaicite:1]); placing articles in nonexistent categories; transcluding nonexistent templates.

## Citations (WP:AIFICTREF)

- Broken external links: multiple dead citations not found in archiving sites are a strong sign of an AI-generated page.
- Invalid DOI and ISBNs: unresolvable DOIs and checksum-invalid ISBNs indicate hallucinated references.
- DOIs that lead to unrelated articles: LLMs generate references to non-existent articles with real-looking DOIs assigned to unrelated works. Example given: two fabricated Proceedings of the IEEE citations about Ohm's Law; C. L. Fortescue had been dead 30+ years at the purported time of writing.
- Book citations without page numbers or URLs: citations that cannot verify the claims; or page numbers that exist but don't verify (e.g. searching an online copy of Goldwater's The Conscience of a Conservative for "Burke" produces no results).
- Incorrect reference use: wrong re-use syntax, irrelevant sources (a PubMed PMID 3 about carbonic anhydrase cited in an article on cognitive orthotics), the character ↩ around footnotes (a web UI artifact), utm_source=chatgpt.com / utm_source=openai / utm_source=copilot.com / referrer=grok.com in URLs (near-definitive proof the tool found the source, though not necessarily that it wrote the text), named references declared but unused (list-defined reference cite errors).

## Comment-specific indicators (WP:AICOMMENT)

Editors who use LLMs to write comments also tend to: misquote policies and cite made-up shortcuts; transclude maintenance banners when mentioning them; post lengthy comments divided into titled sections; downplay their LLM use; request input from critics on what to improve; dismiss concerns as unsubstantiated speculation; urge critics to focus on improving content instead of provenance. Many LLM-generated comments sound like a clerk or customer-service representative: "carefully reviewed", apologizing for inconvenience they "may have" caused, "If there are specific issues that need to be resolved, please point them out...".

## Edit summaries (WP:AISUMMARY / WP:AISUMM)

AI edit summaries follow rigid templates uncommon to nonexistent before 2023. The more a summary deviates from the pattern, the less likely it is AI. Common abbreviations like "ce" suggest human. Older AI summaries: first-person, AI vocabulary, emoji, markdown. Newer ones: exhaustively procedural about the editing process and compliance with guidelines.

- Canned assurance of adherence to policies and guidelines. Words to watch: ensured that... adheres to, refined, enhanced, enriched, streamlined, improved, in compliance/complies with, Wikipedia [guidelines/style/standards], revised, verifiability, neutrality, neutral tone, encyclopedic tone, clarity, flow. Human editors link a specific rule briefly ("removed excessive links per MOS:OVERLINK"); AI equivalents are verbose yet less specific. Stacked assurances strengthen the sign.
- Specific mentions of "preserved" or "retained" information and "avoided" mistakes — procedural statements about what was NOT changed, expected from an AI prompted to "accomplish X and Y but preserve Z".
- Overemphasis on presence/reliability of citations: added sourced/verified [content], improved attribution, with [independent/secondary/third-party/peer-reviewed] sources. Human editors focus on the content itself ("Added info about the artist's debut").
- Overemphasis on parameter/template names and markup idiosyncrasies: itemizing infobox parameters, brackets, equals signs; specifying "inline citations", "internal links".
- Reference to AfC review: stating that edits address reviewer feedback — too obvious for a human to state.

## Miscellaneous

- Pronounced shift in writing style: unexpectedly flawless grammar vs an editor's other communication, especially if the other writing predates November 2022. Subtler: a multi-year AI user's edits drift in parallel with contemporaneous LLM output (2023 edits read like 2023 LLMs, 2025 like 2025). Reverse also applies: consistent style across pre-2022 and current edits suggests human.
- "Submission statements" in AfC drafts: reviewer notes explaining why the subject is notable — instantly tells reviewers the draft is LLM-generated.
- Pre-placed maintenance templates: drafts that include an AfC template already set to "declined", or implausible pre-applied maintenance/protection templates.
- Canned user pages (WP:AIUSERPAGE): rigid format with inline-header lists and headings like Welcome To My User Page!, About Me, My Interests, Let's Connect!, emoji and Markdown bold attempts.
- Permissions gaming: many benign-looking unconstructive edits to raise user access level; post-2023 gamers often use throwaway AI rewrites across dozens of unrelated articles, leaving a swath of unreviewed AI content. One-directional sign only.

## Differences between LLMs

Each model/version has a distinctive idiolect; what is typical for GPT-5 is not necessarily characteristic of GPT-4 or Gemini. Focusing on broader context is more characteristic of ChatGPT and Grok than Gemini and Claude; Gemini and Claude responses tend to be more concise. ChatGPT is historically the most widely used chatbot for Wikipedia edits.

## Biases in content

Pro-authoritarian bias: even large American frontier models have (as of 2026) a pro-authoritarian bias for some prompts, partly from training on the whole internet including state-media propaganda; model makers also cite user safety in authoritarian countries. Chinese-language responses are more authoritarian than English ones. Models criticize governments in freer countries more than repressive regimes.

## Signs of human writing (WP:HUMANSIGNS)

- Age of text relative to ChatGPT launch (November 30, 2022): earlier text is safely human. Tools: Who Wrote That?, WikiBlame.
- Ability to explain one's own editorial choices: an editor who can explain a mistake (supply the correct link, share the real passage) points to ordinary human error.
- Syntax: LLMs default to "formal, neutral, encyclopedic tone" and avoid constructions common in human writing. Empirically more common in human Wikipedia writing over 25 years:
  - Simple is/has phrases, such as there is a, it has a.
  - Words with complex, stiff or euphemistic synonyms: wrote (vs authored), moved (vs relocated), used (vs utilized), tried (vs attempted), died (vs passed away).
  - Superlative or definitive statements: one of the best, is the only, was the first.
  - Qualifiers and intensifiers: very, perhaps, tends to.
  - Isolated wordy constructions: as a result of, in order to, all of the, a part of, or the fact that.

## Ineffective indicators

False accusations drive away new editors. Consider Dunning–Kruger and confirmation bias first. Ineffective indicators: perfect grammar; combination of casual and formal registers; "bland" or "robotic" prose; "fancy"/"academic"/"formal" prose (the correlation is with specific words, not register); transition words in isolation (only a few are overused; the pattern has human precedent); unsourced content (570,000+ articles predate LLMs; modern AI text often has citations); bizarre wikitext (more often browser extensions or the content-translation bug T113137; misplaced syntax like ''Catch-22 i''s is a VisualEditor artifact); correct wikitext (visual editor and Preview exist).

## Historical indicators

- Statements about knowledge cutoffs (2022–2023, WP:AICUTOFF): "Up to my last training update", "as of my last knowledge update".
- Section summaries (WP:CONCLUSION / WP:INCONCLUSION): older LLMs added "Conclusion" sections and ended paragraphs by restating the core idea. Words: In summary, In conclusion, Overall.
- Prompt refusal: "as an AI language model", "I cannot offer medical advice, but I can...", "I'm sorry ...". Outright refusals have become rare.
- Overuse of em dashes (2022–September 2026, WP:AIDASH): LLMs use em dashes far more than nonprofessional human writers, in a formulaic, "punched up" way, usually surrounded by spaces. Best used with other indicators; more common on talk pages. Some AI companies suppressed em dashes in newer chatbots (notably GPT-5.1); a July 2026 study found only Claude used em dashes more than professional writers, ChatGPT less. From September 2026 onward, models hard-coded to avoid em dashes also avoid other alternate punctuation: comma/period monotony is now itself a sign.
- Abrupt cut offs: token-limit truncation (also caused by malformed copy/paste or copyright violation).
- Outdated access-date parameters: access dates old relative to the edit; newer chatbots seldom do this; can be legitimate.
- Lexical diversity/elegant variation (WP:AIELEVAR): older models' repetition penalty discouraged word reuse; observed at broad level comparing pre-2023 vs post-2023 Wikipedia text. Caveat: non-native English speakers (e.g. Italian-taught) also avoid repeated words.

## See also / footer notes

- {{Looks AI-generated}}, Wikipedia:Artificial intelligence resources, User:Guy Macon/AI Slop Detection.
- Notes: the guide is less useful for non-informational writing (fiction tells differ); the regression-to-mean effect is visible in text-to-image models (background details blurry/malformed); utm_source has rare exceptions (Google has indexed such URLs).
- References (as supplied) include: Russell, Karpinska & Iyyer 2025 (ACL; frequent ChatGPT users are accurate detectors); Dik, Erdem & Dik 2025 (GPTZero accuracy, arXiv:2506.23517); Dugan et al. 2024 (RAID benchmark, arXiv:2405.07940); Cheng et al. 2025 (Advances in Simulation; humans and tools vs AI content); Fiedler & Döpke 2025 (German theses, 57%/64%); Yakura et al. 2024 (LLM influence on spoken communication, arXiv:2409.01754); Geng et al. 2025 (LLM impact on academia, ACL Findings); Galpin et al. 2025 (AI-induced language change, arXiv:2506.21817); Druck, Paredes & Smith (Graphite "AI Tells", Sept 2026); Belcher 2025 (Chronicle of Higher Education); Sun, Yin, Xu, Koller & Liu ("Idiosyncrasies in Large Language Models"); Juzek & Ward 2025 ("Why Does ChatGPT Delve So Much?", arXiv:2412.11385); Reinhart et al. 2025 (PNAS, "Do LLMs write like humans?"); Walker Rettberg (genre glitches); Sussman & Carter (AI-mediated communication); Geng & Trotta (human-LLM coevolution); Huang et al. ("Wikipedia in the Era of LLMs"); Kobak, González-Márquez, Horvát & Lause 2025 (Science Advances, excess vocabulary in biomedical publications); Kousha & Thelwall 2025 (ISSI, arXiv:2509.09596); Merrill, Chen & Kumer 2025 (Washington Post style analysis); Buchert 2026 (GPT-6 Astra review); Robbins (Substack); Spero & Emi (Pangram technical report); GPT-4 System Card; Rudnicka 2025 (Scientific American, chatbot idiolects); Zhou, Cho & Terveen (LLMs in Wikipedia); Woo 2026 (WSJ, Chinese censorship); Osmonbekov 2026 (Fortune); Murray & Tersigni 2024 (instructor detection); Strzelecki 2024 ("As of my last knowledge update" in scientific papers, Learned Publishing); Ju, Blix & Williams 2025 (domain regeneration, arXiv:2505.07784); Edwards 2025 (Ars Technica, em dash formatting rules); Birattari and Cortelazzo (Italian guidance on avoiding repetitions).
- Further reading: Kriss, Sam (Dec 3, 2025). "Why Does A.I. Write Like … That?". NYT Magazine. External links: CanYouPasstheTuringTest.com; Tropes - AI Writing Pattern Directory.
- License: CC BY-SA 4.0. Page last edited 31 October 2026.
