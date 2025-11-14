"""
AI API Endpoints
REST API for AI generation (chat, code, images, video, TTS, STT).

All endpoints require authentication and consume user credits.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ..services.ai.ai_router import get_ai_router, AIModel, AIRouter
from ..api.auth import get_current_user
from ..core.database import get_db
from ..models.user import User
from ..services.grokopedia.search import get_search_engine
from ..ai.rag.rag_system import RAGSystem

router = APIRouter(prefix="/ai", tags=["AI"])


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    model: Optional[str] = Field(AIModel.CLAUDE_SONNET, description="Model to use")
    temperature: Optional[float] = Field(0.7, ge=0, le=1, description="Sampling temperature")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Max tokens to generate")


class ChatResponse(BaseModel):
    """Chat completion response."""
    content: str = Field(..., description="Generated response")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider (openrouter/openai)")
    usage: Dict = Field(..., description="Token usage statistics")
    credits_used: float = Field(..., description="Credits deducted")


class DeepSearchRequest(BaseModel):
    """Deep search request combining RAG and AI chat."""
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    search_query: Optional[str] = Field(None, description="Specific search query (defaults to last user message)")
    model: Optional[str] = Field(AIModel.CLAUDE_SONNET, description="Model to use")
    temperature: Optional[float] = Field(0.7, ge=0, le=1, description="Sampling temperature")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Max tokens to generate")
    search_limit: Optional[int] = Field(5, ge=1, le=20, description="Max search results to include")
    include_sources: Optional[bool] = Field(True, description="Include source documents in response")


class SearchResult(BaseModel):
    """Individual search result from knowledge base."""
    document_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content preview")
    score: float = Field(..., description="Relevance score")
    source: str = Field(..., description="Source of the document")
    highlights: List[str] = Field(default_factory=list, description="Highlighted text snippets")


class DeepSearchResponse(BaseModel):
    """Deep search response with RAG-enhanced AI chat."""
    content: str = Field(..., description="Generated response")
    search_results: List[SearchResult] = Field(default_factory=list, description="Knowledge base search results")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider (openrouter/openai)")
    usage: Dict = Field(..., description="Token usage statistics")
    credits_used: float = Field(..., description="Credits deducted")
    search_performed: bool = Field(..., description="Whether knowledge base search was performed")
    confidence_score: float = Field(..., description="Confidence in the response")


class CodeGenerationRequest(BaseModel):
    """Code generation request."""
    prompt: str = Field(..., description="What code to generate")
    language: Optional[str] = Field("python", description="Programming language")
    model: Optional[str] = Field(AIModel.CLAUDE_SONNET, description="Model to use")


class ImageGenerationRequest(BaseModel):
    """Image generation request."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Image description")
    model: Optional[str] = Field(AIModel.STABLE_DIFFUSION, description="Model to use")
    size: Optional[str] = Field("1024x1024", description="Image size")
    quality: Optional[str] = Field("standard", description="Quality (standard/hd)")


class ImageGenerationResponse(BaseModel):
    """Image generation response."""
    url: str = Field(..., description="Generated image URL")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider")
    credits_used: float = Field(..., description="Credits deducted")


# Credit cost calculation
CREDIT_COSTS = {
    "chat_per_1k_tokens": 0.01,  # $0.01 per 1k tokens
    "image_generation": 1.0,     # 1 credit per image
    "video_generation": 5.0,     # 5 credits per video
    "tts_per_char": 0.0001,      # $0.0001 per character
    "stt_per_minute": 0.1        # 0.1 credits per minute
}


