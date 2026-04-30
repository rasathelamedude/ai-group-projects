"""
Trains a Gaussian Naive Bayes classifier on the feature vectors from extractor.py.

Naive Bayes assumes all features are independent given the class label. Despite this
simplification it trains in milliseconds and serves as a fast, interpretable baseline.
"""

import time
import pickle
import pathlib

from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

VECTORIZED_FEATURES_PATH = pathlib.Path(__file__).parent.parent / "features" / "vector_features.pkl"
RESULTS_PATH             = pathlib.Path(__file__).parent.parent / "results"  / "bayesian_results.pkl"


def load_features():
    """Load the train/test split saved by extractor.py."""
    with open(VECTORIZED_FEATURES_PATH, "rb") as f:
        data = pickle.load(f)

    print(f"Loaded features from {VECTORIZED_FEATURES_PATH}")
    return data["X_train"], data["X_test"], data["y_train"], data["y_test"]


def train_bayesian(X_train, y_train):
    """
    Fit a pipeline of StandardScaler + GaussianNB.
    GaussianNB just computes per-class mean and variance — no gradient descent needed.
    """
    pipeline = make_pipeline(StandardScaler(), GaussianNB())
    start = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - start
    n_classes = len(pipeline.named_steps["gaussiannb"].classes_)
    print(f"Pipeline fitted in {train_time:.4f}s  ({n_classes} classes)")
    return pipeline, train_time


def evaluate_model(pipeline, X_test, y_test, label_names):
    """Run the pipeline on the held-out test set and collect accuracy, report, and confusion matrix."""
    start = time.time()
    y_pred     = pipeline.predict(X_test)
    infer_time = time.time() - start

    accuracy    = accuracy_score(y_test, y_pred)
    report_dict = classification_report(
        y_test, y_pred,
        labels=label_names, target_names=label_names,
        output_dict=True, zero_division=0,
    )
    report_text = classification_report(
        y_test, y_pred,
        labels=label_names, target_names=label_names,
        zero_division=0,
    )
    conf_matrix = confusion_matrix(y_test, y_pred, labels=label_names)

    print(f"Test accuracy  : {accuracy:.4f}")
    print(f"Inference time : {infer_time:.4f}s")
    print(report_text)
    return y_pred, accuracy, report_dict, conf_matrix, infer_time


def save_results(pipeline, y_test, y_pred, accuracy, report, conf_matrix, label_names, train_time, infer_time):
    """Save all evaluation results so compare.py can load and compare all four models."""
    results = {
        "model_name"      : "Bayesian (GaussianNB)",
        "model"           : pipeline,
        "y_test"          : y_test,
        "y_pred"          : y_pred,
        "accuracy"        : accuracy,
        "report"          : report,
        "confusion_matrix": conf_matrix,
        "label_names"     : label_names,
        "train_time"      : train_time,
        "infer_time"      : infer_time,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_PATH, "wb") as f:
        pickle.dump(results, f)

    print(f"Saved results to {RESULTS_PATH}")


def main():
    # 1. Load features
    X_train, X_test, y_train, y_test = load_features()
    label_names = sorted(list(set(y_train)))
    print(f"Training samples: {len(X_train)}   Test samples: {len(X_test)}")
    print(f"Classes ({len(label_names)}): {label_names}")

    # 2. Train the pipeline (StandardScaler + GaussianNB)
    pipeline, train_time = train_bayesian(X_train, y_train)

    # 3. Evaluate on the test set
    y_pred, accuracy, report, conf_matrix, infer_time = evaluate_model(
        pipeline, X_test, y_test, label_names
    )

    # 4. Save results (includes the fitted pipeline for live prediction)
    save_results(
        pipeline, y_test, y_pred, accuracy, report,
        conf_matrix, label_names, train_time, infer_time,
    )

    print("Naive Bayes training and evaluation complete.")


if __name__ == "__main__":
    main()
