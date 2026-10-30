# PCAP and web-server log datasets that can yield labeled individual HTTP requests

Research date: 2026-10-17. Method: WebSearch/WebFetch plus Context7 for Zeek and Wireshark docs. No browser-automation MCP tool was available. No large PCAPs were downloaded. Several primary pages could not be fetched, either because WebFetch blocked the domain (hal.science, distrinet-research.be, pmc.ncbi.nlm.nih.gov, medium.com, ieee-dataport.org) or because of timeouts and errors (github.com/Yasir-ali-farrukh/Payload-Byte, idus.us.es). Facts that come only from search-result summaries are marked "(search summary)". Example commands I wrote myself are marked "(constructed, untested)", since neither tshark nor zeek is installed on this machine.

## Q1. Which datasets contain plaintext HTTP web-attack traffic (or HTTP request logs), and roughly how many attack and benign requests can be extracted?

### Takeaway
Only three sources clearly publish raw PCAPs with plaintext HTTP web attacks: CIC-IDS2017 (Thursday morning, DVWA-style brute force, XSS and SQLi), CSE-CIC-IDS2018 (two days of the same attack types against DVWA) and, more loosely, UNSW-NB15 (IXIA-generated "Exploits"/"Fuzzers"). In all three the web-attack portion is tiny: after cleaning, Engelen et al. found only 151 brute-force, 27 XSS and 12 SQLi flows with payload in CIC-IDS2017. Each of those flows carries many HTTP requests, so the request count must be measured by parsing the PCAP. WEB-IDS23 publishes flow features only, with no HTTP content. The largest labeled real-world HTTP request source found is Biblio-US17: 47.4M requests, about 328k attacks, but only method/URI/protocol/status/size, with no headers or bodies. The AIT Log Data Sets give labeled Apache access logs from multi-step attacks.

### Cited Findings

