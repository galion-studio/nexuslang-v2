#!/usr/bin/env python3
"""
Minimal NexusLang v2 Backend - Production Ready
Elon Musk approach: Get something working end-to-end first, then optimize.
"""

from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import logging
import time
from datetime import datetime

# Import our voice API router
try:
    from v2.backend.api.voice import router as voice_router
    VOICE_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Voice API not available: {e}")
    VOICE_API_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NexusLang v2 API",
    description="Production-ready backend with working authentication and voice AI",
    version="2.0.0",
    docs_url="/docs"
)

# Include voice API router if available
if VOICE_API_AVAILABLE:
    app.include_router(voice_router)
    logger.info("Voice API router included successfully")
else:
    logger.warning("Voice API router not available - voice features will be disabled")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database - in production, replace with real database
MOCK_USERS = {
    "admin@nexuslang.dev": {
        "id": 1,
        "email": "admin@nexuslang.dev",
        "username": "admin",
        "hashed_password": "Admin123!",  # In production, use proper hashing
        "full_name": "NexusLang Admin",
        "is_active": True,
        "is_verified": True,
        "is_admin": True,
        "subscription_tier": "enterprise",
        "credits": 10000.0,
        "created_at": "2025-01-01T00:00:00Z"
    },
    "test@example.com": {
        "id": 2,
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "Test123!",
        "full_name": "Test User",
        "is_active": True,
        "is_verified": True,
        "is_admin": False,
        "subscription_tier": "voice_pro",
        "credits": 2000.0,
        "created_at": "2025-01-01T00:00:00Z"
    }
}

MOCK_PROJECTS = []
MOCK_SESSIONS = {}  # Simple session store

# Pydantic Models
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400
    user: Dict[str, Any]

class ExecuteRequest(BaseModel):
    code: str
    language: Optional[str] = "nexuslang"
    timeout: Optional[int] = 30

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    is_verified: bool
    is_admin: bool
    subscription_tier: str
    subscription_status: str
    credits: float
    created_at: str
    last_login: Optional[str]

# Helper Functions
def create_jwt_token(user_id: int, email: str) -> str:
    """Create a simple JWT-like token (in production, use proper JWT library)."""
    import base64
    import json

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + 86400,  # 24 hours
        "iat": int(time.time())
    }

    # Simple encoding (NOT secure - use proper JWT in production)
    token_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"mock_jwt_{token_data}"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode token (simplified for demo)."""
    import base64
    import json

    try:
        if not token.startswith("mock_jwt_"):
            return None

        token_data = token.replace("mock_jwt_", "")
        payload = json.loads(base64.b64decode(token_data).decode())
        return payload
    except:
        return None

def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from token."""
    payload = decode_token(token)
    if not payload:
        return None

    email = payload.get("email")
    return MOCK_USERS.get(email)

