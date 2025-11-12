#!/usr/bin/env python3
"""
Benchmark Script for Nexus Core Models

Evaluates model performance on various benchmarks.

Usage:
    python scripts/benchmark.py --model outputs/nexus-nano-4gb-v1.0
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelBenchmark:
    """Benchmark transformer models"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_model(self):
        """Load model and tokenizer"""
        logger.info(f"Loading model from {self.model_path}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map='auto' if torch.cuda.is_available() else None
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        if not torch.cuda.is_available():
            self.model.to(self.device)
        
        self.model.eval()
        
        # Model info
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Total parameters: {total_params / 1e9:.2f}B")
    
    def benchmark_latency(self, num_samples: int = 100) -> Dict:
        """Benchmark inference latency"""
        logger.info("Benchmarking latency...")
        
        prompts = [
            "The quick brown fox",
            "Once upon a time",
            "In a galaxy far, far away",
            "To be or not to be"
        ] * (num_samples // 4)
        
        latencies = []
        tokens_per_sec = []
        
        for prompt in tqdm(prompts[:num_samples]):
            inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
            
            start = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=False
                )
            end = time.time()
            
            latency = (end - start) * 1000  # ms
            num_tokens = outputs.shape[1] - inputs['input_ids'].shape[1]
            tps = num_tokens / (latency / 1000)
            
            latencies.append(latency)
            tokens_per_sec.append(tps)
        
        results = {
            'latency_mean': sum(latencies) / len(latencies),
            'latency_p50': sorted(latencies)[len(latencies) // 2],
            'latency_p95': sorted(latencies)[int(len(latencies) * 0.95)],
            'latency_p99': sorted(latencies)[int(len(latencies) * 0.99)],
            'tokens_per_sec_mean': sum(tokens_per_sec) / len(tokens_per_sec),
            'tokens_per_sec_median': sorted(tokens_per_sec)[len(tokens_per_sec) // 2]
        }
        
        logger.info(f"Latency (mean): {results['latency_mean']:.2f} ms")
        logger.info(f"Tokens/sec (mean): {results['tokens_per_sec_mean']:.2f}")
        
        return results
    
    def benchmark_throughput(self, batch_sizes: List[int] = [1, 4, 8, 16]) -> Dict:
        """Benchmark throughput at different batch sizes"""
        logger.info("Benchmarking throughput...")
        
        results = {}
        
        prompt = "The quick brown fox jumps over the lazy dog"
        
        for batch_size in batch_sizes:
            if batch_size > 1 and not torch.cuda.is_available():
                logger.warning(f"Skipping batch size {batch_size} (CPU mode)")
                continue
                
            logger.info(f"Testing batch size: {batch_size}")
            
            # Prepare batch
            prompts = [prompt] * batch_size
            inputs = self.tokenizer(
                prompts,
                return_tensors='pt',
                padding=True
            ).to(self.device)
            
            # Warmup
            with torch.no_grad():
                self.model.generate(**inputs, max_new_tokens=10)
            
            # Benchmark
            start = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=False
                )
            end = time.time()
            
            # Calculate metrics
            total_time = end - start
            total_tokens = (outputs.shape[1] - inputs['input_ids'].shape[1]) * batch_size
            throughput = total_tokens / total_time
            
            results[f'batch_{batch_size}'] = {
                'time': total_time,
                'tokens': total_tokens,
                'throughput': throughput
            }
            
            logger.info(f"  Throughput: {throughput:.2f} tokens/sec")
        
        return results
    
    def benchmark_memory(self) -> Dict:
        """Benchmark memory usage"""
        logger.info("Benchmarking memory usage...")
        
        results = {}
        
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.empty_cache()
            
            # Measure model loading
            initial_memory = torch.cuda.memory_allocated() / (1024 ** 3)
            
            # Run inference
            prompt = "Test prompt for memory benchmarking"
            inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=128)
            
            peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 3)
            
            results = {
                'model_memory_gb': initial_memory,
                'peak_memory_gb': peak_memory,
                'inference_overhead_gb': peak_memory - initial_memory
            }
            
            logger.info(f"Model memory: {initial_memory:.2f} GB")
            logger.info(f"Peak memory: {peak_memory:.2f} GB")
        else:
            logger.warning("GPU not available, skipping memory benchmark")
            results = {'gpu_available': False}
        
        return results
    
    def benchmark_accuracy(self, test_file: str = None) -> Dict:
        """Benchmark model accuracy on test set"""
        logger.info("Benchmarking accuracy...")
        
        if not test_file:
            logger.warning("No test file provided, skipping accuracy benchmark")
            return {'skipped': True}
        
        # TODO: Implement accuracy benchmarks (MMLU, HumanEval, etc.)
        results = {
            'note': 'Accuracy benchmarking requires benchmark datasets'
        }
        
        return results
    
    def run_all_benchmarks(self, output_file: str = None) -> Dict:
        """Run all benchmarks"""
        logger.info("Running all benchmarks...")
        
        results = {
            'model_path': self.model_path,
            'device': str(self.device),
            'latency': self.benchmark_latency(num_samples=50),
            'throughput': self.benchmark_throughput(),
            'memory': self.benchmark_memory(),
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to {output_file}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Benchmark Nexus Core model")
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model to benchmark'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results/benchmark.json',
        help='Output file for results'
    )
    parser.add_argument(
        '--benchmarks',
        type=str,
        nargs='+',
        choices=['latency', 'throughput', 'memory', 'accuracy', 'all'],
        default=['all'],
        help='Benchmarks to run'
    )
    
    args = parser.parse_args()
    
    # Create benchmarker
    benchmark = ModelBenchmark(args.model)
    
    # Load model
    benchmark.load_model()
    
    # Run benchmarks
    if 'all' in args.benchmarks:
        results = benchmark.run_all_benchmarks(args.output)
    else:
        results = {}
        if 'latency' in args.benchmarks:
            results['latency'] = benchmark.benchmark_latency()
        if 'throughput' in args.benchmarks:
            results['throughput'] = benchmark.benchmark_throughput()
        if 'memory' in args.benchmarks:
            results['memory'] = benchmark.benchmark_memory()
        if 'accuracy' in args.benchmarks:
            results['accuracy'] = benchmark.benchmark_accuracy()
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
    
    logger.info("Benchmarking complete!")
    
    # Print summary
    print("\n" + "="*50)
    print("BENCHMARK SUMMARY")
    print("="*50)
    if 'latency' in results:
        print(f"Latency (mean): {results['latency']['latency_mean']:.2f} ms")
        print(f"Tokens/sec: {results['latency']['tokens_per_sec_mean']:.2f}")
    if 'memory' in results and 'model_memory_gb' in results['memory']:
        print(f"GPU Memory: {results['memory']['model_memory_gb']:.2f} GB")
    print("="*50)


if __name__ == '__main__':
    main()

