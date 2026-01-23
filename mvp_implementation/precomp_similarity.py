import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# Load dataset with embeddings
with open('../data/mvp/dataset_with_embeddings.json', 'r') as f:
    data = json.load(f)

# Convert embeddings to numpy arrays for efficient computation
product_embeddings = {item['product_id']: np.array(item['embedding']) for item in data}
product_categories = {item['product_id']: item['category'] for item in data}

# List of product IDs for easy indexing
product_ids = list(product_embeddings.keys())

# Precompute similarity scores
top_k = 100  # Number of similar items to store
similarity_results = {}

print("Computing similarity scores...")
for i in tqdm(range(len(product_ids))):
    pid = product_ids[i]
    embedding = product_embeddings[pid].reshape(1, -1)
    category = product_categories[pid]
    
    # Compare only within the same category
    category_products = [p for p in product_ids if product_categories[p] == category and p != pid]
    category_embeddings = np.array([product_embeddings[p] for p in category_products])
    
    if category_embeddings.size > 0:
        similarities = cosine_similarity(embedding, category_embeddings)[0]
        sorted_indices = np.argsort(similarities)[::-1]  # Descending order
        top_similar = [(category_products[idx], float(similarities[idx])) for idx in sorted_indices[:top_k]]
    else:
        top_similar = []
    
    similarity_results[pid] = top_similar

# Save precomputed similarities to JSON
with open('../data/mvp/precomputed_similarities.json', 'w') as f:
    json.dump(similarity_results, f, indent=4)

print("Precomputed similarity scores saved.")


# ////////////////////////////////////////////////////////////////
# OPTIMIZED APPROACH

# import json
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from tqdm import tqdm

# # Load dataset with embeddings
# with open('dataset_with_embeddings.json', 'r') as f:
#     data = json.load(f)

# # Convert embeddings to numpy arrays
# product_embeddings = {item['product_id']: np.array(item['embedding']) for item in data}
# product_categories = {item['product_id']: item['category'] for item in data}

# # List of product IDs
# product_ids = list(product_embeddings.keys())

# # Group products by category
# category_to_products = {}
# for pid in product_ids:
#     category = product_categories[pid]
#     category_to_products.setdefault(category, []).append(pid)

# # Precompute similarity scores
# top_k = 10  # Number of similar items to store
# similarity_results = {}

# print("Computing similarity scores more efficiently...")

# for category, products in tqdm(category_to_products.items()):
#     # Stack all embeddings in the category into a single matrix
#     embeddings_matrix = np.stack([product_embeddings[pid] for pid in products])

#     # Compute cosine similarity for all pairs at once
#     similarity_matrix = cosine_similarity(embeddings_matrix)

#     for i, pid in enumerate(products):
#         similarities = similarity_matrix[i]
#         sorted_indices = np.argsort(similarities)[::-1]  # Descending order
#         top_similar = [(products[idx], float(similarities[idx])) for idx in sorted_indices if idx != i][:top_k]
#         similarity_results[pid] = top_similar

# # Save precomputed similarities to JSON
# with open('precomputed_similarities.json', 'w') as f:
#     json.dump(similarity_results, f, indent=4)

# print("Optimized precomputed similarity scores saved.")


