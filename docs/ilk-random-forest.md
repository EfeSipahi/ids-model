# İlk Random Forest: eğitim ve doğrulama

Tarih: 27 Eylül 2026. Deney: `rf-baseline-v1`.

İlk Random Forest yalnız **604 eğitim kaydı** üzerinde eğitildi ve **197 doğrulama kaydı** üzerinde değerlendirildi. **199 kayıtlık test kümesi değerlendirilmedi; test özellik dosyası açılmadı.** Mevcut `content-split-v1` ayrımı ve veri dosyaları değiştirilmedi. Bu model bir başlangıç denemesidir; final model seçimi yapılmadı.

## 1. Eğitimden önce ne doğrulandı?

- Güncel ayrım 604 eğitim, 197 doğrulama, 199 test; atama dosyasında 1.000 benzersiz kimlik ve 869 grup var. Bölümler arasında ortak grup yok. Önceden incelenmiş 5 kayıt eğitimde.
- Ham istek ve ana özellik dosyalarının SHA-256 değerleri mevcut `split_report.json` ile eşleşti.
- Eğitim/doğrulama kimlikleri, etiketleri ve grupları atamalarla eşleşti. Bu 801 kaydın 21 özelliği mevcut çıkarıcıyla Latin-1 kullanılarak yeniden hesaplandı ve birebir eşleşti. Bu kontrol yeni özellik dosyası veya ayrım üretmedi.
- Mevcut 28 birim testi geçti. Yeni eğitim akışının 9 testi de geçti: toplam 37 test.
- Ortam yeniden kurulmadı: Python 3.14.7, scikit-learn 1.9.1, pandas 3.0.6, NumPy 2.5.3, joblib 1.6.0.

Eski endpoint grupları kullanılmadı. `split_report.json` içindeki `model_trained: false`, veri ayrımının oluşturulduğu andaki tarihsel durumdur; dosya korunmuştur. Yeni eğitim durumu `models/rf-baseline-v1/run.json` içinde kayıtlıdır.

## 2. X ve y neden ayrı?

`X`, yalnız her satırın `features` nesnesinden ve çıkarıcıdaki açık sütun listesinden oluşturulur. `y`, yalnız `label` alanıdır: `0 = normal`, `1 = anomalous`. JSON anahtarlarının geliş sırasına güvenilmez; sütun sırası açıkça sabitlenir.

`sample_id`, `content_group`, `group_id`, `parse_status`, kaynak dosya adı ve diğer metadata modele verilmez. Özellikle kaynak adları sınıfı ele verebilir; bunları öğrenmek HTTP içeriğini öğrenmek olmaz. Kimlik ve gruplar yalnız bütünlük denetimi ve hataların hangi kayda ait olduğunu bulmak için kullanılır.

İlk deneme **16 temel + 5 örüntü özelliği** ile başlatıldı. Önceki ayrım raporundaki temel özelliklerle başlama cümlesi bir gelecek önerisiydi; yapılmış eğitim değildi. Bu oturumda ilk 21 özellikli model kuruldu. 16 özellikli model ile karşılaştırma henüz yapılmadığından örüntü özelliklerinin katkısı hakkında sonuç çıkarılmıyor.

## 3. Ön işleme yalnız eğitimde öğrenildi

Kaydedilen `Pipeline` üç adımdan oluşur:

1. **Sayısal/geçerli girdi kontrolü:** `FunctionTransformer(validate=True)`; eksik, NaN ve sonsuz değerleri reddeder. Eğitimde eksik değer olmadığı için doldurma eklenmedi. Gelecekte desteklenmeyen bir body'nin eksik ölçümlerini sıfıra çevirip normal saymak doğru olmaz; bu sürüm böyle bir girdiye hata verir.
2. **Sabit sütun seçimi:** `VarianceThreshold(0)` sadece `X_train` üzerinde öğrenilir. Eğitimde değişmeyen bir sütun, bu veride sınıfları ayırmaya bilgi sağlamaz. `duplicate_param_count`, `control_char_count`, `path_traversal_count` eğitimde hep sıfırdır; çıkarılır. **21 girdiden 18 özellik ormana ulaşır.** Doğrulamada seçici tekrar eğitilmez.
3. **Random Forest:** kalan 18 özellik ve eğitim etiketleriyle öğrenilir.

