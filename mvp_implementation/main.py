from fastapi import FastAPI
import json
import random
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify a list like ["http://localhost:8001"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load precomputed similarity data (assuming you've precomputed and stored it in a JSON file)
with open("../data/mvp/precomputed_similarities.json", "r") as f:
    similarity_data = json.load(f)

@app.get("/random_products")
def get_random_products():
    """Return 5 random product IDs from precomputed similarities."""
    random_products = random.sample(list(similarity_data.keys()), 5)
    return random_products

@app.get("/similar/{product_id}")
def similar_products(product_id: str, top_k: int = 10):
    # Return top_k similar products for a given product_id
    return similarity_data.get(product_id, [])[:top_k]

@app.get("/recommend")
def recommend_products(viewed: str, top_k: int = 10):
    # Expecting comma-separated product IDs in the 'viewed' parameter
    viewed_list = viewed.split(",")
    recommendation_scores = defaultdict(float)
    for pid in viewed_list:
        for similar_pid, score in similarity_data.get(pid, []):
            recommendation_scores[similar_pid] += score
    sorted_recommendations = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_recommendations[:top_k]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
