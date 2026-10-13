"""Parametre aramalı (v2) HTTP IDS deneyi: bütün seçimler yalnız train içinde yapılır.

Model parametreleri ve karar eşiği, eğitim kümesinde gruplu çapraz doğrulamanın kat dışı
tahminleriyle seçilir. Validation yalnız seçim bittikten sonra ölçülür; test özellik dosyası
bu betikte açılmaz. Girdi sözleşmesi ve ön işleme adımları v1 deneyleriyle ortaktır.
"""
import argparse
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedGroupKFold

from extract_features import VERSION as EXTRACTOR_VERSION
import train_logistic_regression
import train_random_forest
from train_logistic_regression import score_metrics
from train_random_forest import (
    FEATURE_NAMES, binary_metrics, read_jsonl, rows_to_xy, sha256,
    validate_assignments,
)

FOLDS, SEED = 5, 42
THRESHOLDS = tuple(round(0.30 + 0.05 * step, 2) for step in range(9))


def _grid(fixed, **options):
    return [dict(fixed, **dict(zip(options, values))) for values in product(*options.values())]


# Adaylar basitten karmaşığa sıralıdır; tam eşitlikte listede önce gelen seçilir.
MODELS = {
    'rf': dict(
        version='rf-tuned-v2', name='random_forest', step='forest',
        make_pipeline=train_random_forest.make_pipeline,
        scaling=None,
        grid=_grid(dict(random_state=SEED, n_jobs=-1),
                   n_estimators=(200, 500), max_depth=(5, 10, 20, None),
                   min_samples_leaf=(10, 5, 2, 1), max_features=('sqrt', 0.5))),
    'logreg': dict(
        version='logreg-tuned-v2', name='logistic_regression', step='logreg',
        make_pipeline=train_logistic_regression.make_pipeline,
        scaling='log1p then StandardScaler, fitted on train',
        # l1_ratio 0 = L2 (lbfgs), 1 = L1 (liblinear); küçük C daha güçlü düzenlileştirmedir.
        grid=[dict(C=C, class_weight=weight, max_iter=5000, **penalty)
              for penalty in (dict(l1_ratio=0.0, solver='lbfgs'),
                              dict(l1_ratio=1.0, solver='liblinear', random_state=SEED))
              for weight in (None, 'balanced')
              for C in (0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0)]),
}


def build_pipeline(spec, params):
    """v1 ön işleme adımlarını aynen kullanır; yalnız son adımın parametreleri değişir."""
    return spec['make_pipeline']().set_params(**{f"{spec['step']}__{key}": value
                                                 for key, value in params.items()})


def anomalous_scores(pipeline, X):
    return pipeline.predict_proba(X)[:, list(pipeline.classes_).index(1)]


def decide(scores, threshold):
    return (np.asarray(scores) > threshold).astype(int)


def out_of_fold_scores(spec, params, X, y, groups):
    """Her kayıt, kendi içerik grubunu görmemiş bir modelden skor alır."""
    folds = StratifiedGroupKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    scores = np.full(len(y), np.nan)
    for fit_index, held_index in folds.split(X, y, groups):
        if set(groups[fit_index]) & set(groups[held_index]):
            raise RuntimeError('Bir grup iki kata bölünmüş')
        fold_model = clone(build_pipeline(spec, params)).fit(X.iloc[fit_index], y[fit_index])
        scores[held_index] = anomalous_scores(fold_model, X.iloc[held_index])
    if not np.isfinite(scores).all():
        raise RuntimeError('Kat dışı skor eksik')
    return scores


def search(spec, X, y, groups, grid=None):
    """Aday parametreleri 0,5 eşiğindeki kat dışı F1 ile, sonra eşiği aynı skorlarla seçer."""
    candidates = []
    for index, params in enumerate(grid or spec['grid']):
        scores = out_of_fold_scores(spec, params, X, y, groups)
        candidates.append((dict(index=index, params=params, cv=score_metrics(y, decide(scores, 0.5), scores)), scores))
    # F1 yüksek, eşitlikte yanlış pozitif oranı düşük, sonra listede önce gelen (daha basit) aday.
    best, best_scores = min(candidates, key=lambda c: (-c[0]['cv']['f1'], c[0]['cv']['false_positive_rate'], c[0]['index']))
    thresholds = [dict(threshold=t, **binary_metrics(y, decide(best_scores, t))) for t in THRESHOLDS]
    # Eşitlikte 0,5'e en yakın eşik: gereksiz yere varsayılandan uzaklaşılmaz.
    chosen = min(thresholds, key=lambda t: (-t['f1'], abs(t['threshold'] - 0.5), t['threshold']))
    return dict(candidates=[c for c, _ in candidates], selected_index=best['index'],
                selected_params=best['params'], selected_cv_at_0_5=best['cv'],
                threshold_search=thresholds, selected_threshold=chosen['threshold'],
                selected_cv=dict({k: v for k, v in chosen.items() if k != 'threshold'},
                                 roc_auc=best['cv']['roc_auc']))


