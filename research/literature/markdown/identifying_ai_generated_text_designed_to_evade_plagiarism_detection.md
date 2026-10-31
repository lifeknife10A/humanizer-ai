# Paper Title (use style: paper title)
**Authors / Metadata**: IEEE
> **Source File**: `identifying_ai_generated_text_designed_to_evade_plagiarism_detection.pdf` | **Total Pages**: 7

---

<!-- Page 1 -->

# Identifying AI-Generated Text Designed to Evade

# Plagiarism Detection
Aarushi Singh Ahlawat Department of Electronics and

Communication Engineering Amrita School of Engineering,

Bengaluru Amrita Vishwa Vidyapeetham, India

ahlawat.aarushi@gmail.com

Vivek Venugopal Department of Electronics and

Communication Engineering Amrita School of Engineering,

Bengaluru Amrita Vishwa Vidyapeetham, India

v_vivek@blr.amrita.edu

Jaithra Sarma Karlapalam Department of Electronics and

Communication Engineering Amrita School of Engineering,

Bengaluru Amrita Vishwa Vidyapeetham, India BL.EN.U4EAC21025@bl.students.am

rita.edu

Susmitha Vekkot Department of Electronics and

Communication Engineering Amrita School of Engineering,

Bengaluru Amrita Vishwa Vidyapeetham, India

v_susmitha@blr.amrita.edu

Priyam Joshi Department of Electronics and

Communication Engineering Amrita School of Engineering,

Bengaluru Amrita Vishwa Vidyapeetham, India BL.EN.U4EAC21053@bl.students.amr

ita.edu

Abstract—It is inevitable to detect such content to ensure intellectual and academic integrity. Presented study investigates robust approach toward the detection of AI-generated content using a fine-tuned BERT model. A labeled Kaggle dataset with human- and AI-generated text has been used for training, validation and performance evaluation. Data preprocessing has been carried out using text normalization, noise removal, and tokenization using the BERT tokenizer. To address the memory constraint, the dataset has been processed in batches. The model has been fine-tuned with sparse categorical cross-entropy loss and the Adam optimizer. Classification in the form of SoftMax probabilities using a threshold to classify text either as human generated or AI-generated form the basis for performance evaluation. The presented model demonstrates the superior performance in comparison to Roberta and DistilBERT models for all the four evaluation criteria with accuracy of 72%, precision of 80%, recall of 60% and F1- score of 69%. This investigated scalable framework paves way for effective and efficient detection of plagiarism through AI-generated content and humanizers.

Keywords—AI Content Detection, Machine-Generated Text, Humanizer, Text Classification, Plagiarism Detection, Linguistic features, Syntactic features, Chunks, Natural language processing, BERT Fine-Tuning, Deep Learning

I. INTRODUCTION Advancement in generative AI and humanizers has made detection and identification of AI-generated content a challenge. As AI systems, specifically generative models and humanizers, become more advanced, they are becoming increasingly capable of producing text that closely mimics human writing. AI is not only limited to text content but also encompass visual image content as well [1]. This raises significant concerns over the impact on creativity and originality, especially in academic and creative fields, where the authenticity of work is paramount. The need for effective AI content detection tools has never been more pressing, as these tools are vital in preserving the integrity of humangenerated content.

Considering challenges posed by AI for plagiarism detection tools, systematic analysis [2], investigation of linguistics features [3] and approach for enhancement of detection performance using syntax semantics and citation information [4] has been presented over last decade. Citation context classification has been further automated by Premjith and Soman in [5].

Present study further investigates the findings of Sardinha [6] in the context of recent development in generative AI and humanizer and primarily delves into the limitations of current AI content detection methods. Sardinha [6] highlighted the intrinsic difficulty that AI has in replicating the nuances and spontaneous variations of human language. AI-generated texts lack the same level of complexity and authenticity as humanauthored content, especially in areas such as conversational dynamics and register awareness. Though, humanizer advancement narrowing this gap as well. Despite, all recent advancements in generative AI models and humanizer these models cannot fully replicate the complexities of human expression. Hence, there is opportunity to enhance and make plagiarism and AI content detection tools more robust using subtle differences between human and AI generated content.

