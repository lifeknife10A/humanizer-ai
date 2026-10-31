# AI Content Detection — raw research paste (absorbed 2026, source: Wikipedia article "Artificial intelligence content detection", last edited 22 Oct 2026)

Artificial intelligence detection software aims to determine whether some content (text, image, video, or audio) was generated using artificial intelligence (AI). This software is often unreliable.[1]

## Accuracy issues

Many AI detection tools have been shown to be unreliable in detecting AI-generated text. In a 2023 study conducted by Weber-Wulff et al., researchers evaluated 14 detection tools including Turnitin and GPTZero and found that "all scored below 80% of accuracy and only 5 over 70%."[2] They also found that these tools tend to have a bias for classifying texts more as human than as AI, and that accuracy of these tools worsens upon paraphrasing.[2]

## False positives

In AI content detection, a false positive is when human-written work is incorrectly flagged as AI-written. Many AI detection platforms claim to have a minimal level of false positives, with Turnitin claiming a less than 1% false positive rate.[3] However, later research by The Washington Post produced much higher rates of 50%, though they used a smaller sample size.[4] False positives in an academic setting frequently lead to accusations of academic misconduct, which can have serious consequences for a student's academic record. Additionally, studies have shown evidence that many AI detection models are prone to give false positives to work written by people whose first language is not English, and also to neurodivergent people.[5][6]

In June 2023, Janelle Shane wrote that portions of her book You Look Like a Thing and I Love You were flagged as AI-generated.[1]

## False negatives

A false negative is a failure to identify documents with AI-written text. False negatives often happen as a result of a detection software's sensitivity level or because evasive techniques were used when generating the work to make it sound more human.[7] False negatives are less of a concern academically, since they aren't likely to lead to accusations and ramifications. Notably, Turnitin stated they have a 15% false negative rate.[8]

## Text detection

For text, plagiarism, often by detecting repetition of words as telltale signs that a text was AI-generated (including hallucinations). Detection systems may also rely on stylistic and structural regularities associated with LLM output, such as unusually consistent grammar, formulaic transitions, repeated discourse markers, and recurring rhetorical templates. Some tools are designed less to establish authorship provenance than to flag prose that resembles common LLM-generated style patterns.

They are often used by teachers marking their students, usually on an ad hoc basis. Following the release of ChatGPT and similar AI text generative software, many educational establishments have issued policies against the use of AI by students.[9] AI text detection software is also used by those assessing job applicants, as well as online search engines,[10] hiring, online moderation and publishing.

Current detectors may sometimes be unreliable and have incorrectly marked work by humans as originating from AI[11][12][4] while failing to detect AI-generated work in other instances.[13] MIT Technology Review said that the technology "struggled to pick up ChatGPT-generated text that had been slightly rearranged by humans and obfuscated by a paraphrasing tool".[14] AI text detection software has also been shown to discriminate against non-native speakers of English.[10]

Two students from the University of California, Davis, were referred to the university's Office of Student Success and Judicial Affairs (OSSJA) after their professors scanned their essays with positive results; the first with an AI detector called GPTZero, and the second with an AI detector integration in Turnitin. However, following media coverage,[15] and a thorough investigation, the students were cleared of any wrongdoing.[16][17]

In April 2023, Cambridge University and other members of the Russell Group of universities in the United Kingdom opted out of Turnitin's AI text detection tool, after expressing concerns it was unreliable.[18] The University of Texas at Austin opted out of the system six months later.[19]

In May 2023, a professor at Texas A&M University–Commerce used ChatGPT to detect whether his students' content was written by it, which ChatGPT said was the case. As such, he threatened to fail the class despite ChatGPT not being able to detect AI-generated writing.[20] No students were prevented from graduating because of the issue, and all but one student (who admitted to using the software) were exonerated from accusations of having used ChatGPT in their content.[21]

In July 2023, a paper titled "GPT detectors are biased against non-native English writers" was released, reporting that GPTs discriminate against non-native English authors. The paper compared seven GPT detectors against essays from both non-native English speakers and essays from United States students. The essays from non-native English speakers had an average false positive rate of 61.3%.[22]

An article by Thomas Germain, published on Gizmodo in June 2024, reported job losses among freelance writers and journalists due to AI text detection software mistakenly classifying their work as AI-generated.[23]

