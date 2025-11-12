# Nexus Core Model Distillation

This directory contains configurations, scripts, and documentation for distilling the Nexus Core AI model into smaller, efficient versions.

## Available Model Versions

| Version | Size | Use Case | Performance |
|---------|------|----------|-------------|
| **Base** | 500GB | Full model with all capabilities | 100% accuracy |
| **Standard** | 16GB | Production deployment, balanced performance | ~95% accuracy |
| **Nano** | 4GB | Edge devices, mobile, resource-constrained | ~85% accuracy |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Distill to 16GB version
python scripts/distill.py --config configs/standard-16gb.yaml

# Distill to 4GB nano version
python scripts/distill.py --config configs/nano-4gb.yaml
```

## Directory Structure

```
distillation/
├── configs/           # Model configuration files
├── scripts/          # Distillation scripts
├── docs/             # Offline documentation
├── outputs/          # Distilled model outputs
└── checkpoints/      # Training checkpoints
```

## Documentation

- [Complete Distillation Guide](docs/DISTILLATION_GUIDE.md)
- [Model Architecture](docs/ARCHITECTURE.md)
- [Performance Benchmarks](docs/BENCHMARKS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

