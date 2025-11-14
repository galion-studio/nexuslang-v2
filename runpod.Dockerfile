# Nexus Lang V2 Scientific Knowledge Enhancement - RunPod Deployment
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/workspace:/workspace/v2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3-dev \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional scientific packages
RUN pip install --no-cache-dir \
    numpy \
    scipy \
    matplotlib \
    pandas \
    scikit-learn \
    sympy \
    requests \
    aiohttp \
    fastapi \
    uvicorn \
    pydantic \
    psutil \
    beautifulsoup4 \
    lxml

# Copy the entire codebase
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/logs /workspace/data /workspace/shared

# Set permissions
RUN chmod +x /workspace/v2/run_dashboard_simple.py
RUN chmod +x /workspace/v2/launch_dashboard.py

# Create a health check script
RUN echo '#!/bin/bash\n\
python -c "import sys; sys.path.append(\"/workspace/v2\"); from scientific_dashboard import ScientificDashboard; print(\"Health check passed\")"' > /workspace/health_check.py && \
chmod +x /workspace/health_check.py

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /workspace/health_check.py || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "v2.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
