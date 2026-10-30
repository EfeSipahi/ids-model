# IDS Projesi

Bu projenin amacı, HTTP isteklerinin özelliklerini kullanarak normal / anormal ayrımı yapan denetimli bir sınıflandırma modeli geliştirmektir. Özellikler modelin girdileri, normal/anormal etiketi ise öğrenilmesi hedeflenen cevaptır. Anormal kaynak etiketi her kaydın doğrulanmış saldırı olduğu anlamına gelmez.

27 Eylül 2026 itibarıyla CSIC 2010'dan seçilmiş 1.000 HTTP isteği için 21 özellik çıkarıldı. Güncel içerik gruplamasıyla 604 eğitim, 197 doğrulama ve 199 test kaydı ayrıldı. İlk Random Forest yalnız eğitimde öğrenilen ön işlemeyle eğitildi; doğrulamada F1 %72,53 ve yanlış alarm oranı %18,18 elde edildi. Sabit model ayrıca 199 final test kaydında değerlendirildi: accuracy %67,84, F1 %66,32, yanlış alarm oranı %28,00. Model yeniden eğitilmedi. Güncel sonuçlar [final test raporunda](reports/rf-baseline-v1-test/README.md). Canlı trafik toplama ve engelleme henüz yok.

13 Ekim 2026 itibarıyla aynı veri ve aynı özelliklerle bir lojistik regresyon modeli eklendi; ardından iki modelin parametreleri yalnız eğitim kümesinde gruplu çapraz doğrulamayla yeniden seçilip `v2` olarak kaydedildi. 199 test kaydındaki sonuçlar:

| Model | Kayıt | Karar eşiği | Accuracy | Precision | Recall | F1 | Yanlış alarm oranı | ROC AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest v1 | `rf-baseline-v1` | 0,5 | %67,84 | %69,23 | %63,64 | %66,32 | %28,00 | 0,720 |
| Random Forest v2 | `rf-tuned-v2` | 0,5 | %70,35 | %70,41 | %69,70 | %70,05 | %29,00 | 0,765 |
| Lojistik regresyon v1 | `logreg-baseline-v1` | 0,5 | %63,32 | %62,50 | %65,66 | %64,04 | %39,00 | 0,709 |
| Lojistik regresyon v2 | `logreg-tuned-v2` | 0,4 | %57,79 | %55,81 | %72,73 | %63,16 | %57,00 | 0,724 |

Testte en iyi sonucu Random Forest v2 verdi. Lojistik regresyon v2, eğitimde seçilen 0,4 eşiği yüzünden v1'den daha fazla yanlış alarm üretti; iyileşme sayılmaz. Test kümesi artık dört model için de görülmüştür: bu sonuçlara bakarak ayar değiştirilirse aynı küme yeniden hiç görülmemiş test gibi sunulamaz. Ayrıntılar [PDF raporlarında](reports/pdf/).

Model girdisi yalnız `features` alanıdır; kaynak ve grup metadata'sı kullanılmaz. Eski endpoint gruplaması bu ana deneyde kullanılmaz. Eski belgelerdeki "henüz model eğitilmedi" ifadeleri o aşamanın tarihsel durumudur.

## Nereden başlamalı?

1. [Random Forest eğitim süreci](docs/random-forest-egitim-sureci.md): yapılan her şeyin yeni başlayanlar için nedenleriyle anlatımı.
2. [Adım adım notebook](notebooks/04_ilk_random_forest.ipynb): aynı deneyin hücre hücre hâli.
3. [Final test raporu](reports/rf-baseline-v1-test/README.md): ilk Random Forest'ın test sonuçları.
4. [PDF raporları](reports/pdf/): özniteliklerin bir istek üzerinden anlatımı, iki modelin karşılaştırması ve v2 parametre iyileştirmesi.

## Dosya yapısı

