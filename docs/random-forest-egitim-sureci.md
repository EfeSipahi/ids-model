# HTTP IDS projemizde veriyi nasıl hazırladık ve Random Forest'ı nasıl eğittik?

**Rapor tarihi:** 29 Eylül 2026  
**Proje:** ids-model  
**İncelenen model:** rf-baseline-v1  
**Amaç:** Yapılmış işlemleri, makine öğrenmesine yeni başlayan biri için nedenleriyle açıklamak.

Bu rapor mevcut eğitim kodu, kaydedilmiş model ve deney sonuçları incelenerek hazırlanmıştır. Yeni bir model eğitilmemiştir. Aşağıdaki gerçek ağaç örneği de daha önce kaydedilmiş modelden okunmuştur.

## 1. Biz hangi problemi çözmeye çalışıyoruz?

Bir HTTP isteği geldiğinde onu **normal** veya **anormal** olarak sınıflandırmak istiyoruz. Bunun için önceden etiketlenmiş örneklerden öğrenen bir yöntem kullandık.

- **Örnek/kayıt:** Bir HTTP isteği.
- **Özellik:** İstekten ölçtüğümüz sayı; örneğin yol uzunluğu.
- **Etiket:** Veri kaynağının o isteğe verdiği doğru cevap kabul edilen sınıf.
- **Model:** Özelliklerden sınıf tahmin etmek için eğitim sırasında oluşturulan karar yapısı.

Etiketlerimiz `0 = normal`, `1 = anomalous/anormal`. Kaynaktaki “anormal” etiketi, her kaydın doğrulanmış bir saldırı olduğu anlamına gelmez.

Veriyi değiştirmek yerine **veriyi kullanarak modeli eğittik**. Öğrenen şey veri dosyası değil, Random Forest'ın karar ağaçlarıdır. Bu yaklaşım, eğitim örneklerinin cevapları belli olduğu için **denetimli öğrenme** olarak adlandırılır.

## 2. Eğitimden önce elimizde ne vardı?

CSIC 2010 verisinden seçilmiş 1.000 HTTP isteği vardı. Örneklem 500 normal ve 500 anormal istekten oluşuyordu; her sınıfta 250 GET ve 250 POST bulunuyordu.

Ham kayıtların yolu:

```text
data/http-mini/requests.jsonl
```

JSONL dosyasında her satır bir kaydı temsil eder. HTTP metodu, yol, header'lar ve body gibi bilgiler ham kayıtta saklanır. Random Forest'a bu metnin tamamını doğrudan vermedik.

Önce `scripts/extract_features.py` ile her istekten **16 temel + 5 örüntü özelliği** çıkardık. Özellik çıkarmak ile model eğitmek farklı işlemlerdir: özellik çıkarıcı bizim yazdığımız sayma/ayrıştırma kurallarını uygular; Random Forest ise bu sayıların etiketlerle ilişkisini öğrenir.

| Özellik grubu | Örnekler | Modele hangi bilgiyi taşıyor? |
|---|---|---|
| Uzunluk | Yol, query, body, en uzun/ortalama parametre değeri | İsteğin parçaları ne kadar uzun? |
| Parametre yapısı | Query/body parametre sayısı, tekrar eden ad sayısı | Kaç parametre var, tekrar var mı? |
| Kodlama | Yüzde kodlaması sayısı ve oranı | İçerik ne kadar URL kodlaması kullanıyor? |
| Karakter ölçümleri | Tırnak, açı parantezi, noktalı virgül, kontrol karakteri; rakam ve boşluk oranı | Değerlerin karakter yapısı nasıl? |
| Beş örüntü özelliği | SQL sözcükleri, SQL yorum işaretleri, path traversal, script ve SSI işaretleri | Tanımladığımız belirli işaretler var mı? |

CSIC kayıtları için Latin-1 kullanıldı; uygun query/form parametrelerinde yüzde kodlaması bir kez çözüldü. Bir örüntünün bulunması tek başına saldırı kararı değildir.

