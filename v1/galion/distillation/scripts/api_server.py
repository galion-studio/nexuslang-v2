#!/usr/bin/env python3
"""
Simple API Server for Nexus Core Distilled Models

Provides REST API for model inference.

Usage:
    python scripts/api_server.py --model outputs/nexus-nano-4gb-v1.0 --port 8080
"""

import argparse
import logging
import time
from typing import Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Nexus Core API",
    description="API for Nexus Core distilled models",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and tokenizer
model = None
tokenizer = None
device = None


# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt")
    max_tokens: int = Field(100, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Top-p sampling")
    top_k: int = Field(50, ge=1, description="Top-k sampling")
    do_sample: bool = Field(True, description="Whether to use sampling")


class GenerateResponse(BaseModel):
    text: str
    tokens_generated: int
    time_ms: float
    tokens_per_sec: float


class HealthResponse(BaseModel):
    status: str
    model: str
    device: str


def load_model(model_path: str):
    """Load model and tokenizer"""
    global model, tokenizer, device
    
    logger.info(f"Loading model from {model_path}")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map='auto' if torch.cuda.is_available() else None
    )
    
    if not torch.cuda.is_available():
        model.to(device)
    
    model.eval()
    
    # Log model info
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model loaded successfully")
    logger.info(f"Total parameters: {total_params / 1e9:.2f}B")


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    if model is None:
        raise RuntimeError("Model not loaded. Use --model argument.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nexus Core API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return HealthResponse(
        status="healthy",
        model=model.config.name_or_path,
        device=str(device)
    )


@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate text from prompt"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Tokenize input
        inputs = tokenizer(request.prompt, return_tensors='pt').to(device)
        input_length = inputs['input_ids'].shape[1]
        
        # Generate
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                do_sample=request.do_sample,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                pad_token_id=tokenizer.eos_token_id
            )
        
        end_time = time.time()
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Calculate metrics
        tokens_generated = outputs.shape[1] - input_length
        time_ms = (end_time - start_time) * 1000
        tokens_per_sec = tokens_generated / (time_ms / 1000)
        
        return GenerateResponse(
            text=generated_text,
            tokens_generated=tokens_generated,
            time_ms=time_ms,
            tokens_per_sec=tokens_per_sec
        )
    
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    total_params = sum(p.numel() for p in model.parameters())
    
    return {
        "model_name": model.config.name_or_path,
        "architecture": model.config.model_type,
        "parameters": total_params,
        "parameters_b": f"{total_params / 1e9:.2f}B",
        "vocab_size": model.config.vocab_size,
        "hidden_size": model.config.hidden_size,
        "num_layers": model.config.num_hidden_layers,
        "num_attention_heads": model.config.num_attention_heads,
        "max_position_embeddings": model.config.max_position_embeddings,
        "device": str(device)
    }


def main():
    parser = argparse.ArgumentParser(description="Nexus Core API Server")
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to bind to'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes'
    )
    
    args = parser.parse_args()
    
    # Load model
    load_model(args.model)
    
    # Start server
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"API docs available at http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers
    )


if __name__ == '__main__':
    main()

