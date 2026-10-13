# Sabit lojistik regresyon — final test sonucu

Kaydedilmiş `logreg-baseline-v1` modeli 199 test kaydında değerlendirildi.
Model 604 eğitim kaydında öğrenilmişti; bu işlemde yeniden eğitim yapılmadı.
197 doğrulama kaydı da eğitime eklenmedi. Özellikler, ölçekleme, model ayarları
ve 0,5 karar eşiği değiştirilmedi. Eşitlikte normal sınıf seçilir. Kaynak metadata'sı
model girdisi değildir.

## Nasıl çalıştırıldı?

1. Model, eğitim kodu ve veri hash'leri önceki kayıtla karşılaştırıldı.
2. Model ve karar kuralı test okunmadan `selection_before_test.json` dosyasına yazıldı.
3. Test kimlikleri, etiketleri ve grupları mevcut atamalarla doğrulandı.
4. Sadece `features` alanından X, `label` alanından y oluşturuldu.
5. Kaydedilmiş pipeline ile `predict` çağrıldı; `fit` çağrılmadı.
   Eğitimde öğrenilen aynı 3 sütun çıkarıldı; kalan 18 özellik eğitimde öğrenilen
   ortalama ve sapmayla ölçeklendi.
6. Tahminler gerçek etiketlerle karşılaştırıldı. Bellekteki ve diskteki modelin
   değişmediği doğrulandı. Veriler ve önceki deney kayıtları değiştirilmedi.

## Sonuç

| Gerçek etiket | Tahmin normal | Tahmin anormal |
|---|---:|---:|
| Normal (100) | 61 doğru normal | 39 yanlış alarm |
| Anormal (99) | 34 kaçırılan | 65 yakalanan |

| Ölçüt | Doğrulama (197) | Test (199) |
|---|---:|---:|
| Accuracy | %72.08 | %63.32 |
| Precision | %73.12 | %62.50 |
| Recall | %69.39 | %65.66 |
| F1 | %71.20 | %64.04 |
| Yanlış alarm oranı | %25.25 | %39.00 |
| ROC AUC | 0.801 | 0.709 |

Precision = TP/(TP+FP), recall = TP/(TP+FN), yanlış alarm oranı = FP/(FP+TN).
ROC AUC eşikten bağımsızdır; skorların anormal istekleri normallerin üstüne ne kadar
iyi sıraladığını ölçer (0,5 = rastgele, 1 = kusursuz).
Pozitif sınıf 1, kaynak verideki anormal etiketidir; doğrulanmış saldırı anlamına gelmez.
Skor kalibre edilmiş saldırı olasılığı değildir.

Bu testte 126/199 doğru tahmin var.
100 normal isteğin 39'ine yanlış alarm verildi;
99 anormal isteğin 34'i kaçırıldı.

## Dosyalar

- `selection_before_test.json`: test öncesi sabit model ve karar kuralı.
- `test_report.json`: tam metrikler, bütünlük bilgileri ve değerlendirme durumu.
- `test_predictions.jsonl`: 199 isteğin etiketi, tahmini ve skoru.
- `README.md`: bu açıklama.

Proje kökünde çalıştırılan komut (sonuç dizini zaten varsa betik tekrar çalışmaz):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/evaluate_test_logreg.py
```

## Sınırlar ve güncel durum

Bu küçük, eski, sentetik ve dengeli CSIC pilotudur; gerçek trafik başarımı değildir.
İçerik gruplaması tüm sızıntıları garantiyle engellemez. Metrikler istek başınadır;
aynı grup içindeki kayıtlar bağımsız gözlemler sayılmaz. Özellikler daha önce genel
olarak incelenmiştir. Bu sonuç bağımsız dış saha doğrulaması değildir.

Aynı test kümesi daha önce `rf-baseline-v1` için açılmıştı; bu yüzden proje açısından
hiç görülmemiş bir küme değildir. Lojistik regresyonun ayarları o test sonucuna göre
seçilmedi. Bu sonuçlara göre model değiştirilecekse aynı küme yeniden hiç görülmemiş
final testi gibi sunulmamalıdır.
