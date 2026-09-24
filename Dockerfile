# ==========================================
# Stage 1: Build Frontend (Vite + React + TS)
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Accept optional build-time API URL override
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend (FastAPI + LangGraph + Graph-RAG)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
# libgomp1 is required for onnxruntime (FastEmbed & FlashRank)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Create data directory for local SQLite / cache storage
RUN mkdir -p /app/data

# Copy backend codebase
COPY . .

# Copy built frontend assets to FastAPI static mount path
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose API port
EXPOSE 8000

# Health check to monitor container status
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