A number of attempts have been made to employing machine learning models for AI generated content detection, e.g., [7] and [8] but with limited repeatability and reproducibility. These approaches were able to distinguish between AI generated and human text using deep learning and other classifiers with varied performance. Performance reported in [7] that for GPT-4 resulted in an average accuracy of 67% but also generated 45% false positives. This is serious limitation because nearly half of the text written by a human was misclassified as AI-generated. Study presented in [8] also reported similar findings whereby the Extremely Randomized Trees Classifier machine learning model was able to attain an accuracy of 72% but it could only recall at 54%, rendering this ineffective for the proper identification of AI-generated text. These significant limitations, along with poor generalization and imbalance in the datasets, indicate that black-box implementation of machine learning models is not sufficient for a robust for AI-generated content detection system.

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 484

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


<!-- Page 2 -->
Bidirectional Encoder Representations from Transformers (BERT) based models found to perform better than traditional machine learning approaches for AI-generated content detection [9]. Since BERT are pre-trained over vast datasets, it has a greater opportunity to identify subtle features of human language, especially very complex syntactic and semantic features that other models miss to distinguish between AI-generated text and the original human written text.

Considering the strength of BERT in overcoming challenges like dataset imbalances and poor generalization, that makes it a more nuanced and accurate solution to the AI content detection problem, a systematic methodology has been developed leveraging BERT to effectively analyze and classify the AI-generated and human written content. Presented investigation demonstrated that a BERT-based uncased model result in superior performance for detection, identification and classification of human-written content against AI-generated content including that using humanizer. Further fine-tuning on a labeled dataset with an optimized preprocessing pipeline shows that:

• An optimally fine-tuned BERT uncased model performs better in terms of accuracy, precision, and recall than its alternatives, such as RoBERTa [10] and DistilBERT [11].

• Preprocessing approach, such as text normalization and tokenization, and hyperparameter tuning are the key to achieve better performance.

• Presented scalable and efficient framework with regular updates in-line with development in generative AI and humanizer, demonstrate high potential in detection, classification, and analysis AI-generated.

II. LITERATURE SURVEY

Any classifiers performance depends on separability of classes within available dimensions in the dataset. Key differences between AI-generated and human-written texts in terms of style, syntax and other linguistic features has been discussed in [6] which forms the basis for analysis. This study reveals a lack of coherence, flow, and arguments mainly due to limited contextual understanding and reliance on learned patterns. Hence, this approach resulted in frequent misclassifications and render this ineffective for identification and detection of AI-generated content.

BERT-based models in [9] demonstrated a remarkable accuracy of 91%, with a false positive rate of just 12% and a recall rate of 89%, thus outperforming traditional classifiers such as the Extremely Randomized Trees Classifier [8]. Performance of other model based on variation of BERT reported as RoBERTa in [10] and DistilBERT in [11] is comparable for certain dataset.

Iyad et al. [12] proposed the TSA-LSTMNN model to improve the detection capabilities for ChatGPT-generated content. The model reported to achieve an accuracy of 93.93% with the ChatGPT dataset as it combined Term FrequencyInverse Document Frequency (TFIDF), word embeddings, and contextual vectors with sequence modeling in a way surpassing prior approaches in precision, recall, and F1-score. These results establish it as powerful approach to distinguishing between AI-generated and human written text across varying datasets and scenarios.

Dukić et al [13] presented a BERT based approach for bot detection on social media. The study focused on the integration of shallow models and logistic regression with deep learning to achieve better interpretability and performance. It is suggested that adding features like gender prediction significantly improved the accuracy of the model and that the models must be tailored to the specific task.

Impact and effectiveness of preprocessing especially, techniques like tokenization, lowercasing, removal of stop words, and normalization in data preparation on the performance of the NLP models has been investigated and highlighted in [14]. Z. Jianqiang and G. Xiaolin, [15] further investigated and explored the preprocessing aspect for sentiment analysis tasks. In general, it is found that deleting URLs, acronyms, and redundant words improved the accuracy of classification greatly and also provide better generalization. Both the studies highlighted the impact of preprocessing, in addition to improving data quality, influences the performance of the algorithms used in machine learning.

