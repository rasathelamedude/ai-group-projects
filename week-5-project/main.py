"""
main.py

This is the main entry point for the Mammal Classification System.
Running this file executes the entire pipeline from start to finish:

  Step 1 — Preprocessing   : Load raw images, resize to 64x64, normalise to [0,1]
  Step 2 — Feature Extraction : HOG + colour histograms -> vector_features.pkl
  Step 3 — Train SVM        : Grid-search RBF SVM, evaluate, save results
  Step 4 — Train kNN        : CV-tune k, train kNN, evaluate, save results
  Step 5 — Train Neural Net : MLP 256->128->64 with early stopping, save results
  Step 6 — Train Naive Bayes: GaussianNB, evaluate, save results
  Step 7 — Compare Models   : Print ranked comparison table
  Step 8 — Generate Charts  : Accuracy bar, metrics bar, confusion matrices, loss curve

Each step saves its output to a .pkl file so that individual steps can be
re-run independently without repeating the earlier steps.

Usage
-----
Run the full pipeline:
    python main.py

Run a single step on its own:
    python features/preprocessor.py
    python features/extractor.py
    python classifiers/svm.py
    python classifiers/knn.py
    python classifiers/neural_network.py
    python classifiers/bayesian.py
    python analysis/compare.py
    python analysis/report.py
"""

import sys
import pathlib

# Add sub-folders to the path so we can import modules from them directly.
BASE_DIR = pathlib.Path(__file__).parent

for folder in ["features", "classifiers", "analysis"]:
    folder_path = str(BASE_DIR / folder)
    if folder_path not in sys.path:
        sys.path.insert(0, folder_path)


# ── Step runner ───────────────────────────────────────────────────────────────

def run_step(step_number, step_name, module_path):
    """
    Print a section header and execute one pipeline step by running
    the target Python file as a script using runpy.

    runpy.run_path is the standard way to execute a .py file from within
    another Python script — it is the same as running it from the terminal.
    """
    import runpy

    print()
    print("=" * 60)
    print(f"  STEP {step_number} — {step_name}")
    print("=" * 60)

    runpy.run_path(str(module_path), run_name="__main__")


# ── Pipeline steps ─────────────────────────────────────────────────────────────

PREPROCESSED_DATA = BASE_DIR / "features" / "preprocessed_data.pkl"
FEATURE_VECTORS   = BASE_DIR / "features" / "vector_features.pkl"

print()
print("=" * 60)
print("  Mammal Classification System")
print("  Running the full pipeline")
print("=" * 60)
print(f"\n  Project folder : {BASE_DIR}")

# Step 1 — Preprocessing
# Only re-run if the output file does not exist yet, to save time.
if not PREPROCESSED_DATA.exists():
    run_step(1, "Preprocessing images", BASE_DIR / "features" / "preprocessor.py")
else:
    print(f"\n[SKIP] Step 1 — preprocessed_data.pkl already exists")

# Step 2 — Feature Extraction
# Only re-run if feature vectors have not been built yet.
if not FEATURE_VECTORS.exists():
    run_step(2, "Extracting features (HOG + colour histogram)", BASE_DIR / "features" / "extractor.py")
else:
    print(f"[SKIP] Step 2 — vector_features.pkl already exists")

# Steps 3-6 — Train all four classifiers
# Each classifier saves its results to results/<name>_results.pkl.
# We always re-train the classifiers when main.py is run so results are fresh.
run_step(3, "Training SVM",          BASE_DIR / "classifiers" / "svm.py")
run_step(4, "Training kNN",          BASE_DIR / "classifiers" / "knn.py")
run_step(5, "Training Neural Network", BASE_DIR / "classifiers" / "neural_network.py")
run_step(6, "Training Naive Bayes",  BASE_DIR / "classifiers" / "bayesian.py")

# Step 7 — Compare all models
run_step(7, "Comparing models",      BASE_DIR / "analysis" / "compare.py")

# Step 8 — Generate charts and visualisations
run_step(8, "Generating report charts", BASE_DIR / "analysis" / "report.py")

print()
print("=" * 60)
print("  Pipeline complete!")
print(f"  Results saved to: {BASE_DIR / 'results'}")
print("=" * 60)
print()
