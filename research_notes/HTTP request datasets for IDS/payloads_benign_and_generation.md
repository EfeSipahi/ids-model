# Payload corpora, benign HTTP traffic sources, and self-generated labeled HTTP datasets (status: 17 Oct 2026)

Scope: sources that complement full-request labeled datasets (CSIC, ECML/PKDD, SR-BH, modsec-learn are covered elsewhere). Project context: supervised binary normal/anomalous classifier on single raw HTTP requests (method, path, query, form body, headers); current data = 1,000 CSIC 2010 requests (`data/http-mini/requests.jsonl`).

Method notes: repo metadata (license SPDX id, stars, last push) was pulled from the GitHub REST API on 2026-10-17. CRS test counts come from a sparse clone of `coreruleset/coreruleset` at commit `6ee9891` (2026-10-15). Kaggle metadata comes from the public Kaggle API. Row counts marked "verified" were computed locally on small (<3 MB) files. Overlap checks against the user's CSIC subset were run on `data/http-mini/requests.jsonl`, which was only read, not modified. Anything not checked this way is marked **unverified**.

## Q1. Which payload corpora are largest, best-labeled, and permissively licensed, and how can they be turned into labeled full requests?

### Takeaway
SecLists (MIT) and PayloadsAllTheThings (MIT) are the largest permissively licensed and actively maintained payload sources. HttpParamsDataset (MIT, 31,067 labeled parameter values) and mgm WAF-Payload-Collection (about 31k true-positive lines plus a small hand-made false-positive list) are the best labeled. Most Kaggle SQLi/XSS sets have "Unknown" licenses. Their benign side is largely CSIC 2010-derived, which creates a direct contamination risk for this project. Putting payloads into benign templates works, but it produces source and format shortcuts unless both classes share the same templates, encoding, and hard negatives.

### Cited Findings
**Large general