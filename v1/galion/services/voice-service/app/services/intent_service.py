"""
Intent classification and entity extraction using GPT-4
"""

import httpx
import json
import logging
from typing import Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class IntentService:
    """Intent classification and entity extraction using GPT-4"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Intent definitions
        self.intents = {
            "login": {
                "description": "User wants to login",
                "entities": ["email", "password"],
                "examples": ["login as john@example.com", "sign in", "log me in"]
            },
            "register": {
                "description": "User wants to register",
                "entities": ["email", "password", "name"],
                "examples": ["create account", "sign up", "register"]
            },
            "logout": {
                "description": "User wants to logout",
                "entities": [],
                "examples": ["logout", "sign out", "log me out"]
            },
            "get_profile": {
                "description": "User wants to see their profile",
                "entities": [],
                "examples": ["show my profile", "my account", "who am i"]
            },
            "update_profile": {
                "description": "User wants to update their profile",
                "entities": ["name", "email"],
                "examples": ["update my name", "change my email"]
            },
            "search_users": {
                "description": "User wants to search for other users",
                "entities": ["name", "email", "role"],
                "examples": ["find users named Sarah", "search for users"]
            },
            "search_content": {
                "description": "User wants to search content",
                "entities": ["query", "category"],
                "examples": ["search for AI", "find articles about", "look up"]
            },
            "create_post": {
                "description": "User wants to create a post",
                "entities": ["title", "content", "category"],
                "examples": ["create post about AI", "write article"]
            },
            "research": {
                "description": "User wants deep research",
                "entities": ["query", "depth"],
                "examples": ["research quantum computing", "deep search", "investigate"]
            },
            "get_analytics": {
                "description": "User wants analytics data",
                "entities": ["metric", "timeframe"],
                "examples": ["show analytics", "statistics", "usage stats"]
            },
            "help": {
                "description": "User needs help",
                "entities": [],
                "examples": ["help", "what can you do", "commands"]
            },
            "status": {
                "description": "User wants system status",
                "entities": [],
                "examples": ["system status", "are you working", "health check"]
            }
        }
    
    async def classify_intent(
        self,
        text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Classify user intent and extract entities
        
        Args:
            text: User's spoken text
            context: Conversation context
        
        Returns:
            dict: {
                "intent": "get_profile",
                "entities": {"name": "John"},
                "confidence": 0.95,
                "needs_clarification": false,
                "clarification_question": null
            }
        """
        try:
            # Build system prompt with intent definitions
            system_prompt = self._build_system_prompt()
            
            # Build user prompt
            user_prompt = f"User said: '{text}'"
            if context:
                user_prompt += f"\n\nContext: {json.dumps(context)}"
            
            logger.info(f"🧠 Classifying intent for: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            # Call GPT-4 via OpenRouter
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://nexuscore.ai",
                        "X-Title": "Nexus Core Voice"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300
                    },
                    timeout=30.0
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse intent from response
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(content)
            
            logger.info(f"✅ Intent classified: {intent_data['intent']} (confidence: {intent_data['confidence']:.2f})")
            
            return intent_data
            
        except Exception as e:
            logger.error(f"❌ Intent classification error: {e}")
            # Return default "help" intent on error
            return {
                "intent": "help",
                "entities": {},
                "confidence": 0.5,
                "needs_clarification": True,
                "clarification_question": "I didn't understand that. Could you rephrase?"
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with intent definitions"""
        prompt = """You are Nexus Core's voice assistant. Classify user commands into intents and extract entities.

Available intents:\n"""
        
        for intent_name, intent_data in self.intents.items():
            prompt += f"\n- {intent_name}: {intent_data['description']}"
            if intent_data['entities']:
                prompt += f"\n  Entities: {', '.join(intent_data['entities'])}"
            prompt += f"\n  Examples: {', '.join(intent_data['examples'][:2])}"
        
        prompt += """

Return ONLY valid JSON in this exact format:
{
    "intent": "intent_name",
    "entities": {"entity_name": "value"},
    "confidence": 0.95,
    "needs_clarification": false,
    "clarification_question": null
}

Rules:
- If you're not sure (confidence < 0.7), set needs_clarification to true and provide a clarification_question
- Extract all mentioned entities even if not explicitly required
- Confidence should reflect how certain you are (0.0-1.0)
- Use lowercase for intent names
- Return ONLY the JSON, no other text"""
        
        return prompt


# Singleton instance
intent_service = IntentService()

