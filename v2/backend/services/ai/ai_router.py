"""
AI Router Service - Universal AI Gateway
Routes AI requests to different providers and models through OpenRouter.
Supports fallback mechanisms and model selection.
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
import httpx
import openai
from openai import AsyncOpenAI
import json
import asyncio
from enum import Enum

from ...core.config import settings


class AIModel(str, Enum):
    """
    Available AI models through OpenRouter.
    Each model has different strengths and pricing.
    """
    
    # Anthropic Claude Models (Best for reasoning, coding, analysis)
    CLAUDE_SONNET = "anthropic/claude-3.5-sonnet"  # Latest, most capable
    CLAUDE_OPUS = "anthropic/claude-3-opus"  # Most powerful, expensive
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"  # Fastest, cheapest
    
    # OpenAI GPT Models (General purpose, widely tested)
    GPT4_TURBO = "openai/gpt-4-turbo"  # Best GPT-4 version
    GPT4 = "openai/gpt-4"  # Standard GPT-4
    GPT35_TURBO = "openai/gpt-3.5-turbo"  # Fast and cheap
    
    # Google Gemini Models (Good for multimodal)
    GEMINI_PRO = "google/gemini-pro"  # Google's latest
    GEMINI_PRO_VISION = "google/gemini-pro-vision"  # With vision
    
    # Meta Llama Models (Open source, good value)
    LLAMA_70B = "meta-llama/llama-3-70b-instruct"  # Most capable Llama
    LLAMA_8B = "meta-llama/llama-3-8b-instruct"  # Fastest Llama
    
    # Mistral Models (European, privacy-focused)
    MISTRAL_LARGE = "mistralai/mistral-large"  # Most capable
    MISTRAL_MEDIUM = "mistralai/mistral-medium"  # Balanced
    MISTRAL_SMALL = "mistralai/mistral-small"  # Fast
    
    # Specialized Models
    CODELLAMA_70B = "meta-llama/codellama-70b-instruct"  # Best for code
    PERPLEXITY_ONLINE = "perplexity/pplx-70b-online"  # Has internet access
    

class AIProvider(str, Enum):
    """AI provider options."""
    OPENROUTER = "openrouter"  # Primary - access to all models
    OPENAI = "openai"  # Direct OpenAI API
    AUTO = "auto"  # Automatically choose best provider


class AIRouter:
    """
    Universal AI router that provides access to multiple AI models.
    Prioritizes OpenRouter for multi-model access with OpenAI as fallback.
    """
    
    def __init__(self):
        """Initialize AI router with configured providers."""
        
        # OpenRouter client (primary)
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.openrouter_url = settings.OPENROUTER_BASE_URL
        
        # OpenAI client (fallback)
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_client = None
        if self.openai_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_key)
        
        # Default models
        self.default_model = settings.DEFAULT_AI_MODEL
        self.fallback_model = settings.FALLBACK_AI_MODEL
        self.fast_model = settings.FAST_AI_MODEL
        
        # Provider preference
        self.provider = settings.AI_PROVIDER
        
        print(f"🤖 AI Router initialized:")
        print(f"   - Primary: OpenRouter ({self.default_model})")
        print(f"   - Fallback: {self.fallback_model}")
        print(f"   - Fast model: {self.fast_model}")
    
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using specified or default model.
        Automatically handles provider routing and fallbacks.
        
        Args:
            messages: List of chat messages [{"role": "user", "content": "..."}]
            model: AI model to use (defaults to DEFAULT_AI_MODEL)
            temperature: Randomness (0-2, lower = more focused)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Response dict with content, model used, usage stats
        """
        model = model or self.default_model
        
        try:
            # Try OpenRouter first (supports all models)
            if self.openrouter_key and (self.provider in ["openrouter", "auto"]):
                return await self._openrouter_chat(
                    messages, model, temperature, max_tokens, stream, **kwargs
                )
            
            # Fallback to direct OpenAI if model is OpenAI
            elif self.openai_client and model.startswith("openai/"):
                openai_model = model.replace("openai/", "")
                return await self._openai_chat(
                    messages, openai_model, temperature, max_tokens, stream, **kwargs
                )
            
            else:
                raise ValueError(
                    "No AI provider configured. Add OPENROUTER_API_KEY or OPENAI_API_KEY to .env"
                )
        
        except Exception as e:
            print(f"⚠️  AI request failed for {model}: {e}")
            
            # Try fallback model if different from attempted model
            if model != self.fallback_model:
                print(f"🔄 Trying fallback model: {self.fallback_model}")
                try:
                    return await self._openrouter_chat(
                        messages, self.fallback_model, temperature, max_tokens, stream, **kwargs
                    )
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed: {fallback_error}")
            
            raise Exception(f"AI request failed: {str(e)}")
    
    
    async def _openrouter_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make chat completion request to OpenRouter.
        OpenRouter provides unified access to all AI models.
        """
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nexuslang.dev",  # Optional: for rankings
            "X-Title": "NexusLang v2"  # Optional: for rankings
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.openrouter_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        # Format response consistently
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "provider": "openrouter",
            "usage": data.get("usage", {}),
            "finish_reason": data["choices"][0].get("finish_reason"),
            "raw_response": data
        }
    
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make chat completion request directly to OpenAI.
        Used as fallback or when explicitly requested.
        """
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Format response consistently
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "provider": "openai",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason,
            "raw_response": response
        }
    
    
    async def generate_code(
        self,
        prompt: str,
        language: str = "nexuslang",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code using the best coding model.
        Optimized for code generation tasks.
        """
        # Use specialized code model
        code_model = AIModel.CODELLAMA_70B
        
        system_message = f"""You are an expert {language} programmer.
Generate clean, efficient, well-documented code.
Follow best practices and include helpful comments."""
        
        if context:
            system_message += f"\n\nContext:\n{context}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(
            messages=messages,
            model=code_model,
            temperature=0.3,  # Lower temperature for more consistent code
            max_tokens=4000
        )
    
    
    async def analyze_code(
        self,
        code: str,
        language: str = "nexuslang",
        analysis_type: str = "review"
    ) -> Dict[str, Any]:
        """
        Analyze code for errors, improvements, or explanations.
        Uses Claude Sonnet for best reasoning.
        """
        analysis_prompts = {
            "review": "Review this code and suggest improvements:",
            "debug": "Find and explain bugs in this code:",
            "explain": "Explain what this code does in detail:",
            "optimize": "Suggest optimizations for this code:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["review"])
        
        messages = [
            {"role": "system", "content": f"You are an expert {language} code analyst."},
            {"role": "user", "content": f"{prompt}\n\n```{language}\n{code}\n```"}
        ]
        
        return await self.chat_completion(
            messages=messages,
            model=AIModel.CLAUDE_SONNET,  # Best for analysis
            temperature=0.5,
            max_tokens=3000
        )
    
    
    async def quick_response(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> str:
        """
        Get a quick response using the fastest model.
        Good for simple queries that don't need deep reasoning.
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        result = await self.chat_completion(
            messages=messages,
            model=self.fast_model,  # Use fast model
            temperature=0.7,
            max_tokens=500  # Shorter responses
        )
        
        return result["content"]
    
    
    async def search_with_ai(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search and answer using AI with internet access.
        Uses Perplexity model which has real-time web access.
        """
        prompt = f"Search and answer: {query}"
        
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        messages = [
            {"role": "system", "content": "You are a helpful search assistant with internet access."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(
            messages=messages,
            model=AIModel.PERPLEXITY_ONLINE,  # Has internet access
            temperature=0.7,
            max_tokens=2000
        )
    
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get list of all available models organized by category.
        """
        return {
            "anthropic": [
                AIModel.CLAUDE_SONNET,
                AIModel.CLAUDE_OPUS,
                AIModel.CLAUDE_HAIKU
            ],
            "openai": [
                AIModel.GPT4_TURBO,
                AIModel.GPT4,
                AIModel.GPT35_TURBO
            ],
            "google": [
                AIModel.GEMINI_PRO,
                AIModel.GEMINI_PRO_VISION
            ],
            "meta": [
                AIModel.LLAMA_70B,
                AIModel.LLAMA_8B,
                AIModel.CODELLAMA_70B
            ],
            "mistral": [
                AIModel.MISTRAL_LARGE,
                AIModel.MISTRAL_MEDIUM,
                AIModel.MISTRAL_SMALL
            ],
            "specialized": [
                AIModel.CODELLAMA_70B,
                AIModel.PERPLEXITY_ONLINE
            ]
        }
    
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        """
        model_info = {
            # Claude models
            AIModel.CLAUDE_SONNET: {
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "strengths": ["Reasoning", "Coding", "Analysis", "Long context"],
                "context_length": 200000,
                "cost_per_1m_tokens": 3.0
            },
            AIModel.CLAUDE_OPUS: {
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "strengths": ["Complex tasks", "Deep reasoning", "Creative writing"],
                "context_length": 200000,
                "cost_per_1m_tokens": 15.0
            },
            AIModel.CLAUDE_HAIKU: {
                "name": "Claude 3 Haiku",
                "provider": "Anthropic",
                "strengths": ["Speed", "Efficiency", "Simple tasks"],
                "context_length": 200000,
                "cost_per_1m_tokens": 0.25
            },
            
            # GPT models
            AIModel.GPT4_TURBO: {
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "strengths": ["General purpose", "Well-tested", "Reliable"],
                "context_length": 128000,
                "cost_per_1m_tokens": 10.0
            },
            AIModel.GPT35_TURBO: {
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "strengths": ["Speed", "Cost-effective", "Good for simple tasks"],
                "context_length": 16000,
                "cost_per_1m_tokens": 0.5
            },
            
            # Llama models
            AIModel.LLAMA_70B: {
                "name": "Llama 3 70B",
                "provider": "Meta",
                "strengths": ["Open source", "Good value", "Versatile"],
                "context_length": 8000,
                "cost_per_1m_tokens": 0.9
            },
            
            # Code models
            AIModel.CODELLAMA_70B: {
                "name": "CodeLlama 70B",
                "provider": "Meta",
                "strengths": ["Code generation", "Code completion", "Debugging"],
                "context_length": 100000,
                "cost_per_1m_tokens": 0.9
            },
            
            # Search models
            AIModel.PERPLEXITY_ONLINE: {
                "name": "Perplexity 70B Online",
                "provider": "Perplexity",
                "strengths": ["Internet access", "Real-time info", "Search"],
                "context_length": 4000,
                "cost_per_1m_tokens": 1.0
            }
        }
        
        return model_info.get(model, {
            "name": model,
            "provider": "Unknown",
            "strengths": ["General purpose"],
            "context_length": 4000,
            "cost_per_1m_tokens": 1.0
        })


# Global AI router instance
_ai_router: Optional[AIRouter] = None


def get_ai_router() -> AIRouter:
    """Get or create global AI router instance."""
    global _ai_router
    if _ai_router is None:
        _ai_router = AIRouter()
    return _ai_router