Örneğin model isteğin tam yolunu metin olarak görmez; `path_length` ile onun uzunluğunu görür. Parametre adlarının uygulama açısından doğru olup olmadığını da doğrudan bilmez. Bu nedenle özellik çıkarımı, modelin görebileceği bilgiyi sınırlar.

## 3. Neden üç ayrı veri bölümü oluşturduk?

| Bölüm | Normal | Anormal | Toplam | Gerçekte yaptığımız |
|---|---:|---:|---:|---|
| Eğitim | 301 | 303 | **604** | Ön işlemeyi ve Random Forest'ı öğrendik |
| Doğrulama | 99 | 98 | **197** | İlk modelin tahminlerini değerlendirdik |
| Test | 100 | 99 | **199** | Modeli değiştirmeden son değerlendirmeyi yaptık |

Güncel ayrım `content-split-v1` politikasına dayanır. Aynı veya tanımlanan kurallara göre çok benzer içerikleri aynı grupta tuttuk. Böylece modelin eğitimde gördüğü içeriğin çok yakın kopyalarıyla değerlendirilmesi riskini azaltmayı amaçladık.

Aynı endpoint farklı bölümlerde bulunabilir. Önceki endpoint gruplaması bu deneyde kullanılmadı. Beş katlı gruplu/tabakalı ayrımda seed 42 kullanıldı; önceden ayrıntılı incelenen örneklerin grupları eğitimde tutuldu. Sonuç beğenilmediği için ayrım değiştirilmedi.

Bu üç bölümün farkı modelin tahmin yönteminde değildir. **Eğitim öğrenmeye, doğrulama geliştirme kararlarına, test ise seçimler tamamlandıktan sonraki ölçüme ayrılır.** Biz bu ilk modelde doğrulama sonucuna göre parametre taraması da yapmadık.

İlgili veri dizini:

```text
data/processed/http-mini-splits-v1/
```

## 4. X ve y nasıl oluşturuldu?

Eğitim kodundaki `rows_to_xy()` fonksiyonu her kaydın yalnız `features` nesnesini X'e, `label` değerini y'ye alır.

```python
X_train, y_train = rows_to_xy(rows["train"])
```

- **X_train:** 604 satır × 21 sütun. Her satır bir istek, her sütun bir özellik.
- **y_train:** Aynı sıradaki 604 doğru etiket.

Sadece biçimi göstermek için uydurulmuş küçük bir örnek:

| Kayıt | Yol uzunluğu | Query parametre sayısı | Noktalı virgül sayısı | … | Etiket |
|---|---:|---:|---:|---|---:|
| Örnek A | 28 | 5 | 0 | … | 0 |
| Örnek B | 31 | 4 | 2 | … | 1 |

Bu tablodaki özellik sütunları X'e, en sondaki etiket y'ye gider. Bu iki satır gerçek eğitim kayıtlarından alıntı değildir; tablo düzenini açıklamak içindir.

**Etiket X'e eklenmez.** Cevabı modelin girdisine koysaydık, model yeni isteği ayırmayı öğrenmek yerine cevabı girdiden okuyabilirdi.

`sample_id`, `group_id`, `content_group`, `parse_status` ve kaynak dosya adı da X'e alınmadı. Bunlar kayıtları takip etmek ve bütünlüğü kontrol etmek içindir. Örneğin kaynak dosya adında “normal” veya “anomalous” yazması, model için haksız bir cevap ipucu olurdu.

Özellik sırası açık bir listeyle sabitlendi. Böylece eğitimde “yol uzunluğu” olarak kullanılan sütunun tahminde yanlışlıkla başka bir ölçüme dönüşmesi önlendi.

## 5. Ön işleme ne yaptı?

Ön işleme, özellikleri modelin kullanacağı hale getiren adımdır. Biz bunu modelle birlikte bir **Pipeline**, yani sıralı işlem zinciri içinde kurduk:

```text
21 özellik
    ↓
Geçerli sayısal değer ve sütun kontrolü
    ↓
Eğitimde sabit çıkan üç sütunun çıkarılması
    ↓
18 özellik
    ↓
Random Forest
```

