#!/usr/bin/env python3
"""
Model Quantization Script for Nexus Core

Converts models from FP32/FP16 to INT8 for reduced memory and faster inference.

Usage:
    python scripts/quantize.py --model outputs/stage2 --method int8
"""

import argparse
import logging
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.quantization import quantize_dynamic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelQuantizer:
    """Quantize transformer models"""
    
    def __init__(self, model_path: str, method: str = 'int8'):
        self.model_path = model_path
        self.method = method
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
        
        # Get model size
        model_size = sum(
            p.numel() * p.element_size() for p in self.model.parameters()
        ) / (1024 ** 3)
        logger.info(f"Original model size: {model_size:.2f} GB")
    
    def dynamic_quantization_int8(self):
        """Apply dynamic INT8 quantization"""
        logger.info("Applying dynamic INT8 quantization...")
        
        self.model = quantize_dynamic(
            self.model,
            {torch.nn.Linear},
            dtype=torch.qint8
        )
        
        logger.info("INT8 quantization applied")
    
    def static_quantization_int8(self, calibration_data):
        """Apply static INT8 quantization with calibration"""
        logger.info("Applying static INT8 quantization...")
        
        # Prepare for quantization
        self.model.eval()
        self.model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        
        # Fuse modules
        torch.quantization.fuse_modules(
            self.model,
            [['linear', 'relu']],
            inplace=True
        )
        
        # Prepare
        torch.quantization.prepare(self.model, inplace=True)
        
        # Calibration
        logger.info("Running calibration...")
        with torch.no_grad():
            for batch in calibration_data:
                self.model(**batch)
        
        # Convert
        torch.quantization.convert(self.model, inplace=True)
        
        logger.info("Static quantization complete")
    
    def mixed_precision_quantization(self):
        """Apply mixed precision quantization (INT8 + FP16)"""
        logger.info("Applying mixed precision quantization...")
        
        # Sensitive layers to keep in FP16
        sensitive_modules = [
            'lm_head',
            'embed_tokens',
            'norm'
        ]
        
        # Quantize non-sensitive layers
        for name, module in self.model.named_modules():
            if isinstance(module, torch.nn.Linear):
                # Check if sensitive
                is_sensitive = any(s in name for s in sensitive_modules)
                
                if not is_sensitive:
                    # Quantize to INT8
                    module = quantize_dynamic(
                        module,
                        {torch.nn.Linear},
                        dtype=torch.qint8
                    )
                else:
                    # Keep in FP16
                    module.half()
        
        logger.info("Mixed precision quantization complete")
    
    def save_model(self, output_path: str):
        """Save quantized model"""
        logger.info(f"Saving quantized model to {output_path}")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Calculate new size
        model_size = sum(
            p.numel() * p.element_size() for p in self.model.parameters()
        ) / (1024 ** 3)
        logger.info(f"Quantized model size: {model_size:.2f} GB")
        
        logger.info("Model saved successfully")


def main():
    parser = argparse.ArgumentParser(description="Quantize Nexus Core model")
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model to quantize'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for quantized model'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['int8', 'int8_static', 'int8_mixed'],
        default='int8',
        help='Quantization method'
    )
    parser.add_argument(
        '--calibration-samples',
        type=int,
        default=1000,
        help='Number of calibration samples for static quantization'
    )
    
    args = parser.parse_args()
    
    # Create quantizer
    quantizer = ModelQuantizer(args.model, args.method)
    
    # Load model
    quantizer.load_model()
    
    # Apply quantization
    if args.method == 'int8':
        quantizer.dynamic_quantization_int8()
    elif args.method == 'int8_static':
        # TODO: Load calibration data
        logger.warning("Static quantization requires calibration data")
        quantizer.dynamic_quantization_int8()  # Fallback
    elif args.method == 'int8_mixed':
        quantizer.mixed_precision_quantization()
    
    # Save
    quantizer.save_model(args.output)
    
    logger.info("Quantization complete!")


if __name__ == '__main__':
    main()

