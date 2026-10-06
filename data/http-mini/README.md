# HTTP mini veri seti — İlk Random Forest denemesi

## Amaç

Ham HTTP isteğinden özellik çıkarma, iki sınıflı eğitim ve hata incelemesini öğrenmek. Henüz model eğitilmedi; eğitim/test ayrımı yapılmadı.

## Kaynak ve etiketler

CSIC 2010 veri setinin aşağıdaki aynasından normal ve anormal istekler seçildi:

https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010

Özgün veri setinin katalog kaydı:
https://www.impactcybertrust.org/dataset_view?idDataset=940

- `label=0`: kaynak dosyada normal olarak etiketlenen istek.
- `label=1`: kaynak dosyada anormal olarak etiketlenen istek. Anormal etiketi her örnekte bağımsız doğrulanmış başarılı saldırı anlamına gelmez.
- Kaynak dosya adındaki Training/Test ifadeleri korunmuştur. Bu küçük deney, özgün benchmark ayrımı değildir; anormal test dosyasını gelecekte kendi eğitim/doğrulama/test ayrımımız için kaynak olarak kullanacağız. Özgün CSIC test sonucu iddiasında bulunulmayacak.

Veri sentetik, eski bir web uygulamasından gelir. Günümüz HTTP/API trafiğini veya tüm saldırı türlerini temsil etmez. Kaynak etiketleri bağımsız olarak yeniden doğrulanmamıştır.

## Dosyalar

- `requests.jsonl`: 1.000 HTTP kaydı; her satır bir JSON nesnesi.
- `examples.json`: alanları rahat incelemek için dört örnek.
- `manifest.json`: kaynak adresleri, SHA-256 değerleri, ayrıştırma sayıları ve örnekleme bilgisi.

JSONL seçildi çünkü header listesi ve çok satırlı body, düz bir CSV tablosundan daha açık biçimde korunabilir.

## Dağılım

| Kaynak etiketi | GET | POST | Toplam |
|---|---:|---:|---:|
| Normal | 250 | 250 | 500 |
| Anormal | 250 | 250 | 500 |

Bu dağılım özellikle seçilmiştir. Gerçek trafikteki saldırı oranını temsil etmez; bu veriyle ölçülen precision gerçek ortama doğrudan taşınamaz.

## Alanlar

| Alan | Kullanım |
|---|---|
| `method` | HTTP metodu; özellik kaynağı |
| `request_target` | Yol ve sorgu; özellik kaynağı |
| `original_target` | Özgün istek hedefi; izlenebilirlik |
| `http_version` | HTTP sürümü; özellik adayı |
| `headers` | Ad/değer çiftleri listesi; tekrarları ve sıralamayı korur |
| `body` | Ayrıştırılmış body metni; URL kodlaması çözülmemiştir |
| `label`, `label_name` | Öğrenilecek kaynak etiketi; girdi özelliği değildir |
| `sample_id`, `source_file` | İzlenebilirlik; model girdisi değildir |
| `content_group` | Metot + yol/sorgu + body üzerinden tekrar kontrolü; model girdisi değildir |

Cookie/oturum kimliği, Host değeri, dosya adı ve kayıt kimliği ilk modele doğrudan verilmeyecek. WAF kararı veya yanıt kodu eklenmemiştir.

## Hazırlama ve kontroller

- Sabit rastgele tohum: 42.
- İstek başlangıç satırlarıyla kayıtlar ayrıştırıldı; header yapısı ve varsa Content-Length kontrol edildi.
- Body uzunluğu veya kayıt sınırı belirsiz olan örnekler dışlandı; sayıları manifestte kaydedildi. Bu seçim, bazı bozuk protokol örneklerini dışladığından deney kapsamını daraltır.
- Baytların korunması için Latin-1 eşlemesi kullanıldı; bu, her içeriğin gerçek karakter kodlamasının Latin-1 olduğu iddiası değildir.
- Aynı metot + hedef + body içeren kayıtlardan biri tutuldu. Bu işlem header farklılıklarını birleştirebilir; ilk deney kapsamı bunu dikkate almalıdır.
- Aynı içerik için çelişen etiketli gruplar örneklemden dışlandı.
- Tam içerik tekrarları temizlense de birbirine benzeyen istek varyasyonları kalabilir.

## Eğitimden önce birlikte karar verilecekler

1. Dört örneği okuyup alanları tanımak.
2. URL ve body için içerik türüne uygun çözümleme kurallarını belirlemek.
3. Küçük bir sayısal özellik listesi seçmek: yol/sorgu uzunluğu, parametre sayısı, body uzunluğu, karakter oranları ve seçilmiş header bilgileri gibi.
4. Benzer istek şablonlarını gruplayıp eğitim/doğrulama/test ayrımını yapmak. Rastgele satır ayrımıyla sonuçları abartmamak.
5. Yalnızca eğitim verisinden öğrenen bir veri hazırlama hattı kurmak.
6. Küçük bir Random Forest eğitip recall, precision, yanlış alarm oranı ve confusion matrix incelemek.

OWASP logları bu mini sete karıştırılmadı. Sonraki bağımsız incelemelerde kullanılabilir; normal/zararlı etiketi doğrudan WAF mesajından kesinleştirilmemelidir.
