# Quick Start - Visual Search Demo

Get running in 5 minutes.

---

## Prerequisites

- Python 3.9+
- Conda environment: `vis_similarity`
- Pinecone API key (free tier at [pinecone.io](https://www.pinecone.io))

---

## Setup

### 1. Create Conda Environment (First Time Only)

```bash
conda create -n vis_similarity python=3.9
conda activate vis_similarity
pip install -r enterprise_demo/requirements.txt
```

### 2. Configure Environment

```bash
cp enterprise_demo/.env.example enterprise_demo/.env
# Edit .env and add your Pinecone API key
```

---

## Start Demo

### One-Click (Recommended)

**Windows:** Double-click `start_demo.bat`

**Mac/Linux:**
```bash
./start_demo.sh
```

### Manual (If Scripts Fail)

**Terminal 1:**
```bash
conda activate vis_similarity
cd enterprise_demo/backend/app
python main.py
```

**Terminal 2:**
```bash
conda activate vis_similarity
python -m http.server 8001
```

**Open:** http://localhost:8001/enterprise_demo/frontend_product/index.html

---

## Stop Demo

**Windows:** Double-click `stop_demo.bat`

**Mac/Linux:**
```bash
./stop_demo.sh
```

---

## Test It

1. **Click any sample image** → See similar products
2. **Type:** `red leather handbag` → Press Enter
3. **Upload an image** → Click "Search Similar Products"

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'fastapi'"**
→ Activate conda environment first: `conda activate vis_similarity`

**"Port 8000 already in use"**
→ Run `stop_demo.bat` or `./stop_demo.sh` first

**Backend won't start**
→ Check logs: `type backend.log` (Windows) or `cat backend.log` (Mac/Linux)

**Frontend shows errors**
→ Ensure backend is running: `curl http://localhost:8000/health`

---

## What's Running

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Demo | http://localhost:8001/enterprise_demo/frontend_product/index.html |

---

**That's it!** See `DEMO_SCRIPT.md` for presentation guide.
