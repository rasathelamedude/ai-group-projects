"""
classifiers/svm.py — Support Vector Machine classifier

HOW SVM WORKS FOR THIS PROJECT:
  SVM finds the decision boundary (hyperplane) that maximises the margin between
  classes in feature space.  The RBF kernel implicitly maps features into a
  higher-dimensional space so the boundary can be non-linear.

  For image features:
  - StandardScaler is mandatory.  SVM with RBF is extremely sensitive to feature
    scale — a single large-valued HOG feature would dominate all distance
    calculations if not normalised.
  - PCA(150) reduces ~1892 features to the 150 most discriminative directions.
    This removes noise, speeds up training, and makes the kernel more effective.
  - GridSearchCV tests C ∈ {1, 10, 100} with gamma='scale' via 5-fold CV.
    C controls the penalty for misclassified training points:
      low C  → smoother boundary, tolerates some misclassification (less overfit)
      high C → tighter boundary, fits training data more closely (can overfit)
  - probability=True adds Platt scaling so predict_proba() works for the UI.

PIPELINE: StandardScaler → PCA(150) → SVC(RBF, probability=True)
"""

import time
import pickle
import pathlib
import numpy as np
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = pathlib.Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "features" / "vector_features.pkl"
RESULTS_PATH  = BASE_DIR / "results"  / "svm_results.pkl"

# Only 3 values × 1 gamma × 5 folds = 15 fits — fast but effective
PARAM_GRID = {"svc__C": [1, 10, 100], "svc__gamma": ["scale"]}


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
    Build the pipeline and GridSearchCV object.
    No StandardScaler here — extractor.py already scaled the data.
    Applying it again would double-scale and corrupt the features.
    """
    pipeline = make_pipeline(
        PCA(n_components=150, random_state=42),
        SVC(kernel="rbf", probability=True, random_state=42),
    )
    return GridSearchCV(
        pipeline, PARAM_GRID, cv=5, scoring="accuracy", n_jobs=-1, verbose=1
    )


def train_model(gs, X_train, y_train):
    """Fit the GridSearchCV and return the best pipeline + metadata."""
    t0 = time.time()
    gs.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"Best params : {gs.best_params_}")
    print(f"CV accuracy : {gs.best_score_:.4f}   training time: {elapsed:.2f}s")
    return gs.best_estimator_, gs.best_params_, elapsed


def evaluate_model(pipeline, X_test, y_test, label_names):
    """Predict on the held-out test set and return all metrics."""
    t0 = time.time()
    y_pred = pipeline.predict(X_test)
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
               label_names, best_params, train_t, infer_t):
    """
    Save the trained pipeline and all evaluation metrics to results/.
    The 'model' key holds the full trained pipeline (Scaler+PCA+SVC).
    api/server.py loads this pipeline directly for live prediction.
    """
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name"      : "SVM (RBF + PCA)",
        "model"           : pipeline,          # full trained pipeline
        "label_names"     : label_names,        # class names from data/ folders
        "label_encoder"   : None,               # SVM uses string labels directly
        "best_params"     : best_params,
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
    label_names = sorted(set(y_train))  # dynamic — comes from data/ folder names
    print(f"Train: {len(X_train)}  Test: {len(X_test)}  "
          f"Classes ({len(label_names)}): {label_names}")

    # 2. Build and train
    gs = build_model()
    pipeline, best_params, train_t = train_model(gs, X_train, y_train)

    # 3. Evaluate
    y_pred, acc, report, cm, infer_t = evaluate_model(
        pipeline, X_test, y_test, label_names
    )

    # 4. Save
    save_model(pipeline, y_test, y_pred, acc, report, cm,
               label_names, best_params, train_t, infer_t)
    print("SVM training complete.")


if __name__ == "__main__":
    main()
