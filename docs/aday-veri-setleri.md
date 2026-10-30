# Aday veri setleri

Bu belge, ileride modelde kullanılabilecek HTTP istek veri setlerini bilgi amacıyla toplar.
**Buradaki veri setlerinin hiçbiri henüz hiçbir betikte kullanılmıyor.** Bir veri seti
kullanılmaya başlandığında kendi belgesi `docs/` altına ayrıca yazılmalıdır.

Bilgiler Ekim 2026'da kaynak sayfalardan derlendi. "Doğrulanmadı" diye işaretli maddeler
kullanılmadan önce kontrol edilmelidir. 17 Ekim 2026'daki kontrolde yedi bilgi düzeltildi;
ayrıntılar [veri seti araştırma raporunda](../reports/HTTP%20request%20datasets%20for%20IDS.md).

## Neden yalnızca bu veri setleri?

`scripts/extract_features.py` ham HTTP isteğini okur (yol, sorgu, form body'si). Bu yüzden
yalnızca her kaydı tam bir HTTP isteği olan veri setleri bu projeye uyar. CIC-IDS2017/2018,
UNSW-NB15, NSL-KDD gibi bilinen IDS veri setleri ağ akışı (flow) istatistikleri içerir, istek
içeriği içermez; bu model için uygun değildir.

## Özet

| Veri seti | Boyut | Saldırı türleri | Format | Projeye uyumu |
|---|---|---|---|---|
| CSIC 2010 (tam) | 72.000 normal, 25.065 anormal (toplam 97.065; yaklaşık 35.000'i benzersiz) | SQLi, XSS, CRLF, SSI, buffer overflow, bilgi toplama, parametre kurcalama vb. | Ham HTTP istekleri, 3 dosya | Yüksek: mevcut 1.000 istek bunun alt kümesi |
| ECML/PKDD 2007 | 50.000 istek, ~%20 saldırı | XSS, SQLi, LDAP, XPath, path traversal, komut çalıştırma, SSI | XML | Orta: dönüştürücü gerekir |
| pralab / modsec-learn | ~508 bin normal sorgu dizgisi, ~30 bin SQLi | Yalnız SQLi | Parçalı dosyalar, `merge.py` ile birleşir | Düşük–orta: normal tarafı yalnız sorgu dizgisi |
| SR-BH 2020 | ~908.000 istek | SQLi, XSS ve diğerleri, çoklu etiket | CSV, istek alanlara bölünmüş | Düşük: etiket temizliği şart |

## CSIC 2010 (tam sürüm)

- **Kaynak:** İspanya Ulusal Araştırma Konseyi (CSIC) Bilgi Güvenliği Enstitüsü.
- **İçerik:** İspanyolca bir e-ticaret uygulamasına (sepet, kullanıcı kaydı) yönelik sentetik
  trafik. Saldırılar Paros ve W3AF araçlarıyla üretilmiş.
- **Dosyalar:** Normal trafik (eğitim), normal trafik (test), anormal trafik (test). Özgün
  bölünme anomali tespiti içindir: eğitim dosyasında yalnız normal istek vardır. Bu projede
  denetimli sınıflandırma yapıldığı için kendi ayrımımızı (`scripts/split_requests.py`) kullanırız.
- **Etiket anlamı:** "Anormal" sınıfı yalnız saldırı değildir; gizli/olmayan kaynak istekleri,
  değiştirilmiş argümanlar ve kasıtsız hatalı istekler de bu sınıftadır.
- **Bilinmesi gerekenler:** Bazı makalelerde 223.585 kayıtlı bir "CSIC 2010 v2" geçer; bu,
  resmi sayfadaki sürümle aynı değildir. Hangi sürümün kullanıldığı belgeye yazılmalıdır.
  Latin-1 karakterler içerir (bkz. [özellik çıkarıcı](oznitelik-cikarici.md)).
- **Dosya boyutları:** Normal eğitim ve normal test dosyalarında 36.000'er, anormal test
  dosyasında 25.065 istek vardır; toplam 97.065 isteğin yaklaşık 35.000'i benzersizdir.
- **Edinme:** Resmi sayfa (https://www.tic.itefi.csic.es/dataset/) 17 Ekim 2026'da bağlantıyı
  reddetti. Özgün üç dosya msudol/GSI aynasında:
  https://github.com/msudol/Web-Application-Attack-Datasets/tree/master/OriginalDataSets/csic_2010
  Kullanılan dosyaların özetleri (hash) kaydedilmelidir.
- **Lisans/kullanım koşulları:** Erişilebilen hiçbir birincil kaynakta lisans yok. Aynalarda
  GPL-3.0, MIT gibi birbirini tutmayan etiketler var; lisans belirsiz.

## ECML/PKDD 2007 Discovery Challenge

- **İçerik:** 50.000 bağımsız istek; yaklaşık %20'si saldırı. Saldırıların yaklaşık %10'u
  "bağlam dışı"dır: gerçek saldırıya benzer ama yanlış hedefi (ör. LDAP olmayan sunucuya LDAP
  enjeksiyonu) amaçlar.
- **Etiketler:** Normal, XSS, SQLi, LDAP enjeksiyonu, XPath enjeksiyonu, path traversal,
  komut çalıştırma, SSI. LIRMM sayfası her örnekte tek bir `type` alanı gösteriyor; bir
  isteğin birden çok sınıfa ait olabileceği doğrulanmadı. Saldırının istekteki yeri de
  işaretlidir. İkili sınıflandırmadan çok sınıflıya geçilirse işe yarar.
- **Format:** XML. Her kayıtta bağlam (sunucu işletim sistemi, HTTP sunucusu, SQL/LDAP/XPath
  varlığı), sınıf ve istek (method, protokol, URI, sorgu, header, body) bulunur.
  `data/http-mini/requests.jsonl` biçimine dönüştürücü yazılması gerekir.
- **Edinme:** LIRMM veri bağlantısı 17 Ekim 2026'da HTTP 500 döndürdü. Özgün XML zip
  msudol aynasında: https://github.com/msudol/Web-Application-Attack-Datasets
- **Lisans/kullanım koşulları:** Lisans bulunamadı. Özgün veri kullanıcı adı ve şifreyle
  dağıtılıyordu.

## pralab / modsec-learn

- **Kaynak:** "Boosting ModSecurity with Machine Learning" makalesinin veri seti
  (Cagliari ve Genova üniversiteleri).
- **İçerik:** Normal tarafta open-appsec veri setinden yaklaşık 508 bin sorgu dizgisi. Saldırı
  tarafında HTTP Params, Kaggle ve SQLmap ile üretilmiş, toplam yaklaşık 30 bin SQLi örneği.
- **Format:** `legitimate/` ve `malicious/` klasörleri; dosyalar GitHub sınırı yüzünden
  parçalanmış, her klasördeki `merge.py` ile birleştirilir. Dosya formatı doğrulanmadı.
- **Bilinmesi gerekenler:** Saldırı tarafı **yalnızca SQLi**'dır; genel "anormal" sınıfını
  temsil etmez. Normal taraf tam HTTP isteği değildir, yalnız URL kodlu sorgu dizgileridir
  (ör. `v=1645527473`). Tam normal istekler open-appsec'in `legitimate.zip` dosyasındadır.
- **Edinme:** `git clone https://github.com/pralab/modsec-learn-dataset data/raw/modsec-learn-dataset` (~460 MB)
- **Lisans/kullanım koşulları:** Repoda lisans dosyası yok.

## SR-BH 2020

- **İçerik:** Yaklaşık 908 bin HTTP isteği; CAPEC saldırı kategorilerine göre çoklu etiketli.
- **Format:** CSV; `full_http_request` adında bir sütun yoktur. İstek alanlara bölünmüştür ve
  seçilmiş 11 başlık ayrı sütunlardadır.
- **Bilinmesi gerekenler:** Sonradan yapılan bir incelemede "benign" etiketli satırların önemli
  bir kısmının zararlı içerik taşıdığı bulunmuştur. X-WAD projesi yeniden etiketlenen 126.003
  satırın indekslerini yayınlar (Apache-2.0). Normal trafik büyük ölçüde WordPress/PHP
  ağırlıklıdır. **Etiketler temizlenmeden kullanılmamalıdır.**
- **Edinme:** Harvard Dataverse: https://doi.org/10.7910/DVN/OGOIXX
- **Lisans/kullanım koşulları:** CC0.

## Kullanmadan önce bilinmesi gerekenler

1. **Kaynak sızıntısı (en önemli risk).** Normal istekler bir veri setinden, saldırılar başka
   bir veri setinden alınırsa model saldırıyı değil, veri setini ayırt etmeyi öğrenir (ör. host
   adı, URL yapısı, dil). Sonuç yüksek çıkar ama anlamsızdır. Her veri setinde iki sınıf aynı
   kaynaktan gelmeli ya da kaynak farkı ayrıca test edilmelidir.
2. **Etiket anlamları farklıdır.** CSIC'te "anormal", ECML/PKDD'de "saldırı", SR-BH'de CAPEC
   kategorisi aynı şey değildir. Veri setleri birleştirilecekse ortak etiket tanımı önceden yazılmalıdır.
3. **Çapraz test.** Bir veri setinde eğitip diğerinde test etmek, modelin genelleyip
   genellemediğini gösterir. Tek veri setindeki sonuç gerçek trafik başarımı değildir.
4. **Tekrar ve yakın kopyalar.** Sentetik veri setlerinde neredeyse aynı istekler çoktur.
   Mevcut içerik gruplaması (`docs/http-veri-ayrimi.md`) yeni veriye de uygulanmalıdır.
5. **Test seti bir kez kullanılır.** Mevcut deney kuralı yeni veri setleri için de geçerlidir.
6. **Büyük veri repoya girmez.** İndirilen özgün veriler `data/raw/` altına konur, dönüşüm
   sonuçları `data/processed/` altına ayrı klasörlere yazılır.
7. **Kendi loglarımız kişisel veri içerebilir.** IP adresi, oturum çerezi, kullanıcı adı, form
   içerikleri gibi alanlar KVKK kapsamına girebilir. Anonimleştirme ve paylaşım kuralları
   kullanılmadan önce netleştirilmelidir.
8. **Lisanslar.** SR-BH 2020 CC0; open-appsec normal veri seti Apache-2.0; ModSec-WP ve 30 günlük
   ModSecurity logları CC-BY-4.0; HttpParams MIT. CSIC 2010, ECML/PKDD 2007, modsec-learn ve
   ATRDF'nin lisansı yok. Lisanssız verilerde akademik dışı kullanım veya yeniden dağıtım (ör.
   `data/http-mini/` gibi bir alt kümeyi repoya koymak) belirsizdir.

## Kaynaklar

- CSIC 2010: https://www.tic.itefi.csic.es/dataset/ (17 Ekim 2026'da erişilemedi)
- CSIC 2010 ve ECML/PKDD 2007 aynası: https://github.com/msudol/Web-Application-Attack-Datasets
- CSIC 2010 v2 kullanan çalışma: https://arxiv.org/abs/2412.16791
- ECML/PKDD 2007: https://www.lirmm.fr/pkdd2007-challenge/ ve https://hal-lirmm.ccsd.cnrs.fr/lirmm-00168955
- modsec-learn makalesi: https://arxiv.org/abs/2406.13547
- modsec-learn verisi: https://github.com/pralab/modsec-learn-dataset
- SR-BH 2020: https://portalcientifico.uah.es/documentos/668fc479b9e7c03b01bde810
- SR-BH 2020 verisi (Harvard Dataverse): https://doi.org/10.7910/DVN/OGOIXX
- SR-BH 2020 hatalı etiket indeksleri (X-WAD): https://github.com/mattebit/x-wad/tree/main/experiments/srbh2020
- SR-BH 2020 etiket incelemesi (CyShield; 17 Ekim 2026'da 404 döndürdü): https://seclab.cyshield.com/posts/augmenting-sr-bh-2020-a-technical-methodology-for-modern-threat-simulation/