Based on the findings and recommendations in recent advances in the field, present investigation has been focused on improvement on models, handling misclassifications, and optimal fine-tuning of a BERT based tool for detection, identification and classification of AI-generated test including humanizer.

III. METHODOLOGY

A. Dataset

The dataset used for this study is available from Kaggle and this was collected by S. Gerami [16]. This dataset contains 487,235 rows and 2 columns which includes a combination of AI-generated and human written texts in first column and label in the second column. The “generated” column shows whether the text was created by AI (1.0) or by a human (0.0). Specifically, the dataset contains 305,797 human-written entries and 181,438 AI-generated entries, thus providing a balanced representation of both categories. The data was gathered from multiple sources, aggregated, and duplicate entries were removed to ensure the quality and uniqueness of the dataset. With around 500,000 essays, this corpus is a great resource for testing and training AI-generated content detection models. This provide a range of text types for performance evaluation of detection and analysis approaches to distinguish human-written from machinegenerated content.

B. PreProcessing, Data Loading and Batching/Chunking

Preprocessing has a vital role in text mining and NLP tasks; it helps prepare raw text for further analysis and thereby improves the accuracy and effectiveness of the models. Different preprocessing techniques that are commonly used include tokenization, stopword removal, and stemming to transform the text into a more structured format. Ramasamy et al. [17] emphasized the importance of applying a sequence of preprocessing steps to enhance the effectiveness of mining algorithms. In the context of AI content detection, preprocessing ensures that the text data is cleansed of irrelevant or redundant information, thus enabling models to focus on meaningful features that aid in distinguishing between human and AI-generated content. Techniques used for preprocessing are included by this study to improve the quality of the input data before tokenization and fed into the BERT model for classification. The preprocessing techniques

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 485

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


<!-- Page 3 -->
used in this study consists of Tokenization, Stop-word Removal, Stemming, Lowercasing, Punctuation Removal, Number Removal. Downsizing the dataset helped in computation for the process, which ensured efficient reducing the complexity of The downsized function included processing during training. optimizing performance while original columns with text length and cleaned text added to the mix, bringing a refined dataset into the scene with dimensions 438,511 rows by 4 columns: text, generated, text length, and cleaned text.

Another important aspect besides preprocessing techniques is batching and chunking techniques. Batching and chunking are critical preprocessing techniques to handle bigger datasets efficiently, especially for BERT-based models. Data is divided into manageable chunks to limit memory requirement and avoid a memory overflow while dealing with datasets larger than system memory. This would be especially beneficial for the BERT tokenizer, allowing the model to process the inputs in smaller batches, in parallel, to accelerate training and inference. Use of generators also allows on-the-fly chunking, thus loading data as efficiently as possible in computational terms while ensuring scalability. Flexibility increases with the capability to change the size of batches according to constraints in memory and performance. This indirectly leads to more frequently updating the gradient, which, in turn accelerates convergence and improves the models’ efficiency and, hence their overall performance over large datasets [13].

C. Exploratory Data Analysis (EDA)

Exploratory Data Analysis (EDA) was conducted on both the downsized datasets to gain insights into the data distribution and structure. Fig. 1 shows a histogram of text lengths plotted to examine the distribution of the number of words across the dataset, helping to identify any patterns or anomalies.

Fig. 1. Histogram of Downsized Dataset

Fig. 2 showcases a boxen plot of text length was used to visualize the spread of text lengths, highlighting outliers and ensuring the data is within expected ranges. Fig. 3 shows a density distribution provided a smooth representation of text length distribution, offering a clearer view of how text sizes vary within the dataset. Lastly, a bar graph was created for both the original and downsized datasets to compare the count

of the” generated” column, illustrating the balance between human-generated and AI-generated text. This comparison is shown in Fig. 4.

Fig. 2. Boxen Plot of Downsized Dataset

Fig. 3. Density Distribution of Downsized Dataset

Fig. 4. Original Count vs Downsized Count

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 486

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


<!-- Page 4 -->
IV. MODEL ARCHITECTURE AND WORKING

