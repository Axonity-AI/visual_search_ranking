"""
Dataset Shortening Script

Creates a smaller dataset by randomly sampling images from each category.
Useful for quick testing and development.
"""

import os
import random
import shutil
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent.parent.parent


def create_shorter_dataset(
    source_folder: Path,
    destination_folder: Path,
    min_images: int = 3,
    max_images: int = 5
):
    """
    Create a shorter dataset by sampling images from each category.

    Args:
        source_folder: Path to the source images directory
        destination_folder: Path for the output directory
        min_images: Minimum number of images per category
        max_images: Maximum number of images per category
    """
    destination_folder.mkdir(parents=True, exist_ok=True)

    for subfolder_name in os.listdir(source_folder):
        subfolder_path = source_folder / subfolder_name
        if not subfolder_path.is_dir():
            continue

        destination_subfolder_path = destination_folder / subfolder_name
        destination_subfolder_path.mkdir(parents=True, exist_ok=True)

        images = [
            f for f in os.listdir(subfolder_path)
            if (subfolder_path / f).is_file()
        ]

        num_to_select = min(len(images), random.randint(min_images, max_images))
        selected_images = random.sample(images, num_to_select)

        for image in selected_images:
            source_image_path = subfolder_path / image
            destination_image_path = destination_subfolder_path / image
            shutil.copy2(source_image_path, destination_image_path)

        print(f"Copied {len(selected_images)} images from {subfolder_name}")

    print(f"Dataset created at {destination_folder}")


if __name__ == "__main__":
    project_root = get_project_root()

    source_folder = project_root / "images"
    destination_folder = project_root / "images_short"

    create_shorter_dataset(source_folder, destination_folder)