def calculate_chat_credits(usage: Dict) -> float:
    """Calculate credits used for chat completion."""
    total_tokens = usage.get("total_tokens", 0)
    return (total_tokens / 1000) * CREDIT_COSTS["chat_per_1k_tokens"]


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router),
    db: Session = Depends(get_db)
):
    """
    Generate AI chat completion.
    
    Supports 30+ models via OpenRouter:
    - Claude 3.5 Sonnet (best for reasoning)
    - GPT-4 Turbo (general purpose)
    - Llama 3 70B (open source)
    - Many more!
    
    Costs: ~0.01 credits per 1000 tokens
    """
    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    try:
        # Generate response
        result = await ai.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Calculate credits using new pricing system
        from ..services.billing.credit_service import get_credit_service
        credit_service = get_credit_service(db)

        credits_used = credit_service.calculate_ai_cost(
            "chat",
            tokens=result["usage"].get("total_tokens", 0)
        )

        # Deduct credits with proper error handling
        if not credit_service.deduct_credits(current_user.id, credits_used, "ai_chat", f"AI Chat: {result['model']}"):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Insufficient credits",
                    "required": credits_used,
                    "available": credit_service.get_credit_balance(current_user.id)["current_balance"],
                    "message": f"Need {credits_used:.2f} credits, have {credit_service.get_credit_balance(current_user.id)['current_balance']:.2f}"
                }
            )
        
        return {
            **result,
            "credits_used": credits_used
        }
    
    except HTTPException:
        raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI request failed: {str(e)}"
            )


@router.post("/deep-search", response_model=DeepSearchResponse)
async def deep_search_chat(
    request: DeepSearchRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router),
    db: Session = Depends(get_db)
):
    """
    AI chat with deep search capabilities using RAG (Retrieval-Augmented Generation).

    Combines knowledge base search with AI chat to provide more accurate, contextually-rich responses.
    Uses the existing knowledge base and RAG system for intelligent search and response generation.

    Costs: ~0.02 credits per 1k tokens (includes search overhead)
    """
    try:
        # Initialize RAG system
        rag_config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'elasticsearch_url': 'http://localhost:9200',
            'openai_api_key': None,  # Will use environment variables
            'anthropic_api_key': None,
            'generation_models': {}
        }
        rag_system = RAGSystem(rag_config)

        # Extract search query (use last user message if not provided)
        search_query = request.search_query
        if not search_query:
            # Find the last user message
            for msg in reversed(request.messages):
                if msg.role == 'user':
                    search_query = msg.content
                    break

        search_results = []
        search_performed = False
        context_docs = []

        # Perform knowledge base search if we have a query
        if search_query and len(search_query.strip()) > 0:
            try:
                # Use RAG system to search knowledge base
                rag_response = await rag_system.query(search_query)
                search_performed = True

                # Convert RAG search results to our format
                for result in rag_response.sources[:request.search_limit]:
                    search_results.append(SearchResult(
                        document_id=result.document.id,
                        title=result.document.title,
                        content=result.document.content[:500] + "..." if len(result.document.content) > 500 else result.document.content,
                        score=result.score,
                        source=result.document.source,
                        highlights=result.highlights
                    ))

                # Prepare context for AI generation
                if request.include_sources:
                    context_docs = [f"Source: {result.document.title}\n{result.document.content}" for result in rag_response.sources[:3]]

            except Exception as search_error:
                # Log search error but continue with regular chat
                print(f"Deep search failed: {search_error}")
                search_performed = False

        # Prepare enhanced prompt with search context
        enhanced_messages = request.messages.copy()

        if context_docs and search_performed:
            # Add search context to system message or create one
            context_text = "\n\n".join(context_docs)
            search_context = f"\n\nRelevant information from knowledge base:\n{context_text}\n\nUse this information to provide a more accurate and helpful response."

            # Find system message or add one
            system_found = False
            for msg in enhanced_messages:
                if msg.role == 'system':
                    msg.content += search_context
                    system_found = True
                    break

            if not system_found:
                enhanced_messages.insert(0, ChatMessage(
                    role='system',
                    content=f"You have access to relevant information from the knowledge base.{search_context}"
                ))

        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in enhanced_messages]

        # Generate AI response
        result = await ai.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Calculate credits (higher cost for deep search due to RAG overhead)
        from ..services.billing.credit_service import get_credit_service
        credit_service = get_credit_service(db)

        credits_used = credit_service.calculate_ai_cost(
            "deep_search",
            tokens=result["usage"].get("total_tokens", 0)
        )

        # Deduct credits
        if not credit_service.deduct_credits(current_user.id, credits_used, "ai_deep_search", f"Deep Search AI: {result['model']}"):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Insufficient credits",
                    "required": credits_used,
                    "available": credit_service.get_credit_balance(current_user.id)["current_balance"],
                    "message": f"Need {credits_used:.2f} credits, have {credit_service.get_credit_balance(current_user.id)['current_balance']:.2f}"
                }
            )

        # Calculate confidence score (simplified)
        confidence_score = 0.8 if search_performed else 0.6  # Higher confidence with search

        return DeepSearchResponse(
            content=result["content"],
            search_results=search_results,
            model=result["model"],
            provider=result["provider"],
            usage=result["usage"],
            credits_used=credits_used,
            search_performed=search_performed,
            confidence_score=confidence_score
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deep search failed: {str(e)}"
        )


