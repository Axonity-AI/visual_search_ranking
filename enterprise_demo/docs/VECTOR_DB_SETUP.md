# Vector Database Setup Guide

This guide covers setting up vector databases for the Enterprise Visual Search Platform.

## Overview

The platform supports two vector database options:

1. **Pinecone** (Recommended for production demo)
   - Cloud-hosted, serverless
   - Free tier: 2GB storage, 100K vectors
   - Sub-10ms query latency
   - No infrastructure management

2. **Weaviate** (For local development)
   - Self-hosted via Docker
   - Full control over data
   - Good for testing and development

## Option 1: Pinecone Setup (Production Demo)

### Step 1: Create Pinecone Account

1. Go to [https://www.pinecone.io/](https://www.pinecone.io/)
2. Sign up for a free account
3. Verify your email address

### Step 2: Get API Key

1. Log in to Pinecone console
2. Navigate to "API Keys" section
3. Copy your API key (starts with `pcsk_...` or similar)
4. Note your environment region (e.g., `us-east-1`)

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your Pinecone credentials:
   ```env
   # Vector Database - Pinecone (Production Demo)
   PINECONE_API_KEY=your_actual_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_PRODUCTS_INDEX=visual-search-products
   PINECONE_ROOMS_INDEX=visual-search-rooms
   VECTOR_DB_TYPE=pinecone
   ```

### Step 4: Index Your Embeddings

Run the indexing script to upload your CLIP embeddings:

```bash
# Index both products and rooms
cd enterprise_demo
conda activate vis_similarity
python backend/scripts/index_vectors.py --db-type pinecone

# Or index separately
python backend/scripts/index_vectors.py --db-type pinecone --products-only
python backend/scripts/index_vectors.py --db-type pinecone --rooms-only
```

This will:
- Create two Pinecone indexes (products and rooms)
- Upload 46,736 product embeddings (512-dim)
- Upload 213 room embeddings (512-dim)
- Configure cosine similarity metric
- Display progress and performance metrics

Expected upload time: 5-10 minutes

### Step 5: Verify Indexing

The script will show final statistics:

```
[SUCCESS] Uploaded 46736 vectors in 180.32s (259.2 vectors/sec)
[INFO] Final index stats: {'total_vectors': 46736, 'dimension': 512, ...}
```

You can also check in Pinecone console:
1. Navigate to "Indexes" section
2. Click on `visual-search-products`
3. Verify vector count and dimensions

### Pinecone Free Tier Limits

- **Storage**: 2GB (enough for ~400K vectors at 512-dim)
- **Queries**: Unlimited
- **Indexes**: Up to 5
- **Namespaces**: Unlimited

**Our usage**:
- Products: ~46,736 vectors = ~94MB
- Rooms: ~213 vectors = ~0.4MB
- **Total**: ~94.4MB (well within free tier)

---

## Option 2: Weaviate Setup (Local Development)

### Step 1: Install Docker

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### Step 2: Start Weaviate

From the `enterprise_demo/` directory:

```bash
docker-compose up -d
```

This will:
- Pull Weaviate image
- Start Weaviate on `http://localhost:8080`
- Create persistent volume for data
- Enable health checks

### Step 3: Verify Weaviate is Running

Check health status:

```bash
curl http://localhost:8080/v1/.well-known/ready
```

Should return: `{"status": "healthy"}`

View logs:

```bash
docker-compose logs -f weaviate
```

### Step 4: Configure Environment

Edit `.env`:

```env
# Vector Database - Weaviate (Local Development)
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080
VECTOR_DB_TYPE=weaviate
```

### Step 5: Index Your Embeddings

```bash
python backend/scripts/index_vectors.py --db-type weaviate
```

This will:
- Create two Weaviate collections (VisualSearchProducts, VisualSearchRooms)
- Configure HNSW indexing with cosine distance
- Upload all embeddings with metadata

### Step 6: Manage Weaviate

```bash
# Stop Weaviate
docker-compose down

# Stop and remove data
docker-compose down -v

# View stats
curl http://localhost:8080/v1/meta
```

---

## Performance Comparison

| Feature | Pinecone | Weaviate (Local) |
|---------|----------|------------------|
| Setup Time | 5 min | 10 min |
| Query Latency | <10ms | 50-100ms |
| Scalability | Auto-scale | Manual |
| Cost (Demo) | Free | Free |
| Infrastructure | Managed | Self-hosted |
| Best For | Production demo | Development |

---

## Indexing Script Options

```bash
# Full usage
python backend/scripts/index_vectors.py \
  --db-type pinecone \
  --batch-size 100 \
  --embeddings-dir data/embeddings

# Products only
python backend/scripts/index_vectors.py --products-only

# Rooms only
python backend/scripts/index_vectors.py --rooms-only

# Custom batch size (larger = faster but more memory)
python backend/scripts/index_vectors.py --batch-size 200
```

---

## Troubleshooting

### Pinecone Errors

**Error**: `PINECONE_API_KEY not set`
- Solution: Check `.env` file has correct API key

**Error**: `Index already exists`
- Solution: Delete index in Pinecone console or use different name

**Error**: `Rate limit exceeded`
- Solution: Reduce batch size or wait a few minutes

### Weaviate Errors

**Error**: `Connection refused`
- Solution: Check Docker is running: `docker ps`
- Restart: `docker-compose restart`

**Error**: `Collection already exists`
- Solution: Delete via API or recreate with new name

---

## Next Steps

After indexing is complete:

1. **Test Queries**: Verify search works
   ```python
   from app.vector_db import get_vector_db
   db = get_vector_db("pinecone", api_key="xxx")
   results = db.search("visual-search-products", query_vector, top_k=10)
   ```

2. **Build Backend API**: Create FastAPI endpoints in `backend/app/main.py`

3. **Create Frontends**: Build product and room matching UIs

4. **Performance Testing**: Measure query latency and accuracy

---

## Architecture Notes

### Why Two Indexes?

Products and rooms are stored in separate indexes because:
- Different use cases (product similarity vs room matching)
- Different metadata schemas
- Easier filtering and management
- Better query performance

### Metadata Structure

**Products**:
```json
{
  "product_id": "fashion_abc123",
  "source": "fashion_products",
  "category": "dress",
  "image_path": "products/images/fashion_abc123.jpg"
}
```

**Rooms**:
```json
{
  "room_id": "ikea_room_001",
  "source": "ikea_interior",
  "room_type": "bedroom",
  "image_path": "rooms/images/ikea_room_001.jpg"
}
```

### Query Flow

1. User uploads image
2. Backend generates CLIP embedding (3-4ms on GPU)
3. Query vector database with embedding
4. Get top-k similar items with metadata
5. Return results to frontend

**Total latency**: <50ms for Pinecone, <150ms for Weaviate

---

## References

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [CLIP Model Details](https://huggingface.co/openai/clip-vit-base-patch32)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