```text
Lorica/
├── data/
│   ├── http-mini/     # CSIC 2010'dan seçilmiş 1.000 istek (repoda)
│   ├── processed/     # Betiklerin ürettiği özellik, grup ve ayrım tabloları (repoda)
│   └── raw/           # İndirilen büyük özgün veri (repoda DEĞİL, aşağıya bak)
├── scripts/           # Veri hazırlama, eğitim ve değerlendirme betikleri
├── tests/             # Betiklerin testleri
├── notebooks/         # Adım adım inceleme defterleri
├── models/            # Ön işleme + modelin birlikte saklandığı deney kayıtları
├── reports/           # Betiklerin ürettiği sonuç çıktıları
│   └── pdf/           # Ders için hazırlanmış PDF raporları
├── docs/              # Elle yazılmış açıklama ve süreç belgeleri
└── requirements.txt   # Sabitlenmiş Python paket sürümleri
```

| Betik | Görevi |
| --- | --- |
| `scripts/extract_features.py` | HTTP isteklerinden 21 sayısal özellik çıkarır |
| `scripts/group_requests.py` | Eski endpoint gruplaması (ana deneyde kullanılmıyor) |
| `scripts/split_requests.py` | İçerik gruplarını ve sabit eğitim/doğrulama/test ayrımını oluşturur |
| `scripts/train_random_forest.py` | Ön işleme + Random Forest eğitir, doğrulamayı ölçer, modeli kaydeder |
| `scripts/evaluate_test.py` | Kaydedilmiş `rf-baseline-v1` modelini değiştirmeden testte değerlendirir |
| `scripts/train_logistic_regression.py` | log1p + ölçekleme + lojistik regresyon eğitir, doğrulamayı ölçer, modeli kaydeder |
| `scripts/evaluate_test_logreg.py` | Kaydedilmiş `logreg-baseline-v1` modelini değiştirmeden testte değerlendirir |
| `scripts/train_tuned.py` | v2: parametreleri ve karar eşiğini yalnız eğitim kümesinde gruplu çapraz doğrulamayla seçer, modeli kaydeder |
| `scripts/evaluate_test_tuned.py` | Kaydedilmiş bir v2 modelini eğitimde seçilen eşikle testte değerlendirir |
| `scripts/evaluate_predictions.py` | Kayıtlı tahmin dosyalarından sınıflandırma ölçütlerini (hata matrisi, accuracy, precision, recall, F1, yanlış alarm oranı, ROC AUC, ROC noktaları) hesaplar; model yüklemez |

### Deney kayıtları

| Deney | Model klasörü | Test raporu | Tüm ölçütler |
| --- | --- | --- | --- |
| Random Forest v1 | `models/rf-baseline-v1/` | `reports/rf-baseline-v1-test/` | `reports/rf-baseline-v1-metrics/` |
| Lojistik regresyon v1 | `models/logreg-baseline-v1/` | `reports/logreg-baseline-v1-test/` | `reports/logreg-baseline-v1-metrics/` |
| Random Forest v2 | `models/rf-tuned-v2/` | `reports/rf-tuned-v2-test/` | `reports/rf-tuned-v2-metrics/` |
| Lojistik regresyon v2 | `models/logreg-tuned-v2/` | `reports/logreg-tuned-v2-test/` | `reports/logreg-tuned-v2-metrics/` |

