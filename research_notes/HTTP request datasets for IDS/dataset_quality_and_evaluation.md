# HTTP-request / web-attack IDS datasets: usage, quality problems, cross-dataset generalization, and fair evaluation (literature 2020–2026)

Status: compiled 2026-10-17. "Peer-reviewed" means journal or conference proceedings; "preprint" means arXiv-only as far as I could verify. Metrics are as the authors report them. Almost none of the high scores below come from leakage-controlled (group/near-duplicate-aware) splits, so they cannot be compared directly with the project's numbers (RF v2 test F1 70.05%, false-alarm rate 29.00%, ROC AUC 0.765 on 199 CSIC 2010 requests, group-aware split; source: project README).

## Q1. Which datasets do 2020–2026 HTTP/web-attack detection papers actually use? (paper → datasets → reported metrics)

### Takeaway
CSIC 2010 is by far the most common public HTTP-request benchmark. It is followed at a distance by ECML/PKDD 2007, and since about 2022 by SR-BH 2020. Private or self-collected datasets are even more common than any public one. Newer transformer/LLM papers (2024–2026) shift toward SR-BH 2020 and CSIC, nearly always with random splits, and report F1 in the 96–99.9% range.

### Cited Findings
**Dataset-usage counts from systematic reviews**
- Alaoui & Nfaoui SLR (Future Internet 2022, peer-reviewed; 63 DL primary studies, 2010–Sep 2021): "37 studies used private datasets, 29 studies used the CSIC-2010 dataset, three studies used the ECML/PKDD 2007 dataset, two studies used KDD-Cup99, six studies use the CICIDS 2017 dataset, and six studies used publicly available datasets not very commonly used (e.g., xssed.com, Apache 2006/2017, HttpParams)" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118)
- Same SLR: CICIDS-2017 "contains only 2180 web attacks instances, which means it is insufficient for evaluating a web attacks detection model" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118)
- Sureda Riera et al. systematic review (Sustainability 2020, peer-reviewed; 88 papers out of 8,041 screened): public-dataset usage was CSIC 2010 in 13 studies, KDD-Cup 99 in 8, DARPA in 4, NSL-KDD 2, UNSW-NB15 2, Kyoto 2006 2, ISCX 1, ECML/PKDD 2007 1. "Only 26 (29.55%) of the 88 papers include public datasets... The rest (70.45%) include private, synthetic or unspecified datasets, making it impossible to replicate the experiments" — [Sureda Riera et al. 2020](https://doi.org/10.3390/su12124945)
- Damayanti et al. (ICITISEE 2024, peer-reviewed conference; 37 papers, 2020–2024): reviewed works used "92 public datasets and 8 private datasets" (dataset-instance counts). The most common models were CNN (9 papers), RF and SVM (8 each), and LSTM (7). The abstract gives no per-dataset breakdown — [Damayanti et al. 2024](https://ir.lib.ugm.ac.id/id/eprint/13508/)
- HTTP2vec authors: CSIC2010 "is the dataset most often used in similar problems, as it contains ready-to-use text files with HTTP requests"; "Most of the research is based only on one CSIC2010 dataset and other self-prepared data" — [Gniewkowski et al. 2021 (preprint)](https://arxiv.org/abs/2108.01763)
- Aharon et al.: "Many research efforts rely solely on the CSIC 2010 dataset", which raises reliability and generalizability concerns — [Aharon et al. 2024 (preprint)](https://arxiv.org/abs/2405.11247)

**Paper → datasets → metrics (2020–2026)**

| Paper (status) | Datasets | Split / protocol | Reported result |
|---|---|---|---|
| [HTTP2vec, Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763) (preprint) | CSIC2010; CSE-CIC-IDS2018 web subset; UMP (own, real benign + Arachni attacks) | RoBERTa embeddings + LR/SVM/RF, 5-fold CV | CSIC F1 96.9% (SVC), FPR99 4.2%; UMP F1 about 92.6%; CIC-IDS2018 F1 about 99.9% |
| [Sivri et al., FedCSIS 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf) (peer-reviewed conf.) | CSIC 2012 (TORPEDA, "over 74000 requests", artificial) + ECML/PKDD 2007, merged | Train/val/test + 5-fold CV; CSIC normal upsampled 2–8× by swapping in ECML header values | Accuracy/F1 up to about 0.99 (LSTM; e.g., F1 0.9927 on the 8× upsampled set) |
| [Riverol, Betarte, Martínez, Pardo, LADC 2024](https://arxiv.org/abs/2407.18445) (peer-reviewed conf.) | DRUPAL (real university site), SR-BH 2020 attacks, PKDD 2007 attacks | One-class SVM over expert-selected token features | Drupal: TPR 91.76%, FPR 2.29%, AUC 0.97 (100 features), vs ModSecurity best TPR 75% with FPR 39.69% |
| [ModSec-Learn, Scano et al.](https://arxiv.org/abs/2406.13547) (arXiv v2 Sep 2026) | Benign: 508,529 requests from open-appsec; SQLi: 30,543 from HTTP Params, Kaggle, SQLmap | Random balanced 25k/25k; train 20k/20k | Detection improves >45% at 1% FPR over vanilla CRS (TPR at 1% FPR) |
| [Aharon et al. 2024](https://arxiv.org/abs/2405.11247) (preprint) | CSIC 2010, ATRDF 2023 | Per-endpoint few-shot retrieval; trained on 36,000 normal | CSIC F1 0.9713 (FT-ANN); ATRDF F1 1.0 |
| [Babaey & Faragardi 2025](https://arxiv.org/abs/2504.14122) (preprint) | "CSIC 2012" (labelled "CSIC" in places) | Autoencoder ensemble trained on 80% of normal; test set 1,299 normal vs 50,174 malicious | F1 98.74%, FPR 0.2% |
| [WADBERT, Luo et al. 2026](https://arxiv.org/abs/2601.21893) (preprint) | CSIC2010 (36,000 benign / 21,065 malicious); SR-BH2020 after "manual validation and deduplication" (161,334 / 345,942) | 70/30 split, no stated stratification or grouping | F1 99.63% (CSIC), 99.50% (SR-BH); baselines DistilBERT 98.99%, CNN-BiLSTM 96.00% on CSIC |
| [WAMM, Osama et al. 2025](https://arxiv.org/abs/2512.23610) (preprint, Cyshield) | SR-BH 2020 plus three refined/augmented versions | Stratified 80/20 | SRBH-Original: XGBoost macro-F1 96.77%, DistilBERT 85.47%, BiLSTM 77.11%; DS-Augmented-v1: XGBoost 77.61%, DL models ≈50–51% |
| [X-WAD 2026](https://arxiv.org/abs/2608.27172) (preprint) | SR-BH2020 and a label-fixed "SR-BH2020-fix" | Trained on normal only (70/20/10); test = 10% normal + all anomalies | Original: ModernBERT F1 86.16% (FPR 1.68%), SmolLM2-360M F1 91.31%; fixed: 98.29% / 98.84% |
| [ADL-WAF, Sameh & Selim](https://arxiv.org/abs/2511.12643) (preprint) | CSIC2010, HttpParams (anomaly layer); HttpParams, ECML, XSS (threat layer); "real application" set of 30,690 for testing | not detailed in my read | Accuracy 99.88% |
| [Biblio-US17, Díaz-Verdejo et al., Cybersecurity 2025](https://doi.org/10.1186/s42400-024-00336-3) (peer-reviewed) | Biblio-US17 (real, 47M URIs) | dataset paper with a simple anomaly-detector example | — |
| [SR-BH 2020, Sureda Riera et al., Computers & Security 2022](https://doi.org/10.1016/j.cose.2022.102788) (peer-reviewed) | SR-BH 2020 (multi-label, CAPEC) | dataset paper; LightGBM/CatBoost multi-label | — |

- Prior CSIC results as tabulated by Babaey & Faragardi (cited from those papers): Vartouni et al. accuracy 88.32% / F1 84.12%; Liang et al. 98.42% acc / FPR 0.7%; Kuang et al. 96% acc / FPR 2%; Shahid et al. 98.73% acc / FPR 1.67% / F1 99.13%; Moarref et al. 99.36% acc / F1 99.22% — [Babaey & Faragardi 2025](https://arxiv.org/abs/2504.14122)
- A semi-supervised frozen-BERT + autoencoder paper (EURASIP J. Information Security 2025) reportedly gives F1 1.00 with zero FPR on CSIC2010, but also F1 0.98 elsewhere in the same paper (seen only through search snippets; internally inconsistent) — [Springer 2025](https://link.springer.com/article/10.1186/s13635-025-00210-w)
- LLM-WAF (IJWMT) claims 96.8% accuracy and F1 0.95 on CSIC 2010 plus "real-world traffic". I saw only the listing, not the paper — [MECS Press](https://www.mecs-press.org/ijwmt/ijwmt-v16-n4/v16n4-18.html)

### Inferences
- For a fair comparison, CSIC 2010 is unavoidable (it is the lingua franca). SR-BH 2020 is the most used "realistic" alternative in 2024–2026 transformer/LLM work, and ECML/PKDD 2007 is the usual second public set in older and feature-based work.
- Reported CSIC F1 values cluster at 96–99.9% for supervised models on random splits. Unsupervised or one-class models trained only on normal data (the dataset's original protocol) report noticeably lower numbers (for example F1 84.12% for Isolation Forest).
- Dataset counts are inconsistent across papers (CSIC anomalous: 25,065 in the official files vs 21,065 in WADBERT). A paper's exact subset and version must be stated before its numbers are compared.

### Gaps
- No 2020–2026 survey with a per-dataset usage count limited to HTTP request-level work. The Alaoui (to 2021) and Sureda Riera (to about 2019) counts are the best available. Full texts of the 2025 IJEECS review and the 2026 XAI systematic review (Artificial Intelligence Review) were not accessible.
- I could not verify Sec2vec (ACM SAC 2023) numbers first-hand, nor any peer-reviewed LLM-WAF result on CSIC.

## Q2. Documented flaws of CSIC 2010, ECML/PKDD 2007, SR-BH 2020 and other HTTP datasets

### Takeaway
Every major public HTTP dataset has a documented flaw that can either inflate or cap scores:
- CSIC 2010 is synthetic, covers a single application, has near-constant headers, uses an "anomalous" class that includes non-malicious "unintentional illegal" requests, and carries a line-ending artifact.
- ECML/PKDD 2007 has obfuscated, never-repeating parameter values that make it artificial for value modeling.
- SR-BH 2020 has heavy label noise (5–14% depending on the estimate) and extreme benign redundancy.
- CSE-CIC-IDS2018 web traffic has trivially separable Host, URI and header artifacts.

### Cited Findings
**CSIC 2010**
- The "anomalous" class contains many non-attacks. Records from the two classes are similar, and "most of the anomalous requests which overlap with normal requests actually have no malicious payload". These are "unintentional illegal requests" that "lack malicious intent" (for example an invalid Spanish national ID). 8 of 38 endpoints have no normal representation — [Aharon et al. 2024 (preprint)](https://arxiv.org/abs/2405.11247)
- Line-ending artifact: "each anomalous request ended with a '\n' character and not '\r\n'. It is intriguing how many other researchers also faced this issue" — [Gniewkowski et al. 2021 (preprint)](https://arxiv.org/abs/2108.01763)
- Narrow header diversity: "ECML has an excessive amount of unique values in both attack and normal requests. On the contrary, CSIC has a narrow range of unique values". Their Table I shows single-valued CSIC headers such as Accept-Charset. The authors upsampled CSIC normal requests by swapping in ECML header values — [Sivri et al. 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf)
- Single domain, limited attacks: "The dataset contains traffic only to a single domain from a single computer, and the number of types of attack is very limited. It, therefore, allows assessment of accuracy only on individual URLs" — [Nested MIL paper, arXiv 2002.04059](https://arxiv.org/pdf/2002.04059)
- Generated traffic for one e-commerce application; an "automatically generated dataset" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118); [Sureda Riera et al. 2020](https://doi.org/10.3390/su12124945)
- Missing fields: "the CSIC 2010 dataset had restrictions that prevented some features from being retrieved, such as the lack of cookie-length data" (summarizing Sharma et al.) — [ADL-WAF (preprint)](https://arxiv.org/abs/2511.12643)
- Outdated: CSIC 2010 "lacks the complexity and evolving attack patterns characteristic of modern cybersecurity threats". This claim is uncited in the paper — [Babaey & Faragardi 2025 (preprint)](https://arxiv.org/abs/2504.14122). "Many studies relied on outdated datasets such as CSIC2010 and its derivatives" — [WAMM (preprint)](https://arxiv.org/abs/2512.23610)
- Prior CSIC results are reported inconsistently. In Babaey & Faragardi's comparison table, several CSIC 2010 studies give only accuracy/F1 with no FPR (e.g., Vartouni et al., Moarref et al.), and supervised results cluster at 96–99% accuracy — [Babaey & Faragardi 2025](https://arxiv.org/abs/2504.14122)

**ECML/PKDD 2007**
- Obfuscation artifact: "some process of obfuscation/anonymization was executed on the dataset... no URI, parameter name or value appears twice in the dataset. As a consequence, the ECML/PKDD 2007 dataset revealed useless for carrying on n-gram analysis". The random values use letters, numbers, "=" and "−", "so specific and different from the normal traffic... that the generic approach did not work" (2018, foundational) — [Betarte et al. 2018](https://arxiv.org/abs/1803.05529)
- 35,006 normal and 15,110 attack requests. Collected from real traffic, then processed "to mask parameter names and values—replacing them with random values" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118)
- "Although the data quality is lower" than SR-BH 2020, PKDD is still useful as a source of varied attack types — [Riverol et al. 2024](https://arxiv.org/abs/2407.18445)

**SR-BH 2020** (12-day Internet-exposed honeypot, WordPress; 13 labels / 12 CAPEC categories — [Riverol et al. 2024](https://arxiv.org/abs/2407.18445); [Sureda Riera et al. 2022](https://doi.org/10.1016/j.cose.2022.102788))
- Label noise in the benign class (WAMM): regex fingerprinting flagged CMDi 16,740 (3.35% of benign), SQLi 20,800 (4.16%), Path Traversal 8,000 (1.6%), SSTI 2,500 (0.5%) and XSS 2,335 (0.47%). An LLM (Qwen3-8B) pass found "48,522 malicious requests incorrectly labeled as benign". On 300+ samples, expert manual review agreed 100% with the LLM classification — [Osama et al. (WAMM, preprint)](https://arxiv.org/abs/2512.23610)
- Unusable categories (WAMM): HTTP Request Smuggling samples lack Content-Length/Transfer-Encoding headers; dictionary password attacks are "indistinguishable from normal login HTTP requests"; HTTP verb tampering "relied on response content rather than request-based indicators"; the CAPEC-194 class actually contained SSRF; CMDi (CAPEC-248) had a single entry — [WAMM](https://arxiv.org/abs/2512.23610)
- Redundancy: "LSH was used to remove about 519K redundant benign payloads" (out of 525,195 benign) — [WAMM](https://arxiv.org/abs/2512.23610). WADBERT's exact/manual dedup instead kept 161,334 benign and 345,942 malicious — [WADBERT](https://arxiv.org/abs/2601.21893). The two dedup criteria differ, so the remaining sizes conflict.
- A second independent estimate: "approximately 13.8% of the dataset is mislabeled" (attacks labelled normal). Fixing labels raised ModernBERT F1 from 86.16% to 98.29% — [X-WAD 2026 (preprint)](https://arxiv.org/abs/2608.27172). This conflicts in magnitude with WAMM's 48,522 (≈5.3% of all rows, ≈9.2% of benign).

**CSE-CIC-IDS2018 (web subset) and self-built sets**
- The attacks came from a single DVWA host, so "Every 'Host' field... pointed to a single IP address", URIs start with "/DVWA...", and "Every anomalous request contained 'Upgrade-Insecure-Requests' header". The authors had to rewrite these to "avoid spurious correlations". Even after that, "Accept" and "Accept-Encoding" lines remained near-perfect class predictors ("This is why we obtained such excellent results") — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- In their own UMP set, Arachni-generated attacks "had very similar headers and nearly no payloads", so only request first lines were used "to avoid oversimplification" — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- The flow-level CIC-IDS2017 is outside HTTP-request scope but is the canonical example: more than 25% of flows were meaningless artefacts, rising to 50% for some attack classes, and the problem persists in CSE-CIC-IDS2018 — [Engelen, Rimmer & Joosen, IEEE S&P Workshops 2021](https://lirias.kuleuven.be/retrieve/713070)
- Flood et al. identify six "data design smells" in seven benchmark NIDS datasets, which "can introduce severe experimental bias" — [Flood et al., IEEE EuroS&P 2024](https://ieeexplore.ieee.org/document/10629000). A 2026 survey summarizes them as limited feature diversity, high feature interdependence, ambiguous ground truth, collapse of traffic distributions, artificial diversity generation, and labeling inaccuracies — [arXiv 2602.05594](https://arxiv.org/pdf/2602.05594)

**Cross-cutting critiques**
- Public datasets "are outdated and simplistic... do not reflect the complexity of real-world web applications". Researchers "use different portions and apply different pre-processing techniques, which results in different versions of the same dataset", and "a dataset with many duplicated instances results in biased accuracy" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118)
- Recurring issues: "label noise and redundancy undermine ground truth, synthetic traffic produces unrealistic distributions that miss multi-vector campaigns, and narrow coverage excludes critical classes such as web shells" — [WAMM](https://arxiv.org/abs/2512.23610)
- General ML-security pitfalls (USENIX Security 2022, Distinguished Paper; 30 top-venue papers). Sampling bias (P1) and data snooping (P3) are at least partly present in 90% and 73% of papers. Spurious correlations (P4): "Artifacts unrelated to the security problem create shortcut patterns for separating classes". Label inaccuracy (P2), base-rate fallacy (P8) and lab-only evaluation (P9) are also covered. "Every paper is affected by at least three pitfalls" — [Arp et al. 2022](https://arxiv.org/abs/2010.09470)

### Inferences
- CSIC's near-constant headers mean header-derived features in the project's 21 can carry little class signal. Header features can still pick up artifacts such as the CRLF line ending, if body or line-ending handling is exposed to them. The useful signal sits in path, query and body values.
- The "unintentional illegal request" sub-population of CSIC's anomalous class is semantically, not syntactically, anomalous. Length and special-character features will tend to miss it. This is a structural ceiling for generic hand-crafted features (see Q6).
- SR-BH 2020 should not be used as-is. Either adopt a published cleaned version (if released) or apply one's own label audit, and report which one was used.

### Gaps
- I found no paper that quantifies exact or near-duplicate rates inside CSIC 2010 (searches returned nothing CSIC-specific). The 25,065 vs 21,065 anomalous count discrepancy (official vs WADBERT) hints at dedup or subset effects but is unexplained.
- I could not access the full text of the Díaz-Verdejo et al. critical review (Computers & Security 2023), which likely contains the most systematic HTTP-dataset critique (ScienceDirect returned 403).
- The official CSIC page (tic.itefi.csic.es) refused connections, so the license and the exact definitions of the anomalous sub-types could not be re-verified first-hand.

## Q3. Cross-dataset generalization: train on one HTTP dataset, test on another

### Takeaway
Explicit cross-dataset HTTP experiments are rare, but the few that exist show severe degradation. In the starkest result, a Random Forest went from TPR 1.00 / FPR 0.00002 in training to TPR 0.22 on the protected application. Authors conclude that supervised models trained on one application or dataset do not transfer. One-class models of normal traffic transfer somewhat better. No paper I found reports a clean CSIC→PKDD or CSIC→SR-BH F1 matrix.

### Cited Findings
- Riverol et al. trained a Random Forest (n_estimators=100) on generic attacks plus valid application data. It "produced a good performance in training (FPR: 0.00002, TPR: 1.00) but when evaluated with validation data of the application to be protected, the accuracy decreased significantly (FPR: 0.0161, TPR: 0.22)... the model cannot generalize to new data and is ineffective in real environments". The same group states that "training the model with generic data sets and testing it with application-specific data, has revealed that classifiers built this way do not generalize well... a model trained for one application cannot be directly applied to protect a different one" — [Riverol et al., LADC 2024](https://arxiv.org/abs/2407.18445)
- Earlier work, likely by the same Uruguayan group (search snippet only; attribution to this exact paper not verified): "even using the same features they could not obtain good performance scores when applying the model trained for PKDD2007 and then tested using DRUPAL... the classifier designed for one dataset cannot be used in other ones" — [Betarte et al. 2018 (ICMLA), ResearchGate](https://www.researchgate.net/publication/329514915_Web_Application_Attacks_Detection_Using_Machine_Learning_Techniques)
- One-class models were trained on "generic training data, that is, using a dataset with request not from the web application to protect". For CSIC 2010 and DRUPAL the authors found "the degradation with respect to the same classifier trained with specific data for the web application is not critical". For ECML/PKDD the generic model failed because of the obfuscation artifact — [Betarte et al. 2018](https://arxiv.org/abs/1803.05529)
- Feature selection does not transfer: CSF-based selection worked well on CSIC 2010 while mRMR worked better on ECML/PKDD 2007 (search-level summary of an older analysis) — [Althubiti et al., KSU](https://digitalcommons.kennesaw.edu/cgi/viewcontent.cgi?httpsredir=1&article=1053&context=ccerp)
- WAMM: "When trained and tested on similar technology stacks, model performance remains optimal. However, different technologies may require separate models or additional fine-tuning to achieve comparable accuracy". Its DL models dropped from about 75–85% macro-F1 to about 50% on a Burp-augmented variant, showing "sensitivity to distributional shifts" — [WAMM](https://arxiv.org/abs/2512.23610)
- HTTP2vec claims its models "generalize to new data, as we successfully discovered anomalies in real" traffic, but this is qualitative, not a cross-dataset metric — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- Analogous flow-level evidence: with the XeNIDS cross-evaluation framework (6 datasets), ML-NIDS F1 "drops by 20% against botnet attacks of diverse datasets; even worse, it is unable to detect DoS attacks (F1-score of 38%)". This "could only be assessed via cross-evaluations". Adding the other datasets' malicious samples restored F1 to 99% — [Apruzzese, Pajola & Conti, IEEE TNSM (arXiv 2203.04686)](https://arxiv.org/abs/2203.04686)
- Verkerken et al. report "a substantial average drop in detection performance under cross-dataset evaluation" for unsupervised NIDS (as cited by a 2026 IIoT paper) — [arXiv 2607.00553](https://arxiv.org/pdf/2607.00553)

### Inferences
- The project should expect a sharp drop, not a modest one, if a CSIC-trained RF is scored on modsec-learn, SR-BH or the team's ModSecurity logs. Expected FPR inflation is especially large, because CSIC's benign distribution (a single Spanish e-shop) is narrow.
- A cross-dataset matrix (train A → test B for every pair, plus within-dataset group splits) would be a genuine contribution, since the literature lacks one at the HTTP-request level.

### Gaps
- No quantitative CSIC↔ECML/PKDD↔SR-BH transfer matrix with F1/FPR found in 2020–2026 literature. The best quantitative evidence is Riverol et al. (TPR 1.00 → 0.22).
- The full text of the 2018 Betarte et al. ICMLA paper (PKDD→DRUPAL numbers) was not accessible.

## Q4. Recommended practices for combining multiple HTTP datasets (schema, dedup, labels, dataset-identity leakage)

### Takeaway
No HTTP-specific standard exists, but a consistent set of practices emerges:
- Normalize to a common schema built from the intersection of fields.
- Strip or randomize source-identifying fields (Host, URI prefixes, header sets, line endings, IP and port).
- Deduplicate structurally (MinHash/LSH) before splitting.
- Remap labels to an explicit shared taxonomy and verify with manual audit.
- Keep both classes from the same source/context, or inject payloads into the same benign context. Otherwise the model learns which dataset a request came from.

### Cited Findings
- Schema normalization: bring all datasets "into a common... format", establish "a common feature set (taken from the intersection of the features across all D) while simultaneously removing network artifacts that may lead to overfitting". If artifact-free standardization of a field (such as IP address) is impossible, "we suggest not to use any IP-related feature" — [Apruzzese et al. (XeNIDS)](https://arxiv.org/abs/2203.04686)
- Dataset/environment identity is a named threat: the "malicious traffic of a given dataset may be entirely produced by just few machines. Neglecting these issues may result in ML models that distinguish legitimate from anomalous samples on the sole basis of the IP address" — [Apruzzese et al.](https://arxiv.org/abs/2203.04686). Arp et al. P4 gives the same IDS example: "The model may learn to detect a specific IP range instead of generic attack patterns" — [Arp et al. 2022](https://arxiv.org/abs/2010.09470)
- HTTP-specific artifact scrubbing, concretely:
  - Host values: "randomly change that to any value that appeared in the normal dataset".
  - Source-specific URI prefixes: remove them (e.g., "/DVWA/...").
  - Attack-only headers (Upgrade-Insecure-Requests): remove them.
  - Tool-generated attacks with uniform headers: restrict to request lines.
  — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- Header/field harmonization when merging CSIC 2012 and ECML/PKDD:
  - Keep a fixed common header set (User-Agent, Accept, Accept-Charset, Accept-Encoding, Accept-Language, Content-Length, Content-Encoding, Cookie) plus method, URL and body.
  - Map labels to binary (normal 0 / any anomalous or attack 1).
  - Lowercase everything.
  - Explicit aim: "we have generalized the headers that appear only in attacks or only in normal requests".
  — [Sivri et al. 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf)
- Deduplication and label repair pipeline:
  - Structural near-duplicate removal via MinHash + LSH (datasketch), which removed about 519K redundant benign payloads.
  - LLM relabeling (about 48K labels corrected).
  - Expert spot-check of 300+ samples.
  - "Taxonomy update... mapping rules" to OWASP-aligned classes.
  - Dropping classes that are not identifiable from the request alone.
  — [WAMM](https://arxiv.org/abs/2512.23610)
- Same-context injection: the Hybrid 2020 dataset "was created by converting known valid requests from both the ECML/PKDD 2007 and the CSIC 2010 datasets to malicious type" using PayloadsAllTheThings payloads (search-level; full text not parsed) — [JCSANDM paper](https://journals.riverpublishers.com/index.php/JCSANDM/article/download/2263/5081/21237)
- Mixing benign from one source with attacks from another is the setup in which Riverol et al. observed TPR collapse from 1.00 to 0.22 on the target application. Their workaround was a one-class model on application-specific normal traffic plus generic attacks used only for feature selection — [Riverol et al. 2024](https://arxiv.org/abs/2407.18445)
- Several recent datasets have source-mismatched classes by construction:
  - ModSec-Learn: benign from open-appsec (508,529), SQLi from HTTP Params, Kaggle and SQLmap — [Scano et al.](https://arxiv.org/abs/2406.13547)
  - WAMM: benign "enriched with legitimate requests from platforms such as Facebook, Amazon, and Medium", attacks generated by Burp Suite scans — [WAMM](https://arxiv.org/abs/2512.23610)
- Label definitions differ across sources. CSIC "anomalous" includes non-malicious unintentional illegal requests ([Aharon et al. 2024](https://arxiv.org/abs/2405.11247)), whereas SR-BH uses CAPEC multi-labels ([Sureda Riera et al. 2022](https://doi.org/10.1016/j.cose.2022.102788)). Ring et al.'s "Labeled" property distinguishes "yes (IDS)" labels, which "might be wrong since an IDS might be imperfect" — [Ring et al., Computers & Security 2019](https://arxiv.org/abs/1903.02460)
- Data snooping (P3) covers test, temporal and selective snooping. Normalization or feature-fitting on the full data before splitting counts as snooping — [Arp et al. 2022](https://arxiv.org/abs/2010.09470)
- The upsampling-by-header-swap approach (copies of CSIC normal requests with ECML headers, 2–8×) was followed by random train/val/test and K-fold splitting — [Sivri et al. 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf)

### Inferences
- Sivri et al.'s augmentation creates near-duplicates that can land on both sides of a random split. Their about 0.99 scores are therefore likely optimistic, which is exactly the leakage the project's content grouping prevents.
- A practical dataset-identity leakage test for the project: train a classifier to predict source dataset (CSIC vs modsec-learn vs SR-BH) from the same 21 features. High accuracy means the features encode source. Then report (a) within-source group-split results, (b) leave-one-dataset-out results, and (c) a "both classes from one source" control.
- For modsec-learn (benign only from open-appsec, SQLi from other tools), the cleanest use is as cross-test benign traffic (an FPR check) or as SQLi-only recall, not as a merged binary training set.

### Gaps
- No HTTP-request-specific published guideline (equivalent to XeNIDS for flows) on schema harmonization and dataset-identity leakage. The practices above are assembled from scattered papers.
- No paper found that empirically measures "dataset-of-origin" predictability for HTTP datasets.

## Q5. Benchmark-quality criteria proposed by surveys; which datasets they recommend

### Takeaway
Surveys converge on several criteria:
- Real (not synthetic) normal traffic at realistic attack base rates.
- Recency and attack diversity.
- Reliable, documented labeling (preferably expert-verified).
- Sufficient size and duration, to allow time-aware and data-shift studies.
- Predefined splits, metadata and documentation.
- Public availability, with privacy handled through anonymization.

No survey endorses CSIC 2010 as sufficient. The recommendations point to building or adopting real-traffic datasets (Biblio-US17; a cleaned SR-BH 2020; application-specific captures), alongside common evaluation frameworks.

### Cited Findings
- Ring et al. (Computers & Security 2019; foundational, network-level) propose 15 properties in five groups:
  - General information: year of creation, public availability, normal user behaviour, attack traffic.
  - Nature of the data: metadata, format, anonymity.
  - Data volume: count, duration.
  - Recording environment: kind of traffic, type of network, complete network.
  - Evaluation: predefined splits, balanced, labeled.
  On predefined splits: "it must be clarified whether the same subsets are used for training and evaluation". Ring et al. regard Labeled and Format as the most important properties. CSIC 2010 is mentioned only as an example of a non-network-based dataset — [Ring et al. 2019](https://arxiv.org/abs/1903.02460)
- Alaoui & Nfaoui key findings: "(i) It is fundamental to generate standard real-world web attacks datasets"; "(iv) It is important to create a corpus for web attacks detection"; "(v) It is essential to define a common framework for developing and comparing DL-based web attacks detection models" — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118)
- Sureda Riera et al. stress that a reproducible framework requires "one or more datasets with updated normal and attack records". Public data are scarce "due to the data's sensitive nature", and "activity found in a small laboratory network cannot be generalized to larger scale network" — [Sureda Riera et al. 2020](https://doi.org/10.3390/su12124945)
- Díaz-Verdejo et al. critical review (Computers & Security 2023, vol. 124, 102997): proposes a common-steps framework and taxonomy for HTTP anomaly detection. It argues the field is held back because papers are "isolated contributions" whose results cannot be generalized (abstract-level; full text inaccessible) — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167404822003893)
- Biblio-US17 (Cybersecurity 2025, CC BY):
  - Size and scope: 47 million records over 6 months from a University of Seville public website. Each record holds the method, URI, response code and size.
  - Labeling: a semi-automated process combining "signature-based detection, assisted inspection of URIs vocabulary, and substantial expert manual supervision".
  - Positioning: "a genuine real-world perspective... along with an unbiased proportion of actual attacks (i.e., non-synthetic)", whose "size and duration also make it valuable for addressing challenges like data shift".
  — [Díaz-Verdejo et al. 2025](https://doi.org/10.1186/s42400-024-00336-3). Another version reports about 320k attacks — [ACM EICC 2024 version](https://dl.acm.org/doi/fullHtml/10.1145/3655693.3661319)
- The same group, on a real large-scale URI dataset, shows "significant limitations in the performance metrics commonly used to select the system's operating point and its practical use in real-world scenarios" — [Díaz-Verdejo et al., EICC 2024](https://doi.org/10.1145/3655693.3655745)
- Arp et al. recommendations relevant to benchmarks: report metrics suited to class imbalance (P7) and account for the base rate (P8; "even a very low false-positive rate can result in surprisingly high numbers of false positives"). Avoid lab-only evaluation (P9); 92% of surveyed authors agreed lab-only evaluation is frequent — [Arp et al. 2022](https://arxiv.org/abs/2010.09470)
- Realistic operating points are reported as TPR at a fixed low FPR, e.g., "1% FPR because it is a reasonable value commonly adopted in the literature" — [Scano et al. (ModSec-Learn)](https://arxiv.org/abs/2406.13547)
- A real-traffic baseline for scale: on real Drupal traffic, ModSecurity CRS had an FPR of 39.69% vs 2.29% for a one-class model — [Riverol et al. 2024](https://arxiv.org/abs/2407.18445)
- Coverage gap: common HTTP datasets omit families such as PHP web shells (WAMM summarizing Li et al. 2019) — [WAMM](https://arxiv.org/abs/2512.23610)

### Inferences
- Applied to the project's candidates:
  - CSIC 2010 fails on realism, recency and label semantics, but scores on availability and comparability.
  - ECML/PKDD fails on realism of values (obfuscation).
  - SR-BH 2020 scores on realism (honeypot) and size but fails on labeling.
  - modsec-learn has real benign traffic but source-mismatched, SQLi-only attacks.
  - Biblio-US17 scores best on realism and labeling but is URI-only (no headers or body), so only the path/query subset of the project's 21 features applies.
- A fair evaluation report for the project should include: confusion matrix; FPR and TPR at a fixed low FPR (e.g., 1%); ROC/PR AUC; the base-rate implication; dataset version and subset; split method; and a dedup/grouping description.

### Gaps
- Licensing and terms of use for CSIC 2010, ECML/PKDD 2007 and SR-BH 2020 were not verifiable from reachable pages. Biblio-US17's journal paper is CC BY, but the dataset's own access terms were not confirmed.
- No HTTP-specific scored checklist (dataset × criteria) was found in 2020–2026 surveys. Ring et al.'s scheme is network-level.

## Q6. Why a feature-based model on CSIC 2010 may plateau around F1 70%, and what is typical under proper splits

### Takeaway
The headline 96–99.9% CSIC F1 numbers come almost entirely from supervised models on random splits (often with deep sequence models over raw characters, sometimes with artifacts or augmentation leakage). Under the dataset's original protocol, unsupervised or one-class models report roughly 71–94% accuracy and 82–89% F1. I found no paper reporting CSIC results with group-aware, near-duplicate-controlled splits.

The project's 70% F1 / 29% false-alarm rate is plausible for 21 generic hand-crafted features on 1,000 requests, for four reasons:
- CSIC's "anomalous" class contains non-malicious, syntactically normal-looking requests.
- Headers carry almost no signal.
- Grouping removes the template memorization that random splits reward.
- The training set is small.

### Cited Findings
- Lower results under normal-only or unsupervised protocols:
  - Isolation Forest (Vartouni et al.): F1 84.12% — [Babaey & Faragardi 2025](https://arxiv.org/abs/2504.14122); [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
  - AE-LSTM with Isolation Forest: F1 81.96% (search-level) — [Babaey & Faragardi 2025](https://arxiv.org/html/2504.14122)
  - Haruta et al. ASCII autoencoder: accuracy 0.71; fastText + convolutional AE: 0.94 — [ADL-WAF (preprint)](https://arxiv.org/abs/2511.12643)
  - WADBERT's ablation without its URL channel drops to F1 86.67% — [WADBERT](https://arxiv.org/abs/2601.21893)
- Methodological inflation flagged by peers: HTTP2vec criticizes a near-perfect Doc2Vec CSIC result because "the language model (Doc2Vec) is trained on a whole dataset (same samples are used for training and inference)" and "they combined ten different samples into one document, which makes the problem much easier" — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- Artifacts that make CSIC easier for raw-text models: the anomalous-only "\n" line ending — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)
- Feature-engineering limits: on Shaheed & Kurdy's length and special-character features, "the assumption that legitimate requests are longer than malicious ones are not always valid", and "being dependent on special characters causes some false positives... special character combinations might appear in the normal-looking application traffic too" — [ADL-WAF](https://arxiv.org/abs/2511.12643)
- Semantic anomalies: the overlapping anomalous requests "have no malicious payload" (unintentional illegal requests, e.g., invalid ID formats) — [Aharon et al. 2024](https://arxiv.org/abs/2405.11247). Handling these required per-endpoint modelling (8 of 38 endpoints excluded for lacking normal data) — same source.
- Header uniformity in CSIC ("narrow range of unique values") — [Sivri et al. 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf)
- Splits in high-scoring papers are typically random: WADBERT "split into 70% for training and 30% for testing" with no grouping — [WADBERT](https://arxiv.org/abs/2601.21893). HTTP2vec uses 5-fold CV — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763). Sivri et al. use random splits after upsampling — [Sivri et al. 2022](https://annals-csis.org/Volume_32/drp/pdf/147.pdf)
- Test-set composition can dominate the metrics. Babaey & Faragardi's test set has 1,299 normal vs 50,174 malicious (about 2.5% normal), so F1 is driven by the attack class — [Babaey & Faragardi 2025](https://arxiv.org/abs/2504.14122)
- Duplicates bias accuracy in general ("a dataset with many duplicated instances results in biased accuracy") — [Alaoui & Nfaoui 2022](https://doi.org/10.3390/fi14040118). Data snooping was at least partly present in 73% of the top-venue papers Arp et al. audited — [Arp et al. 2022](https://arxiv.org/abs/2010.09470)
- Simple tabular models can beat deep ones on HTTP payload data when features are engineered well. XGBoost on TF-IDF + length/keyword/entropy features beat BiLSTM, CNN-BiLSTM and DistilBERT on all four SR-BH variants (macro-F1 96.77% vs ≤85.47% on the original) — [WAMM](https://arxiv.org/abs/2512.23610)
- Real-traffic false-alarm reference points:
  - ModSecurity CRS: FPR 39.69% on real Drupal traffic, vs 2.29% for a 100-token one-class model — [Riverol et al. 2024](https://arxiv.org/abs/2407.18445)
  - HTTP2vec: FPR99 4.2% on CSIC — [Gniewkowski et al. 2021](https://arxiv.org/abs/2108.01763)

### Inferences
- Likely contributors to the project's plateau, ranked by expected impact:
  1. Label semantics. A sizeable share of CSIC "anomalous" requests are valid-looking values that only violate a per-parameter format. The 21 aggregate features (lengths, counts, character classes) cannot see these, whereas per-parameter value models or char n-grams can.
  2. Weak header signal, because CSIC headers are near-constant.
  3. Group-aware splitting removes the template and near-duplicate memorization that inflates random-split results, so the project's 70% is likely closer to honest generalization than the published 99%.
  4. Small sample (604 training requests), plus threshold choice. RF v2 ROC AUC is 0.765, which suggests ranking quality, not just threshold, is the limit.
- Diagnostics worth running: per-anomaly-subtype recall, if sub-types can be recovered (attacks vs unintentional illegal vs hidden resources); a learning curve on the full CSIC under the same grouping; adding char n-gram or TF-IDF features of parameter values (WAMM's XGBoost recipe); and per-endpoint normal-value profiling. These are suggestions, not literature results.
- When comparing with published CSIC numbers, the project should explicitly state that it uses group-aware splits, and contrast only with one-class or normal-only results (about 82–89% F1), not with random-split supervised 99%+ results.

### Gaps
- No 2020–2026 paper found that re-evaluates CSIC 2010 with endpoint-, template- or near-duplicate-disjoint splits and reports the resulting F1. The size of random-split inflation on CSIC is therefore not quantified in the literature. The non-HTTP analogy is a WiFi-CSI benchmark where a proper subject-wise split fell to about 63–72% of published metrics ([PMC11679234](https://pmc.ncbi.nlm.nih.gov/articles/PMC11679234/)).
- No source gives the fraction of CSIC anomalous requests that are "unintentional illegal" vs actual attacks.
