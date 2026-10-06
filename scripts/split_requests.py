"""CSIC mini: içerik grupları + sabit train/validation/test ayrımı. Eğitim yapmaz."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

VERSION = 'content-split-v1'
THRESHOLD = 0.97
MIN_TEXT_LENGTH = 40
SEED = 42


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def representation(r):
    """Bu CSIC deneyi için açık Latin-1/form politikası; canlı HTTP parser değildir."""
    target = urlsplit(r['request_target'])
    path = unquote(target.path or '/', encoding='latin-1', errors='strict')
    body = r['body']
    types = [v.split(';')[0].strip().lower() for k,v in r['headers'] if k.lower()=='content-type']
    if body and types != ['application/x-www-form-urlencoded']:
        raise ValueError('Bu deney yalnızca form body destekliyor')
    pairs = sorted(parse_qsl(target.query, keep_blank_values=True, encoding='latin-1', errors='strict')
                   + parse_qsl(body, keep_blank_values=True, encoding='latin-1', errors='strict'))
    # Sıralama yalnızca değerlendirme gruplaması içindir. Model girdisi değiştirilmez.
    names = tuple(k for k,v in pairs)
    values = json.dumps([v for k,v in pairs], ensure_ascii=True, separators=(',', ':'))
    return path, names, values, digest([path,pairs])


def near(a, b):
    if min(len(a),len(b)) < MIN_TEXT_LENGTH:
        return False
    if 2*min(len(a),len(b))/(len(a)+len(b)) < THRESHOLD:
        return False
    matcher=SequenceMatcher(None,a,b,autojunk=False)
    return matcher.quick_ratio() >= THRESHOLD and matcher.ratio() >= THRESHOLD


def make_groups(rows):
    reps=[representation(r) for r in rows]
    parent=list(range(len(rows)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b: parent[max(a,b)]=min(a,b)
    exact=defaultdict(list)
    buckets=defaultdict(list)
    for i,(path,names,values,key) in enumerate(reps):
        exact[key].append(i)
        buckets[(path,names)].append(i)
    for members in exact.values():
        for i in members[1:]: union(members[0],i)
    edges=[]
    for members in buckets.values():
        for i,j in combinations(members,2):
            if reps[i][3]!=reps[j][3] and near(reps[i][2],reps[j][2]):
                union(i,j)
                edges.append([rows[i]['sample_id'],rows[j]['sample_id']])
    # Uzun aynı değer farklı sayfalarda taşınsa da bir arada tut.
    # Sınıf etiketi kullanılmaz; normal uzun değerler de bu kurala tabidir.
    long_values=defaultdict(list)
    for i,(_,_,values,_) in enumerate(reps):
        for value in set(json.loads(values)):
            if len(value)>=40:
                long_values[value].append(i)
    for members in long_values.values():
        for i in members[1:]:
            union(members[0],i)
    components=defaultdict(list)
    for i,r in enumerate(rows): components[root(i)].append(r['sample_id'])
    keys={k:digest(sorted(ids)) for k,ids in components.items()}
    gids=[keys[root(i)] for i in range(len(rows))]
    return gids, reps, dict(exact), edges


def prepare(input_path, features_path, examples_path, output_dir):
    raw=Path(input_path).read_bytes()
    rows=[json.loads(s) for s in raw.decode().splitlines() if s.strip()]
    feature_raw=Path(features_path).read_bytes()
    features=[json.loads(s) for s in feature_raw.decode().splitlines() if s.strip()]
    ids=[r['sample_id'] for r in rows]
    feature_map={r['sample_id']:r for r in features}
    assert len(set(ids))==len(rows)==len(features)==len(feature_map)
    assert set(ids)==set(feature_map)
    assert all(r['label']==feature_map[r['sample_id']]['label'] for r in rows)
    gids,reps,exact,edges=make_groups(rows)
    examples=json.loads(Path(examples_path).read_text())
    pin_ids={r['sample_id'] for r in examples}
    assert pin_ids.issubset(ids)
    pinned={g for r,g in zip(rows,gids) if r['sample_id'] in pin_ids}
    strata=np.array([f"{r['label']}/{r['method']}" for r in rows])
    group_array=np.array(gids)
    folds=np.full(len(rows),-1)
    cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED)
    for fold,(_,indices) in enumerate(cv.split(np.zeros((len(rows),1)),strata,group_array)):
        folds[indices]=fold
    assert np.all(folds>=0)
    splits=['train' if g in pinned or fold>=2 else ('test' if fold==0 else 'validation')
            for g,fold in zip(gids,folds)]
    assignments=[dict(sample_id=r['sample_id'],group_id=g,split=s,label=r['label'],
                      method=r['method'],endpoint=reps[i][0],pinned_to_train=g in pinned)
                 for i,(r,g,s) in enumerate(zip(rows,gids,splits))]
    summary={}
    group_sets={}
    for s in ('train','validation','test'):
        members=[a for a in assignments if a['split']==s]
        group_sets[s]={a['group_id'] for a in members}
        assert {a['label'] for a in members}=={0,1}
        summary[s]=dict(records=len(members),groups=len(group_sets[s]),
            labels=dict(Counter(str(a['label']) for a in members)),
            label_method=dict(Counter(f"{a['label']}/{a['method']}" for a in members)))
    assert sum(x['records'] for x in summary.values())==len(rows)
    for a,b in combinations(group_sets,2): assert not group_sets[a]&group_sets[b]
    lookup={a['sample_id']:a['split'] for a in assignments}
    assert all(lookup[a]==lookup[b] for a,b in edges)
    for members in exact.values(): assert len({splits[i] for i in members})==1
    endpoint_counts=defaultdict(Counter)
    for a in assignments: endpoint_counts[a['endpoint']][a['split']]+=1
    # Tekrarlanan uzun değerlerin kümeler arasında kalmadığını ayrıca doğrula.
    value_uses=defaultdict(list)
    for i,(path,names,values,key) in enumerate(reps):
        for value in set(json.loads(values)):
            if len(value)>=40: value_uses[digest(value)].append(i)
    cross_values=[dict(value_sha256=k,records=len(v),splits=sorted({splits[i] for i in v}),
                       example_ids=[ids[i] for i in v[:5]])
                  for k,v in value_uses.items() if len({splits[i] for i in v})>1]
    assert not cross_values
    details=defaultdict(list)
    for a in assignments: details[a['group_id']].append(a)
    report=dict(version=VERSION,seed=SEED,input_sha256=hashlib.sha256(raw).hexdigest(),
        features_sha256=hashlib.sha256(feature_raw).hexdigest(),records=len(rows),
        exact_groups=len(exact),exact_multi_groups=sum(len(v)>1 for v in exact.values()),
        near_threshold=THRESHOLD,min_similarity_text_length=MIN_TEXT_LENGTH,
        near_edges=len(edges),content_groups=len(details),largest_group=max(map(len,details.values())),
        mixed_label_groups=sum(len({a['label'] for a in v})>1 for v in details.values()),
        pinned_example_ids=sorted(pin_ids),pinned_records=sum(a['pinned_to_train'] for a in assignments),
        splits=summary,common_groups_between_splits=0,common_exact_content_between_splits=0,
        cross_split_near_edges=0,cross_split_long_value_reuse=cross_values,
        major_endpoint_coverage={k:dict(v) for k,v in endpoint_counts.items() if sum(v.values())>=50},
        policy='Exact content ignores method/parameter placement and sorts decoded parameter pairs. '
               'Near grouping requires same path and parameter-name multiset, compares serialized values '
               'with SequenceMatcher >=0.97, min length 40; identical decoded parameter values '
               'of >=40 characters also link records across endpoints. Unions connected components. '
               '5 fixed stratified group folds: 0 test, 1 validation, 2-4 train; reviewed groups pinned train.',
        limitations=['Heuristic similarity is not session identity or a guarantee against all leakage.',
                     'Different parameter names/paths and differently encoded attacks may evade near grouping.',
                     'Sorting/merging query and body is a grouping policy, not server semantic equivalence.',
                     'Old balanced synthetic data only; shared endpoints intentionally allowed.',
                     'Features were previously inspected globally; this is a learning pilot, not pristine external validation.'],
        model_trained=False)
    out=Path(output_dir)
    if out.exists(): raise FileExistsError(f'Yeni çıktı dizini seçin: {out}')
    out.mkdir(parents=True)
    def save(name,records):
        with (out/name).open('w') as f:
            for r in records: f.write(json.dumps(r,ensure_ascii=True,allow_nan=False)+'\n')
    save('assignments.jsonl',assignments)
    save('near_pairs.jsonl',[dict(left=a,right=b) for a,b in edges])
    for s in summary:
        selected=[a for a in assignments if a['split']==s]
        save(s+'_features.jsonl',[dict(feature_map[a['sample_id']],group_id=a['group_id']) for a in selected])
    (out/'split_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True)
    p.add_argument('--features',required=True)
    p.add_argument('--examples',required=True)
    p.add_argument('--output-dir',required=True)
    a=p.parse_args()
    prepare(a.input,a.features,a.examples,a.output_dir)
