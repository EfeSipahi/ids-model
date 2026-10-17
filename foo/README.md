# CSIC 2010 HTTP request classifier (normal / anomalous)

Classifies HTTP requests from the [CSIC 2010 Web Application Attacks](https://www.kaggle.com/datasets/ispangler/csic-2010-web-application-attacks) dataset (`csic_database.csv`, 61,065 requests: 36,000 normal, 25,065 anomalous).

## Files

| File | What it is |
|---|---|
| `features.py` | Request parsing and feature extraction (`ParamProfile`, `NumericFeatures`) |
| `train.py` | Trains, evaluates on a leakage-free split, saves `model.joblib` + `metrics.json` |
| `predict.py` | Classifies a URL, a raw HTTP request file, or a CSV |
| `model.joblib` | Trained model, pickled with scikit-learn 1.9.1 (keep `features.py` in the same folder; on another scikit-learn version just rerun `train.py`, it takes ~1.5 min) |

```bash
pip install -r requirements.txt
python train.py --data csic_database.csv --cv
python predict.py --url "http://localhost:8080/tienda1/publico/anadir.jsp?id=3&cantidad=1%27+OR+%271%27%3D%271"
python predict.py --method POST --url http://localhost:8080/tienda1/publico/autenticar.jsp --body "modo=entrar&login=bob&pwd=x&remember=off&B1=Entrar"
python predict.py --raw request.txt
python predict.py --csv some_requests.csv        # needs Method, URL, content columns
```

## Results

Evaluated on **unique** requests with a **grouped** split (see "Data pitfalls"):

| Evaluation | Accuracy | Precision | Recall | F1 | ROC AUC |
|---|---|---|---|---|---|
| 5-fold grouped CV | 0.9962 ± 0.0006 | 0.9969 ± 0.0009 | 0.9970 ± 0.0007 | 0.9969 ± 0.0005 | 0.9999 |
| Held-out grouped test (5,096 requests) | 0.9969 | 0.9972 | 0.9978 | 0.9975 | 1.0000 |

Held-out confusion matrix:

|  | pred normal | pred anomalous |
|---|---|---|
| **normal** | 1911 | 9 |
| **anomalous** | 7 | 3169 |

Models compared (same grouped 5-fold CV, F1):

| Model | F1 |
|---|---|
| Hand-crafted attack indicators only + gradient boosting | 0.889 |
| Char 1–4-gram TF-IDF + logistic regression | 0.969 |
| Char n-grams (decoded + raw URL) + logistic regression | 0.980 |
| **Normal-traffic profile + attack indicators + gradient boosting (final)** | **0.997** |

## How it works

Only the method, URL path, and parameters (query string or POST body) are used. Each request is URL-decoded (Latin-1, twice to unwrap double encoding) and turned into two feature groups:

1. **Normal-traffic profile (`ParamProfile`)** – learned from the *normal* training requests only, like a positive-security WAF. For each known parameter (`cp`, `dni`, `email`, `ntc`, `precio`, …) it records value "shapes" (`28001 → 9`, `280A1 → 9A9`), the characters ever seen, and the length range. A request is scored on unknown paths, unknown parameter names, unseen shapes, novel characters, and out-of-range lengths. It is cross-fitted on the training set so the classifier never sees a profile built from the row it is scoring.
2. **Attack indicators (`NumericFeatures`)** – lengths, special-character counts and ratios, SQL / XSS / traversal / command-injection keyword counts, double-encoding, HTTP method, etc.

A `HistGradientBoostingClassifier` combines both. The profile features do most of the work: many "anomalous" requests in CSIC are not textbook attacks but malformed values (a letter in a postcode, a 15-digit card number, two `@` in an email), which only make sense relative to what that field normally contains.

## Data pitfalls handled

- **Duplicates:** only 25,598 of 61,065 rows are unique requests (e.g. `/tienda1/index.jsp` appears 1,000 times). With a plain random split ~60% of test rows are exact copies of training rows, which inflates scores. Exact duplicates are removed, and the split groups requests by path + parameters so a GET and its POST twin never straddle train and test.
- **Leaky or useless columns dropped:** User-Agent, Accept, Pragma, etc. are constant; the cookie is a random session ID; `host=localhost:9090` appears only in the 397 anomalous PUT requests.

## Limitations

- The profile is specific to this web shop. For a different application, retrain on that application's normal traffic.
- `PUT` only occurs in anomalous rows, so the model treats any PUT as suspicious.
- The Kaggle CSV contains the original `normalTrafficTraining` and `anomalousTrafficTest` files; the original `normalTrafficTest` set is not included, so all metrics come from splits of these two files.
- Most remaining errors are borderline value anomalies, e.g. a trailing space in a password.