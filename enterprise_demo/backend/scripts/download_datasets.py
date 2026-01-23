"""
Dataset Download Script

Automates downloading of Fashion Products and IKEA Interior datasets.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    print(f"{Colors.OKGREEN}[SUCCESS] {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}[ERROR] {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.OKCYAN}[INFO] {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}[WARNING] {message}{Colors.ENDC}")


def get_project_root():
    """Get the project root directory."""
    current = Path(__file__).resolve()
    # Go up from backend/scripts/ to enterprise_demo/
    return current.parent.parent.parent


def check_kaggle_setup():
    """Check if Kaggle CLI is installed and configured."""
    print_info("Checking Kaggle CLI setup...")

    # Check if kaggle is installed
    try:
        subprocess.run(["kaggle", "--version"],
                      capture_output=True,
                      check=True,
                      text=True)
        print_success("Kaggle CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Kaggle CLI is not installed")
        print_info("Install with: pip install kaggle")
        return False

    # Check for credentials
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print_error("Kaggle credentials not found")
        print_info("1. Go to https://www.kaggle.com/settings/account")
        print_info("2. Click 'Create New API Token' to download kaggle.json")
        print_info(f"3. Move it to: {kaggle_json}")
        return False

    print_success("Kaggle credentials found")
    return True


def check_git():
    """Check if git is installed."""
    try:
        subprocess.run(["git", "--version"],
                      capture_output=True,
                      check=True,
                      text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Git is not installed")
        return False


def download_fashion_dataset(data_dir):
    """Download Fashion Product Images dataset from Kaggle."""
    print_header("Fashion Product Images Dataset")

    if not check_kaggle_setup():
        return False

    target_dir = data_dir / "raw" / "fashion_products"

    # Check if already exists
    if target_dir.exists() and any(target_dir.iterdir()):
        print_warning(f"Dataset already exists at {target_dir}")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print_info("Skipping Fashion dataset download")
            return True
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    print_info("Downloading Fashion Product Images dataset...")
    print_info("This may take 5-10 minutes depending on your connection...")

    try:
        # Download dataset
        result = subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", "paramaggarwal/fashion-product-images-dataset",
                "-p", str(target_dir)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print_success("Download complete!")

        # Find the zip file
        zip_files = list(target_dir.glob("*.zip"))
        if not zip_files:
            print_error("No zip file found after download")
            return False

        zip_file = zip_files[0]
        print_info(f"Extracting {zip_file.name}...")

        # Extract
        subprocess.run(
            ["unzip", "-q", str(zip_file), "-d", str(target_dir)],
            check=True
        )

        # Remove zip file
        zip_file.unlink()

        print_success(f"Fashion dataset ready at {target_dir}")

        # Verify structure
        images_dir = target_dir / "images"
        styles_csv = target_dir / "styles.csv"

        if images_dir.exists() and styles_csv.exists():
            image_count = len(list(images_dir.glob("*.jpg")))
            print_success(f"Verified: {image_count} product images found")
            return True
        else:
            print_warning("Dataset structure verification failed")
            print_info(f"Expected: {images_dir} and {styles_csv}")
            return False

    except subprocess.CalledProcessError as e:
        print_error(f"Download failed: {e}")
        print_error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def download_ikea_dataset(data_dir):
    """Download IKEA Interior Design dataset from GitHub."""
    print_header("IKEA Interior Design Dataset")

    if not check_git():
        return False

    target_dir = data_dir / "raw" / "ikea_interior"

    # Check if already exists
    if target_dir.exists() and any(target_dir.iterdir()):
        print_warning(f"Dataset already exists at {target_dir}")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print_info("Skipping IKEA dataset download")
            return True
        shutil.rmtree(target_dir)

    print_info("Cloning IKEA Interior dataset from GitHub...")

    try:
        result = subprocess.run(
            [
                "git", "clone",
                "--depth", "1",  # Shallow clone for faster download
                "https://github.com/IvonaTau/ikea.git",
                str(target_dir)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print_success("Clone complete!")

        # Remove .git directory to save space
        git_dir = target_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        print_success(f"IKEA dataset ready at {target_dir}")

        # Verify structure
        images_dir = target_dir / "images"
        if images_dir.exists():
            room_images = len(list((images_dir / "rooms").glob("*"))) if (images_dir / "rooms").exists() else 0
            product_images = len(list((images_dir / "products").glob("*"))) if (images_dir / "products").exists() else 0
            print_success(f"Verified: {room_images} room images, {product_images} product images")
            return True
        else:
            print_warning("Dataset structure verification failed")
            return False

    except subprocess.CalledProcessError as e:
        print_error(f"Clone failed: {e}")
        print_error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download datasets for Enterprise Visual Search Platform"
    )
    parser.add_argument(
        "--fashion-only",
        action="store_true",
        help="Download only Fashion Products dataset"
    )
    parser.add_argument(
        "--ikea-only",
        action="store_true",
        help="Download only IKEA Interior dataset"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Custom data directory path (default: project_root/data)"
    )

    args = parser.parse_args()

    # Determine data directory
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        project_root = get_project_root()
        data_dir = project_root / "data"

    data_dir.mkdir(parents=True, exist_ok=True)

    print_header("Enterprise Visual Search - Dataset Downloader")
    print_info(f"Data directory: {data_dir}")

    results = {}

    # Download datasets based on arguments
    if args.ikea_only:
        results['ikea'] = download_ikea_dataset(data_dir)
    elif args.fashion_only:
        results['fashion'] = download_fashion_dataset(data_dir)
    else:
        # Download both
        results['fashion'] = download_fashion_dataset(data_dir)
        results['ikea'] = download_ikea_dataset(data_dir)

    # Print summary
    print_header("Download Summary")

    all_success = all(results.values())

    for dataset, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        color = Colors.OKGREEN if success else Colors.FAIL
        print(f"{color}{dataset.upper()}: {status}{Colors.ENDC}")

    if all_success:
        print_success("\nAll datasets downloaded successfully!")
        print_info("\nNext steps:")
        print_info("1. Run: python backend/scripts/organize_datasets.py")
        print_info("2. Run: python backend/scripts/generate_embeddings.py")
        return 0
    else:
        print_error("\nSome downloads failed. Please check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
