"""
classifiers/bayesian.py — Gaussian Naive Bayes classifier

HOW GAUSSIAN NAIVE BAYES WORKS FOR THIS PROJECT:
  GNB models the distribution of each feature for each class as a Gaussian
  (normal) curve.  To classify a new sample it computes:
    P(class | features) ∝ P(class) × ∏ P(feature_i | class)
  and picks the class with the highest posterior probability.

  The "Naive" assumption is that features are independent given the class.
  In reality image features are correlated, but the model still works
  surprisingly well in practice.

  For image features:
  - StandardScaler centres and scales the features, helping GNB fit
    better Gaussian distributions to each feature dimension.
  - PCA(100) is the most important step for Naive Bayes.  PCA produces
    principal components that are uncorrelated by construction — which is
    exactly the independence that Naive Bayes assumes.  Without PCA, the
    independence assumption is badly violated and accuracy suffers.
  - After PCA, features are closer to Gaussian-distributed per class,
    making the model's assumptions more valid.

WHY GNB SHOWS 100% CONFIDENCE WITHOUT CALIBRATION:
  GNB multiplies one probability per feature.  With 100 features, even
  a tiny per-feature bias compounds exponentially:
    (0.51 / 0.49)^100 ≈ 58,000 : 1  →  rounds to 100%
  CalibratedClassifierCV (sigmoid method, 5-fold) learns to convert those
  extreme raw scores into realistic probabilities (e.g. 40%, 25%, 18%...)
  using held-out fold data.  Classification accuracy does not change —
  only the confidence values become meaningful.

GNB is expected to be the weakest model in this comparison.  It is included
because (a) the university task requires it and (b) it provides a useful
baseline: if SVM/kNN/NN barely beat GNB, the feature set is likely weak.

PIPELINE: StandardScaler → PCA(100) → CalibratedClassifierCV(GaussianNB, sigmoid)
"""

import time
import pickle
import pathlib
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = pathlib.Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "features" / "vector_features.pkl"
RESULTS_PATH  = BASE_DIR / "results"  / "bayesian_results.pkl"


# ── Functions ─────────────────────────────────────────────────────────────────

def load_data():
    """Load the train/test feature vectors saved by extractor.py."""
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"vector_features.pkl not found at {FEATURES_PATH}\n"
            "Run:  python features/extractor.py"
        )
    with open(FEATURES_PATH, "rb") as f:
        d = pickle.load(f)
    X_train = np.array(d["X_train"])
    X_test  = np.array(d["X_test"])
    y_train = list(d["y_train"])
    y_test  = list(d["y_test"])
    return X_train, X_test, y_train, y_test


def build_model():
    """
    Build the pipeline: PCA(100) → Calibrated GaussianNB.
    No StandardScaler — extractor.py already scaled the data.
    Applying it again would double-scale and corrupt the features.
    """
    return make_pipeline(
        PCA(n_components=100, random_state=42),
        CalibratedClassifierCV(GaussianNB(), cv=5, method="sigmoid"),
    )


def train_model(pipeline, X_train, y_train):
    """Fit the calibrated Naive Bayes pipeline."""
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"Model fitted in {elapsed:.2f}s")
    return pipeline, elapsed


def evaluate_model(pipeline, X_test, y_test, label_names):
    """Predict on the held-out test set and return all metrics."""
    t0 = time.time()
    y_pred  = pipeline.predict(X_test)
    infer_t = time.time() - t0

    acc = accuracy_score(y_test, y_pred)
    report_dict = classification_report(
        y_test, y_pred,
        labels=label_names, target_names=label_names,
        output_dict=True, zero_division=0,
    )
    print(classification_report(
        y_test, y_pred,
        labels=label_names, target_names=label_names,
        zero_division=0,
    ))
    print(f"Test accuracy : {acc:.4f}   Inference time: {infer_t:.4f}s")
    cm = confusion_matrix(y_test, y_pred, labels=label_names)
    return y_pred, acc, report_dict, cm, infer_t


def save_model(pipeline, y_test, y_pred, acc, report, cm,
               label_names, train_t, infer_t):
    """
    Save the trained pipeline and all evaluation metrics to results/.
    The 'model' key holds the full trained pipeline (Scaler+PCA+CalibratedGNB).
    api/server.py loads this pipeline directly for live prediction.
    """
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name"      : "Bayesian (GaussianNB + Calibrated)",
        "model"           : pipeline,       # full trained pipeline
        "label_names"     : label_names,    # class names from data/ folders
        "label_encoder"   : None,           # GNB uses string labels directly
        "y_test"          : y_test,
        "y_pred"          : y_pred,
        "accuracy"        : acc,
        "report"          : report,
        "confusion_matrix": cm,
        "train_time"      : train_t,
        "infer_time"      : infer_t,
    }
    with open(RESULTS_PATH, "wb") as f:
        pickle.dump(payload, f)
    print(f"Saved → {RESULTS_PATH}")


def main():
    # 1. Load features
    X_train, X_test, y_train, y_test = load_data()
    label_names = sorted(set(y_train))  # dynamic — from data/ folder names
    print(f"Train: {len(X_train)}  Test: {len(X_test)}  "
          f"Classes ({len(label_names)}): {label_names}")

    # 2. Build and train
    pipeline = build_model()
    pipeline, train_t = train_model(pipeline, X_train, y_train)

    # 3. Evaluate
    y_pred, acc, report, cm, infer_t = evaluate_model(
        pipeline, X_test, y_test, label_names
    )

    # 4. Save
    save_model(pipeline, y_test, y_pred, acc, report, cm,
               label_names, train_t, infer_t)
    print("Naive Bayes training complete.")


if __name__ == "__main__":
    main()

 
