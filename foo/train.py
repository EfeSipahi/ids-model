"""Train a normal/anomalous HTTP request classifier on CSIC 2010 (Kaggle: ispangler/csic-2010-web-application-attacks).

    python train.py --data csic_database.csv            # train, evaluate on a held-out grouped split, save model.joblib
    python train.py --data csic_database.csv --cv       # also run 5-fold grouped cross-validation

Evaluation protocol (leakage-free):
  * Only ~25.6k of the 61k rows are unique requests; a random row split puts ~60% exact copies of training rows in the
    test set. We drop exact duplicates and split by groups of (path + decoded parameters), so GET/POST twins of the
    same request never land on both sides.
  * Training is always done on de-duplicated data: ParamProfile cross-fits its features, and thousands of copies of
    one request would all get the same out-of-fold view and dominate the fit.
  * Headers are ignored: User-Agent/Accept/etc. are constant, the cookie is a random session id, and host=localhost:9090
    only occurs in anomalous rows (a dataset artifact, not a real signal).
"""
import argparse
import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline

from Features import NumericFeatures, ParamProfile, prepare

SEED = 42


def build_model():
    features = ColumnTransformer([
        ("profile", ParamProfile(), ["path", "params_raw"]),                      # deviation from learned normal traffic
        ("numeric", NumericFeatures(), ["path", "params", "params_raw", "method"]),  # generic attack indicators
    ])
    clf = HistGradientBoostingClassifier(max_iter=500, learning_rate=0.08, random_state=SEED)
    return Pipeline([("features", features), ("clf", clf)])


def load(path):
    df = pd.read_csv(path)
    if "classification" in df.columns:
        y = pd.to_numeric(df["classification"], errors="coerce")
    else:  # the unnamed first column holds "Normal" / "Anomalous"
        y = (df.iloc[:, 0].astype(str).str.lower() == "anomalous").astype(int)
    df = df[y.notna()]
    return df, y[y.notna()].astype(int).values


def scores(y, p, s):
    return {"accuracy": accuracy_score(y, p), "precision": precision_score(y, p), "recall": recall_score(y, p),
            "f1": f1_score(y, p), "roc_auc": roc_auc_score(y, s)}


def fmt(d):
    return "  ".join(f"{k}={v:.4f}" for k, v in d.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/home/user/Repositores/ids-model/foo/data/raw/csic_database.csv")
    ap.add_argument("--out", default="model.joblib")
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--cv", action="store_true", help="run 5-fold grouped cross-validation")
    args = ap.parse_args()

    df, y = load(args.data)
    X = prepare(df)
    print(f"Loaded {len(X)} rows  (normal={int((y == 0).sum())}, anomalous={int((y == 1).sum())})")

    key = X["method"] + "|" + X["path_raw"] + "|" + X["params_raw"]
    keep = ~key.duplicated().values
    X, y = X[keep].reset_index(drop=True), y[keep]
    groups = (X["path"] + "?" + X["params"]).values
    print(f"After removing exact duplicates: {len(X)} unique requests "
          f"(normal={int((y == 0).sum())}, anomalous={int((y == 1).sum())}), {len(set(groups))} groups")

    results = {}
    if args.cv:
        t, folds = time.time(), []
        for tr, te in GroupKFold(n_splits=5).split(X, y, groups):
            m = build_model().fit(X.iloc[tr], y[tr])
            s = m.predict_proba(X.iloc[te])[:, 1]
            folds.append(scores(y[te], (s >= 0.5).astype(int), s))
        cv = pd.DataFrame(folds)
        results["cv_5fold_grouped"] = {c: {"mean": cv[c].mean(), "std": cv[c].std()} for c in cv}
        print(f"[5-fold grouped CV] " + "  ".join(f"{c}={cv[c].mean():.4f}±{cv[c].std():.4f}" for c in cv)
              + f"  ({time.time() - t:.0f}s)")

    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=SEED).split(X, y, groups))
    m = build_model().fit(X.iloc[tr], y[tr])
    s = m.predict_proba(X.iloc[te])[:, 1]
    p = (s >= 0.5).astype(int)
    results["holdout_grouped"] = scores(y[te], p, s)
    cm = confusion_matrix(y[te], p)
    results["holdout_confusion_matrix"] = {"labels": ["normal", "anomalous"], "matrix": cm.tolist()}
    print(f"\n[held-out grouped test set: {len(te)} unique requests]  {fmt(results['holdout_grouped'])}")
    print("Confusion matrix (rows=true, cols=pred)  [normal, anomalous]")
    print(f"  normal     {cm[0, 0]:6d} {cm[0, 1]:6d}\n  anomalous  {cm[1, 0]:6d} {cm[1, 1]:6d}")
    print(classification_report(y[te], p, target_names=["normal", "anomalous"], digits=4))

    final = build_model().fit(X, y)  # refit on all unique requests for deployment
    joblib.dump({"model": final, "threshold": 0.5, "trained_on": len(X)}, args.out)
    with open("metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved final model -> {args.out}, metrics -> metrics.json")


if __name__ == "__main__":
    main()