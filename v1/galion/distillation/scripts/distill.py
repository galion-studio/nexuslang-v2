#!/usr/bin/env python3
"""
Nexus Core Model Distillation Script

This script performs knowledge distillation from the base 500GB model
to smaller, efficient versions (4GB nano or 16GB standard).

Usage:
    python scripts/distill.py --config configs/nano-4gb.yaml
    python scripts/distill.py --config configs/standard-16gb.yaml
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import yaml
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_cosine_schedule_with_warmup,
)
import wandb

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DistillationTrainer:
    """Knowledge distillation trainer for Nexus Core models"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Models
        self.teacher_model = None
        self.student_model = None
        self.tokenizer = None
        
        # Training components
        self.optimizer = None
        self.scheduler = None
        self.train_dataloader = None
        self.val_dataloader = None
        
        # Metrics
        self.global_step = 0
        self.best_val_loss = float('inf')
        
    def load_models(self):
        """Load teacher and student models"""
        logger.info("Loading teacher model...")
        teacher_path = self.config['model']['base_model']
        
        self.teacher_model = AutoModelForCausalLM.from_pretrained(
            teacher_path,
            torch_dtype=torch.float16,
            device_map='auto',
            trust_remote_code=True
        )
        self.teacher_model.eval()
        
        logger.info("Initializing student model...")
        # Create student model architecture
        student_config = self._create_student_config()
        self.student_model = AutoModelForCausalLM.from_config(student_config)
        self.student_model.to(self.device)
        
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(teacher_path)
        
        logger.info(f"Teacher params: {sum(p.numel() for p in self.teacher_model.parameters()) / 1e9:.2f}B")
        logger.info(f"Student params: {sum(p.numel() for p in self.student_model.parameters()) / 1e9:.2f}B")
    
    def _create_student_config(self):
        """Create student model configuration"""
        from transformers import AutoConfig
        
        arch = self.config['architecture']
        base_config = AutoConfig.from_pretrained(self.config['model']['base_model'])
        
        # Modify config for student
        base_config.num_hidden_layers = arch['layers']
        base_config.hidden_size = arch['hidden_size']
        base_config.num_attention_heads = arch['attention_heads']
        base_config.intermediate_size = arch['intermediate_size']
        base_config.vocab_size = arch['vocab_size']
        base_config.max_position_embeddings = arch['max_sequence_length']
        
        return base_config
    
    def prepare_dataloaders(self):
        """Prepare training and validation dataloaders"""
        from datasets import load_dataset
        
        logger.info("Loading datasets...")
        
        # Load training data
        train_files = self.config['dataset']['training']
        train_dataset = load_dataset('json', data_files=train_files, split='train')
        
        # Load validation data
        val_files = self.config['dataset']['validation']
        val_dataset = load_dataset('json', data_files=val_files, split='train')
        
        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                max_length=self.config['architecture']['max_sequence_length'],
                padding='max_length'
            )
        
        logger.info("Tokenizing datasets...")
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)
        
        # Create dataloaders
        self.train_dataloader = DataLoader(
            train_dataset,
            batch_size=self.config['training']['batch_size'],
            shuffle=True,
            num_workers=4
        )
        
        self.val_dataloader = DataLoader(
            val_dataset,
            batch_size=self.config['training']['batch_size'],
            shuffle=False,
            num_workers=4
        )
        
        logger.info(f"Training samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
    
    def setup_optimizer(self):
        """Setup optimizer and scheduler"""
        training_config = self.config['training']
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.student_model.parameters(),
            lr=training_config['learning_rate'],
            betas=training_config['optimizer']['betas'],
            weight_decay=training_config['optimizer']['weight_decay']
        )
        
        # Scheduler
        num_training_steps = len(self.train_dataloader) * training_config['epochs']
        self.scheduler = get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=training_config['warmup_steps'],
            num_training_steps=num_training_steps
        )
        
        logger.info(f"Total training steps: {num_training_steps}")
    
    def distillation_loss(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor,
        labels: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """Calculate distillation loss"""
        
        temperature = self.config['distillation']['temperature']
        alpha = self.config['distillation']['alpha']
        beta = self.config['distillation']['beta']
        
        # Soft target loss (knowledge distillation)
        soft_student = F.log_softmax(student_logits / temperature, dim=-1)
        soft_teacher = F.softmax(teacher_logits / temperature, dim=-1)
        distill_loss = F.kl_div(
            soft_student,
            soft_teacher,
            reduction='batchmean'
        ) * (temperature ** 2)
        
        # Hard target loss (ground truth)
        student_loss = F.cross_entropy(
            student_logits.view(-1, student_logits.size(-1)),
            labels.view(-1),
            ignore_index=-100
        )
        
        # Combined loss
        total_loss = alpha * distill_loss + beta * student_loss
        
        return {
            'loss': total_loss,
            'distill_loss': distill_loss,
            'student_loss': student_loss
        }
    
    def train_epoch(self, epoch: int) -> float:
        """Train one epoch"""
        self.student_model.train()
        total_loss = 0
        
        progress_bar = tqdm(
            self.train_dataloader,
            desc=f"Epoch {epoch}",
            disable=not self.config.get('verbose', True)
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = input_ids.clone()
            
            # Teacher forward pass (no gradients)
            with torch.no_grad():
                teacher_outputs = self.teacher_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                teacher_logits = teacher_outputs.logits
            
            # Student forward pass
            student_outputs = self.student_model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            student_logits = student_outputs.logits
            
            # Calculate loss
            losses = self.distillation_loss(student_logits, teacher_logits, labels)
            loss = losses['loss']
            
            # Backward pass
            loss.backward()
            
            # Gradient accumulation
            if (batch_idx + 1) % self.config['training'].get('gradient_accumulation', 1) == 0:
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.student_model.parameters(), 1.0)
                
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
            
            # Update metrics
            total_loss += loss.item()
            self.global_step += 1
            
            # Log to wandb
            if self.global_step % 10 == 0:
                wandb.log({
                    'train/loss': loss.item(),
                    'train/distill_loss': losses['distill_loss'].item(),
                    'train/student_loss': losses['student_loss'].item(),
                    'train/lr': self.scheduler.get_last_lr()[0],
                    'global_step': self.global_step
                })
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'lr': f"{self.scheduler.get_last_lr()[0]:.2e}"
            })
        
        avg_loss = total_loss / len(self.train_dataloader)
        return avg_loss
    
    def validate(self) -> float:
        """Validate model"""
        self.student_model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(self.val_dataloader, desc="Validating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = input_ids.clone()
                
                # Teacher outputs
                teacher_outputs = self.teacher_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                # Student outputs
                student_outputs = self.student_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                # Calculate loss
                losses = self.distillation_loss(
                    student_outputs.logits,
                    teacher_outputs.logits,
                    labels
                )
                total_loss += losses['loss'].item()
        
        avg_loss = total_loss / len(self.val_dataloader)
        return avg_loss
    
    def save_checkpoint(self, epoch: int, output_dir: str):
        """Save model checkpoint"""
        checkpoint_dir = Path(output_dir) / f"checkpoint-epoch-{epoch}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving checkpoint to {checkpoint_dir}")
        
        # Save model
        self.student_model.save_pretrained(checkpoint_dir)
        self.tokenizer.save_pretrained(checkpoint_dir)
        
        # Save training state
        torch.save({
            'epoch': epoch,
            'global_step': self.global_step,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_loss': self.best_val_loss,
        }, checkpoint_dir / 'training_state.pt')
        
        logger.info("Checkpoint saved successfully")
    
    def train(self, output_dir: str):
        """Main training loop"""
        logger.info("Starting distillation training...")
        
        num_epochs = self.config['training']['epochs']
        
        for epoch in range(1, num_epochs + 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"Epoch {epoch}/{num_epochs}")
            logger.info(f"{'='*50}\n")
            
            # Train
            train_loss = self.train_epoch(epoch)
            logger.info(f"Training loss: {train_loss:.4f}")
            
            # Validate
            val_loss = self.validate()
            logger.info(f"Validation loss: {val_loss:.4f}")
            
            # Log to wandb
            wandb.log({
                'epoch': epoch,
                'train/epoch_loss': train_loss,
                'val/loss': val_loss
            })
            
            # Save checkpoint
            self.save_checkpoint(epoch, output_dir)
            
            # Save best model
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                best_dir = Path(output_dir) / "checkpoint-best"
                best_dir.mkdir(parents=True, exist_ok=True)
                self.student_model.save_pretrained(best_dir)
                self.tokenizer.save_pretrained(best_dir)
                logger.info(f"New best model! Validation loss: {val_loss:.4f}")
        
        logger.info("\n" + "="*50)
        logger.info("Training completed!")
        logger.info(f"Best validation loss: {self.best_val_loss:.4f}")
        logger.info("="*50)


def main():
    parser = argparse.ArgumentParser(description="Nexus Core Model Distillation")
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help='Path to configuration file (YAML)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='outputs/distilled',
        help='Output directory for checkpoints'
    )
    parser.add_argument(
        '--resume',
        type=str,
        default=None,
        help='Resume from checkpoint'
    )
    parser.add_argument(
        '--wandb-project',
        type=str,
        default='nexus-core-distillation',
        help='Weights & Biases project name'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize wandb
    wandb.init(
        project=args.wandb_project,
        name=config['model']['name'],
        config=config
    )
    
    # Create trainer
    trainer = DistillationTrainer(config)
    
    # Load models
    trainer.load_models()
    
    # Prepare data
    trainer.prepare_dataloaders()
    
    # Setup optimizer
    trainer.setup_optimizer()
    
    # Train
    trainer.train(args.output)
    
    # Finish wandb
    wandb.finish()
    
    logger.info("Distillation complete!")


if __name__ == '__main__':
    main()

