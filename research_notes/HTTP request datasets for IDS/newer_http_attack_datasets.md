# Newer and lesser-known labeled HTTP-request / web-attack datasets (2019–2026)

Scope: datasets where each record is an HTTP request (or at least URL + payload) with a normal/attack label, usable for a supervised normal-vs-anomalous classifier whose feature extractor reads method, path, query, form body and headers. CSIC 2010, ECML/PKDD 2007, pralab/modsec-learn, SR-BH 2020, Fwaf and HttpParamsDataset are covered by another researcher and appear here only for comparison. Pure network-flow datasets are excluded but are named once so nobody re-researches them.

How things were checked (17 Oct 2026): pages were read with web fetch/search. The Hugging Face, Kaggle, Zenodo, GitHub and idUS public APIs were queried directly. Large archives were never downloaded: zip contents were listed with HTTP range requests. Only small files (<1 MB: openappsec `malicious.zip`, ATRDF `dataset_1_train.7z`) were downloaded into the scratchpad and inspected. Counts marked "counted by this researcher" come from that inspection. "Unverified" means no primary source confirmed it.

## Q0 — Which newer datasets exist, and what are their key properties? (catalog)

### Takeaway
The strongest new candidates are: (1) the **open-appsec / Check Point WAF Comparison Project**, with about 1.04M real-browsing benign requests (full headers and body, Apache-2.0) and 73,924 attack requests that include Log4Shell, XXE and Shellshock; (2) **Biblio-US17**, with 47M real URIs from a production server and expert-supervised labels, but URI only; (3) **ATRDF** (Cisco–Ariel University), with full JSON API requests and responses covering Log4j, RCE, log forging and cookie injection, but synthetic and with no license; (4) **ModSec-WP** (2026), with 108,823 labeled WordPress ModSecurity audit-log transactions under CC-BY-4.0; and (5) the **30-day ModSecurity production dataset** (2025), which holds real attacks only. That last one is byte-for-byte the same as the team's existing `data/raw/owasp/` folder. Most Hugging Face and Kaggle uploads are re-packaged CSIC data, payload-only lists, or undocumented mashups.

### Cited Findings

