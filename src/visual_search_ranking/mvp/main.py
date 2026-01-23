"""
MVP FastAPI Backend for Visual Search Platform.

Serves precomputed similarity recommendations for artwork images.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="MVP Visual Search API",
    description="ResNet-50 based visual similarity recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine data path relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "mvp" / "precomputed_similarities.json"

# Load precomputed similarity data
similarity_data = {}
if DATA_PATH.exists():
    with open(DATA_PATH, "r") as f:
        similarity_data = json.load(f)
else:
    print(f"Warning: Data file not found at {DATA_PATH}")


@app.get("/random_products")
def get_random_products():
    """Return 5 random product IDs from precomputed similarities."""
    if not similarity_data:
        return []
    random_products = random.sample(list(similarity_data.keys()), min(5, len(similarity_data)))
    return random_products


@app.get("/similar/{product_id}")
def similar_products(product_id: str, top_k: int = 10):
    """Return top_k similar products for a given product_id."""
    return similarity_data.get(product_id, [])[:top_k]


@app.get("/recommend")
def recommend_products(viewed: str, top_k: int = 10):
    """
    Recommend products based on viewing history.

    Args:
        viewed: Comma-separated product IDs
        top_k: Number of recommendations to return
    """
    viewed_list = viewed.split(",")
    recommendation_scores = defaultdict(float)
    for pid in viewed_list:
        for similar_pid, score in similarity_data.get(pid, []):
            recommendation_scores[similar_pid] += score
    sorted_recommendations = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_recommendations[:top_k]


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "data_loaded": bool(similarity_data),
        "total_products": len(similarity_data)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
