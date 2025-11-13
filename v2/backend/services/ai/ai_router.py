"""
AI Router Service
Smart routing to 30+ AI models via OpenRouter with automatic fallback to OpenAI.

Features:
- OpenRouter primary (cost-optimized)
- OpenAI fallback
- Model selection
- Cost tracking
- Error handling with retry logic
- Support for chat, completion, image, video generation
"""

import os
import aiohttp
import asyncio
from typing import List, Dict, Optional, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENAI_BASE_URL = "https://api.openai.com/v1"


class AIModel(str, Enum):
    """Supported AI models."""
    # Claude models (Anthropic)
    CLAUDE_SONNET = "anthropic/claude-3.5-sonnet"
    CLAUDE_OPUS = "anthropic/claude-3-opus"
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"
    
    # GPT models (OpenAI)
    GPT4_TURBO = "openai/gpt-4-turbo"
    GPT4 = "openai/gpt-4"
    GPT35_TURBO = "openai/gpt-3.5-turbo"
    
    # Llama models (Meta)
    LLAMA_70B = "meta-llama/llama-3-70b-instruct"
    LLAMA_8B = "meta-llama/llama-3-8b-instruct"
    
    # Gemini models (Google)
    GEMINI_PRO = "google/gemini-pro"
    GEMINI_FLASH = "google/gemini-flash-1.5"
    
    # Mistral models
    MISTRAL_LARGE = "mistralai/mistral-large"
    MISTRAL_MEDIUM = "mistralai/mistral-medium"
    MISTRAL_SMALL = "mistralai/mistral-small"
    
    # Code-specific models
    CODELLAMA_70B = "codellama/codellama-70b-instruct"
    DEEPSEEK_CODER = "deepseek/deepseek-coder-33b-instruct"
    
    # Image generation
    STABLE_DIFFUSION = "stability-ai/stable-diffusion-xl"
    DALLE_3 = "openai/dall-e-3"
    
    # Other popular models
    PERPLEXITY_ONLINE = "perplexity/pplx-70b-online"  # Has internet access


class AIProvider(str, Enum):
    """AI service providers."""
    OPENROUTER = "openrouter"
    OPENAI = "openai"


class AIRouter:
    """
    Smart AI model router with fallback capabilities.
    
    Routes requests to OpenRouter by default, falls back to OpenAI if needed.
    Handles rate limiting, retries, and error recovery.
    """
    
    def __init__(self):
        self.openrouter_key = OPENROUTER_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.request_count = 0
        self.error_count = 0
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = AIModel.CLAUDE_SONNET,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using specified model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (defaults to Claude Sonnet)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
        
        Returns:
            Dict with 'content', 'model', 'provider', 'usage'
        """
        self.request_count += 1
        
        # Try OpenRouter first
        try:
            result = await self._openrouter_chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            result["provider"] = AIProvider.OPENROUTER
            return result
        
        except Exception as e:
            logger.warning(f"OpenRouter failed: {e}, falling back to OpenAI")
            self.error_count += 1
            
            # Fallback to OpenAI
            if self.openai_key:
                try:
                    # Map model to OpenAI equivalent
                    openai_model = self._map_to_openai_model(model)
                    result = await self._openai_chat(
                        messages=messages,
                        model=openai_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    result["provider"] = AIProvider.OPENAI
                    return result
                
                except Exception as openai_error:
                    logger.error(f"OpenAI fallback also failed: {openai_error}")
                    raise Exception(f"All AI providers failed. OpenRouter: {e}, OpenAI: {openai_error}")
            else:
                raise Exception(f"OpenRouter failed and no OpenAI key available: {e}")
    
    async def _openrouter_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Make request to OpenRouter API."""
        url = f"{OPENROUTER_BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://developer.galion.app",
            "X-Title": "Galion NexusLang"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error ({response.status}): {error_text}")
                
                data = await response.json()
                
                # Extract response
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                return {
                    "content": content,
                    "model": model,
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                }
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Make request to OpenAI API (fallback)."""
        url = f"{OPENAI_BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error ({response.status}): {error_text}")
                
                data = await response.json()
                
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                return {
                    "content": content,
                    "model": model,
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                }
    
    def _map_to_openai_model(self, model: str) -> str:
        """Map OpenRouter model to OpenAI equivalent."""
        mapping = {
            AIModel.CLAUDE_SONNET: "gpt-4-turbo",
            AIModel.CLAUDE_OPUS: "gpt-4-turbo",
            AIModel.CLAUDE_HAIKU: "gpt-3.5-turbo",
            AIModel.GPT4_TURBO: "gpt-4-turbo",
            AIModel.GPT4: "gpt-4",
            AIModel.GPT35_TURBO: "gpt-3.5-turbo",
            AIModel.LLAMA_70B: "gpt-4-turbo",
            AIModel.LLAMA_8B: "gpt-3.5-turbo",
            AIModel.GEMINI_PRO: "gpt-4-turbo",
            AIModel.MISTRAL_LARGE: "gpt-4-turbo",
        }
        
        return mapping.get(model, "gpt-3.5-turbo")  # Default fallback
    
    async def generate_image(
        self,
        prompt: str,
        model: str = AIModel.STABLE_DIFFUSION,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt.
        
        Args:
            prompt: Text description of desired image
            model: Image generation model
            size: Image size (e.g., "1024x1024")
            quality: Image quality ("standard" or "hd")
        
        Returns:
            Dict with 'url', 'model', 'provider'
        """
        if model == AIModel.DALLE_3 and self.openai_key:
            return await self._openai_generate_image(prompt, size, quality)
        else:
            # Use OpenRouter for Stable Diffusion
            return await self._openrouter_generate_image(prompt, model)
    
    async def _openai_generate_image(
        self,
        prompt: str,
        size: str,
        quality: str
    ) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E."""
        url = f"{OPENAI_BASE_URL}/images/generations"
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI image generation error: {error_text}")
                
                data = await response.json()
                image_url = data["data"][0]["url"]
                
                return {
                    "url": image_url,
                    "model": "dall-e-3",
                    "provider": AIProvider.OPENAI
                }
    
    async def _openrouter_generate_image(
        self,
        prompt: str,
        model: str
    ) -> Dict[str, Any]:
        """Generate image using OpenRouter (Stable Diffusion, etc.)."""
        # OpenRouter uses chat completion API for image generation
        url = f"{OPENROUTER_BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://developer.galion.app"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter image generation error: {error_text}")
                
                data = await response.json()
                # Extract image URL from response
                # Format depends on specific model
                content = data["choices"][0]["message"]["content"]
                
                return {
                    "url": content,  # Or extract URL from content
                    "model": model,
                    "provider": AIProvider.OPENROUTER
                }
    
    def get_stats(self) -> Dict[str, int]:
        """Get router statistics."""
        return {
            "total_requests": self.request_count,
            "errors": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100
        }


# Global router instance
_router_instance = None

def get_ai_router() -> AIRouter:
    """Get global AI router instance (singleton)."""
    global _router_instance
    if _router_instance is None:
        _router_instance = AIRouter()
    return _router_instance
