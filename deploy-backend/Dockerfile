# ============================================
# GPU-ENABLED DOCKERFILE FOR TELECOM AI ASSISTANT
# ============================================
# Uses NVIDIA CUDA base image for GPU acceleration
# Supports: Ollama LLM, Whisper STT, Kokoro TTS

FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # CUDA settings
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install Python 3.11 and system dependencies (3.11 is more compatible with spacy/pydantic)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    gcc \
    g++ \
    git \
    curl \
    wget \
    libsndfile1 \
    ffmpeg \
    procps \
    zstd \
    # CUDA libraries for PyTorch
    libcudnn8 \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install Ollama (supports GPU automatically when CUDA is available)
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyTorch with CUDA 12.1 support FIRST (before other dependencies)
RUN pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Install other Python dependencies (skip torch/torchaudio as already installed)
RUN grep -v "^torch" requirements.txt | grep -v "^torchaudio" > requirements_no_torch.txt \
    && pip install --no-cache-dir -r requirements_no_torch.txt \
    && rm requirements_no_torch.txt

# Install aiosqlite for SQLite async support
RUN pip install --no-cache-dir aiosqlite

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY knowledge/ ./knowledge/

# Copy startup script and .env
COPY start.sh .
COPY .env .
RUN chmod +x start.sh

# Create directories for data persistence
RUN mkdir -p /app/chroma_db

# Expose ports (8080 for FastAPI, 11434 for Ollama)
EXPOSE 8080 11434

# Health check (increased start period for model download)
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=5 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run startup script (starts Ollama, pulls model, then runs app)
CMD ["./start.sh"]