This section describes the architecture and the workflow of the operating model to identify AI-generated content. The model proposed uses a pre-trained BERT (Bidirectional Encoder Representations from Transformers) model that was fine-tuned on the text classification task. BERT, originally developed for the purpose of NLU, has been able to outperform state-of-the-art performances across many NLP applications such as text classification, question answering, and sentiment analysis [18]. The transformer-based architecture of BERT has core advantage in terms of enabling the model to capture the context in a bidirectional manner and thus renders it very applicable for complex textual patterns. The subsequent subsections break down the model’s architecture and data preprocessing as well as operational flow as shown in Fig. 5.

Fig. 5. Block Diagram Overview

A. Pre-trained BERT Model

BERT is a transformer-based architecture that uses selfattention mechanisms to encode contextual relations between words in a sentence as shown presented in [19]. It is pretrained over a large corpus of texts to learn general language representations. BERT-base-uncased, a 12-layer model with 110 million parameters has been used in presented study. This model is known for its balancing performance and efficiency. The pre-trained model is further finetuned in for binary classification toward discriminating between human-written and AI-generated content.

The BERT model processes its input text by passing this through multiple layers of self-attention followed by a classifier that gives the final output prediction. In the present study, the output layer is adapted as a binary classification problem using two labels: Human and AI. The key components of the architecture are as in Fig. 6. And also, are mentioned below:

• Layer: Text is tokenized and converted into input embeddings, which are passed through the BERT encoder.

• Encoder Layers: The encoder layers utilize selfattention to capture contextual relationships.

• Output Layer: The final output layer applies a SoftMax activation function to provide a probability distribution over the two classes.

The transformative impact of BERT on NLP makes it a highly-supported choice for the task of discriminating between human-written and AI-generated content. Jacob et al. [18] summarize BERT’s state-of-the-art performance across multiple NLP tasks, where BERTBASE and BERTLARGE outperform other models such as OpenAI GPT and ESIMELMo, scoring 80.5 on the GLUE leaderboard and improving MNLI accuracy by 4.6 points. BERT’s pretraining through masked language modeling and next sentence prediction has been found to be highly effective. It achieved 97.98% accuracy on the latter task. Fine-tuning BERT requires minimal task specific adjustments, making it a unified and cost-effective solution for NLP tasks.

This agrees with Patrick et al. [20] who noted the pretraining objectives as well as the efficiency of models for contextualized text encoders. The survey mainly explains how the transfer learning could utilize the pre-trained models like BERT towards increased efficiency and performance during task implementation. Using a pre-trained BERT model and fine-tuning it for the binary classification task maximizes the benefits of transfer learning to achieve high performance with minimum computational cost and complexity. Given its success in NLP tasks and the efficiency of transfer learning, BERT was the optimal choice for the AI content detection model.

Fig. 6. BERT Architecture [19]

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 487

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


<!-- Page 5 -->
B. Model Training and Fine-tuning

The decision to fine-tune the BERT model for the task of distinguishing AI-generated content from human-written text aligns with proven best practices in NLP, as demonstrated by Chi Sun et al. [21] who highlight BERT’s effectiveness in text classification tasks. Fine-tuning BERT involves adapting the pretrained model to the specific task by updating its weights using labeled data, where each text sample is classified as either Human or AI. A Sparse Categorical CrossEntropy has been used as loss function and the Adam optimizer with a learning rate of for efficient optimization. This way, the model’s weights are updated effectively by the gradients computed from the loss function. This has been proven to improve performance highly, with Chi Sun et al. reporting an average error rate reduction of 18.57% through further pretraining with the BERT-IDPT-FiT model.

Also, their work pointed out that fine-tuning the last layer of BERT, which happened to be the most promising layer for classification tasks is also necessary. This step-wise finetuning framework, that their work specifies, leaves a robust base to achieve an accuracy high enough, so this justifies the decision on fine-tuning BERT on the dataset. It is shown that on even the smallest datasets the model works well, but overcoming such challenges as catastrophic forgetting with the use of layer-wise decreasing learning rates ensures successful adaptation of BERT without an efficiency penalty. With chosen proper training parameters and finetuning of the model toward task-specific data, full capabilities of BERT had been taken advantage of towards getting the desired output regarding the AI content detection task.

