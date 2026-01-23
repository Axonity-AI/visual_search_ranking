"""
Embedding Generation Script

Generates CLIP embeddings for all products and rooms in batch mode.
"""

import json
import sys
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clip_service import get_clip_service


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
    print(f"\n{'='*60}")
    print(f"{message}")
    print(f"{'='*60}\n")


def print_success(message):
    print(f"[SUCCESS] {message}", flush=True)


def print_error(message):
    print(f"[ERROR] {message}", flush=True)


def print_info(message):
    print(f"[INFO] {message}", flush=True)


def print_warning(message):
    print(f"[WARNING] {message}", flush=True)


def get_project_root():
    """Get the project root directory."""
    current = Path(__file__).resolve()
    # Go up from backend/scripts/ to enterprise_demo/
    return current.parent.parent.parent


class EmbeddingGenerator:
    def __init__(
        self,
        data_dir: Path,
        embeddings_dir: Path,
        batch_size: int = 32,
        device: Optional[str] = None
    ):
        self.data_dir = data_dir
        self.embeddings_dir = embeddings_dir
        self.batch_size = batch_size

        self.processed_dir = data_dir / "processed"
        self.products_dir = self.processed_dir / "products"
        self.rooms_dir = self.processed_dir / "rooms"

        # Create embeddings directory
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        # Initialize CLIP service
        print_info("Initializing CLIP service...")
        self.clip_service = get_clip_service(device=device)

        model_info = self.clip_service.get_model_info()
        print_success(f"CLIP model loaded: {model_info['model_name']}")
        print_info(f"Device: {model_info['device']}")
        print_info(f"Embedding dimension: {model_info['embedding_dim']}")

    def load_metadata(self, metadata_path: Path) -> List[Dict]:
        """Load metadata JSON file."""
        if not metadata_path.exists():
            print_error(f"Metadata file not found: {metadata_path}")
            return []

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return metadata

    def generate_product_embeddings(self, resume: bool = False) -> Dict:
        """Generate embeddings for all product images."""
        print_header("Generating Product Embeddings")

        # Load metadata
        metadata_path = self.products_dir / "metadata.json"
        products = self.load_metadata(metadata_path)

        if not products:
            print_error("No product metadata found")
            return {}

        print_info(f"Found {len(products)} products")

        # Check for existing embeddings if resume is enabled
        embeddings_path = self.embeddings_dir / "products_embeddings.npz"
        start_idx = 0

        if resume and embeddings_path.exists():
            print_info("Resume mode: Loading existing embeddings...")
            existing_data = np.load(embeddings_path, allow_pickle=True)
            existing_embeddings = existing_data['embeddings']
            existing_ids = existing_data['product_ids'].tolist()
            start_idx = len(existing_ids)
            print_info(f"Resuming from product {start_idx}/{len(products)}")
        else:
            existing_embeddings = None
            existing_ids = []

        # Prepare image paths and IDs
        image_paths = []
        product_ids = []

        for i, product in enumerate(products):
            if i < start_idx:
                continue

            # Construct full image path
            image_rel_path = product['image_path']
            image_full_path = self.data_dir / "processed" / image_rel_path

            if not image_full_path.exists():
                print_warning(f"Image not found: {image_full_path}")
                continue

            image_paths.append(image_full_path)
            product_ids.append(product['product_id'])

        if not image_paths:
            print_error("No valid product images to process")
            return {}

        print_info(f"Processing {len(image_paths)} product images...")

        # Generate embeddings in batches
        start_time = time.time()

        try:
            embeddings = self.clip_service.encode_images_batch(
                images=image_paths,
                batch_size=self.batch_size,
                normalize=True,
                show_progress=True
            )

            elapsed_time = time.time() - start_time
            images_per_sec = len(image_paths) / elapsed_time

            print_success(f"Generated {len(embeddings)} embeddings")
            print_info(f"Time: {elapsed_time:.2f}s ({images_per_sec:.1f} images/sec)")

            # Combine with existing embeddings if resuming
            if existing_embeddings is not None:
                embeddings = np.vstack([existing_embeddings, embeddings])
                product_ids = existing_ids + product_ids

            # Save embeddings
            np.savez_compressed(
                embeddings_path,
                embeddings=embeddings,
                product_ids=np.array(product_ids),
                embedding_dim=embeddings.shape[1],
                model_name=self.clip_service.model_name
            )

            print_success(f"Saved embeddings to {embeddings_path}")

            # Save metadata mapping
            metadata_mapping_path = self.embeddings_dir / "products_metadata_mapping.json"
            mapping = {
                "total_products": len(product_ids),
                "embedding_dim": int(embeddings.shape[1]),
                "model_name": self.clip_service.model_name,
                "device_used": self.clip_service.device,
                "product_ids": product_ids,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            with open(metadata_mapping_path, 'w') as f:
                json.dump(mapping, f, indent=2)

            return {
                "total_products": len(product_ids),
                "embedding_dim": embeddings.shape[1],
                "time_seconds": elapsed_time,
                "images_per_sec": images_per_sec,
                "embeddings_path": str(embeddings_path)
            }

        except Exception as e:
            print_error(f"Error generating embeddings: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def generate_room_embeddings(self, resume: bool = False) -> Dict:
        """Generate embeddings for all room images."""
        print_header("Generating Room Embeddings")

        # Load metadata
        metadata_path = self.rooms_dir / "metadata.json"
        rooms = self.load_metadata(metadata_path)

        if not rooms:
            print_error("No room metadata found")
            return {}

        print_info(f"Found {len(rooms)} rooms")

        # Check for existing embeddings if resume is enabled
        embeddings_path = self.embeddings_dir / "rooms_embeddings.npz"
        start_idx = 0

        if resume and embeddings_path.exists():
            print_info("Resume mode: Loading existing embeddings...")
            existing_data = np.load(embeddings_path, allow_pickle=True)
            existing_embeddings = existing_data['embeddings']
            existing_ids = existing_data['room_ids'].tolist()
            start_idx = len(existing_ids)
            print_info(f"Resuming from room {start_idx}/{len(rooms)}")
        else:
            existing_embeddings = None
            existing_ids = []

        # Prepare image paths and IDs
        image_paths = []
        room_ids = []

        for i, room in enumerate(rooms):
            if i < start_idx:
                continue

            # Construct full image path
            image_rel_path = room['image_path']
            image_full_path = self.data_dir / "processed" / image_rel_path

            if not image_full_path.exists():
                print_warning(f"Image not found: {image_full_path}")
                continue

            image_paths.append(image_full_path)
            room_ids.append(room['room_id'])

        if not image_paths:
            print_error("No valid room images to process")
            return {}

        print_info(f"Processing {len(image_paths)} room images...")

        # Generate embeddings in batches
        start_time = time.time()

        try:
            embeddings = self.clip_service.encode_images_batch(
                images=image_paths,
                batch_size=self.batch_size,
                normalize=True,
                show_progress=True
            )

            elapsed_time = time.time() - start_time
            images_per_sec = len(image_paths) / elapsed_time

            print_success(f"Generated {len(embeddings)} embeddings")
            print_info(f"Time: {elapsed_time:.2f}s ({images_per_sec:.1f} images/sec)")

            # Combine with existing embeddings if resuming
            if existing_embeddings is not None:
                embeddings = np.vstack([existing_embeddings, embeddings])
                room_ids = existing_ids + room_ids

            # Save embeddings
            np.savez_compressed(
                embeddings_path,
                embeddings=embeddings,
                room_ids=np.array(room_ids),
                embedding_dim=embeddings.shape[1],
                model_name=self.clip_service.model_name
            )

            print_success(f"Saved embeddings to {embeddings_path}")

            # Save metadata mapping
            metadata_mapping_path = self.embeddings_dir / "rooms_metadata_mapping.json"
            mapping = {
                "total_rooms": len(room_ids),
                "embedding_dim": int(embeddings.shape[1]),
                "model_name": self.clip_service.model_name,
                "device_used": self.clip_service.device,
                "room_ids": room_ids,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            with open(metadata_mapping_path, 'w') as f:
                json.dump(mapping, f, indent=2)

            return {
                "total_rooms": len(room_ids),
                "embedding_dim": embeddings.shape[1],
                "time_seconds": elapsed_time,
                "images_per_sec": images_per_sec,
                "embeddings_path": str(embeddings_path)
            }

        except Exception as e:
            print_error(f"Error generating embeddings: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def generate_all(self, resume: bool = False):
        """Generate embeddings for both products and rooms."""
        print_header("Enterprise Visual Search - Embedding Generation")
        print_info(f"Data directory: {self.data_dir}")
        print_info(f"Embeddings directory: {self.embeddings_dir}")
        print_info(f"Batch size: {self.batch_size}")

        results = {}

        # Generate product embeddings
        results['products'] = self.generate_product_embeddings(resume=resume)

        # Generate room embeddings
        results['rooms'] = self.generate_room_embeddings(resume=resume)

        # Print summary
        print_header("Embedding Generation Summary")

        if results['products']:
            print(f"{Colors.OKGREEN}Products:{Colors.ENDC}")
            print(f"  Total: {results['products']['total_products']}")
            print(f"  Dimension: {results['products']['embedding_dim']}")
            print(f"  Speed: {results['products']['images_per_sec']:.1f} images/sec")
            print(f"  Time: {results['products']['time_seconds']:.2f}s")
        else:
            print(f"{Colors.FAIL}Products: FAILED{Colors.ENDC}")

        print()

        if results['rooms']:
            print(f"{Colors.OKGREEN}Rooms:{Colors.ENDC}")
            print(f"  Total: {results['rooms']['total_rooms']}")
            print(f"  Dimension: {results['rooms']['embedding_dim']}")
            print(f"  Speed: {results['rooms']['images_per_sec']:.1f} images/sec")
            print(f"  Time: {results['rooms']['time_seconds']:.2f}s")
        else:
            print(f"{Colors.FAIL}Rooms: FAILED{Colors.ENDC}")

        print()

        if results['products'] and results['rooms']:
            print_success("All embeddings generated successfully!")
            print_info("\nNext steps:")
            print_info("1. Set up vector database (Pinecone/Weaviate)")
            print_info("2. Run: python backend/scripts/index_vectors.py")
            return 0
        else:
            print_error("Some embedding generation failed. Check errors above.")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="Generate CLIP embeddings for Enterprise Visual Search Platform"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Custom data directory path (default: project_root/data)"
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        help="Custom embeddings directory path (default: data_dir/embeddings)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for embedding generation (default: 32)"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=['cuda', 'cpu', 'auto'],
        default='auto',
        help="Device to use for CLIP model (default: auto)"
    )
    parser.add_argument(
        "--products-only",
        action="store_true",
        help="Generate only product embeddings"
    )
    parser.add_argument(
        "--rooms-only",
        action="store_true",
        help="Generate only room embeddings"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing embeddings"
    )

    args = parser.parse_args()

    # Determine directories
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        project_root = get_project_root()
        data_dir = project_root / "data"

    if args.embeddings_dir:
        embeddings_dir = Path(args.embeddings_dir)
    else:
        embeddings_dir = data_dir / "embeddings"

    # Check if processed data exists
    processed_dir = data_dir / "processed"
    if not processed_dir.exists():
        print_error(f"Processed data directory not found: {processed_dir}")
        print_info("Please run organize_datasets.py first")
        return 1

    # Determine device
    device = None if args.device == 'auto' else args.device

    # Create generator
    generator = EmbeddingGenerator(
        data_dir=data_dir,
        embeddings_dir=embeddings_dir,
        batch_size=args.batch_size,
        device=device
    )

    # Generate embeddings based on arguments
    if args.products_only:
        result = generator.generate_product_embeddings(resume=args.resume)
        return 0 if result else 1
    elif args.rooms_only:
        result = generator.generate_room_embeddings(resume=args.resume)
        return 0 if result else 1
    else:
        return generator.generate_all(resume=args.resume)


if __name__ == "__main__":
    sys.exit(main())
