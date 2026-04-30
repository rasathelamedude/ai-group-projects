"""
report.py

This file reads the saved results from all four classifiers and generates
four visualisation charts that make the results easy to understand at a glance.

Charts generated (saved to results/):
  1. accuracy_comparison.png   — bar chart showing test accuracy for each model
  2. metrics_comparison.png    — grouped bars for precision, recall and F1
  3. confusion_<model>.png     — one confusion matrix heatmap per classifier
  4. nn_loss_curve.png         — line chart showing how the MLP loss decreased
                                 during training (only for the neural network)

A confusion matrix is a grid where:
  - Rows = true animal class
  - Columns = what the model predicted
  - Diagonal cells = correct predictions (darker = more correct)
  - Off-diagonal cells = mistakes (e.g. row=kangaroo, col=giraffe means the
    model mistook a kangaroo for a giraffe)
"""

import pickle
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")   # use a non-interactive backend — no GUI window needed
import matplotlib.pyplot as plt


# ── File paths ────────────────────────────────────────────────────────────────
RESULTS_DIR = pathlib.Path(__file__).parent.parent / "results"

RESULT_FILES = {
    "SVM"            : RESULTS_DIR / "svm_results.pkl",
    "Neural Network" : RESULTS_DIR / "nn_results.pkl",
    "Naive Bayes"    : RESULTS_DIR / "bayesian_results.pkl",
    "kNN"            : RESULTS_DIR / "knn_results.pkl",
}

# Consistent colours for each model across all charts.
MODEL_COLORS = {
    "SVM"            : "#3d6b5e",
    "Neural Network" : "#c4622d",
    "Naive Bayes"    : "#5b7db1",
    "kNN"            : "#8a5ba8",
}


# ── Helper functions ──────────────────────────────────────────────────────────

def load_all_results():
    """
    Load every result pickle file that exists in the results folder.

    Returns a dictionary mapping model name to its result dict.
    """
    all_results = {}

    for model_name, file_path in RESULT_FILES.items():
        if file_path.exists():
            with open(file_path, "rb") as f:
                all_results[model_name] = pickle.load(f)
            print(f"  Loaded: {file_path.name}")
        else:
            print(f"  Missing: {file_path.name}")

    return all_results


