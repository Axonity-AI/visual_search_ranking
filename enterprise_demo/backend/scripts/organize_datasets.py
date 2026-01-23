"""
Dataset Organization Script

Organizes downloaded datasets into a unified structure with metadata.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List
import pandas as pd
from PIL import Image
import argparse


class DatasetOrganizer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.processed_dir = data_dir / "processed"

        self.fashion_raw = self.raw_dir / "fashion_products"
        self.ikea_raw = self.raw_dir / "ikea_interior"

        self.products_processed = self.processed_dir / "products"
        self.rooms_processed = self.processed_dir / "rooms"

    def print_status(self, message, status="INFO"):
        symbols = {"INFO": "[INFO]", "SUCCESS": "[SUCCESS]", "ERROR": "[ERROR]", "WARNING": "[WARNING]"}
        print(f"{symbols.get(status, '[INFO]')} {message}")

    def validate_image(self, image_path: Path) -> Dict:
        """Validate and get image metadata."""
        try:
            with Image.open(image_path) as img:
                return {
                    "valid": True,
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def organize_fashion_products(self) -> Dict:
        """Organize Fashion Products dataset."""
        self.print_status("Organizing Fashion Products dataset...")

        if not self.fashion_raw.exists():
            self.print_status("Fashion Products dataset not found", "WARNING")
            return {}

        # Read metadata CSV
        styles_csv = self.fashion_raw / "styles.csv"
        if not styles_csv.exists():
            self.print_status("styles.csv not found", "ERROR")
            return {}

        df = pd.read_csv(styles_csv, on_bad_lines='skip')
        self.print_status(f"Loaded metadata for {len(df)} products", "SUCCESS")

        # Create output directory
        output_images = self.products_processed / "images"
        output_images.mkdir(parents=True, exist_ok=True)

        products_metadata = []
        valid_count = 0
        invalid_count = 0

        for idx, row in df.iterrows():
            product_id = str(row['id'])
            image_path = self.fashion_raw / "images" / f"{product_id}.jpg"

            if not image_path.exists():
                invalid_count += 1
                continue

            # Validate image
            img_info = self.validate_image(image_path)
            if not img_info['valid']:
                invalid_count += 1
                continue

            # Copy image to processed directory
            output_path = output_images / f"{product_id}.jpg"
            shutil.copy2(image_path, output_path)

            # Create metadata entry
            metadata = {
                "product_id": product_id,
                "product_name": row.get('productDisplayName', f"Product {product_id}"),
                "category": row.get('masterCategory', 'Unknown'),
                "subcategory": row.get('subCategory', 'Unknown'),
                "article_type": row.get('articleType', 'Unknown'),
                "color": row.get('baseColour', 'Unknown'),
                "season": row.get('season', 'Unknown'),
                "year": int(row['year']) if pd.notna(row.get('year')) else None,
                "usage": row.get('usage', 'Unknown'),
                "gender": row.get('gender', 'Unisex'),
                "image_path": f"products/images/{product_id}.jpg",
                "image_width": img_info['width'],
                "image_height": img_info['height'],
                "source": "fashion_products_kaggle"
            }

            products_metadata.append(metadata)
            valid_count += 1

            if valid_count % 1000 == 0:
                self.print_status(f"Processed {valid_count} products...", "INFO")

        # Save metadata
        metadata_path = self.products_processed / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(products_metadata, f, indent=2)

        self.print_status(f"Fashion Products: {valid_count} valid, {invalid_count} invalid", "SUCCESS")

        return {
            "total": len(df),
            "valid": valid_count,
            "invalid": invalid_count,
            "metadata_path": str(metadata_path)
        }

    def organize_ikea_interior(self) -> Dict:
        """Organize IKEA Interior dataset."""
        self.print_status("Organizing IKEA Interior dataset...")

        if not self.ikea_raw.exists():
            self.print_status("IKEA Interior dataset not found", "WARNING")
            return {}

        # Create output directories
        room_images_dir = self.rooms_processed / "images"
        product_images_dir = self.products_processed / "images"
        room_images_dir.mkdir(parents=True, exist_ok=True)
        product_images_dir.mkdir(parents=True, exist_ok=True)

        rooms_metadata = []
        ikea_products_metadata = []

        # Process room images
        rooms_source = self.ikea_raw / "images" / "room_scenes"
        if rooms_source.exists():
            room_count = 0
            for room_img in rooms_source.glob("*"):
                if room_img.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                    continue

                img_info = self.validate_image(room_img)
                if not img_info['valid']:
                    continue

                room_id = f"room_{room_img.stem}"
                output_path = room_images_dir / f"{room_id}{room_img.suffix}"
                shutil.copy2(room_img, output_path)

                metadata = {
                    "room_id": room_id,
                    "room_name": room_img.stem.replace('_', ' ').title(),
                    "image_path": f"rooms/images/{room_id}{room_img.suffix}",
                    "image_width": img_info['width'],
                    "image_height": img_info['height'],
                    "source": "ikea_interior",
                    "room_type": "living_room",  # Default, can be enhanced
                    "style": "modern"  # Default, can be enhanced
                }

                rooms_metadata.append(metadata)
                room_count += 1

            self.print_status(f"Processed {room_count} room images", "SUCCESS")

        # Process IKEA product images (organized by category folders)
        ikea_images_dir = self.ikea_raw / "images"
        product_count = 0

        # IKEA has category folders: bed, chair, couch, clock, dining table, objects, plant_pot
        product_categories = ['bed', 'chair', 'couch', 'clock', 'dining table', 'objects', 'plant_pot']

        for category in product_categories:
            category_dir = ikea_images_dir / category
            if not category_dir.exists():
                continue

            for product_img in category_dir.glob("*"):
                if product_img.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                    continue

                img_info = self.validate_image(product_img)
                if not img_info['valid']:
                    continue

                product_id = f"ikea_{category.replace(' ', '_')}_{product_img.stem}"
                output_path = product_images_dir / f"{product_id}{product_img.suffix}"
                shutil.copy2(product_img, output_path)

                metadata = {
                    "product_id": product_id,
                    "product_name": product_img.stem.replace('_', ' ').title(),
                    "category": "Furniture",
                    "subcategory": category.title(),
                    "image_path": f"products/images/{product_id}{product_img.suffix}",
                    "image_width": img_info['width'],
                    "image_height": img_info['height'],
                    "source": "ikea_interior",
                    "brand": "IKEA"
                }

                ikea_products_metadata.append(metadata)
                product_count += 1

        if product_count > 0:
            self.print_status(f"Processed {product_count} IKEA product images", "SUCCESS")

        # Save room metadata
        rooms_metadata_path = self.rooms_processed / "metadata.json"
        with open(rooms_metadata_path, 'w') as f:
            json.dump(rooms_metadata, f, indent=2)

        # Merge IKEA products with fashion products if exists
        products_metadata_path = self.products_processed / "metadata.json"
        if products_metadata_path.exists():
            with open(products_metadata_path, 'r') as f:
                existing_products = json.load(f)
            combined_products = existing_products + ikea_products_metadata
            with open(products_metadata_path, 'w') as f:
                json.dump(combined_products, f, indent=2)
        else:
            with open(products_metadata_path, 'w') as f:
                json.dump(ikea_products_metadata, f, indent=2)

        return {
            "rooms": len(rooms_metadata),
            "products": len(ikea_products_metadata),
            "rooms_metadata_path": str(rooms_metadata_path),
            "products_metadata_path": str(products_metadata_path)
        }

    def create_manifest(self, fashion_stats: Dict, ikea_stats: Dict):
        """Create a manifest file with dataset statistics."""
        manifest = {
            "version": "1.0.0",
            "created_at": pd.Timestamp.now().isoformat(),
            "datasets": {
                "fashion_products": fashion_stats,
                "ikea_interior": ikea_stats
            },
            "total_products": fashion_stats.get("valid", 0) + ikea_stats.get("products", 0),
            "total_rooms": ikea_stats.get("rooms", 0),
            "structure": {
                "products": {
                    "images": "data/processed/products/images/",
                    "metadata": "data/processed/products/metadata.json"
                },
                "rooms": {
                    "images": "data/processed/rooms/images/",
                    "metadata": "data/processed/rooms/metadata.json"
                }
            }
        }

        manifest_path = self.processed_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        self.print_status(f"Manifest created: {manifest_path}", "SUCCESS")
        return manifest

    def organize_all(self):
        """Run complete organization process."""
        print("\n" + "="*60)
        print("Dataset Organization")
        print("="*60 + "\n")

        # Create processed directories
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Organize fashion products
        fashion_stats = self.organize_fashion_products()

        # Organize IKEA interior
        ikea_stats = self.organize_ikea_interior()

        # Create manifest
        manifest = self.create_manifest(fashion_stats, ikea_stats)

        # Print summary
        print("\n" + "="*60)
        print("Organization Summary")
        print("="*60 + "\n")

        print(f"Total Products: {manifest['total_products']}")
        print(f"Total Rooms: {manifest['total_rooms']}")
        print(f"\nProcessed data location: {self.processed_dir}")
        print("\nNext steps:")
        print("1. Review organized data in data/processed/")
        print("2. Run: python backend/scripts/generate_embeddings.py")


def main():
    parser = argparse.ArgumentParser(
        description="Organize datasets for Enterprise Visual Search Platform"
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
        # Get project root (go up from backend/scripts/)
        current = Path(__file__).resolve()
        project_root = current.parent.parent.parent
        data_dir = project_root / "data"

    if not data_dir.exists():
        print(f"[ERROR] Data directory not found: {data_dir}")
        print("[INFO] Please run download_datasets.py first")
        return 1

    organizer = DatasetOrganizer(data_dir)
    organizer.organize_all()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
