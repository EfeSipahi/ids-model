# HTTP isteklerini gruplama — İlk aşama

## Amaç

Aynı uygulama sayfasına ait farklı isteklerin sonraki eğitim/doğrulama/test ayrımında birlikte kalması. Bu aşamada ayrım veya model eğitimi yapılmadı.

## Karar

Gruplama anahtarı URL yol şablonudur. Yolun yüzde kodlaması bir kez çözülür; `;jsessionid=...` çıkarılır, sayı dizileri `{number}` ile temsil edilir. Harf büyüklüğü, `+`, eğik çizgiler ve nokta segmentleri korunur. Bu normalizasyon sunucu yönlendirmesinin birebir simülasyonu değildir; sayısal farklılıkları aynı grupta tutan bir sezgidir.

GET/POST, parametre adları ve değerleri, header'lar ve etiket gruplama anahtarına girmez. Böylece aynı sayfadaki normal ve saldırılı varyasyonlar farklı kümelere düşmez. Örneğin `/login?user=ali` ve `/login` adresine gönderilen bir POST aynı gruptadır. Bu, yakın metinleri matematiksel olarak kümeleme algoritması değil, açıkça tanımlanmış hedef sayfa gruplamasıdır.

Etiket sadece raporlamada kullanılır. Aynı grupta normal ve anormal kayıt bulunması beklenir; bu kayıtlar silinmez ve etiketleri değiştirilmez.

## Sonuç

- 1.000 kayıt, 53 grup.
- 45 grup tek kayıt içeriyor.
- En büyük grup 196 kayıt.
- 6 grupta iki sınıf da var.
- En büyük beş grupta 937 kayıt var. Etkin çeşitlilik 1.000 bağımsız senaryo kadar yüksek değil.

## Sınırlar

Bu ayrım daha sonra eğitimde görülmeyen hedef sayfalara aktarımı ölçer. Bilinen sayfalardaki yeni istek başarısıyla aynı değerlendirme değildir. Aynı saldırı payload'ı farklı sayfalarda kullanılmışsa farklı gruplarda kalabilir; bütün yakın kopyaların ve veri sızıntısının engellendiği iddia edilmez. Model performansı sadece bu küçük, eski uygulama verisine göre yorumlanmalıdır.

## Çalıştırma

```bash
cd ~/Documents/ids-model
source .venv/bin/activate
python scripts/group_requests.py \
  --input data/http-mini/requests.jsonl \
  --output-dir data/processed/http-mini-groups-v1 \
  --encoding latin-1
```

Çıktı varsa üzerine yazmaz; yeniden çalıştırırken başka çıktı dizini seçin.

```bash
PYTHONPATH=scripts python -m unittest discover -s tests -p test_group_requests.py -v
```

## Çıktılar

- `group_assignments.jsonl`: sample_id ile group_id eşlemesi. Özellik tablosuyla sample_id üzerinden birleştirilir; group_id model girdisi yapılmaz.
- `group_report.json`: grup büyüklükleri, sınıf/metot dağılımları ve örnek kimlikler.

Sonraki aşama: grup bütünlüğünü koruyarak yaklaşık %60/%20/%20 ayrım oluşturmak. Her kümede iki sınıfın da bulunduğu, kimlik ve grup kesişiminin olmadığı kontrol edilecek. Büyük gruplar nedeniyle oranlar tam tutmayabilir.