**CIC-IDS2017 (UNB/CIC)**
- The dataset page says it includes "full packet payloads in pcap format", plus labeled flows (GeneratedLabelledFlows.zip) and ML CSVs (MachineLearningCSV.zip). Per-day capture sizes: Monday 11.0G, Tuesday 11G, Wednesday 13G, Thursday 7.8G, Friday 8.3G. — [UNB CIC-IDS2017 page](https://www.unb.ca/cic/datasets/ids-2017.html)
- The download link points to http://cicresearch.ca/CICDataset/CIC-IDS-2017/. — [UNB CIC-IDS2017 page](https://www.unb.ca/cic/datasets/ids-2017.html)
- When fetched on 2026-10-17, that URL returned a CIC dataset download request form showing "Server error. Please try again later." I saw no directory listing, so the current PCAP availability could not be confirmed. — [cicresearch.ca CIC-IDS-2017](http://cicresearch.ca/CICDataset/CIC-IDS-2017/)
- Thursday 6 July 2017 web-attack windows: Brute Force 9:20–10:00, XSS 10:15–10:35, SQL Injection 10:40–10:42. Attacker: Kali 205.174.165.73. Victim: "WebServer Ubuntu" 205.174.165.68 (local IP 192.168.10.50). NAT path on the firewall: "205.174.165.73 -> 205.174.165.80 (Valid IP of the Firewall) -> 172.16.0.1 -> 192.168.10.50". — [UNB CIC-IDS2017 page](https://www.unb.ca/cic/datasets/ids-2017.html)
- The UNB page does not name DVWA as the victim application. — [UNB CIC-IDS2017 page](https://www.unb.ca/cic/datasets/ids-2017.html)
- Original vs. corrected flow counts (Engelen et al., Table I):
  - Web Brute Force: 1507 → 1365 after the TCP-appendix fix → **151** after the payload filter
  - Web XSS: 652 → 679 → **27**
  - Web SQLi: 21 → 12 → **12**
  - BENIGN: 2,271,326 → 1,823,964

  — [Engelen, Rimmer & Joosen 2021 (WTMC), KU Leuven Lirias PDF](https://lirias.kuleuven.be/retrieve/713070)
- Engelen et al.: "Manual inspection of these attacks showed that the large majority of their flows do not contain any packet data. The attacks are largely executed through a select few flows, which each of them containing many brute force or XSS attempts." — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)

**CSE-CIC-IDS2018 (CIC + AWS)**
- Download: `aws s3 sync --no-sign-request --region <your-region> "s3://cse-cic-ids2018/" dest-dir`. The data includes "the network traffic (Pcaps) and event logs" for each machine, organized by day. The page states no size. — [UNB CSE-CIC-IDS2018 page](https://www.unb.ca/cic/datasets/ids-2018.html)
- Web-attack windows (Table 2):

  | Day | Brute Force-Web | Brute Force-XSS | SQL Injection |
  |---|---|---|---|
  | Thu 22-02-2018 | 10:17–11:24 | 13:50–14:29 | 16:15–16:29 |
  | Fri 23-02-2018 | 10:03–11:03 | 13:00–14:10 | 15:05–15:18 |

  — [UNB CSE-CIC-IDS2018 page](https://www.unb.ca/cic/datasets/ids-2018.html)
- Attacker 18.218.115.60. Victim 18.218.83.150 / 172.31.69.28. Victim application: Damn Vulnerable Web App (DVWA), "PHP/MySQL web application", on an Ubuntu web server. XSS and brute force were automated with an in-house Selenium framework. — [UNB CSE-CIC-IDS2018 page](https://www.unb.ca/cic/datasets/ids-2018.html)
- Engelen et al. report that the CICIDS2017 artefact problem "is still present in the newest version of the dataset - CIC-CSE-DS2018" (search summary of the abstract). — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- The figures of roughly 611 / 230 / 87 web-attack flows that are often quoted for CSE-CIC-IDS2018 could NOT be confirmed. The search tool offered them only "from memory". — [search result context](https://cybersecurity.springeropen.com/articles/10.1186/s42400-020-00053-7/tables/1)

**UNSW-NB15**
- "The tcpdump tool was utilised to capture 100 GB of the raw traffic (e.g., Pcap files)". The pcaps, BRO (Zeek) files, Argus files, CSVs and reports are downloadable from a SharePoint link on the page. — [UNSW-NB15 project page](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
- There are nine attack categories: Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, Worms. Ground truth ships as `UNSW-NB15_GT.csv`, with the event list in `UNSW-NB15_LIST_EVENTS.csv`. — [UNSW-NB15 project page](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
- License: "Free use of the UNSW-NB15 dataset for academic research purposes is hereby granted in perpetuity". Commercial use must be agreed with the authors. — [UNSW-NB15 project page](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
- The raw packets were reportedly generated with the IXIA PerfectStorm tool in the UNSW Canberra Cyber Range Lab. Source: a third-party copy of the UNSW text, low quality. — [blink.digitalpress.blog copy](https://blink.digitalpress.blog/the-raw-network-packets-of-the-unsw-nb15-dataset-was-created-by-the-ixia-perfectstorm-tool-in-the-cyber-range-lab-of-the-australian-centre-for-cyber-security-accs-for-g)

**Packet-level relabelings of CIC-IDS2017 / UNSW-NB15 (Payload-Byte)**
- The Zenodo record "UNSW-NB15 and CIC-IDS2017 Labelled PCAP Data" (2022) contains Payload_data_CICIDS2017.csv (~4.9 GB) and Payload_data_UNSW.csv (~270.1 MB). Dimensions are "Nx1504", all columns integers. "Each packet is labelled by comparing the eight distinct features": Src/Dst IP, Src/Dst Port, Start time, End time, Protocol, TTL. License CC BY 4.0. Tool: github.com/Yasir-ali-farrukh/Payload-Byte. — [Zenodo 7258579](https://zenodo.org/records/7258579)
- The pip package `nids-datasets` advertises packet- and flow-level data for over 230 million packets: 179M from UNSW-NB15 and 54M from CIC-IDS2017 (search summary). — [PyPI nids-datasets](https://pypi.org/project/nids-datasets/0.1.4)

**WEB-IDS23 (Lanfer, Brockmann, Aschenbruck, Osnabrück)**
- Flow-level only: "We process the traffic recordings to create flow-level features". There are 82 features, and payloads appear only as statistics: "The packet payloads are extracted as statistics about the payload length". The authors recommend that future datasets "record the unencrypted payloads". — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)
- Web classes, each in HTTP and HTTPS variants (Table II):

  | Attack | HTTP | HTTPS |
  |---|---|---|
  | bruteforce | 912,503 | 865,126 |
  | sql_injection | 74,300 | 102,584 |
  | dos | 86,443 | 33,216 |
  | revshell | 8,549 | 9,404 |
  | ssrf | 5,509 | 6,656 |
  | xss | 4,558 | 4,533 |

  benign: 825,187. Total: 12,059,749 samples in 21 classes. Tools: Selenium, python-requests, sqlmap, Hydra, netcat. Samples are labeled from the generator's logs. Dataset DOI 10.26249/FK2/MOCIY8. The generator is available only on request. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)

**CIC-IoT2023**
- Web-based attack classes: SQL injection, Command injection, Backdoor malware, Uploading attack, XSS, Browser hijacking. A PCAP subdirectory holds "the original traffic captured during the attacks". TCPDump was used "to split the .pcap files in multiple smaller files". "All attacks are executed by malicious IoT devices targeting other IoT devices". The page names no target web app and gives no labeling details. Download: http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/ — [UNB CIC-IoT2023 page](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
- No authoritative per-class counts were found. One 2025 paper's table, apparently built on a sampled subset, lists only 31 SQLi, 30 BrowserHijacking, 28 CommandInjection and 22 Backdoor_Malware samples (search summary). — [Cybersecurity (Springer) 2025 table](https://cybersecurity.springeropen.com/articles/10.1186/s42400-025-00364-7/tables/2)

**AIT Log Data Sets (Austrian Institute of Technology)**
- **AIT-LDS v1.0** (Zenodo, 2020):
  - Size and scope: one 3.3 GB zip covering four testbeds and six days of simulated users. Stack: Apache2, PHP7, Horde 5.2.22 webmail, OkayCMS 2.3.4, Exim 4.89, MariaDB and Suricata.
  - Attack 1: nmap → nikto → smtp-user-enum → hydra brute force → webshell upload via Horde (CVE-2019-9858) → Exim privilege escalation (CVE-2019-10149).
  - Attack 2: webshell injection through a malicious cookie (CVE-2019-16885).
  - Labels: "two labels for each log line", one time-based and one similarity-based. The authors warn this "does not guarantee correct labeling for all lines and that no manual corrections were conducted".
  - License: CC BY-NC-SA 4.0.

  — [Zenodo 3723083](https://zenodo.org/records/3723083)
- **AIT-LDS v2.0** (Zenodo, 2022):
  - Size and scope: 130.6 GB across eight testbed zips (fox 15.8 GB … wilson 26.5 GB). Logs include "Apache access and error logs", and the record lists "network traffic packet captures".
  - Web attack steps: scans (nmap, WPScan, dirb) and a "Webshell upload (CVE-2020-24186)".
  - Labels: a separate `labels` directory with line-based JSON referencing line numbers. Unlabeled lines count as normal.
  - License: CC BY-NC-SA 4.0.

  — [Zenodo 5789064](https://zenodo.org/records/5789064)
- CSET 2024 slides describe the AIT-LDSv2 labels as time-based, with known issues of "delays, false positives, and overlapping intervals" (search summary). — [Landauer CSET 2024 slides](https://cset24.isi.edu/slides/cset2024-slides-landauer.pdf)

**Biblio-US17 (University of Seville / Granada) — real production web server**
- Record counts:
  - RAW: 47,402,907 requests
  - CLEAN (normal): 42,473,128
  - ATTACK (LVL1): 327,906
  - Attacks at all levels in RAW: 348,365
  - False positives: 9,222
  - Out-of-specification: 10,352

  — [Biblio-US17 README](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- Fields: only IDENTIFIER, METHOD, URI, PROTOCOL, RESP_CODE, RESP_SIZE (no headers, no bodies). Labels come from Snort, Nemesida and ModSecurity (PL1, PL2) plus manual review (ManualTP, Phase2TP). It ships time-independent and time-dependent 60/30/10 partitions via `partitions.sh`. License: CC BY-NC for research. Collected over about 6.5 months in 2017 from the Seville university library server. — [Biblio-US17 README](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- Hosted on idUS (handle 11441/148254) as restricted access, requested via a form (search summary). Peer-reviewed description: "Building a large, realistic and labeled HTTP URI dataset for anomaly-based intrusion detection systems: Biblio-US17", *Cybersecurity* 2025, DOI 10.1186/s42400-024-00336-3. — [idUS handle](https://idus.us.es/handle/11441/148254); [Springer article](https://cybersecurity.springeropen.com/articles/10.1186/s42400-024-00336-3)

**Other access-log sources (benign or unlabeled)**
- A search surfaced Zenodo records for a Charles University SIS access log dataset (2018, ~3.0 GB archive), the 1998 World Cup website access logs, and a web-robot detection dataset from a Greek library search engine. I did not open these records, so which URL holds which dataset is unverified. — [Zenodo 3241445](https://zenodo.org/record/3241445); [Zenodo 5145855](https://zenodo.org/records/5145855)

### Inferences
- **CIC-IDS2017 is the best-documented PCAP source but yields few attack requests.** Engelen et al. found BF and XSS "largely executed through a select few flows … containing many … attempts" (HTTP keep-alive), so the number of HTTP *requests* will exceed the 151/27/12 cleaned flow counts by an unknown factor. Brute-force requests probably number in the hundreds to low thousands, and SQLi requests probably in the tens. The real numbers must be measured by parsing `Thursday-WorkingHours.pcap` (7.8 GB). Attacks are also generated by one tool configuration against one app, so diversity is very low.
- **CSE-CIC-IDS2018 offers about twice the attack time (two days) with the same DVWA/Selenium setup.** It likely adds requests but not diversity. It is still useful as a cross-dataset test: train on 2017, test on 2018, or the reverse.
- **Benign HTTP in these captures is a source-leakage risk.** In CIC-IDS2017/2018 most benign web traffic goes to many external sites, much of it over HTTPS (not verified). Attacks all target one internal server (192.168.10.50 / 172.31.69.28). A request-level model could learn "Host = victim / path starts with DVWA prefix → attack". Benign samples should be drawn from requests to the same victim server, or Host/path-prefix features controlled for.
- **UNSW-NB15 is a weak fit.** It has plenty of HTTP in 100 GB of PCAP, but its attacks are IXIA-generated exploit/fuzz traffic that is not specific to web applications. Separating HTTP-carrying ground-truth events from the rest needs per-event matching, and the yield of SQLi/XSS-like requests is unknown.
- **Payload-Byte / nids-datasets give per-packet byte vectors (1500 bytes), not reassembled HTTP requests.** They help with label alignment, but the extractor would still need TCP/HTTP reassembly.
- **WEB-IDS23 can be dropped for this project.** It has no HTTP content and no PCAPs in the public release.
- **For an access-log-only model (URI features), Biblio-US17 is the strongest real-world option.** It cannot feed body/header features, so the project's extractor would have to treat missing fields as empty. That creates a feature-distribution mismatch with CSIC 2010.
- **AIT-LDS Apache access logs give realistic benign traffic.** Attacks are only a few hundred to a few thousand lines per testbed (scanner noise from nikto/WPScan/dirb plus a few exploit requests). Access logs carry no POST bodies.

### Gaps
- Exact number of HTTP requests (not flows) in the CIC-IDS2017 and CSE-CIC-IDS2018 web-attack windows. No source was found, so it must be measured locally.
- Whether DVWA was the CIC-IDS2017 victim app. The UNB page does not say so, and the original paper (Sharafaldin et al., ICISSP 2018) was not fetched.
- Size of the CSE-CIC-IDS2018 S3 bucket and per-day PCAP sizes. Not stated on the page, and the bucket was not listed.
- Whether CIC-IDS2017 PCAPs are still downloadable as of Oct 2026. The download server returned a form with "Server error".
- CIC-IoT2023 web-attack sample counts and PCAP sizes. The target app and whether the HTTP is plaintext were not determined.
- UNSW-NB15_GT.csv column names, attacker/victim IP ranges, and how much of "Exploits"/"Fuzzers" is HTTP. Not found in sources.
- Per-host Apache attack line counts in AIT-LDS v1.0/v2.0, and whether the v2.0 zips actually contain PCAPs. Not stated on Zenodo.
- Not researched or verified: CICAPT-IIoT; LITNET-2020 (believed NetFlow-only); NASA/ClarkNet logs (believed benign-only, no labels); SecRepo logs; the Kaggle/Harvard Dataverse "web server access logs" (zanbil.ir), for which no source was found; decrypted-HTTPS capture datasets.

## Q2. How to assign per-request labels reliably, and known labeling errors in these datasets

### Takeaway
The official CIC labels are flow labels derived only from IP addresses plus a documented time window. Engelen et al. showed those windows are imprecise and that most web-attack flows carry no attack payload. Per-request labels should therefore combine three things: (1) attacker→victim IP/port, (2) a tuned time window, and (3) content verification of each request (payload/regex/WAF match, or manual review). Requests in the window that carry no attack content go into an "attempted/context" bucket rather than being labeled attacks.

### Cited Findings
- **CIC-IDS2017 official labeling.** Flows are labeled "based on the time stamp, source, and destination IPs, source and destination ports, protocols and attack". — [UNB CIC-IDS2017 page](https://www.unb.ca/cic/datasets/ids-2017.html)
- **CSE-CIC-IDS2018 official labeling.** Labels use the schedule plus IPs/ports/protocol "to label the data per flow". — [UNB CSE-CIC-IDS2018 page](https://www.unb.ca/cic/datasets/ids-2018.html)
- **Time windows are imprecise.** "We found that the time frames reported on the dataset information page are not precise, therefore we had to tune them to reproduce the labelling." — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Labels ignore content.** The labeling "relies solely on a flow's source and destination IP and a specific data collection window, and thus labels a traffic flow between an attacker and a victim as malicious simply on the grounds of being collected at a certain moment in time". — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Most web-attack flows carry no attack data.** "Web Attack - Brute Force and Web Attack - XSS largely consist of flows that have no data transfer in the forward direction, which means that the attacker never actually executes an attack within those flows." — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **"Attempted" labels.** Engelen et al. introduced "'X - Attempted'" labels for attack-tool connections without forward payload. In their benchmark all "Attempted" flows were assigned to BENIGN. Overall "more than 20 percent of original traffic traces are reconstructed or relabelled". — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **TCP appendices.** CICFlowMeter's premature end-of-flow on the first FIN created "TCP appendices", which make up "25.9 percent of the entire dataset" and inherit the original flow's label. — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Where the corrected data lives.** The corrected CICIDS2017 data and code are referenced at downloads.distrinet-research.be/WTMC2021. The domain could not be fetched here. — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Liu, Engelen, Lynar, Essam & Joosen (CNS 2022).** They report previously undocumented errors "in attack orchestration, feature generation, documentation, and labeling" in both CIC-IDS-2017 and CSE-CIC-IDS-2018. They released a "fully-recreated dataset, with labeling logic that has been reverse-engineered, corrected, and made publicly available for the first time" (search summary). — [CPS-VO record](https://archive.cps-vo.org/node/97449)
- **Lanvin et al. (2022).** They describe "packet misorder, packet duplication and attack that were performed but not correctly labelled" in CICIDS2017, and incorrectly labeled port-scan attacks (search summary; the HAL full text was blocked). — [HAL hal-03775466](https://hal.archives-ouvertes.fr/hal-03775466)
- **WEB-IDS23 labels.** Each sample is "labeled based on the logs generated by the traffic generator". This is ground truth by construction, but at flow level only. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)
- **AIT-LDS v1.0 labels.** These are automatic (time-based plus similarity-based), with "no manual corrections". — [Zenodo 3723083](https://zenodo.org/records/3723083)
- **AIT-LDS v2.0 labels.** These reference attack events by line number. The CSET 2024 slides note "delays, false positives, and overlapping intervals" (search summary). — [Zenodo 5789064](https://zenodo.org/records/5789064); [CSET 2024 slides](https://cset24.isi.edu/slides/cset2024-slides-landauer.pdf)
- **Biblio-US17 labels.** These combine four signature detectors (Snort, Nemesida, ModSecurity PL1/PL2) with manual true-positive review, and flag FP and OOS separately. — [Biblio-US17 README](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- **Payload-Byte labeling.** Packets are labeled by matching them to CIC/UNSW flow labels on src/dst IP, ports, start/end time, protocol and TTL. This means packet labels inherit any flow-label errors. — [Zenodo 7258579](https://zenodo.org/records/7258579)

### Inferences
- **Recommended per-request labeling recipe for CIC-IDS2017 Thursday:**
  1. Keep requests whose server is 192.168.10.50:80 and whose client is the attacker's NATed address. Per the NAT path this is 172.16.0.1 inside the LAN capture; on which side of the NAT the pcap was captured is not verified.
  2. Keep only requests inside the tuned windows (Engelen's corrected windows, if obtainable from DistriNet).
  3. Mark a request "attack" only if its URI/body contains the brute-force login parameters, an XSS payload or an SQLi payload. Check this with regex and/or an OWASP CRS/ModSecurity replay, then spot-check manually.
  4. Treat other requests from the attacker in the window (static assets fetched by Selenium, page loads) as "attack-context". Either drop them or label them benign, and document the choice.
- **Brute-force requests are the hardest to label.** A wrong-password login POST looks like a benign login. For a "normal vs. anomalous request content" model, labeling them "attack" teaches the model a rate/sequence concept it cannot see in a single request. Consider excluding brute force or keeping it as a separate class.
- **Label request-by-request, not flow-by-flow.** Because flows contain many requests, flow labels propagated to every request of a keep-alive connection will mislabel benign-looking requests mixed into attack sessions.
- **Ask DistriNet for the CSE-CIC-IDS2018 relabeling logic.** For CSE-CIC-IDS2018 the same recipe applies (attacker 18.218.115.60 → victim 172.31.69.28/18.218.83.150). The Liu et al. 2022 relabeling logic should be obtained, if possible, before trusting the window boundaries.

### Gaps
- Engelen's corrected time windows, and whether any per-request (not per-flow) ground truth exists for CIC web attacks. DistriNet pages were blocked here.
- The specific web-attack errors in CSE-CIC-IDS2018 reported by Liu et al. 2022. The full text was not accessible.
- Time zones of the CIC schedules (local Atlantic time vs. pcap epoch/UTC). This is commonly reported as a pitfall but no source was found here, so it must be checked empirically by locating the first attack request in the PCAP.
- Whether CIC-IDS2017 pcaps were captured before or after the firewall NAT (that is, whether the attacker appears as 205.174.165.73 or 172.16.0.1). Not confirmed.

## Q3. Tools and workflow to extract HTTP requests from PCAP

### Takeaway
Use tshark with TCP reassembly enabled (out-of-order reassembly turned on explicitly) to emit one row per HTTP request with method, URI, headers and body. Alternatively, use Zeek for http.log metadata plus a package to capture POST bodies, because stock http.log stores only body lengths. Python libraries (dpkt/scapy) need hand-written TCP reassembly. pyshark is a wrapper around tshark.

### Cited Findings
- **Zeek http.log has no body content.** Its columns are: ts, uid, id.orig_h/p, id.resp_h/p, trans_depth, method, host, uri, referrer, version, user_agent, origin, request_body_len, response_body_len, status_code, status_msg, info_code, info_msg, tags, username, password, proxied, orig_fuids, orig_filenames, orig_mime_types, resp_fuids, resp_filenames, resp_mime_types. Only the body *length* is logged. — [Zeek docs via Context7 (TLS decryption http.log example)](https://docs.zeek.org/en/current/frameworks/tls-decryption.html)
- **Bodies can still be matched or scripted.** Zeek can match request bodies in signatures (`http-request-body /<regex>/`), and per-request scripting is possible via the `http_request` event. — [Zeek signatures docs](https://docs.zeek.org/en/current/frameworks/signatures.html); [Zeek quickstart](https://docs.zeek.org/en/current/_sources/quickstart.rst.txt)
- **POST bodies need a package.** Corelight's `log-add-http-post-bodies` package adds a `post_body` field (configurable length from the start of the POST body), installed via `zkg install corelight/log-add-http-post-bodies`. The core HTTP::Info record has `request_body_len` but no body field. — [Zeek package page](https://packages.zeek.org/packages/view/2171ba8d-d070-11ee-8674-0a598146b5c6); [Zeek http main.zeek docs](https://docs.zeek.org/en/v8.2.1/_sources/scripts/base/protocols/http/main.zeek.rst.txt)
- **Custom body scripts are costly.** Writing your own body capture needs reassembly from `http_entity_*` events, and `http_entity_data` "is a pretty expensive event" (Zeek community forum). — [Zeek community: HTTP POST data](https://community.zeek.org/t/http-post-data/2256); [Zeek community: response body](https://community.zeek.org/t/zeek-6-1-1-http-response-body/7280)
- **tshark field extraction.** `tshark -T fields -e <field> …` prints chosen fields, tab-separated by default. `-E` controls format. A field prefixed with `@` prints as hex bytes. — [tshark man page via Context7](https://www.wireshark.org/docs/man-pages/tshark.html)
- **Wireshark TCP reassembly.** "Allow subdissector to reassemble TCP streams" is enabled by default and lets Wireshark "reconstruct a full HTTP message". "Reassemble out-of-order segments" is "currently disabled by default". If a capture starts mid-connection or segments are lost or out of order, "HTTP messages could be shown as 'Continuation'". Reassembled HTTP bodies appear as an "Uncompressed entity body" data source. — [Wireshark User's Guide §7.8 via Context7](https://www.wireshark.org/docs/wsug_html)
- **pyshark** is "a Python wrapper for tshark that enables packet parsing from capture files … using Wireshark dissectors". — [Context7 library listing: /kiminewt/pyshark](https://github.com/KimiNewt/pyshark)
- **The Payload-Byte tool** extracts and labels packets from NIDS datasets and converts them to byte-wise feature vectors (search summary; the GitHub page timed out). — [Payload-Byte paper record](https://athena.westpoint.edu/items/48c75309-6908-42ec-b9e4-ef246e02f3ab); [Zenodo 7258579](https://zenodo.org/records/7258579)
- **No dedicated repo found.** No public GitHub repo was found that specifically extracts labeled HTTP requests from CIC-IDS2017/2018 PCAPs; a general search returned only generic tshark recipes. — [search results, e.g., tshark skill page](https://smithery.ai/skills/AgentSecOps/analysis-tshark)

### Inferences
- Example tshark extraction (constructed, untested). Field names `http.request.method`, `http.request.uri`, `http.host`, `http.user_agent`, `http.cookie`, `http.content_type`, `http.file_data` and `tcp.stream` are standard Wireshark HTTP/TCP fields, but they were not checked locally because tshark is not installed:
  ```bash
  tshark -r Thursday-WorkingHours.pcap \
    -o tcp.desegment_tcp_streams:TRUE -o tcp.reassemble_out_of_order:TRUE \
    -Y 'http.request && ip.dst==192.168.10.50 && tcp.dstport==80' \
    -T fields -E header=y -E separator=/t -E quote=d -E occurrence=a \
    -e frame.time_epoch -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.stream \
    -e http.request.method -e http.request.uri -e http.request.version \
    -e http.host -e http.user_agent -e http.cookie -e http.referer \
    -e http.content_type -e http.content_length_header -e http.file_data \
    > thursday_http_requests.tsv
  ```
  - `-T json` or `-T ek`, or `-e @http.file_data` for hex, is safer when bodies contain tabs or newlines or non-UTF-8 bytes.
  - HTTP-dissector preferences for body reassembly, de-chunking and decompression (believed to be `http.desegment_headers`, `http.desegment_body`, `http.dechunk_body`, `http.decompress_body`) should be confirmed with `tshark -G defaultprefs | grep '^#*http\.'`.
  - If DVWA runs on a non-standard port, add it with `-d tcp.port==<p>,http`.
- Pre-split the 7.8 GB pcap by time and IP with `editcap -A/-B` and a `tcpdump 'host 192.168.10.50'` filter, so tshark's reassembly memory stays bounded.
- Example Zeek workflow (constructed, untested): `zkg install corelight/log-add-http-post-bodies`, then `zeek -C -r file.pcap local`. Join http.log on `uid` + `trans_depth`. `-C` ignores bad checksums, which is common in offloaded captures. Request headers beyond the default fields need a custom script, for example one hooking `http_header`.
- dpkt/scapy can parse HTTP from a single packet, but requests spanning segments (POST bodies, long cookies) need custom stream reassembly. tshark/pyshark or Zeek are the lower-risk choices.
- **Output format.** Produce one JSONL record per request (method, path, query, headers dict, body bytes as base64/latin-1, ts, src/dst, stream id). That format can be converted directly to the project's `requests.jsonl` input.

### Gaps
- tshark HTTP preference names and current defaults were not verified (no local install, and the Context7 snippets did not list them).
- Maximum `post_body` length and Zeek 8.x compatibility of the Corelight package were not checked.
- No existing open-source "CIC PCAP → labeled HTTP requests" converter was found to reuse or compare counts against.

## Q4. Honeypot HTTP datasets as a source of real-world attack requests (and their bias)

### Takeaway
Real-world web-honeypot request data exists, from DShield/ISC web honeypots, research papers with 0.75M–1.24M requests, and informal GitHub dumps. However, none was confirmed to be a clean, openly downloadable, labeled HTTP request dataset. Honeypots see almost only scanners, bots and exploit attempts, so they supply attack variety but not benign traffic. Mixing them with benign traffic from another source creates the source-leakage problem already noted in the project docs.

### Cited Findings
- **SANS DShield web honeypot project.** Volunteers run web honeypots and full request details are archived (OWASP 2009 project page). — [OWASP wiki](https://wiki.owasp.org/index.php/SANS_Dshield_Webhoneypot_Project)
- **Submitting logs to DShield** requires registration; anonymous logs are not accepted. — [DShield weblogs](https://www.dshield.org/weblogs)
- **ISC Web Server Log Project.** It groups top attacks with regexes and notes some hits are benign. — [ISC diary 14710](https://isc.sans.edu/diary/14710)
- **SNARE/Tanner** are web honeypot software (Tanner evaluates HTTP requests and builds the responses SNARE serves). No published request logs were found. — [ecosyste.ms Tanner](https://awesome.ecosyste.ms/projects/github.com%2Fmushorg%2Ftanner)
- **CIC Honeynet report.** Lists Glastopf in the CIC honeynet setup; it is a design document, not a dataset. — [CIC honeynet PDF](https://www.unb.ca/cic/_assets/documents/cic_honeynet_08-16_02_2018.pdf)
- **"Beyond the Leak" (2025).** Analyzes 754,281 HTTP requests from 34 HTTP honeypot sensors over 363 days. Public release of the raw requests was not confirmed (search summary; PMC was blocked). — [PMC12197152](https://pmc.ncbi.nlm.nih.gov/articles/PMC12197152/)
- **"Intercepting and Monitoring Potentially Malicious Payloads with Web Honeypots".** About 1.24M requests over 6–7 months. No public release was mentioned (search summary). — [ResearchGate](https://www.researchgate.net/publication/395574853_Intercepting_and_Monitoring_Potentially_Malicious_Payloads_with_Web_Honeypots)
- **Foospidy (2018).** Published unique POST payloads collected from honeypots on GitHub (search summary; Medium was blocked). — [Medium post](https://medium.com/@foospidy/honeypot-data-post-request-payloads-de132a225618)
- **Merit Network "Honeypot Cyber Intrusion Dataset" (IEEE DataPort).** Contains events with a payload field from distributed sensors. It is not HTTP-specific and access terms were not checked (search summary). — [IEEE DataPort](https://ieee-dataport.org/documents/honeypot-cyber-intrusion-dataset-cybersecurity-research)
- **CyberLab honeynet (Zenodo).** This is Cowrie SSH/Telnet, not HTTP. — [Zenodo 3687527](https://zenodo.org/records/3687527)
- **Kaggle/GitHub "Web Application Payloads".** These are curated, synthetic payload strings, not captured traffic. — [Kaggle](https://www.kaggle.com/datasets/cyberprince/web-application-payloads-dataset); [GitHub](https://github.com/SunnyThakur25/Web-Application-Payloads-Dataset)

### Inferences
- **Honeypot data fits a supplementary role.** Honeypot requests are best used as an extra attack-only test set, to check whether a CSIC-trained model generalizes to real exploit traffic (Log4Shell, path traversal, webshell probes). They should not be a training source mixed with benign traffic from elsewhere.
- **Labeling honeypot traffic "all attack" is wrong.** Search-engine crawlers and benign scanners also hit honeypots (ISC notes some hits are benign). A WAF/CRS pass plus a manual review is needed.
- **Running our own honeypot is an option.** A T-Pot/SNARE deployment would give full raw requests including headers and bodies. It falls under the KVKK/privacy rules already listed in `docs/aday-veri-setleri.md` (IP addresses are personal data).

### Gaps
- No openly downloadable, labeled HTTP-honeypot request dataset with headers and bodies was confirmed. The data-availability statements of the two papers could not be read.
- Access terms and HTTP coverage of the Merit IEEE DataPort dataset, and whether DShield web logs can be bulk-downloaded today, were not verified.
- T-Pot community data sharing (Sicherheitstacho), Glastopf datasets and HTTP-honeypot Kaggle dumps were not researched.

## Q5. Pitfalls: TCP reassembly, chunked/compressed bodies, label leakage via IP/timestamp, class imbalance

### Takeaway
The main risks:
- Mis-reassembled or duplicated requests: CICIDS2017 has documented packet duplication and misordering, and Wireshark does not reassemble out-of-order segments by default.
- Labels that follow IP and time rather than content.
- Shortcut learning on host, IP and time artefacts.
- Extreme imbalance with very few distinct attack payloads.

### Cited Findings
- **Wireshark reassembly failures.** Without reassembly, or when segments are lost or out of order, HTTP messages show up as "Continuation". Out-of-order reassembly is off by default. Lost packets in the capture make full stream reconstruction impossible. — [Wireshark User's Guide §7.8.3](https://www.wireshark.org/docs/wsug_html)
- **Duplication and misordering in CICIDS2017.** Lanvin et al. report packet misorder and packet duplication in the CICIDS2017 capture (search summary). This would yield duplicate HTTP requests. — [HAL hal-03775466](https://hal.archives-ouvertes.fr/hal-03775466)
- **Shortcut learning.** Engelen et al.: Flow ID, Source IP, Destination IP and Timestamp "should be excluded from the feature representation during training" to avoid a NIDS "associating a certain timestamp or some host-specific information with a certain class". They found the RF overfit through shortcut learning on TCP appendices. — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Tiny attack classes give unstable results.** After cleaning, Web Attack SQL had 12 traces and "all 3 test traces are mispredicted as Benign", F1 0.00. Web XSS F1 was 0.79 and Web Brute Force F1 0.95 (RF, 75/25 split). Engelen et al. also note diversity concerns: attacks generated "using one configuration of the attack tool may not generalize to other configurations". — [Engelen et al. 2021](https://lirias.kuleuven.be/retrieve/713070)
- **Imbalance in real-server logs.** Biblio-US17 has 327,906 LVL1 attacks against 42,473,128 clean requests, about 0.77% attacks. — [Biblio-US17 README](https://dtstc.ugr.es/neus-cslab/wp-content/uploads/2023/08/README.txt)
- **WEB-IDS23 imbalance.** The web classes are dominated by brute force (912,503 HTTP flows) versus 4,558 XSS HTTP flows. — [arXiv 2502.03909](https://arxiv.org/html/2502.03909v1)
- **Automatic log labels carry errors.** AIT v1 labels are automatic with no manual correction. AIT v2 time-based labels have delays, false positives and overlapping intervals (search summary). — [Zenodo 3723083](https://zenodo.org/records/3723083); [CSET 2024 slides](https://cset24.isi.edu/slides/cset2024-slides-landauer.pdf)
- **Zeek body capture limits.** Zeek logs only `request_body_len`; capturing bodies needs extra scripts or packages, which have performance costs. — [Zeek package page](https://packages.zeek.org/packages/view/2171ba8d-d070-11ee-8674-0a598146b5c6); [Zeek community](https://community.zeek.org/t/http-post-data/2256)

### Inferences
- **Deduplicate before splitting.** Hash (method, URI, body), or keep tcp.stream + seq, before the train/test split. Duplicated packets, retransmissions and brute-force loops create many near-identical attack requests, and the project's existing content-grouping split (`docs/http-veri-ayrimi.md`) should be applied to them.
- **Chunked and compressed bodies.** Request bodies in DVWA attacks are normally small url-encoded forms, so chunked or gzip *request* bodies should be rare. Decoding settings matter mostly for responses, which this project does not need. The extractor should still record Transfer-Encoding/Content-Encoding and either decode or flag such requests.
- **Leakage via IP, time and Host.** Never feed src/dst IP, timestamps, the Host header or session cookies as features. Check that an attack-vs-benign split does not reduce to "requests to the victim server during the attack window". Ideally draw benign requests to the same DVWA host from outside the attack windows. If too few exist, document that the PCAP datasets serve only as attack-side test data.
- **Imbalance and low diversity.** The few distinct SQLi/XSS payloads in CIC data mean metrics on them will be high-variance. Report per-class counts and consider using CIC/AIT/honeypot data only for cross-dataset evaluation of a model trained on CSIC 2010 or other request-level datasets.
- **Encryption.** WEB-IDS23 splits classes into HTTP and HTTPS variants. In general only plaintext HTTP yields request content, and HTTPS portions of any capture are unusable without session keys.

### Gaps
- No quantitative study was found on how many HTTP requests are lost or duplicated when reassembling CIC-IDS2017/2018 PCAPs with tshark or Zeek.
- No source was found on how much benign plaintext HTTP to the CIC victim web servers exists in the captures, which is key to judging whether benign and attack requests can come from the same target.
