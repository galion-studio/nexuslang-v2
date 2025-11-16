"""
Conversation Manager - AI Integration for Voice API
Handles multi-turn conversations with various AI providers
"""

import os
import asyncio
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel
import anthropic
import openai
from datetime import datetime

# ============================================
# DATA MODELS
# ============================================

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class ConversationMessage(BaseModel):
    """A single message in a conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[datetime] = None


class ConversationContext(BaseModel):
    """Context for a conversation including history and metadata"""
    session_id: str
    messages: List[ConversationMessage] = []
    user_name: Optional[str] = None
    user_preferences: Dict[str, Any] = {}
    conversation_summary: Optional[str] = None


class ConversationRequest(BaseModel):
    """Request to process a user message"""
    session_id: str
    user_message: str
    context: Optional[ConversationContext] = None
    provider: AIProvider = AIProvider.OPENROUTER
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500


class ConversationResponse(BaseModel):
    """Response from AI"""
    ai_message: str
    updated_context: ConversationContext
    model_used: str
    tokens_used: int
    cost_estimate: float
    processing_time_ms: int


# ============================================
# CONVERSATION MANAGER
# ============================================

class ConversationManager:
    """Manages AI-driven conversations with user identity learning"""
    
    def __init__(self):
        # API keys from environment
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # Default settings
        self.default_provider = AIProvider(os.getenv("DEFAULT_AI_PROVIDER", "openrouter"))
        self.default_model = os.getenv("DEFAULT_AI_MODEL", "anthropic/claude-3.5-sonnet")
        
        # Cost tracking (approximate USD per 1K tokens)
        self.cost_per_1k_tokens = {
            "gpt-4": 0.06,
            "gpt-3.5-turbo": 0.002,
            "anthropic/claude-3.5-sonnet": 0.015,
            "anthropic/claude-3-opus": 0.075,
        }
        
    async def process_message(
        self,
        request: ConversationRequest
    ) -> ConversationResponse:
        """
        Process a user message and generate AI response
        
        This function:
        1. Retrieves conversation context
        2. Calls the appropriate AI provider
        3. Updates context with user identity learning
        4. Returns AI response with updated context
        """
        start_time = datetime.now()
        
        # Get or create context
        context = request.context or ConversationContext(
            session_id=request.session_id
        )
        
        # Add user message to history
        user_msg = ConversationMessage(
            role="user",
            content=request.user_message,
            timestamp=datetime.now()
        )
        context.messages.append(user_msg)
        
        # Build system prompt for identity learning
        system_prompt = self._build_system_prompt(context)
        
        # Call AI provider
        if request.provider == AIProvider.ANTHROPIC:
            ai_response, model, tokens = await self._call_anthropic(
                system_prompt,
                context.messages,
                request.model,
                request.temperature,
                request.max_tokens
            )
        elif request.provider == AIProvider.OPENAI:
            ai_response, model, tokens = await self._call_openai(
                system_prompt,
                context.messages,
                request.model,
                request.temperature,
                request.max_tokens
            )
        else:  # OPENROUTER
            ai_response, model, tokens = await self._call_openrouter(
                system_prompt,
                context.messages,
                request.model or self.default_model,
                request.temperature,
                request.max_tokens
            )
        
        # Add AI response to history
        ai_msg = ConversationMessage(
            role="assistant",
            content=ai_response,
            timestamp=datetime.now()
        )
        context.messages.append(ai_msg)
        
        # Learn from conversation (extract user info)
        context = self._learn_from_conversation(context)
        
        # Calculate metrics
        end_time = datetime.now()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        cost_estimate = self._estimate_cost(model, tokens)
        
        return ConversationResponse(
            ai_message=ai_response,
            updated_context=context,
            model_used=model,
            tokens_used=tokens,
            cost_estimate=cost_estimate,
            processing_time_ms=processing_time_ms
        )
    
    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build system prompt for AI with identity learning"""
        base_prompt = """You are Galion AI, an advanced voice assistant for the 22nd century.
You communicate naturally through voice, helping users with any task.

Key behaviors:
- Be conversational and friendly
- Keep responses concise (under 3 sentences for voice)
- Remember information users share about themselves
- Never mention that you're an AI unless asked
- Focus on being helpful and insightful"""
        
        # Add known user information
        if context.user_name:
            base_prompt += f"\n\nUser's name: {context.user_name}"
        
        if context.user_preferences:
            prefs_str = "\n".join([f"- {k}: {v}" for k, v in context.user_preferences.items()])
            base_prompt += f"\n\nKnown preferences:\n{prefs_str}"
        
        return base_prompt
    
    async def _call_openrouter(
        self,
        system_prompt: str,
        messages: List[ConversationMessage],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> tuple[str, str, int]:
        """Call OpenRouter API"""
        # Prepare messages for API
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]  # Last 10 messages for context
        ])
        
        # Call OpenRouter
        response = await openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.openrouter_key
        ).chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return ai_message, model, tokens_used
    
    async def _call_anthropic(
        self,
        system_prompt: str,
        messages: List[ConversationMessage],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> tuple[str, str, int]:
        """Call Anthropic API"""
        model = model or "claude-3-5-sonnet-20241022"
        
        # Prepare messages
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]
        ]
        
        client = anthropic.AsyncAnthropic(api_key=self.anthropic_key)
        response = await client.messages.create(
            model=model,
            system=system_prompt,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        ai_message = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        
        return ai_message, model, tokens_used
    
    async def _call_openai(
        self,
        system_prompt: str,
        messages: List[ConversationMessage],
        model: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> tuple[str, str, int]:
        """Call OpenAI API"""
        model = model or "gpt-4"
        
        # Prepare messages
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]
        ])
        
        client = openai.AsyncOpenAI(api_key=self.openai_key)
        response = await client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return ai_message, model, tokens_used
    
    def _learn_from_conversation(self, context: ConversationContext) -> ConversationContext:
        """Extract user information from conversation to personalize experience"""
        # This is a simple implementation
        # In production, you'd use NLP/NER to extract:
        # - User name
        # - Preferences
        # - Interests
        # - Goals
        
        recent_messages = context.messages[-5:]
        
        # Simple name extraction (looking for "my name is X")
        for msg in recent_messages:
            if msg.role == "user" and "my name is" in msg.content.lower():
                # Extract name (very basic)
                parts = msg.content.lower().split("my name is")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0].capitalize()
                    context.user_name = name
        
        return context
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost of API call"""
        # Get cost per 1K tokens
        cost_per_1k = self.cost_per_1k_tokens.get(model, 0.01)
        
        # Calculate total cost
        return (tokens / 1000) * cost_per_1k


# ============================================
# SINGLETON INSTANCE
# ============================================

_conversation_manager: Optional[ConversationManager] = None


async def get_conversation_manager() -> ConversationManager:
    """Get or create the conversation manager singleton"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager

