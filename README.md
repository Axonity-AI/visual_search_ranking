# Visual Search Ranking

AI-powered image recommendation and visual search system for Axonity AI.

## Overview

This project provides two visual similarity solutions:

1. **MVP Implementation** - ResNet-50 based visual similarity for artwork recommendations
2. **Enterprise Implementation** - CLIP-powered multi-modal search for production environments

### Features

- **Image-based search**: Find visually similar products/artworks
- **Text-based search**: Search using natural language descriptions (Enterprise)
- **Real-time inference**: Fast embedding generation with CLIP
- **Vector database integration**: Pinecone for production, Weaviate for development
- **Modern UI**: Glass morphism design with responsive layouts

## Quickstart (Development)

### Prerequisites

- Python 3.9+
- CUDA-capable GPU (optional, for faster inference)

### 1. Clone and Setup

```bash
git clone <repo-url>
cd visual_search_ranking

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Pinecone API key (for enterprise demo)
```

### 3. Run the Application

**Using the run script:**
```bash
./scripts/run_local.sh              # MVP demo
./scripts/run_local.sh --enterprise # Enterprise demo
```

**Or manually:**
```bash
# Terminal 1: Start backend
PYTHONPATH=src python -m visual_search_ranking.mvp.main

# Terminal 2: Serve frontend
python -m http.server 8001

# Open: http://localhost:8001/frontend/mvp/index.html
```

## Run Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/visual_search_ranking

# Run specific test file
pytest tests/test_mvp.py -v
```

## Project Structure

```
visual_search_ranking/
├── src/visual_search_ranking/     # Production code
│   ├── mvp/                       # ResNet-50 MVP implementation
│   │   ├── main.py               # FastAPI backend
│   │   ├── convert_to_json.py    # Embedding generation
│   │   └── precompute_similarity.py
│   ├── enterprise/                # CLIP enterprise implementation
│   │   ├── main.py               # FastAPI backend
│   │   ├── clip_service.py       # CLIP model wrapper
│   │   └── vector_db.py          # Vector DB abstraction
│   └── scripts/                   # Utility scripts
│       ├── mvp/                   # MVP utilities
│       └── enterprise/            # Enterprise utilities
├── tests/                         # Test suite
├── frontend/                      # Web frontends
│   ├── mvp/                      # MVP frontend
│   └── enterprise/               # Enterprise frontend
├── docs/                          # Documentation
├── docker/                        # Docker configuration
├── scripts/                       # Shell scripts
│   └── run_local.sh              # Local runner
├── data/                          # Data files (gitignored)
├── images/                        # Artwork images
├── requirements.txt               # Python dependencies
├── LICENSE                        # Proprietary license (Axonity Solutions Inc.)
└── README.md                      # This file
```

## Deploy Notes

### Docker Deployment

```bash
# Build image
docker build -t visual-search -f docker/Dockerfile .

# Run with docker-compose
docker-compose -f docker/compose.yml up

# With local Weaviate
docker-compose -f docker/compose.yml --profile local up
```

### Production Configuration

1. Set `VECTOR_DB_TYPE=pinecone` and configure Pinecone API key
2. Update CORS settings in `main.py` for your domain
3. Add authentication middleware as needed
4. Configure monitoring and logging

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /random_products` | Random product IDs (MVP) |
| `GET /similar/{id}` | Similar products (MVP) |
| `POST /search` | Image-based search (Enterprise) |
| `POST /search/text` | Text-based search (Enterprise) |

## Performance

| Metric | MVP | Enterprise |
|--------|-----|------------|
| Query Latency | <10ms | <100ms (GPU) |
| Embedding Dim | 2048 | 512 |
| Text Search | No | Yes |

## Tech Stack

- **Backend**: FastAPI, PyTorch, Transformers
- **Models**: ResNet-50 (MVP), CLIP ViT-B/32 (Enterprise)
- **Vector DB**: Pinecone, Weaviate
- **Frontend**: Vanilla JavaScript, HTML, CSS

## Contacts

**Axonity AI** - AI Solutions & Software Services

- Website: [axonityai.com](https://axonityai.com)
- Email: contact@axonityai.com

## License

Proprietary - Copyright (c) 2026 Axonity Solutions Inc. See [LICENSE](LICENSE) file.
