# Raw datasets

Datasets for the per-value HTTP model. Each value (query/body value, path, a few headers) is
scored on its own, so datasets that only hold URLs or parameter values are usable too.
Everything in this folder except this file and `download_datasets.sh` is git-ignored. `download_datasets.sh` downloads all of it (see the end).
Links, sizes and licenses were checked on 19 October 2026.

Only data files are kept. Git repositories are cut down to the files listed below: their code,
images, documentation and git history are not downloaded. Do not run any program from these
folders.

## Contents

| Folder | Dataset | Files | Role | Size | License | Source |
|---|---|---|---|---|---|---|
| `open-appsec/` | open-appsec WAF Comparison Project | `legitimate.zip`: ~1.04M normal requests from real websites, 692 JSON files (7.3 GB unpacked). `malicious.zip`: 73,924 attack requests | `legitimate`: training normal examples. `malicious`: attack strings only, never the original requests | 1.2 GB | Apache-2.0 / "mostly MIT" | https://github.com/openappsec/waf-comparison-project |
| `sr-bh-2020/` | SR-BH 2020 + X-WAD label fixes | `data_capec_multilabel.csv`: 907,814 real requests to one WordPress site. `mislabeled_indexes.csv`: 126,003 rows X-WAD marks as mislabeled | Main test set | 418 MB | CC0 / Apache-2.0 | https://doi.org/10.7910/DVN/OGOIXX, https://github.com/mattebit/x-wad |
| `csic-2010/` | CSIC 2010 | `normalTrafficTraining.txt` (36,000), `normalTrafficTest.txt` (36,000), `anomalousTrafficTest.txt` (25,065) | Test set | 54 MB | No dataset license | https://github.com/msudol/Web-Application-Attack-Datasets |
| `ecml-pkdd-2007/` | ECML/PKDD 2007 | `learning_dataset_xml.zip`: one XML file, 50,116 requests; `attackIntervall` marks where the attack is | Attack values and test set | 20 MB (107 MB unpacked) | No dataset license | same mirror |
| `modsec-wp/` | ModSec-WP, WordPress audit logs | `combined_final_dataset_augmented.xlsx` (108,823 transactions) | Test set | 27 MB | CC-BY-4.0 | https://zenodo.org/records/21872151 |
| `owasp/` | 30-day ModSecurity production logs | `DD-Mon-2025/modsec_audit.anon.log`, one per day, 27 Jul–25 Aug 2025 | Test: real-world attacks. Attacks only; labels come from CRS rules, so do not train on them. Logs name the matched part (`found within ARGS:...`) | 380 MB | CC-BY-4.0 | https://zenodo.org/records/17178461 |
| `atrdf/` | ATRDF, JSON API requests (Cisco and Ariel University) | `dataset_{1,2,3,4}_{train,val}.7z` | Test set for API attacks (needs JSON support) | 140 MB (1.1 GB unpacked) | None, local use only | https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge |
| `httpparams/` | HttpParams | `payload_full.csv`: 31,067 parameter values (the repo's train/test files are splits of it) | Attack strings, attack side only (normal side is copied from CSIC) | 2 MB | MIT | https://github.com/Morzeux/HttpParamsDataset |
| `modsec-learn-dataset/` | pralab modsec-learn, SQLi side | `sqli_kaggle/sqli_parsed.json` (11,378), `sqlmap/sqli_parsed.json` (8,245), each value written as `p=<value>` | Attack strings (SQLi) | 4 MB | None | https://github.com/pralab/modsec-learn-dataset |
| `gotestwaf/` | Wallarm GoTestWAF test cases | YAML in `community/`, `owasp/`, `owasp-api/`. `false-pos/texts.yml` is harmless text that looks like attacks | Attack strings, newer types (SSTI, SSRF, ...). `false-pos`: hard normal examples | 1 MB | MIT | https://github.com/wallarm/gotestwaf |
| `payloadsallthethings/` | PayloadsAllTheThings | 28 attack-type folders: `.md` pages (payloads inside code blocks) and `Intruder/` lists (one payload per line) | Attack strings | 4 MB | MIT | https://github.com/swisskyrepo/PayloadsAllTheThings |
| `seclists/` | SecLists `Fuzzing/`, attack lists only | `Databases/` (SQLi), `LFI/`, `XSS/` and 17 single lists | Attack strings. `big-list-of-naughty-strings.txt` is mostly odd but harmless text and `fuzz-Bo0oM.txt` is file paths scanners probe: label these two by hand | 4 MB | MIT | https://github.com/danielmiessler/SecLists |
| `fwaf/` | Fwaf (2017) | `goodqueries.txt` (1,294,531 lines), `badqueries.txt` (48,126) | Extra normal and attack values, low trust: inspect first | 27 MB | None | https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall |

Total: 2.2 GB, 300 files. Python reads the `.zip` files directly (`zipfile`); the `.7z` files need
`7z x` or the `py7zr` package.

Git sources were taken at these commits: HttpParams `926670a`, GoTestWAF `8ed7bc2`,
PayloadsAllTheThings `3ac2790`, SecLists `75064ac`, Fwaf `9c92866`, modsec-learn `8f2b27a`,
CSIC/ECML mirror `424c6e1`, ATRDF `9494785`.

## Left out of the downloaded repos

- **CSIC/ECML mirror:** CSV and Weka copies (feature tables built from the originals), the
  reformatted `.tar.gz` copies, and ECML's train/test split, which drops the attack position marks.
- **modsec-learn:** `legitimate/` (508,530 query strings taken from open-appsec, which is here in
  full), the copies of HttpParams and open-appsec SQLi, and the files `merge.py` builds.
- **HttpParams:** train, test and lexical files (subsets of `payload_full.csv`).
- **SecLists:** `User-Agents/` (363 MB), number, letter, date and amount lists, single-character and
  hex-encoding lists, name lists (file extensions, OS, locales, LDAP, Java classes, Oracle SIDs),
  and the "human-friendly" XSS copies.
- **PayloadsAllTheThings:** topics whose attacks are not values inside a request (account takeover,
  CORS, race conditions, request smuggling, prompt injection, file upload samples, ...), and every
  `Images/` and `Files/` folder (pictures, sample attack files, exploit scripts).

## Checks done on 19 October 2026

- Every fetched file matches the md5 in `download_datasets.sh`; the `.zip` and `.7z` archives pass
  their own integrity tests.
- `owasp/` is byte-for-byte the content of `owasp.zip` from Zenodo 17178461.
- CSIC request counts are 36,000 / 36,000 / 25,065. `normalTrafficTraining.txt` and
  `anomalousTrafficTest.txt` match the SHA-256 values in `data/http-mini/manifest.json`.
- The first download (night of 18 October) left `legitimate.zip` cut off at 697 of 1,204 MB but
  still reported "All downloads OK". On Fedora, `wget` is Wget2, which can exit without an error on a
  broken download. The file was completed, and the script now checks the md5 of every file.

## Not downloaded

- **Biblio-US17** (47M real requests, URLs only): the file needs permission (HTTP 401). Access must be
  requested from the University of Seville. Non-commercial license.
- Left out on purpose: `puyang2025/waf_data_v2` (wrong labels), the 199,793-request Kaggle set
  (path gives the label away), SecureAI-SE (built from CSIC), "CSIC 2010 v2" (undocumented),
  FADE (paywall), network-level datasets (CIC-IDS, UNSW-NB15, WEB-IDS23: no HTTP requests).

## How to download

From this folder:

```bash
cd ~/Documents/ids-model/data/raw
nohup systemd-inhibit --what=sleep:idle --why="dataset download" bash download_datasets.sh > download.log 2>&1 &
```

This keeps running after the terminal is closed and stops the computer from sleeping. If GNOME
still suspends, turn off automatic suspend in Settings → Power for the night. In the morning:

```bash
tail -n 30 ~/Documents/ids-model/data/raw/download.log
```

The last lines say "All downloads OK." or list what failed. Running the script again checks the
finished files and retries only what is missing or broken. To download a cloned dataset again,
delete its folder first. About 2 GB is downloaded in total.
