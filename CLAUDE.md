# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an image-based recommendation system demo project for Axonity AI that uses deep learning (ResNet-50 and CLIP) to generate visual embeddings for images and compute similarity scores. The system provides product recommendations based on visual similarity.

**Project Status:** MVP and Enterprise demos complete

**Technology Stack:**
- Python with PyTorch for image embeddings
- FastAPI backend for serving recommendations
- Pinecone/Weaviate for vector database
- Vanilla JavaScript frontend with HTML/CSS

## Repository Structure (Axonity Standard Layout)

```
visual_search_ranking/
├── src/visual_search_ranking/     # Production code package
│   ├── __init__.py
│   ├── mvp/                       # MVP ResNet-50 implementation
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI backend server
│   │   ├── convert_to_json.py    # Image embedding generation
│   │   └── precompute_similarity.py  # Similarity computation
│   ├── enterprise/                # Enterprise CLIP implementation
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI backend server
│   │   ├── clip_service.py       # CLIP model wrapper
│   │   └── vector_db.py          # Vector DB abstraction
│   └── scripts/                   # Utility scripts
│       ├── __init__.py
│       ├── mvp/                   # MVP utilities
│       │   ├── shorten_dataset.py
│       │   └── rename_files.py
│       └── enterprise/            # Enterprise utilities
│           ├── download_datasets.py
│           ├── organize_datasets.py
│           ├── generate_embeddings.py
│           ├── index_vectors.py
│           └── test_clip.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_mvp.py               # MVP tests
│   └── test_enterprise.py        # Enterprise tests
├── frontend/                      # Web frontends
│   ├── mvp/                      # MVP frontend
│   │   ├── index.html            # Modern UI
│   │   └── view.html             # Legacy UI
│   └── enterprise/               # Enterprise frontend
│       └── index.html            # Product search UI
├── docs/                          # Documentation
│   ├── architecture.md           # System architecture
│   └── run_instructions.md       # Run instructions
├── docker/                        # Docker configuration
│   ├── Dockerfile                # Application container
│   └── compose.yml               # Docker compose
├── scripts/                       # Shell scripts
│   └── run_local.sh              # Development runner
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline
├── data/                          # Data files (gitignored)
│   └── mvp/                      # MVP datasets
├── images/                        # 14 art category folders
├── logs/                          # Server logs (generated)
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT license
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment template
├── README.md                      # Project overview
├── CLAUDE.md                      # This file
├── start_demo.bat                 # Windows startup script
└── start_demo.sh                  # Unix startup script
```

## Running the System

### Quick Start
```bash
# Using the run script
./scripts/run_local.sh              # MVP demo
./scripts/run_local.sh --enterprise # Enterprise demo
```

### Manual Start

**MVP Backend:**
```bash
PYTHONPATH=src python -m visual_search_ranking.mvp.main
# Serves on http://localhost:8000
```

**Enterprise Backend:**
```bash
PYTHONPATH=src python -m visual_search_ranking.enterprise.main
# Serves on http://localhost:8000
```

**Serve Frontend:**
```bash
python -m http.server 8001
# MVP: http://localhost:8001/frontend/mvp/index.html
# Enterprise: http://localhost:8001/frontend/enterprise/index.html
```

### Run Tests
```bash
pytest -v                          # Run all tests
pytest --cov=src/visual_search_ranking  # With coverage
```

## API Endpoints

### MVP API
- `GET /random_products` - Get 5 random product IDs
- `GET /similar/{product_id}?top_k=10` - Get similar products
- `GET /recommend?viewed=id1,id2&top_k=10` - Dynamic recommendations
- `GET /health` - Health check

### Enterprise API
- `GET /health` - Service health check
- `GET /stats` - Vector DB statistics
- `POST /search` - Image-based product search
- `POST /search/text` - Text-based product search
- `POST /embed` - Generate CLIP embedding

## Key Data Files

All MVP data files are located in `data/mvp/`:
- `dataset_with_embeddings.json` - ResNet-50 embeddings (6.5GB)
- `precomputed_similarities.json` - Cosine similarity scores (1.1GB)
- `dataset.json` - Product metadata without embeddings

## Architecture Notes

**Product ID Format:** `{category}_{filename_without_extension}`
- Example: `abstract_c90b7a03`, `landscape_abcd1234`

**MVP Similarity Strategy:**
- Compares only within same category
- Uses cosine similarity on 2048-dim ResNet-50 embeddings
- Stores top-k (default 100) similar items per product

**Enterprise Similarity Strategy:**
- Uses CLIP for multi-modal embeddings (512-dim)
- Real-time vector search via Pinecone
- Supports both image and text queries

**Frontend-Backend Contract:**
- Frontend constructs image URLs as: `{baseUrl}/{category}/{filename}.jpg`
- Product IDs split on underscore to extract category and filename

## Important Considerations

**Memory Requirements:** Loading large JSON files requires 8GB+ RAM.

**GPU Usage:** Scripts auto-detect CUDA. GPU highly recommended for large datasets.

**Image Categories (14 total):**
abstract, animal-painting, cityscape, figurative, flower-painting, genre-painting, landscape, marina, mythological-painting, nude-painting-nu, portrait, religious-painting, still-life, symbolic-painting

**CORS:** Configured to allow all origins - modify for production use.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run linting
flake8 src/ tests/

# Format code
black src/ tests/

# Run specific test
pytest tests/test_mvp.py -v

# Build Docker image
docker build -t visual-search -f docker/Dockerfile .
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `VECTOR_DB_TYPE` - pinecone or weaviate
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ENVIRONMENT` - Pinecone region
- `PINECONE_PRODUCTS_INDEX` - Index name
