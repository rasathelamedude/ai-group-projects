"""
Trains a k-Nearest Neighbors (kNN) classifier on the feature vectors from extractor.py.

kNN memorizes all training examples and classifies new images by finding the k closest
training images using Euclidean distance. The majority class among those k neighbors wins.
Best k is chosen via 5-fold cross-validation on odd values 1-19.
"""

import time
import pickle
import pathlib

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

VECTORIZED_FEATURES_PATH = pathlib.Path(__file__).parent.parent / "features" / "vector_features.pkl"
RESULTS_PATH             = pathlib.Path(__file__).parent.parent / "results"  / "knn_results.pkl"

K_VALUES_TO_TEST = range(1, 20, 2)  # odd values 1-19 to avoid majority-vote ties
CV_FOLDS         = 5


def load_features():
    """Load the train/test split saved by extractor.py."""
    with open(VECTORIZED_FEATURES_PATH, "rb") as f:
        data = pickle.load(f)

    print(f"Loaded features from {VECTORIZED_FEATURES_PATH}")
    return data["X_train"], data["X_test"], data["y_train"], data["y_test"]


def find_best_k(X_train, y_train):
    """
    Test odd k values 1-19 with 5-fold CV and return the k with the highest mean accuracy.
    StandardScaler is inside the pipeline so it is re-fitted inside each CV fold —
    this prevents the validation slice from leaking into the scaler.
    """
    print(f"Tuning k with {CV_FOLDS}-fold CV over values: {list(K_VALUES_TO_TEST)}")

    best_k, best_score = 1, 0.0

    for k in K_VALUES_TO_TEST:
        pipeline = make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=k, metric="euclidean", n_jobs=-1),
        )
        scores     = cross_val_score(pipeline, X_train, y_train, cv=CV_FOLDS, scoring="accuracy")
        mean_score = scores.mean()
        print(f"  k={k:2d}  mean accuracy = {mean_score:.4f}  (std = {scores.std():.4f})")

        if mean_score > best_score:
            best_score = mean_score
            best_k     = k

    print(f"Best k = {best_k}  (CV accuracy = {best_score:.4f})")
    return best_k


def train_knn(X_train, y_train, best_k):
    """
    Fit the final pipeline on all training data using the best k.
    StandardScaler is fitted here on the full X_train.
    """
    pipeline = make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=best_k, metric="euclidean", n_jobs=-1),
    )
    start = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"Pipeline fitted in {train_time:.4f}s  (k={best_k})")
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


def save_results(pipeline, y_test, y_pred, accuracy, report, conf_matrix, label_names, best_k, train_time, infer_time):
    """Save all evaluation results so compare.py can load and compare all four models."""
    results = {
        "model_name"      : "KNN",
        "model"           : pipeline,
        "best_k"          : best_k,
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

    # 2. Tune k via cross-validation (scaling is done correctly inside each fold)
    best_k = find_best_k(X_train, y_train)

    # 3. Train the final pipeline with best k on all training data
    pipeline, train_time = train_knn(X_train, y_train, best_k)

    # 4. Evaluate on the test set
    y_pred, accuracy, report, conf_matrix, infer_time = evaluate_model(
        pipeline, X_test, y_test, label_names
    )

    # 5. Save results (includes the fitted pipeline for live prediction)
    save_results(
        pipeline, y_test, y_pred, accuracy, report,
        conf_matrix, label_names, best_k, train_time, infer_time,
    )

    print("kNN training and evaluation complete.")


if __name__ == "__main__":
    main()
