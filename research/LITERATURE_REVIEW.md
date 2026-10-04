# AI-text detection and meaning-preserving rewriting: a grounded literature review

*Compiled 2026-10-04. I checked every paper below against its arXiv record (title, authors, date) and pulled every quoted number from the paper's own text or abstract. Vendor statements are labelled **[vendor claim]**. Statements that are my inference are labelled **[inference]**.*

---

## 1. How detectors work

### 1.1 Zero-shot statistical methods

| Method | Signal | Notes |
|---|---|---|
| **Perplexity / log-likelihood, entropy, rank, log-rank** | Machine text gets higher likelihood and lower token rank under a scoring LM. | Log-rank baselines and **DetectLLM-LRR/NPR** improved AUROC by 3.9 and 1.75 points over prior zero-shot methods [Su 2023]. |
| **GLTR** | Puts each token in a rank bucket under GPT-2. By default it colours top-10 green, top-100 yellow, top-1,000 red and the rest purple. Human text samples more often from the tail. | In a user study, the overlay raised human detection of fake text from 54% to 72% [Gehrmann 2019]. |
| **DetectGPT** | Machine text sits in regions of negative log-probability curvature. Perturbations made with T5 lower its likelihood more than they lower human text's. | AUROC went from 0.81 to 0.95 on GPT-NeoX news [Mitchell 2023]. |
| **Fast-DetectGPT** | Conditional probability curvature, computed from samples instead of perturbations. | About 75% relative improvement over DetectGPT and 340x faster. In the black-box setting it scores with a *surrogate* model (GPT-Neo-2.7B / GPT-J) [Bao 2024]. |
| **Binoculars** | Ratio of log-perplexity under an "observer" LM to the cross-perplexity between observer and "performer". This corrects the "capybara problem", where an unusual prompt makes machine text look high-perplexity. | Uses Falcon-7B / Falcon-7B-Instruct, and the two models must share a tokenizer. Detects >90% of ChatGPT samples at 0.01% FPR [Hans 2024]. |
| **Ghostbuster** | Token probabilities from a unigram model, a trigram model and GPT-3 (ada, davinci), combined by feature search plus logistic regression. | 99.0 F1 in-domain [Verma 2024]. |
| **DNA-GPT** | Truncates the text, regenerates the continuation, and measures n-gram or probability divergence between original and regeneration. | [Yang 2024] |
| **Raidar** | LLMs edit AI text less than human text when asked to rewrite it. The score is edit distance. | [Mao 2024] |
| **Successors (2024-25)** | **Lastde**: time-series statistics of the token-probability *sequence* (local and global). **Glimpse**: estimates full distributions from proprietary-API top-k probabilities so white-box scores can use GPT-3.5-class models (AUROC about 0.95). | [Xu 2024; Bao 2025] |

**Proxy/surrogate result relevant to us.** Smaller scoring models are better *universal* detectors. OPT-125M reached AUC 0.81 on ChatGPT text, while GPT-J-6B reached 0.45 [Mireshghallah 2024].

**Sentence level.** SeqXGPT feeds per-token log-probability lists from white-box LMs into a CNN plus attention model. It reports that earlier document-level methods "struggle" on sentence-level detection [Wang 2023]. Per-sentence statistics are noisier than document statistics: the sample-complexity bound grows as machine text approaches human text [Chakraborty 2023], and Binoculars accuracy drops on short documents (its Fig. 2) [Hans 2024].

### 1.2 Supervised classifiers and commercial tools

