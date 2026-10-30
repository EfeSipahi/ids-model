# Established labeled raw-HTTP-request datasets for supervised HTTP IDS (status as of 17 Oct 2026)

Method note: URLs were checked live on 2026-10-17 with curl/HEAD requests, the GitHub/Hugging Face/Kaggle/Dataverse APIs, and HTTP range requests (zip central directories, the first bytes of CSVs). No large archive was downloaded. Some figures are marked "own count". For those, the public mirror text file was streamed through awk/wc and nothing was kept except hash keys in a scratch folder. The Internet Archive (Wayback/CDX) answered "Temporarily Offline" on 2026-10-17, so archived copies of dead pages could not be checked.

## Q1. What each dataset contains: attack types, label semantics, original split

### Takeaway
Only five sources have per-request records with a real HTTP method, path and query, headers and body: CSIC 2010, ECML/PKDD 2007, SR-BH 2020, the open-appsec WCP legitimate set, and ATRDF. Among these, CSIC 2010 and ECML/PKDD 2007 are the classic pair, and SR-BH 2020 is the largest real-traffic one. modsec-learn, Fwaf and HttpParams work at the query or parameter level. TORPEDA/CSIC 2012 is a specification plus an example set that can no longer be obtained.

### Cited Findings

**HTTP DATASET CSIC 2010 (CSIC, Madrid)**
- Built automatically from requests to a CSIC-built Spanish e-commerce app. The original 3 files are 36,000 normal training requests, 36,000 normal test requests and 25,000 anomalous requests. Anomalies were made with Paros (later OWASP ZAP) and w3af, and "some valid requests were modified with typos errors in parameters". The README adds: "we do not know how real attacks and anomalous traffic distribute in this dataset." — [msudol mirror, OriginalDataSets README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/README.md)
- The CSIC authors' own comparison table lists these attack types for CSIC2010: SQL injection, XSS, buffer overflow, SSI, directory browsing and parameter tampering. LDAP, XPath and OS-command injection are absent. — [TORPEDA paper, RECSI 2012, Cuadro I](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- The authors describe CSIC2010 as "creado artificialmente por nuestro grupo" (artificially created by our group), with web requests to an e-commerce application, built to evaluate a WAF. — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- Raw record format: a request line with an absolute URL (`POST http://localhost:8080/tienda1/publico/anadir.jsp HTTP/1.1`), about 12 headers including `Cookie: JSESSIONID=...`, and a urlencoded body after a blank line for POST. Values are Latin-1 percent-encoded (e.g. `Jam%F3n+Ib%E9rico`). — [msudol README example](https://github.com/msudol/Web-Application-Attack-Datasets)
- Original split: the training file holds normal requests only, built for anomaly detection. The GSI (Univ. de la República, Uruguay) re-packaging keeps 36,000 valid training, 36,000 valid test and 25,065 attack test requests, labelled "Valid"/"Attack" with a "Start - Id"/"End - Id" wrapper. — [msudol mirror csic_2010 README (cloned from GSI GitLab)](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010)
- **"CSIC2010 v2" (223,585 records)**: Urda et al. describe "CSIC2010 v2" as 223,585 samples × 18 features, 104,000 normal and 119,585 attacks. They group rows by the cookie into 13,569 session samples (4,303 normal, 9,266 attack) and rebuild the full payload "by joining the value of the payload variable of samples belonging to the same session". Their variables include "method" (GET/POST/PUT) and "payload" (key=value strings). Their citation for v2 is the CSIC page archived at `https://web.archive.org/web/20140128044520/http://www.iec.csic.es/dataset/`. — [arXiv 2412.16791](https://arxiv.org/abs/2412.16791)
- The 2026 X-WAD paper treats "CSIC2010" and "CSIC2010v2" ("The CSIC 2010 dataset, in v2 version") as two separate evaluation datasets. — [X-WAD, arXiv 2608.27172](https://arxiv.org/abs/2608.27172)

**CSIC TORPEDA 2012 / "CSIC2012"**
- TORPEDA (TORrano PErez DAtaset; Torrano-Giménez, Pérez-Villegas, Álvarez, CSIC) is an open XML specification for labelled WAF evaluation datasets. Each sample is labelled **normal / anómala / ataque** plus an attack category. "Anomalous" means a request that looks legitimate but carries unexpected data, such as fuzzing or user typos (e.g. `cantidad=-10`). — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- The example set CSIC2012 has "aproximadamente 8.500 peticiones normales, 15.000 peticiones anómalas y 55.000 ataques" (about 8,500 normal, 15,000 anomalous and 55,000 attack requests). It targets an in-house e-commerce app. Normal traffic came from manual browsing plus WebScarab; attacks came from w3af, ZAProxy, sqlmap, XSSer and Nikto. Attacks were placed in the path, query, cookies, other headers and the body. Categories: SQLi, XSS, buffer overflow, format string, LDAP, OS commanding, HTTP splitting, LFI, SSI, XPath, CRLF, directory browsing, parameter tampering. The traffic was captured with tcpdump and converted from pcap to XML. — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- The paper says the XML files and the script can be downloaded from `http://iec.csic.es/torpeda/` (ref [15]). — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)

**ECML/PKDD 2007 Discovery Challenge ("Analyzing Web Traffic")**
- Organised by LIRMM, EMA LGI2P, Univ. Montpellier 2 and Bee-Ware. 50,000 samples, about 20% attacks, and 10% of the attacks are "out of context". XML format. Each sample has an id plus Context (OS, HTTP server, XPath understood, LDAP present, SQL present), Class (`type` ∈ Valid, XSS, SqlInjection, LdapInjection, XPathInjection, PathTransversal, OsCommanding, SSI; `inContext`; `attackIntervall` giving the attack location in uri/query/body/header) and the query (method, protocol, uri, query, headers, body). — [LIRMM challenge page](https://www.lirmm.fr/pkdd2007-challenge/)
- The normal traffic is real recorded traffic that was then sanitised: "renaming every url, parameters names and values with randomly generated strings". — [msudol OriginalDataSets README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/README.md)
- The GSI re-split holds 35,006 normal and 15,110 attack requests. The train file has 24,504 valid requests only; the test file has 10,502 valid and 15,110 attacks. — [msudol ecml_pkdd README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/ecml_pkdd/README.md). Own count of `xml_train.txt` confirms 24,504 records, all `class: Valid` — [mirror file](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/ecml_pkdd/dataset_ecml_pkdd_train_test)
- Results paper: Raïssi C. et al., "Web Analyzing Traffic Challenge: Description and Results", ECML/PKDD'2007 Discovery Challenge, pp. 47–52. — [HAL lirmm-00168955](https://hal-lirmm.ccsd.cnrs.fr/lirmm-00168955)

**SR-BH 2020 multi-label dataset (Univ. de Alcalá / UNIR)**
- Requests to a WordPress VM exposed to the Internet for 12 days in July 2020, logged by ModSecurity 2.9.2 with CRS 3.3.0 in detection-only mode. Labels were reviewed "manually and semi-automatically" with CAPEC categories. 907,814 requests: 525,195 normal and 382,619 anomalous; "24 different features and a set of 13 labels". — [Harvard Dataverse doi:10.7910/DVN/OGOIXX](https://doi.org/10.7910/DVN/OGOIXX) (metadata via [Dataverse API](https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/OGOIXX))
- The single CSV file has this header (read via a range request on 2026-10-17): `timestamp, src_ip, src_port, dst_ip, dst_port, request_http_method, request_http_request, request_http_protocol, request_user_agent, request_referer, request_host, request_origin, request_cookie, request_content_type, request_accept, request_accept_language, request_accept_encoding, request_do_not_track, request_connection, request_body, response_http_protocol, response_http_status_code, response_http_status_message, response_content_length`. Then come 14 one-hot label columns: `000 - Normal, 272 - Protocol Manipulation, 242 - Code Injection, 88 - OS Command Injection, 126 - Path Traversal, 66 - SQL Injection, 16 - Dictionary-based Password Attack, 310 - Scanning for Vulnerable Software, 153 - Input Data Manipulation, 248 - Command Injection, 274 - HTTP Verb Tampering, 194 - Fake the Source of Data, 34 - HTTP Response Splitting, 33 - HTTP Request Smuggling`. Example first row: `GET / HTTP/1.1`, host `test-site.com`, src 172.26.0.1 → dst 172.26.0.4:80, label `000 - Normal`=1. — [Dataverse file 6319496](https://dataverse.harvard.edu/api/access/datafile/6319496)
- Associated article: Computers & Security, doi 10.1016/j.cose.2022.102788. — [Dataverse metadata](https://doi.org/10.7910/DVN/OGOIXX)

**open-appsec WAF Comparison Project (WCP) datasets (the benign source behind modsec-learn)**
- Legitimate set: "1,040,242 different HTTP requests from 185 real-web sites in 12 categories". It was recorded by browsing real sites and doing actions such as sign-up and add-to-cart, "ensuring the presence of 100% legitimate requests". Malicious set: 73,924 payloads (SQLi, XSS, XXE, path traversal, command execution, Log4Shell, Shellshock) taken from the mgm security partners "WAF Payload Collection". The README says the sets "will be updated annually". — [WCP README](https://github.com/openappsec/waf-comparison-project)
- Remote zip listing (range requests): `legitimate.zip` holds 692 files `Legitimate/browsing_2024_<site>.json`, 7,317,200,331 bytes uncompressed. Each record is `{"method","url","headers":{...},"data"}`; for example `POST /api/monitoring?...` carries full Chrome 129 headers (host, sec-ch-ua, origin, referer, cookie...) and a JSON body. `malicious.zip` holds 7 files (cmdexe, log4shell, shellshock, sqli, traversal, xss, xxe; 21,738,538 bytes uncompressed) with records like `{"method":"GET","url":"/?p=<urlencoded payload>","headers":{"User-Agent":"...Firefox/105.0","Connection":"close"},"data":""}`. — [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip), [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)

**pralab/modsec-learn-dataset ("ModSec-Learn: Boosting ModSecurity with Machine Learning", Scano et al.)**
- 508,529 legitimate samples from the open-appsec dataset. Because open-appsec had only 458 SQLi payloads, SQLi was augmented from HTTP Params, a Kaggle SQLi set (sajid576) and sqlmap with tamper scripts, for 30,543 SQLi in total. The experiments use a balanced 25,000/25,000 subset: train 20k benign + 20k SQLi, test 5k + 5k with no overlap. The legitimate source is cited as `github.com/openappsec/waf-comparison-project/tree/main/Data`. — [arXiv 2406.13547](https://arxiv.org/abs/2406.13547)
- Repo files: `legitimate/openappsec/legitimate_1..6.json` (about 185 MB total), plus `malicious/{httpparams,sqli_kaggle,sqlmap,openappsec}/sqli_parsed.json` and `merge.py`. Content is a JSON list of **URL-encoded query strings only**, e.g. `"v=1645527473"`, `"source%5Baction%5D=show&..."`. The malicious records are `"p=<payload>"`. — [GitHub repo](https://github.com/pralab/modsec-learn-dataset) (own inspection of [legitimate_1.json](https://raw.githubusercontent.com/pralab/modsec-learn-dataset/main/legitimate/openappsec/legitimate_1.json) and [sqlmap/sqli_parsed.json](https://raw.githubusercontent.com/pralab/modsec-learn-dataset/main/malicious/sqlmap/sqli_parsed.json))
- The paper's announced URL `github.com/pralab/http-traffic-dataset` now redirects to `pralab/modsec-learn-dataset`. — [GitHub API](https://github.com/pralab/http-traffic-dataset)

**Fwaf (faizann24)**
- `goodqueries.txt` (24.1 MB) and `badqueries.txt` (3.4 MB) plus `script.py`. One URL path+query per line, e.g. `/top.php?stuff='uname >q36497765 #`, `/javascript/nets.png`. No method, headers or body. — [GitHub repo](https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall)

**HttpParamsDataset (Morzeux)**
- Parameter values only, from a diploma thesis. 19,304 `norm` and 11,763 `anom` (sqli 10,852, xss 532, cmdi 89, path-traversal 290). Benign values come from CSIC2010 benign requests; attacks come from sqlmap, xssya, Vega and FuzzDB. Columns: `payload,length,attack_type,label`. — [GitHub README](https://github.com/Morzeux/HttpParamsDataset)

**Other full-request datasets found**
- **ATRDF – API Traffic Research Dataset Framework** (Ariel University / Cisco API Security Detection Challenge 2023, Shmuel Lavian). Four datasets of "HTTP traffic of API requests and responses" as JSON inside `.7z` files (train + unlabelled validation). Labels: Benign/Malware, plus attack types Cookie Injection, Directory Traversal, LOG4J, Log Forging, RCE, SQL Injection, XSS. — [GitHub repo + README](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)
- **Biblio-US17** (Univ. Sevilla / Granada NEUS-CSLab). Labelled, sanitised HTTP requests from a production library web server over 6.5 months in 2017. Fields are only `IDENTIFIER METHOD URI PROTOCOL RESP_CODE RESP_SIZE`, so there are **no headers or body**. Labels come from Snort, Nemesida and ModSecurity PL1/PL2 alerts plus manual supervision. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt); the methodology paper sanitised a 45M-request trace — [ds-biblio page](https://dtstc.ugr.es/neus-cslab/recursos/ds-biblio/)
- **WAF-A-MoLE** (AvalZ). This is a mutation fuzzer, not a request dataset. Its "datasets" are SQLi payload sets (the original WAF-A-MoLE SQLi set, Kaggle SQLiV3, and SQLiV5 from nidnogg). — [GitHub README](https://github.com/AvalZ/WAF-A-MoLE). `pralab/waf-a-mole` and `AI-secure/WAF-A-MoLE` return 404 — [GitHub](https://github.com/pralab/waf-a-mole)

### Inferences
- Read CSIC "anomalous" as "deviation from the normal profile of one app", not "attack". It mixes attacks with typo or out-of-range values, and per-request sub-labels do not exist (the GSI README says the distribution is unknown). TORPEDA later split "anomalous" and "attack" into separate labels, which supports this reading.
- CSIC2010 "v2" looks like a **parameter-level or tabular expansion** of CSIC 2010, not a different raw capture. The evidence: 18 tabular variables, a "payload" variable that has to be re-joined per session, and 223,585 rows against 97,065 raw requests. The 104,000 / 119,585 split does not decompose into the official file sizes. This is an inference; no source documents how v2 was built.
- ECML/PKDD normal traffic is real, but random-string renaming removed natural vocabulary, so token-level features learned on ECML transfer poorly.

### Gaps
- The official CSIC dataset page text (label definitions such as "static/dynamic attacks, unintentional illegal requests", and any terms) could not be re-read on 2026-10-17: the host was unreachable and Wayback was offline.
- No primary documentation was found for who built "CSIC2010 v2", where it is hosted, or how 104,000/119,585 were derived.
- Whether ECML samples can carry several class labels ("multi-label") was not confirmed. The LIRMM page shows a single `type` element per sample.
- ATRDF per-dataset record counts and exact JSON schema were not verified, because the 7z archives were not downloaded.

## Q2. Which datasets are downloadable today (Oct 2026), from where, and under what license?

### Takeaway
SR-BH 2020 (Harvard Dataverse, CC0), the open-appsec WCP sets (live zips, benign part Apache-2.0) and the GitHub mirrors of CSIC 2010 and ECML/PKDD 2007 can all be downloaded today. The official CSIC host (dataset and TORPEDA) did not respond on 17 Oct 2026, and the LIRMM ECML data page returns HTTP 500. CSIC and ECML have no verifiable license: they effectively survive only as third-party mirrors.

### Cited Findings
- **CSIC official**: `https://www.tic.itefi.csic.es/dataset/` → port 443 "connection refused", port 80 timed out after 20 s. `www.isi.csic.es` resolves to 161.111.32.51 and also timed out. TORPEDA (`/torpeda/`) is on the same host and was equally unreachable. — own curl checks 2026-10-17 of [CSIC dataset page](https://www.tic.itefi.csic.es/dataset/) and [TORPEDA page](https://www.tic.itefi.csic.es/torpeda/). Search engines still index `torpeda/about.html` and `torpeda/tools.html` ("PCap to XML") — [search result listing](https://www.tic.itefi.csic.es/torpeda/tools.html)
- **CSIC mirrors (verified live)**:
  - GitHub `msudol/Web-Application-Attack-Datasets`: the 3 original txt files (20,148,988 / 20,151,204 / 15,734,523 bytes), the GSI-formatted `dataset_cisc_train_test.tar.gz`, CSV and ARFF conversions. Repo license GPL-3.0, last push 2024-06-27. — [GitHub](https://github.com/msudol/Web-Application-Attack-Datasets)
  - Upstream GSI GitLab `gitlab.fing.edu.uy/gsi/web-application-attacks-datasets` → HTTP 200. — [GitLab](https://gitlab.fing.edu.uy/gsi/web-application-attacks-datasets)
  - Kaggle `ispangler/csic-2010-web-application-attacks`: `csic_database.csv` (29,539,583 bytes, created 2019-10-11, 7,432 downloads, license field "Data files © Original Authors"). The description says "I did my best to produce a .csv… still need some work". — [Kaggle](https://www.kaggle.com/datasets/ispangler/csic-2010-web-application-attacks) (metadata via [Kaggle API](https://www.kaggle.com/api/v1/datasets/view/ispangler/csic-2010-web-application-attacks))
  - Kaggle `ivoguerreirorosa/http-dataset-csic-2010-clone`: raw txt `csic_complete/{normalTrafficTraining, normalTrafficTest, anomalousTrafficTest}.txt` (20,640,988 / 20,599,204 / 16,090,299 bytes), 2026-09-13. Other Kaggle copies include `rishirajmukati/csic2010`, `pazzinga/csic2010` (tagged "MIT"), `aaliyah06/csic2010`, `chentemp123456/csicdataset` and `mtasfi/csic2010-flow-matched-replay` (2026-10-07). — [Kaggle API search "csic"](https://www.kaggle.com/api/v1/datasets/list?search=csic)
  - Hugging Face `bridge4/CSIC2010_dataset_classification` (parquet, columns `requests,label`; train 43,254 / test 18,538, ungated, modified 2024-07-21); `bridge4/CSIC2010_dataset_domain_adaptation` (36,000 rows, `requests` only); `ittailup/csic` (one `text` column, 30,929 rows, 929 MB). — [HF API bridge4 classification](https://huggingface.co/datasets/bridge4/CSIC2010_dataset_classification), [bridge4 domain adaptation](https://huggingface.co/datasets/bridge4/CSIC2010_dataset_domain_adaptation), [ittailup/csic](https://huggingface.co/datasets/ittailup/csic)
- **CSIC license**: no license or terms text could be retrieved from any primary source. Mirrors label it inconsistently: "© Original Authors" (ispangler), "MIT" (pazzinga), GPL-3.0 at repo level (msudol). — [Kaggle API](https://www.kaggle.com/api/v1/datasets/list?search=csic); [msudol](https://github.com/msudol/Web-Application-Attack-Datasets)
- **ECML/PKDD 2007**: the challenge page is live (HTTP 200). Its "Data" link `http://www.lirmm.fr/pkdd2007-challenge/Donnees/index.html` returns **HTTP 500**, and guessed file names under `/Donnees/` also return 500. The main page links `accord_confidentialite.html` (confidentiality agreement), `corpus/donnees.html` and `resultats.html`, all **404**. — own checks of [LIRMM page](https://www.lirmm.fr/pkdd2007-challenge/) and [Donnees link](http://www.lirmm.fr/pkdd2007-challenge/Donnees/index.html)
- The CSIC authors wrote in 2012 that ECML downloads were "restringida bajo usuario y contraseña" (restricted behind a username and password). — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- **ECML mirrors**: `msudol/.../OriginalDataSets/ecml_pkdd/learning_dataset_xml.zip` (19,954,936 B, the original XML), the GSI-formatted `dataset_ecml_pkdd_train_test.tar.gz` (33,462,529 B), and the unpacked `xml_train.txt` (40,658,137 B) and `xml_test.txt` (42,041,312 B). — [GitHub tree](https://github.com/msudol/Web-Application-Attack-Datasets). No Kaggle mirror turned up in a Kaggle API search for "ecml pkdd". — [Kaggle API search](https://www.kaggle.com/api/v1/datasets/list?search=ecml%20pkdd)
- **SR-BH 2020**: Harvard Dataverse doi:10.7910/DVN/OGOIXX, version 1.2, released 2022-06-06, **CC0 1.0**, not restricted, no terms of access. One file, `data_capec_multilabel.csv`: 436,437,661 bytes, md5 `173ec515308bdce5aec19cfd5b792596`. The access URL answered 303 to a signed S3 URL, and a ranged GET returned the CSV header. — [Dataverse](https://doi.org/10.7910/DVN/OGOIXX); [API metadata](https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/OGOIXX). The X-WAD repo pins sha256 `9c73c90ce6564ae48b14f7179cd864d037a6a130ef69c68c1626ec5d7ce4a910` for the same file. — [mattebit/x-wad README](https://github.com/mattebit/x-wad)
- SR-BH mirror: Kaggle `hado313/sr-bh2020` has the same file name and identical byte size (436,437,661), license "Unknown", 2026-06-27. — [Kaggle API](https://www.kaggle.com/api/v1/datasets/list/hado313/sr-bh2020). The university portal lists it as Dataverse V1.2 CC0 — [UAH portal](https://portalcientifico.uah.es/documentos/668fc479b9e7c03b01bde810). No Mendeley Data record for SR-BH was found.
- **open-appsec WCP**: `legitimate.zip` → HTTP 200, 1,203,983,791 bytes, Last-Modified 2024-12-01. `malicious.zip` → HTTP 200, 452,537 bytes, Last-Modified 2023-07-17. — own HEAD checks of [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip) and [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip). README: "The Legitimate Requests Dataset and the Tooling are available under Apache 2.0 license. The Malicious Requests Dataset is a collection of datasets assembled by MGM with different copyrights, mostly under MIT." Repo license Apache-2.0, last push 2026-02-11. — [WCP README](https://github.com/openappsec/waf-comparison-project). The payload repo `openappsec/mgm-web-attack-payloads` itself carries **GPL-3.0** — [GitHub](https://github.com/openappsec/mgm-web-attack-payloads), which conflicts with "mostly MIT".
- **modsec-learn**: repo live, **no license file** (GitHub `license: null`), about 90 MB, last push 2024-09-23. The README's BibTeX block is empty. — [GitHub](https://github.com/pralab/modsec-learn-dataset). The arXiv paper itself is CC BY 4.0, which says nothing about the data. — [arXiv 2406.13547](https://arxiv.org/abs/2406.13547)
- **Fwaf**: live, **no license**, last push 2017-05-15. — [GitHub](https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall)
- **HttpParamsDataset**: live, **MIT**, last push 2020-09-04. — [GitHub](https://github.com/Morzeux/HttpParamsDataset)
- **ATRDF**: live, no license file (CITATION.cff only, date-released 2023-01-01), 7z files 0.2–55 MB each, last push 2025-04-20. — [GitHub](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)

### Inferences
- If redistribution matters (e.g. committing a `data/http-mini/` subset to the repo), only SR-BH (CC0), the open-appsec legitimate set (Apache-2.0) and HttpParams (MIT) have explicit licenses. CSIC and ECML have none. ECML was originally behind a login and a confidentiality-agreement page, so redistributing ECML subsets is the riskiest choice.
- The practical CSIC source today is the msudol/GSI mirror or the Kaggle raw clone. Record the mirror and its file hashes in the project docs, since the official site may be permanently gone.
- The two raw CSIC mirrors differ by about 492 KB per normal file, e.g. 20,640,988 vs 20,148,988 bytes. That is consistent with CRLF vs LF line endings (about 13–14 lines × 36,000 requests). This is an inference; the files were not diffed.

### Gaps
- No primary license or terms for CSIC 2010, TORPEDA or ECML/PKDD 2007 could be found.
- Whether the CSIC outage is temporary could not be determined (Wayback offline).
- The legitimate.zip version used by modsec-learn (508,529 samples, cited at a `tree/main/Data` path that no longer exists in the repo) cannot be matched to the current 2024 release.

## Q3. Exact record counts and class balance per file/split

### Takeaway
CSIC 2010 has 97,065 raw requests (72,000 normal + 25,065 anomalous), but only about 35,000 are distinct by request line + body. ECML/PKDD has 50,116 (35,006 / 15,110). SR-BH has 907,814 (525,195 / 382,619), and about 13.8% of its "normal" labels have been challenged. open-appsec has 1,040,242 benign requests and 73,924 attack payloads.

### Cited Findings
- **CSIC 2010, own count** (streamed from the msudol mirror; a record starts at a `GET|POST|PUT http` request line):

  | File | Records | Methods | Distinct by request line + body |
  |---|---|---|---|
  | `normalTrafficTraining.txt` | 36,000 | — | 9,644 |
  | `normalTrafficTest.txt` | 36,000 | GET 28,000, POST 8,000 | 9,622 |
  | `anomalousTrafficTest.txt` | 25,065 | GET 15,088, POST 9,580, PUT 397 | 15,964 |

  Source: [mirror files](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010)
- CSIC cross-file overlap, own count: 626 distinct request+body keys occur in both normal files, covering **26,704 of the 36,000 normal-test records**. No anomalous request has an exact request-line+body match in either normal file. — same [mirror files](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010)
- The 61,065-request CSIC total often quoted (36,000 benign + 25,065 malicious) leaves out one of the two normal files. — [JIS EURASIP table (search snippet)](https://jis-eurasipjournals.springeropen.com/articles/10.1186/s13635-025-00210-w/tables/7)
- The HF `bridge4` split is 43,254 + 18,538 = 61,792 rows, which matches neither 61,065 nor 97,065. — [HF dataset card](https://huggingface.co/datasets/bridge4/CSIC2010_dataset_classification)
- CSIC2010 v2: 223,585 rows = 104,000 normal + 119,585 attack; session-grouped version 13,569 = 4,303 + 9,266. — [arXiv 2412.16791](https://arxiv.org/abs/2412.16791)
- CSIC2012 / TORPEDA: about 8,500 normal, 15,000 anomalous and 55,000 attacks. — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf)
- ECML/PKDD 2007: the official page gives 50,000 with about 20% attacks — [LIRMM](https://www.lirmm.fr/pkdd2007-challenge/). The GSI re-split gives 35,006 valid + 15,110 attacks = 50,116, with train 24,504 valid and test 10,502 valid + 15,110 attack — [msudol ecml README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/ecml_pkdd/README.md). Own count of the train file: 24,504, all `Valid`.
- ECML/PKDD per-class counts, own count of the GSI `xml_test.txt`: Valid 10,502; OsCommanding 2,302; PathTransversal 2,295; LdapInjection 2,279; XPathInjection 2,279; SqlInjection 2,274; SSI 1,856; XSS 1,825. The attack classes sum to 15,110, which matches the README. — [mirror file](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/ecml_pkdd/dataset_ecml_pkdd_train_test)
- SR-BH 2020: 907,814 = 525,195 normal + 382,619 anomalous (57.9% / 42.1%). — [Dataverse](https://doi.org/10.7910/DVN/OGOIXX). A CyShield post quotes 907,816. — [search snippet of CyShield post](https://seclab.cyshield.com/posts/augmenting-sr-bh-2020-a-technical-methodology-for-modern-threat-simulation/)
- SR-BH fix: the X-WAD `mislabeled_indexes.csv` lists **126,003** row indexes changed from normal to anomalous (own `wc -l` minus the header), about 13.9% of 907,814. The paper says "approximately 13.8% of the dataset is mislabeled". — [X-WAD repo file](https://github.com/mattebit/x-wad/blob/main/experiments/srbh2020/mislabeled_indexes.csv); [arXiv 2608.27172](https://arxiv.org/abs/2608.27172)
- open-appsec: 1,040,242 legitimate requests (185 sites, 12 categories) and 73,924 malicious payloads in 7 attack families — [WCP README](https://github.com/openappsec/waf-comparison-project). The malicious.zip file sizes run xss 12.6 MB > traversal 8.0 MB > cmdexe 0.74 MB > sqli 0.27 MB > log4shell 69 KB > xxe 37 KB > shellshock 15 KB, so the set is dominated by XSS and traversal. — own zip listing of [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)
- modsec-learn: 508,529 legitimate and 30,543 SQLi; experimental subset 25k/25k (train 20k/20k, test 5k/5k). — [arXiv 2406.13547](https://arxiv.org/abs/2406.13547)
- Fwaf, own count: `goodqueries.txt` 1,294,531 lines (1,265,994 unique), `badqueries.txt` 48,126 lines (44,713 unique). — [GitHub](https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall)
- HttpParams, own count: `payload_full.csv` 31,067 rows (norm 19,304; sqli 10,852; xss 532; cmdi 89; path-traversal 290; all payloads unique); `payload_train.csv` 20,712 (norm 12,870 / sqli 7,235 / xss 355 / cmdi 59 / pt 193); `payload_test.csv` 10,355 (6,434 / 3,617 / 177 / 30 / 97). The README's "over 3100 values" is a typo for about 31,000. — [GitHub](https://github.com/Morzeux/HttpParamsDataset)
- ATRDF README baseline tables give *test-split support* only (e.g. dataset 2: 20,812 benign / 1,692 malware; dataset 4 label phase: 5,019 / 5,575). — [GitHub README](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)

### Inferences
- After exact-duplicate removal, CSIC has about 19,266 distinct normal and 15,964 distinct anomalous requests (roughly 45% / 55%, before removing the 626 keys shared between the two normal files). The usable supervised dataset is therefore much smaller than "97k". Any random split without grouping leaks heavily: 74% of normal-test records have an exact copy in normal-train. The project's existing content grouping (`docs/http-veri-ayrimi.md`) is essential when scaling up.
- SR-BH's effective class balance after the X-WAD fix is about 399k normal vs about 509k anomalous (525,195 − 126,003 and 382,619 + 126,003). That is computed, not published.

### Gaps
- The original LIRMM XML (`learning_dataset_xml.zip`) was not counted directly; per-class figures above come from the GSI re-formatted txt. The `inContext=FALSE` count is also unverified.
- CSIC distinct counts *including headers* were not computed: the key ignored headers, so requests that differ only in Cookie or Content-Length are collapsed.
- Duplicate rates for SR-BH, open-appsec and ATRDF were not measured (no full download).
- The Kaggle `ispangler` CSV row count was not verified.

## Q4. Which contain full headers + body vs only URL/query?

### Takeaway
Full method + path + query + headers + body: CSIC 2010 (raw txt), ECML/PKDD 2007 (XML), open-appsec WCP legitimate (JSON), and ATRDF (JSON with responses). SR-BH 2020 has method, path+query, body and **11 selected headers** (not the full header block). The open-appsec malicious set, modsec-learn, Fwaf, HttpParams and Biblio-US17 are URL/query- or parameter-level only.

### Cited Findings
- CSIC 2010 raw: request line + about 12 headers + body for POST/PUT. — [msudol README example](https://github.com/msudol/Web-Application-Attack-Datasets)
- ECML/PKDD: method, protocol, uri, query, headers, body. — [LIRMM](https://www.lirmm.fr/pkdd2007-challenge/). The header set is randomised and exotic (e.g. `Content-MD5`, `UA-CPU: MIPS`, `Warning:`, `Via: HTTP/5.7`) with obfuscated values. — [msudol README example](https://github.com/msudol/Web-Application-Attack-Datasets)
- SR-BH: columns `request_http_method`, `request_http_request`, `request_http_protocol`, 11 header columns (user_agent, referer, host, origin, cookie, content_type, accept, accept_language, accept_encoding, do_not_track, connection), `request_body`, plus network and response fields. **There is no `full_http_request` column** in the Dataverse CSV header. — [Dataverse file](https://dataverse.harvard.edu/api/access/datafile/6319496)
- open-appsec legitimate: `method`, `url` (path+query), full browser `headers` dict, `data` body. open-appsec malicious: `GET /?p=<payload>` with only `User-Agent` and `Connection` headers and an empty body. — own zip sampling of [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip) and [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)
- modsec-learn: query-string lists only (`"v=1645527473"`, `"p=<sqli>"`). — [GitHub](https://github.com/pralab/modsec-learn-dataset)
- Fwaf: path+query lines only. — [GitHub](https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall). HttpParams: parameter values only. — [GitHub](https://github.com/Morzeux/HttpParamsDataset). Biblio-US17: METHOD URI PROTOCOL + response code/size only. — [README.txt](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- ATRDF: "All the datasets contain HTTP traffic of API requests and responses". — [GitHub README](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)

### Inferences
- The project's `docs/aday-veri-setleri.md` contains errors on these points. It says SR-BH's raw request is in a `full_http_request` column; the official CSV has split columns with a selected header subset. It calls modsec-learn's normal data "realistic normal traffic" requests; in the repo these are query strings only. The full-request version of that benign data is the newer open-appsec `legitimate.zip`.
- For a feature extractor that reads path, query, form body and headers, CSIC 2010, ECML/PKDD, SR-BH, open-appsec legitimate and ATRDF are directly usable. The query-level sets can only test the query/parameter features.

### Gaps
- The exact ATRDF JSON field names and whether request bodies are included in all four datasets were not verified.

## Q5. Known flaws (synthetic origin, label semantics, trivially separable artifacts, duplicates)

### Takeaway
Every established set has serious flaws:
- **CSIC 2010**: one synthetic Spanish app, an "anomalous" class that is not purely attacks, and massive exact duplication with train/test leakage.
- **ECML**: random-string obfuscation and random headers.
- **SR-BH**: about 13.8% of rows flagged as mislabeled normals, a single WordPress site, and network/response columns that can leak the label.
- **open-appsec benign vs WCP malicious**: trivially separable by header shape.
- **Query-level sets**: carry no header or body signal at all.

### Cited Findings
- CSIC: "entirely generated from a lab environment, so HOST information is all the same" and there is no date/time information. — [msudol README](https://github.com/msudol/Web-Application-Attack-Datasets)
- CSIC anomalous includes typo-modified valid requests, with an unknown attack vs anomaly breakdown. — [OriginalDataSets README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/README.md). Search summaries cite critics of its "single-application, single-client scope" and 2010 age. — [arXiv 2412.16791 (search summary)](https://arxiv.org/abs/2412.16791)
- CSIC duplication: 36,000 → 9,644 distinct normal-train records, 36,000 → 9,622 normal-test, 25,065 → 15,964 anomalous. 26,704 normal-test records duplicate normal-train content (own count, see Q3). — [mirror files](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010)
- CSIC method artifact: all 397 PUT requests in the corpus are in the anomalous file (the normal-test file is GET/POST only; own count). — [mirror files](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010)
- ECML: values and names are random strings, and the dataset cannot be used for anomaly-based evaluation because the target application is unknown (TORPEDA authors). The CSIC authors also say it "sólo contiene seis categorías de ataques" (only six attack categories), while the LIRMM page lists seven attack classes. — [TORPEDA paper](https://recsi2012.mondragon.edu/es/programa/recsi2012_submission_73.pdf); [LIRMM](https://www.lirmm.fr/pkdd2007-challenge/). About 10% of attacks are "out of context" (e.g. an attack class that does not apply to the server context). — [LIRMM](https://www.lirmm.fr/pkdd2007-challenge/)
- SR-BH labels: X-WAD's explainability analysis found "approximately 13.8% of the dataset is mislabeled". The fix "reclassif[ied] normal samples as anomalous if they exhibited the identified attack patterns". Only a subset was manually inspected, so "some benign samples may have been incorrectly relabeled as anomalous". — [arXiv 2608.27172](https://arxiv.org/abs/2608.27172). The index list is published (Apache-2.0 repo). — [mattebit/x-wad](https://github.com/mattebit/x-wad/tree/main/experiments/srbh2020)
- SR-BH labels (independent): CyShield SecLab (Omar Elebiary, July 2026) reports that "many rows labelled as 'benign' were mislabeled" and relabelled them with scripts plus Qwen3-8B. The post URL returned **404** on 2026-10-17, so this is known only from a search snippet. — [CyShield post (dead link)](https://seclab.cyshield.com/posts/augmenting-sr-bh-2020-a-technical-methodology-for-modern-threat-simulation/)
- SR-BH origin: a single WordPress test site (`test-site.com`), 12 days, labels seeded by ModSecurity CRS 3.3.0 alerts and then reviewed. — [Dataverse](https://doi.org/10.7910/DVN/OGOIXX); [CSV header/first row](https://dataverse.harvard.edu/api/access/datafile/6319496)
- open-appsec malicious records are synthetic `GET /?p=` requests with two headers and a Firefox/105 user-agent, while legitimate records carry about 15+ real Chrome headers from 185 hosts. — own zip sampling of [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip) and [malicious.zip](https://downloads.openappsec.io/waf-comparison-project/malicious.zip)
- modsec-learn: SQLi only, with benign and malicious from different sources (open-appsec benign vs HttpParams/Kaggle/sqlmap SQLi). — [arXiv 2406.13547](https://arxiv.org/abs/2406.13547)
- HttpParams: benign values are taken from CSIC2010 benign requests. — [README](https://github.com/Morzeux/HttpParamsDataset). Fwaf: about 2.2% duplicate lines in good and about 7.1% in bad (own count, see Q3); the benign origin is undocumented in the repo. — [GitHub](https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall)

### Inferences
- **Source-leakage risk is very high** in any open-appsec-benign + WCP-malicious or modsec-learn pairing. Header count, Host, User-Agent family and `/?p=` path shape alone would separate the classes. Use open-appsec benign only for a false-positive / cross-domain test, or inject payloads into real benign request templates.
- **SR-BH**: drop `src_ip`, `src_port`, `dst_ip`, `dst_port`, `timestamp` and all `response_*` columns before training. The example row shows Docker-internal addresses (172.26.0.x). Response codes such as 404 for scanners are post-hoc signals, not request features, which matches the project's request-only design. The X-WAD fix inflates the anomalous class where its pattern-matching relabel is wrong, so report results on both the original and the fixed labels.
- **CSIC**: PUT appearing only in anomalous traffic is a free feature, and the project's 21 features likely include the method. Check whether model gains come from this artifact.
- Combining HttpParams with CSIC creates cross-dataset leakage, because HttpParams' benign values are CSIC's.
- The ECML attack classes are almost uniform (1,825–2,302 each), which points to deliberately balanced, generated attack sets rather than a natural attack distribution. The GSI re-split also puts every attack in the test file, so a supervised user must re-split it.

### Gaps
- No published audit of ECML label noise, or of SR-BH duplicates and near-duplicates, was found.
- The CyShield findings cannot be re-verified (page 404, no archive).
- The extent of near-duplicates in CSIC (e.g. same template, different values) was not measured; only exact request-line+body duplicates were counted.

## Q6. Effort to convert each into the project's per-request JSONL (method/path/query/headers/body/label)

### Takeaway
- **Low effort**: CSIC 2010 raw txt and open-appsec legitimate JSON.
- **Low–medium**: ECML/PKDD (XML or GSI txt) and SR-BH (CSV column mapping, multi-label → binary, optional X-WAD fix).
- **Medium**: ATRDF (7z + JSON schema discovery).
- **Not meaningfully convertible**: Fwaf, HttpParams, modsec-learn and Biblio-US17. These would need synthetic request wrapping, which adds artifacts.

### Cited Findings
- CSIC raw blocks begin with `METHOD http://localhost:8080/... HTTP/1.1`, then headers, a blank line and an optional body. The label comes from the file name. Latin-1 percent-encoding is present (`%F3`, `%E9`, `%F1`). — [msudol README](https://github.com/msudol/Web-Application-Attack-Datasets)
- The GSI CSIC/ECML txt format wraps each request as `Start - Id: … / class: … / full request incl. headers and body / End - Id: …`, using ModSecurity unique ids. — [msudol csic README](https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010); [ecml README](https://github.com/msudol/Web-Application-Attack-Datasets/blob/master/OriginalDataSets/ecml_pkdd/README.md)
- ECML XML: per-sample `reqContext`, `class/type`, `inContext`, `attackIntervall`, and request `method/protocol/uri/query/headers/body`. — [LIRMM](https://www.lirmm.fr/pkdd2007-challenge/)
- SR-BH CSV: one row per request with split columns and 14 one-hot label columns (see Q1). 436 MB. — [Dataverse](https://doi.org/10.7910/DVN/OGOIXX). The fix list is indexed by `original_index` (row position). — [x-wad mislabeled_indexes.csv](https://github.com/mattebit/x-wad/blob/main/experiments/srbh2020/mislabeled_indexes.csv)
- open-appsec legitimate: 692 JSON arrays of `{method,url,headers,data}`, files of about 1.5–22 MB, 7.3 GB uncompressed. — own listing of [legitimate.zip](https://downloads.openappsec.io/waf-comparison-project/legitimate.zip)
- ATRDF: `.7z` archives with JSON; validation sets unlabeled; a baseline notebook with a log parser is provided. — [GitHub README](https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge)

### Inferences
Effort estimates are judgments, not sourced.

| Dataset | Mapping | Effort |
|---|---|---|
| CSIC 2010 | Split on request-line regex; `urlsplit` the absolute URL into path and query; headers into a dict; body = text after the blank line; label normal/anomalous by file; keep Latin-1 bytes. Must add dedup/grouping. | Low (about 50 lines; the project already parses the CSIC subset) |
| ECML/PKDD 2007 | Parse the XML (use the original zip from the mirror) or the GSI txt; label = `type != Valid`; keep `type`, `inContext`, `attackIntervall` as metadata; decide whether out-of-context attacks count as anomalous. | Low–medium |
| SR-BH 2020 | `method` = `request_http_method`; split `request_http_request` into path and query; headers from 11 columns (empty → absent); body = `request_body`; label = 1 − `000 - Normal`; keep the CAPEC vector as metadata; drop network/response columns; optionally apply X-WAD indexes. Check CSV quoting of bodies with newlines and commas. | Low–medium |
| open-appsec legitimate | Direct field rename; `url` → path + query; per-site group id from the file name (useful for grouped splits). Benign only. | Low |
| open-appsec malicious / modsec-learn / Fwaf / HttpParams | No real request context: would need templates (e.g. inject into CSIC or open-appsec benign requests), which creates synthetic artifacts. | Medium effort, low value |
| ATRDF | Extract the 7z, inspect the JSON schema, map request fields, drop responses, label = Benign/Malware. | Medium (schema unverified) |
| Biblio-US17 | Method + URI only; headers and body empty. | Low effort, partial fit |
| CSIC2010 v2 / TORPEDA 2012 | Not obtainable from a verified source. | n/a |

### Gaps
- Whether SR-BH's `request_body` and cookie fields contain embedded newlines or quoting issues that break naive CSV parsing was not checked.
- The ATRDF JSON schema was not inspected.
- Original ECML XML well-formedness and encoding were not checked; the zip was not downloaded.