def plot_accuracy_comparison(all_results):
    """
    Draw a bar chart comparing test accuracy across all four models.

    A bar chart makes it immediately obvious which model performs best.
    We add the exact accuracy value above each bar so the reader does not
    have to estimate from the axis.
    """
    # Sort models from best to worst accuracy for a cleaner presentation.
    sorted_models = sorted(all_results.items(), key=lambda x: x[1]["accuracy"], reverse=True)

    model_names = [name for name, _ in sorted_models]
    accuracies  = [result["accuracy"] for _, result in sorted_models]
    colors      = [MODEL_COLORS.get(name, "#888888") for name in model_names]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#f5f1eb")
    ax.set_facecolor("#f5f1eb")

    bars = ax.bar(model_names, accuracies, color=colors, width=0.55, edgecolor="white", zorder=3)

    # Add the exact accuracy value on top of each bar.
    for bar, acc in zip(bars, accuracies):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.008,
            f"{acc*100:.2f}%",
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    # A dashed line at 10% shows the random-chance baseline for 10 classes.
    ax.axhline(0.10, color="#999", linestyle="--", linewidth=1.2, label="Random baseline (10%)", zorder=2)
    ax.legend(fontsize=10)

    ax.set_ylim(0, 0.65)
    ax.set_ylabel("Test Accuracy", fontsize=12)
    ax.set_title("Model Accuracy Comparison", fontsize=14, fontweight="bold", pad=12)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    output_path = RESULTS_DIR / "accuracy_comparison.png"
    fig.savefig(output_path, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved: {output_path.name}")


def plot_metrics_comparison(all_results):
    """
    Draw a grouped bar chart showing precision, recall and F1 side by side
    for each model.

    Grouped bars let the reader compare all three metrics for one model at
    a glance AND compare the same metric across models.  We use the macro
    average which weights every class equally regardless of size.
    """
    sorted_models = sorted(all_results.items(), key=lambda x: x[1]["accuracy"], reverse=True)
    model_names   = [name for name, _ in sorted_models]

    # Pull macro-averaged precision, recall and F1 from the report dict.
    precisions = [r["report"]["macro avg"]["precision"] for _, r in sorted_models]
    recalls    = [r["report"]["macro avg"]["recall"]    for _, r in sorted_models]
    f1_scores  = [r["report"]["macro avg"]["f1-score"]  for _, r in sorted_models]

    x     = np.arange(len(model_names))
    width = 0.25   # width of each individual bar

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#f5f1eb")
    ax.set_facecolor("#f5f1eb")

    ax.bar(x - width,  precisions, width, label="Precision", color="#5b7db1", edgecolor="white")
    ax.bar(x,          recalls,    width, label="Recall",    color="#3d6b5e", edgecolor="white")
    ax.bar(x + width,  f1_scores,  width, label="F1 Score",  color="#c4622d", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.set_ylim(0, 0.70)
    ax.set_ylabel("Score (macro average)", fontsize=12)
    ax.set_title("Precision / Recall / F1 Comparison", fontsize=14, fontweight="bold", pad=12)
    ax.legend()
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    output_path = RESULTS_DIR / "metrics_comparison.png"
    fig.savefig(output_path, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved: {output_path.name}")


def plot_confusion_matrix(model_name, result):
    """
    Draw a heatmap confusion matrix for one model.

    We row-normalise the matrix (divide each row by the row total) so the
    colour shows what fraction of each true class was predicted correctly or
    incorrectly, rather than raw counts which are harder to compare when
    class sizes differ.

    We still print the raw count inside each cell for exact reference.
    """
    conf_matrix  = np.array(result["confusion_matrix"])
    label_names  = result["label_names"]
    n_classes    = len(label_names)
    accuracy     = result["accuracy"]

    # Row-normalise so each row sums to 1.0.
    row_totals   = conf_matrix.sum(axis=1, keepdims=True)
    norm_matrix  = conf_matrix / row_totals   # fraction of each true class

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#f5f1eb")

    # Blues colourmap — darker blue means more predictions in that cell.
    image = ax.imshow(norm_matrix, cmap="Blues", vmin=0, vmax=1)
    plt.colorbar(image, ax=ax, fraction=0.04, pad=0.04, label="Row-normalised proportion")

    # Print the raw count inside each cell.
    for row in range(n_classes):
        for col in range(n_classes):
            count    = conf_matrix[row, col]
            fraction = norm_matrix[row, col]
            # Use white text on dark cells, dark text on light cells.
            text_color = "white" if fraction > 0.55 else "#111"
            ax.text(col, row, str(count), ha="center", va="center",
                    fontsize=8.5, color=text_color, fontweight="bold")

    # Add axis labels using the actual class names.
    ax.set_xticks(range(n_classes))
    ax.set_yticks(range(n_classes))
    display_names = [name.replace("_", " ").title() for name in label_names]
    ax.set_xticklabels(display_names, rotation=40, ha="right", fontsize=9)
    ax.set_yticklabels(display_names, fontsize=9)

    ax.set_xlabel("Predicted label", fontsize=11)
    ax.set_ylabel("True label", fontsize=11)
    ax.set_title(f"{model_name} — Confusion Matrix  (acc = {accuracy*100:.2f}%)",
                 fontsize=13, fontweight="bold", pad=12)

    fig.tight_layout()

    # Build the filename from the model name e.g. "Neural Network" -> confusion_neural_network.png
    safe_name   = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    output_path = RESULTS_DIR / f"confusion_{safe_name}.png"
    fig.savefig(output_path, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved: {output_path.name}")


def plot_nn_loss_curve(all_results):
    """
    Draw the training loss curve for the Neural Network model.

    The loss curve shows how the error decreased over each training iteration.
    A smooth downward curve means the network learnt steadily.  If the curve
    flattens early it means the network hit early stopping.  A loss that does
    not decrease much means the network struggled to learn from the features.
    """
    # Find the neural network result — its key contains "Neural".
    nn_result = None
    for name, result in all_results.items():
        if "Neural" in name:
            nn_result = result
            break

    if nn_result is None:
        print("  Neural Network result not found — skipping loss curve.")
        return

    loss_curve  = nn_result.get("loss_curve", [])
    n_iter      = nn_result.get("n_iterations", len(loss_curve))

    if not loss_curve:
        print("  No loss curve data found — skipping.")
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#f5f1eb")
    ax.set_facecolor("#f5f1eb")

    iterations = list(range(1, len(loss_curve) + 1))
    ax.fill_between(iterations, loss_curve, alpha=0.15, color="#3d6b5e")
    ax.plot(iterations, loss_curve, color="#3d6b5e", linewidth=2.5)

    # Annotate start and end loss values.
    ax.annotate(f"Start: {loss_curve[0]:.4f}", xy=(1, loss_curve[0]),
                xytext=(5, 5), textcoords="offset points", fontsize=10)
    ax.annotate(f"End: {loss_curve[-1]:.4f}", xy=(len(loss_curve), loss_curve[-1]),
                xytext=(-60, 10), textcoords="offset points", fontsize=10)

    ax.set_xlabel("Training Iteration", fontsize=12)
    ax.set_ylabel("Training Loss", fontsize=12)
    ax.set_title(f"Neural Network — Training Loss Curve  ({n_iter} iterations)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    output_path = RESULTS_DIR / "nn_loss_curve.png"
    fig.savefig(output_path, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved: {output_path.name}")


# ── Run the report generation ─────────────────────────────────────────────────
# This code runs automatically when you execute this file directly:
#   python analysis/report.py

print("=" * 60)
print("  Generating Performance Report")
print("=" * 60)

print("\nLoading results ...")
all_results = load_all_results()

if not all_results:
    print("\nNo results found.  Run all four classifiers first.")
else:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\nGenerating accuracy comparison chart ...")
    plot_accuracy_comparison(all_results)

    print("\nGenerating precision/recall/F1 chart ...")
    plot_metrics_comparison(all_results)

    print("\nGenerating confusion matrices ...")
    for model_name, result in all_results.items():
        plot_confusion_matrix(model_name, result)

    print("\nGenerating neural network loss curve ...")
    plot_nn_loss_curve(all_results)

    print(f"\nAll charts saved to: {RESULTS_DIR}")
    print("\nReport generation complete.")
