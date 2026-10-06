# IDS Projesi

Bu projenin amacı, HTTP isteklerinin özelliklerini kullanarak normal / anormal ayrımı yapan denetimli bir sınıflandırma modeli geliştirmektir. Özellikler modelin girdileri, normal/anormal etiketi ise öğrenilmesi hedeflenen cevaptır. Anormal kaynak etiketi her kaydın doğrulanmış saldırı olduğu anlamına gelmez.

27 Eylül 2026 itibarıyla CSIC 2010'dan seçilmiş 1.000 HTTP isteği için 21 özellik çıkarıldı. Güncel içerik gruplamasıyla 604 eğitim, 197 doğrulama ve 199 test kaydı ayrıldı. İlk Random Forest yalnız eğitimde öğrenilen ön işlemeyle eğitildi; doğrulamada F1 %72,53 ve yanlış alarm oranı %18,18 elde edildi. Sabit model ayrıca 199 final test kaydında değerlendirildi: accuracy %67,84, F1 %66,32, yanlış alarm oranı %28,00. Model yeniden eğitilmedi. Güncel sonuçlar [final test raporunda](reports/rf-baseline-v1-test/README.md). Canlı trafik toplama ve engelleme henüz yok.

Model girdisi yalnız `features` alanıdır; kaynak ve grup metadata'sı kullanılmaz. Eski endpoint gruplaması bu ana deneyde kullanılmaz. Eski belgelerdeki "henüz model eğitilmedi" ifadeleri o aşamanın tarihsel durumudur.

## Nereden başlamalı?

1. [Random Forest eğitim süreci](docs/random-forest-egitim-sureci.md): yapılan her şeyin yeni başlayanlar için nedenleriyle anlatımı.
2. [Adım adım notebook](notebooks/04_ilk_random_forest.ipynb): aynı deneyin hücre hücre hâli.
3. [Final test raporu](reports/rf-baseline-v1-test/README.md): güncel sonuçlar.

## Dosya yapısı

```text
ids-model/
├── data/
│   ├── http-mini/     # CSIC 2010'dan seçilmiş 1.000 istek (repoda)
│   ├── processed/     # Betiklerin ürettiği özellik, grup ve ayrım tabloları (repoda)
│   └── raw/           # İndirilen büyük özgün veri (repoda DEĞİL, aşağıya bak)
├── scripts/           # Veri hazırlama, eğitim ve değerlendirme betikleri
├── tests/             # Betiklerin testleri
├── notebooks/         # Adım adım inceleme defterleri
├── models/            # Ön işleme + modelin birlikte saklandığı deney kayıtları
├── reports/           # Betiklerin ürettiği sonuç çıktıları
├── docs/              # Elle yazılmış açıklama ve süreç belgeleri
└── requirements.txt   # Sabitlenmiş Python paket sürümleri
```

| Betik | Görevi |
| --- | --- |
| `scripts/extract_features.py` | HTTP isteklerinden 21 sayısal özellik çıkarır |
| `scripts/group_requests.py` | Eski endpoint gruplaması (ana deneyde kullanılmıyor) |
| `scripts/split_requests.py` | İçerik gruplarını ve sabit eğitim/doğrulama/test ayrımını oluşturur |
| `scripts/train_random_forest.py` | Ön işleme + Random Forest eğitir, doğrulamayı ölçer, modeli kaydeder |
| `scripts/evaluate_test.py` | Kaydedilmiş modeli değiştirmeden testte değerlendirir |

Belgeler: [özellik çıkarıcı](docs/oznitelik-cikarici.md), [veri ayrımı](docs/http-veri-ayrimi.md), [ilk eğitim raporu](docs/ilk-random-forest.md), [eski gruplama](docs/http-gruplama.md).

## Kurulum

```bash
git clone https://github.com/EfeSipahi/ids-model.git
cd ids-model
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`.venv` sanal makine değildir; Python kütüphanelerini sistem ortamından ayırır. Sistem Python'u değiştirilmez ve `sudo pip` kullanılmaz. Her yeni terminalde `source .venv/bin/activate` ile ortam açılır, `deactivate` ile kapatılır.

## Çalıştırma

```bash
# Testler
PYTHONPATH=scripts python -m unittest discover -s tests -v

# Aynı deneyi yeniden üretmek için yeni bir çıktı dizini verilir
python scripts/train_random_forest.py --output-dir models/rf-baseline-v1-repeat

# Notebook'lar
python -m jupyterlab
```

Eğitim ve değerlendirme betikleri var olan çıktı dizininin üzerine yazmaz.

## Veri

`data/http-mini/` ve `data/processed/` küçük olduğu için repodadır; klonladıktan sonra ek indirme yapmadan eğitim çalıştırılabilir. Kaynak ve etiket açıklamaları [data/http-mini/README.md](data/http-mini/README.md) içindedir.

`data/raw/` altındaki büyük özgün veriler repoya alınmaz, herkes kendi bilgisayarına indirir:

| Klasör | Boyut | Nasıl edinilir |
| --- | --- | --- |
| `data/raw/modsec-learn-dataset/` | ~460 MB | `git clone https://github.com/pralab/modsec-learn-dataset data/raw/modsec-learn-dataset` |
| `data/raw/owasp/` | ~380 MB | Anonimleştirilmiş ModSecurity denetim logları; ekip içinde paylaşılır |

Bu iki veri seti henüz hiçbir betikte kullanılmıyor. Özgün verinin üzerine yazılmaz; temizleme ve dönüşüm sonuçları `data/processed/` altında ayrı dosyalara kaydedilir.

## Ortak çalışma kuralları

- Kişisel notlar ve denemeler `local/` klasörüne konur; bu klasör `.gitignore` ile dışlanmıştır.
- Belgelere ve kodlara kendi bilgisayarındaki tam yol (`/home/...`) yazılmaz, proje köküne göre yol kullanılır.
- `models/rf-baseline-v1/` ve `reports/rf-baseline-v1-test/` kayıtlı deneydir; içlerindeki hash'ler betiklere ve veriye bağlıdır, elle değiştirilmez. Yeni deney yeni bir klasöre yazılır.
- `.joblib` dosyaları yüklenirken kod çalıştırabilir; yalnız bu repodan gelen model dosyalarını yükleyin.
- Paket eklendiğinde `python -m pip freeze > requirements.txt` ile sürüm kaydı güncellenir.

## Kütüphaneler

- JupyterLab: kodu hücreler hâlinde çalıştırmak ve çıktıları görmek.
- pandas: tabloları okumak ve incelemek.
- NumPy: sayısal dizilerle çalışmak.
- scikit-learn: ön işleme, model eğitimi ve değerlendirme.
- Matplotlib: veri dağılımlarını çizmek.