C. Predicting AI Percentage

First, it passes the input text to the BERT model that outputs logits for every class. This further gets passed through the SoftMax function to derive a probability distribution over two classes. Then the AI percentage is calculated from the probability score generated by the AI class or label 1. Specifically, score multiplied by 100 to describe this probability as a percentage because the percentage represents the model’s confidence regarding that the text is AI-generated, and then one adds an appropriate threshold and generates the predicted label as shown in Fig. 7.

Fig. 7. Range of AI %

V. RESULTS AND DISCUSSION

Due to limitations in computational resources, prediction of AI content has been performed on 30% of the validation set that has been obtained from the Downsized Dataset.

Fig. 7 is the spread of AI percentage that has been obtained on the validation set with the range of 45.56% to 58.23% and the mean being 52.96%. The threshold determines if the input will be classified as AI generated or not needs to be optimized during training to minimize the type-I and type-II errors. There is a very fine relation between the threshold and the accuracy obtained with each change in the threshold. The interaction between the threshold and precision is related to how the threshold affects the classification between AI and Human. In general, a lower threshold (e.g., 30%) would classify more texts as AI because more texts would be labeled as AI, but this might lead to an increase in false positives and misclassify some of the actual human texts. Conversely, a higher threshold (e.g., 70%) will classify fewer texts as AI, thereby reducing false positives but potentially increasing the number of Human texts misclassified as AI (false negatives). Accuracy will depend on balancing the correct identification of both AI and Human texts while minimizing misclassifications. With changes in the threshold, the number of true positives, true negatives, false positives, and false negatives shifts, directly affecting the overall accuracy of the model. Error! Reference source not found. showcases the confusion matrix for the threshold value set as 47%.

While both DistilBERT and RoBERTa have gained recognition as lightweight and optimized transformer-based models, their performance in this specific task of AI content detection falls short when compared to BERT-Base-Uncased. DistilBERT, achieving a modest accuracy of 54.9%, as show in the confusion matrix in Error! Reference source not found. demonstrates noticeable shortcomings in its ability to distinguish between human written and AI-generated text effectively [11]. This can mainly be accounted to its architecture, a distilled version of BERT, which reduces the number of parameters and layers. While this decreases the representational depth, thus losing nuanced contextual understanding which full-scale BERT models hold onto, DistilBERT struggles with subtle linguistic cues and variance inherent in AI-generated content. This trade-off of computational efficiency for performance has proven painful in those applications in which precision and contextual sensitivity were highly critical, further sealing its inferior status in such scenarios. Similarly, RoBERTa, though it does get a slightly higher accuracy of 42.6% as shown in Error! Reference source not found., performs woefully compared to BERT-based-uncased. RoBERTa’s training process, which focuses much on heavy pretraining over large datasets and removes the next sentence prediction, typically results in it performing well on most NLP tasks. However, its dismal performance here does point out to its shortcomings when required to discern subtle inter-sentence relationships and stylistic features that distinguish human from AI writing. While RoBERTa tends to outperform BERT in most classification and language modeling benchmarks, its failure in this domain indicates that the dataset-specific demands, such as the detection of syntactic uniformity or irregularities from AI models, expose a gap in its pretraining optimization. These results thus reaffirm the robustness of BERT-BaseUncased, which strikes an ideal balance between parameterization and linguistic adaptability, outperforming these models significantly.

BERT model has been optimally fine-tuned to classify text as either human-written or AI-generated at a high accuracy level with respect to the distinction between categories. Use of BERT’s self-attention mechanism along with the necessary

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 488

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


<!-- Page 6 -->
preprocessing techniques ensured that this model is effective in capturing relationships within text.

(a)

(b)

(c)

Fig. 8. (a) Confusion Matrix for Threshold = 47% (b) Confusion Matrix

for DistilBERT (c) Confusion Matrix for RoBERTa

The overall performance of the models in terms of evaluation matrices, i.e., classification accuracy, precision, recall and F1-Score has been shown below in Error! Reference source not found. These results demonstrate BERT as a powerful tool for content classification and handling more complex text scenarios.

