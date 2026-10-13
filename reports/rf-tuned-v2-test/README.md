# Sabit `rf-tuned-v2` — final test sonucu

Kaydedilmiş `rf-tuned-v2` modeli 199 test kaydında değerlendirildi.
Model 604 eğitim kaydında öğrenilmişti; bu işlemde yeniden eğitim yapılmadı.
197 doğrulama kaydı eğitime ve parametre seçimine eklenmedi.

## Seçilen ayarlar

Parametreler ve karar eşiği yalnız eğitim kümesinde, içerik gruplarına göre bölünmüş
StratifiedGroupKFold çapraz doğrulamasının kat dışı tahminleriyle seçildi
(64 aday denendi). Doğrulama ve test kümeleri seçimde kullanılmadı.

- `random_state`: `42`
- `n_jobs`: `-1`
- `n_estimators`: `200`
- `max_depth`: `10`
- `min_samples_leaf`: `1`
- `max_features`: `sqrt`
- karar eşiği: `0.5` (skor bu değerden büyükse anormal; eşitlikte normal)

## Nasıl çalıştırıldı?

1. Model, eğitim kodu ve veri hash'leri eğitim kaydıyla karşılaştırıldı.
2. Model ve karar kuralı test okunmadan `selection_before_test.json` dosyasına yazıldı.
3. Test kimlikleri, etiketleri ve grupları mevcut atamalarla doğrulandı.
4. Kaydedilmiş pipeline ile yalnız skor üretildi; `fit` çağrılmadı.
5. Bellekteki ve diskteki modelin değişmediği doğrulandı.

## Sonuç

| Gerçek etiket | Tahmin normal | Tahmin anormal |
|---|---:|---:|
| Normal (100) | 71 doğru normal | 29 yanlış alarm |
| Anormal (99) | 30 kaçırılan | 69 yakalanan |

| Ölçüt | Çapraz doğrulama (eğitim) | Doğrulama (197) | Test (199) |
|---|---:|---:|---:|
| Accuracy | %79.97 | %75.13 | %70.35 |
| Precision | %85.83 | %78.82 | %70.41 |
| Recall | %71.95 | %68.37 | %69.70 |
| F1 | %78.28 | %73.22 | %70.05 |
| Yanlış alarm oranı | %11.96 | %18.18 | %29.00 |
| ROC AUC | 0.848 | 0.820 | 0.765 |

Precision = TP/(TP+FP), recall = TP/(TP+FN), yanlış alarm oranı = FP/(FP+TN).
Çapraz doğrulama sütunu seçimin yapıldığı kat dışı eğitim tahminleridir ve iyimser olabilir.
Pozitif sınıf 1, kaynak verideki anormal etiketidir; doğrulanmış saldırı anlamına gelmez.
Skor kalibre edilmiş saldırı olasılığı değildir.

## Dosyalar

- `selection_before_test.json`: test öncesi sabit model, seçim kaydı ve karar kuralı.
- `test_report.json`: tam metrikler, bütünlük bilgileri ve değerlendirme durumu.
- `test_predictions.jsonl`: 199 isteğin etiketi, tahmini ve skoru.
- `README.md`: bu açıklama.

Proje kökünde çalıştırılan komut (sonuç dizini zaten varsa betik tekrar çalışmaz):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_test_tuned.py rf-tuned-v2
```

## Sınırlar ve güncel durum

Bu küçük, eski, sentetik ve dengeli CSIC pilotudur; gerçek trafik başarımı değildir.
İçerik gruplaması tüm sızıntıları garantiyle engellemez. Metrikler istek başınadır;
aynı grup içindeki kayıtlar bağımsız gözlemler sayılmaz.

Aynı test kümesi daha önce v1 modelleri için açılmıştı; bu yüzden proje açısından hiç
görülmemiş bir küme değildir. Bu modelin ayarları test sonuçlarına bakılarak seçilmedi.
Bu sonuçlara göre model değiştirilecekse aynı küme yeniden hiç görülmemiş final testi
gibi sunulmamalıdır.