In September 2024, Common Sense Media reported that generative AI detectors had a 20% false positive rate for Black students, compared to 10% of Latino students and 7% of White students.[24][25]

To improve the reliability of AI text detection, researchers have explored digital watermarking techniques (see Text watermarking). A 2023 paper titled "A Watermark for Large Language Models"[26] presents a method to embed imperceptible watermarks into text generated by large language models (LLMs). This watermarking approach allows content to be flagged as AI-generated with a high level of accuracy, even when text is slightly paraphrased or modified. The technique is designed to be subtle and hard to detect for casual readers, thereby preserving readability, while providing a detectable signal for those employing specialized tools. However, while promising, watermarking faces challenges in remaining robust under adversarial transformations and ensuring compatibility across different LLMs.

## Anti text detection

There is software available designed to bypass AI text detection.[27][28]

In practice, evasion may not require specialized bypass tools. Paraphrasing, style editing, and removal of repeated discourse markers can substantially reduce the effectiveness of detectors that rely on recognizable surface patterns. A study published in August 2023 analyzed 20 abstracts from papers published in the Eye Journal, which were then paraphrased using GPT-4.0. The AI-paraphrased abstracts were examined for plagiarism using QueText and for AI-generated content using Originality.AI. The texts were then re-processed through an adversarial software called Undetectable.ai in order to reduce the AI-detection scores. The study found that the AI detection tool, Originality.AI, identified text generated by GPT-4 with a mean accuracy of 91.3%. However, after reprocessing by Undetectable.ai, the detection accuracy of Originality.ai dropped to a mean accuracy of 27.8%.[29]

Some experts also believe that techniques like digital watermarking are ineffective because they can be removed or added to trigger false positives.[30] "A Watermark for Large Language Models" paper by Kirchenbauer et al. (2023) [26] also addresses potential vulnerabilities of watermarking techniques. The authors outline a range of adversarial tactics, including text insertion, deletion, and substitution attacks, that could be used to bypass watermark detection. These attacks vary in complexity, from simple paraphrasing to more sophisticated approaches involving tokenization and homoglyph alterations. The study highlights the challenge of maintaining watermark robustness against attackers who may employ automated paraphrasing tools or even specific language model replacements to alter text spans iteratively while retaining semantic similarity. Experimental results show that although such attacks can degrade watermark strength, they also come at the cost of text quality and increased computational resources.

## Image, video, and audio detection

Several purported AI image detection software exist, to detect AI-generated images (for example, those originating from Midjourney or DALL-E). They are not completely reliable.[31][32]

Industry analyses have also noted that AI-driven image recognition systems often struggle in real-world environments, where inconsistent lighting, noise and variable visual inputs reduce detection reliability, a challenge highlighted in modern agricultural quality-control research.[33]

Others claim to identify video and audio deepfakes, but this technology is also not fully reliable yet either.[34]

Despite debate around the efficacy of watermarking, Google DeepMind is actively developing a detection software called SynthID, which works by inserting a digital watermark that is invisible to the human eye into the pixels of an image.[35][36]

## See also

- AI effect – Phenomenon in which AI achievements are reclassified as non-intelligent
- AI slop – Low-quality AI-generated digital content
- Copyleaks – Plagiarism detection platform
- AI alignment – Conformance of AI to intended objectives
- Artificial intelligence and elections
- Comparison of anti-plagiarism software
- Content similarity detection – Process of detecting plagiarism and/or copyright infringement
- Hallucination (artificial intelligence) – Erroneous AI-generated content presented as true
- Natural language processing – Processing of natural language by a computer

## References (as supplied)

