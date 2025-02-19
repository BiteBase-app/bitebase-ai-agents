# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    pkg-config \
    gcc \
    g++ \
    cmake \
    python3-dev \
    # Required for Prophet
    libstan-dev \
    # Required for some ML libraries
    libblas-dev \
    liblapack-dev \
    gfortran \
    # Required for PDF processing
    poppler-utils \
    # Required for image processing
    libgl1-mesa-glx \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional ML models
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download en_core_web_lg && \
    python -m nltk.downloader punkt vader_lexicon averaged_perceptron_tagger

# Create necessary directories
RUN mkdir -p \
    data/chroma \
    data/models \
    data/cache \
    logs

# Copy application code
COPY restaurant_bi/ restaurant_bi/
COPY README.md .

# Set up environment
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set up entry point
CMD ["uvicorn", "restaurant_bi.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1