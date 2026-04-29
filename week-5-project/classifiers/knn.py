"""
knn.py

Trains a k-Nearest Neighbors (kNN) classifier on the feature vectors
produced by extractor.py.

kNN memorises all training examples and finds the k closest training
images (Euclidean distance) for each new image. The most common class
among those k neighbours wins the vote.

Best k is chosen via 5-fold cross-validation on odd values 1–19.
Results are saved to results/knn_results.pkl.
"""

import time
import pickle
import pathlib

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ── File paths ─────────────────────────────────────────────────────────────
FEATURE_VECTORS_PATH = (
    pathlib.Path(__file__).parent.parent / "features" / "feature_vectors.pkl"
)
RESULTS_PATH = (
    pathlib.Path(__file__).parent.parent / "results" / "knn_results.pkl"
)

# ── kNN settings ───────────────────────────────────────────────────────────
K_VALUES_TO_TEST = range(1, 20, 2)  # 1, 3, 5 … 19  (odd only → no ties)
CV_FOLDS         = 5


# ── Helper functions ───────────────────────────────────────────────────────

def load_feature_vectors():
    """
    Load the shared train/test split saved by extractor.py.

    All four classifiers (kNN, Bayesian, SVM, Neural Network) load from
    the same pickle — this guarantees a fair comparison with no
    information leakage between training and test data.
    """
    with open(FEATURE_VECTORS_PATH, "rb") as f:
        data = pickle.load(f)

    print(f"Loaded feature vectors from {FEATURE_VECTORS_PATH}")
    return (
        data["X_train"],
        data["X_test"],
        data["y_train"],
        data["y_test"],
        data["label_names"],
    )


def find_best_k(X_train, y_train):
    """
    Select the best k using 5-fold cross-validation.

    Only odd k values are tested to prevent majority-vote ties.
    For each k, the training data is split into 5 folds: 4 folds are
    used for training and 1 for validation, rotating each time.
    The k with the highest mean validation accuracy is returned.
    """
    print(f"Tuning k with {CV_FOLDS}-fold cross-validation ...")
    print(f"Testing k values: {list(K_VALUES_TO_TEST)}\n")

    best_k, best_score = 1, 0.0

    for k in K_VALUES_TO_TEST:
        model = KNeighborsClassifier(
            n_neighbors=k, metric="euclidean", n_jobs=-1
        )
        scores     = cross_val_score(
            model, X_train, y_train, cv=CV_FOLDS, scoring="accuracy"
        )
        mean_score = scores.mean()
        std_score  = scores.std()

        print(
            f"  k={k:2d}  mean accuracy = {mean_score:.4f}"
            f"  (std = {std_score:.4f})"
        )

        if mean_score > best_score:
            best_score = mean_score
            best_k     = k

    print(f"\nBest k = {best_k}  (CV accuracy = {best_score:.4f})")
    return best_k


def train_knn(X_train, y_train, best_k):
    """
    Fit the final kNN model using the best k.

    kNN does not build an explicit model — it stores all training
    examples. fit() is nearly instant; predict() is the expensive step
    as it searches for the nearest neighbours at query time.
    """
    model = KNeighborsClassifier(
        n_neighbors=best_k, metric="euclidean", n_jobs=-1
    )

    start      = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start

    print(f"Model fitted in {train_time:.4f}s  (k={best_k})")
    return model, train_time


def evaluate_model(model, X_test, y_test, label_names):
    """
    Evaluate on the held-out test set and return all metrics.

    Metrics collected:
      - Accuracy        : overall correct predictions
      - Macro F1        : average F1 across all 10 classes (unweighted)
                          — key metric for the comparative analysis
      - Per-class report: precision, recall, F1 per mammal class
      - Confusion matrix: shows which classes are confused with each other
    """
    start      = time.time()
    y_pred     = model.predict(X_test)
    infer_time = time.time() - start

    accuracy    = accuracy_score(y_test, y_pred)
    report_dict = classification_report(
        y_test, y_pred, target_names=label_names, output_dict=True
    )
    report_text = classification_report(
        y_test, y_pred, target_names=label_names
    )
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Extract Macro F1 explicitly — needed by compare.py for model ranking
    macro_f1 = report_dict["macro avg"]["f1-score"]

    print(f"\nTest accuracy  : {accuracy:.4f}")
    print(f"Macro F1       : {macro_f1:.4f}")
    print(f"Inference time : {infer_time:.4f}s")
    print("\nFull classification report:")
    print(report_text)

    return y_pred, accuracy, macro_f1, report_dict, conf_matrix, infer_time


def save_results(
    y_test, y_pred, accuracy, macro_f1,
    report, conf_matrix, label_names,
    best_k, train_time, infer_time,
):
    """
    Save all evaluation results to a pickle file for compare.py.

    macro_f1 is stored at the top level (not buried inside report)
    so compare.py can read it directly without re-parsing the report.
    """
    results = {
        "model_name"       : "KNN",
        "best_k"           : best_k,
        "y_test"           : y_test,
        "y_pred"           : y_pred,
        "accuracy"         : accuracy,
        "macro_f1"         : macro_f1,      # ← top-level for compare.py
        "report"           : report,
        "confusion_matrix" : conf_matrix,
        "label_names"      : label_names,
        "train_time"       : train_time,
        "infer_time"       : infer_time,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_PATH, "wb") as f:
        pickle.dump(results, f)

    print(f"Results saved to {RESULTS_PATH}")


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  kNN Classifier")
    print("=" * 60)

    # 1. Load shared feature vectors (same split used by all 4 models)
    X_train, X_test, y_train, y_test, label_names = load_feature_vectors()
    print(f"Training samples : {len(X_train)}")
    print(f"Test samples     : {len(X_test)}")
    print(f"Classes ({len(label_names)})     : {label_names}")

    # 2. Tune k via 5-fold cross-validation
    print()
    best_k = find_best_k(X_train, y_train)

    # 3. Train final model with best k
    print()
    trained_model, train_time = train_knn(X_train, y_train, best_k)

    # 4. Evaluate on held-out test set
    print("\nEvaluating on test set ...")
    y_pred, accuracy, macro_f1, report, conf_matrix, infer_time = (
        evaluate_model(trained_model, X_test, y_test, label_names)
    )

    # 5. Save all results for compare.py
    save_results(
        y_test, y_pred, accuracy, macro_f1,
        report, conf_matrix, label_names,
        best_k, train_time, infer_time,
    )

    print("\nkNN training and evaluation complete.")


if __name__ == "__main__":
    main()