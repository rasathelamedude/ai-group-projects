"""
knn.py

This file trains a k-Nearest Neighbors (kNN) classifier on the
feature vectors produced by extractor.py.

kNN works by memorising all training examples and then, for each new
image, finding the k training images whose feature vector is closest
(using Euclidean distance).  The most common class among those k
neighbours wins the vote.

The tricky part is choosing the right value of k:
  - Too small (k=1) : the model memorises noise, giving poor test accuracy
  - Too large (k=19): the model ignores local patterns and underfits

We find the best k by running 5-fold cross-validation on odd values
from 1 to 19 and picking the k that scores highest on average.

Results are saved to results/knn_results.pkl.
"""

import time
import pickle
import pathlib

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ── File paths ────────────────────────────────────────────────────────────────
FEATURE_VECTORS_PATH = pathlib.Path(__file__).parent.parent / "features" / "feature_vectors.pkl"
RESULTS_PATH         = pathlib.Path(__file__).parent.parent / "results"  / "knn_results.pkl"

# ── kNN settings ──────────────────────────────────────────────────────────────
# We only test odd values of k to avoid ties in the majority vote.
K_VALUES_TO_TEST = range(1, 20, 2)   # 1, 3, 5, 7, 9, 11, 13, 15, 17, 19
CV_FOLDS         = 5                  # 5-fold cross-validation


# ── Helper functions ──────────────────────────────────────────────────────────

def load_feature_vectors():
    """
    Load the train/test splits that extractor.py prepared.

    All four classifiers load from the same pickle so we always compare
    models trained on identical data with no information leakage.
    """
    with open(FEATURE_VECTORS_PATH, "rb") as f:
        data = pickle.load(f)

    print(f"Loaded feature vectors from {FEATURE_VECTORS_PATH}")
    return data["X_train"], data["X_test"], data["y_train"], data["y_test"], data["label_names"]


def find_best_k(X_train, y_train):
    """
    Try every odd value of k from 1 to 19 using 5-fold cross-validation
    and return the k that gives the highest average validation accuracy.

    Cross-validation works by splitting the training data into 5 equal
    parts (folds).  For each k, we train on 4 folds and validate on 1,
    rotating which fold is held out.  The average accuracy across all 5
    rotations gives a stable estimate of how well that k generalises.
    """
    print(f"Tuning k with {CV_FOLDS}-fold cross-validation ...")
    print(f"Testing k values: {list(K_VALUES_TO_TEST)}")
    print()

    best_k     = 1
    best_score = 0.0

    for k in K_VALUES_TO_TEST:
        model = KNeighborsClassifier(n_neighbors=k, metric="euclidean", n_jobs=-1)

        # cross_val_score returns one accuracy per fold; we take the mean.
        scores     = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring="accuracy")
        mean_score = scores.mean()
        std_score  = scores.std()

        print(f"  k={k:2d}  mean accuracy = {mean_score:.4f}  (std = {std_score:.4f})")

        if mean_score > best_score:
            best_score = mean_score
            best_k     = k

    print(f"\nBest k = {best_k}  (CV accuracy = {best_score:.4f})")
    return best_k


def train_knn(X_train, y_train, best_k):
    """
    Train the final kNN model using the best k we found during tuning.

    kNN does not really 'train' in the traditional sense — it just stores
    all the training examples.  The fit() call is almost instant; the
    expensive part is predict() which has to search for neighbours.
    """
    model = KNeighborsClassifier(n_neighbors=best_k, metric="euclidean", n_jobs=-1)

    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time

    print(f"Model fitted in {train_time:.4f}s  (k={best_k})")
    return model, train_time


def evaluate_model(model, X_test, y_test, label_names):
    """
    Run the trained model on the held-out test set and collect all metrics.

    Precision tells us: of everything predicted as koala, how many were
    really koala?  Recall tells us: of all real koalas, how many did we find?
    F1 is the harmonic mean of the two — it is the number to look at when
    precision and recall are both important.
    """
    start_time = time.time()
    y_pred     = model.predict(X_test)
    infer_time = time.time() - start_time

    accuracy    = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, target_names=label_names, output_dict=True)
    report_text = classification_report(y_test, y_pred, target_names=label_names)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print(f"\nTest accuracy  : {accuracy:.4f}")
    print(f"Inference time : {infer_time:.4f}s")
    print("\nFull classification report:")
    print(report_text)

    return y_pred, accuracy, report_dict, conf_matrix, infer_time


def save_results(y_test, y_pred, accuracy, report, conf_matrix,
                 label_names, best_k, train_time, infer_time):
    """
    Save all evaluation results to a pickle file.

    We include best_k so the analysis scripts can report which k value
    was selected during tuning.
    """
    results = {
        "model_name"       : "KNN",
        "best_k"           : best_k,
        "y_test"           : y_test,
        "y_pred"           : y_pred,
        "accuracy"         : accuracy,
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


# ── Run the kNN classifier ────────────────────────────────────────────────────
# This code runs automatically when you execute this file directly:
#   python classifiers/knn.py

print("=" * 60)
print("  kNN Classifier")
print("=" * 60)

# 1. Load the shared feature vectors
X_train, X_test, y_train, y_test, label_names = load_feature_vectors()
print(f"Training samples: {len(X_train)}   Test samples: {len(X_test)}")

# 2. Find the best k using cross-validation
print()
best_k = find_best_k(X_train, y_train)

# 3. Train the final kNN model with the best k
print()
trained_model, train_time = train_knn(X_train, y_train, best_k)

# 4. Evaluate on the test set
print("\nEvaluating on test set ...")
y_pred, accuracy, report, conf_matrix, infer_time = evaluate_model(
    trained_model, X_test, y_test, label_names
)

# 5. Save results to disk
save_results(y_test, y_pred, accuracy, report, conf_matrix,
             label_names, best_k, train_time, infer_time)

print("\nkNN training and evaluation complete.")
