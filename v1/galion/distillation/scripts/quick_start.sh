#!/bin/bash
# Quick Start Script for Nexus Core Distillation
# 
# This script sets up the environment and starts the distillation process
#
# Usage:
#   ./scripts/quick_start.sh nano    # For 4GB nano model
#   ./scripts/quick_start.sh standard # For 16GB standard model

set -e

echo "=================================="
echo "Nexus Core Distillation Quick Start"
echo "=================================="
echo ""

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 [nano|standard]"
    exit 1
fi

MODEL_TYPE=$1

# Validate model type
if [ "$MODEL_TYPE" != "nano" ] && [ "$MODEL_TYPE" != "standard" ]; then
    echo "Error: Model type must be 'nano' or 'standard'"
    exit 1
fi

echo "Model type: $MODEL_TYPE"
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check CUDA
echo ""
echo "[2/6] Checking CUDA..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    echo "Warning: CUDA not found. Training will be slow on CPU."
fi

# Create virtual environment
echo ""
echo "[3/6] Setting up virtual environment..."
if [ ! -d "venv-distill" ]; then
    python3 -m venv venv-distill
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate venv
source venv-distill/bin/activate

# Install dependencies
echo ""
echo "[4/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Prepare directories
echo ""
echo "[5/6] Preparing directories..."
mkdir -p data outputs checkpoints exports results

# Download base model (placeholder)
echo ""
echo "[6/6] Checking base model..."
if [ ! -d "models/nexus-core-500gb" ]; then
    echo "Warning: Base model not found at models/nexus-core-500gb"
    echo "Please download the base model first:"
    echo "  wget https://models.galion.app/nexus-core-500gb.tar.gz"
    echo "  tar -xzf nexus-core-500gb.tar.gz -C models/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start distillation
echo ""
echo "=================================="
echo "Starting Distillation Process"
echo "=================================="
echo ""

if [ "$MODEL_TYPE" == "nano" ]; then
    CONFIG="configs/nano-4gb.yaml"
    OUTPUT="outputs/nexus-nano-4gb"
else
    CONFIG="configs/standard-16gb.yaml"
    OUTPUT="outputs/nexus-standard-16gb"
fi

echo "Configuration: $CONFIG"
echo "Output directory: $OUTPUT"
echo ""
echo "Press Ctrl+C to stop training"
echo ""

sleep 2

# Run distillation
python scripts/distill.py \
    --config $CONFIG \
    --output $OUTPUT \
    --wandb-project nexus-core-distillation

echo ""
echo "=================================="
echo "Distillation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Benchmark the model:"
echo "   python scripts/benchmark.py --model $OUTPUT/checkpoint-best"
echo ""
echo "2. Export the model:"
echo "   python scripts/export.py --model $OUTPUT/checkpoint-best --formats onnx tensorrt"
echo ""
echo "3. Deploy the model:"
echo "   See docs/DEPLOYMENT.md for deployment options"
echo ""

