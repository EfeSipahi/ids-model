"""Kaydedilmiş rf-baseline-v1 modelini final testte değerlendirir; eğitim yapmaz."""
from datetime import datetime, timezone
import json
from pathlib import Path

import joblib
import numpy as np
import sklearn

from train_random_forest import (
    FEATURE_NAMES, binary_metrics, read_jsonl, rows_to_xy, sha256,
    validate_assignments,
)


def main():
    root = Path(__file__).resolve().parents[1]
    model_dir = root / 'models/rf-baseline-v1'
    split_dir = root / 'data/processed/http-mini-splits-v1'
    output = root / 'reports/rf-baseline-v1-test'
    if output.exists():
        raise FileExistsError('Test kaydı zaten var; mevcut sonuçların üzerine yazılmaz.')
    run_path = model_dir / 'run.json'
    run = json.loads(run_path.read_text(encoding='utf-8'))
    model_path = model_dir / 'pipeline.joblib'
    model_hash = sha256(model_path)
    if model_hash != run['pipeline_sha256']:
        raise ValueError('Kaydedilmiş modelin SHA-256 değeri değişmiş')
    for relative, expected in run['source_sha256'].items():
        if sha256(root / relative) != expected:
            raise ValueError(f'Veri bütünlüğü uyuşmuyor: {relative}')
    for filename, expected in run['code_sha256'].items():
        if sha256(root / 'scripts' / filename) != expected:
            raise ValueError(f'Eğitim kodu değişmiş: {filename}')
    if sklearn.__version__ != run['packages']['scikit_learn']:
        raise ValueError('scikit-learn sürümü eğitim ortamından farklı')
    model = joblib.load(model_path)
    if list(FEATURE_NAMES) != run['input_feature_order']:
        raise ValueError('Özellik sözleşmesi değişmiş')
    if list(model.feature_names_in_) != run['input_feature_order']:
        raise ValueError('Model girdi sırası uyuşmuyor')
    if list(model.named_steps['drop_constant'].get_feature_names_out()) != run['retained_feature_order']:
        raise ValueError('Öğrenilmiş sütun seçimi uyuşmuyor')
    if model.named_steps['forest'].get_params() != run['forest_parameters']:
        raise ValueError('Model parametreleri değişmiş')
    if run['decision']['threshold'] != 0.5 or list(model.classes_) != [0, 1]:
        raise ValueError('Beklenen karar kuralı/sınıflar uyuşmuyor')

    # Model ve eşik test özellikleri okunmadan önce kayda geçirilir.
    selection = dict(
        fixed_at_utc=datetime.now(timezone.utc).isoformat(),
        model='models/rf-baseline-v1/pipeline.joblib', model_sha256=model_hash,
        training_run_sha256=sha256(run_path),
        evaluation_script_sha256=sha256(__file__),
        input_feature_order=run['input_feature_order'],
        retained_feature_order=run['retained_feature_order'],
        forest_parameters=run['forest_parameters'], decision=run['decision'],
        training_records=604, refit=False,
    )
    output.mkdir(exist_ok=False)
    def save_json(name, value):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                              allow_nan=False) + '\n', encoding='utf-8')
    save_json('selection_before_test.json', selection)

    test_path = split_dir / 'test_features.jsonl'
    rows = read_jsonl(test_path)
    split_report = json.loads((split_dir / 'split_report.json').read_text(encoding='utf-8'))
    assignments = read_jsonl(split_dir / 'assignments.jsonl')
    validate_assignments(assignments, split_report, {'test': rows})
    X_test, y_test = rows_to_xy(rows)
    if X_test.shape != (199, 21):
        raise ValueError('Beklenen test boyutu 199 x 21')
    state_before = joblib.hash(model)
    # Sadece tahmin: fit/fit_transform çağrısı yok.
    predictions = model.predict(X_test)
    scores = model.predict_proba(X_test)[:, 1]
    if not np.array_equal(predictions, (scores > 0.5).astype(int)):
        raise ValueError('Tahminler sabit karar kuralıyla uyuşmuyor')
    if state_before != joblib.hash(model) or sha256(model_path) != model_hash:
        raise RuntimeError('Değerlendirme sırasında model değişmiş')
    metrics = binary_metrics(y_test, predictions)
    records = [dict(sample_id=row['sample_id'], group_id=row['group_id'],
                    label=int(label), prediction=int(pred), anomalous_score=float(score),
                    outcome=('TP' if label else 'FP') if pred else ('FN' if label else 'TN'))
               for row, label, pred, score in zip(rows, y_test, predictions, scores)]
    (output / 'test_predictions.jsonl').write_text(
        ''.join(json.dumps(row, ensure_ascii=True, allow_nan=False) + '\n' for row in records),
        encoding='utf-8')
    result = dict(
        evaluated_at_utc=datetime.now(timezone.utc).isoformat(),
        evaluation='final_test_of_fixed_rf_baseline_v1', test_evaluated=True,
        test_records=len(rows), test_groups=len({r['group_id'] for r in rows}),
        labels={str(label): int((y_test == label).sum()) for label in (0, 1)},
        test_features_sha256=sha256(test_path), model_sha256=model_hash,
        training_run_sha256=sha256(run_path),
        evaluation_script_sha256=sha256(__file__),
        model_unchanged=True, refit=False, threshold_tuned=False,
        positive_label=1, confusion_matrix_order='rows=actual [0,1], columns=predicted [0,1]',
        metrics=metrics, validation_metrics=run['validation']['random_forest'],
        sklearn_version=sklearn.__version__,
        limitations=run['limitations'][:4] + [
            'This test is now observed; do not tune against it and call it unseen.',
            'Metrics are per request; grouped requests are not fully independent.',
        ],
    )
    save_json('test_report.json', result)
    v = result['validation_metrics']
    names = [('accuracy', 'Accuracy'), ('precision', 'Precision'), ('recall', 'Recall'),
             ('f1', 'F1'), ('false_positive_rate', 'Yanlış alarm oranı')]
    table = '\n'.join(f'| {name} | %{v[key]*100:.2f} | %{metrics[key]*100:.2f} |'
                      for key, name in names)
    report = f'''# Sabit Random Forest — final test sonucu

Kaydedilmiş `rf-baseline-v1` modeli 199 test kaydında değerlendirildi.
Model 604 eğitim kaydında öğrenilmişti; bu işlemde yeniden eğitim yapılmadı.
197 doğrulama kaydı da eğitime eklenmedi. Özellikler, ağaç ayarları ve 0,5 karar eşiği
değiştirilmedi. Eşitlikte normal sınıf seçilir. Kaynak metadata'sı model girdisi değildir.

## Nasıl çalıştırıldı?

1. Model, eğitim kodu ve veri hash'leri önceki kayıtla karşılaştırıldı.
2. Model ve karar kuralı test okunmadan `selection_before_test.json` dosyasına yazıldı.
3. Test kimlikleri, etiketleri ve grupları mevcut atamalarla doğrulandı.
4. Sadece `features` alanından X, `label` alanından y oluşturuldu.
5. Kaydedilmiş pipeline ile `predict` çağrıldı; `fit` çağrılmadı.
   Eğitimde öğrenilen aynı üç sütun çıkarıldı; orman aynı 18 özelliği kullandı.
6. Tahminler gerçek etiketlerle karşılaştırıldı. Bellekteki ve diskteki modelin
   değişmediği doğrulandı. Veriler ve önceki deney kayıtları değiştirilmedi.

## Sonuç

| Gerçek etiket | Tahmin normal | Tahmin anormal |
|---|---:|---:|
| Normal (100) | {metrics['tn']} doğru normal | {metrics['fp']} yanlış alarm |
| Anormal (99) | {metrics['fn']} kaçırılan | {metrics['tp']} yakalanan |

| Ölçüt | Doğrulama (197) | Test (199) |
|---|---:|---:|
{table}

Precision = TP/(TP+FP), recall = TP/(TP+FN), yanlış alarm oranı = FP/(FP+TN).
Pozitif sınıf 1, kaynak verideki anormal etiketidir; doğrulanmış saldırı anlamına gelmez.
Skor kalibre edilmiş saldırı olasılığı değildir.

Bu testte {metrics['tp'] + metrics['tn']}/199 doğru tahmin var.
100 normal isteğin {metrics['fp']}'ine yanlış alarm verildi;
99 anormal isteğin {metrics['fn']}'i kaçırıldı.

## Dosyalar

- `selection_before_test.json`: test öncesi sabit model ve karar kuralı.
- `test_report.json`: tam metrikler, bütünlük bilgileri ve değerlendirme durumu.
- `test_predictions.jsonl`: 199 isteğin etiketi, tahmini ve skoru.
- `README.md`: bu açıklama.

Çalıştırılan komut (sonuç dizini zaten varsa betik tekrar çalışmaz):

```bash
cd /home/esip/Documents/ids-model
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_test.py
```

## Sınırlar ve güncel durum

Bu küçük, eski, sentetik ve dengeli CSIC pilotudur; gerçek trafik başarımı değildir.
İçerik gruplaması tüm sızıntıları garantiyle engellemez. Metrikler istek başınadır;
aynı grup içindeki kayıtlar bağımsız gözlemler sayılmaz. Özellikler daha önce genel
olarak incelenmiştir. Bu sonuç bağımsız dış saha doğrulaması değildir.

Test artık değerlendirildi. Bu sonuçlara göre model değiştirilecekse aynı küme
yeniden hiç görülmemiş final testi gibi sunulmamalıdır. Bu çalışmada test sonucuna
göre ayar değişikliği yapılmadı. Eski `run.json` ve önceki raporların testin henüz
açılmadığını belirten alanları tarihsel eğitim aşamasını anlatır; güncel test kaydı buradadır.
'''
    (output / 'README.md').write_text(report, encoding='utf-8')
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f'Sonuçlar: {output}')


if __name__ == '__main__':
    main()
