#!/usr/bin/env python3
"""
Model Export Script for Nexus Core

Exports models to various formats (ONNX, TensorRT, CoreML, etc.)

Usage:
    python scripts/export.py --model outputs/nexus-nano-4gb-v1.0 --formats onnx tensorrt
"""

import argparse
import logging
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelExporter:
    """Export models to various formats"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
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
        self.model.eval()
        
    def export_pytorch(self, output_dir: str):
        """Export as PyTorch checkpoint"""
        logger.info("Exporting to PyTorch format...")
        
        output_path = Path(output_dir) / 'pytorch'
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        
        logger.info(f"PyTorch model saved to {output_path}")
    
    def export_onnx(self, output_dir: str):
        """Export to ONNX format"""
        logger.info("Exporting to ONNX format...")
        
        try:
            import onnx
            from transformers.onnx import export as onnx_export
            
            output_path = Path(output_dir) / 'onnx'
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Prepare dummy input
            dummy_input = self.tokenizer(
                "Hello world",
                return_tensors='pt'
            )
            
            # Export
            torch.onnx.export(
                self.model,
                (dummy_input['input_ids'], dummy_input['attention_mask']),
                output_path / 'model.onnx',
                input_names=['input_ids', 'attention_mask'],
                output_names=['logits'],
                dynamic_axes={
                    'input_ids': {0: 'batch', 1: 'sequence'},
                    'attention_mask': {0: 'batch', 1: 'sequence'},
                    'logits': {0: 'batch', 1: 'sequence'}
                },
                opset_version=14
            )
            
            # Save tokenizer
            self.tokenizer.save_pretrained(output_path)
            
            logger.info(f"ONNX model saved to {output_path}")
            
        except ImportError:
            logger.error("ONNX export requires 'onnx' package")
    
    def export_tensorrt(self, output_dir: str):
        """Export to TensorRT format"""
        logger.info("Exporting to TensorRT format...")
        
        try:
            import tensorrt as trt
            
            # First export to ONNX
            onnx_dir = Path(output_dir) / 'onnx_temp'
            self.export_onnx(str(onnx_dir))
            
            # Convert ONNX to TensorRT
            output_path = Path(output_dir) / 'tensorrt'
            output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Converting ONNX to TensorRT...")
            # TODO: Implement TensorRT conversion
            # This requires trtexec or Python TensorRT API
            
            logger.warning("TensorRT export is a placeholder - requires trtexec")
            logger.info(f"TensorRT output directory: {output_path}")
            
        except ImportError:
            logger.error("TensorRT export requires 'tensorrt' package")
    
    def export_safetensors(self, output_dir: str):
        """Export to SafeTensors format"""
        logger.info("Exporting to SafeTensors format...")
        
        try:
            from safetensors.torch import save_file
            
            output_path = Path(output_dir) / 'safetensors'
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Get state dict
            state_dict = self.model.state_dict()
            
            # Save as safetensors
            save_file(state_dict, output_path / 'model.safetensors')
            
            # Save config and tokenizer
            self.model.config.save_pretrained(output_path)
            self.tokenizer.save_pretrained(output_path)
            
            logger.info(f"SafeTensors model saved to {output_path}")
            
        except ImportError:
            logger.error("SafeTensors export requires 'safetensors' package")
    
    def export_coreml(self, output_dir: str):
        """Export to CoreML format (for Apple devices)"""
        logger.info("Exporting to CoreML format...")
        
        try:
            import coremltools as ct
            
            output_path = Path(output_dir) / 'coreml'
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Prepare traced model
            dummy_input = self.tokenizer(
                "Hello world",
                return_tensors='pt'
            )
            
            traced_model = torch.jit.trace(
                self.model,
                (dummy_input['input_ids'], dummy_input['attention_mask'])
            )
            
            # Convert to CoreML
            mlmodel = ct.convert(
                traced_model,
                inputs=[
                    ct.TensorType(name="input_ids", shape=(1, ct.RangeDim())),
                    ct.TensorType(name="attention_mask", shape=(1, ct.RangeDim()))
                ]
            )
            
            mlmodel.save(str(output_path / 'model.mlmodel'))
            
            logger.info(f"CoreML model saved to {output_path}")
            
        except ImportError:
            logger.error("CoreML export requires 'coremltools' package")
    
    def optimize_for_inference(self):
        """Optimize model for inference"""
        logger.info("Optimizing model for inference...")
        
        # Fuse operations
        try:
            self.model = torch.jit.optimize_for_inference(
                torch.jit.script(self.model)
            )
            logger.info("Model optimized for inference")
        except:
            logger.warning("Could not optimize model (jit script failed)")


def main():
    parser = argparse.ArgumentParser(description="Export Nexus Core model")
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model to export'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='exports',
        help='Output directory for exports'
    )
    parser.add_argument(
        '--formats',
        type=str,
        nargs='+',
        choices=['pytorch', 'onnx', 'tensorrt', 'safetensors', 'coreml', 'all'],
        default=['pytorch'],
        help='Export formats'
    )
    parser.add_argument(
        '--optimize-inference',
        action='store_true',
        help='Optimize for inference'
    )
    
    args = parser.parse_args()
    
    # Create exporter
    exporter = ModelExporter(args.model)
    
    # Load model
    exporter.load_model()
    
    # Optimize
    if args.optimize_inference:
        exporter.optimize_for_inference()
    
    # Export formats
    formats = args.formats
    if 'all' in formats:
        formats = ['pytorch', 'onnx', 'safetensors']
    
    for fmt in formats:
        if fmt == 'pytorch':
            exporter.export_pytorch(args.output)
        elif fmt == 'onnx':
            exporter.export_onnx(args.output)
        elif fmt == 'tensorrt':
            exporter.export_tensorrt(args.output)
        elif fmt == 'safetensors':
            exporter.export_safetensors(args.output)
        elif fmt == 'coreml':
            exporter.export_coreml(args.output)
    
    logger.info("Export complete!")
    logger.info(f"All exports saved to: {args.output}")


if __name__ == '__main__':
    main()