@router.post("/generate/code")
async def generate_code(
    request: CodeGenerationRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router),
    db: Session = Depends(get_db)
):
    """
    Generate code using AI.
    
    Optimized prompts for code generation.
    Best models: Claude Sonnet, GPT-4, CodeLlama
    """
    # Build code generation prompt
    system_message = f"""You are an expert {request.language} programmer.
Generate clean, well-documented code that follows best practices.
Include helpful comments explaining the logic."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": request.prompt}
    ]
    
    try:
        result = await ai.chat_completion(
            messages=messages,
            model=request.model,
            temperature=0.3,  # Lower temperature for code
            max_tokens=2000
        )
        
        credits_used = calculate_chat_credits(result["usage"])
        
        if not current_user.deduct_credits(credits_used):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )
        
        db.commit()
        
        return {
            "code": result["content"],
            "model": result["model"],
            "provider": result["provider"],
            "language": request.language,
            "credits_used": credits_used
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )


@router.post("/generate/image", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router),
    db: Session = Depends(get_db)
):
    """
    Generate image from text prompt.
    
    Models:
    - DALL-E 3 (OpenAI) - High quality, photorealistic
    - Stable Diffusion XL - Fast, artistic
    
    Cost: 1 credit per image
    """
    credits_required = CREDIT_COSTS["image_generation"]
    
    # Check credits before generating
    if not current_user.has_credits(credits_required):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {credits_required}, Available: {current_user.credits}"
        )
    
    try:
        result = await ai.generate_image(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            quality=request.quality
        )
        
        # Deduct credits
        current_user.deduct_credits(credits_required)
        db.commit()
        
        return {
            **result,
            "credits_used": credits_required
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


@router.get("/models")
async def list_models(current_user: User = Depends(get_current_user)):
    """
    List available AI models with descriptions and pricing.
    
    Returns information about all supported models.
    """
    models = [
        {
            "id": AIModel.CLAUDE_SONNET,
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "type": "chat",
            "description": "Best for reasoning, analysis, and complex tasks",
            "cost_per_1k_tokens": 0.015,
            "context_window": 200000
        },
        {
            "id": AIModel.GPT4_TURBO,
            "name": "GPT-4 Turbo",
            "provider": "OpenAI",
            "type": "chat",
            "description": "Powerful general-purpose model",
            "cost_per_1k_tokens": 0.01,
            "context_window": 128000
        },
        {
            "id": AIModel.GPT35_TURBO,
            "name": "GPT-3.5 Turbo",
            "provider": "OpenAI",
            "type": "chat",
            "description": "Fast and cost-effective",
            "cost_per_1k_tokens": 0.002,
            "context_window": 16000
        },
        {
            "id": AIModel.LLAMA_70B,
            "name": "Llama 3 70B",
            "provider": "Meta",
            "type": "chat",
            "description": "Open source, powerful",
            "cost_per_1k_tokens": 0.008,
            "context_window": 8000
        },
        {
            "id": AIModel.STABLE_DIFFUSION,
            "name": "Stable Diffusion XL",
            "provider": "Stability AI",
            "type": "image",
            "description": "High-quality image generation",
            "cost_per_image": 1.0
        },
        {
            "id": AIModel.DALLE_3,
            "name": "DALL-E 3",
            "provider": "OpenAI",
            "type": "image",
            "description": "Photorealistic images",
            "cost_per_image": 1.0
        }
    ]
    
    return {"models": models}


@router.get("/stats")
async def get_ai_stats(
    current_user: User = Depends(get_current_user),
    ai: AIRouter = Depends(get_ai_router)
):
    """
    Get AI usage statistics.
    
    Returns stats about AI requests, success rate, etc.
    """
    router_stats = ai.get_stats()
    
    return {
        "user_credits": current_user.credits,
        "user_credits_used": current_user.credits_used,
        "subscription_tier": current_user.subscription_tier,
        "router_stats": router_stats
    }
