#!/usr/bin/env python3
"""
🚀 Galion Platform - AI Model Serving Service
Dedicated GPU-optimized model inference server

Features:
- Dynamic model loading and caching
- GPU memory management
- Batch processing capabilities
- Health monitoring and metrics
- RESTful API for model inference
"""

import os
import sys
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import psutil
import GPUtil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Galion AI Model Serving",
    description="GPU-optimized AI model inference service",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/app/models")
MAX_MODEL_MEMORY = os.getenv("MAX_MODEL_MEMORY", "8GB")
MODEL_PRELOAD_STRATEGY = os.getenv("MODEL_PRELOAD_STRATEGY", "on_demand")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
MAX_SEQUENCE_LENGTH = int(os.getenv("MAX_SEQUENCE_LENGTH", "2048"))
QUANTIZATION = os.getenv("QUANTIZATION", "4bit")

# GPU Configuration
GPU_MEMORY_FRACTION = float(os.getenv("GPU_MEMORY_FRACTION", "0.9"))
GPU_ALLOW_GROWTH = os.getenv("GPU_ALLOW_GROWTH", "true").lower() == "true"

# Model registry
loaded_models = {}
model_cache = {}

class ModelRequest(BaseModel):
    model_name: str = Field(..., description="Name of the model to use")
    prompt: str = Field(..., description="Input prompt for generation")
    max_tokens: int = Field(100, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Top-p sampling parameter")
    frequency_penalty: float = Field(0.0, description="Frequency penalty")
    presence_penalty: float = Field(0.0, description="Presence penalty")

class ModelResponse(BaseModel):
    model_name: str
    generated_text: str
    tokens_used: int
    processing_time: float
    gpu_memory_used: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    gpu_available: bool
    gpu_count: int
    gpu_memory_total: Optional[float] = None
    gpu_memory_used: Optional[float] = None
    gpu_utilization: Optional[float] = None
    loaded_models: List[str]
    system_memory_used: float

def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information and status"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {
                "available": False,
                "count": 0,
                "memory_total": None,
                "memory_used": None,
                "utilization": None
            }

        gpu = gpus[0]  # Use first GPU
        return {
            "available": True,
            "count": len(gpus),
            "memory_total": gpu.memoryTotal,
            "memory_used": gpu.memoryUsed,
            "utilization": gpu.load * 100
        }
    except Exception as e:
        logger.warning(f"Failed to get GPU info: {e}")
        return {
            "available": False,
            "count": 0,
            "memory_total": None,
            "memory_used": None,
            "utilization": None
        }

def load_model(model_name: str) -> Any:
    """Load a model dynamically"""
    if model_name in loaded_models:
        return loaded_models[model_name]

    try:
        logger.info(f"Loading model: {model_name}")

        # For now, we'll use a simple mock implementation
        # In production, this would load actual models like GPT, BERT, etc.
        class MockModel:
            def generate(self, prompt: str, **kwargs) -> str:
                # Mock response based on model type
                if "gpt" in model_name.lower():
                    return f"GPT Response to: {prompt[:50]}..."
                elif "bert" in model_name.lower():
                    return f"BERT Analysis: {prompt[:50]}... [Confidence: 0.95]"
                else:
                    return f"AI Response from {model_name}: {prompt[:50]}..."

        model = MockModel()
        loaded_models[model_name] = model
        model_cache[model_name] = datetime.now()

        logger.info(f"Successfully loaded model: {model_name}")
        return model

    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {model_name}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    gpu_info = get_gpu_info()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        gpu_available=gpu_info["available"],
        gpu_count=gpu_info["count"],
        gpu_memory_total=gpu_info["memory_total"],
        gpu_memory_used=gpu_info["memory_used"],
        gpu_utilization=gpu_info["utilization"],
        loaded_models=list(loaded_models.keys()),
        system_memory_used=psutil.virtual_memory().percent
    )

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "name": "gpt-3.5-turbo",
                "type": "text-generation",
                "description": "OpenAI GPT-3.5 Turbo for text generation"
            },
            {
                "name": "bert-base-uncased",
                "type": "text-classification",
                "description": "BERT model for text classification and analysis"
            },
            {
                "name": "galion-nexus",
                "type": "multimodal",
                "description": "Galion's custom multimodal AI model"
            }
        ],
        "loaded_models": list(loaded_models.keys()),
        "cache_info": {k: v.isoformat() for k, v in model_cache.items()}
    }

@app.post("/generate", response_model=ModelResponse)
async def generate_text(request: ModelRequest, background_tasks: BackgroundTasks):
    """Generate text using specified model"""
    import time
    start_time = time.time()

    try:
        # Load model
        model = load_model(request.model_name)

        # Generate response
        generated_text = model.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )

        processing_time = time.time() - start_time

        # Get GPU memory usage
        gpu_info = get_gpu_info()
        gpu_memory_used = gpu_info["memory_used"] if gpu_info["available"] else None

        # Estimate tokens used (rough approximation)
        tokens_used = len(generated_text.split()) + len(request.prompt.split())

        response = ModelResponse(
            model_name=request.model_name,
            generated_text=generated_text,
            tokens_used=tokens_used,
            processing_time=round(processing_time, 3),
            gpu_memory_used=gpu_memory_used
        )

        logger.info(f"Generated response for model {request.model_name} in {processing_time:.3f}s")

        # Background task to cleanup old models if needed
        background_tasks.add_task(cleanup_old_models)

        return response

    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/unload/{model_name}")
async def unload_model(model_name: str):
    """Unload a model from memory"""
    if model_name in loaded_models:
        del loaded_models[model_name]
        if model_name in model_cache:
            del model_cache[model_name]
        logger.info(f"Unloaded model: {model_name}")
        return {"status": "unloaded", "model": model_name}
    else:
        raise HTTPException(status_code=404, detail=f"Model not loaded: {model_name}")

async def cleanup_old_models():
    """Cleanup old models to free memory"""
    # Simple cleanup logic - unload models not used in last hour
    current_time = datetime.now()
    to_unload = []

    for model_name, load_time in model_cache.items():
        if (current_time - load_time).seconds > 3600:  # 1 hour
            to_unload.append(model_name)

    for model_name in to_unload:
        logger.info(f"Auto-unloading old model: {model_name}")
        await unload_model(model_name)

@app.on_event("startup")
async def startup_event():
    """Initialize the model serving service"""
    logger.info("🚀 Starting Galion AI Model Serving Service")
    logger.info(f"GPU Memory Fraction: {GPU_MEMORY_FRACTION}")
    logger.info(f"Batch Size: {BATCH_SIZE}")
    logger.info(f"Max Sequence Length: {MAX_SEQUENCE_LENGTH}")

    # Log GPU availability
    gpu_info = get_gpu_info()
    if gpu_info["available"]:
        logger.info(f"GPU Available: {gpu_info['count']} GPUs, {gpu_info['memory_total']}MB total memory")
    else:
        logger.warning("No GPU detected - running in CPU mode")

    logger.info("✅ AI Model Serving Service initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down AI Model Serving Service")
    loaded_models.clear()
    model_cache.clear()

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "start_models:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
        access_log=True
    )
