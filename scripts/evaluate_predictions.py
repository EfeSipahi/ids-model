"""Kayıtlı bir deneyin tahmin dosyalarından sınıflandırma ölçütlerini hesaplar.

Model yüklenmez, eğitim yapılmaz, özellik dosyaları açılmaz: yalnız deneyin daha önce
yazdığı etiket/tahmin/skor kayıtları okunur. Bu yüzden kayıtlı deney klasörleri ve
hash'leri değişmez; sonuç ayrı bir klasöre yazılır.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_curve

from train_logistic_regression import score_metrics
from train_random_forest import read_jsonl, sha256

RECORDED_KEYS = ('confusion_matrix', 'tn', 'fp', 'fn', 'tp', 'accuracy', 'precision',
                 'recall', 'f1', 'false_positive_rate')


def evaluate_rows(rows, recorded=None, threshold=0.5):
    """Hata matrisi, doğruluk, kesinlik, duyarlılık, F1, YPO, ROC AUC ve ROC noktaları."""
    if not rows:
        raise ValueError('Boş tahmin dosyası')
    y = np.asarray([row['label'] for row in rows])
    prediction = np.asarray([row['prediction'] for row in rows])
    scores = np.asarray([row['anomalous_score'] for row in rows], dtype=float)
    if set(y) != {0, 1} or not set(prediction) <= {0, 1}:
        raise ValueError('Etiketlerde iki sınıf, tahminlerde yalnız 0/1 bulunmalı')
    if not np.isfinite(scores).all() or scores.min() < 0 or scores.max() > 1:
        raise ValueError('Skorlar 0-1 aralığında sonlu sayılar olmalı')
    if not np.array_equal(prediction, (scores > threshold).astype(int)):
        raise ValueError('Tahminler kayıtlı skor ve karar eşiğiyle uyuşmuyor')
    for row in rows:
        expected = ('TP' if row['label'] else 'FP') if row['prediction'] else ('FN' if row['label'] else 'TN')
        if row['outcome'] != expected:
            raise ValueError(f"Sonuç etiketi uyuşmuyor: {row['sample_id']}")
    metrics = score_metrics(y, prediction, scores)
    # Yeniden hesaplanan eşikli ölçütler deneyin kendi kaydıyla aynı çıkmalı.
    if recorded is not None:
        for key in RECORDED_KEYS:
            if not np.allclose(metrics[key], recorded[key]):
                raise ValueError(f'Kayıtlı ölçütle uyuşmuyor: {key}')
    fpr, tpr, thresholds = roc_curve(y, scores)
    # İlk nokta (0, 0) "hiçbir isteğe anormal deme" eşiğidir; sonsuz yerine null yazılır.
    curve = [dict(threshold=float(t) if np.isfinite(t) else None,
                  false_positive_rate=float(f), true_positive_rate=float(r))
             for t, f, r in zip(thresholds, fpr, tpr)]
    return dict(records=len(rows), labels={str(label): int((y == label).sum()) for label in (0, 1)},
                metrics=metrics, roc_curve=curve)


def run(project_root, experiment, output_dir=None):
    project_root = Path(project_root).resolve()
    output_dir = Path(output_dir).resolve() if output_dir else project_root / 'reports' / f'{experiment}-metrics'
    if output_dir.exists():
        raise FileExistsError(f'Yeni çıktı dizini seçin: {output_dir}')
    model_dir = project_root / 'models' / experiment
    training_run = json.loads((model_dir / 'run.json').read_text(encoding='utf-8'))
    if training_run['version'] != experiment:
        raise ValueError('Deney adı run.json sürümüyle uyuşmuyor')
    trained = [name for name in training_run['validation'] if name != 'dummy_most_frequent']
    if len(trained) != 1:
        raise ValueError('run.json içinde tek bir eğitilmiş model bekleniyor')
    # Eşik deneyin kendi kaydından gelir: v1'de 0,5, v2'de eğitimde seçilen değer.
    threshold = training_run['decision']['threshold']
    if type(threshold) is not float or not 0 < threshold < 1:
        raise ValueError('Kayıtlı karar eşiği geçersiz')
    sources = {'validation': (model_dir / 'validation_predictions.jsonl',
                              training_run['validation'][trained[0]])}
    # Test tahminleri yalnız test daha önce değerlendirilip kaydedildiyse okunur.
    test_dir = project_root / 'reports' / f'{experiment}-test'
    if test_dir.exists():
        test_report = json.loads((test_dir / 'test_report.json').read_text(encoding='utf-8'))
        sources['test'] = (test_dir / 'test_predictions.jsonl', test_report['metrics'])
    result = dict(experiment=experiment, model=trained[0], model_loaded=False, refit=False,
                  threshold=threshold, positive_label=1,
                  confusion_matrix_order='rows=actual [0,1], columns=predicted [0,1]',
                  source_sha256={}, splits={})
    for split, (path, recorded) in sources.items():
        result['source_sha256'][str(path.relative_to(project_root))] = sha256(path)
        result['splits'][split] = evaluate_rows(read_jsonl(path), recorded, threshold)
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / 'classification_metrics.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', help='models/ altındaki deney adı, ör. rf-baseline-v1')
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    outcome = run(args.project_root, args.experiment, args.output_dir)
    print(json.dumps({split: values['metrics'] for split, values in outcome['splits'].items()}, indent=2))
