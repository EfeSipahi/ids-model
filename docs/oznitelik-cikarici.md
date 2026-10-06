# HTTP öznitelik çıkarıcı

Python standart kütüphanesiyle çalışır; ek paket kurulumu gerektirmez. Model eğitmez.

## Projede çalıştırma

```bash
cd ~/Documents/ids-model
source .venv/bin/activate
python scripts/extract_features.py \
  --input data/http-mini/requests.jsonl \
  --output-dir data/processed/http-mini-features-v1 \
  --encoding latin-1
```

Çıktı varsa üzerine yazmaz. Yeni deneyde farklı bir çıktı dizini seçin.

Testler:

```bash
cd ~/Documents/ids-model
PYTHONPATH=scripts python -m unittest discover -s tests -p test_extract_features.py -v
```

## Çıktı

`features.jsonl` içinde her satır bir istektir:

```json
{"sample_id":"...","content_group":"...","label":0,"features":{"path_length":28},"parse_status":{"body":"parsed"}}
```

Bu kısaltılmış örnektir; gerçek kayıtta 16 temel ve 5 örüntü özelliği bulunur. Yalnızca `features` nesnesi model girdisidir. `label` öğrenilecek cevap; diğer alanlar izlenebilirlik ve veri kalite kontrolü içindir. `feature_report.json`, eksik değerleri, sabit özellikleri ve ayrıştırma durumlarını gösterir.

## Kurallar ve sınırlar

- URL sorguları form kodlama kurallarıyla ayrıştırılır. Form body'si yalnızca Content-Type uygun olduğunda ayrıştırılır.
- `+` form içeriğinde boşluk; `%2B` gerçek artıdır. Yolda `+` korunur. Yüzde kodlaması yalnızca bir kez çözülür.
- Tekrarlanan parametre adları ve boş değerler korunur. Sorgu ve body'deki aynı ad, tek başına tekrar sayılmaz.
- Boş body bilinen sıfırdır. Eksik body, desteklenmeyen tür veya ayrıştırma hatası ilgili özelliklerde `null` üretir. Bu durumlar normal trafik kararı değildir.
- Varsayılan kodlama UTF-8'dir. CSIC örneklerinin `%F3` gibi baytlarını incelemek için bu çalıştırmada açıkça Latin-1 seçildi; bu politika bütün gerçek trafik için geçerli değildir. Form header'ındaki charset varsa body için kullanılır.
- Uzunluklar Python metnindeki karakter sayısıdır; genel durumda ağdaki bayt uzunluğu değildir.
- Kodlama oranı: `3 * geçerli %XX sayısı / (ham sorgu uzunluğu + ham body uzunluğu)`.
- Karakter istatistikleri çözülmüş parametre değerlerinden hesaplanır. Kontrol karakterleri ASCII 0–31 ve 127, rakamlar ASCII 0–9'dur.
- Örüntüler çözülmüş yolda ve değerlerde ayrı ayrı aranır. Parametre adları ve header içerikleri ilk sürümde taranmaz.
- SQL listesi: select, union, insert, update, delete, drop, alter, create, where, from. Sözcük sınırları ve büyük/küçük harf duyarsızlığı kullanılır. SQL yorum işaretleri literal olarak sayılır; gerçek SQL sözdizimi doğrulaması değildir.
- JSON/multipart body desteği ve tam HTTP protokol doğrulaması yoktur. HTML entity çözümü, çok katmanlı URL çözümü veya Unicode normalizasyonu yapılmaz.
- Saldırı örüntüleri kesin saldırı kararları değildir. Sabit kalan özellikler otomatik silinmez; seçim yalnızca eğitim bölümünde yapılmalıdır.
- Model girdileri etiketten bağımsız hesaplanır. Eğitim/test ayrımı, eksik değer doldurma ve model eğitimi yapılmaz.

## Bu veri setindeki kontrol sonucu

- 1.000 kayıt: 500 normal, 500 anormal.
- 16 temel + 5 örüntü özelliği.
- Body: 500 ayrıştırılmış form, 500 boş.
- Eksik özellik değeri yok.
- Bu örneklemde sabit özellikler: duplicate_param_count, control_char_count, path_traversal_count.
- 14 birim testi ve dört örneğin önceki ölçümlerle karşılaştırması başarılı.

Sonraki adım: benzer istekleri gruplandırarak veri ayrımı yapmak; ardından temel özelliklerle ve örüntüler eklenmiş özelliklerle Random Forest deneylerini karşılaştırmak.