TABLE I. MODEL PERFORMANCE FOR THRESHOLD OF 47%

For RoBERTa 0.4255 0.4263 0.424 0.4255

VI. CONCLUSIONS AND FUTURE SCOPE Considering the strength of BERT in overcoming challenges like dataset imbalances and poor generalization, that makes it a more nuanced and accurate solution to the AI content detection problem, a systematic methodology has been developed to effectively detect, classify and analyse the AI-generated and human written content. Presented investigation demonstrated that an optimally fine-tuned BERT-based uncased model results in superior performance for detection, identification and classification of humanwritten content against AI-generated content including that using humanizer in comparison to RoBERTa and DistilBERT.

Since correct classification and type-I and type-II error largely depends on the selected threshold, same need to be optimized and updated regularly using updated authentic dataset. Presented scalable and efficient framework may be updated regularly in-line with developments in generative AI and humanizer, to maintain its performance in detection, classification, and analysis of plagiarism fueled by AIgenerated content and help in maintaining integrity of intellectual academic content.

REFERENCES

[1] M. Diviya and A. Karmel, “Review on technological advancement and

textual data management algorithms in NLP and CBIR systems,” In: Raje, R.R., Hussain, F., Kannan, R.J. (eds) Artificial Intelligence and Technologies. Lecture Notes in Electrical Engineering, vol 806. Springer, Singapore, 2021. doi: 10.1007/978-981-16-6448-9_32 [2] Vani K. and Deepa Gupta, “Study on extrinsic text plagiarism detection

techniques and tools”, Journal of Engineering Science and Technology Review, vol. 9, pp. 150-164, 2016, doi: 10.25103/jestr.094.23 [3] Vani K. and Deepa Gupta, “Text plagiarism classification using syntax

based linguistic features”, Expert Systems with Applications, vol. 88, pp. 448-464, 2017. doi: 10.1016/j.eswa.2017.07.006 [4] Vani K. & Deepa Gupta, "Integrating syntax‐semantic‐based text

analysis with structural and citation information for scientific plagiarism detection," Journal of the Association for Information Science & Technology, Association for Information Science & Technology, vol. 69(11), 2018, pages 1330-1345. https://ideas.repec.org/a/bla/jinfst/v69y2018i11p1330-1345.html [5] B. Premjith and Soman K. P., “Amrita_CEN_NLP @ WOSP 3C

Citation Context Classification Task”, in Proceedings of the 8th International Workshop on Mining Scientific Publications, Wuhan, China, Association for Computational Linguistics, 2020, pp. 71-74. https://aclanthology.org/2020.wosp-1.11/ [6] Tony Berber Sardinha, “AI-generated vs human-authored texts: A

multidimensional comparison,” Applied Corpus Linguistics, Vol. 4, no. 1, 2024, p. 100083. doi: 10.1016/j.acorp.2023.100083 [7] Ahmed M. Elkhatat, Khaled Elsaid and Saeed Almeer, “Evaluating the

efficacy of AI content detection tools in differentiating between human and AI-generated text,” Int. J. Educ. Integr., 19, 17, 2023. doi: 10.1007/s40979-023-00140-5.

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 489

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.


