"""
FastAPI Backend for Enterprise Visual Search Platform

Provides real-time visual search endpoints for:
1. Product-to-product similarity search
2. Text-based product search

Key Features:
- Real-time CLIP embedding generation (<5ms per image)
- Sub-50ms vector search queries (Pinecone)
- Image upload support (base64, multipart, URL)
- Enterprise-level error handling and logging
"""

import base64
import io
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import requests
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl

from .clip_service import CLIPService
from .vector_db import SearchResult, get_vector_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances (initialized at startup)
clip_service: Optional[CLIPService] = None
vector_db = None

# Environment configuration
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "pinecone")
PINECONE_PRODUCTS_INDEX = os.getenv("PINECONE_PRODUCTS_INDEX", "visual-search-products")

# Data paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


# ============================================================================
# Pydantic Models
# ============================================================================

class SearchRequest(BaseModel):
    """Request model for image-based search."""
    image_url: Optional[HttpUrl] = Field(None, description="URL of the image to search")
    image_base64: Optional[str] = Field(None, description="Base64-encoded image data")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold")
    category_filter: Optional[str] = Field(None, description="Filter by product category")


class SearchResultItem(BaseModel):
    """Single search result item."""
    id: str = Field(..., description="Product or room ID")
    score: float = Field(..., description="Similarity score (0-1)")
    image_path: str = Field(..., description="Relative path to image")
    source: str = Field(..., description="Dataset source (fashion/ikea)")
    category: Optional[str] = Field(None, description="Product category (if applicable)")


class SearchResponse(BaseModel):
    """Response model for search endpoints."""
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")
    results: List[SearchResultItem] = Field(..., description="Ordered list of similar items")
    total_results: int = Field(..., description="Total number of results before filtering")


class TextSearchRequest(BaseModel):
    """Request model for text-based search."""
    query: str = Field(..., min_length=1, max_length=500, description="Text query to search for")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold")


class EmbedRequest(BaseModel):
    """Request model for embedding generation."""
    image_url: Optional[HttpUrl] = Field(None, description="URL of the image")
    image_base64: Optional[str] = Field(None, description="Base64-encoded image data")


class EmbedResponse(BaseModel):
    """Response model for embedding generation."""
    embedding: List[float] = Field(..., description="512-dimensional CLIP embedding")
    dimension: int = Field(512, description="Embedding dimension")
    generation_time_ms: float = Field(..., description="Time taken to generate embedding")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field("healthy", description="Service status")
    clip_model_loaded: bool = Field(..., description="CLIP model initialization status")
    vector_db_connected: bool = Field(..., description="Vector database connection status")
    vector_db_type: str = Field(..., description="Type of vector database in use")


# ============================================================================
# Startup & Shutdown
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    global clip_service, vector_db

    logger.info("=" * 80)
    logger.info("Starting Enterprise Visual Search Backend")
    logger.info("=" * 80)

    # Initialize CLIP service
    try:
        logger.info("Loading CLIP model...")
        clip_service = CLIPService(device=None)
        logger.info(f"CLIP model loaded on device: {clip_service.device}")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        raise

    # Initialize vector database
    try:
        logger.info(f"Connecting to {VECTOR_DB_TYPE} vector database...")
        vector_db = get_vector_db(db_type=VECTOR_DB_TYPE)
        logger.info(f"Connected to {VECTOR_DB_TYPE}")

        # Verify product index exists
        products_exists = vector_db.index_exists(PINECONE_PRODUCTS_INDEX)

        if not products_exists:
            logger.warning(f"Product index not found: {PINECONE_PRODUCTS_INDEX}")
        else:
            logger.info(f"Product index verified: {PINECONE_PRODUCTS_INDEX}")

    except Exception as e:
        logger.error(f"Failed to connect to vector database: {e}")
        raise

    logger.info("=" * 80)
    logger.info("Backend ready for requests")
    logger.info("=" * 80)

    yield

    # Cleanup on shutdown
    logger.info("Shutting down services...")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Enterprise Visual Search API",
    description="Real-time visual search for product similarity and room-to-product matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Helper Functions
# ============================================================================