- **RoBERTa detectors.** OpenAI's GPT-2 output detector [Solaiman 2019] and the HC3 ChatGPT detector [Guo 2023] are fine-tuned RoBERTa models. They generalise poorly to unseen domains and generators, and they tend to call unseen machine text human [Wang 2024 (M4)]. **RADAR** trains a detector adversarially against a paraphraser [Hu 2023].
- **GPTZero.**
  - [vendor claim] The current pipeline is "Deep Learning → Sentence Classifier → Paraphraser Shield", with a false positive rate held at no more than 1%.
  - [vendor claim] "As of autumn 2023, GPTZero no longer uses perplexity and burstiness ... migrated to a deep-learning based architecture". The two signals survive as one of seven "indicators".
  - The 2026 technical report [Adam 2026] describes a hierarchical multi-task neural classifier with document labels Human / AI / Mixed. Sentence-level probabilities come from the same forward pass (loss L = L_doc + αL_sent). The model was hardened by red-teaming with paraphrasing prompts, DIPPER, 9 commercial "bypasser" services, and gradient-guided masked-LM token substitution.
  - "Deep Scan" assigns per-sentence importance scores using saliency and occlusion.
  - Treat this report as a vendor-authored description, not independent verification.
- **ZeroGPT.**
  - [vendor claim, zerogpt.com] "DeepAnalyse™" is a "multi-stage methodology" using "comprehensive deep learning ... trained on extensive text collections from the internet, educational datasets, and ... proprietary synthetic AI datasets". It claims 98.4% accuracy and <1% FPR, and "every sentence written by AI is highlighted".
  - **No technical report exists.** Third-party blogs say it uses perplexity and burstiness, but I could not verify that from a primary source.
  - **Independent:** in RAID, ZeroGPT could not be calibrated below **16.9% FPR** (its accuracy-vs-FPR curve plateaued) [Dugan 2024]. It was one of the seven detectors in Liang et al. (below), and one of the 14 tools in Weber-Wulff et al.
- **Turnitin.**
  - [vendor claim, relayed by Inside Higher Ed, 2023-06-01] Turnitin's chief product officer gave these figures: document FPR <1% for documents above 20% AI, sentence-level FPR of "approximately 4 percent", and "54 percent of false positive (human-written) sentences are located right next to AI-written sentences".
  - Turnitin's own pages returned HTTP 403 to my fetches, so I could not verify its segment/window architecture, its minimum length, or its handling of 1-19% scores from the primary source.
- **Independent evaluations.**
  - Weber-Wulff et al. tested 14 tools, including Turnitin. All scored below 80% accuracy. About 50% of manually edited AI texts went undetected, and accuracy on machine-paraphrased AI text was 26% [Weber-Wulff 2023].
  - Perkins et al. tested 6 detectors on 805 samples. Mean accuracy was 39.5% on unmodified AI text and dropped a further 17.4% after evasion edits [Perkins 2024].
  - RAID covered 12 detectors (including GPTZero, Originality, Winston and ZeroGPT), 11 attacks and about 6M generations. Detectors are "easily fooled", and a repetition penalty in decoding strongly lowers accuracy [Dugan 2024].

### 1.3 Features that separate human from LLM text

- **Token predictability:** rank and likelihood (GLTR, log-rank), and its *local dynamics* (Lastde). Simple LLM paraphrasing *lowered* perplexity (LLaMA-3.1-8B scorer) from 14.94 for the original AI text to 9.28. Human text scored 15.02 [Cheng 2025, Table 5].
- **Sentence-length spread and lexical variety.** Human news text shows "more scattered sentence length distributions" and "more variety of vocabulary", along with shorter constituents and different dependency types [Muñoz-Ortiz 2024]. This is the empirical basis for "burstiness". I found **no published ablation that ranks burstiness against other features inside a commercial detector**.
- **Grammatical and rhetorical style (Biber features).**
  - Instruction-tuned models use present participial clauses at 2-5x the human rate (GPT-4o: 5.3x, d = 1.38), and nominalizations at 1.5-2x.
  - They also overuse 'that'-clauses as subjects, phrasal coordination, and certain words. GPT-4o uses "tapestry" and "palpable" more than 100x as often as humans.
  - Differences are *larger for instruction-tuned models than for base models* [Reinhart 2025].
