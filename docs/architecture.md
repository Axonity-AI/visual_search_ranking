# Architecture Documentation

## Overview

Visual Search Ranking is an AI-powered image recommendation and search system consisting of two main components:

1. **MVP Implementation** - ResNet-50 based visual similarity for artwork recommendations
2. **Enterprise Implementation** - CLIP-powered multi-modal search for production use

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Visual Search Ranking                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   MVP (ResNet-50)   │    │    Enterprise (CLIP + Pinecone) │ │
│  │                     │    │                                  │ │
│  │  ┌───────────────┐  │    │  ┌───────────────┐              │ │
│  │  │   FastAPI     │  │    │  │   FastAPI     │              │ │
│  │  │   Backend     │  │    │  │   Backend     │              │ │
│  │  └───────────────┘  │    │  └───────────────┘              │ │
│  │         │           │    │         │                        │ │
│  │         ▼           │    │         ▼                        │ │
│  │  ┌───────────────┐  │    │  ┌───────────────┐              │ │
│  │  │  Precomputed  │  │    │  │ CLIP Service  │              │ │
│  │  │  Similarities │  │    │  │ (Embeddings)  │              │ │
│  │  │    (JSON)     │  │    │  └───────────────┘              │ │
│  │  └───────────────┘  │    │         │                        │ │
│  │                     │    │         ▼                        │ │
│  │                     │    │  ┌───────────────┐              │ │
│  │                     │    │  │   Pinecone    │              │ │
│  │                     │    │  │  Vector DB    │              │ │
│  │                     │    │  └───────────────┘              │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Frontend Layer                         ││
│  │         Vanilla JavaScript + HTML + CSS                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### MVP Implementation

**Technology Stack:**
- **Model**: ResNet-50 (ImageNet pre-trained)
- **Embeddings**: 2048-dimensional feature vectors
- **Storage**: JSON files (precomputed similarities)
- **Backend**: FastAPI

**Data Flow:**
1. Images processed through ResNet-50 → 2048-dim embeddings
2. Cosine similarities computed within categories
3. Top-100 similar items stored per product
4. FastAPI serves precomputed results (O(1) lookup)

**Key Files:**
- `src/visual_search_ranking/mvp/main.py` - FastAPI server
- `src/visual_search_ranking/mvp/convert_to_json.py` - Embedding generation
- `src/visual_search_ranking/mvp/precompute_similarity.py` - Similarity computation

### Enterprise Implementation

**Technology Stack:**
- **Model**: CLIP ViT-B/32 (OpenAI)
- **Embeddings**: 512-dimensional multi-modal vectors
- **Storage**: Pinecone vector database
- **Backend**: FastAPI with async support

**Data Flow:**
1. Image/text processed through CLIP → 512-dim embeddings
2. Query embedding sent to Pinecone
3. Vector similarity search returns top-k results
4. Results formatted and returned to client

**Key Files:**
- `src/visual_search_ranking/enterprise/main.py` - FastAPI server
- `src/visual_search_ranking/enterprise/clip_service.py` - CLIP model wrapper
- `src/visual_search_ranking/enterprise/vector_db.py` - Vector DB abstraction

## API Endpoints

### MVP API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/random_products` | GET | Returns 5 random product IDs |
| `/similar/{product_id}` | GET | Returns similar products |
| `/recommend` | GET | Multi-product recommendations |
| `/health` | GET | Health check |

### Enterprise API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/stats` | GET | Vector DB statistics |
| `/search` | POST | Image-based search |
| `/search/text` | POST | Text-based search |
| `/embed` | POST | Generate embeddings |

## Data Directory Structure

```
data/
├── mvp/
│   ├── dataset_with_embeddings.json   # ResNet-50 embeddings (6.5GB)
│   ├── precomputed_similarities.json  # Similarity scores (1.1GB)
│   └── dataset.json                   # Product metadata
├── processed/
│   ├── products/
│   │   ├── images/                    # Product images
│   │   └── metadata.json              # Product metadata
│   └── rooms/
│       ├── images/                    # Room images
│       └── metadata.json              # Room metadata
└── embeddings/
    ├── products_embeddings.npz        # CLIP embeddings
    └── rooms_embeddings.npz           # CLIP embeddings
```

## Performance Characteristics

| Metric | MVP | Enterprise |
|--------|-----|------------|
| Query Latency | <10ms | <100ms (GPU) |
| Embedding Dimension | 2048 | 512 |
| Storage | 7.5GB JSON | ~100MB vectors |
| Scalability | Limited | Production-ready |
| Text Search | No | Yes |

## Security Considerations

- CORS configured to allow all origins (modify for production)
- No authentication implemented (add for production)
- Environment variables for API keys
- Input validation on all endpoints
