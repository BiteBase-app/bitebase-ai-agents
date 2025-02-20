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
    libblas-dev \
    liblapack-dev \
    gfortran \
    poppler-utils \
    libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY # Install system dependencies
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
    libblas-dev \
    liblapack-dev \
    gfortran \
    poppler-utils \
    libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*# Install system dependencies
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
        libblas-dev \
        liblapack-dev \
        gfortran \
        poppler-utils \
        libgl1-mesa-glx && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set up entry point
CMD ["uvicorn", "restaurant_bi.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]