- **Syntactic templates.** POS-sequence templates recur more in model text. 76% of templates found in model output appear in pre-training data, against 35% for human text [Shaib 2024].
- **Which features matter most:** there is no consensus ranking. One quasi-mechanistic hint is that instruction-tuning artifacts, more than "machine-ness" in general, drive commercial scores. Base-model continuations scored 96.7% / 98.8% human on GPTZero / Pangram, against 30.3% / 17.1% for the instruct model given the same prefix [Xu 2026].

### 1.4 Known weaknesses

- **Non-native writers.** Seven detectors (ZeroGPT among them) flagged TOEFL essays at an average FPR of **61.22%**. 19.78% of essays were flagged by all seven, and 97.8% by at least one. Prompting ChatGPT to "enhance the word choices" raised perplexity and cut the FPR to 11.77%. The authors attribute the bias to low perplexity from constrained vocabulary [Liang 2023].
- **Formal and academic prose.**
  - On 2023-25 published abstracts, flag rates were 14.9% (Pangram) and 8.9% (GPTZero), against 0% for 2013-15 abstracts. Non-STEM rates were higher (p < 0.001).
  - Detector scores correlate with long-token and **Academic Word List density**.
  - Light AI "refine" edits were flagged 38-80% of the time [Karr 2026].
- **Length.** Detection needs more samples as models improve [Chakraborty 2023], and accuracy falls on short inputs [Hans 2024; Wu 2024 (DetectRL)]. Turnitin [vendor] reports sentence-level FPR roughly 4x its document-level FPR.

---

## 2. Humanizers and evasion: methods and results

| Attack | Mechanism | Detection effect | Meaning/quality |
|---|---|---|---|
| **DIPPER** [Krishna 2023] | 11B T5 paraphraser with lexical and order-diversity knobs and context conditioning. | DetectGPT dropped from 70.3% to 4.6% detection at 1% FPR. It also evaded GPTZero, watermarks and the OpenAI classifier. | "Without appreciably modifying the input semantics" (P-SP plus human evaluation). |
| **Recursive paraphrasing** [Sadasivan 2024] | Paraphrases repeatedly (about 300-token passages). | Large drops across watermark, neural, zero-shot and retrieval detectors. | "Only slightly degrades text quality in many cases". |
| **SICO** [Lu 2024] | Prompt-only. A *proxy detector* (GPT3-D) greedily picks word and sentence substitutions in in-context examples; the optimised prompt is then reused. | AUC of six detectors (including GPTZero, the OpenAI detector, DetectGPT and Log-Rank) fell by 0.5 on average, *transferring from the proxy*. | Human-level readability in human evaluation. |
| **Substitution / prompt search** [Shi 2024] | LLM-proposed synonym swaps, chosen query-free or by evolutionary search against the detector, plus instructional-prompt search. | Compromised all detectors studied. | "Plausible generations". |
| **HMGC** [Zhou 2024] | Minor perturbations in white-box and black-box settings. | Detectors broken "in as little as 10 seconds". Adversarial training helps only partly. | Small perturbations. |
| **Adversarial Paraphrasing** [Cheng 2025, NeurIPS] | LLaMA-3-8B-Instruct paraphrases. At *every token* it keeps the top-p/top-k candidate (p = 0.99, k = 50) that a *guidance detector* scores lowest. | With OpenAI-RoBERTa-Large as guide: T@1%F fell 98.96% on Fast-DetectGPT and 64.49% on RADAR, with an 87.88% mean reduction across neural, watermark and zero-shot detectors. Simple paraphrasing *increased* T@1%F (+15.03% on Fast-DetectGPT). | SBERT similarity 0.81 versus 0.86 for simple paraphrase. Perplexity close to human. "Slight degradation" overall. |
| **AuthorMist** [David & Gervais 2025] | 3B model trained with GRPO, using a detector API as the reward. | 78.6-96.2% attack success against the target detector. | Semantic similarity >0.94. |
| **StealthRL** [Ranganath & Ramesh 2026] | Qwen3-4B with LoRA and GRPO against a *4-detector ensemble*, with a semantic term in the reward. | Mean TPR@1%FPR of 0.024, AUROC from 0.79 to 0.43. Transfers to 2 held-out detectors. | LLM Likert judging. |
| **HIP** [Xu 2026] | Lightly fine-tuned *base* model used as a paraphraser, applied iteratively. | Best semantic-vs-human-likeness Pareto front on **GPTZero and Pangram** among the baselines tested (DIPPER, SilverSpeak, StealthRL, simple paraphrase). | GPT-5-nano semantic score (0-10). |
| **Commercial humanizers** [Masrour 2025 (DAMAGE)] | Audit of 19 tools. | Many detectors miss humanized text. A detector trained with humanizer data recovers it. | Weak tools added hallucinated citations, nonsense phrases and grammar errors. The best tools kept tone and vocabulary level. |

