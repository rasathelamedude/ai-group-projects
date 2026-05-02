"""
classifiers/knn.py — k-Nearest Neighbors classifier

HOW kNN WORKS FOR THIS PROJECT:
  kNN stores every training feature vector.  When predicting, it finds the K
  training samples closest to the query vector (by distance) and returns the
  majority class among those K neighbors.

  For image features:
  - StandardScaler is mandatory.  Without scaling, a single large HOG value
    would dominate all distance calculations, making color/histogram features
    irrelevant to the distance.
  - PCA(80) is critical for kNN.  In high dimensions (~1892 features), all
    training points are roughly equally far from a test point — the "curse of
    dimensionality".  PCA compresses the data to the 80 directions of highest
    variance, making distance calculations meaningful.
  - Cosine distance outperforms Euclidean for HOG-based vectors.  HOG produces
    histogram-like outputs where the relative distribution of values matters
    more than the absolute magnitude.  Cosine distance captures this.
  - Best k is found via 5-fold CV on odd values 1–15 (odd avoids tie votes).

PIPELINE: StandardScaler → PCA(80) → KNeighborsClassifier(cosine)
"""

import time
import pickle
import pathlib
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = pathlib.Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "features" / "vector_features.pkl"
RESULTS_PATH  = BASE_DIR / "results"  / "knn_results.pkl"


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


def build_model(k):
    """
    Build the pipeline for a given k.
    No StandardScaler — extractor.py already scaled the data.
    Applying it again would double-scale and corrupt the features.
    """
    return make_pipeline(
        PCA(n_components=80, random_state=42),
        KNeighborsClassifier(n_neighbors=k, metric="cosine", n_jobs=-1),
    )


def find_best_k(X_train, y_train):
    """
    Test odd k values 1–15 using 5-fold CV.
    Returns the k with the highest mean validation accuracy.
    Odd values only — avoids tie-breaking when deciding the majority class.
    """
    print("Tuning k via 5-fold cross-validation:")
    best_k, best_score = 1, 0.0
    for k in range(1, 16, 2):
        pipe  = build_model(k)
        score = cross_val_score(pipe, X_train, y_train, cv=5, scoring="accuracy").mean()
        print(f"  k={k:2d}  mean CV accuracy = {score:.4f}")
        if score > best_score:
            best_score, best_k = score, k
    print(f"Best k = {best_k}  (CV accuracy = {best_score:.4f})")
    return best_k


def train_model(X_train, y_train, best_k):
    """Fit the final pipeline on the full training set using the best k."""
    pipe = build_model(best_k)
    t0 = time.time()
    pipe.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"Model fitted with k={best_k} in {elapsed:.4f}s")
    return pipe, elapsed


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
               label_names, best_k, train_t, infer_t):
    """
    Save the trained pipeline and all evaluation metrics to results/.
    The 'model' key holds the full trained pipeline (Scaler+PCA+kNN).
    api/server.py loads this pipeline directly for live prediction.
    """
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name"      : "kNN",
        "model"           : pipeline,           # full trained pipeline
        "label_names"     : label_names,         # class names from data/ folders
        "label_encoder"   : None,                # kNN uses string labels directly
        "best_k"          : best_k,
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

    # 2. Find best k via cross-validation
    best_k = find_best_k(X_train, y_train)

    # 3. Train final model with best k
    pipeline, train_t = train_model(X_train, y_train, best_k)

    # 4. Evaluate on test set
    y_pred, acc, report, cm, infer_t = evaluate_model(
        pipeline, X_test, y_test, label_names
    )

    # 5. Save
    save_model(pipeline, y_test, y_pred, acc, report, cm,
               label_names, best_k, train_t, infer_t)
    print("kNN training complete.")


if __name__ == "__main__":
    main()
