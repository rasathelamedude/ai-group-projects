"""
compare.py

This file loads the saved results from all four classifiers and prints a
ranked comparison table so we can see at a glance which model performed best.

The table shows:
  - Accuracy   : percentage of test images correctly classified
  - Precision  : of everything we called "koala", how many really were koala?
  - Recall     : of all real koalas, how many did we correctly identify?
  - F1 Score   : harmonic mean of precision and recall — the best single number
                 to compare models when class sizes are unequal
  - Train time : seconds taken to fit the model
  - Infer time : seconds taken to classify the entire test set

All four metrics are macro-averaged, meaning we compute them per class and
then take the simple average across all 10 classes.  This treats a rare
class (like camel with 51 test images) the same as a common one (polar bear
with 71 test images).
"""

import pickle
import pathlib


# ── File paths ────────────────────────────────────────────────────────────────
RESULTS_DIR = pathlib.Path(__file__).parent.parent / "results"

# Map a human-readable name to the pkl file for each model.
RESULT_FILES = {
    "SVM"            : RESULTS_DIR / "svm_results.pkl",
    "Neural Network" : RESULTS_DIR / "nn_results.pkl",
    "Naive Bayes"    : RESULTS_DIR / "bayesian_results.pkl",
    "kNN"            : RESULTS_DIR / "knn_results.pkl",
}


# ── Helper functions ──────────────────────────────────────────────────────────

def load_all_results():
    """
    Load every result pickle file that exists in the results folder.

    If a model has not been trained yet its file will be missing — we just
    skip it and continue so a partially-run pipeline still shows useful output.
    """
    all_results = {}

    for model_name, file_path in RESULT_FILES.items():
        if file_path.exists():
            with open(file_path, "rb") as f:
                all_results[model_name] = pickle.load(f)
            print(f"  Loaded: {file_path.name}")
        else:
            print(f"  Missing: {file_path.name}  (run the classifier first)")

    return all_results


def get_metrics_for_model(result):
    """
    Pull the key performance numbers out of one result dictionary.

    We use the macro-averaged values from the classification report so
    every animal class contributes equally to the summary numbers regardless
    of how many test images it has.
    """
    report = result["report"]

    accuracy   = result["accuracy"]
    precision  = report["macro avg"]["precision"]
    recall     = report["macro avg"]["recall"]
    f1_score   = report["macro avg"]["f1-score"]
    train_time = result["train_time"]
    infer_time = result["infer_time"]

    return accuracy, precision, recall, f1_score, train_time, infer_time


def print_comparison_table(all_results):
    """
    Print a neatly formatted table of all models sorted from best to worst
    accuracy, and return the name of the best-performing model.
    """
    # Sort models by accuracy from highest to lowest.
    sorted_models = sorted(
        all_results.items(),
        key=lambda item: item[1]["accuracy"],
        reverse=True
    )

    # Print the header row.
    header = (
        f"{'Rank':<6} {'Model':<20} {'Accuracy':>10} {'Precision':>10} "
        f"{'Recall':>10} {'F1 Score':>10} {'Train(s)':>10} {'Infer(s)':>10}"
    )
    separator = "-" * len(header)

    print()
    print(separator)
    print(header)
    print(separator)

    # Print one row per model.
    for rank, (model_name, result) in enumerate(sorted_models, start=1):
        accuracy, precision, recall, f1, train_time, infer_time = get_metrics_for_model(result)

        print(
            f"{rank:<6} {model_name:<20} {accuracy:>10.4f} {precision:>10.4f} "
            f"{recall:>10.4f} {f1:>10.4f} {train_time:>10.2f} {infer_time:>10.4f}"
        )

    print(separator)

    # The first item in sorted_models is the winner.
    best_name   = sorted_models[0][0]
    best_result = sorted_models[0][1]
    best_acc    = best_result["accuracy"]

    print(f"\nBest model: {best_name}  (accuracy = {best_acc:.4f} = {best_acc*100:.2f}%)")

    return best_name, sorted_models


# ── Run the comparison ────────────────────────────────────────────────────────
# This code runs automatically when you execute this file directly:
#   python analysis/compare.py

print("=" * 60)
print("  Model Comparison")
print("=" * 60)

print("\nLoading results ...")
all_results = load_all_results()

if not all_results:
    print("\nNo results found.  Run all four classifiers first.")
else:
    best_model_name, sorted_results = print_comparison_table(all_results)

    print("\nComparison complete.")
