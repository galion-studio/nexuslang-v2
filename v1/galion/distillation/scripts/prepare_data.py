#!/usr/bin/env python3
"""
Data Preparation Script for Model Distillation

Prepares training data from various sources and formats.

Usage:
    python scripts/prepare_data.py --config configs/nano-4gb.yaml --output data/training
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict

from datasets import load_dataset
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparator:
    """Prepare training data for distillation"""
    
    def __init__(self, output_dir: str, max_samples: int = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_samples = max_samples
        
    def prepare_from_huggingface(self, dataset_name: str, split: str = 'train'):
        """Load and prepare data from HuggingFace datasets"""
        logger.info(f"Loading dataset: {dataset_name}")
        
        dataset = load_dataset(dataset_name, split=split)
        
        if self.max_samples:
            dataset = dataset.select(range(min(self.max_samples, len(dataset))))
        
        logger.info(f"Loaded {len(dataset)} samples")
        
        return dataset
    
    def prepare_from_jsonl(self, file_path: str) -> List[Dict]:
        """Load data from JSONL file"""
        logger.info(f"Loading data from {file_path}")
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
                if self.max_samples and len(data) >= self.max_samples:
                    break
        
        logger.info(f"Loaded {len(data)} samples")
        return data
    
    def prepare_conversation_data(self, sources: List[str]):
        """Prepare conversational data"""
        logger.info("Preparing conversation data...")
        
        all_conversations = []
        
        for source in sources:
            if source.startswith('hf://'):
                # HuggingFace dataset
                dataset_name = source.replace('hf://', '')
                dataset = self.prepare_from_huggingface(dataset_name)
                all_conversations.extend(dataset)
            else:
                # Local JSONL file
                data = self.prepare_from_jsonl(source)
                all_conversations.extend(data)
        
        # Save processed data
        output_file = self.output_dir / 'conversations.jsonl'
        with open(output_file, 'w', encoding='utf-8') as f:
            for conv in all_conversations:
                f.write(json.dumps(conv) + '\n')
        
        logger.info(f"Saved {len(all_conversations)} conversations to {output_file}")
    
    def generate_synthetic_data(
        self,
        teacher_model_path: str,
        prompts: List[str],
        samples_per_prompt: int = 10
    ):
        """Generate synthetic data from teacher model"""
        logger.info("Generating synthetic data from teacher model...")
        
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        # Load teacher model
        logger.info(f"Loading teacher model: {teacher_model_path}")
        model = AutoModelForCausalLM.from_pretrained(
            teacher_model_path,
            torch_dtype=torch.float16,
            device_map='auto'
        )
        tokenizer = AutoTokenizer.from_pretrained(teacher_model_path)
        
        synthetic_data = []
        
        for prompt in tqdm(prompts, desc="Generating"):
            for _ in range(samples_per_prompt):
                inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.9,
                    top_p=0.95
                )
                
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                synthetic_data.append({
                    'text': generated_text,
                    'source': 'synthetic',
                    'prompt': prompt
                })
        
        # Save synthetic data
        output_file = self.output_dir / 'synthetic.jsonl'
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in synthetic_data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"Generated {len(synthetic_data)} synthetic samples")
    
    def prepare_code_data(self, sources: List[str]):
        """Prepare code generation data"""
        logger.info("Preparing code data...")
        
        # Common code datasets
        code_datasets = [
            'codeparrot/github-code',
            'bigcode/the-stack',
        ]
        
        all_code = []
        
        for dataset_name in code_datasets[:1]:  # Limit to avoid huge downloads
            try:
                dataset = load_dataset(dataset_name, split='train', streaming=True)
                
                count = 0
                for item in dataset:
                    all_code.append(item)
                    count += 1
                    if self.max_samples and count >= self.max_samples // 2:
                        break
                
                logger.info(f"Loaded {count} samples from {dataset_name}")
            except Exception as e:
                logger.warning(f"Could not load {dataset_name}: {e}")
        
        # Save code data
        if all_code:
            output_file = self.output_dir / 'code.jsonl'
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in all_code:
                    f.write(json.dumps(item) + '\n')
            
            logger.info(f"Saved {len(all_code)} code samples")


def main():
    parser = argparse.ArgumentParser(description="Prepare training data")
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for prepared data'
    )
    parser.add_argument(
        '--max-samples',
        type=int,
        default=None,
        help='Maximum number of samples to prepare'
    )
    parser.add_argument(
        '--types',
        type=str,
        nargs='+',
        choices=['conversations', 'code', 'synthetic'],
        default=['conversations'],
        help='Types of data to prepare'
    )
    parser.add_argument(
        '--teacher-model',
        type=str,
        default=None,
        help='Teacher model for synthetic data generation'
    )
    
    args = parser.parse_args()
    
    # Create preparator
    preparator = DataPreparator(args.output, args.max_samples)
    
    # Prepare data
    if 'conversations' in args.types:
        # Default conversation sources
        sources = [
            'hf://OpenAssistant/oasst1',
        ]
        preparator.prepare_conversation_data(sources)
    
    if 'code' in args.types:
        preparator.prepare_code_data([])
    
    if 'synthetic' in args.types:
        if not args.teacher_model:
            logger.error("--teacher-model required for synthetic data generation")
        else:
            prompts = [
                "Explain the concept of",
                "Write a Python function to",
                "What is the difference between",
                "How do you"
            ]
            preparator.generate_synthetic_data(args.teacher_model, prompts)
    
    logger.info("Data preparation complete!")


if __name__ == '__main__':
    main()

