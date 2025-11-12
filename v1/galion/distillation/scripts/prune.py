#!/usr/bin/env python3
"""
Model Pruning Script for Nexus Core

Applies magnitude-based or structured pruning to reduce model size.

Usage:
    python scripts/prune.py --model outputs/stage1 --sparsity 0.6
"""

import argparse
import logging
from pathlib import Path

import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.utils.prune as prune

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPruner:
    """Prune transformer models"""
    
    def __init__(self, model_path: str, sparsity: float):
        self.model_path = model_path
        self.sparsity = sparsity
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load model and tokenizer"""
        logger.info(f"Loading model from {self.model_path}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float32
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Total parameters: {total_params / 1e9:.2f}B")
    
    def magnitude_pruning(self):
        """Apply magnitude-based pruning"""
        logger.info(f"Applying magnitude pruning with sparsity {self.sparsity}")
        
        parameters_to_prune = []
        
        # Prune all linear layers
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                parameters_to_prune.append((module, 'weight'))
        
        # Apply pruning
        prune.global_unstructured(
            parameters_to_prune,
            pruning_method=prune.L1Unstructured,
            amount=self.sparsity
        )
        
        logger.info("Pruning applied successfully")
    
    def structured_pruning(self, n: int = 2):
        """Apply structured pruning (prune entire rows/columns)"""
        logger.info(f"Applying structured pruning (L{n})")
        
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                prune.ln_structured(
                    module,
                    name='weight',
                    amount=self.sparsity,
                    n=n,
                    dim=0  # Prune output neurons
                )
        
        logger.info("Structured pruning applied")
    
    def make_pruning_permanent(self):
        """Remove pruning masks and make pruning permanent"""
        logger.info("Making pruning permanent...")
        
        for module in self.model.modules():
            if isinstance(module, nn.Linear):
                try:
                    prune.remove(module, 'weight')
                except:
                    pass
        
        # Count remaining parameters
        non_zero = sum(
            (p != 0).sum().item() for p in self.model.parameters()
        )
        total = sum(p.numel() for p in self.model.parameters())
        actual_sparsity = 1 - (non_zero / total)
        
        logger.info(f"Actual sparsity achieved: {actual_sparsity:.2%}")
        logger.info(f"Active parameters: {non_zero / 1e9:.2f}B / {total / 1e9:.2f}B")
    
    def save_model(self, output_path: str):
        """Save pruned model"""
        logger.info(f"Saving pruned model to {output_path}")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info("Model saved successfully")


def main():
    parser = argparse.ArgumentParser(description="Prune Nexus Core model")
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model to prune'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for pruned model'
    )
    parser.add_argument(
        '--sparsity',
        type=float,
        default=0.5,
        help='Sparsity level (0.0 to 1.0)'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['magnitude', 'structured'],
        default='magnitude',
        help='Pruning method'
    )
    
    args = parser.parse_args()
    
    # Create pruner
    pruner = ModelPruner(args.model, args.sparsity)
    
    # Load model
    pruner.load_model()
    
    # Apply pruning
    if args.method == 'magnitude':
        pruner.magnitude_pruning()
    elif args.method == 'structured':
        pruner.structured_pruning()
    
    # Make permanent
    pruner.make_pruning_permanent()
    
    # Save
    pruner.save_model(args.output)
    
    logger.info("Pruning complete!")


if __name__ == '__main__':
    main()

