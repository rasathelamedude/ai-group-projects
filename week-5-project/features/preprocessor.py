"""
This file is used to normalize and clean up the data and transform it into a standard format that can be used by the clasification models.
"""

from skimage import io, color, transform
import pathlib
import os
import pickle

DATA_FOLDER_PATH = pathlib.Path(__file__).parent.parent / "data"
PREPROCESSED_DATA_PATH = pathlib.Path(__file__).parent / "preprocessed_data.pkl"


def fix_image_channels(image):
    """
    Some images in the dataset can have 2 channels (black and white) or 4 channels (RGBA).
    We want to convert all the images to have 3 channels (RGB) to make it easier for the model to learn.

    A gray image - shape (3, 3) - just brightness values looks like this:
        [[  0,  128, 255],
        [ 64,  192,  32],
        [100,   50, 200]]

    # RGB - shape (3, 3, 3) - [Red, Green, Blue] per pixel
        [[[255,   0,   0],   [0, 255,   0],   [0,   0, 255]],
        [[255, 255,   0],   [0, 255, 255],   [255, 0, 255]],
        [[128, 128, 128],   [0,   0,   0],   [255,255,255]]]

    # RGBA - shape (3, 3, 4) - [Red, Green, Blue, Alpha] per pixel
        [[[255,   0,   0, 255],   [0, 255,   0, 128],   [0,   0, 255,   0]],
        [[255, 255,   0, 255],   [0, 255, 255, 255],   [255, 0, 255, 100]],
        [[128, 128, 128, 255],   [0,   0,   0, 255],   [255,255,255, 255]]]
    """

    if image.ndim == 2:  # Gray image
        image = color.gray2rgb(image)

    if image.shape[2] == 4:  # RGBA image
        image = image[:, :, :3]  # Keep only the RGB channels

    return image


def load_images(data_folder: str) -> tuple:
    """Load all the images and labels from the data folder."""
    images = []
    labels = []

    # for each folder in the data/ folder
    for folder in os.listdir(data_folder):
        folder_path = os.path.join(data_folder, str(folder))

        # for each image in that folder
        for image_file in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_file)
            image = io.imread(image_path)
            images.append(image)
            labels.append(folder)

    print(f"Loaded {len(images)} images.")
    return images, labels


def resize_image(image):
    """The images in the dataset have different sizes, but we want to have a standard size for all the images to make it easier for the model to learn. We will resize all the images to 64x64 pixels."""

    resized_image = transform.resize(image, (64, 64))

    return resized_image


def normalize_pixel_values(image):
    """
    Each image's pixlel values are between 0-255

    For more stable and easier calculations, we want to normalize the pixel values to be between 0 and 1.
    Where 0 means the pixel is black and 1 means the pixel is white.
    """

    return image / 255.0


def save_preprocessed_data(images, labels):
    """Save the preprocessed images and labels to a file for the extractor to use later."""

    if os.path.exists(PREPROCESSED_DATA_PATH):
        os.remove(PREPROCESSED_DATA_PATH)

    with open(PREPROCESSED_DATA_PATH, "wb") as f:
        pickle.dump({"images": images, "labels": labels}, f)

    print(
        f"Saved {len(images)} preprocessed images and labels to {PREPROCESSED_DATA_PATH}"
    )


# 1. Load the images
images, labels = load_images(DATA_FOLDER_PATH)

# 2. Fix channels, resize and normalize pixel values
images = [fix_image_channels(image) for image in images]
images = [resize_image(image) for image in images]
images = [normalize_pixel_values(image) for image in images]
print("Finished preprocessing the images. Saving...")

# 3. Save the preprocessed images
save_preprocessed_data(images, labels)
