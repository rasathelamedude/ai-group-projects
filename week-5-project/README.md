# Mammals Image Classification

A comparative study of four machine learning classifiers (Neural Network, kNN, Bayesian, SVM) on a 10-class mammal image dataset.

---

## Setup

1. Clone the repository
2. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/asaniczka/mammals-image-classification-dataset-45-animals)
3. Place the downloaded folders inside the `data/` directory
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run feature extraction first before anything else:
   ```bash
   python features/extractor.py
   ```
6. Run the full pipeline:
   ```bash
   python main.py
   ```

> **Note:** The `data/` folder is not included in this repository. You must download it manually from Kaggle.

---

## Folder Structure

```
mammals_classification/
│
├── data/                          # Raw dataset from Kaggle (NOT in git)
│   ├── lion/
│   ├── elephant/
│   ├── tiger/
│   └── ...                        # One folder per animal class
│
├── features/                      # Member 1 — Feature extraction
│   ├── extractor.py               # Extracts HOG, color histograms, etc. from images
│   ├── preprocessor.py            # Resizes and normalizes images before extraction
│   └── feature_vectors.pkl        # Saved feature output — loaded by all classifiers
│
├── classifiers/                   # Classifier implementations
│   ├── knn.py                     # Member 2 — k-Nearest Neighbors classifier
│   ├── bayesian.py                # Member 3 — Naive Bayes classifier
│   ├── svm.py                     # Member 4 — Support Vector Machine classifier
│   └── neural_network.py          # Member 5 — Neural Network classifier
│
├── analysis/                      # Member 6 — Comparative analysis
│   ├── compare.py                 # Loads all results and compares accuracy across models
│   └── report.py                  # Generates charts, confusion matrices, and final report
│
├── results/                       # Shared output folder (auto-generated)
│   ├── knn_results.pkl
│   ├── bayesian_results.pkl
│   ├── svm_results.pkl
│   └── nn_results.pkl
│
└── main.py                        # Entry point — runs the full pipeline in order
```

---

## How It Works

The program runs as a pipeline:

```
Images → Feature Extraction → Feature Vectors → 4 Classifiers → Compare Results
```

**Feature extraction runs first.** Member 1's extractor processes every image and saves a compact numerical representation of each one to `feature_vectors.pkl`. All four classifiers load from this file, ensuring every model is tested on identical data which makes the final comparison valid.

---

## Team Members

| Member   | Role                               | File(s)                                             |
| -------- | ---------------------------------- | --------------------------------------------------- |
| Member 1 | Feature Extraction & Preprocessing | `features/extractor.py`, `features/preprocessor.py` |
| Member 2 | kNN Classifier                     | `classifiers/knn.py`                                |
| Member 3 | Bayesian Classifier                | `classifiers/bayesian.py`                           |
| Member 4 | SVM Classifier                     | `classifiers/svm.py`                                |
| Member 5 | Neural Network Classifier          | `classifiers/neural_network.py`                     |
| Member 6 | Comparative Analysis & Report      | `analysis/compare.py`, `analysis/report.py`         |

---
