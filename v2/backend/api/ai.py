"""
AI API Endpoints
Provides access to multiple AI models through unified interface.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from ..core.security import get_current_user
from ..services.ai import get_ai_router, AIModel, AIRouter
from ..models.user import User


router = APIRouter(prefix="/ai", tags=["AI"])


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[ChatMessage]
    model: Optional[str] = Field(None, description="AI model to use (optional)")
    temperature: float = Field(0.7, ge=0, le=2, description="Response randomness (0-2)")
    max_tokens: int = Field(2000, ge=1, le=8000, description="Maximum response length")


class ChatResponse(BaseModel):
    """Chat completion response."""
    content: str = Field(..., description="Generated response")
    model: str = Field(..., description="Model that generated response")
    provider: str = Field(..., description="AI provider used")
    usage: Dict[str, Any] = Field(..., description="Token usage statistics")


class CodeGenerationRequest(BaseModel):
    """Code generation request."""
    prompt: str = Field(..., description="What code to generate")
    language: str = Field("nexuslang", description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")


class CodeAnalysisRequest(BaseModel):
    """Code analysis request."""
    code: str = Field(..., description="Code to analyze")
    language: str = Field("nexuslang", description="Programming language")
    analysis_type: str = Field("review", description="Type: review, debug, explain, optimize")


class QuickQueryRequest(BaseModel):
    """Quick query request."""
    prompt: str = Field(..., description="Your question or query")
    system_message: Optional[str] = Field(None, description="System instructions")


class SearchRequest(BaseModel):
    """AI-powered search request."""
    query: str = Field(..., description="Search query")
    context: Optional[str] = Field(None, description="Additional context")


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Generate chat completion using AI.
    
    Supports multiple models through OpenRouter:
    - Claude 3.5 Sonnet (best for reasoning)
    - GPT-4 Turbo (general purpose)
    - Llama 3 70B (open source)
    - And many more!
    
    Leave model blank to use the default (Claude 3.5 Sonnet).
    """
    try:
        # Convert Pydantic models to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        result = await ai.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            content=result["content"],
            model=result["model"],
            provider=result["provider"],
            usage=result["usage"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {str(e)}"
        )


@router.post("/code/generate")
async def generate_code(
    request: CodeGenerationRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Generate code using specialized code model.
    
    Uses CodeLlama 70B - optimized for code generation.
    """
    try:
        result = await ai.generate_code(
            prompt=request.prompt,
            language=request.language,
            context=request.context
        )
        
        return {
            "code": result["content"],
            "model": result["model"],
            "usage": result["usage"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )


@router.post("/code/analyze")
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Analyze code for errors, improvements, or explanations.
    
    Analysis types:
    - review: Code review with suggestions
    - debug: Find and explain bugs
    - explain: Explain what code does
    - optimize: Suggest performance improvements
    
    Uses Claude 3.5 Sonnet for best reasoning.
    """
    try:
        result = await ai.analyze_code(
            code=request.code,
            language=request.language,
            analysis_type=request.analysis_type
        )
        
        return {
            "analysis": result["content"],
            "model": result["model"],
            "usage": result["usage"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code analysis failed: {str(e)}"
        )


@router.post("/quick")
async def quick_query(
    request: QuickQueryRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Get quick answer using fastest model.
    
    Good for simple questions that don't need deep reasoning.
    Uses GPT-3.5 Turbo for speed and cost efficiency.
    """
    try:
        response = await ai.quick_response(
            prompt=request.prompt,
            system_message=request.system_message
        )
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/search")
async def ai_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Search and answer using AI with internet access.
    
    Uses Perplexity model which has real-time web access.
    Perfect for questions that need current information.
    """
    try:
        result = await ai.search_with_ai(
            query=request.query,
            context=request.context
        )
        
        return {
            "answer": result["content"],
            "model": result["model"],
            "usage": result["usage"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Get list of all available AI models organized by category.
    
    Returns models from:
    - Anthropic (Claude)
    - OpenAI (GPT)
    - Google (Gemini)
    - Meta (Llama)
    - Mistral
    - And more!
    """
    return {
        "available_models": ai.get_available_models(),
        "default_model": ai.default_model,
        "fallback_model": ai.fallback_model,
        "fast_model": ai.fast_model
    }


@router.get("/models/{model}")
async def get_model_info(
    model: str,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Get detailed information about a specific AI model.
    
    Includes:
    - Model name and provider
    - Strengths and use cases
    - Context length
    - Pricing information
    """
    info = ai.get_model_info(model)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model}' not found"
        )
    
    return info

