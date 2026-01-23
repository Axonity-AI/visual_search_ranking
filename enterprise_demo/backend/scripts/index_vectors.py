"""
Vector Indexing Script

Uploads CLIP embeddings to vector database (Pinecone or Weaviate).
Enterprise-grade with progress tracking and error handling.
"""

import json
import sys
import time
import os
import numpy as np
from pathlib import Path
from typing import Dict, List
import argparse
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.vector_db import get_vector_db


def print_header(message):
    print(f"\n{'='*70}")
    print(f"{message}")
    print(f"{'='*70}\n")


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


def load_embeddings_and_metadata(embeddings_dir: Path, data_type: str):
    """
    Load embeddings and metadata for products or rooms.

    Args:
        embeddings_dir: Path to embeddings directory
        data_type: "products" or "rooms"

    Returns:
        Tuple of (embeddings array, metadata list)
    """
    print_info(f"Loading {data_type} embeddings...")

    # Load embeddings
    embeddings_file = embeddings_dir / f"{data_type}_embeddings.npz"
    if not embeddings_file.exists():
        print_error(f"Embeddings file not found: {embeddings_file}")
        return None, None

    embeddings_data = np.load(embeddings_file, allow_pickle=True)
    embeddings = embeddings_data['embeddings']
    ids = embeddings_data[f'{data_type.rstrip("s")}_ids'].tolist()

    print_success(f"Loaded {len(embeddings)} {data_type} embeddings")

    # Load metadata mapping
    metadata_file = embeddings_dir / f"{data_type}_metadata_mapping.json"
    if not metadata_file.exists():
        print_error(f"Metadata file not found: {metadata_file}")
        return None, None

    with open(metadata_file, 'r') as f:
        metadata_mapping = json.load(f)

    print_success(f"Loaded metadata for {metadata_mapping[f'total_{data_type}']} {data_type}")

    # Load full product/room metadata
    processed_dir = embeddings_dir.parent / "processed"
    full_metadata_file = processed_dir / data_type / "metadata.json"

    if not full_metadata_file.exists():
        print_error(f"Full metadata file not found: {full_metadata_file}")
        return None, None

    with open(full_metadata_file, 'r') as f:
        full_metadata = json.load(f)

    # Create a mapping from ID to full metadata
    metadata_dict = {}
    for item in full_metadata:
        item_id = item.get(f'{data_type.rstrip("s")}_id')
        if item_id:
            metadata_dict[item_id] = item

    # Build metadata list matching embeddings order
    metadata_list = []
    for item_id in ids:
        if item_id in metadata_dict:
            # Extract relevant fields for vector DB
            item = metadata_dict[item_id]
            meta = {
                f"{data_type.rstrip('s')}_id": item_id,
                "source": item.get("source", "unknown"),
                "image_path": item.get("image_path", ""),
            }

            # Add category for products
            if "category" in item:
                meta["category"] = item["category"]

            # Add room type for rooms
            if "room_type" in item:
                meta["room_type"] = item.get("room_type", "unknown")

            metadata_list.append(meta)
        else:
            print_warning(f"Metadata not found for {data_type.rstrip('s')}: {item_id}")
            metadata_list.append({
                f"{data_type.rstrip('s')}_id": item_id,
                "source": "unknown",
                "image_path": ""
            })

    print_success(f"Prepared {len(metadata_list)} metadata entries")

    return embeddings, ids, metadata_list