Eğitim verisinde eksik değer yoktu. Bu yüzden ortalama/medyan ile doldurma eklemedik. Eksik, NaN veya sonsuz değer gelirse bu ilk sürüm hata verir.

`VarianceThreshold(0)`, yalnız eğitim verisine bakarak şu üç sütunun hep sıfır olduğunu belirledi:

| Çıkarılan sütun | Eğitimdeki değer |
|---|---:|
| duplicate_param_count | Hep 0 |
| control_char_count | Hep 0 |
| path_traversal_count | Hep 0 |

Bir sütun bütün eğitim örneklerinde aynıysa, bu örnekler arasında ayrım yapmaya yardım etmez. Böylece ormana **604 × 18** boyutunda tablo ulaştı.

Doğrulama ve test için “hangi sütunlar sabit?” sorusunu yeniden öğrenmedik; eğitimde seçilmiş aynı sütunları çıkardık. Öğrenilen ön işlemenin yalnız eğitim verisine dayanması, değerlendirme bilgisinin eğitime karışmasını önler. [scikit-learn: veri sızıntısı ve ön işleme](https://scikit-learn.org/stable/common_pitfalls.html)

Özellikleri standartlaştırmadık. Bu karar ağacı tabanlı modelde böyle bir ölçeklendirme zorunlu değildi.

## 6. Random Forest'ı hangi ayarlarla kurduk?

Koddaki gerçek başlangıç ayarlarımız:

```python
RF_PARAMS = dict(
    n_estimators=100,
    max_depth=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=2,
)
```

| Ayar | Anlamı | Bizim tercihimizin amacı |
|---|---|---|
| n_estimators=100 | 100 karar ağacı oluştur | Birçok ağacın tahminini birleştirmek |
| max_depth=10 | Ağaç derinliği en fazla 10 olabilir | Çok ayrıntılı bölünmeleri sınırlamak |
| min_samples_leaf=5 | Bir son yaprakta en az 5 eğitim örneği bulunmalı | Çok az örneğe dayanan kuralları sınırlamak |
| random_state=42 | Rastgele seçimlerin başlangıç değeri | Aynı ortamda denemeyi tekrarlayabilmek |
| n_jobs=2 | İki paralel işçi kullan | CPU işini paralel yürütmek |

Bunlar eğitimden önce verdiğimiz **ayarlar**, yani hiperparametrelerdir. Modelin kendi öğrendiği eşiklerle aynı şey değildir. Seed 42 özel bir başarı sayısı değildir; n_jobs=2 de iki ağaç anlamına gelmez.

Kayıtlı diğer ayarlardan önemli olanlar: `bootstrap=True`, `max_samples=None`, `max_features="sqrt"`, `criterion="gini"`, `class_weight=None`, `oob_score=False`.

Bu ayarlar “en iyisini bulduk” sonucu değildir. İlk deneme için seçildi; otomatik parametre araması yapılmadı. Parametrelerin resmi tanımları: [RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html).

## 7. fit() çağrısı sırasında içeride ne oldu?

Eğitimi başlatan gerçek satır:

```python
pipeline = make_pipeline().fit(X_train, y_train)
```

`make_pipeline()` önce henüz öğrenmemiş bir işlem zinciri oluşturur. `fit()` ise girdi kontrolünü yapar, sabit sütun seçicisini eğitimde öğrenir ve ardından Random Forest'ı eğitir.

### 7.1. Her ağaç için eğitim örnekleri seçildi

Bootstrap açık olduğu için, her ağaç 604 eğitim kaydından **yerine koyarak 604 çekiliş** yaptı. Bir kayıt birkaç kez seçilebilir; bazı kayıtlar o ağacın örnekleminde hiç bulunmayabilir.

Kaydedilmiş modelimizde **ilk ağacın 604 çekilişi 385 farklı eğitim kaydından oluşmuş**. Bu sayı modelin içinden okundu. Diğer ağaçların seçtiği örnekler farklı olabilir.

Dolayısıyla 100 ağaç, 100 farklı dış veri kümesiyle eğitilmedi. Hepsi bizim aynı 604 kayıtlık eğitim bölümünden oluşturulan örneklemleri kullandı.

### 7.2. Ağaç, ayırıcı sorular öğrendi

Ağaç, “şu özellik şu eşikten küçük veya eşit mi?” biçiminde bölünmeler oluşturdu. Biz eşikleri tek tek yazmadık.

Her bölünmede rastgele özellik adayları seçildi. Modelimizin 18 girdisi ve `max_features="sqrt"` ayarı için başlangıç aday sayısı **4**. Adaylar her bölünmede yeniden seçilir; bir ağacın bütün ömrü boyunca yalnız aynı dört özelliğe bağlı kalması gerekmez. Geçerli bir bölünme bulmak için uygulama bazı durumlarda daha fazla özelliği inceleyebilir.

Algoritma, o düğümdeki normal ve anormal örnekleri daha iyi ayıran özellik/eşik çiftini seçer. Bu seçimde kullandığı Gini ölçüsü sınıfların ne kadar karışık olduğunu gösterir.

Sadece fikri anlatan küçük hesap: normal/anormal oranı yarı yarıya ise Gini 0,5'tir; bütün örnekler tek sınıftaysa 0'dır. Algoritma, oluşan iki grubun büyüklüklerini de dikkate alarak karışıklığı azaltan bölünmeleri arar. Bu işlem bütün ağacın mümkün olan en iyi halini baştan hesaplayan bir arama değildir; bulunduğu düğümde seçim yapıp ilerler.

### 7.3. Bizim ilk ağacımız gerçekten hangi soruyu öğrendi?

Kaydedilmiş ormanın **birinci ağacının ilk iki seviyesi**:

```text
semicolon_count <= 0.5 ?
│
├─ Evet: noktalı virgül yok
│       ↓
│   percent_encoding_count <= 6.5 ?
│       ├─ Evet → sonraki dallara devam
│       └─ Hayır → sonraki dallara devam
│
└─ Hayır: en az bir noktalı virgül var
        ↓
    Bu ağacın anormal örneklerden oluşan bir yaprağı
```

Sayaç tamsayı olduğu için 0,5 eşiği “0 mı, en az 1 mi?” ayrımını yapıyor. Benzer şekilde 6,5, “en fazla 6 mı, en az 7 mi?” ayrımıdır.

İlk ağacın bu sağ yaprağında 15 farklı eğitim kaydı var; bootstrap tekrarlarıyla toplam ağırlık 23. Bu yapraktaki örneklerin tamamı anormal etiketli. Bu nedenle **bu ağaç** buraya gelen isteğe anormal sınıf skoru 1 verir.

Bu, noktalı virgül içeren her HTTP isteğinin gerçekten saldırı olduğu veya bütün ormanın mutlaka alarm vereceği anlamına gelmez. Bir ağacın eğitim örneklerinden çıkardığı yerel kuraldır.

İlk ağaç toplam **45 yapraklı ve 10 derinlikli**. Ormanın tamamı **100 ağaçtan** oluşuyor; kayıtlı ağaçların gerçek derinlikleri 9 ile 10 arasında. Bu bilgiler eğitim tekrarlanmadan, model dosyasından okunmuştur.

### 7.4. Ağaç büyümesi sınırlara ulaşınca durdu

Bir dal yeterince ayrıştığında veya büyüme koşulları artık sağlanmadığında yaprak oluşur. Maksimum derinlik 10, her ağacın mutlaka 10 derinliğe ulaşacağı anlamına gelmez.

Random Forest'ta sonraki ağaç önceki ağacın hatalarını sırayla düzeltmek zorunda değildir; ağaçlar ayrı örneklemlerle oluşturulur. Bu deneyde sinir ağı eğitimi veya epoch döngüsü kullanılmadı. Ormanın genel çalışma biçimi: [scikit-learn Random Forest açıklaması](https://scikit-learn.org/stable/modules/ensemble.html#forest).

## 8. Eğitilmiş orman bir isteğe nasıl cevap veriyor?

Yeni isteğin 21 özelliği aynı sırada hazırlanır. Pipeline aynı üç sütunu çıkarır. Kalan 18 değer her ağacın sorularını izleyerek bir yaprağa ulaşır.

Her ağaç ulaşılan yapraktaki eğitim sınıf dağılımından bir sınıf skoru verir. **Kullandığımız scikit-learn uygulaması bu skorları 100 ağaç boyunca ortalar.** Bu nedenle açıklamayı yalnız “100 ağaç evet/hayır oyluyor” diye düşünmek tam değildir.

Sadece mantığı göstermek için üç ağaçlı bir örnek düşünelim: anormal skorları 0,2; 0,6; 0,9 olsun. Ortalama yaklaşık 0,567 olur. Bizim gerçek modelimizde bu ortalama 100 ağaç için alınır.

Karar kuralımız:

```text
Anormal sınıf skoru > 0.5  → anormal
Anormal sınıf skoru <= 0.5 → normal
```

İki sınıf eşit skora sahipse sınıf 0 seçilir. Bu eşiği doğrulama veya test sonucuna göre değiştirmedik. Skor, gerçek trafikte kalibre edilmiş saldırı olasılığı değildir.

## 9. Eğitimi, tahmini ve değerlendirmeyi ayırmak

| İşlem | Kod | Ne yapar? | Model öğrenir mi? |
|---|---|---|---|
| Eğitim | pipeline.fit(X_train, y_train) | Ön işlemi ve ağaçların kararlarını oluşturur | **Evet** |
| Tahmin | pipeline.predict(X_validation) | Öğrenilmiş kararları yeni özelliklere uygular | **Hayır** |
| Değerlendirme | binary_metrics(y_validation, predicted) | Tahminleri doğru etiketlerle karşılaştırır | **Hayır** |
| Kayıt | joblib.dump(pipeline, dosya) | Öğrenilmiş yapıyı diske yazar | **Hayır** |
| Yükleme | joblib.load(dosya) | Kaydedilmiş yapıyı belleğe alır | **Hayır** |

Doğrulamada 32 anormal kaydın kaçırıldığını ölçmemiz, modele otomatik olarak “bunları düzelt” komutu vermedi. Aynı şekilde testte ölçtüğümüz hatalar da ağaçları değiştirmedi.

Doğrulama sonucuna göre ayar değiştirmek isteseydik yeni ayarlarla yeniden eğitim yapmamız gerekirdi. Bu modelde böyle bir ayar araması yapılmadı. Testten önce eğitim ve doğrulamayı birleştirip 801 kayıtla yeniden eğitim de yapılmadı.

Ayrıca basit karşılaştırma için `DummyClassifier(strategy="most_frequent")` eğitimde çoğunluk sınıfını öğrendi. Bu yardımcı model her isteğe anormal diyordu. Kaydettiğimiz `pipeline.joblib` ise Random Forest zinciridir.

## 10. Model dosyası tam olarak ne saklıyor?

```text
models/rf-baseline-v1/pipeline.joblib
```

Bu ikili dosya, Python'daki eğitilmiş Pipeline nesnesinin kaydıdır. Girdi denetimini, sütun seçicisini ve 100 ağacı birlikte saklar. Ağaçların hangi özelliği hangi eşikte böldüğü, dalların bağlantıları ve yaprakların sınıf dağılımları gibi öğrenilmiş bilgiler içerir.

HTTP ham kayıtlarının kopyası veya okunabilir bir Python betiği değildir. Modeli tekrar kullanmak için eğitim sürecini tekrarlamamız gerekmez:

```python
model = joblib.load(model_dosyasi)
tahmin = model.predict(X_yeni)
```

Buradaki `X_yeni`, aynı özellik çıkarımıyla hazırlanmış ve aynı 21 sütun sırasını taşıyan tablodur. HTTP metnini doğrudan `predict()` içine koyamayız. **Özellik çıkarıcı model dosyasının içinde değildir; pipeline sayısal özelliklerden başlar.**

Kodlama politikası, özellik sırası, paket sürümleri, parametreler ve dosya hash'leri ayrıca `models/rf-baseline-v1/run.json` içinde tutulur.

## 11. Yapılan eğitimin sonucu ne oldu?

| Ölçüt | Doğrulama: 197 kayıt | Test: 199 kayıt |
|---|---:|---:|
| Accuracy | %74,62 | %67,84 |
| Precision | %78,57 | %69,23 |
| Recall | %67,35 | %63,64 |
| F1 | %72,53 | %66,32 |
| Yanlış alarm oranı | %18,18 | %28,00 |

Doğrulamada 99 normal isteğin 18'ine yanlış alarm verildi; 98 anormal isteğin 32'si kaçırıldı. Testte 100 normal isteğin 28'ine yanlış alarm verildi; 99 anormal isteğin 36'sı kaçırıldı.

Accuracy bütün doğru tahminlerin oranıdır. Precision verilen alarmların ne kadarının anormal etiketli olduğunu, recall anormal etiketli örneklerin ne kadarının bulunduğunu gösterir. F1 precision ve recall'u birlikte özetler. Yanlış alarm oranının paydası bütün kayıtlar değil, **gerçekte normal olan kayıtların sayısıdır**.

Bu sonuçlar ilk modelin ölçümüdür. Hataların tek nedeninin ağaç ayarları olduğu sonucuna varamayız; özelliklerin taşıdığı bilgi ve eğitim örneklerinin çeşitliliği de etkilidir.

Test **27 Eylül 2026'da çalıştırılmıştır**. Eğitim anında yazılan `run.json` içindeki `test_evaluated: false` tarihsel bilgidir. Güncel test durumu `reports/rf-baseline-v1-test/test_report.json` içinde yer alır.

Veri küçük, eski, sentetik ve dengeli bir pilottur. Özellikler daha önce tüm örneklemde genel olarak incelenmiştir; içerik gruplaması her tür sızıntıyı garantiyle engellemez. Sonuçlar gerçek trafik başarımı veya bağımsız dış saha doğrulaması olarak sunulmaz. Test artık görüldüğü için, onu kullanarak yapılacak geliştirmelerden sonra aynı test yeniden hiç görülmemiş gibi gösterilmemelidir.

## 12. Projede hangi dosya hangi işi yapıyor?

Aşağıdaki yollar proje köküne göredir.

| Dosya | Görevi |
|---|---|
| scripts/extract_features.py | HTTP isteklerinden 21 sayısal özellik çıkarır |
| scripts/split_requests.py | İçerik gruplarını ve sabit veri ayrımını oluşturur |
| scripts/train_random_forest.py | Eğitimde ön işleme + RF öğrenir; doğrulamayı ölçer ve modeli kaydeder |
| scripts/evaluate_test.py | Kaydedilmiş modeli değişmeden testte değerlendirir |
| models/rf-baseline-v1/pipeline.joblib | Eğitilmiş ön işleme ve orman |
| models/rf-baseline-v1/run.json | Eğitim anındaki ayarlar ve doğrulama sonuçları |
| reports/rf-baseline-v1-test/test_report.json | Sonradan yapılan testin gerçek sonuçları |
| notebooks/04_ilk_random_forest.ipynb | Aynı eğitim adımlarını açıklayan hazırlanmış notebook |

Notebook hazırlanmış ve kod hücrelerinin sözdizimi kontrol edilmiştir; bu oturum zincirinde Jupyter çekirdeği yerel soket kısıtlaması nedeniyle çalıştırılamamıştır. Gerçek eğitim ve test sonuçları Python betiklerinden alınmıştır.

Kod okumaya `train_random_forest.py` içindeki şu üç noktadan başlanabilir: `rows_to_xy()` modelin ne gördüğünü, `make_pipeline()` işlem sırasını, `pipeline = make_pipeline().fit(X_train, y_train)` ise öğrenmenin başlatıldığı yeri gösterir.

**Kontrol sorusu:** “Yeni bir isteği tahmin ederken doğru etiketi modele vermem gerekir mi?” Hayır. Özellikleri veririz; model öğrendiği yapıyla cevap üretir. Doğru etiket yalnız bu cevabın ne kadar başarılı olduğunu sonradan ölçebilmemiz için gerekir.