Her model klasöründe `pipeline.joblib` (ön işleme + model), `run.json` (ayarlar, veri ve kod hash'leri, doğrulama sonuçları) ve doğrulama tahminleri bulunur. v2 klasörlerinde ayrıca denenen bütün adayların çapraz doğrulama sonuçları `search_results.json` içindedir.

### PDF raporları

| Dosya | İçerik |
| --- | --- |
| [IDS_Oznitelik_Ornegi_Raporu.pdf](reports/pdf/IDS_Oznitelik_Ornegi_Raporu.pdf) | Gerçek bir HTTP isteği üzerinden 21 özniteliğin nasıl hesaplandığı |
| [IDS_Model_Karsilastirma_Raporu.pdf](reports/pdf/IDS_Model_Karsilastirma_Raporu.pdf) | Random Forest v1 ile lojistik regresyon v1'in doğrulama ve test karşılaştırması |
| [IDS_Model_Iyilestirme_Raporu_v2.pdf](reports/pdf/IDS_Model_Iyilestirme_Raporu_v2.pdf) | v2 parametre araması, seçilen ayarlar ve v1–v2 karşılaştırması |

Bu PDF'ler `reports/` altındaki JSON kayıtlarından elle tetiklenen ayrı bir betikle üretilmiştir; üretim betiği repoda değildir.

Belgeler: [özellik çıkarıcı](docs/oznitelik-cikarici.md), [veri ayrımı](docs/http-veri-ayrimi.md), [ilk eğitim raporu](docs/ilk-random-forest.md), [eski gruplama](docs/http-gruplama.md).

## Ortam

| Bileşen | Sürüm |
| --- | --- |
| Python | 3.14.7 |
| scikit-learn | 1.9.1 |
| NumPy | 2.5.3 |
| pandas | 3.0.6 |
| SciPy | 1.18.1 |
| joblib | 1.6.0 |
| Matplotlib | 3.11.2 |
| JupyterLab | 4.6.4 |

Proje Linux üzerinde (Fedora) bu sürümlerle geliştirildi ve test edildi; başka Python sürümlerinde denenmedi. Bütün paketlerin tam sürümleri `requirements.txt` içindedir. Kayıtlı modelleri (`pipeline.joblib`) yüklemek ve test değerlendirme betiklerini çalıştırmak için scikit-learn sürümünün aynı (1.9.1) olması gerekir; betikler farklı sürümde durur.

## Kurulum

```bash
git clone https://github.com/EfeSipahi/Lorica.git
cd Lorica
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
python scripts/train_logistic_regression.py --output-dir models/logreg-baseline-v1-repeat

# v2: parametre araması (Random Forest için birkaç dakika sürer)
python scripts/train_tuned.py --model rf --output-dir models/rf-tuned-v2-repeat
python scripts/train_tuned.py --model logreg --output-dir models/logreg-tuned-v2-repeat

# Kayıtlı bir deneyin tahminlerinden bütün sınıflandırma ölçütleri (çıktı dizini yoksa)
python scripts/evaluate_predictions.py rf-tuned-v2 --output-dir reports/rf-tuned-v2-metrics-repeat

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
| `data/raw/owasp/` | ~380 MB | Lucz & Forstner'ın herkese açık 30 günlük ModSecurity denetim logları (CC-BY-4.0, DOI [10.5281/zenodo.17178461](https://zenodo.org/records/17178461)). 19 Ekim 2026'da doğrulandı: Zenodo'daki `owasp.zip` (MD5 `95b7a8237abc163d8ca31e49f7318efd`) açıldığında çıkan 30 log dosyası bu klasördekilerle bayt bayt aynı |

Bu iki veri seti henüz hiçbir betikte kullanılmıyor. Özgün verinin üzerine yazılmaz; temizleme ve dönüşüm sonuçları `data/processed/` altında ayrı dosyalara kaydedilir.

## Ortak çalışma kuralları

- Kişisel notlar ve denemeler `local/` klasörüne konur; bu klasör `.gitignore` ile dışlanmıştır.
- Belgelere ve kodlara kendi bilgisayarındaki tam yol (`/home/...`) yazılmaz, proje köküne göre yol kullanılır.
- `models/` altındaki dört deney klasörü ve `reports/` altındaki `-test` ve `-metrics` klasörleri kayıtlı deneydir; içlerindeki hash'ler betiklere ve veriye bağlıdır, elle değiştirilmez. Yeni deney yeni bir klasöre yazılır.
- Kayıtlı bir deneyin hash'ine giren betikler (`extract_features.py`, `train_random_forest.py`, `train_logistic_regression.py`, `train_tuned.py`) değiştirilirse o deneyin test betiği "eğitim kodu değişmiş" diyerek durur. Yeni davranış için yeni betik ya da yeni deney sürümü açılır.
- `.joblib` dosyaları yüklenirken kod çalıştırabilir; yalnız bu repodan gelen model dosyalarını yükleyin.
- Paket eklendiğinde `python -m pip freeze > requirements.txt` ile sürüm kaydı güncellenir.

## Kütüphaneler

- JupyterLab: kodu hücreler hâlinde çalıştırmak ve çıktıları görmek.
- pandas: tabloları okumak ve incelemek.
- NumPy: sayısal dizilerle çalışmak.
- scikit-learn: ön işleme, model eğitimi ve değerlendirme.
- Matplotlib: veri dağılımlarını çizmek.
