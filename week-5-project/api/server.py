"""
api/server.py — FastAPI backend for MammalNet

Serves:
  GET  /api/results  — evaluation metrics from the 4 trained classifiers
  GET  /api/dataset  — dataset statistics
  POST /api/predict  — live prediction on an uploaded image

PREDICTION PIPELINE (matches training exactly):
  1. Uploaded image → PIL resize to 64×64 → numpy float [0,1]
  2. feature_utils.extract_features_from_image()  — same RGB hist + HOG as extractor.py
  3. scaler.transform(features)  — apply the StandardScaler saved in vector_features.pkl
       extractor.py fit this scaler on X_train and saved it alongside the features.
       Using the same scaler ensures identical scaling between training and prediction.
  4. Load saved trained pipeline from results/<model>_results.pkl["model"]
       The pipeline contains PCA → classifier (no internal scaler — already applied above)
  5. pipeline.predict_proba(scaled_features) → class probabilities
  6. Decode class index to real animal name (required for Neural Network)
  7. Return predictions with real class names like "horse", "zebra", etc.
"""

import io
import sys
import pathlib
import pickle

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add features/ to path so we can import feature_utils
BASE_DIR     = pathlib.Path(__file__).resolve().parent.parent
FEATURES_DIR = BASE_DIR / "features"
if str(FEATURES_DIR) not in sys.path:
    sys.path.insert(0, str(FEATURES_DIR))

from feature_utils import extract_features_from_image  # shared extraction function

RESULTS_DIR = BASE_DIR / "results"
WEB_DIST    = BASE_DIR / "web" / "dist"

# Model result filenames — these are the files written by the 4 classifier scripts
_MODEL_FILES = [
    ("knn",      "knn_results.pkl"),
    ("bayesian", "bayesian_results.pkl"),
    ("svm",      "svm_results.pkl"),
    ("nn",       "nn_results.pkl"),
]

app = FastAPI(title="MammalNet API", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory caches — loaded once on first request
_pipeline_cache: dict = {}
_scaler_cache:   dict = {}


def _load_scaler():
    """
    Load the StandardScaler saved by extractor.py inside vector_features.pkl.
    This scaler was fit on X_train.  Applying it to an uploaded image's features
    ensures exactly the same scaling as was used during training.
    """
    if "scaler" in _scaler_cache:
        return _scaler_cache["scaler"]

    features_pkl = BASE_DIR / "features" / "vector_features.pkl"
    if not features_pkl.exists():
        raise HTTPException(
            status_code=503,
            detail="vector_features.pkl not found — run:  python features/extractor.py",
        )
    with open(features_pkl, "rb") as f:
        d = pickle.load(f)

    scaler = d.get("scaler")
    if scaler is None:
        raise HTTPException(
            status_code=503,
            detail="Scaler not found in vector_features.pkl — re-run:  python features/extractor.py",
        )
    _scaler_cache["scaler"] = scaler
    return scaler


def _load_pipeline(model_id: str, fname: str):
    """
    Load the trained pipeline from results/<fname>.
    The pipeline contains PCA → classifier (no internal StandardScaler —
    scaling is handled separately via the scaler from vector_features.pkl).
    Returns (pipeline, label_names, label_encoder).
    """
    if model_id in _pipeline_cache:
        return _pipeline_cache[model_id]

    path = RESULTS_DIR / fname
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"{fname} not found — run:  python classifiers/{model_id}.py",
        )

    with open(path, "rb") as f:
        result = pickle.load(f)

    pipeline      = result["model"]                  # trained PCA → classifier
    label_names   = result["label_names"]            # e.g. ["brown_bear", "camel", ...]
    label_encoder = result.get("label_encoder")      # LabelEncoder for NN only

    _pipeline_cache[model_id] = (pipeline, label_names, label_encoder)
    return pipeline, label_names, label_encoder


