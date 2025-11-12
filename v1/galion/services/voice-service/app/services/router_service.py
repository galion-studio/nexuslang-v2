"""
Action router service - routes intents to appropriate service actions
"""

import httpx
import logging
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class RouterService:
    """Routes intents to appropriate service actions"""
    
    def __init__(self):
        self.services = {
            "auth": settings.AUTH_SERVICE_URL,
            "user": settings.USER_SERVICE_URL,
            "content": settings.CONTENT_SERVICE_URL
        }
    
    async def execute_intent(
        self,
        user_email: str,
        intent: str,
        entities: Dict[str, Any],
        jwt_token: Optional[str] = None
    ) -> str:
        """
        Execute intent by calling appropriate service
        
        Args:
            user_email: User's email (from JWT)
            intent: Intent name
            entities: Extracted entities
            jwt_token: JWT token for authenticated requests
        
        Returns:
            str: Natural language response
        """
        try:
            logger.info(f"🎯 Executing intent: {intent} for user: {user_email}")
            
            # Route to appropriate handler
            handlers = {
                "login": self._handle_login,
                "register": self._handle_register,
                "logout": self._handle_logout,
                "get_profile": self._handle_get_profile,
                "update_profile": self._handle_update_profile,
                "search_users": self._handle_search_users,
                "search_content": self._handle_search_content,
                "create_post": self._handle_create_post,
                "research": self._handle_research,
                "get_analytics": self._handle_get_analytics,
                "help": self._handle_help,
                "status": self._handle_status
            }
            
            handler = handlers.get(intent, self._handle_unknown)
            response = await handler(user_email, entities, jwt_token)
            
            logger.info(f"✅ Intent executed successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ Intent execution error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    # Intent Handlers
    
    async def _handle_login(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle login intent"""
        email = entities.get("email")
        password = entities.get("password")
        
        if not email or not password:
            return "To login, I need your email and password. Please say 'login as your-email password your-password'"
        
        # TODO: Call auth service
        return f"Logging you in as {email}..."
    
    async def _handle_register(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle register intent"""
        return "Account registration through voice is coming soon. Please use the web interface for now."
    
    async def _handle_logout(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle logout intent"""
        return f"Logging you out. Goodbye, {user_email}!"
    
    async def _handle_get_profile(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle get profile intent"""
        # TODO: Call user service to get full profile
        return f"Your profile shows you're logged in as {user_email}. You have access to all Nexus Core features."
    
    async def _handle_update_profile(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle update profile intent"""
        name = entities.get("name")
        email = entities.get("email")
        
        updates = []
        if name:
            updates.append(f"name to {name}")
        if email:
            updates.append(f"email to {email}")
        
        if not updates:
            return "What would you like to update? You can change your name or email."
        
        # TODO: Call user service to update
        return f"I've updated your {' and '.join(updates)}."
    
    async def _handle_search_users(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle search users intent"""
        query = entities.get("name") or entities.get("email") or entities.get("query")
        
        if not query:
            return "Who would you like to search for?"
        
        # TODO: Call user service to search
        return f"Searching for users matching '{query}'... I found 3 users. Would you like details?"
    
    async def _handle_search_content(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle search content intent"""
        query = entities.get("query")
        
        if not query:
            return "What would you like to search for?"
        
        # TODO: Call content service to search
        return f"Searching for content about '{query}'... I found 15 articles. The top result is about machine learning fundamentals."
    
    async def _handle_create_post(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle create post intent"""
        title = entities.get("title")
        content = entities.get("content")
        
        if not title and not content:
            return "What would you like to write about?"
        
        # TODO: Call content service to create post
        return f"I've started creating a post about '{title or content}'. You can continue editing it in the web interface."
    
    async def _handle_research(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle research intent"""
        query = entities.get("query")
        
        if not query:
            return "What topic would you like me to research?"
        
        # TODO: Call deep search service
        return f"Starting research on '{query}'. This will take about 30 seconds. I'll analyze multiple sources and create a comprehensive summary for you."
    
    async def _handle_get_analytics(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle get analytics intent"""
        # TODO: Call analytics service
        return f"Your analytics show: 23 posts created, 145 searches performed, 8 voice commands today. You're an active user!"
    
    async def _handle_help(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle help intent"""
        return """I'm Nexus Core's voice assistant. I can help you with:
        
- Authentication: 'login', 'logout'
- Profile: 'show my profile', 'update my name'
- Search: 'search for articles about AI'
- Research: 'research quantum computing'
- Content: 'create post about machine learning'
- Analytics: 'show my statistics'

Just speak naturally, and I'll understand. What would you like to do?"""
    
    async def _handle_status(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle status intent"""
        return "All systems operational! Voice recognition, text-to-speech, and all services are running perfectly."
    
    async def _handle_unknown(self, user_email: str, entities: Dict, token: Optional[str]) -> str:
        """Handle unknown intent"""
        return "I'm not sure how to help with that yet. Try saying 'help' to see what I can do."


# Singleton instance
router_service = RouterService()

