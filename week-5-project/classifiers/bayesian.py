import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report
from skimage.feature import hog

# =====================
# CONFIGURATION
# =====================
DATASET_PATH = "Data"   
IMAGE_SIZE = (64, 64)

model = None
class_names = []
accuracy = 0
report = ""


# =====================
# FEATURE EXTRACTION
# =====================
def extract_features(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, IMAGE_SIZE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    features = hog(
        gray,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        visualize=False,
    )
    return features


# =====================
# LOAD DATASET
# =====================
def load_dataset():
    global class_names

    X = []
    y = []
    class_names = []

    for label, folder in enumerate(os.listdir(DATASET_PATH)):
        folder_path = os.path.join(DATASET_PATH, folder)

        if not os.path.isdir(folder_path):
            continue

        class_names.append(folder)

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                features = extract_features(file_path)
                X.append(features)
                y.append(label)
            except Exception:
                continue

    return np.array(X), np.array(y)


# =====================
# TRAIN MODEL
# =====================
def train_model():
    global model, accuracy, report

    try:
        status_label.config(text="Loading dataset and training...")
        root.update()

        X, y = load_dataset()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = GaussianNB()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(
            y_test,
            predictions,
            target_names=class_names,
            zero_division=0,
        )

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"Accuracy: {accuracy:.4f}\n\n")
        result_text.insert(tk.END, report)

        status_label.config(text="Training completed successfully.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# =====================
# TEST SINGLE IMAGE
# =====================
def predict_image():
    global model

    if model is None:
        messagebox.showwarning("Warning", "Train model first.")
        return

    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    features = extract_features(file_path).reshape(1, -1)
    prediction = model.predict(features)[0]
    predicted_class = class_names[prediction]

    messagebox.showinfo("Prediction", f"Predicted class: {predicted_class}")


 
