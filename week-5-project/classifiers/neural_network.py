"""
classifiers/neural_network.py — Multi-Layer Perceptron (MLP) neural network

IMPORTANT: This is NOT a CNN.
This is an MLPClassifier trained on extracted feature vectors (HOG + HSV histogram).
It does not process raw pixel images.  It learns weighted combinations of the
~1892-dimensional feature vectors through three hidden layers.

HOW THE MLP WORKS FOR THIS PROJECT:
  Each hidden layer learns increasingly abstract combinations of the input
  features.  With 10 classes and ~800 training samples, the architecture
  (512 → 256 → 128) is large enough to capture complexity but not so large
  that it immediately overfits.

  - StandardScaler normalises the feature vector so no feature dominates the
    gradient updates during training.
  - PCA(200) compresses the ~1892-dim input to 200 principal components.
    This removes noise and reduces training time significantly.
  - Adam optimiser adapts the learning rate automatically per parameter.
  - Early stopping monitors a 10% validation split and halts training if
    accuracy does not improve for 20 consecutive iterations — prevents overfit.
  - alpha=0.0001 is L2 regularisation (weight decay) — penalises very large
    weights to improve generalisation.

LABEL ENCODING:
  MLPClassifier requires numeric targets.  LabelEncoder converts string class
  names (e.g. "zebra") to integers (e.g. 8).  The fitted LabelEncoder is saved
  alongside the model so that server.py can decode integer predictions back to
  real animal names.

PIPELINE: StandardScaler → PCA(200) → MLPClassifier(512→256→128→10)
"""

import time
import pickle
import pathlib
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = pathlib.Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "features" / "vector_features.pkl"
RESULTS_PATH  = BASE_DIR / "results"  / "nn_results.pkl"

ARCHITECTURE = (512, 256, 128)


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


def encode_labels(y_train, y_test):
    """
    MLPClassifier requires numeric targets.  LabelEncoder maps each unique
    class name to an integer (sorted alphabetically):
      brown_bear → 0, camel → 1, dolphin → 2, ..., zebra → 9

    The fitted encoder is returned so predictions can be decoded back to
    the original animal names.
    """
    le          = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc  = le.transform(y_test)
    return y_train_enc, y_test_enc, le


def build_model(n_classes):
    """Build the PCA → MLP pipeline. No StandardScaler — extractor.py already scaled."""
    print(f"Architecture: input(~1860) → PCA(200) → {ARCHITECTURE} → {n_classes} classes")
    return make_pipeline(
        PCA(n_components=200, random_state=42),
        MLPClassifier(
            hidden_layer_sizes  = ARCHITECTURE,
            activation          = "relu",
            solver              = "adam",
            learning_rate_init  = 0.001,
            alpha               = 0.0001,       # L2 regularisation
            max_iter            = 500,
            early_stopping      = True,
            validation_fraction = 0.1,          # 10% of train used for early stop
            n_iter_no_change    = 20,            # stop if no improvement for 20 iter
            random_state        = 42,
            verbose             = False,
        ),
    )


def train_model(pipeline, X_train, y_train_enc):
    """Fit the pipeline on the full training set."""
    t0 = time.time()
    pipeline.fit(X_train, y_train_enc)
    elapsed = time.time() - t0
    mlp = pipeline.named_steps["mlpclassifier"]
    print(f"Stopped at iteration {mlp.n_iter_}  |  "
          f"final loss = {mlp.loss_:.6f}  |  time = {elapsed:.2f}s")
    return pipeline, elapsed


def evaluate_model(pipeline, X_test, y_test_enc, le, label_names):
    """
    Predict on the test set, decode integer predictions back to animal names,
    and compute all metrics.
    """
    t0          = time.time()
    y_pred_enc  = pipeline.predict(X_test)
    infer_t     = time.time() - t0

    # Decode integers back to animal name strings
    y_pred = le.inverse_transform(y_pred_enc)
    y_test = le.inverse_transform(y_test_enc)

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
    return y_pred, y_test, acc, report_dict, cm, infer_t


def save_model(pipeline, le, y_test, y_pred, acc, report, cm,
               label_names, train_t, infer_t):
    """
    Save the trained pipeline and all evaluation metrics to results/.

    IMPORTANT: The LabelEncoder is saved under 'label_encoder' so that
    api/server.py can decode integer predictions back to real animal names.
    Without this, the server would show "0", "1", "2" instead of "zebra" etc.
    """
    mlp = pipeline.named_steps["mlpclassifier"]
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name"      : "Neural Network (MLP)",
        "model"           : pipeline,       # full trained pipeline (Scaler+PCA+MLP)
        "label_names"     : label_names,    # class names from data/ folders
        "label_encoder"   : le,             # REQUIRED for decoding NN integer outputs
        "architecture"    : ARCHITECTURE,
        "n_iterations"    : mlp.n_iter_,
        "loss_curve"      : mlp.loss_curve_,
        "y_test"          : y_test,         # string labels for compare.py
        "y_pred"          : y_pred,         # string labels for compare.py
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

    # 2. Encode string labels to integers (MLP requirement)
    y_train_enc, y_test_enc, le = encode_labels(y_train, y_test)

    # 3. Build and train
    pipeline = build_model(len(label_names))
    pipeline, train_t = train_model(pipeline, X_train, y_train_enc)

    # 4. Evaluate — decode back to animal names for the report
    y_pred, y_test_str, acc, report, cm, infer_t = evaluate_model(
        pipeline, X_test, y_test_enc, le, label_names
    )

    # 5. Save — include LabelEncoder so server.py can decode predictions
    save_model(pipeline, le, y_test_str, y_pred, acc, report, cm,
               label_names, train_t, infer_t)
    print("Neural network training complete.")


if __name__ == "__main__":
    main()