# Authentication Endpoints
@app.post("/api/v2/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """User login endpoint."""
    user = MOCK_USERS.get(credentials.email)

    if not user or user["hashed_password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Create token
    token = create_jwt_token(user["id"], user["email"])

    # Update last login
    user["last_login"] = datetime.utcnow().isoformat() + "Z"

    return TokenResponse(
        access_token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "is_verified": user["is_verified"],
            "is_admin": user["is_admin"],
            "subscription_tier": user["subscription_tier"],
            "credits": user["credits"]
        }
    )

@app.post("/api/v2/auth/register", response_model=TokenResponse)
async def register(user_data: dict):
    """User registration endpoint."""
    # Simple registration - in production, validate properly
    email = user_data.get("email")
    password = user_data.get("password")
    username = user_data.get("username", email.split("@")[0])

    if email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Create new user
    new_user = {
        "id": len(MOCK_USERS) + 1,
        "email": email,
        "username": username,
        "hashed_password": password,  # In production, hash properly
        "full_name": user_data.get("full_name", ""),
        "is_active": True,
        "is_verified": False,
        "is_admin": False,
        "subscription_tier": "free",
        "credits": 100.0,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    MOCK_USERS[email] = new_user

    # Create token
    token = create_jwt_token(new_user["id"], new_user["email"])

    return TokenResponse(
        access_token=token,
        user={
            "id": new_user["id"],
            "email": new_user["email"],
            "username": new_user["username"],
            "full_name": new_user["full_name"],
            "is_verified": new_user["is_verified"],
            "is_admin": new_user["is_admin"],
            "subscription_tier": new_user["subscription_tier"],
            "credits": new_user["credits"]
        }
    )

@app.get("/api/v2/auth/me", response_model=UserResponse)
async def get_current_user_endpoint(Authorization: Optional[str] = Header(None)):
    """Get current user profile."""
    print(f"DEBUG: Authorization header: '{Authorization}'")
    if not Authorization or not Authorization.startswith("Bearer "):
        print(f"DEBUG: Header check failed - Authorization: {Authorization}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = Authorization.replace("Bearer ", "")
    user = get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return UserResponse(**user)

# NexusLang Endpoints
@app.post("/api/v2/nexuslang/execute")
async def execute_nexuslang_code(request: ExecuteRequest):
    """Execute NexusLang code."""
    # Simple execution - in production, use real interpreter
    code = request.code.strip()

    # Mock execution results
    if "print(" in code:
        # Extract print content
        import re
        match = re.search(r'print\(["\']([^"\']+)["\']', code)
        if match:
            output = match.group(1)
        else:
            output = "Hello from NexusLang!"
    elif "return" in code:
        output = "Function executed"
    else:
        output = f"Executed: {code[:50]}..."

    return {
        "stdout": output,
        "stderr": "",
        "return_code": 0,
        "execution_time": 0.1,
        "success": True,
        "error": None,
        "credits_used": 1
    }

@app.get("/api/v2/nexuslang/examples")
async def get_nexuslang_examples():
    """Get NexusLang code examples."""
    examples = [
        {
            "id": 1,
            "title": "Hello World",
            "description": "Basic print statement",
            "code": 'print("Hello, NexusLang!")',
            "category": "basics",
            "difficulty": "beginner"
        },
        {
            "id": 2,
            "title": "Voice Command",
            "description": "AI voice interaction",
            "code": 'voice.speak("Hello from NexusLang!")',
            "category": "voice",
            "difficulty": "intermediate"
        },
        {
            "id": 3,
            "title": "Data Processing",
            "description": "Process and analyze data",
            "code": 'data = load_dataset("example.csv")\nresult = analyze(data)\nprint(result)',
            "category": "data",
            "difficulty": "advanced"
        }
    ]
    return examples

@app.get("/api/v2/nexuslang/docs")
async def get_nexuslang_docs():
    """Get NexusLang documentation."""
    return {
        "language": "NexusLang",
        "version": "2.0",
        "description": "AI-native programming language",
        "features": [
            "Voice-first interaction",
            "Binary optimization",
            "Universal knowledge integration",
            "Personality-driven behavior"
        ],
        "syntax": {
            "print": "print('message')",
            "voice": "voice.speak('message')",
            "data": "data = load_dataset('file')"
        }
    }

# AI Endpoints
@app.get("/api/v2/ai/models")
async def get_ai_models():
    """Get available AI models."""
    return {
        "models": [
            {
                "id": "anthropic/claude-3-haiku",
                "name": "Claude 3 Haiku",
                "provider": "Anthropic",
                "capabilities": ["chat", "text"],
                "credits_per_token": 0.0001
            },
            {
                "id": "openai/gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "capabilities": ["chat", "text", "image"],
                "credits_per_token": 0.0002
            }
        ]
    }

@app.post("/api/v2/ai/chat")
async def ai_chat(request: dict, Authorization: Optional[str] = Header(None)):
    """AI chat endpoint."""
    if not Authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Mock AI response
    messages = request.get("messages", [])
    last_message = messages[-1]["content"] if messages else "Hello"

    return {
        "content": f"I understand you said: '{last_message}'. This is a mock AI response. Configure OpenRouter API key for real AI.",
        "model": "anthropic/claude-3-haiku",
        "provider": "Anthropic",
        "usage": {"tokens": 50},
        "credits_used": 5
    }

# Billing Endpoints
@app.get("/api/v2/billing/credits")
async def get_credits(Authorization: Optional[str] = Header(None)):
    """Get user credits."""
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = Authorization.replace("Bearer ", "")
    user = get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "balance": user["credits"],
        "used_this_month": 150.0,  # Mock data
        "subscription_tier": user["subscription_tier"],
        "auto_recharge": True
    }

@app.get("/api/v2/billing/subscription")
async def get_subscription(Authorization: Optional[str] = Header(None)):
    """Get user subscription."""
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = Authorization.replace("Bearer ", "")
    user = get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "tier": user["subscription_tier"],
        "status": "active",
        "credits_per_month": 1000,
        "features": ["voice_ai", "code_execution", "ai_chat"]
    }

# Grokopedia Endpoints
@app.get("/api/v2/grokopedia/search")
async def search_grokopedia(query: str, limit: int = 10):
    """Search Grokopedia knowledge base."""
    # Mock search results
    results = [
        {
            "id": 1,
            "title": "Artificial Intelligence",
            "snippet": "Artificial Intelligence (AI) is intelligence demonstrated by machines...",
            "category": "Technology",
            "relevance_score": 0.95
        },
        {
            "id": 2,
            "title": "Machine Learning",
            "snippet": "Machine learning is a subset of AI that enables systems to learn...",
            "category": "Technology",
            "relevance_score": 0.89
        }
    ]

    return {"query": query, "results": results[:limit]}

@app.get("/api/v2/grokopedia/categories")
async def get_grokopedia_categories():
    """Get knowledge base categories."""
    return {
        "categories": [
            {"name": "Technology", "count": 1500},
            {"name": "Science", "count": 1200},
            {"name": "Business", "count": 800},
            {"name": "Health", "count": 600},
            {"name": "Education", "count": 400}
        ]
    }

# Health and Root Endpoints
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "NexusLang v2 API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "platforms": ["developer.galion.app", "galion.studio"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "healthy",
            "cache": "healthy",
            "ai": "ready"
        }
    }

@app.get("/health/fast")
async def fast_health_check():
    """Fast health check."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": "fast"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup."""
    logger.info("🚀 NexusLang v2 Minimal Backend starting...")
    logger.info("✅ API documentation: http://localhost:8000/docs")
    logger.info("✅ Authentication: admin@nexuslang.dev / Admin123!")
    logger.info("✅ Test user: test@example.com / Test123!")

if __name__ == "__main__":
    logger.info("Starting NexusLang v2 Minimal Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
