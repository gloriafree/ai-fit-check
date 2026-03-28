# Multi-stage build for AI Fit Check Backend
# ============================================

# Stage 1: Base image with Python and system dependencies
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies for image processing and GPU support
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libopenblas0 \
    libopenblas-dev \
    liblapack3 \
    liblapack-dev \
    libblas3 \
    libblas-dev \
    gcc \
    g++ \
    gfortran \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Stage 2: Build the application image
FROM base as builder

WORKDIR /app

# Copy requirements
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Runtime image
FROM base as runtime

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY server/ /app/server/
COPY ai_fit_check/ /app/ai_fit_check/
COPY configs/ /app/configs/
COPY models/ /app/models/

# Create data directories
RUN mkdir -p /app/server/data/persons /app/server/data/wardrobe

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FASHN_API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start the application
WORKDIR /app/server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
