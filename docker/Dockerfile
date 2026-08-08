# Visual Search Ranking - Dockerfile
# Multi-stage build for optimized image size

# ============================================================================
# Stage 1: Build stage
# ============================================================================
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
# requirements.txt pins plain torch==2.1.1, which pulls the default PyPI
# build -- that build bundles its own CUDA runtime libraries (several GB:
# nvidia-cublas/cudnn/cufft/etc.) even though this image never uses a GPU.
# Install the CPU-only build explicitly and exclude torch/torchvision from
# the general requirements pass, same fix as .github/workflows/ci.yml.
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels \
        torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && grep -v -E '^(torch|torchvision)(==|>=|$)' requirements.txt > requirements-nocuda.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements-nocuda.txt

# ============================================================================
# Stage 2: Runtime stage
# ============================================================================
FROM python:3.9-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies (libgl1 replaces deprecated libgl1-mesa-glx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY requirements.txt .

# Set Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8001

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command - start both servers
CMD ["sh", "-c", "python -m http.server 8001 --directory /app & python -m visual_search_ranking.enterprise.main"]