**A. open-appsec "WAF Comparison Project" (Check Point / open-appsec, editions 2023, 2024/25, 2026)**
- Measures WAF true-positive and false-positive rates. The legitimate set is under Apache-2.0. The malicious set is "assembled by MGM with different copyrights, mostly under MIT." The data sets "will be updated annually." — [GitHub README](https://github.com/openappsec/waf-comparison-project)
- 2026 edition: 1,040,242 legitimate HTTP requests from 692 real websites in 14 categories, plus 73,924 malicious payloads. — [open-appsec blog 2026](https://openappsec.io/post/best-waf-solutions-in-2026-real-world-comparison). The docs/README text still says "185 real-web sites in 12 categories." That matches the 2023 edition, which had 973,964 requests from 185 sites. — [docs](https://docs.openappsec.io/references/waf-comparison-project); [blog 2023](https://www.openappsec.io/post/best-waf-solutions-in-2023-real-world-comparison). **Conflict: the site and category counts differ between docs and blog.**
- How benign traffic was made: recorded by browsing real sites and performing actions such as sign-up, product selection, cart, search and file upload, "ensuring the presence of 100% legitimate requests." — [blog 2023](https://www.openappsec.io/post/best-waf-solutions-in-2023-real-world-comparison)
- Download verified: `legitimate.zip` is 1,203,983,791 bytes, Last-Modified 1 Dec 2024. Range-listing found 692 JSON files named `Legitimate/browsing_2024_<site>.json`, about 7.32 GB uncompressed. Each record is `{"method","url","headers":{...},"data":...}` with full browser headers (Chrome 129 UA, sec-ch-ua, cookies, referer). Counted by this researcher. — [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip)
- `malicious.zip` is 452,537 bytes (Last-Modified 17 Jul 2023) and holds 7 JSON files in the same schema. Counted by this researcher: xss 41,888; traversal 28,314; cmdexe 2,468; sqli 916; log4shell 220; xxe 70; shellshock 48; total 73,924. Sampled records put the payload in a single query parameter (`GET /?p=<payload>`) with only `User-Agent` and `Connection` headers. — [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)
- The payload source repo `openappsec/mgm-web-attack-payloads` reports **GPL-3.0** in the GitHub API. That contradicts the "mostly MIT" statement in the comparison README. — [mgm-web-attack-payloads](https://github.com/openappsec/mgm-web-attack-payloads); [README](https://github.com/openappsec/waf-comparison-project)
- No peer-reviewed paper. Documentation is vendor blog plus docs. A Check Point report on the 2026 edition exists. — [Check Point report](https://engage.checkpoint.com/2026-cloud-security-report-it/items/report--waf-comparison-project-2026)

**B. Biblio-US17 (Univ. of Seville / Univ. of Granada; data from 2017, released Jul 2023; papers 2023–2025)**
- Anonymized, labeled HTTP requests ("selected fields") from the logs of a production web server at the University of Seville library over 6.5 months in 2017. idUS lists it as **open access, CC BY-NC-ND 4.0**, issued 2023-07, DOI 10.12795/11441/148254. The single file is `Biblio-US17.tar.gz` at 1,223,176,305 bytes (idUS REST API, checked by this researcher). — [idUS record](https://idus.us.es/handle/11441/148254)
- The README says "free for research under CC BY-NC" and requires citing the Computers & Security 2023 paper. **License conflict: the README says CC BY-NC, idUS says CC BY-NC-ND.** — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- Counts from the README: RAW 47,402,907 registers; CLEAN (normal) 42,473,128; ATTACK 327,906 (level-1 "indubitable" attacks only); attack levels 1–4 (LVL2 context-dependent, LVL3 percent-encoding, LVL4 DoS). There are also false positives (9,222) and "out-of-specification" requests (10,352). Filtering to response code <300 cuts attacks to 5,207. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- Fields: tab-delimited identifier, method, URI, protocol, response code, response size. No headers and no body. Labels come from Snort, Nemesida and ModSecurity PL1/PL2, plus manual and vocabulary-based supervision. 198 daily files. Partition scripts give time-independent and time-dependent 60/30/10 splits. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- Papers: Díaz-Verdejo et al., "Building a large, realistic and labeled HTTP URI dataset… Biblio-US17", *Cybersecurity* 8:35 (2025), plus the EICC 2024 short paper (doi 10.1145/3655693.3661319). — [Cybersecurity 2025](https://cybersecurity.springeropen.com/articles/10.1186/s42400-024-00336-3); [project page](https://dtstc.ugr.es/neus-cslab/recursos/ds-biblio/)

**C. ATRDF – API Traffic Research Dataset Framework (Cisco–Ariel University API Security Detection Challenge, 2023)**
- Four datasets, each a list of JSON HTTP API request + response records. Label phase: Benign/Malware. Attack-type phase: Benign, Cookie Injection, Directory Traversal, LOG4J, Log Forging, RCE, SQL Injection, XSS. Splits are 70/15/15 and the validation split is unlabeled. Used by Aharon et al., *Computers & Security* vol. 150 (2025). — [GitHub repo](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)
- The GitHub API reports **no license**. Created Dec 2022, last pushed Apr 2025. Archive sizes: `dataset_1_train.7z` 0.88 MB, `dataset_2_train.7z` 24.3 MB, `dataset_3_train.7z` 44.3 MB, `dataset_4_train.7z` 54.8 MB (download URL returned HTTP 200). — [GitHub repo](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)
- Counted by this researcher in `dataset_1_train.json` (24.7 MB uncompressed): 4,282 records. 2,018 have no attack tag (benign). The rest: SQL Injection 586, Cookie Injection 566, Log Forging 297, LOG4J 277, Directory Traversal 270, RCE 268. Each record has `request.{headers, method, url, body, Attack_Tag}` and `response.{status, headers, body}`. The target is a local Flask-style API (`Host: 127.0.0.1:5000`), so traffic is synthetic. — [dataset_1_train.7z](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge/raw/main/Datasets/dataset_1_train.7z)

**D. ModSec-WP – WordPress Web Attack Audit Log Dataset / "LightIDS" (Pramukantoro, Universitas Brawijaya; Zenodo, 10 Aug 2026)**
- Labeled HTTP transactions from a WordPress testbed running ModSecurity (OWASP CRS) in detection-only mode. Benign traffic and attacks against real, publicly disclosed WordPress plugin vulnerabilities were replayed. Labels came from attack-scenario timestamp correlation, regex matching and manual expert validation. **CC-BY-4.0.** — [Zenodo 21872151](https://zenodo.org/records/21872151)
- v1 has 108,823 transactions: sqli 69,631; normal 12,597; xss 8,625; bruteforce 7,568; fileinclusion-ldf (LFI/RFI/traversal) 6,230; rce (incl. malicious upload) 4,172. v2 has 108,883 (+60 file-inclusion rows). Format is `.xlsx`, 26 columns: request_host, request_useragent, request_line (method/url/protocol), request_body, response_status, response_body, plus ModSecurity rule metadata. The authors warn that "a substantial fraction of rows are near-identical" and recommend de-duplicated or group-aware splits. — [Zenodo 21872151](https://zenodo.org/records/21872151)
- File download verified (HTTP 206 on a range request). Only the v2 file `combined_final_dataset_augmented.xlsx` (27.8 MB) appears in the current record. — [Zenodo 21872151](https://zenodo.org/records/21872151)

**E. "A Thirty-Day Dataset of Malicious HTTP Requests Blocked by OWASP ModSecurity on a Production Web Server" (Lucz & Forstner, Budapest Univ. of Technology and Economics; Zenodo Sep 2025, MDPI *Data* Nov 2025)**
- Real-world malicious requests that triggered OWASP CRS rules on a live production server. Covers SQLi, XSS, LFI, scanner probes, and malformed/evasive input. Anonymized, but keeps method, URI, triggered rule IDs, request headers and user agent. **CC-BY-4.0.** — [Zenodo 17178461](https://zenodo.org/records/17178461); [Crossref record for Data 10(11):186](https://api.crossref.org/works/10.3390/data10110186)
- `owasp.zip` is 29,524,147 bytes. Range-listing found 60 entries: 30 day folders, each holding `modsec_audit.anon.log`, totalling 397,963,611 bytes uncompressed. Checked by this researcher. — [Zenodo 17178461](https://zenodo.org/records/17178461)
- Counted by this researcher in the identical local copy: 30 days (27 Jul–25 Aug 2025); 139,840 audit transactions; 13,061 with a request-body (C) section. Every transaction has a request-header (B) section. Native ModSecurity audit format (sections A/B/C/E/F/H/Z), CRS v3.2.3. The most frequent rule IDs are 930130 (restricted file access), 920450, 920340, 920440, 920210, 942100 (libinjection SQLi) and 920350. 488 lines contain a `jndi` string, i.e. Log4Shell probes. — [Zenodo 17178461](https://zenodo.org/records/17178461)
- **There is no benign class.** Every record is a CRS-flagged request. — [Zenodo 17178461](https://zenodo.org/records/17178461)

**F. FADE – Firewall Attack Detections and Extractions (Gavin Black, Leidos-funded; IEEE DataPort, 18 Dec 2024, updated Sep 2026)**
- Over 10 million categorized attacks in eight categories, drawn from open-source rule sets and public penetration-testing repositories. They are injected into "realistic network traffic" to give 50 million fully formed requests, balanced between benign and malicious. Columns: `sample` (request text), `class`, `label`, `benign_class`, `malicious_class`, `malicious_source`, `payload_start_byte`, `payload_end_byte`. Files: `FADE_50M.parquet` (20.41 GB) / `.csv` (31.08 GB) and `injections.parquet`/`.csv`. DOI 10.21227/018f-ka11. **"Subscription Required."** — [IEEE DataPort FADE](https://ieee-dataport.org/documents/firewall-attack-detections-and-extractions-fade)

**G. DarkSegments_IDS (Mohamed Almaleki, UAE University; IEEE DataPort, created 29 May 2026)**
- Plaintext and evasive (obfuscated) web attacks: SQLi (Boolean/tautology/union variants), XSS (incl. event-handler), CMDi, plus benign. Comes as flow features (CICFlowMeter) and as HTTP URI/payload files (`HTTP_Plaintext_Labeled.csv` 1.93 MB, `HTTP_Evasive_Labeled.csv` 6.82 MB) and PCAPs. DOI 10.21227/488q-0176. **"Subscription Required."** — [IEEE DataPort DarkSegments_IDS](https://ieee-dataport.org/documents/darksegmentsids)

**H. Zaker "Online Shopping Store – Web Server Logs" + Kaggle labeled version (Zaker, York Univ., Harvard Dataverse 2021, CC0; labels by mahendradata, Kaggle Jun 2025, CC0)**
- The source is the real Nginx access log of an online shopping store: `Access.log.zip` (274 MB), released 2021-05-20, CC0. — [Harvard Dataverse doi:10.7910/DVN/3QBYB5](https://doi.org/10.7910/DVN/3QBYB5)
- The Kaggle "Web Server Access Logs – Labeled" adds `label` (benign/attack) and `type` (benign/sqli/rce/…) columns using **rule-based keyword heuristics**. `labeled.csv` is 2.86 GB. CC0. — [Kaggle mahendradata/web-server-access-logs-labeled](https://www.kaggle.com/datasets/mahendradata/web-server-access-logs-labeled); [labeling code](https://github.com/mahendradata/web-log-keyword-heuristics)

**I. Smaller or forensic-oriented Zenodo log datasets (2026)**
- Web Server Log Dataset (anonymous authors; Zenodo, 3 May 2026; MIT): real Apache/OpenLiteSpeed access/error/auth/syslog files from two Indonesian public-sector organizations (Aug–Oct 2025 for org X). Ground truth is YAML pattern rules; "entries that do not match any rule are labeled as benign." — [Zenodo 20001206](https://zenodo.org/records/20001206)
- Multi-Attacker Web Attack (MAWA) Log Dataset (Utomo, Studiawan, Pratomo; Zenodo, 12 Oct 2026; CC-BY-4.0): eight simulated multi-attacker scenarios against DVWA on Apache (dirb, password spraying, webshell upload, RCE, WPScan, Hydra). Includes access.log/error.log/auth.log/syslog plus a ground-truth timeline. Each zip is about 0.6–1.2 MB. — [Zenodo 23308212](https://zenodo.org/records/23308212)
- HTTP Tarpit Interaction Dataset (Boyko & Spesivtsev, Odesa; Zenodo, v3.1 Sep 2026; CC-BY-4.0): 251,140 bot interactions captured over 11 months by an HTTP tarpit, including 6 Log4Shell cases. SQLite file. — [Zenodo 22749296](https://zenodo.org/records/22749296)
- A Synthetic Dataset of Cross-Site Request Forgery (CSRF) Attacks Based on HTTP Requests (Alves, Pinto, Silvestre; Zenodo, 5 Jun 2026; CC-BY-4.0): one 300 KB `dataset.zip`, no description in the record. — [Zenodo 20555856](https://zenodo.org/records/20555856)
- AIT Log Data Set v1.1 (AIT Austrian Institute of Technology, 2020, CC BY-NC-SA 4.0): simulated users of Horde Webmail/OkayCMS. Attacks include nmap, nikto, hydra brute force, webshell upload (CVE-2019-9858), Exim privilege escalation, and cookie-based webshell injection (CVE-2019-16885). Labeled Apache access logs among other logs. 3.4 GB zip. — [Zenodo 4264796](https://zenodo.org/records/4264796). v2.1 (9 Apr 2026, eight testbeds incl. WordPress, per-dataset `_no-pcaps.zip` around 0.7 GB): — [Zenodo 19483937](https://zenodo.org/records/19483937)

**J. Hugging Face / Kaggle uploads with full raw requests (no paper)**
- `puyang2025/waf_data_v2` (Dec 2025–Jan 2026, MIT): 2,405,579 rows with method, url, protocol, headers, body, label (normal/anomalous). The README splits it into train 1,924,461 / eval 240,560 / test 240,558 / heldout 147,188. Provenance is undocumented. Sampled rows include SR-BH-style WordPress requests (`Host: test-site.com`, 2020 cookies) and `localhost:8080?/…` wordlist-like paths labeled `normal`. — [HF puyang2025/waf_data_v2](https://huggingface.co/datasets/puyang2025/waf_data_v2)
- `vyykaaa/dataset-web-attack` (Jan 2026, no license, no README text): 272,265 rows (`raw_request`, `label`, `attack_type`), attack_type values incl. NoSQL_Injection, SSRF, SSI, Directory_Traversal. Sampled normal rows target OWASP Juice Shop (`127.0.0.1:3000`); sampled attacks target DVWA paths (`/vulnerabilities/sqli/`). — [HF vyykaaa/dataset-web-attack](https://huggingface.co/datasets/vyykaaa/dataset-web-attack)
- Kaggle "Web Application Attack Dataset", 199,793 HTTP request messages, 4 classes (benign, SQLi 57,240, XSS 40,395, CMDi): a 2026 Research Square preprint (Saravanan C et al., not peer reviewed) reports that "the label of the targeted resource, encoded in the HTTP request path field, determines the message class independently of the actual request content." The authors fix it with header stripping, decoding and group-stratified splits. — [Research Square rs-10802265](https://www.researchsquare.com/article/rs-10802265/v1). A Kaggle upload by user `saravanan3113`, "SQL_XSS_CMD_INJECTION_RAW_DATASET" (MIT, updated 11 Aug 2026, `processed_dataset.csv` 120 MB, labels 0=benign/1=SQLi/2=XSS/3=CMDi), matches that label scheme. — [Kaggle saravanan3113/sql-xss-cmd-injection-raw-dataset](https://www.kaggle.com/datasets/saravanan3113/sql-xss-cmd-injection-raw-dataset)
- `SecureAI-SE/http-attack-requests` (Jun 2026, CC-BY-4.0): 7,000 requests, 1,000 per class (normal, sqli, xss, ssrf, ssti, lfi, traversal). Built on CSIC 2010 normal-request "envelopes" with one parameter value replaced by a PayloadsAllTheThings payload; SSRF/SSTI payloads are "templated"; Host is randomized to avoid shortcuts. — [HF SecureAI-SE/http-attack-requests](https://huggingface.co/datasets/SecureAI-SE/http-attack-requests)
- `notesbymuneeb/ai-waf-dataset` (May 2025, MIT): "synthetically generated," 8,658 benign / 3,291 malicious. Payloads in URL params, paths, headers/cookies, JSON and form bodies. — [HF notesbymuneeb/ai-waf-dataset](https://huggingface.co/datasets/notesbymuneeb/ai-waf-dataset)
- `netgoat-ai/WAF-Bench` (3 Oct 2026, CC-BY-4.0): 77 hand-curated, replayable requests with OWASP Top-10 mapping and benign false-positive traps. Authors say it is "not suitable as sole training data." — [HF netgoat-ai/WAF-Bench](https://huggingface.co/datasets/netgoat-ai/WAF-Bench)

**K. Payload-only corpora (no request envelope) — attack-side augmentation only**
- GoTestWAF (Wallarm, MIT): test-case sets `owasp` (crlf, ldap, mail, nosql, path-traversal, rce-urlparam/urlpath, shell, sql, ss-include, sst-injection, xml, xss), `owasp-api` (graphql, grpc, rest, soap, non-crud), `community`, and a `false-pos/texts.yml` benign set. — [GitHub wallarm/gotestwaf](https://github.com/wallarm/gotestwaf)
- `YangYang-Research/web-attack-detection` (Mar 2025, MIT): 625,904 payload samples (294,771 label 1 / 331,129 label 0). `truongp/web-attack-detection` (Apr 2026) has the same row count and byte size, so it is a re-upload. — [HF YangYang-Research](https://huggingface.co/datasets/YangYang-Research/web-attack-detection); [HF truongp](https://huggingface.co/datasets/truongp/web-attack-detection)
- Kaggle `mreowie/web-application-attack-payload-dataset` (Dec 2025, Apache-2.0): about 240k payloads aggregated from foospidy/payloads, PayloadBox, the openappsec MGM payloads and other public lists. — [Kaggle mreowie](https://www.kaggle.com/datasets/mreowie/web-application-attack-payload-dataset)
- Mendeley "Large-Scale Annotated Dataset for XSS Attack Detection": 1,831,254 query-string records (1,164,770 malicious / 666,484 benign). — [Mendeley py6cnbgdh2](https://data.mendeley.com/datasets/py6cnbgdh2). Mendeley "Obfuscated and LLM-Augmented XSS Payload Dataset": 27,314 entries (22,066 malicious / 5,248 benign). — [Mendeley z6xm42spk6](https://data.mendeley.com/datasets/z6xm42spk6/1)
- IEEE DataPort "SQL Injection Detection Payloads V2 Extended": 320,000 records, subscriber-only per search snippet. — [IEEE DataPort](https://ieee-dataport.org/documents/sqlinjectiondetectionpayloadsv2extended)

**L. Papers that build or fix HTTP datasets but don't clearly release new data**
- X-WAD (Bitussi & Doriguzzi-Corin, FBK, arXiv Aug 2026) found "approximately 13.8% of the [SR-BH 2020] dataset is mislabeled." It builds "SR-BH2020-fix" and says the list of inconsistencies and the tool source are public (ref [16]). — [arXiv 2608.27172](https://arxiv.org/abs/2608.27172)
- WAMM (Osama et al., arXiv Dec 2025/Jan 2026) refines SR-BH 2020 by dedup, LLM relabeling, augmentation and LLM filtering into "three refined datasets." The abstract page gives no download link. — [arXiv 2512.23610](https://arxiv.org/abs/2512.23610)
- Multi-Agent Honeypot SQLi request-response dataset (Yu et al., arXiv Mar 2026): "140,973 labeled pairs" of request + response, generated by LLM agents. — [arXiv 2603.02963](https://arxiv.org/abs/2603.02963v1)
- ml-based-waf-mitmproxy-tool (Durmuşkaya, Zenodo Jun 2025, CC-BY-4.0): "WAF-related dataset" plus code for the PeerJ CS paper. Per search, the data is a hybrid of CSIC 2010, HTTPParams and live requests. — [Zenodo 15574488](https://zenodo.org/records/15574488); [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12453791/)

**M. Excluded (flow-only, no request content), noted so nobody re-checks them**
- WEB-IDS23 (Lanfer, Brockmann, Aschenbruck, Osnabrück, arXiv Feb 2025): 12,059,749 samples, 82 Zeek-FlowMeter features, 21 classes incl. SQLi, XSS, SSRF and SSTI-based reverse shell. "Unencrypted payloads were not recorded." Data at osnaData doi:10.26249/FK2/MOCIY8. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)
- WKLIN-WEB-2023 (Wenzhou Univ., IJWIS Dec 2024): partial-flow features built from CSE-CIC-IDS2018 PCAPs. — [vLex abstract](https://international.vlex.com/vid/toward-fast-network-intrusion-1072311397)
- TRUST Lab API dataset: CICFlowMeter flow CSVs. — [UPCT portal](https://portalinvestigacion.upct.es/documentos/69821f20df011a1efbe63b28?lang=en)

### Inferences
- For this project's extractor (method, path, query, form body, headers), the datasets that fill every feature are: openappsec (benign + attacks), ATRDF, FADE (if accessible), ModSec-WP (request line, UA and body, but not the full header set), the 30-day ModSecurity data (headers, some bodies, attacks only), and the HF/Kaggle raw-request uploads. Biblio-US17 and the access-log datasets (Zaker/Kaggle, Indonesian, MAWA, AIT) supply only method + URI (+UA/referrer in combined logs), so the body and header features would always be empty.
- A good design for this project: openappsec legitimate requests as real benign traffic, plus attack requests built by injecting openappsec/GoTestWAF payloads into those same benign envelopes. The SecureAI-SE construction method does this on a small scale with CSIC. This avoids the source leakage that a raw openappsec legitimate-vs-malicious split would create (see Q4). Test on ModSec-WP, ATRDF or the 30-day ModSecurity data for cross-dataset generalization.
- Only the README, the ATRDF repo and the Zenodo/IEEE descriptions vouch for most per-class counts. Openappsec's malicious counts, ATRDF dataset 1 and the 30-day ModSecurity totals were independently recounted here.

### Gaps
- ATRDF datasets 2–4: record counts and class balance not verified. Downloads of the 24–55 MB archives timed out and were stopped; the README baseline tables suggest dataset 2 has an evaluation split of 22,504 rows.
- FADE and DarkSegments_IDS contents could not be inspected (subscription wall). The FADE "paper" venue was not found.
- The openappsec 2026 count of 1,040,242 legitimate requests was not recounted (the 1.2 GB archive was not downloaded). Whether every one of the 692 files belongs to a distinct website is unclear: some sites have two files, e.g. `agoda` and `agoda_al`.
- ModSec-WP: no associated paper (the "LightIDS study") was found. Full HTTP headers beyond User-Agent and Host appear not to be included (inferred from the column list).
- The CSRF Zenodo dataset (20555856) has no description. Contents not inspected.
- No public dataset found with **deserialization** payloads embedded in labeled HTTP requests.
- No public request corpus found from Cloudflare, Akamai, Imperva, Fastly or Elastic. Wallarm's public contribution is the GoTestWAF test-case set, not labeled traffic.

## Q1 — Which newer datasets have real (not purely synthetic) benign traffic?

### Takeaway
Real benign traffic is rare. **Biblio-US17** (production university server, 42M clean URIs) and the **Zaker e-commerce Nginx log** (CC0) are real but URI/log-line only. **openappsec legitimate** is real-world browsing of about 692 live websites with full headers, but recorded deliberately, not passively. Every other full-request dataset with benign traffic is a testbed (ModSec-WP, ATRDF, MAWA, AIT, Juice Shop/DVWA uploads) or synthetic (notesbymuneeb, FADE injection, SecureAI-SE's CSIC envelopes).

### Cited Findings
- Biblio-US17 comes from "a real-in-production web server at the library of the University of Seville during 6.5 months in 2017." — [idUS record](https://idus.us.es/handle/11441/148254). The CLEAN set has 42,473,128 registers. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- openappsec legitimate traffic was "recorded by browsing real-world websites and conducting various operations on the site." — [blog 2023](https://www.openappsec.io/post/best-waf-solutions-in-2023-real-world-comparison). File names are `browsing_2024_<site>.json` for sites such as adidas, airbnb, amazon and agoda (range-listed by this researcher). — [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip)
- The Zaker dataset is the "Nginx server access log for an online shopping store." — [Harvard Dataverse](https://doi.org/10.7910/DVN/3QBYB5). The Kaggle labeled version adds heuristic labels. — [Kaggle mahendradata](https://www.kaggle.com/datasets/mahendradata/web-server-access-logs-labeled)
- The Indonesian Web Server Log Dataset holds "real-world web server log files collected from two public sector organizations in Indonesia." Anything not matched by an attack rule is labeled benign. — [Zenodo 20001206](https://zenodo.org/records/20001206)
- ModSec-WP benign traffic was "replayed against the site" in "a controlled research testbed." — [Zenodo 21872151](https://zenodo.org/records/21872151)
- ATRDF benign records target a local API host (`127.0.0.1:5000`; inspected by this researcher). — [dataset_1_train.7z](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge/raw/main/Datasets/dataset_1_train.7z)
- AIT-LDS benign traffic is simulated users ("synthetic log data"). — [Zenodo 4264796](https://zenodo.org/records/4264796); [Zenodo 19483937](https://zenodo.org/records/19483937)
- FADE combines injected attacks with "realistic network traffic"; its source is not described. — [IEEE DataPort FADE](https://ieee-dataport.org/documents/firewall-attack-detections-and-extractions-fade)
- The 30-day ModSecurity dataset has real traffic but **no benign requests**. — [Zenodo 17178461](https://zenodo.org/records/17178461)
- WEB-IDS23 says outright it "does not contain real-world traffic" (and is flow-only anyway). — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)

### Inferences
- For a full-request classifier, openappsec legitimate is the best freely licensed source of realistic, modern (2024, Chrome 129, sec-ch-* headers), multi-site benign requests. It is far more diverse than CSIC's single Spanish shop.
- Biblio-US17 is the best source of truly passive, production benign traffic with genuine attacks, but only for URL-level features. Its 2017 date and single site (a library) limit how modern and diverse it is.
- Real benign data labeled "benign" by elimination (Indonesian rules, Kaggle keyword heuristics) will contain unflagged attacks. X-WAD found this to be about 13.8% in SR-BH. — [arXiv 2608.27172](https://arxiv.org/abs/2608.27172)

### Gaps
- How much of openappsec's legitimate traffic is third-party CDN, analytics or ad requests rather than first-party application requests was not measured. The sample shows CDN hosts such as `cdn1.1800flowers.com`.
- No newer (2020+) passive production benign corpus with full headers and bodies was found. Privacy is the likely reason, but no source says so.

## Q2 — Which cover modern attacks (Log4Shell, SSRF, SSTI, deserialization, API/JSON abuse) beyond classic SQLi/XSS?

### Takeaway
Log4Shell appears in **openappsec** (220 requests), **ATRDF** (LOG4J class), real **30-day ModSecurity** traffic (jndi probes) and the HTTP tarpit (6 cases). API/JSON-style requests appear in **ATRDF** (JSON API, cookie injection, log forging, RCE). SSRF/SSTI appear only in tiny or questionable uploads (SecureAI-SE templated, vyykaaa labels) and in GoTestWAF test cases (SSTI, NoSQL, XML, GraphQL/gRPC/SOAP). No labeled dataset with deserialization payloads was found.

### Cited Findings
- openappsec malicious classes: SQLi, XSS, XXE, path traversal, command execution, Log4Shell, Shellshock. — [GitHub README](https://github.com/openappsec/waf-comparison-project). Counts (by this researcher): log4shell 220, xxe 70, shellshock 48, cmdexe 2,468. — [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)
- ATRDF attack types: Cookie Injection, Directory Traversal, LOG4J, Log Forging, RCE, SQL Injection, XSS. — [GitHub repo](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge). Dataset 1 train has 277 LOG4J and 297 Log Forging records (counted by this researcher). — [dataset_1_train.7z](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge/raw/main/Datasets/dataset_1_train.7z)
- 30-day ModSecurity production logs (2025): 488 log lines contain `jndi` (counted by this researcher; lines, not unique requests). — [Zenodo 17178461](https://zenodo.org/records/17178461)
- HTTP tarpit: "6 Log4Shell cases: 3 cryptominer deployment attempts and 3 Out-of-Band probes," plus targeting of `.env.prod` and `wp-config.php.bak`. — [Zenodo 22749296](https://zenodo.org/records/22749296)
- ModSec-WP: exploitation of real WordPress plugin vulnerabilities; RCE "including malicious upload"; brute force. — [Zenodo 21872151](https://zenodo.org/records/21872151)
- SecureAI-SE: SSRF and SSTI classes are "templated (no clean public payload file)," 1,000 each. — [HF SecureAI-SE](https://huggingface.co/datasets/SecureAI-SE/http-attack-requests)
- vyykaaa/dataset-web-attack has attack_type labels NoSQL_Injection, Server-Side_Request_Forgery and Server_Side_Include_Injection. A sampled "SSRF" row is a POST to `/vulnerabilities/sqli/` (inspected by this researcher), which casts doubt on the labels. — [HF vyykaaa](https://huggingface.co/datasets/vyykaaa/dataset-web-attack)
- GoTestWAF test cases include `nosql-injection`, `sst-injection`, `xml-injection`, `ldap-injection`, `ss-include`, `crlf`, plus API sets `graphql`, `grpc`, `rest`, `soap`, `non-crud`. — [GitHub wallarm/gotestwaf](https://github.com/wallarm/gotestwaf)
- notesbymuneeb/ai-waf-dataset injects payloads into JSON bodies, cookies and custom headers (synthetic). — [HF notesbymuneeb](https://huggingface.co/datasets/notesbymuneeb/ai-waf-dataset)
- AIT-LDS: CVE exploitation (Horde CVE-2019-9858 webshell upload, CVE-2019-16885 cookie webshell injection), nikto scans, hydra brute force. — [Zenodo 4264796](https://zenodo.org/records/4264796)
- MAWA: dirb/WPScan scanning, password spraying, webshell upload, RCE. — [Zenodo 23308212](https://zenodo.org/records/23308212)
- WEB-IDS23 includes SSRF and SSTI-driven reverse shells, but flow-only. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)

### Inferences
- For a binary "anomalous" class with modern coverage, the most practical public mix is: openappsec malicious (XSS-heavy; Log4Shell/XXE/Shellshock), ATRDF (Log4j, RCE, log forging, cookie injection in JSON API context), and GoTestWAF payloads (SSTI, NoSQL, XML, API protocols) injected into real benign envelopes.
- Attack classes are badly imbalanced in openappsec: XSS + traversal are about 95% of 73,924, and SQLi is only 916. Stratify or reweight by attack family before evaluating.

### Gaps
- No dataset found with Java/PHP/.NET deserialization payloads (e.g., ysoserial gadgets) inside labeled HTTP requests.
- No labeled dataset with BOLA/IDOR or business-logic API abuse found. SecureAI-SE excludes IDOR on purpose, as it has "no payload signature." — [HF SecureAI-SE](https://huggingface.co/datasets/SecureAI-SE/http-attack-requests)
- The eight FADE attack categories are not named on the public page.

## Q3 — Which are large (>100k requests) and well-documented with a citable paper?

### Takeaway
Large **and** peer-reviewed: **Biblio-US17** (47.4M URIs; Cybersecurity 2025, EICC 2024, Computers & Security 2023) and the **30-day ModSecurity** set (139,840 transactions counted; MDPI *Data* 2025, attack-only). Large with good documentation but no peer-reviewed paper: **openappsec** (about 1.1M; vendor docs/blog), **ModSec-WP** (108,823; detailed Zenodo description), **FADE** (50M; DataPort abstract, paywalled). Large but undocumented: `puyang2025/waf_data_v2` (2.4M), `vyykaaa/dataset-web-attack` (272k), the Kaggle 199,793-request "Web Application Attack Dataset" (known leakage), and Kaggle labeled Zaker logs (millions; heuristic labels).

### Cited Findings
- Biblio-US17: 47,402,907 raw registers, 327,906 level-1 attacks. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt). Journal paper: *Cybersecurity* vol. 8, no. 35 (2025). — [SpringerOpen](https://cybersecurity.springeropen.com/articles/10.1186/s42400-024-00336-3)
- 30-day ModSecurity: MDPI *Data* paper (Lucz & Forstner, published 11 Nov 2025). — [Crossref](https://api.crossref.org/works/10.3390/data10110186). 139,840 audit transactions (counted by this researcher). — [Zenodo 17178461](https://zenodo.org/records/17178461)
- openappsec: 1,040,242 legitimate + 73,924 malicious. — [blog 2026](https://openappsec.io/post/best-waf-solutions-in-2026-real-world-comparison)
- ModSec-WP: 108,823 / 108,883 transactions. — [Zenodo 21872151](https://zenodo.org/records/21872151)
- FADE: 50 million entries; abstract reads "In this paper, we introduce…", but no venue is given. — [IEEE DataPort FADE](https://ieee-dataport.org/documents/firewall-attack-detections-and-extractions-fade)
- ATRDF: used in Aharon et al., *Computers & Security* vol. 150 (2025). Total size across datasets 1–4 not verified; dataset 1 train is only 4,282 records. — [GitHub repo](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)
- puyang2025/waf_data_v2: 2,405,579 rows, no provenance section. — [HF](https://huggingface.co/datasets/puyang2025/waf_data_v2)
- Kaggle Web Application Attack Dataset: 199,793 requests; the only documentation found is a non-peer-reviewed preprint that reports leakage. — [Research Square](https://www.researchsquare.com/article/rs-10802265/v1)
- HTTP tarpit: 251,140 interactions, but no benign class. — [Zenodo 22749296](https://zenodo.org/records/22749296)
- Honeypot SQLi request–response pairs: 140,973 (arXiv preprint; release not confirmed). — [arXiv 2603.02963](https://arxiv.org/abs/2603.02963v1)

### Inferences
- If a peer-reviewed citation is required, Biblio-US17 is the only large real-traffic option, but URI-only. For full-request training, openappsec is the realistic large option and is cited through its project page/blog.
- ModSec-WP passes 100k rows, but its normal class (12,597) is small and rows are near-duplicates. After de-duplication the usable size may be much smaller.

### Gaps
- Unique-request counts after de-duplication are not published for any of these sets.
- No paper describing the ModSec-WP/LightIDS study was found.

## Q4 — Which are actually downloadable (as of 17 Oct 2026) and under what license?

### Takeaway
Freely downloadable and verified today: openappsec (Apache-2.0 legitimate; malicious "mostly MIT" vs. GPL-3.0 on the payload repo), Biblio-US17 (open access on idUS, CC BY-NC-ND 4.0 vs. CC BY-NC in the README), ATRDF (GitHub, **no license**), ModSec-WP (CC-BY-4.0), 30-day ModSecurity (CC-BY-4.0), Zaker logs (CC0) + Kaggle labels (CC0, Kaggle login needed), AIT-LDS (CC BY-NC-SA 4.0), MAWA (CC-BY-4.0), Indonesian logs (MIT), HF uploads (mostly MIT/CC-BY or none). **FADE and DarkSegments_IDS need an IEEE DataPort subscription.**

### Cited Findings
- openappsec `legitimate.zip`: HTTP 200, 1,203,983,791 bytes. `malicious.zip`: HTTP 200, 452,537 bytes (both checked 17 Oct 2026). — [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip); [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip). Licenses: Apache-2.0 / "mostly under MIT." — [GitHub README](https://github.com/openappsec/waf-comparison-project). The payload repo is GPL-3.0. — [mgm-web-attack-payloads](https://github.com/openappsec/mgm-web-attack-payloads)
- Biblio-US17: `dc.rights.accessRights = open access`, CC BY-NC-ND 4.0, `Biblio-US17.tar.gz` 1.22 GB. — [idUS](https://idus.us.es/handle/11441/148254). README: CC BY-NC. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- ATRDF: `.7z` archives under `Datasets/`; `dataset_4_train.7z` returned HTTP 200 (54,762,203 bytes); GitHub API license `None`. — [GitHub repo](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)
- ModSec-WP, Indonesian logs, MAWA and AIT v2.1 files answered range requests with HTTP 206. Licenses are CC-BY-4.0, MIT, CC-BY-4.0 and CC BY-NC-SA 4.0. — [Zenodo 21872151](https://zenodo.org/records/21872151); [Zenodo 20001206](https://zenodo.org/records/20001206); [Zenodo 23308212](https://zenodo.org/records/23308212); [Zenodo 19483937](https://zenodo.org/records/19483937)
- 30-day ModSecurity `owasp.zip`: HTTP 200, 29,524,147 bytes, CC-BY-4.0. — [Zenodo 17178461](https://zenodo.org/records/17178461)
- Zaker logs: CC0 1.0. — [Harvard Dataverse](https://doi.org/10.7910/DVN/3QBYB5). Kaggle labeled version: CC0. — [Kaggle](https://www.kaggle.com/datasets/mahendradata/web-server-access-logs-labeled)
- FADE: "Subscription Required… LOGIN TO ACCESS DATASET FILES." — [IEEE DataPort FADE](https://ieee-dataport.org/documents/firewall-attack-detections-and-extractions-fade). DarkSegments_IDS: "Subscription Required." — [IEEE DataPort DarkSegments](https://ieee-dataport.org/documents/darksegmentsids)
- HF `puyang2025/waf_data_v2` train.parquet: HTTP 200 (80,180,766 bytes), MIT. — [HF](https://huggingface.co/datasets/puyang2025/waf_data_v2). `vyykaaa/dataset-web-attack`: license field empty. — [HF](https://huggingface.co/datasets/vyykaaa/dataset-web-attack)
- The Cyshield SR-BH 2020 augmentation post, which the project's `docs/aday-veri-setleri.md` cites, returned **HTTP 404** to a scripted request on 17 Oct 2026. This may be bot blocking; recheck in a browser. — [Cyshield post](https://seclab.cyshield.com/posts/augmenting-sr-bh-2020-a-technical-methodology-for-modern-threat-simulation/)
- **Project-relevant finding:** the team's local `data/raw/owasp/` (README: "~380 MB, anonymized ModSecurity audit logs; shared within team") has the same folder layout (30 `DD-Mon-2025/modsec_audit.anon.log` folders) and **exactly the same total size (397,963,611 bytes)** as the public Zenodo 17178461 archive contents. — [Zenodo 17178461](https://zenodo.org/records/17178461) (compared by this researcher)

### Inferences
- `data/raw/owasp/` is almost certainly the public Lucz & Forstner dataset (CC-BY-4.0), not private team data. The project docs could cite it (Zenodo DOI 10.5281/zenodo.17178461; MDPI *Data* 10(11):186) instead of calling it team-internal. A file-hash comparison would confirm this.
  - **Update 19 Oct 2026: confirmed.** Zenodo's `owasp.zip` matched the md5 Zenodo publishes (`95b7a8237abc163d8ca31e49f7318efd`). Unpacked, its 30 log files are byte-for-byte the same as `data/raw/owasp/`, with no file missing or extra on either side.
- The CC BY-NC-ND "NoDerivatives" term on Biblio-US17 could restrict redistributing processed subsets, e.g. a `data/http-mini`-style sample in the repo. Non-commercial terms (Biblio-US17, AIT) matter if the project leaves academia.
- ATRDF has no license, so in principle no redistribution rights are granted. Use it only locally or ask the authors.
- If openappsec malicious payloads come from GPL-3.0 sources, redistributing derived training data may carry copyleft obligations. That is unclear for data; legal review needed.

### Gaps
- Kaggle downloads need a logged-in account. Kaggle file contents (saravanan3113, mahendradata) were not opened.
- The 1.22 GB Biblio-US17 tarball was not downloaded, so its internal file list was not checked against the README.

## Q5 — Red flags: tiny, undocumented, scraped/duplicated CSIC re-uploads, unclear labels, leakage

### Takeaway
Most Hugging Face and Kaggle "WAF/web attack" datasets are CSIC 2010/ECML/HttpParams re-uploads, payload-only lists, duplicate copies, or undocumented mashups. The biggest technical red flag in otherwise good datasets is **source/endpoint leakage**: benign and attack requests come from different apps or templates, so a model can learn the source instead of the attack. This hits openappsec (benign = rich browser headers on real sites; attacks = `/?p=` with 2 headers), vyykaaa (Juice Shop vs. DVWA) and the Kaggle 199,793-request set (path predicts class). The project's existing docs already list this as the main risk.

### Cited Findings
- Endpoint leakage confirmed in the Kaggle "Web Application Attack Dataset": "the label of the targeted resource, encoded in the HTTP request path field, determines the message class independently of the actual request content." — [Research Square](https://www.researchsquare.com/article/rs-10802265/v1)
- openappsec malicious records sampled by this researcher are `GET /?p=<payload>` with only `User-Agent` and `Connection` headers. Legitimate records carry 10–20 real browser headers on real hostnames. — [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip); [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip)
- vyykaaa/dataset-web-attack: sampled normal rows hit `127.0.0.1:3000` (Juice Shop paths `/rest/captcha`, `/account`); sampled anomalous rows hit `/vulnerabilities/sqli/` (DVWA). No README text, no license. — [HF vyykaaa](https://huggingface.co/datasets/vyykaaa/dataset-web-attack)
- puyang2025/waf_data_v2: undocumented provenance; sampled rows mix SR-BH-style WordPress traffic with `localhost:8080?/<wordlist path>` requests labeled `normal`; a sampled `normal` row contains `/%2F%2F…owasp.org/` and another contains `sleep(15)` in the path. — [HF puyang2025/waf_data_v2](https://huggingface.co/datasets/puyang2025/waf_data_v2)
- SR-BH label contamination: about 13.8% of the dataset is mislabeled, per X-WAD. — [arXiv 2608.27172](https://arxiv.org/abs/2608.27172)
- ModSec-WP: "a substantial fraction of rows are near-identical." — [Zenodo 21872151](https://zenodo.org/records/21872151)
- Heuristic or elimination labels: the Indonesian logs mark anything unmatched as benign — [Zenodo 20001206](https://zenodo.org/records/20001206). The Kaggle Zaker labels come from "rule-based keyword heuristics" — [Kaggle](https://www.kaggle.com/datasets/mahendradata/web-server-access-logs-labeled). The 30-day ModSecurity data is labeled by CRS alerts; the most frequent rules counted here are protocol-enforcement/restricted-file rules (920xxx/930130), not injection rules — [Zenodo 17178461](https://zenodo.org/records/17178461).
- CSIC 2010 re-uploads/derivatives found on HF: `ittailup/csic`, `b1nch3f/csic-dataset`, `bridge4/CSIC2010_dataset_classification`, `nquangit/CSIC2010_dataset_classification`, `vyykaaa/csic2010-soc-clean`, `arbk2023/csic_2010`, plus `SecureAI-SE/http-attack-requests` built on CSIC envelopes. — [HF API search "csic"](https://huggingface.co/api/datasets?search=csic); [HF SecureAI-SE](https://huggingface.co/datasets/SecureAI-SE/http-attack-requests)
- CSIC 2010 re-uploads/bundles found on Kaggle: `ispangler/csic-2010-web-application-attacks`, `rishirajmukati/csic2010`, `pazzinga/csic2010` (labeled MIT), `aaliyah06/csic2010`, `ivoguerreirorosa/http-dataset-csic-2010-clone`, `chentemp123456/csicdataset`, `teddylegessemunea/csic-ecml-combined-dataset`, `sambitmssu/ats-waf-classifier` ("sourced from CSIC 2010, ECML/PKDD 2007, and demo shop traffic"), `phungvannamanh/waf-dataset` (CSIC, HttpParams, SQLiV3, XSS, ECML files), `khoilv2005/waf-data` (CSIC + LSNM_2024 network flows, license "Unknown"). — [Kaggle API search](https://www.kaggle.com/api/v1/datasets/list?search=csic); [Kaggle sambitmssu](https://www.kaggle.com/datasets/sambitmssu/ats-waf-classifier); [Kaggle phungvannamanh](https://www.kaggle.com/datasets/phungvannamanh/waf-dataset); [Kaggle khoilv2005](https://www.kaggle.com/datasets/khoilv2005/waf-data)
- Duplicate copies: seven HF repos named `*/web-attacks-multiclass` were all last modified on 15 Jun 2026 (e.g. `ola-melin-dt`, `sirlath`, `kblanchfield`, …). `ola-melin-dt` has the same 7 classes and 4,900/700/1,400 splits as SecureAI-SE. `truongp/web-attack-detection` matches `YangYang-Research/web-attack-detection` in rows and bytes. — [HF ola-melin-dt](https://huggingface.co/datasets/ola-melin-dt/web-attacks-multiclass); [HF SecureAI-SE](https://huggingface.co/datasets/SecureAI-SE/http-attack-requests); [HF truongp](https://huggingface.co/datasets/truongp/web-attack-detection)
- Tiny or off-target: `netgoat-ai/WAF-Bench` (77 rows), `darkknight25/WAF_DETECTION_DATASET` (650 WAF-fingerprinting entries with response headers, not traffic), `niklioni/web-attack-prediction` (28 engineered features, no raw requests). — [HF WAF-Bench](https://huggingface.co/datasets/netgoat-ai/WAF-Bench); [HF darkknight25](https://huggingface.co/datasets/darkknight25/WAF_DETECTION_DATASET); [Kaggle niklioni](https://www.kaggle.com/datasets/niklioni/web-attack-prediction)
- The HF search for "ssrf"/"xss" returned dozens of 2026 repos named like `ssrf-escalation-NN`, `xss-probe…`, `dsview-xss-…`. Their names suggest probes of the HF dataset viewer, not datasets. — [HF API search "ssrf"](https://huggingface.co/api/datasets?search=ssrf)
- Names in the brief that **do not exist** as HTTP-request datasets: no "CICWAF", "HTTP-ATTACK-2023" or "BIG-WAF" dataset turned up in HF/Kaggle/Zenodo API searches or web searches. "WEB-IDS23" exists but is flow-only. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)

### Inferences
- Any dataset whose two classes come from different apps, hosts or templates should be treated as leaky until a header-stripped / endpoint-grouped evaluation shows otherwise. This matches the project's existing "kaynak sızıntısı" (source leakage) rule and its content-group splits (`docs/http-veri-ayrimi.md`).
- For openappsec specifically, two mitigations would stop a model separating classes by header count or Host: strip or normalize non-payload headers, and re-inject the malicious payloads into legitimate request envelopes.
- Using the 30-day ModSecurity data as "anomalous" ties labels to CRS's definition. That includes protocol anomalies (numeric Host header, restricted file extensions) that are arguably scanner noise, which is close to CSIC's broad "anomalous" meaning but not identical.

### Gaps
- The near-duplicate rate was not measured for any dataset here.
- No check was made of whether the openappsec legitimate set itself contains any attack-like requests (it claims 100% legitimate).
- The Kaggle 199,793-request "Web Application Attack Dataset" original upload was not identified. The `saravanan3113` upload may be a processed derivative (same label scheme, same first author's name), which is unverified.