def run_experiment(project_root, output_dir, model, grid=None):
    spec = MODELS[model]
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
    train_rows = read_jsonl(split_dir / 'train_features.jsonl')
    X_train, y_train = rows_to_xy(train_rows)
    groups = np.asarray([row['group_id'] for row in train_rows])
    if set(y_train) != {0, 1}:
        raise ValueError('Eğitimde iki sınıf da bulunmalı')
    if (X_train.to_numpy() < 0).any():
        raise ValueError('log1p negatif olmayan özellik bekliyor')

    # Parametreler ve eşik validation dosyası okunmadan önce, yalnız eğitimle sabitlenir.
    found = search(spec, X_train, y_train, groups, grid)
    threshold = found['selected_threshold']
    # TEK son fit: seçilen ayarla tüm eğitim kümesi.
    pipeline = build_pipeline(spec, found['selected_params']).fit(X_train, y_train)
    dummy = DummyClassifier(strategy='most_frequent').fit(X_train, y_train)

    validation_rows = read_jsonl(split_dir / 'validation_features.jsonl')
    validate_assignments(assignments, split_report, dict(train=train_rows, validation=validation_rows))
    X_validation, y_validation = rows_to_xy(validation_rows)
    scores = anomalous_scores(pipeline, X_validation)
    predicted = decide(scores, threshold)
    selector = pipeline.named_steps['drop_constant']
    kept = list(selector.get_feature_names_out())
    dropped = [name for name in FEATURE_NAMES if name not in kept]
    predictions = [dict(sample_id=row['sample_id'], group_id=row['group_id'],
                        label=int(label), prediction=int(pred), anomalous_score=float(score),
                        outcome=('TP' if label else 'FP') if pred else ('FN' if label else 'TN'))
                   for row, label, pred, score in zip(validation_rows, y_validation, predicted, scores)]
    source_paths = [report_path, split_dir / 'assignments.jsonl',
                    split_dir / 'train_features.jsonl', split_dir / 'validation_features.jsonl']
    script_dir = Path(__file__).parent
    run = dict(version=spec['version'], created_at_utc=datetime.now(timezone.utc).isoformat(),
               status='tuned_on_train_cross_validation', model_trained=True,
               test_features_loaded=False, test_evaluated=False,
               training_records=len(y_train), validation_records=len(y_validation),
               test_records_from_split_report=split_report['splits']['test']['records'],
               split_version=split_report['version'], split_changed=False,
               source_sha256={**sources, **{str(p.relative_to(project_root)): sha256(p) for p in source_paths}},
               code_sha256={name: sha256(script_dir / name) for name in
                            ('train_tuned.py', 'train_logistic_regression.py',
                             'train_random_forest.py', 'extract_features.py')},
               extractor_version=EXTRACTOR_VERSION, encoding='latin-1',
               feature_set='basic16_plus_pattern5', input_feature_order=list(FEATURE_NAMES),
               retained_feature_order=kept, dropped_constant_features=dropped,
               missing_value_policy='Reject null/NaN/inf; no imputation; finite guard saved in pipeline.',
               preprocessing_fit_split='train', scaling=spec['scaling'],
               labels={'0': 'normal', '1': 'anomalous'}, positive_label=1,
               model=spec['name'], model_step=spec['step'],
               model_parameters=pipeline.named_steps[spec['step']].get_params(),
               selection=dict(
                   data='train only; validation and test not used',
                   cross_validation=f'StratifiedGroupKFold(n_splits={FOLDS}, shuffle=True, random_state={SEED}) by group_id',
                   training_groups=len(set(groups)), candidates=len(found['candidates']),
                   parameter_rule='max out-of-fold F1 at threshold 0.5; ties: lower false positive rate, then earlier (simpler) candidate',
                   threshold_rule='max out-of-fold F1 of the selected candidate; ties: closest to 0.5',
                   thresholds_tried=list(THRESHOLDS), selected_index=found['selected_index'],
                   selected_params=found['selected_params'],
                   cross_validation_at_0_5=found['selected_cv_at_0_5'],
                   cross_validation_at_selected_threshold=found['selected_cv']),
               decision=dict(threshold=threshold, rule=f'score > {threshold}; tie at the threshold predicts class 0',
                             threshold_tuned=True, threshold_source='out-of-fold train predictions',
                             probability_calibrated=False),
               validation={spec['name']: score_metrics(y_validation, predicted, scores),
                           'dummy_most_frequent': binary_metrics(y_validation, dummy.predict(X_validation))},
               packages=dict(python=platform.python_version(), numpy=np.__version__,
                             pandas=pd.__version__, scikit_learn=sklearn.__version__, joblib=joblib.__version__),
               limitations=['Small balanced synthetic CSIC pilot; not real traffic performance.',
                            'Content grouping is heuristic; shared endpoints are intentional.',
                            'Global features were inspected before this run.',
                            'Anomalous is a source label, not proof of an attack.',
                            'Parameters and threshold were chosen on 604 training records; cross-validation estimates are noisy.',
                            'The test split was already observed by the v1 baselines; it is not unseen for this project.'])
    output_dir.mkdir(parents=True, exist_ok=False)
    joblib.dump(pipeline, output_dir / 'pipeline.joblib')
    run['pipeline_sha256'] = sha256(output_dir / 'pipeline.joblib')

    def save_json(name, value):
        (output_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                                       encoding='utf-8')
    save_json('run.json', run)
    save_json('search_results.json', dict(version=spec['version'], candidates=found['candidates'],
                                          threshold_search=found['threshold_search']))
    for name, selected in [('validation_predictions.jsonl', predictions),
                           ('validation_errors.jsonl', [r for r in predictions if r['outcome'] in ('FP', 'FN')])]:
        (output_dir / name).write_text(''.join(json.dumps(r, ensure_ascii=True, allow_nan=False) + '\n'
                                            for r in selected), encoding='utf-8')
    return run


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=sorted(MODELS), required=True)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = run_experiment(args.project_root, args.output_dir, args.model)
    print(json.dumps(dict(selected_params=result['selection']['selected_params'],
                          threshold=result['decision']['threshold'],
                          cross_validation=result['selection']['cross_validation_at_selected_threshold'],
                          validation=result['validation'][result['model']]), indent=2))