Ölçeklendirme eklenmedi: karar ağaçları özelliklerdeki eşiklere göre bölünür ve standartlaştırma gerektirmez. Pipeline, öğrenilen aynı dönüşümü doğrulamada ve daha sonraki tahminlerde uygulamayı sağlar. Bu yaklaşım scikit-learn'ün [veri sızıntısını önleme rehberi](https://scikit-learn.org/stable/common_pitfalls.html) ve [karar ağacı açıklaması](https://scikit-learn.org/stable/modules/tree.html) ile uyumludur.

## 4. Başlangıç ayarları neden böyle?

| Ayar | Değer | Gerekçe |
|---|---:|---|
| `n_estimators` | 100 | Birden fazla ağacın sonucunu birleştiren makul bir ilk deneme |
| `max_depth` | 10 | Küçük veri üzerinde ağaçların sınırsız ayrıntı öğrenmesini sınırlamak |
| `min_samples_leaf` | 5 | Bir yaprağın çok az örneğe dayanmasını sınırlamak |
| `random_state` | 42 | Aynı veri ve ortamda denemeyi tekrar edebilmek |
| `n_jobs` | 2 | CPU üzerinde iki iş parçacığıyla çalışmak |

Diğer parametreler kurulu scikit-learn varsayılanlarıdır; tüm değerler `run.json` içinde kayıtlıdır. Bunlar en iyi ayarlar olarak seçilmedi. Parametre taraması, seed seçimi ve eşik ayarı yapılmadı. Parametre anlamları için [RandomForestClassifier belgesi](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html).

Tahmin varsayılan `predict` ile alınır: anormal sınıf skoru **0,5'ten büyükse** sınıf 1, eşitlikte sınıf 0. `predict_proba` çıktısı kalibre edilmiş gerçek saldırı olasılığı değildir. Eğitimde `class_weight` veya yeniden örnekleme kullanılmadı; sınıflar zaten 301/303 ile yaklaşık dengeli.

## 5. Doğrulama sonucu

Pozitif sınıf `1 = anomalous`; aşağıdaki sayılar istek başınadır.

| Gerçek etiket | Tahmin normal | Tahmin anormal |
|---|---:|---:|
| Normal (99) | 81 doğru normal (TN) | 18 yanlış alarm (FP) |
| Anormal (98) | 32 kaçırılan (FN) | 66 yakalanan (TP) |

| Ölçüt | Random Forest | Hep çoğunluk sınıfını söyleyen Dummy |
|---|---:|---:|
| Accuracy | %74,62 | %49,75 |
| Precision | %78,57 | %49,75 |
| Recall | %67,35 | %100,00 |
| F1 | %72,53 | %66,44 |
| Yanlış alarm oranı | %18,18 | %100,00 |

- **Precision:** 84 alarmın 66'sı kaynak etiketine göre doğru: `66 / (66 + 18)`.
- **Recall:** 98 anormal isteğin 66'sı yakalandı: `66 / (66 + 32)`.
- **F1:** precision ve recall'un harmonik ortalaması.
- **Yanlış alarm oranı:** 99 normal isteğin 18'ine alarm verildi: `18 / (18 + 81)`. Payda tüm kayıtlar veya bütün alarmlar değildir.
- **Accuracy:** 197 isteğin 147'si doğru sınıflandı: `(81 + 66) / 197`.

Dummy yalnız eğitim etiketlerinden çoğunluk sınıfını öğrenir. Eğitimde 303 anormal ve 301 normal olduğu için her isteğe anormal der; recall'u %100 olurken bütün normal isteklere de alarm verir. Bu karşılaştırma recall veya accuracy'yi tek başına yorumlamamak için yararlıdır.

## 6. Hatalar bize ne gösteriyor?

Toplam 50 hatalı istek, 49 içerik grubundadır. Bazı istekler aynı grup içinde ilişkili olduğundan 197 doğrulama satırını tamamen bağımsız gözlem saymıyoruz. Aşağıdakiler seçilmiş örneklerdir; hata dağılımını tek başlarına temsil etmezler. Skorlar yüzde saldırı riski olarak okunmamalıdır.

