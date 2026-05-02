import os
import pickle
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, f1_score
)


# ──────────────────────────────────────────────
#  Paths
# ──────────────────────────────────────────────

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
FEATURES_PATH   = os.path.join(BASE_DIR, "..", "features", "feature_vectors.pkl")
RESULTS_PATH    = os.path.join(BASE_DIR, "..", "results", "nn_results.pkl")


# ──────────────────────────────────────────────
#  Load Features
# ──────────────────────────────────────────────

def load_features(path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load pre-extracted feature vectors and labels from a pickle file.

    Expected format inside the .pkl:
        dict with keys 'features' (ndarray) and 'labels' (list or ndarray)

    Returns:
        X : feature matrix  (n_samples, n_features)
        y : label array     (n_samples,)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Feature file not found at:\n  {path}\n"
            "Make sure Member 1 has run extractor.py first."
        )

    with open(path, "rb") as f:
        data = pickle.load(f)

    X = np.array(data["features"])
    y = np.array(data["labels"])

    print(f"[INFO] Features loaded — {X.shape[0]} samples, {X.shape[1]} features each.")
    print(f"[INFO] Classes found : {sorted(set(y))}\n")
    return X, y


# ──────────────────────────────────────────────
#  Preprocessing
# ──────────────────────────────────────────────

def preprocess(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple:
    """
    Encode labels, scale features, and split into train/test sets.

    Neural networks are sensitive to feature scale, so StandardScaler
    (zero mean, unit variance) is applied after splitting to avoid
    data leakage from the test set.

    Returns:
        X_train, X_test, y_train, y_test, scaler, label_encoder
    """
    # Encode string labels → integers
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Stratified split keeps class proportions equal in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=test_size,
        random_state=random_state,
        stratify=y_encoded
    )

    # Fit scaler on training data only, then apply to both sets
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    print(f"[INFO] Train samples : {len(X_train)}")
    print(f"[INFO] Test  samples : {len(X_test)}\n")
    return X_train, X_test, y_train, y_test, scaler, le


# ──────────────────────────────────────────────
#  Build & Train Model
# ──────────────────────────────────────────────

def build_model() -> MLPClassifier:
    """
    Construct an MLP neural network with two hidden layers.

    Architecture
    ────────────
    Input → Dense(512, ReLU) → Dense(256, ReLU) → Softmax Output

    Hyperparameter choices
    ──────────────────────
    • adam          : adaptive learning rate, works well on large feature sets
    • alpha=1e-4    : L2 regularisation to reduce overfitting
    • max_iter=500  : enough epochs for convergence on tabular features
    • early_stopping: halt training when validation loss stops improving
    """
    model = MLPClassifier(
        hidden_layer_sizes=(512, 256),
        activation="relu",
        solver="adam",
        alpha=1e-4,              # L2 regularisation strength
        batch_size="auto",
        learning_rate="adaptive",
        max_iter=500,
        early_stopping=True,     # monitors a held-out validation set
        validation_fraction=0.1,
        n_iter_no_change=15,     # patience — stop if no improvement for 15 epochs
        random_state=42,
        verbose=False
    )
    return model


def train(model: MLPClassifier, X_train: np.ndarray, y_train: np.ndarray) -> MLPClassifier:
    """Fit the neural network on the training set."""
    print("[INFO] Training Neural Network — please wait ...")
    model.fit(X_train, y_train)
    print(f"[INFO] Training complete. Iterations run : {model.n_iter_}\n")
    return model


# ──────────────────────────────────────────────
#  Evaluation
# ──────────────────────────────────────────────

def evaluate(
    model: MLPClassifier,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    label_encoder: LabelEncoder
) -> dict:
    """
    Evaluate the trained model and collect all metrics into a dictionary
    that will be pickled and shared with Member 6 (analysis/compare.py).

    Metrics collected
    ─────────────────
    • train_accuracy        : accuracy on training split
    • test_accuracy         : accuracy on held-out test split
    • f1_macro              : macro-averaged F1 (treats all classes equally)
    • cv_scores             : 5-fold cross-validation accuracy scores
    • cv_mean / cv_std      : mean and standard deviation of CV scores
    • classification_report : per-class precision, recall, F1
    • confusion_matrix      : raw confusion matrix (ndarray)
    • class_names           : decoded class labels for plotting
    • predictions           : predicted labels on the test set
    • true_labels           : ground-truth labels on the test set
    """
    y_pred = model.predict(X_test)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc  = accuracy_score(y_test, y_pred)
    f1        = f1_score(y_test, y_pred, average="macro")
    cm        = confusion_matrix(y_test, y_pred)
    report    = classification_report(
                    y_test, y_pred,
                    target_names=label_encoder.classes_,
                    output_dict=True
                )

    # 5-fold cross-validation on the full dataset for a robust accuracy estimate
    cv        = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy")

    # ── Print summary ──────────────────────────────────
    print("=" * 55)
    print("  NEURAL NETWORK — EVALUATION RESULTS")
    print("=" * 55)
    print(f"  Train Accuracy      : {train_acc * 100:.2f}%")
    print(f"  Test  Accuracy      : {test_acc  * 100:.2f}%")
    print(f"  Macro F1-Score      : {f1        * 100:.2f}%")
    print(f"  CV Accuracy (5-fold): {cv_scores.mean() * 100:.2f}% ± {cv_scores.std() * 100:.2f}%")
    print("=" * 55)
    print("\n[INFO] Per-class Classification Report:\n")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    results = {
        "model_name"            : "Neural Network (MLP)",
        "train_accuracy"        : train_acc,
        "test_accuracy"         : test_acc,
        "f1_macro"              : f1,
        "cv_scores"             : cv_scores,
        "cv_mean"               : cv_scores.mean(),
        "cv_std"                : cv_scores.std(),
        "classification_report" : report,
        "confusion_matrix"      : cm,
        "class_names"           : list(label_encoder.classes_),
        "predictions"           : y_pred,
        "true_labels"           : y_test,
    }
    return results


# ──────────────────────────────────────────────
#  Save Results
# ──────────────────────────────────────────────

def save_results(results: dict, path: str) -> None:
    """Pickle the results dictionary so Member 6 can load it in compare.py."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(results, f)
    print(f"\n[INFO] Results saved → {path}")


# ──────────────────────────────────────────────
#  Main Entry Point
# ──────────────────────────────────────────────

def main() -> None:
    print("\n╔══════════════════════════════════════════════════╗")
    print("║   Mammals Classification — Neural Network (MLP)  ║")
    print("╚══════════════════════════════════════════════════╝\n")

    # 1. Load pre-extracted features (produced by Member 1)
    X, y = load_features(FEATURES_PATH)

    # 2. Preprocess: encode labels, scale, split
    X_train, X_test, y_train, y_test, scaler, le = preprocess(X, y)

    # 3. Build and train the model
    model = build_model()
    model = train(model, X_train, y_train)

    # 4. Evaluate and collect metrics
    results = evaluate(model, X_train, X_test, y_train, y_test, le)

    # 5. Save results for comparative analysis (Member 6)
    save_results(results, RESULTS_PATH)


if __name__ == "__main__":
    main()