"""Lojistik regresyon HTTP IDS deneyi: yalnız train ile fit, yalnız validation ile değerlendirme.

Test özellik dosyası bu betikte açılmaz. Mevcut veri ayrımı değiştirilmez.
Girdi sözleşmesi ve ölçüt hesabı Random Forest deneyiyle ortaktır.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from extract_features import VERSION as EXTRACTOR_VERSION
from train_random_forest import (
    FEATURE_NAMES, binary_metrics, read_jsonl, rows_to_xy, sha256,
    validate_assignments,
)

VERSION = 'logreg-baseline-v1'
LOGREG_PARAMS = dict(C=1.0, max_iter=1000)


def make_pipeline():
    # Ağaçların aksine doğrusal model ölçeğe duyarlıdır: çarpık sayım/uzunluk
    # özellikleri log1p ile sıkıştırılır, sonra eğitim ortalaması/sapmasıyla ölçeklenir.
    return Pipeline([
        ('finite', FunctionTransformer(validate=True, feature_names_out='one-to-one')
         .set_output(transform='pandas')),
        ('drop_constant', VarianceThreshold(threshold=0.0).set_output(transform='pandas')),
        ('log1p', FunctionTransformer(np.log1p, feature_names_out='one-to-one')),
        ('scale', StandardScaler()),
        ('logreg', LogisticRegression(**LOGREG_PARAMS)),
    ])


def score_metrics(y, prediction, scores):
    """Eşikli ölçütlere, eşikten bağımsız ROC AUC değerini ekler."""
    return dict(binary_metrics(y, prediction), roc_auc=float(roc_auc_score(y, scores)))


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
    if (X_train.to_numpy() < 0).any():
        raise ValueError('log1p negatif olmayan özellik bekliyor')

    # TEK fit: seçici, ölçekleyici ve model sadece eğitim kümesini görür.
    pipeline = make_pipeline().fit(X_train, y_train)
    dummy = DummyClassifier(strategy='most_frequent').fit(X_train, y_train)
    X_validation, y_validation = rows_to_xy(rows['validation'])
    predicted = pipeline.predict(X_validation)
    scores = pipeline.predict_proba(X_validation)[:, list(pipeline.classes_).index(1)]
    selector = pipeline.named_steps['drop_constant']
    model = pipeline.named_steps['logreg']
    kept = list(selector.get_feature_names_out())
    dropped = [name for name in FEATURE_NAMES if name not in kept]
    predictions = [dict(sample_id=row['sample_id'], group_id=row['group_id'],
                        label=int(label), prediction=int(pred), anomalous_score=float(score),
                        outcome=('TP' if label else 'FP') if pred else ('FN' if label else 'TN'))
                   for row, label, pred, score in zip(rows['validation'], y_validation, predicted, scores)]
    source_paths = [report_path, split_dir / 'assignments.jsonl',
                    split_dir / 'train_features.jsonl', split_dir / 'validation_features.jsonl']
    script_dir = Path(__file__).parent
    run = dict(version=VERSION, created_at_utc=datetime.now(timezone.utc).isoformat(),
               status='provisional_validation_baseline', model_trained=True,
               test_features_loaded=False, test_evaluated=False,
               training_records=len(y_train), validation_records=len(y_validation),
               test_records_from_split_report=split_report['splits']['test']['records'],
               split_version=split_report['version'], split_changed=False,
               source_sha256={**sources, **{str(p.relative_to(project_root)): sha256(p) for p in source_paths}},
               code_sha256={name: sha256(script_dir / name) for name in
                            ('train_logistic_regression.py', 'train_random_forest.py', 'extract_features.py')},
               extractor_version=EXTRACTOR_VERSION, encoding='latin-1',
               feature_set='basic16_plus_pattern5', input_feature_order=list(FEATURE_NAMES),
               retained_feature_order=kept, dropped_constant_features=dropped,
               train_constant_values={name: float(X_train[name].iloc[0]) for name in dropped},
               train_variances={name: float(v) for name, v in zip(FEATURE_NAMES, selector.variances_)},
               missing_value_policy='Reject null/NaN/inf; no imputation; finite guard saved in pipeline.',
               preprocessing_fit_split='train', scaling='log1p then StandardScaler, fitted on train',
               labels={'0': 'normal', '1': 'anomalous'}, positive_label=1,
               decision=dict(threshold=0.5, rule='score > 0.5; tie at 0.5 predicts class 0',
                             threshold_tuned=False, probability_calibrated=False),
               logreg_parameters=model.get_params(), iterations=int(model.n_iter_[0]),
               # Katsayılar log1p + ölçekleme sonrası uzaydadır; pozitif değer anormal yönüne iter.
               coefficients={name: float(c) for name, c in zip(kept, model.coef_[0])},
               intercept=float(model.intercept_[0]),
               validation=dict(logistic_regression=score_metrics(y_validation, predicted, scores),
                               dummy_most_frequent=binary_metrics(y_validation, dummy.predict(X_validation))),
               packages=dict(python=platform.python_version(), numpy=np.__version__,
                             pandas=pd.__version__, scikit_learn=sklearn.__version__, joblib=joblib.__version__),
               limitations=['Small balanced synthetic CSIC pilot; not real traffic performance.',
                            'Content grouping is heuristic; shared endpoints are intentional.',
                            'Global features were inspected before this run.',
                            'Anomalous is a source label, not proof of an attack.',
                            'No hyperparameter search, threshold tuning, or basic-only ablation performed.',
                            'The test split was already observed by rf-baseline-v1; it is not unseen for this project.'])
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