def index_data(
    db_type: str,
    index_name: str,
    embeddings: np.ndarray,
    ids: List[str],
    metadata: List[Dict],
    batch_size: int = 100,
    **db_kwargs
):
    """
    Index embeddings to vector database.

    Args:
        db_type: "pinecone" or "weaviate"
        index_name: Name of the index/collection
        embeddings: Numpy array of vectors
        ids: List of IDs
        metadata: List of metadata dicts
        batch_size: Batch size for uploads
        **db_kwargs: Additional database connection parameters
    """
    print_header(f"Indexing to {db_type.upper()}")

    try:
        # Initialize database
        print_info(f"Connecting to {db_type}...")
        db = get_vector_db(db_type, **db_kwargs)
        print_success(f"Connected to {db_type}")

        # Get embedding dimension
        dimension = embeddings.shape[1]
        print_info(f"Vector dimension: {dimension}")

        # Create index if it doesn't exist
        print_info(f"Creating index '{index_name}' if not exists...")
        db.create_index(index_name, dimension=dimension, metric="cosine")

        # Check existing stats
        if db.index_exists(index_name):
            stats = db.get_index_stats(index_name)
            print_info(f"Index stats: {stats}")

        # Upload vectors
        print_info(f"Uploading {len(embeddings)} vectors in batches of {batch_size}...")
        start_time = time.time()

        uploaded = db.upsert_vectors(
            index_name=index_name,
            vectors=embeddings,
            ids=ids,
            metadata=metadata,
            batch_size=batch_size
        )

        elapsed = time.time() - start_time
        vectors_per_sec = uploaded / elapsed if elapsed > 0 else 0

        print_success(f"Uploaded {uploaded} vectors in {elapsed:.2f}s ({vectors_per_sec:.1f} vectors/sec)")

        # Get final stats
        time.sleep(2)  # Wait for indexing to complete
        final_stats = db.get_index_stats(index_name)
        print_info(f"Final index stats: {final_stats}")

        return True

    except Exception as e:
        print_error(f"Failed to index data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Index CLIP embeddings to vector database"
    )
    parser.add_argument(
        "--db-type",
        type=str,
        choices=['pinecone', 'weaviate'],
        help="Vector database type (default: from .env VECTOR_DB_TYPE)"
    )
    parser.add_argument(
        "--products-only",
        action="store_true",
        help="Index only product embeddings"
    )
    parser.add_argument(
        "--rooms-only",
        action="store_true",
        help="Index only room embeddings"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for uploads (default: 100)"
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        help="Custom embeddings directory path (default: project_root/data/embeddings)"
    )

    args = parser.parse_args()

    print_header("Enterprise Visual Search - Vector Indexing")

    # Load environment variables
    project_root = get_project_root()
    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        print_success(f"Loaded environment from {env_file}")
    else:
        print_warning(f"No .env file found at {env_file}")

    # Determine database type
    db_type = args.db_type or os.getenv("VECTOR_DB_TYPE", "pinecone")
    print_info(f"Using vector database: {db_type}")

    # Get embeddings directory
    if args.embeddings_dir:
        embeddings_dir = Path(args.embeddings_dir)
    else:
        embeddings_dir = project_root / "data" / "embeddings"

    if not embeddings_dir.exists():
        print_error(f"Embeddings directory not found: {embeddings_dir}")
        print_info("Please run generate_embeddings.py first")
        return 1

    # Database connection parameters
    db_kwargs = {}

    if db_type == "pinecone":
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")

        if not api_key:
            print_error("PINECONE_API_KEY not set in environment")
            print_info("Set it in .env file or export PINECONE_API_KEY=your_key")
            return 1

        db_kwargs = {
            "api_key": api_key,
            "environment": environment
        }

        products_index = os.getenv("PINECONE_PRODUCTS_INDEX", "visual-search-products")
        rooms_index = os.getenv("PINECONE_ROOMS_INDEX", "visual-search-rooms")

    elif db_type == "weaviate":
        host = os.getenv("WEAVIATE_HOST", "localhost")
        port = int(os.getenv("WEAVIATE_PORT", "8080"))

        db_kwargs = {
            "host": host,
            "port": port
        }

        products_index = "VisualSearchProducts"
        rooms_index = "VisualSearchRooms"

    # Index products
    if not args.rooms_only:
        print_header("INDEXING PRODUCTS")

        products_embeddings, products_ids, products_metadata = load_embeddings_and_metadata(
            embeddings_dir, "products"
        )

        if products_embeddings is not None:
            success = index_data(
                db_type=db_type,
                index_name=products_index,
                embeddings=products_embeddings,
                ids=products_ids,
                metadata=products_metadata,
                batch_size=args.batch_size,
                **db_kwargs
            )

            if not success:
                print_error("Failed to index products")
                return 1

            print_success("Products indexed successfully")
        else:
            print_error("Failed to load product embeddings")
            return 1

    # Index rooms
    if not args.products_only:
        print_header("INDEXING ROOMS")

        rooms_embeddings, rooms_ids, rooms_metadata = load_embeddings_and_metadata(
            embeddings_dir, "rooms"
        )

        if rooms_embeddings is not None:
            success = index_data(
                db_type=db_type,
                index_name=rooms_index,
                embeddings=rooms_embeddings,
                ids=rooms_ids,
                metadata=rooms_metadata,
                batch_size=args.batch_size,
                **db_kwargs
            )

            if not success:
                print_error("Failed to index rooms")
                return 1

            print_success("Rooms indexed successfully")
        else:
            print_error("Failed to load room embeddings")
            return 1

    print_header("Indexing Complete")

    if not args.rooms_only and not args.products_only:
        print_success("All embeddings indexed successfully!")
        print_info("\nNext steps:")
        print_info("1. Test queries with search API")
        print_info("2. Build FastAPI backend: backend/app/main.py")
        print_info("3. Create frontend interfaces")
    else:
        print_success("Selected embeddings indexed successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