def load_image_from_request(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
    file: Optional[UploadFile] = None
) -> Image.Image:
    """Load PIL Image from various input formats."""

    if file:
        # From uploaded file
        try:
            image_data = file.file.read()
            return Image.open(io.BytesIO(image_data)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    elif image_url:
        # From URL
        try:
            response = requests.get(str(image_url), timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch image from URL: {str(e)}")

    elif image_base64:
        # From base64
        try:
            image_data = base64.b64decode(image_base64)
            return Image.open(io.BytesIO(image_data)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="No image provided (file, URL, or base64)")


def format_search_results(
    results: List[SearchResult],
    min_score: float = 0.0
) -> List[SearchResultItem]:
    """Convert SearchResult objects to API response format."""

    formatted = []
    for result in results:
        if result.score < min_score:
            continue

        formatted.append(SearchResultItem(
            id=result.id,
            score=float(result.score),
            image_path=result.metadata.get("image_path", ""),
            source=result.metadata.get("source", "unknown"),
            category=result.metadata.get("category")
        ))

    return formatted


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Enterprise Visual Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "embed": "/embed",
            "stats": "/stats"
        },
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""

    clip_loaded = clip_service is not None
    db_connected = vector_db is not None

    return HealthResponse(
        status="healthy" if (clip_loaded and db_connected) else "degraded",
        clip_model_loaded=clip_loaded,
        vector_db_connected=db_connected,
        vector_db_type=VECTOR_DB_TYPE
    )


@app.get("/stats", tags=["Health"])
async def get_stats():
    """Get vector database index statistics."""

    if not vector_db:
        return {"status": "not_connected", "total_vectors": 0}

    try:
        stats = vector_db.get_index_stats(PINECONE_PRODUCTS_INDEX)
        return {
            "status": "connected",
            "index_name": PINECONE_PRODUCTS_INDEX,
            "total_vectors": int(stats.get("total_vectors", 0)) if stats else 0,
            "dimension": int(stats.get("dimension", 512)) if stats else 512
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"status": "error", "total_vectors": 0, "error": str(e)}


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_products(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Query(None),
    top_k: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    category_filter: Optional[str] = Query(None)
):
    """
    Product-to-Product Similarity Search

    Upload an image of a product to find visually similar products.
    """

    if not clip_service or not vector_db:
        raise HTTPException(status_code=503, detail="Services not initialized")

    start_time = time.time()

    try:
        # Load image
        image = load_image_from_request(image_url=image_url, file=file)

        # Generate embedding
        query_embedding = clip_service.encode_image(image)

        # Build filter
        filter_dict = None
        if category_filter:
            filter_dict = {"category": category_filter}

        # Search vector database
        results = vector_db.search(
            index_name=PINECONE_PRODUCTS_INDEX,
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )

        # Format results
        formatted_results = format_search_results(results, min_score=min_score)

        query_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Product search completed in {query_time_ms:.2f}ms - {len(formatted_results)} results")

        return SearchResponse(
            query_time_ms=query_time_ms,
            results=formatted_results,
            total_results=len(results)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search/text", response_model=SearchResponse, tags=["Search"])
async def search_by_text(request: TextSearchRequest):
    """
    Text-Based Product Search

    Search for products using natural language descriptions.
    """

    if not clip_service or not vector_db:
        raise HTTPException(status_code=503, detail="Services not initialized")

    start_time = time.time()

    try:
        # Generate text embedding using CLIP
        query_embedding = clip_service.encode_text(request.query)

        # Search vector database
        results = vector_db.search(
            index_name=PINECONE_PRODUCTS_INDEX,
            query_vector=query_embedding,
            top_k=request.top_k,
            filter_dict=None
        )

        # Format results
        formatted_results = format_search_results(results, min_score=request.min_score)

        query_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Text search '{request.query[:50]}...' completed in {query_time_ms:.2f}ms - {len(formatted_results)} results")

        return SearchResponse(
            query_time_ms=query_time_ms,
            results=formatted_results,
            total_results=len(results)
        )

    except Exception as e:
        logger.error(f"Text search error: {e}")
        raise HTTPException(status_code=500, detail=f"Text search failed: {str(e)}")


@app.post("/embed", response_model=EmbedResponse, tags=["Embedding"])
async def generate_embedding(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Query(None)
):
    """
    Real-Time Embedding Generation

    Generate CLIP embeddings for any image in real-time.
    """

    if not clip_service:
        raise HTTPException(status_code=503, detail="CLIP service not initialized")

    start_time = time.time()

    try:
        # Load image
        image = load_image_from_request(image_url=image_url, file=file)

        # Generate embedding
        embedding = clip_service.encode_image(image)

        generation_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Embedding generated in {generation_time_ms:.2f}ms")

        return EmbedResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding),
            generation_time_ms=generation_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()

    uvicorn.run(
        "visual_search_ranking.enterprise.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