| Doğrulama kaydı | Hata | Skor | Gözlem |
|---|---|---:|---|
| `normalTrafficTraining.txt:25` | Yanlış alarm | 0,935 | GET `/tienda1/miembros/imagenes/zarauz.jpg`; query/body boş, tüm örüntü sayaçları sıfır. Kaynak normal etiketli bu görsel isteği yine de anormal tahmin edildi. |
| `normalTrafficTraining.txt:5872` | Yanlış alarm | 0,906 | Normal etiketli giriş isteğinde 5 parametre ve 2 yüzde kodlaması var; örüntü sayaçları sıfır. POST karşılığı `:5873` aynı grupta ve o da yanlış alarm. |
| `anomalousTrafficTest.txt:8484` | Kaçırılan anormal | 0,133 | `/tienda1/publico/anadir.jsp` formunda `nombreA` var; uzunluk ve karakter istatistikleri normal görünümlü bir forma benziyor. |
| `anomalousTrafficTest.txt:18948` | Kaçırılan anormal | 0,133 | Aynı endpoint'te `B1A` var. Önceki örnekten farklı içerik taşımasına rağmen mevcut 21 özellik vektörü birebir aynı. |

Özellikler parametre adlarının anlamını, beklenen alan şemasını ve uygulamanın iş kurallarını temsil etmiyor. Bu, bazı anlamsal anormalliklerin niçin zor olabileceğine ilişkin bir hipotezdir. Tek tek orman kararlarının nedensel açıklaması veya kesin saldırı türü tanısı değildir. Aynı özellik vektörüne dönüşen farklı içerikleri bu model ayıramaz.

Buradaki `anomalousTrafficTest.txt` ifadesi **orijinal kaynak dosyanın adıdır**. Listelenen bu örneklerin hepsi bizim güncel **doğrulama** bölümündedir; final testten örnek alınmadı. Kimlikler model girdisi değildir.

## 7. Üretilen dosyalar ve tekrar çalıştırma

- `scripts/train_random_forest.py`: sabit ayrımı kontrol eder, train ile eğitir, validation ile değerlendirir. Test dosyasını okumaz.
- `tests/test_train_random_forest.py`: 9 sentetik kontrol testi.
- `notebooks/04_ilk_random_forest.ipynb`: açıklamalarla adım adım aynı deneyi çalıştırır; dosya üzerine yazmaz.
- `models/rf-baseline-v1/pipeline.joblib`: ön işleme ve eğitilmiş orman birlikte. Bu bir aday deney kaydıdır, final testten geçmiş model değildir.
- `models/rf-baseline-v1/run.json`: özellik sırası, sabit sütunlar, eğitim varyansları, kod/veri hash'leri, sürümler, parametreler, karar kuralı ve metrikler.
- `models/rf-baseline-v1/validation_predictions.jsonl`: 197 doğrulama tahmini.
- `models/rf-baseline-v1/validation_errors.jsonl`: 50 hatalı doğrulama tahmini.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv/bin/python -m unittest discover -s tests -v

# Aynı deneyi yeniden üretmek için yeni çıktı dizini verilir:
.venv/bin/python scripts/train_random_forest.py --output-dir models/rf-baseline-v1-repeat
```

Betik var olan çıktı dizinini kabul etmez. Ön işleme ve model tekrar eğitilecekse aynı sabit train/validation dosyaları kullanılır; test açılmaz. Eğitim betiği çalıştırıldı ve kaydedilen model yeniden yüklenerek doğrulama metrikleri doğrulandı. Notebook hazırlandı ve kod hücrelerinin sözdizimi kontrol edildi; ancak oturumun yerel soket kısıtlaması Jupyter çekirdeğinin başlamasını engellediği için notebook hücreleri çalıştırılamadı. Notebook'taki sonuç açıklamaları eğitim betiğinin gerçek çıktısından alınmıştır.

## 8. Henüz yapılmayanlar

16 temel özelliğin tek başına denenmesi, sınırlı model/ayar karşılaştırması, karar eşiği seçimi, olasılık kalibrasyonu, final test ve canlı IDS entegrasyonu yapılmadı. Daha sonraki karşılaştırmalar aynı sabit ayrımda yürütülmeli. Model/özellik/eşik kararı sabitlenince test bir kez final değerlendirme için kullanılmalı.

Bu veri küçük, eski, sentetik ve dengeli bir CSIC pilotudur. İçerik gruplaması tüm olası benzerlikleri yakalamaz; endpoint paylaşımı bilinçlidir. Özellikler daha önce tüm örneklemde genel olarak incelenmiştir. Bu doğrulama sonucu, güncel gerçek trafikteki performans veya bağımsız dış saha doğrulaması değildir. `anomalous` kaynak etiketidir; her kayıt doğrulanmış saldırı olarak sunulmaz.