**RAID nuance [Dugan 2024, Table 6, accuracy at 5% FPR].** Attacks hit detectors unevenly:
- DIPPER paraphrasing lowered GPTZero by only 2.5 points and *raised* Originality by 11.7.
- BERT synonym swap lowered Binoculars by 36.1 points and GLTR by 31.4.
- Homoglyphs lowered Originality by 75.7 points.

Broader stress tests agree: averaged over editing, paraphrasing, prompting and co-generation attacks, detector performance fell 35% [Wang 2024 (Stumbling Blocks)]. Iteratively paraphrased text sits in an "intermediate laundering region" that current detectors handle poorly [Zha 2025 (PADBen)].

**Transfer and proxies.**
1. A guide or proxy can transfer. SICO went from a RoBERTa proxy to GPTZero, and Adversarial Paraphrasing went from a RoBERTa guide to open-source zero-shot and neural detectors.
2. **The choice of proxy matters a lot.** AuthorMist's cross-detector table shows this:
   - The policy trained against the *open-source OpenAI RoBERTa* detector reached only **2.0% success on GPTZero, 0% on Originality and 2.3% on Sapling**.
   - The policy trained against Originality.ai averaged 95.17% across all six detectors.
3. Ensemble training transfers better to unseen detectors (StealthRL).
4. Commercial tools are now hardened against known paraphrasers [Adam 2026; Masrour 2025]. Gains measured against academic detectors may not carry over.

**Meaning preservation.** Papers mostly report SBERT/P-SP similarity or LLM-judge scores. None of them tests exact preservation of numbers, entities or hedges. DAMAGE shows that real humanizers fabricate content. Detector-guided decoding trades some similarity for evasion (0.86 → 0.81 SBERT).

---

## 3. Practical implications for a ZeroGPT-style, sentence-highlighting black box

**What we know:** ZeroGPT is a black box. Its vendor says deep learning plus sentence-level highlighting. Independently, it shows a high FPR floor (RAID), and in 2023 it was among detectors whose scores fell when perplexity was raised [Liang 2023]. Our text is academic, a genre in which *human* prose is flagged because of Academic Word List density [Karr 2026]. **[inference]** Some of the residual 27-30% may be a genre floor rather than a flaw in the rewrite.

