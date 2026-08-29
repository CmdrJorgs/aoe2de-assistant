# ==============================================================================
# AoE2 Coach AI — Production FastAPI Backend Multi-Stage Dockerfile
# Stage 1: Build & Dependency Wheel Cache
# Stage 2: Hardened, Non-Root Minimal Production Runtime
# ==============================================================================

FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Install build tools & compiler dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast dependency compilation
COPY --from=ghcr.io/astral-sh/uv:0.6.0 /uv /uvx /bin/

# Copy dependency definition
COPY pyproject.toml ./

# Create virtual environment and install production dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache gunicorn && \
    uv pip install --no-cache -r pyproject.toml

# ==============================================================================
# Production Runtime Stage
# ==============================================================================
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

# Install runtime dependencies (OpenMP for ONNX, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user
RUN groupadd -g 10001 aoe2coach && \
    useradd -u 10001 -g aoe2coach -s /bin/bash -m aoe2coach

# Copy virtualenv from builder stage
COPY --from=builder --chown=aoe2coach:aoe2coach /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code and models
COPY --chown=aoe2coach:aoe2coach pyproject.toml ./
COPY --chown=aoe2coach:aoe2coach aoe2_coach ./aoe2_coach
COPY --chown=aoe2coach:aoe2coach models/artifacts ./models/artifacts
COPY --chown=aoe2coach:aoe2coach data/metadata ./data/metadata

# Configure environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=4 \
    LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# Drop to non-root user
USER aoe2coach

# Expose API port
EXPOSE 8000

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "-c", "aoe2_coach/api/gunicorn_conf.py", "aoe2_coach.api.app:app"]
