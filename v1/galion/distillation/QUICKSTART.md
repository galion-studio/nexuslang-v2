# Nexus Core Model Distillation - Quick Start Guide

Get started with model distillation in minutes!

---

## Prerequisites

1. **Hardware**:
   - For **Nano (4GB)**: NVIDIA RTX 3060 or better (12GB VRAM)
   - For **Standard (16GB)**: NVIDIA A100 (40GB VRAM) recommended

2. **Software**:
   - Python 3.10+
   - CUDA 12.0+
   - 100GB+ free disk space

---

## Installation

### Step 1: Clone Repository

```bash
cd project-nexus/distillation
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv-distill
source venv-distill/bin/activate  # Linux/Mac
# or
.\venv-distill\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

---

## Quick Start: Distill Nano Model (4GB)

### Option 1: Automated (Recommended)

```bash
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh nano
```

### Option 2: Manual Steps

#### 1. Prepare Data

```bash
python scripts/prepare_data.py \
    --output data/nano-training \
    --max-samples 500000 \
    --types conversations
```

#### 2. Start Distillation

```bash
python scripts/distill.py \
    --config configs/nano-4gb.yaml \
    --output outputs/nexus-nano-4gb \
    --wandb-project nexus-distillation
```

**Expected Time**: 3-5 days on RTX 3090

#### 3. Benchmark Results

```bash
python scripts/benchmark.py \
    --model outputs/nexus-nano-4gb/checkpoint-best \
    --output results/nano-benchmarks.json
```

#### 4. Export Model

```bash
python scripts/export.py \
    --model outputs/nexus-nano-4gb/checkpoint-best \
    --formats pytorch onnx tensorrt \
    --output exports/nexus-nano-4gb-v1.0
```

---

## Quick Start: Distill Standard Model (16GB)

### Option 1: Automated

```bash
./scripts/quick_start.sh standard
```

### Option 2: Manual Steps

#### 1. Prepare Data

```bash
python scripts/prepare_data.py \
    --output data/standard-training \
    --max-samples 2000000 \
    --types conversations code
```

#### 2. Start Distillation

```bash
python scripts/distill.py \
    --config configs/standard-16gb.yaml \
    --output outputs/nexus-standard-16gb \
    --wandb-project nexus-distillation
```

**Expected Time**: 7-10 days on A100

#### 3. Benchmark Results

```bash
python scripts/benchmark.py \
    --model outputs/nexus-standard-16gb/checkpoint-best \
    --output results/standard-benchmarks.json
```

#### 4. Export Model

```bash
python scripts/export.py \
    --model outputs/nexus-standard-16gb/checkpoint-best \
    --formats pytorch onnx tensorrt safetensors \
    --output exports/nexus-standard-16gb-v1.0
```

---

## Test Your Distilled Model

### Option 1: Python API

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "outputs/nexus-nano-4gb/checkpoint-best"
)
tokenizer = AutoTokenizer.from_pretrained(
    "outputs/nexus-nano-4gb/checkpoint-best"
)

inputs = tokenizer("Hello, how are you?", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0]))
```

### Option 2: REST API

Start the API server:

```bash
python scripts/api_server.py \
    --model outputs/nexus-nano-4gb/checkpoint-best \
    --port 8080
```

Test the API:

```bash
curl -X POST http://localhost:8080/v1/generate \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Write a Python function to calculate fibonacci",
        "max_tokens": 200,
        "temperature": 0.7
    }'
```

### Option 3: Command Line

```bash
python -c "
from transformers import pipeline
generator = pipeline('text-generation', model='outputs/nexus-nano-4gb/checkpoint-best')
print(generator('Once upon a time', max_length=100))
"
```

---

## Monitor Training Progress

### Option 1: Weights & Biases (Recommended)

1. Create account at https://wandb.ai
2. Login: `wandb login`
3. View training: https://wandb.ai/your-project/nexus-distillation

### Option 2: TensorBoard

```bash
tensorboard --logdir outputs/nexus-nano-4gb/logs
# Open http://localhost:6006
```

### Option 3: Log Files

```bash
tail -f outputs/nexus-nano-4gb/training.log
```

---

## Common Issues & Solutions

### Issue 1: Out of Memory

**Solution**:
```bash
# Reduce batch size in config
sed -i 's/batch_size: 32/batch_size: 16/g' configs/nano-4gb.yaml

# Enable gradient checkpointing
# Add to config: gradient_checkpointing: true
```

### Issue 2: Slow Training

**Solution**:
```bash
# Use mixed precision
# Already enabled in configs (fp16/bf16)

# Use multiple GPUs
export CUDA_VISIBLE_DEVICES=0,1
python scripts/distill.py --config configs/standard-16gb.yaml
```

### Issue 3: Poor Accuracy

**Solution**:
```bash
# Increase training epochs
# Modify config: epochs: 20 (instead of 10)

# Add more training data
python scripts/prepare_data.py --max-samples 1000000
```

---

## Next Steps

1. **Read Full Documentation**:
   - [Complete Distillation Guide](docs/DISTILLATION_GUIDE.md)
   - [Architecture Details](docs/ARCHITECTURE.md)
   - [Benchmark Results](docs/BENCHMARKS.md)
   - [Deployment Guide](docs/DEPLOYMENT.md)

2. **Optimize Your Model**:
   - Apply pruning: `python scripts/prune.py`
   - Quantize to INT8: `python scripts/quantize.py`
   - Convert to TensorRT for faster inference

3. **Deploy to Production**:
   - Docker: See `docs/DEPLOYMENT.md#docker`
   - Kubernetes: See `docs/DEPLOYMENT.md#kubernetes`
   - Serverless: See `docs/DEPLOYMENT.md#serverless`

4. **Join Community**:
   - Discord: https://discord.gg/nexus-core
   - GitHub: https://github.com/nexus-core
   - Email: support@galion.app

---

## Performance Expectations

### Nano Model (4GB)

| Metric | Value |
|--------|-------|
| Model Size | 4 GB |
| Accuracy vs Base | 85% |
| Inference Speed | 50 tokens/sec (RTX 3060) |
| Training Time | 7-10 days |
| GPU Required | 12GB VRAM |

### Standard Model (16GB)

| Metric | Value |
|--------|-------|
| Model Size | 16 GB |
| Accuracy vs Base | 95% |
| Inference Speed | 100 tokens/sec (RTX 4090) |
| Training Time | 9-15 days |
| GPU Required | 24GB VRAM |

---

## Cost Estimates

### Training Costs (AWS)

- **Nano**: $300-500 (g5.2xlarge for 7 days)
- **Standard**: $1,500-2,500 (p4d.24xlarge for 10 days)

### Inference Costs (Monthly)

- **Nano**: $40/month (g4dn.xlarge)
- **Standard**: $300/month (g5.2xlarge)

---

## Support

Need help? We're here!

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: support@galion.app
- **Discord**: Nexus Core Community

---

**Happy Distilling! 🚀**

*Built with ❤️ by the Nexus Core Team*

