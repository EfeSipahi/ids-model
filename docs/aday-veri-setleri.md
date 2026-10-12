# Aday veri setleri

Bu belge, ileride modelde kullanılabilecek HTTP istek veri setlerini bilgi amacıyla toplar.
**Buradaki veri setlerinin hiçbiri henüz hiçbir betikte kullanılmıyor.** Bir veri seti
kullanılmaya başlandığında kendi belgesi `docs/` altına ayrıca yazılmalıdır.

Bilgiler Ekim 2026'da kaynak sayfalardan derlendi. "Doğrulanmadı" diye işaretli maddeler
kullanılmadan önce kontrol edilmelidir.

## Neden yalnızca bu veri setleri?

`scripts/extract_features.py` ham HTTP isteğini okur (yol, sorgu, form body'si). Bu yüzden
yalnızca her kaydı tam bir HTTP isteği olan veri setleri bu projeye uyar. CIC-IDS2017/2018,
UNSW-NB15, NSL-KDD gibi bilinen IDS veri setleri ağ akışı (flow) istatistikleri içerir, istek
içeriği içermez; bu model için uygun değildir.

## Özet

| Veri seti | Boyut | Saldırı türleri | Format | Projeye uyumu |
|---|---|---|---|---|
| CSIC 2010 (tam) | ~36.000 normal, 25.000+ anormal | SQLi, XSS, CRLF, SSI, buffer overflow, bilgi toplama, parametre kurcalama vb. | Ham HTTP istekleri, 3 dosya | Yüksek: mevcut 1.000 istek bunun alt kümesi |
| ECML/PKDD 2007 | 50.000 istek, ~%20 saldırı | XSS, SQLi, LDAP, XPath, path traversal, komut çalıştırma, SSI | XML | Orta: dönüştürücü gerekir |
| pralab / modsec-learn | ~508 bin normal, ~30 bin SQLi | Yalnız SQLi | Parçalı dosyalar, `merge.py` ile birleşir | Orta: normal trafik için değerli |
| SR-BH 2020 | ~908.000 istek | SQLi, XSS ve diğerleri, çoklu etiket | CSV, ham istek tek sütunda | Düşük: etiket temizliği şart |

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
- **Edinme:** https://www.tic.itefi.csic.es/dataset/
- **Lisans/kullanım koşulları:** Doğrulanmadı.

## ECML/PKDD 2007 Discovery Challenge

- **İçerik:** 50.000 bağımsız istek; yaklaşık %20'si saldırı. Saldırıların yaklaşık %10'u
  "bağlam dışı"dır: gerçek saldırıya benzer ama yanlış hedefi (ör. LDAP olmayan sunucuya LDAP
  enjeksiyonu) amaçlar.
- **Etiketler:** Normal, XSS, SQLi, LDAP enjeksiyonu, XPath enjeksiyonu, path traversal,
  komut çalıştırma, SSI. Bir istek birden çok sınıfa ait olabilir. Saldırının istekteki yeri de
  işaretlidir. İkili sınıflandırmadan çok sınıflıya geçilirse işe yarar.
- **Format:** XML. Her kayıtta bağlam (sunucu işletim sistemi, HTTP sunucusu, SQL/LDAP/XPath
  varlığı), sınıf ve istek (method, protokol, URI, sorgu, header, body) bulunur.
  `data/http-mini/requests.jsonl` biçimine dönüştürücü yazılması gerekir.
- **Edinme:** https://www.lirmm.fr/pkdd2007-challenge/ (indirme bağlantısının çalışıp
  çalışmadığı doğrulanmadı).
- **Lisans/kullanım koşulları:** Doğrulanmadı.

## pralab / modsec-learn

- **Kaynak:** "Boosting ModSecurity with Machine Learning" makalesinin veri seti
  (Cagliari ve Genova üniversiteleri).
- **İçerik:** Normal tarafta open-appsec veri setinden yaklaşık 508 bin istek. Saldırı
  tarafında HTTP Params, Kaggle ve SQLmap ile üretilmiş, toplam yaklaşık 30 bin SQLi örneği.
- **Format:** `legitimate/` ve `malicious/` klasörleri; dosyalar GitHub sınırı yüzünden
  parçalanmış, her klasördeki `merge.py` ile birleştirilir. Dosya formatı doğrulanmadı.
- **Bilinmesi gerekenler:** Saldırı tarafı **yalnızca SQLi**'dır; genel "anormal" sınıfını
  temsil etmez. Asıl değeri gerçekçi normal trafik ve çapraz test içindir.
- **Edinme:** `git clone https://github.com/pralab/modsec-learn-dataset data/raw/modsec-learn-dataset` (~460 MB)
- **Lisans/kullanım koşulları:** Doğrulanmadı.

## SR-BH 2020

- **İçerik:** Yaklaşık 908 bin HTTP isteği; CAPEC saldırı kategorilerine göre çoklu etiketli.
- **Format:** CSV; ham istek `full_http_request` sütunundadır.
- **Bilinmesi gerekenler:** Sonradan yapılan bir incelemede "benign" etiketli satırların önemli
  bir kısmının zararlı içerik taşıdığı bulunmuştur. Normal trafik büyük ölçüde WordPress/PHP
  ağırlıklıdır. **Etiketler temizlenmeden kullanılmamalıdır.**
- **Edinme:** Özgün verinin indirme yeri doğrulanmadı.
- **Lisans/kullanım koşulları:** Doğrulanmadı.

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
8. **Lisanslar.** Hiçbir veri setinin lisansı henüz doğrulanmadı. Akademik dışı kullanım veya
   yeniden dağıtım (ör. `data/http-mini/` gibi bir alt kümeyi repoya koymak) öncesinde kontrol edilmelidir.

## Kaynaklar

- CSIC 2010: https://www.tic.itefi.csic.es/dataset/
- CSIC 2010 v2 kullanan çalışma: https://arxiv.org/abs/2412.16791
- ECML/PKDD 2007: https://www.lirmm.fr/pkdd2007-challenge/ ve https://hal-lirmm.ccsd.cnrs.fr/lirmm-00168955
- modsec-learn makalesi: https://arxiv.org/abs/2406.13547
- modsec-learn verisi: https://github.com/pralab/modsec-learn-dataset
- SR-BH 2020: https://portalcientifico.uah.es/documentos/668fc479b9e7c03b01bde810
- SR-BH 2020 etiket incelemesi: https://seclab.cyshield.com/posts/augmenting-sr-bh-2020-a-technical-methodology-for-modern-threat-simulation/
