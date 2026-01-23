# Run Instructions

## Prerequisites

- Python 3.9+
- Conda (recommended) or virtualenv
- CUDA-capable GPU (optional, for faster inference)

## Quick Start

### One-Click Start (Recommended)

```bash
# Windows
start_demo.bat

# Mac/Linux
./start_demo.sh
```

This starts both the backend API and static file server.

### Using the Run Script

```bash
# Development mode
./scripts/run_local.sh

# Production mode
./scripts/run_local.sh --production
```

## Manual Setup

### 1. Create Virtual Environment

```bash
# Using conda
conda create -n vis_similarity python=3.9
conda activate vis_similarity

# Or using venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your Pinecone API key (enterprise only)
# PINECONE_API_KEY=your_key_here
```

### 4. Run MVP Demo

```bash
# Terminal 1: Start backend
cd src/visual_search_ranking/mvp
python main.py

# Terminal 2: Serve frontend
python -m http.server 8001

# Open: http://localhost:8001/frontend/mvp/index.html
```

### 5. Run Enterprise Demo

```bash
# Terminal 1: Start backend
python -m visual_search_ranking.enterprise.main

# Terminal 2: Serve frontend
python -m http.server 8001

# Open: http://localhost:8001/frontend/enterprise/index.html
```

## Running with Docker

```bash
# Build image
docker build -t visual-search -f docker/Dockerfile .

# Run container
docker run -p 8000:8000 -p 8001:8001 visual-search
```

## Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/visual_search_ranking

# Run specific test file
pytest tests/test_mvp.py -v
```

## Ports

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI server |
| Static Files | 8001 | Frontend serving |
| Weaviate | 8080 | Local vector DB (optional) |

## Troubleshooting

**ModuleNotFoundError**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Port already in use**
- Run `./stop_demo.sh` or `stop_demo.bat`
- Or manually kill processes on ports 8000/8001

**CUDA errors**
- Ensure CUDA toolkit is installed
- Or set `device=cpu` in configuration

**Vector DB connection errors**
- Verify Pinecone API key in `.env`
- Or start local Weaviate with `docker-compose up -d`
