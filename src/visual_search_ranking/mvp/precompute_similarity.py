"""
Similarity Computation Script.

Computes cosine similarities between product embeddings within categories.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent.parent


def compute_similarities(
    embeddings_path: Path = None,
    output_path: Path = None,
    top_k: int = 100
):
    """
    Compute cosine similarity scores within categories.

    Args:
        embeddings_path: Path to dataset with embeddings JSON
        output_path: Path for output similarities JSON
        top_k: Number of similar items to store per product
    """
    project_root = get_project_root()

    if embeddings_path is None:
        embeddings_path = project_root / "data" / "mvp" / "dataset_with_embeddings.json"
    if output_path is None:
        output_path = project_root / "data" / "mvp" / "precomputed_similarities.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading embeddings from {embeddings_path}...")
    with open(embeddings_path, 'r') as f:
        data = json.load(f)

    # Convert embeddings to numpy arrays
    product_embeddings = {
        item['product_id']: np.array(item['embedding'])
        for item in data
    }
    product_categories = {
        item['product_id']: item['category']
        for item in data
    }

    product_ids = list(product_embeddings.keys())
    print(f"Loaded {len(product_ids)} products")

    # Compute similarity scores
    similarity_results = {}

    print(f"Computing similarity scores (top-{top_k} per product)...")
    for i in tqdm(range(len(product_ids))):
        pid = product_ids[i]
        embedding = product_embeddings[pid].reshape(1, -1)
        category = product_categories[pid]

        # Compare only within the same category
        category_products = [
            p for p in product_ids
            if product_categories[p] == category and p != pid
        ]

        if not category_products:
            similarity_results[pid] = []
            continue

        category_embeddings = np.array([
            product_embeddings[p] for p in category_products
        ])

        similarities = cosine_similarity(embedding, category_embeddings)[0]
        sorted_indices = np.argsort(similarities)[::-1]

        top_similar = [
            (category_products[idx], float(similarities[idx]))
            for idx in sorted_indices[:top_k]
        ]

        similarity_results[pid] = top_similar

    # Save results
    with open(output_path, 'w') as f:
        json.dump(similarity_results, f, indent=4)

    print(f"Saved precomputed similarities to {output_path}")
    return similarity_results


def compute_similarities_optimized(
    embeddings_path: Path = None,
    output_path: Path = None,
    top_k: int = 100
):
    """
    Optimized similarity computation using vectorized operations.

    Faster for large datasets by computing all similarities per category at once.
    """
    project_root = get_project_root()

    if embeddings_path is None:
        embeddings_path = project_root / "data" / "mvp" / "dataset_with_embeddings.json"
    if output_path is None:
        output_path = project_root / "data" / "mvp" / "precomputed_similarities.json"

    print(f"Loading embeddings from {embeddings_path}...")
    with open(embeddings_path, 'r') as f:
        data = json.load(f)

    # Convert embeddings to numpy arrays
    product_embeddings = {
        item['product_id']: np.array(item['embedding'])
        for item in data
    }
    product_categories = {
        item['product_id']: item['category']
        for item in data
    }

    product_ids = list(product_embeddings.keys())

    # Group products by category
    category_to_products = {}
    for pid in product_ids:
        category = product_categories[pid]
        category_to_products.setdefault(category, []).append(pid)

    similarity_results = {}

    print("Computing similarity scores (optimized)...")
    for category, products in tqdm(category_to_products.items()):
        # Stack all embeddings in the category
        embeddings_matrix = np.stack([
            product_embeddings[pid] for pid in products
        ])

        # Compute cosine similarity for all pairs at once
        similarity_matrix = cosine_similarity(embeddings_matrix)

        for i, pid in enumerate(products):
            similarities = similarity_matrix[i]
            sorted_indices = np.argsort(similarities)[::-1]

            top_similar = [
                (products[idx], float(similarities[idx]))
                for idx in sorted_indices
                if idx != i
            ][:top_k]

            similarity_results[pid] = top_similar

    # Save results
    with open(output_path, 'w') as f:
        json.dump(similarity_results, f, indent=4)

    print(f"Saved precomputed similarities to {output_path}")
    return similarity_results


if __name__ == "__main__":
    compute_similarities()
