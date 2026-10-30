#!/usr/bin/env bash
# Downloads the datasets for the per-value HTTP model into data/raw/.
# Safe to re-run: finished downloads are skipped, interrupted ones continue.
# Git repositories are cut down to their data files. DATASETS.md next to this
# file lists each dataset, its role and what is kept.
set -u
cd "$(dirname "$0")"

failed=()

# fetch <dir> <file> <url> <md5>
# The md5 is required: Fedora's wget (Wget2) can exit 0 on a cut-off download.
fetch() {
    local dir=$1 file=$2 url=$3 md5=$4
    mkdir -p "$dir"
    echo "== $dir/$file"
    if echo "$md5  $dir/$file" | md5sum -c --status 2>/dev/null; then
        echo "already complete"
        return 0
    fi
    if wget -c -nv -O "$dir/$file" "$url" &&
       echo "$md5  $dir/$file" | md5sum -c --status; then
        echo "md5 OK"
        return 0
    fi
    failed+=("$dir/$file (run again to continue; delete the file if it keeps failing)")
    return 1
}

# clone <dir> <repo-url> <prefix> <pattern>...
# Checks out only the files matching the git patterns (written from the repo
# root), then moves what is under <prefix> into <dir>. A root LICENSE matched by
# the patterns is moved too. Code, images and git history are not kept.
clone() {
    local dir=$1 url=$2 prefix=$3
    shift 3
    echo "== $dir"
    if [ -e "$dir" ]; then
        echo "already exists, skipping (delete the folder to download again)"
        return
    fi
    local tmp=$dir.part
    rm -rf "$tmp"
    if git clone -q --depth 1 --filter=blob:none --no-checkout "$url" "$tmp" &&
       git -C "$tmp" sparse-checkout set --no-cone "$@" &&
       git -C "$tmp" checkout -q &&
       mkdir "$dir" &&
       mv "$tmp/$prefix"/* "$dir"/; then
        [ -f "$tmp/LICENSE" ] && mv "$tmp/LICENSE" "$dir"/
        rm -rf "$tmp"
        return
    fi
    rm -rf "$tmp" "$dir"
    failed+=("$dir")
}

echo "Started: $(date)"

# Attack strings
fetch open-appsec malicious.zip https://downloads.openappsec.io/waf-comparison-project/malicious.zip 9fa7acec948a2b5c9f728d6fa06f8cad
clone httpparams https://github.com/Morzeux/HttpParamsDataset.git "" \
    /payload_full.csv /LICENSE
clone gotestwaf https://github.com/wallarm/gotestwaf.git testcases \
    /testcases/ /LICENSE
patt=()
for d in "Client Side Path Traversal" "Command Injection" "CRLF Injection" "CSS Injection" \
         "CSV Injection" "CVE Exploits" "Directory Traversal" "DOM Clobbering" \
         "Encoding Transformations" "File Inclusion" "GraphQL Injection" \
         "HTTP Parameter Pollution" "Insecure Deserialization" "LaTeX Injection" \
         "LDAP Injection" "NoSQL Injection" "Open Redirect" "ORM Leak" "Prototype Pollution" \
         "SAML Injection" "Server Side Include Injection" "Server Side Request Forgery" \
         "Server Side Template Injection" "SQL Injection" "XPATH Injection" "XSLT Injection" \
         "XSS Injection" "XXE Injection"; do
    patt+=("/$d/*.md" "/$d/Intruder*/")
done
clone payloadsallthethings https://github.com/swisskyrepo/PayloadsAllTheThings.git "" \
    "${patt[@]}" /LICENSE
clone seclists https://github.com/danielmiessler/SecLists.git Fuzzing \
    /Fuzzing/Databases/ '!/Fuzzing/Databases/OracleDB-SID.txt' /Fuzzing/LFI/ \
    /Fuzzing/XSS/Polyglots/ /Fuzzing/XSS/robot-friendly/ \
    /Fuzzing/big-list-of-naughty-strings.txt /Fuzzing/command-injection-commix.txt \
    /Fuzzing/FormatString-Jhaddix.txt /Fuzzing/fuzz-Bo0oM.txt \
    /Fuzzing/HTML5sec-Injections-Jhaddix.txt /Fuzzing/JSON.Fuzzing.txt \
    /Fuzzing/LDAP.Fuzzing.txt /Fuzzing/login_bypass.txt /Fuzzing/Metacharacters.fuzzdb.txt \
    /Fuzzing/SSI-Injection-Jhaddix.txt /Fuzzing/template-engines-expression.txt \
    /Fuzzing/template-engines-identification.txt /Fuzzing/UnixAttacks.fuzzdb.txt \
    /Fuzzing/URI-XSS.fuzzdb.txt /Fuzzing/Windows-Attacks.fuzzdb.txt /Fuzzing/XML-FUZZ.txt \
    /Fuzzing/XXE-Fuzzing.txt '!README.md' /LICENSE
clone fwaf https://github.com/faizann24/Fwaf-Machine-Learning-driven-Web-Application-Firewall.git "" \
    /goodqueries.txt /badqueries.txt
clone modsec-learn-dataset https://github.com/pralab/modsec-learn-dataset.git malicious \
    /malicious/sqli_kaggle/sqli_parsed.json /malicious/sqlmap/sqli_parsed.json

# Test sets
echo "== owasp"
if [ -e owasp ]; then
    echo "already exists, skipping (delete the folder to download again)"
else
    fetch . owasp.zip https://zenodo.org/api/records/17178461/files/owasp.zip/content 95b7a8237abc163d8ca31e49f7318efd &&
        { unzip -q owasp.zip -d owasp && rm owasp.zip || failed+=(owasp); }
fi
fetch sr-bh-2020 data_capec_multilabel.csv https://dataverse.harvard.edu/api/access/datafile/6319496 173ec515308bdce5aec19cfd5b792596
fetch sr-bh-2020 mislabeled_indexes.csv https://raw.githubusercontent.com/mattebit/x-wad/main/experiments/srbh2020/mislabeled_indexes.csv 974262238819ac6e4764cc7491319325
clone csic-2010 https://github.com/msudol/Web-Application-Attack-Datasets.git OriginalDataSets/csic_2010 \
    '/OriginalDataSets/csic_2010/*.txt'
clone ecml-pkdd-2007 https://github.com/msudol/Web-Application-Attack-Datasets.git OriginalDataSets/ecml_pkdd \
    /OriginalDataSets/ecml_pkdd/learning_dataset_xml.zip
fetch modsec-wp combined_final_dataset_augmented.xlsx https://zenodo.org/api/records/21872151/files/combined_final_dataset_augmented.xlsx/content 6d02547829e0b460ef6473d5603a84db
clone atrdf https://github.com/ArielCyber/Cisco_Ariel_Uni_API_security_challenge.git Datasets \
    '/Datasets/*.7z'

# Normal examples for training (largest file, last)
fetch open-appsec legitimate.zip https://downloads.openappsec.io/waf-comparison-project/legitimate.zip 2997f8697bdeec5cc9cb6064023b17d7

echo
echo "Finished: $(date)"
du -sh -- */ 2>/dev/null
if [ ${#failed[@]} -eq 0 ]; then
    echo "All downloads OK."
else
    echo "FAILED (run the script again to retry):"
    printf '  %s\n' "${failed[@]}"
    exit 1
fi
