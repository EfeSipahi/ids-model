"""HTTP isteklerini hedef yol şablonuna göre gruplar. Eğitim veya split yapmaz."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

VERSION = 'endpoint-template-v1'
BAD_PERCENT = re.compile(r'%(?![0-9a-fA-F]{2})')


def endpoint_template(record, encoding='utf-8'):
    target = record.get('request_target')
    if not isinstance(target, str) or not target:
        raise ValueError('request_target boş olmayan metin olmalı')
    raw_path = urlsplit(target).path or '/'
    if BAD_PERCENT.search(raw_path):
        raise ValueError('Yolda bozuk yüzde kodlaması var; elle inceleme gerekiyor')
    path = unquote(raw_path, encoding=encoding, errors='strict')
    # Gruplama sezgisidir; sunucunun gerçek yönlendirme davranışı iddiası değildir.
    path = re.sub(r';jsessionid=[^/;]*', '', path, flags=re.I)
    path = re.sub(r'\d+', '{number}', path)
    # Yol harf büyüklüğü, eğik çizgiler ve nokta segmentleri korunur.
    return path


def group_identity(record, encoding='utf-8'):
    template = endpoint_template(record, encoding)
    digest = hashlib.sha256((VERSION+'\0'+template).encode('utf-8')).hexdigest()
    return template, digest


def build_groups(input_path, output_dir, encoding='utf-8'):
    raw = Path(input_path).read_bytes()
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    ids = [r['sample_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Tekrarlanan sample_id var')
    if not rows:
        raise ValueError('Veri boş')
    groups = defaultdict(list)
    assignments = []
    for r in rows:
        template, gid = group_identity(r, encoding)
        groups[gid].append(r)
        assignments.append(dict(sample_id=r['sample_id'], group_id=gid,
                                endpoint_template=template, label=r.get('label'),
                                original_content_group=r.get('content_group')))
    summaries = []
    for gid, members in groups.items():
        summaries.append(dict(group_id=gid, endpoint_template=endpoint_template(members[0], encoding),
            count=len(members), labels=dict(Counter(str(r.get('label')) for r in members)),
            methods=dict(Counter(r.get('method') for r in members)),
            example_ids=[r['sample_id'] for r in members[:3]]))
    summaries.sort(key=lambda r: (-r['count'],r['endpoint_template']))
    counts = Counter(g['count'] for g in summaries)
    report = dict(version=VERSION, input_sha256=hashlib.sha256(raw).hexdigest(),
        encoding=encoding, records=len(rows), groups=len(groups),
        singleton_groups=counts[1], largest_group=summaries[0]['count'],
        mixed_label_groups=sum(len(g['labels'])>1 for g in summaries),
        top_five_records=sum(g['count'] for g in summaries[:5]),
        split_created=False, trained=False,
        policy='Group by once-decoded path with digit runs and jsessionid normalized. '
               'Ignore method, query, body, headers and labels. No statistical fit.',
        limitations=['This tests transfer across endpoint templates, not random requests from known endpoints.',
                     'Digit normalization can merge different pages deliberately.',
                     'Equivalent aliases and payloads reused across different paths may remain in different groups.',
                     'Similar does not mean identical; mixed labels within a group are retained.',
                     'Grouping is not proof that every near-duplicate or leakage source is eliminated.'],
        group_details=summaries)
    out=Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in ('group_assignments.jsonl','group_report.json'):
        if (out/name).exists():
            raise FileExistsError(f'Çıktı zaten var: {out/name}')
    with (out/'group_assignments.jsonl').open('w',encoding='utf-8') as f:
        for row in assignments:
            f.write(json.dumps(row,ensure_ascii=True)+'\n')
    (out/'group_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:v for k,v in report.items() if k!='group_details'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--encoding',default='utf-8')
    args=p.parse_args()
    print(json.dumps(build_groups(args.input,args.output_dir,args.encoding),indent=2))