**(a) Small local LM scoring per-sentence perplexity or token rank, then rewriting the most predictable sentences.**
- *For it:* small models make good universal scorers [Mireshghallah 2024]. Fast-DetectGPT works with surrogates. GLTR/log-rank capture what Liang found moves commercial scores (perplexity). SeqXGPT shows sentence-level signal exists in small-LM log-probabilities.
- *Against it:* raw perplexity is confounded by topic and prompt (Binoculars' capybara problem). Per-sentence estimates are noisy. Pushing perplexity up invites rare words that may hurt quality or change meaning.
- *Evidence on correlation:* no published study reports correlation between GPT-2 perplexity and ZeroGPT sentence highlights.
- *Use it to:* **triage** which sentences to rewrite, and as one term in an ensemble. Do not use it as the sole objective.

**(b) Binoculars-style score with two small models.**
- It is the strongest open zero-shot detector at low FPR in RAID, so it is a better "is this still AI-like?" check than raw perplexity.
- Caveats: it needs a shared tokenizer, it is published only with 7B Falcon models, and its behaviour with very small model pairs at sentence length is **unverified**. It is fragile to synonym swaps (−36.1), so optimising against it alone may overfit to lexical tricks that a neural ZeroGPT ignores.
- *Use it to:* serve as an ensemble member or held-out check.

**(c) Best-of-n candidate selection with a proxy.**
- This has the best-supported mechanism: SICO's greedy proxy selection, Adversarial Paraphrasing's per-token argmin, and RL-with-detector reward all work. Per-sentence best-of-n is a coarse-grained, meaning-safer version of Cheng et al.
- The literature's main warning is **proxy mismatch**: a weak open-source proxy can fail completely on commercial detectors (AuthorMist: 2% on GPTZero). Ensembles transfer better (StealthRL).
- **[inference]** Use an *ensemble* proxy, for example a GPT-2 log-rank score, a Binoculars-style score and an open RoBERTa/RADAR classifier. Gate every candidate with a hard fact and hedge checker plus a semantic-similarity threshold.
- **[inference]** Calibrate the ensemble against ZeroGPT on 30-50 held-out sentences and report Spearman ρ before trusting it.

**(d) Style or lexical guidance alone.**
- Prompt-level style changes do work: Liang's "literary/technical language" prompts cut detection of AI-written abstracts from up to 68% to up to 28%, and SICO is prompt-only.
- The targets are well documented: participial clauses, nominalizations, 'that'-subject clauses, phrasal coordination, overused words, recurring syntactic templates, and low sentence-length variance [Reinhart 2025; Shaib 2024; Muñoz-Ortiz 2024].
- Risk: an instruction-tuned rewriter can make text *more* detectable (Cheng 2025: simple paraphrase lowered perplexity and raised detection).
- The strongest 2026 commercial-detector result comes from **base-model** paraphrasing [Xu 2026], because instruction tuning leaves the detected artifacts.
- **[inference]** Combine style guidance with (c). Consider generating sentence candidates with a base (non-instruct) model conditioned on human-written academic context.

**Context effects.** Turnitin's [vendor] note that false-positive sentences sit next to AI sentences, together with HIP's emphasis on "local context", suggests sentence highlights depend on their neighbours. **[inference]** Re-score after each edit at paragraph level, and rewrite adjacent flagged clusters together instead of one isolated sentence at a time.

---

## Unverified or unavailable

- ZeroGPT's internal method (perplexity/burstiness, model type). Only marketing claims are available.
- Turnitin's segment/window architecture, minimum word count, and 1-19% suppression rule (primary pages returned 403). Only the 2023 figures relayed by Inside Higher Ed are verified.
- Any published correlation between open-source proxy scores (GPT-2 perplexity, Binoculars) and **ZeroGPT** specifically.
- Behaviour of Binoculars with small (<1B) model pairs at sentence length.

---

## References

1. Gehrmann, Strobelt, Rush. *GLTR: Statistical Detection and Visualization of Generated Text.* ACL 2019 Demo. arXiv:1906.04043. https://arxiv.org/abs/1906.04043
2. Mitchell, Lee, Khazatsky, Manning, Finn. *DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature.* ICML 2023. arXiv:2301.11305. https://arxiv.org/abs/2301.11305
3. Bao, Zhao, Teng, Yang, Zhang. *Fast-DetectGPT: Efficient Zero-Shot Detection ... via Conditional Probability Curvature.* ICLR 2024. arXiv:2310.05130. https://arxiv.org/abs/2310.05130
4. Hans, Schwarzschild, Cherepanova, Kazemi, Saha, Goldblum, Geiping, Goldstein. *Spotting LLMs With Binoculars.* 2024 (venue not verified). arXiv:2401.12070. https://arxiv.org/abs/2401.12070
5. Verma, Fleisig, Tomlin, Klein. *Ghostbuster: Detecting Text Ghostwritten by Large Language Models.* NAACL 2024. arXiv:2305.15047. https://arxiv.org/abs/2305.15047
6. Yang, Cheng, Wu, Petzold, Wang, Chen. *DNA-GPT: Divergent N-Gram Analysis for Training-Free Detection of GPT-Generated Text.* 2023 (venue not verified). arXiv:2305.17359. https://arxiv.org/abs/2305.17359
7. Su, Zhuo, Wang, Nakov. *DetectLLM: Leveraging Log Rank Information for Zero-Shot Detection.* 2023. arXiv:2306.05540. https://arxiv.org/abs/2306.05540
8. Mao, Vondrick, Wang, Yang. *Raidar: geneRative AI Detection viA Rewriting.* ICLR 2024. arXiv:2401.12970. https://arxiv.org/abs/2401.12970
9. Xu et al. *Training-free LLM-generated Text Detection by Mining Token Probability Sequences (Lastde).* 2024. arXiv:2410.06072. https://arxiv.org/abs/2410.06072
10. Bao, Zhao, He, Zhang. *Glimpse: Enabling White-Box Methods to Use Proprietary Models.* ICLR 2025. arXiv:2412.11506. https://arxiv.org/abs/2412.11506
11. Mireshghallah, Mattern, Gao, Shokri, Berg-Kirkpatrick. *Smaller Language Models are Better Black-box Machine-Generated Text Detectors.* 2023 (venue not verified). arXiv:2305.09859. https://arxiv.org/abs/2305.09859
12. Wang P. et al. *SeqXGPT: Sentence-Level AI-Generated Text Detection.* EMNLP 2023. arXiv:2310.08903. https://arxiv.org/abs/2310.08903
13. Chakraborty et al. *On the Possibilities of AI-Generated Text Detection.* 2023. arXiv:2304.04736. https://arxiv.org/abs/2304.04736
14. Solaiman et al. *Release Strategies and the Social Impacts of Language Models.* 2019. arXiv:1908.09203. https://arxiv.org/abs/1908.09203
15. Guo et al. *How Close is ChatGPT to Human Experts? (HC3).* 2023. arXiv:2301.07597. https://arxiv.org/abs/2301.07597
16. Wang Y. et al. *M4: Multi-generator, Multi-domain, and Multi-lingual Black-Box MGT Detection.* 2023 (venue not verified). arXiv:2305.14902. https://arxiv.org/abs/2305.14902
17. Hu, Chen, Ho. *RADAR: Robust AI-Text Detection via Adversarial Learning.* NeurIPS 2023. arXiv:2307.03838. https://arxiv.org/abs/2307.03838
18. Adam, Cui, Thomas, ... Tian, Lee. *GPTZero: Robust Detection of LLM-Generated Texts.* 2026 (vendor). arXiv:2602.13042. https://arxiv.org/abs/2602.13042
19. Emi, Spero. *Technical Report on the Pangram AI-Generated Text Classifier.* 2024 (vendor). arXiv:2402.14873. https://arxiv.org/abs/2402.14873
20. GPTZero. *Technology* page and *Perplexity and burstiness* post (vendor). https://gptzero.me/technology ; https://gptzero.me/news/perplexity-and-burstiness-what-is-it/
21. ZeroGPT homepage (vendor). https://www.zerogpt.com/
22. D'Agostino. *Turnitin's AI Detector: Higher-Than-Expected False Positives.* Inside Higher Ed, 2023-06-01. https://www.insidehighered.com/news/quick-takes/2023/06/01/turnitins-ai-detector-higher-expected-false-positives
23. Weber-Wulff et al. *Testing of Detection Tools for AI-Generated Text.* Int. J. Educ. Integrity 19:26 (2023). arXiv:2306.15666. https://arxiv.org/abs/2306.15666
24. Perkins et al. *GenAI Detection Tools, Adversarial Techniques and Implications for Inclusivity in Higher Education.* IJETHE 21:53 (2024). arXiv:2403.19148. https://arxiv.org/abs/2403.19148
25. Dugan et al. *RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors.* ACL 2024. arXiv:2405.07940. https://arxiv.org/abs/2405.07940
26. Wu J. et al. *DetectRL: Benchmarking LLM-Generated Text Detection in Real-World Scenarios.* NeurIPS 2024 D&B. arXiv:2410.23746. https://arxiv.org/abs/2410.23746
27. Liang, Yuksekgonul, Mao, Wu, Zou. *GPT detectors are biased against non-native English writers.* Patterns 2023. arXiv:2304.02819. https://arxiv.org/abs/2304.02819
28. Karr, Khvatskii, Hua, Chawla. *Why AI Detection Fails for Academic Integrity.* 2026. arXiv:2608.11256. https://arxiv.org/abs/2608.11256
29. Muñoz-Ortiz, Gómez-Rodríguez, Vilares. *Contrasting Linguistic Patterns in Human and LLM-Generated News Text.* AI Review 57:265 (2024). arXiv:2308.09067. https://arxiv.org/abs/2308.09067
30. Reinhart et al. *Do LLMs write like humans? Variation in grammatical and rhetorical styles.* PNAS 122 (2025). arXiv:2410.16107. https://arxiv.org/abs/2410.16107
31. Shaib, Elazar, Li, Wallace. *Detection and Measurement of Syntactic Templates in Generated Text.* EMNLP 2024. arXiv:2407.00211. https://arxiv.org/abs/2407.00211
32. Krishna, Song, Karpinska, Wieting, Iyyer. *Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense.* NeurIPS 2023. arXiv:2303.13408. https://arxiv.org/abs/2303.13408
33. Sadasivan, Kumar, Balasubramanian, Wang, Feizi. *Can AI-Generated Text be Reliably Detected?* TMLR. arXiv:2303.11156. https://arxiv.org/abs/2303.11156
34. Lu, Liu, He, Wang, Ong, Tang. *Large Language Models can be Guided to Evade AI-Generated Text Detection (SICO).* TMLR 2024. arXiv:2305.10847. https://arxiv.org/abs/2305.10847
35. Shi, Wang, Yin, Chen, Chang, Hsieh. *Red Teaming Language Model Detectors with Language Models.* TACL 2024. arXiv:2305.19713. https://arxiv.org/abs/2305.19713
36. Zhou, He, Sun. *Humanizing Machine-Generated Content: Evading AI-Text Detection through Adversarial Attack.* LREC-COLING 2024. arXiv:2404.01907. https://arxiv.org/abs/2404.01907
37. Wang Y., Feng et al. *Stumbling Blocks: Stress Testing the Robustness of MGT Detectors Under Attacks.* 2024. arXiv:2402.11638. https://arxiv.org/abs/2402.11638
38. Cheng, Sadasivan, Saberi, Saha, Feizi. *Adversarial Paraphrasing: A Universal Attack for Humanizing AI-Generated Text.* NeurIPS 2025. arXiv:2506.07001. https://arxiv.org/abs/2506.07001
39. David, Gervais. *AuthorMist: Evading AI Text Detectors with Reinforcement Learning.* 2025. arXiv:2503.08716. https://arxiv.org/abs/2503.08716
40. Ranganath, Ramesh. *StealthRL: Reinforcement Learning Paraphrase Attacks for Multi-Detector Evasion.* 2026. arXiv:2602.08934. https://arxiv.org/abs/2602.08934
41. Xu, Zhong, Raghunathan, Fang, Kolter. *Base Models Look Human To AI Detectors.* 2026. arXiv:2605.19516. https://arxiv.org/abs/2605.19516
42. Masrour, Emi, Spero. *DAMAGE: Detecting Adversarially Modified AI Generated Text.* 2025. arXiv:2501.03437. https://arxiv.org/abs/2501.03437
43. Zha, Min, Sushmita. *PADBen: Benchmark for AI Text Detectors Against Paraphrase Attacks.* 2025. arXiv:2511.00416. https://arxiv.org/abs/2511.00416
