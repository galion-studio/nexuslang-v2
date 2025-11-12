# NexusLang v2 - API Documentation

**REST API Reference for NexusLang v2 Platform**

**Base URL:** `http://localhost:8000/api/v2`  
**Production:** `https://api.nexuslang.dev/api/v2`

---

## Authentication

All protected endpoints require JWT token in Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Errors:**
- `400` - Invalid input (weak password, username taken, etc.)

---

### POST /auth/login

Login with credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account inactive

---

### GET /auth/me

Get current user information.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "avatar_url": null,
  "bio": null,
  "is_verified": false,
  "created_at": "2025-11-11T00:00:00Z"
}
```

**Errors:**
- `401` - Invalid or expired token

---

## NexusLang Execution

### POST /nexuslang/run

Execute NexusLang code.

**Headers:** Requires authentication

**Request:**
```json
{
  "code": "fn main() {\n  print(\"Hello!\")\n}\nmain()",
  "compile_to_binary": false
}
```

**Response (200):**
```json
{
  "output": "Hello!\n",
  "execution_time": 45.23,
  "success": true
}
```

**Response (200) - Error:**
```json
{
  "output": "❌ Error: ...",
  "execution_time": 12.5,
  "success": false,
  "error": "ParseError: ..."
}
```

**Limits:**
- Max execution time: 10 seconds
- Max output size: 100KB
- Code length: 1MB

---

### POST /nexuslang/compile

Compile code to binary format.

**Headers:** Requires authentication

**Request:**
```json
{
  "code": "fn main() { print(\"Hello\") }\nmain()"
}
```

**Response (200):**
```json
{
  "success": true,
  "binary_size": 456,
  "compression_ratio": 2.71
}
```

---

### POST /nexuslang/analyze

Analyze code for errors and suggestions.

**Headers:** Requires authentication

**Request:**
```json
{
  "code": "fn main() { print(\"Hello\") }"
}
```

**Response (200):**
```json
{
  "errors": [],
  "warnings": [],
  "suggestions": ["Code looks good!"]
}
```

---

### GET /nexuslang/examples

Get example programs.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "examples": [
    {
      "name": "hello_world",
      "filename": "01_hello_world.nx",
      "code": "...",
      "description": "Basic hello world program"
    }
  ]
}
```

---

## Projects

### GET /ide/projects

List user's projects.

**Headers:** Requires authentication

**Response (200):**
```json
[
  {
    "id": "project-uuid",
    "name": "My Project",
    "description": "Description here",
    "visibility": "private",
    "stars_count": 0,
    "forks_count": 0,
    "created_at": "2025-11-11T00:00:00Z",
    "updated_at": "2025-11-11T00:00:00Z",
    "file_count": 3
  }
]
```

---

### POST /ide/projects

Create a new project.

**Headers:** Requires authentication

**Request:**
```json
{
  "name": "My New Project",
  "description": "Optional description",
  "visibility": "private"
}
```

**Response (201):**
```json
{
  "id": "project-uuid",
  "name": "My New Project",
  "description": "Optional description",
  "visibility": "private",
  "stars_count": 0,
  "forks_count": 0,
  "created_at": "2025-11-11T00:00:00Z",
  "updated_at": "2025-11-11T00:00:00Z",
  "file_count": 1
}
```

**Note:** Automatically creates a `main.nx` file in the project.

---

### GET /ide/projects/{project_id}

Get project details.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "id": "project-uuid",
  "name": "Project Name",
  ...
}
```

**Errors:**
- `404` - Project not found

---

### PUT /ide/projects/{project_id}

Update project details.

**Headers:** Requires authentication

**Request:**
```json
{
  "name": "Updated Name",
  "description": "New description"
}
```

---

### DELETE /ide/projects/{project_id}

Delete a project and all its files.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "message": "Project deleted successfully"
}
```

---

## Files

### GET /ide/projects/{project_id}/files

List files in a project.

**Headers:** Requires authentication

**Response (200):**
```json
[
  {
    "id": "file-uuid",
    "project_id": "project-uuid",
    "path": "main.nx",
    "content": "...",
    "size_bytes": 1234,
    "version": 1,
    "created_at": "2025-11-11T00:00:00Z",
    "updated_at": "2025-11-11T00:00:00Z"
  }
]
```

---

### POST /ide/projects/{project_id}/files

Create a new file.

**Headers:** Requires authentication

**Request:**
```json
{
  "path": "utils.nx",
  "content": "// Utility functions\n"
}
```

**Response (201):**
```json
{
  "id": "file-uuid",
  "project_id": "project-uuid",
  "path": "utils.nx",
  "content": "// Utility functions\n",
  "size_bytes": 23,
  "version": 1,
  "created_at": "2025-11-11T00:00:00Z",
  "updated_at": "2025-11-11T00:00:00Z"
}
```

**Errors:**
- `400` - File already exists
- `404` - Project not found

---

### GET /ide/files/{file_id}

Get file content.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "id": "file-uuid",
  "project_id": "project-uuid",
  "path": "main.nx",
  "content": "...",
  ...
}
```

**Errors:**
- `404` - File not found
- `403` - Access denied

---

### PUT /ide/files/{file_id}

Update file content (save).

**Headers:** Requires authentication

**Request:**
```json
{
  "content": "// Updated code\nprint(\"Hello\")"
}
```

**Response (200):**
```json
{
  "id": "file-uuid",
  "version": 2,
  ...
}
```

**Note:** Version number increments on each save.

---

### DELETE /ide/files/{file_id}

Delete a file.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "message": "File deleted successfully"
}
```

---

## Rate Limits

- **Free tier:** 60 requests/minute
- **Pro tier:** 600 requests/minute
- **Enterprise:** Unlimited

**Headers returned:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699999999
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

---

## WebSocket API

### /ws/ide

Real-time collaboration socket (coming soon).

---

## Pagination

For endpoints returning lists:

**Query Parameters:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)

**Response includes:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

---

## SDKs and Libraries

### Python SDK
```python
from nexuslang import NexusClient

client = NexusClient(api_key="your-key")
result = client.run_code("print('Hello')")
```

### JavaScript SDK
```javascript
import { NexusClient } from '@nexuslang/sdk'

const client = new NexusClient({ apiKey: 'your-key' })
const result = await client.runCode("print('Hello')")
```

**Coming soon!**

---

## Interactive API Docs

Visit `http://localhost:8000/docs` for:
- Interactive API explorer
- Try endpoints directly
- Auto-generated from OpenAPI spec
- Examples for each endpoint

---

**Questions?** Email: api@nexuslang.dev

