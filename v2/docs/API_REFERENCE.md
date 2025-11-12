# NexusLang v2 - API Reference

**Complete API documentation for all services**

---

## Base URL

**Development:** http://localhost:8000  
**Production:** https://api.nexuslang.dev

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

### POST /api/v2/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

### POST /api/v2/auth/login

Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

### GET /api/v2/auth/me

Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name"
}
```

---

## NexusLang Execution

### POST /api/v2/nexuslang/run

Execute NexusLang code.

**Request:**
```json
{
  "code": "fn main() { print(\"Hello!\") }\nmain()",
  "compile_to_binary": false
}
```

**Response:**
```json
{
  "output": "Hello!",
  "execution_time": 45.3,
  "success": true,
  "error": null
}
```

### POST /api/v2/nexuslang/compile

Compile NexusLang code to binary.

**Request:**
```json
{
  "code": "fn factorial(n) { ... }"
}
```

**Response:**
```json
{
  "success": true,
  "binary_size": 1024,
  "compression_ratio": 3.2
}
```

### POST /api/v2/nexuslang/analyze

Analyze code for errors and suggestions.

**Request:**
```json
{
  "code": "let x = 10\nprint(x)"
}
```

**Response:**
```json
{
  "errors": [],
  "warnings": ["Warning message"],
  "suggestions": ["Suggestion text"]
}
```

### GET /api/v2/nexuslang/examples

Get list of example programs.

**Response:**
```json
{
  "examples": [
    {
      "name": "personality_demo",
      "filename": "personality_demo.nx",
      "code": "...",
      "description": "Demonstrates personality system"
    }
  ]
}
```

---

## IDE Operations

### GET /api/v2/ide/projects

List user's projects.

**Response:**
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "My Project",
      "description": "Description",
      "visibility": "private",
      "created_at": "2025-11-11T00:00:00Z"
    }
  ]
}
```

### POST /api/v2/ide/projects

Create a new project.

**Request:**
```json
{
  "name": "New Project",
  "description": "My new project",
  "visibility": "private"
}
```

### GET /api/v2/ide/files/{project_id}

List files in a project.

**Response:**
```json
{
  "files": [
    {
      "id": "uuid",
      "path": "/main.nx",
      "content": "...",
      "size_bytes": 1024
    }
  ]
}
```

---

## Grokopedia

### GET /api/v2/grokopedia/search?q={query}

Search knowledge base.

**Parameters:**
- `q` - Search query
- `verified` - Only verified entries (optional)
- `tags` - Filter by tags (optional)

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Quantum Mechanics",
      "summary": "...",
      "verified": true,
      "similarity": 0.95
    }
  ],
  "total": 1
}
```

### GET /api/v2/grokopedia/entries/{entry_id}

Get specific knowledge entry.

**Response:**
```json
{
  "id": "uuid",
  "title": "Entry Title",
  "content": "Full content...",
  "tags": ["tag1", "tag2"],
  "verified": true
}
```

### GET /api/v2/grokopedia/graph/{concept}

Get knowledge graph for concept.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

---

## Voice Services

### POST /api/v2/voice/stt

Speech-to-text (STT).

**Request:**
```
Content-Type: multipart/form-data
audio: (audio file)
language: en (optional)
```

**Response:**
```json
{
  "text": "transcribed text",
  "language": "en",
  "confidence": 0.95,
  "segments": [...]
}
```

### POST /api/v2/voice/tts

Text-to-speech (TTS).

**Request:**
```json
{
  "text": "Hello world",
  "voice_id": "galion-1",
  "emotion": "friendly",
  "speed": 1.0
}
```

**Response:**
```json
{
  "audio_url": "/audio/generated.wav",
  "text": "Hello world",
  "voice_id": "galion-1"
}
```

### POST /api/v2/voice/clone

Clone a voice from samples.

**Request:**
```
Content-Type: multipart/form-data
samples: (multiple audio files)
name: my_voice
```

**Response:**
```json
{
  "voice_id": "cloned_voice_id",
  "status": "completed",
  "name": "my_voice"
}
```

### GET /api/v2/voice/voices

List available voices.

**Response:**
```json
{
  "voices": ["galion-1", "galion-2", "default"]
}
```

---

## Billing

### GET /api/v2/billing/subscriptions

Get subscription info.

**Response:**
```json
{
  "tier": "pro",
  "status": "active",
  "credits": 10000,
  "current_period_end": "2025-12-11T00:00:00Z"
}
```

### POST /api/v2/billing/subscribe

Subscribe to a tier.

**Request:**
```json
{
  "tier": "pro"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.shopify.com/..."
}
```

### GET /api/v2/billing/credits

Get credit balance.

**Response:**
```json
{
  "balance": 8500,
  "used": 1500,
  "total_purchased": 10000
}
```

### POST /api/v2/billing/buy-credits

Purchase additional credits.

**Request:**
```json
{
  "amount": 10000
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.shopify.com/..."
}
```

---

## Community

### GET /api/v2/community/posts

List community posts.

**Response:**
```json
{
  "posts": [...],
  "total": 100
}
```

### POST /api/v2/community/posts

Create a new post.

**Request:**
```json
{
  "title": "My Post",
  "content": "Post content...",
  "tags": ["ai", "ml"]
}
```

### GET /api/v2/community/projects/public

List public projects.

**Response:**
```json
{
  "projects": [...]
}
```

---

## Rate Limiting

- **Per Minute:** 60 requests
- **Per Hour:** 1000 requests
- **Per Day:** 10000 requests

Rate limit headers included in responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed description",
  "code": "ERROR_CODE"
}
```

Common error codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## WebSocket API

### /ws/ide/collaborate/{project_id}

Real-time collaboration.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ide/collaborate/project_id')
```

**Messages:**
```json
{
  "type": "cursor_move",
  "user_id": "uuid",
  "position": {"line": 10, "column": 5}
}
```

### /ws/voice/stream/{session_id}

Real-time voice streaming.

---

**For more details, see interactive API docs at http://localhost:8000/docs**