def _predict_one_model(model_id, pipeline, label_names, label_encoder, feat_scaled):
    """
    Run prediction for one model and return a dict with class name, confidence,
    and per-class probability dict.

    feat_scaled : np.ndarray, shape (n_features,) — already scaled by the training scaler.
    """
    feat = feat_scaled.reshape(1, -1)  # pipeline expects shape (1, n_features)

    if hasattr(pipeline, "predict_proba"):
        proba_arr = pipeline.predict_proba(feat)[0]   # shape (n_classes,)

        # pipeline.classes_ gives the class labels the pipeline was trained on.
        # For SVM / kNN / Bayesian: these are string animal names.
        # For Neural Network: these are integers (from LabelEncoder).
        classes = pipeline.classes_

        if model_id == "nn" and label_encoder is not None:
            # Decode integer indices back to animal name strings
            proba_dict = {
                label_encoder.inverse_transform([int(c)])[0]: round(float(p), 4)
                for c, p in zip(classes, proba_arr)
            }
        else:
            proba_dict = {str(c): round(float(p), 4) for c, p in zip(classes, proba_arr)}

        top_class = max(proba_dict, key=proba_dict.get)
        confidence = proba_dict[top_class]

    else:
        # Fallback for models without predict_proba
        raw_pred = pipeline.predict(feat)[0]
        if model_id == "nn" and label_encoder is not None:
            top_class = label_encoder.inverse_transform([int(raw_pred)])[0]
        else:
            top_class = str(raw_pred)
        confidence = 1.0
        proba_dict = {lbl: (1.0 if lbl == top_class else 0.0) for lbl in label_names}

    return {
        "model"        : model_id,
        "class"        : top_class,         # real animal name — never a number
        "confidence"   : round(confidence, 4),
        "probabilities": proba_dict,
    }


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/api/results")
def get_results():
    """Return evaluation metrics for all trained models."""
    model_list = []
    for model_id, fname in _MODEL_FILES:
        path = RESULTS_DIR / fname
        if not path.exists():
            continue
        with open(path, "rb") as fh:
            r = pickle.load(fh)
        rpt         = r["report"]
        label_names = r["label_names"]
        model_list.append({
            "model"     : model_id,
            "accuracy"  : round(float(r["accuracy"]), 4),
            "precision" : round(float(rpt["macro avg"]["precision"]), 4),
            "recall"    : round(float(rpt["macro avg"]["recall"]), 4),
            "f1"        : round(float(rpt["macro avg"]["f1-score"]), 4),
            "train_time": round(float(r.get("train_time", 0)), 4),
            "infer_time": round(float(r.get("infer_time", 0)), 4),
            "confusion_matrix": np.array(r["confusion_matrix"]).tolist(),
            "label_names": label_names,
            "per_class": {
                lbl: {
                    "precision": round(float(rpt.get(lbl, {}).get("precision", 0)), 4),
                    "recall"   : round(float(rpt.get(lbl, {}).get("recall", 0)), 4),
                    "f1"       : round(float(rpt.get(lbl, {}).get("f1-score", 0)), 4),
                    "support"  : int(rpt.get(lbl, {}).get("support", 0)),
                }
                for lbl in label_names
            },
            "loss_curve"  : r.get("loss_curve"),
            "best_k"      : r.get("best_k"),
            "best_params" : r.get("best_params"),
            "architecture": list(r["architecture"]) if r.get("architecture") else None,
        })
    return {"models": model_list}


@app.get("/api/dataset")
def get_dataset():
    """Return dataset statistics from vector_features.pkl."""
    features_pkl = BASE_DIR / "features" / "vector_features.pkl"
    if not features_pkl.exists():
        return {}
    with open(features_pkl, "rb") as fh:
        d = pickle.load(fh)
    y_train     = list(d["y_train"])
    y_test      = list(d["y_test"])
    y_all       = y_train + y_test
    label_names = sorted(set(y_all))
    counts      = {lbl: y_all.count(lbl) for lbl in label_names}
    return {
        "label_names": label_names,
        "n_classes"  : len(label_names),
        "counts"     : counts,
        "n_train"    : len(y_train),
        "n_test"     : len(y_test),
        "total"      : len(y_all),
        "n_features" : int(np.array(d["X_train"]).shape[1]),
    }


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accept an uploaded image and return predictions from all 4 trained models.

    Steps:
      1. Decode uploaded bytes → PIL Image → 64×64 RGB numpy [0,1]
      2. Extract features using the SAME function used during training
      3. For each model: load saved pipeline → predict → decode to animal name
      4. Return real animal class names with confidence scores
    """
    # Step 1: decode and preprocess the image
    try:
        raw      = await file.read()
        pil_img  = Image.open(io.BytesIO(raw)).convert("RGB").resize((64, 64), Image.LANCZOS)
        img_arr  = np.array(pil_img, dtype=np.float32) / 255.0   # shape (64,64,3), [0,1]
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot read image file.")

    # Step 2: extract raw features — same RGB hist + HOG as extractor.py
    feat_raw = extract_features_from_image(img_arr)   # shape (~1860,), unscaled

    # Step 3: apply the same StandardScaler that was fit on training data
    scaler     = _load_scaler()
    feat_scaled = scaler.transform(feat_raw.reshape(1, -1))[0]  # shape (~1860,), scaled

    # Step 4: predict with each trained pipeline (PCA → model, no internal scaler)
    predictions = []
    label_names = []
    for model_id, fname in _MODEL_FILES:
        try:
            pipeline, names, le = _load_pipeline(model_id, fname)
        except HTTPException:
            predictions.append({
                "model": model_id, "class": "not trained",
                "confidence": 0.0, "probabilities": {},
            })
            continue

        pred = _predict_one_model(model_id, pipeline, names, le, feat_scaled)
        predictions.append(pred)
        if not label_names:
            label_names = names

    return {"predictions": predictions, "labels": label_names}


# ── Serve React build (production) ────────────────────────────────────────────
if WEB_DIST.exists():
    assets_dir = WEB_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        index = WEB_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(404, "React build not found — run npm run build in web/")
