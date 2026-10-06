# İçerik gruplarıyla eğitim / doğrulama / test ayrımı

## Sonuç

| Bölüm | Normal | Anormal | Toplam |
|---|---:|---:|---:|
| Eğitim | 301 | 303 | 604 |
| Doğrulama | 99 | 98 | 197 |
| Test | 100 | 99 | 199 |

1.000 kayıt korunmuştur. 982 tam içerik grubundan yakın benzerlik ve uzun değer tekrarlarını birleştirerek 869 son grup oluşturuldu. En büyük grup 16 kayıt. Etiketler korunmuş, hiçbir örnek silinmemiştir. Henüz model eğitilmemiştir.

## Ne ölçüyoruz?

Bilinen uygulamanın yeni normal/anormal isteklerini ayırma. Aynı endpoint farklı kümelerde bulunabilir. Örneğin registro.jsp: eğitim 121, doğrulama 30, test 37 kayıt. Önceki endpoint grupları yeni sayfaya aktarım testi için ayrı tutulur; bu deneyde kullanılmaz.

## Gruplama

1. Tam içerik: bir kez Latin-1 ile çözülmüş yol ve sıralanmış sorgu/form parametre çiftleri. GET/POST ve sorgu/body yerleşimi gruplama için önemsenmez; tekrarlı parametreler korunur. 18 GET/POST eşdeğer çift aynı grupta kalır. Bu sunucu davranışının birebir eşdeğerliği iddiası değil, muhafazakâr değerlendirme gruplamasıdır.
2. Yakın içerik: aynı yol ve aynı parametre adları çoklu kümesi içinde, JSON olarak temsil edilen değer dizileri karşılaştırılır. En az 40 karakter ve SequenceMatcher benzerliği en az 0,97 gerekir. 148 yakınlık bağlantısı bulundu. Bu oran saldırı olasılığı değildir.
3. Uzun değer tekrarı: 40 veya daha uzun karakterli aynı çözülmüş parametre değeri, farklı sayfalarda da olsa kayıtları aynı gruba bağlar. Etikete bakılmaz; normal değerler de kapsanır.
4. Bağlantılı bileşenler oluşturulur: A-B ve B-C bağlıysa üçü birlikte kalır. Eşik altı iki uç bu nedenle aynı gruba girebilir.

İlk ayrımın tekrar denetiminde uzun değerlerin kümeler arasında kaldığı görüldü; üçüncü kural bu veri kalite bulgusuna dayanarak eklendi. Hiçbir model skoru kullanılmadı. Son politika bu sürümde sabitlendi.

## Bölme

- StratifiedGroupKFold: 5 kat, shuffle=True, seed=42.
- Sınıf ve GET/POST birleşimi dengelenir; grup bölünmez.
- Kat 0 test, kat 1 doğrulama, kalan katlar eğitimdir.
- Önceden ayrıntılı incelenmiş dört örneğin bütün grupları eğitimde sabittir; toplam 5 kayıt.
- Sonuç beğenilmediğinde seed veya test kümesi değiştirilmemelidir.

## Kontroller

- 8 birim testi geçti.
- Özellik ve istek dosyalarının 1.000 kimliği ve etiketi eşleşiyor.
- Kümeler arasında ortak grup ve belirlenen tam içerik grubu yok.
- Seçilen yakınlık tanımına göre kümeler arasında yakın çift yok.
- En az 40 karakterli aynı parametre değeri kümeler arasında paylaşılmıyor.
- Her bölümde iki sınıf ve iki metot var; beş yaygın endpoint her bölümde temsil ediliyor.

Bu kontroller bütün veri sızıntısının bittiği anlamına gelmez. Kısa tekrarlar, farklı kodlanmış saldırılar, parametre adı değişmiş varyasyonlar veya gerçek oturum ilişkileri kaçabilir. Veri eski, sentetik ve dengeli bir alıştırma setidir. Özellikler daha önce genel olarak incelendiğinden test bağımsız dış saha doğrulaması sayılmaz.

## Dosyalar

`data/processed/http-mini-splits-v1/` altında:

- `train_features.jsonl`: eğitim özellikleri ve ayrı etiketler.
- `validation_features.jsonl`: ayar ve eşik seçimi.
- `test_features.jsonl`: son değerlendirme; model seçimi için kullanılmaz.
- `assignments.jsonl`: her sample_id için split ve group_id.
- `near_pairs.jsonl`: yakın içerik çiftleri; inceleme kaydı.
- `split_report.json`: sayılar, yöntem, kaynak SHA-256 değerleri ve sınırlar.

Model girdisi yalnızca her kaydın `features` nesnesidir. `label`, `sample_id`, `group_id`, dosya adları, ayrıştırma durumu ve diğer metadata modele özellik olarak verilmez.

## Yeniden üretme

```bash
cd ~/Documents/ids-model
source .venv/bin/activate
python scripts/split_requests.py \
  --input data/http-mini/requests.jsonl \
  --features data/processed/http-mini-features-v1/features.jsonl \
  --examples data/http-mini/examples.json \
  --output-dir data/processed/http-mini-splits-v1
```

Çıktı dizini mevcutsa üzerine yazılmaz. Tekrar çalıştırmada yeni bir dizin kullanın. Kullanılan ortam: scikit-learn 1.9.1; yeniden üretimde paket sürümlerini koruyun.

```bash
PYTHONPATH=scripts python -m unittest discover -s tests -p test_split_requests.py -v
```

Sonraki adım: eğitim bölümünde sabit özellikleri belirlemek; temel özelliklerle Random Forest eğitmek ve doğrulama bölümünde incelemek. Test en sona saklanır.
