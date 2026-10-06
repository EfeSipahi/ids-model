"""İlk HTTP IDS deneyi: yalnız train ile fit, yalnız validation ile değerlendirme.

Test özellik dosyası bu betikte açılmaz. Mevcut veri ayrımı değiştirilmez.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from extract_features import BASIC_FEATURES, PATTERN_FEATURES, VERSION as EXTRACTOR_VERSION

VERSION = 'rf-baseline-v1'
FEATURE_NAMES = BASIC_FEATURES + PATTERN_FEATURES
RF_PARAMS = dict(n_estimators=100, max_depth=10, min_samples_leaf=5,
                 random_state=42, n_jobs=2)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines()
            if line.strip()]


def rows_to_xy(rows):
    """Dış alanlar X'e alınmaz; adlar ve sıra çıkarıcının açık listesinden gelir."""
    if not rows:
        raise ValueError('Boş veri kümesi')
    ids = [row['sample_id'] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('Tekrarlı sample_id')
    for row in rows:
        if set(row['features']) != set(FEATURE_NAMES):
            raise ValueError(f"Özellik şeması uyuşmuyor: {row['sample_id']}")
        if type(row['label']) is not int or row['label'] not in (0, 1):
            raise ValueError('Etiket 0 veya 1 tamsayısı olmalı')
        for name in FEATURE_NAMES:
            value = row['features'][name]
            if type(value) not in (int, float) or not np.isfinite(value):
                raise ValueError(f"Eksik/geçersiz özellik: {row['sample_id']} / {name}")
    X = pd.DataFrame([{name: row['features'][name] for name in FEATURE_NAMES}
                      for row in rows], columns=list(FEATURE_NAMES), dtype=float)
    y = np.asarray([row['label'] for row in rows], dtype=int)
    return X, y


def make_pipeline():
    # finite ayrıca kaydedilen modelin NaN/inf girdisini sessizce kabul etmesini önler.
    return Pipeline([
        ('finite', FunctionTransformer(validate=True, feature_names_out='one-to-one')
         .set_output(transform='pandas')),
        ('drop_constant', VarianceThreshold(threshold=0.0).set_output(transform='pandas')),
        ('forest', RandomForestClassifier(**RF_PARAMS)),
    ])


def binary_metrics(y, prediction):
    matrix = confusion_matrix(y, prediction, labels=[0, 1])
    tn, fp, fn, tp = map(int, matrix.ravel())
    return dict(confusion_matrix=matrix.tolist(), tn=tn, fp=fp, fn=fn, tp=tp,
                accuracy=float(accuracy_score(y, prediction)),
                precision=float(precision_score(y, prediction, zero_division=0)),
                recall=float(recall_score(y, prediction, zero_division=0)),
                f1=float(f1_score(y, prediction, zero_division=0)),
                false_positive_rate=fp / (fp + tn) if fp + tn else None)


def validate_assignments(assignments, split_report, selected_rows):
    lookup = {a['sample_id']: a for a in assignments}
    if len(lookup) != len(assignments) or len(assignments) != split_report['records']:
        raise ValueError('Atama sayısı/kimlikleri uyuşmuyor')
    if {a['split'] for a in assignments} != {'train', 'validation', 'test'}:
        raise ValueError('Beklenmeyen bölüm adı')
    group_splits = {}
    for a in assignments:
        previous = group_splits.setdefault(a['group_id'], a['split'])
        if previous != a['split']:
            raise ValueError('Bir grup birden fazla bölümde')
        if a['pinned_to_train'] and a['split'] != 'train':
            raise ValueError('Önceden incelenen örnek eğitim dışında')
    for split in ('train', 'validation', 'test'):
        members = [a for a in assignments if a['split'] == split]
        summary = dict(records=len(members), groups=len({a['group_id'] for a in members}),
                       labels=dict(Counter(str(a['label']) for a in members)),
                       label_method=dict(Counter(f"{a['label']}/{a['method']}" for a in members)))
        if summary != split_report['splits'][split]:
            raise ValueError(f'Atamalar raporla uyuşmuyor: {split}')
    for split, rows in selected_rows.items():
        expected_ids = {a['sample_id'] for a in assignments if a['split'] == split}
        if {r['sample_id'] for r in rows} != expected_ids or len(rows) != len(expected_ids):
            raise ValueError(f'Özellik kimlikleri uyuşmuyor: {split}')
        for row in rows:
            a = lookup[row['sample_id']]
            if row['label'] != a['label'] or row['group_id'] != a['group_id']:
                raise ValueError(f"Etiket/grup uyuşmuyor: {row['sample_id']}")


def run_experiment(project_root, output_dir):
    project_root, output_dir = Path(project_root).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError(f'Yeni çıktı dizini seçin: {output_dir}')
    split_dir = project_root / 'data/processed/http-mini-splits-v1'
    report_path = split_dir / 'split_report.json'
    split_report = json.loads(report_path.read_text(encoding='utf-8'))
    if split_report['version'] != 'content-split-v1':
        raise ValueError('Bu deney güncel content-split-v1 ayrımını bekliyor')
    # Kaynakların sadece bayt bütünlüğü denetlenir; buradan X/y oluşturulmaz.
    sources = {'data/http-mini/requests.jsonl': split_report['input_sha256'],
               'data/processed/http-mini-features-v1/features.jsonl': split_report['features_sha256']}
    for relative, expected in sources.items():
        if sha256(project_root / relative) != expected:
            raise ValueError(f'Kaynak SHA-256 uyuşmuyor: {relative}')
    assignments = read_jsonl(split_dir / 'assignments.jsonl')
    rows = {split: read_jsonl(split_dir / f'{split}_features.jsonl')
            for split in ('train', 'validation')}
    validate_assignments(assignments, split_report, rows)
    X_train, y_train = rows_to_xy(rows['train'])
    if set(y_train) != {0, 1}:
        raise ValueError('Eğitimde iki sınıf da bulunmalı')

    # TEK fit: seçici ve orman sadece eğitim kümesini görür.
    pipeline = make_pipeline().fit(X_train, y_train)
    dummy = DummyClassifier(strategy='most_frequent').fit(X_train, y_train)
    X_validation, y_validation = rows_to_xy(rows['validation'])
    predicted = pipeline.predict(X_validation)
    scores = pipeline.predict_proba(X_validation)[:, list(pipeline.classes_).index(1)]
    selector = pipeline.named_steps['drop_constant']
    kept = list(selector.get_feature_names_out())
    dropped = [name for name in FEATURE_NAMES if name not in kept]
    predictions = [dict(sample_id=row['sample_id'], group_id=row['group_id'],
                        label=int(label), prediction=int(pred), anomalous_score=float(score),
                        outcome=('TP' if label else 'FP') if pred else ('FN' if label else 'TN'))
                   for row, label, pred, score in zip(rows['validation'], y_validation, predicted, scores)]
    validation_metrics = binary_metrics(y_validation, predicted)
    source_paths = [report_path, split_dir / 'assignments.jsonl',
                    split_dir / 'train_features.jsonl', split_dir / 'validation_features.jsonl']
    run = dict(version=VERSION, created_at_utc=datetime.now(timezone.utc).isoformat(),
               status='provisional_validation_baseline', model_trained=True,
               test_features_loaded=False, test_evaluated=False,
               training_records=len(y_train), validation_records=len(y_validation),
               test_records_from_split_report=split_report['splits']['test']['records'],
               split_version=split_report['version'], split_changed=False,
               source_sha256={**sources, **{str(p.relative_to(project_root)): sha256(p) for p in source_paths}},
               code_sha256={'train_random_forest.py': sha256(__file__),
                            'extract_features.py': sha256(Path(__file__).with_name('extract_features.py'))},
               extractor_version=EXTRACTOR_VERSION, encoding='latin-1',
               feature_set='basic16_plus_pattern5', input_feature_order=list(FEATURE_NAMES),
               retained_feature_order=kept, dropped_constant_features=dropped,
               train_constant_values={name: float(X_train[name].iloc[0]) for name in dropped},
               train_variances={name: float(v) for name, v in zip(FEATURE_NAMES, selector.variances_)},
               missing_value_policy='Reject null/NaN/inf; no imputation; finite guard saved in pipeline.',
               preprocessing_fit_split='train', scaling=None,
               labels={'0': 'normal', '1': 'anomalous'}, positive_label=1,
               decision=dict(threshold=0.5, rule='score > 0.5; tie at 0.5 predicts class 0',
                             threshold_tuned=False, probability_calibrated=False),
               forest_parameters=pipeline.named_steps['forest'].get_params(),
               validation=dict(random_forest=validation_metrics,
                               dummy_most_frequent=binary_metrics(y_validation, dummy.predict(X_validation))),
               packages=dict(python=platform.python_version(), numpy=np.__version__,
                             pandas=pd.__version__, scikit_learn=sklearn.__version__, joblib=joblib.__version__),
               limitations=['Small balanced synthetic CSIC pilot; not real traffic performance.',
                            'Content grouping is heuristic; shared endpoints are intentional.',
                            'Global features were inspected before this run.',
                            'Anomalous is a source label, not proof of an attack.',
                            'No hyperparameter search, threshold tuning, or basic-only ablation performed.'])
    # Tahmin kuralı kaydedilen eşik açıklamasıyla aynı olmalı.
    if not np.array_equal(predicted, (scores > 0.5).astype(int)):
        raise RuntimeError('Tahmin ve eşik kuralı uyuşmuyor')
    output_dir.mkdir(parents=True, exist_ok=False)
    joblib.dump(pipeline, output_dir / 'pipeline.joblib')
    run['pipeline_sha256'] = sha256(output_dir / 'pipeline.joblib')
    (output_dir / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    for name, selected in [('validation_predictions.jsonl', predictions),
                           ('validation_errors.jsonl', [r for r in predictions if r['outcome'] in ('FP', 'FN')])]:
        (output_dir / name).write_text(''.join(json.dumps(r, ensure_ascii=True, allow_nan=False) + '\n'
                                            for r in selected), encoding='utf-8')
    return run


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = run_experiment(args.project_root, args.output_dir)
    print(json.dumps({key: result[key] for key in ('training_records', 'validation_records',
                      'dropped_constant_features', 'validation', 'test_evaluated')}, indent=2))
