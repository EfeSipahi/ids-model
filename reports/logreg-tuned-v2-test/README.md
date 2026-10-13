# Sabit `logreg-tuned-v2` — final test sonucu

Kaydedilmiş `logreg-tuned-v2` modeli 199 test kaydında değerlendirildi.
Model 604 eğitim kaydında öğrenilmişti; bu işlemde yeniden eğitim yapılmadı.
197 doğrulama kaydı eğitime ve parametre seçimine eklenmedi.

## Seçilen ayarlar

Parametreler ve karar eşiği yalnız eğitim kümesinde, içerik gruplarına göre bölünmüş
StratifiedGroupKFold çapraz doğrulamasının kat dışı tahminleriyle seçildi
(36 aday denendi). Doğrulama ve test kümeleri seçimde kullanılmadı.

- `C`: `100.0`
- `class_weight`: `None`
- `max_iter`: `5000`
- `l1_ratio`: `1.0`
- `solver`: `liblinear`
- `random_state`: `42`
- karar eşiği: `0.4` (skor bu değerden büyükse anormal; eşitlikte normal)

## Nasıl çalıştırıldı?

1. Model, eğitim kodu ve veri hash'leri eğitim kaydıyla karşılaştırıldı.
2. Model ve karar kuralı test okunmadan `selection_before_test.json` dosyasına yazıldı.
3. Test kimlikleri, etiketleri ve grupları mevcut atamalarla doğrulandı.
4. Kaydedilmiş pipeline ile yalnız skor üretildi; `fit` çağrılmadı.
5. Bellekteki ve diskteki modelin değişmediği doğrulandı.

## Sonuç

| Gerçek etiket | Tahmin normal | Tahmin anormal |
|---|---:|---:|
| Normal (100) | 43 doğru normal | 57 yanlış alarm |
| Anormal (99) | 27 kaçırılan | 72 yakalanan |

| Ölçüt | Çapraz doğrulama (eğitim) | Doğrulama (197) | Test (199) |
|---|---:|---:|---:|
| Accuracy | %72.85 | %70.56 | %57.79 |
| Precision | %70.50 | %67.86 | %55.81 |
| Recall | %78.88 | %77.55 | %72.73 |
| F1 | %74.45 | %72.38 | %63.16 |
| Yanlış alarm oranı | %33.22 | %36.36 | %57.00 |
| ROC AUC | 0.775 | 0.816 | 0.724 |

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
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_test_tuned.py logreg-tuned-v2
```

## Sınırlar ve güncel durum

Bu küçük, eski, sentetik ve dengeli CSIC pilotudur; gerçek trafik başarımı değildir.
İçerik gruplaması tüm sızıntıları garantiyle engellemez. Metrikler istek başınadır;
aynı grup içindeki kayıtlar bağımsız gözlemler sayılmaz.

Aynı test kümesi daha önce v1 modelleri için açılmıştı; bu yüzden proje açısından hiç
görülmemiş bir küme değildir. Bu modelin ayarları test sonuçlarına bakılarak seçilmedi.
Bu sonuçlara göre model değiştirilecekse aynı küme yeniden hiç görülmemiş final testi
gibi sunulmamalıdır.