1. "'Don't use AI detectors for anything important,' says the author of the definitive 'AI Weirdness' blog. Her own book failed the test". Fortune.
2. Weber-Wulff, Debora, et al. (2023-12-25). "Testing of detection tools for AI-generated text". International Journal for Educational Integrity. 19 (1): 26. arXiv:2306.15666. doi:10.1007/s40979-023-00146-z.
3. "Understanding false positives within our AI writing detection capabilities". turnitin.com. 2023-03-16.
4. Fowler, Geoffrey A.; Ovide, Shira (2023-04-01). "We tested a new ChatGPT detector for teachers. It flagged an innocent student". The Washington Post.
5. "AI-Detectors Biased Against Non-Native English Writers". Stanford HAI.
6. "The Challenge of AI Checkers". Center for Transformative Teaching, Nebraska.
7. Condit, Cynthia. "LibGuides: ChatGPT and Generative AI Legal Research Guide: AI Detection Tools". law-arizona.libguides.com.
8. "Turnitin adding AI writing detection, but instructors should use it with caution".
9. Hern, Alex (31 December 2022). "AI-assisted plagiarism? ChatGPT bot says it has an answer for that". The Guardian.
10. Sample, Ian (10 July 2023). "Programs to detect AI discriminate against non-native English speakers, shows study". The Guardian.
11. Fowler, Geoffrey A. (2 June 2023). "Detecting AI may be impossible. That's a big problem for teachers". The Washington Post.
12. Tangermann, Victor (9 January 2023). "There's a Problem With That App That Detects GPT-Written Text: It's Not Very Accurate". Futurism.
13. Taylor, Josh (1 February 2023). "ChatGPT maker OpenAI releases 'not fully reliable' tool to detect AI generated content". The Guardian.
14. Williams, Rhiannon (7 July 2023). "AI-text detection tools are really easy to fool". MIT Technology Review.
15. "AI Detection Apps Keep Falsely Accusing Students of Cheating". Futurism. 6 June 2023.
16. Jimenez, Kayla. "Professors are using ChatGPT detector tools to accuse students of cheating. But what if the software is wrong?". USA TODAY.
17. Klee, Miles (2023-06-06). "She Was Falsely Accused of Cheating With AI -- And She Won't Be the Last". Rolling Stone.
18. Staton, Bethan (3 April 2023). "Universities express doubt over tool to detect AI-powered plagiarism". Financial Times.
19. Carter, Tom. "Some universities are ditching AI detection software amid fears students could be falsely accused of cheating by using ChatGPT". Business Insider.
20. Verma, Prashnu (18 May 2023). "A professor accused his class of using ChatGPT, putting diplomas in jeopardy". The Washington Post.
21. "College instructor put on blast for accusing students of using ChatGPT". NBC News. 18 May 2023.
22. Liang, Weixin, et al. (14 July 2023). "GPT detectors are biased against non-native English writers". Patterns. 4 (7) 100779. doi:10.1016/j.patter.2023.100779.
23. Germain, Thomas (2024-06-12). "AI Detectors Get It Wrong. Writers Are Being Fired Anyway". Gizmodo.
24. Madden, Mary, et al. (18 September 2024). "The Dawn of the AI Era" (PDF). Common Sense Media. p. 10.
25. Klein, Alyson (18 September 2024). "Black Students Are More Likely to Be Falsely Accused of Using AI to Cheat". Education Week.
26. Kirchenbauer, Johannes, et al. (2023). "A Watermark for Large Language Models". arXiv:2301.10226.
27. Beam, Christopher. "The AI Detection Arms Race Is On—and College Students Are Building the Weapons". Wired.
28. Lee, Maxie (August 8, 2025). "Is Undetectable AI Legit? 2025 Review, Accuracy & User Insights". Humanizer Ai.
29. Taloni, Andrea; Scorcia, Vincenzo; Giannaccare, Giuseppe (2023-08-02). "Modern threats in academia: evaluating plagiarism and artificial intelligence detection scores of ChatGPT". Eye. 38 (2): 397-400. doi:10.1038/s41433-023-02678-7.
30. Knibbs, Kate. "Researchers Tested AI Watermarks—and Broke All of Them". Wired.
31. Thompson, Stuart A.; Hsu, Tiffany (28 June 2023). "How Easy Is It to Fool A.I.-Detection Tools?". The New York Times.
32. Rizwan, Choudhury (October 15, 2023). "Expert debunks AI tool's claim that Israel's photo is fake". Interesting Engineering.
33. Hamal, Ihor (24 September 2025). "Digital Quality Control: The New Edge In Agriculture". Forbes.
34. Hsu, Tiffany; Myers, Steven Lee (18 May 2023). "Another Side of the A.I. Boom: Detecting What A.I. Makes". The New York Times.
35. Pierce, David (2023-08-29). "Google made a watermark for AI images that you can't edit out". The Verge.
36. Wiggers, Kyle (2023-08-29). "DeepMind partners with Google Cloud to watermark AI-generated images". TechCrunch.