**Table (Page 6, #1)**:

| Model | Accuracy | Precision | Recall | F1- Score |
| --- | --- | --- | --- | --- |
| BERT-uncased For DistilBERT For RoBERTa | 0.723354 0.5473 0.4255 | 0.8019 0.5961 0.4263 | 0.605 0.545 0.424 | 0.69 0.5698 0.4255 |


<!-- Page 7 -->
[8] Niful Islam, Debopom Sutradhar, Humaira Noor, Jarin Tasnim Raya,

Monowara Tabassum Maisha, and Dewan Md Farid,” Distinguishing human generated text from ChatGPT generated text using machine learning,” arXiv, Jun. 2023. doi: 10.48550/arXiv.2306.01761 [9] Ethan Walker, Lucas Evans, Ava Mitchell, Zoe Zhang, Ryan Patel and

Isabella Chen, “Text classification in detection of AI generated content using BERT”, pre-print, 2024, doi: 10.13140/RG.2.2.30193.90722 [10] Yan Lai, and Lin Zhang, “Government affairs message text

classification based on RoBerta and TextCNN,” In proceedings of 2023 5th International Conference on Communications, Information System and Computer Engineering (CISCE), Guangzhou, China, 2023, pp. 258-262, doi: 10.1109/ISIEA61920.2024.10607351 [11] Slamet Riyadi, Ahmad Musthafa Masyhur, and Annisa Divayu

Andriyani, “Deep learning for hate speech intensity analysis: DistilBERT classification algorithm,” In proceedings of 2024 IEEE Symposium on Industrial Electronics & Applications (ISIEA), Kuala Lumpur, Malaysia, 2024, pp. 1-6, doi: 10.1109/ISIEA61920.2024.10607351 [12] Iyad Katib, Fatmah Y. Assiri, Hesham A. Abdushkour, Diaa Hamed

and Mahmoud Ragab, “Differentiating chat generative pretrained transformer from humans: detecting ChatGPT-generated text and human text using machine learning,” Mathematics, MDPI, vol. 11(15), pages 1-19, 2023. https://ideas.repec.org/a/gam/jmathe/v11y2023i15p3400d1210228.html [13] D. Dukić, D. Keča and D. Stipić, "Are You Human? Detecting Bots on

Twitter Using BERT," 2020 IEEE 7th International Conference on Data Science and Advanced Analytics (DSAA), Sydney, NSW, Australia, 2020, pp. 631-636, doi: 10.1109/DSAA49011.2020.00089

[14] Aachal Jakhotiya, Harshada Jain, Bhavik Jain, and Ms. Charmi

Chaniyara, “Text pre-processing techniques in natural language processing: A review,” Int. Res. J. Eng. Technol. (IRJET), vol. 9, no. 2, pp. 878, Feb. 2022, https://www.irjet.net/archives/V9/i2/IRJETV9I2150.pdf [15] Z. Jianqiang and G. Xiaolin, "Comparison Research on Text Pre-

processing Methods on Twitter Sentiment Analysis," in IEEE Access, vol. 5, pp. 2870-2879, 2017, doi: 10.1109/ACCESS.2017.2672677 [16] Shayan Gerami, “AI Vs Human Text, Version 8.82”. Retrieved

December 05, 2024. https://www.kaggle.com/datasets/shanegerami/aivs-human-text [17] Arjun Srinivas Nayak, Ananthu P Kanive, Naveen Chandavekar, and

Balasubramani R, “Survey on pre-processing techniques for text mining”, int. jour. eng. com. sci, vol. 5, no. 6, 2016. https://www.ijecs.in/index.php/ijecs/article/view/2019 [18] Jacob Devlin, Ming-Wei Chang, Kenton Lee and Kristina Toutanova,”

BERT: Pretraining of deep bidirectional transformers for language understanding,” arXiv, 24 May 2019. doi: 10.48550/arXiv.1810.04805 [19] Miguel Romero Calvo, “Dissecting BERT Part 1: The Encoder”, Nov

27 2018, Retrieved December 05, 2024, https://medium.com/dissecting-bert/dissecting-bert-part-1d3c3d495cdb3 [20] Patrick Xia, Shijie Wu, and Benjamin Van Durme, “Which *BERT? A

survey organizing contextualized encoders,” In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), Association for Computational Linguistics, 2020, pp 7516–7533. doi: 10.18653/v1/2020.emnlp-main.608 [21] Chi Sun, Xipeng Qiu, Yige Xu, and Xuanjing Huang,”How to fine-tune

BERT for text classification?” arXiv, 5 Feb 2020 (v3). doi: 10.48550/arXiv.1905.05583

Proceedings of the Third International Conference on Augmented Intelligence and Sustainable Systems (ICAISS-2025) IEEE Xplore Part Number: CFP25CB2-ART; ISBN: 979-8-3315-0724-4

979-8-3315-0724-4/25/$31.00 ©2025 IEEE 490

Authorized licensed use limited to: Mukesh Patel School of Technology & Engineering. Downloaded on October 31,2026 at 08:16:59 UTC from IEEE Xplore. Restrictions apply.

