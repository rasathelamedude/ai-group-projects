import subprocess
import sys


def main():
    # 1. Preprocess the images and save them in a file
    print("Starting the image classification pipeline...")
    print("Step 1: Preprocessing images...")
    subprocess.run([sys.executable, "features/preprocessor.py"], check=True)

    # 2. Extract features from the preprocessed images and save them in a file
    print("Step 2: Extracting features...")
    subprocess.run([sys.executable, "features/extractor.py"], check=True)

    # 3. Train the classifiers in parallel and save their results in files
    print("Step 3: Training models...")
    model_scripts = [
        "classifiers/knn.py",
        "classifiers/svm.py",
        "classifiers/bayesian.py",
        "classifiers/neural_network.py",
    ]

    processes = [subprocess.Popen([sys.executable, script]) for script in model_scripts]

    for process in processes:
        process.wait()

    # 4. Run the compare method to find the best model
    print("Step 4: Comparing models...")
    subprocess.run([sys.executable, "analysis/compare.py"], check=True)

    # 5. Run the report method to visualize the results
    print("Step 5: Generating report...")
    subprocess.run([sys.executable, "analysis/report.py"], check=True)

    print("Pipeline Complete! Check the terminal and the 'results' folder.")


if __name__ == "__main__":
    main()
