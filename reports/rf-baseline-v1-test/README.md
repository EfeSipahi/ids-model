# Sabit Random Forest — final test sonucu

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
| Normal (100) | 72 doğru normal | 28 yanlış alarm |
| Anormal (99) | 36 kaçırılan | 63 yakalanan |

| Ölçüt | Doğrulama (197) | Test (199) |
|---|---:|---:|
| Accuracy | %74.62 | %67.84 |
| Precision | %78.57 | %69.23 |
| Recall | %67.35 | %63.64 |
| F1 | %72.53 | %66.32 |
| Yanlış alarm oranı | %18.18 | %28.00 |

Precision = TP/(TP+FP), recall = TP/(TP+FN), yanlış alarm oranı = FP/(FP+TN).
Pozitif sınıf 1, kaynak verideki anormal etiketidir; doğrulanmış saldırı anlamına gelmez.
Skor kalibre edilmiş saldırı olasılığı değildir.

Bu testte 135/199 doğru tahmin var.
100 normal isteğin 28'ine yanlış alarm verildi;
99 anormal isteğin 36'i kaçırıldı.

## Dosyalar

- `selection_before_test.json`: test öncesi sabit model ve karar kuralı.
- `test_report.json`: tam metrikler, bütünlük bilgileri ve değerlendirme durumu.
- `test_predictions.jsonl`: 199 isteğin etiketi, tahmini ve skoru.
- `README.md`: bu açıklama.

Çalıştırılan komut (sonuç dizini zaten varsa betik tekrar çalışmaz):

```bash
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
