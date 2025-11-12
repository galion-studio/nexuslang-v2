# 🔧 NexusLang v2 - Complete API Reference

**Comprehensive REST API Documentation**

**Base URL:** `https://api.developer.galion.app/api/v2`  
**Interactive Docs:** https://api.developer.galion.app/docs  
**Version:** 2.0.0-beta

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Code Execution](#code-execution)
3. [Projects](#projects)
4. [Files](#files)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)
8. [SDK & Libraries](#sdks)

---

## 1. Authentication

### POST /auth/register

Create a new user account.

**Endpoint:** `/api/v2/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Errors:**
```json
// 400 Bad Request
{
  "detail": "Email already registered"
}

// 400 Bad Request  
{
  "detail": "Password must be at least 8 characters long"
}
```

**Requirements:**
- Email: Valid format
- Username: 3-50 characters, alphanumeric + _ -
- Password: Min 8 chars, 1 uppercase, 1 lowercase, 1 digit

**cURL Example:**
```bash
curl -X POST https://api.developer.galion.app/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

---

### POST /auth/login

Authenticate and get JWT token.

**Endpoint:** `/api/v2/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe"
}
```

**Errors:**
```json
// 401 Unauthorized
{
  "detail": "Incorrect email or password"
}

// 403 Forbidden
{
  "detail": "Account is inactive"
}
```

**JavaScript Example:**
```javascript
const response = await fetch('https://api.developer.galion.app/api/v2/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!'
  })
});

const data = await response.json();
localStorage.setItem('token', data.access_token);
```

---

### GET /auth/me

Get current user information.

**Endpoint:** `/api/v2/auth/me`

**Headers Required:**
```
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "avatar_url": null,
  "bio": null,
  "is_verified": false,
  "created_at": "2025-11-11T12:00:00Z"
}
```

**Python Example:**
```python
import requests

headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get(
    'https://api.developer.galion.app/api/v2/auth/me',
    headers=headers
)

user = response.json()
print(f"Logged in as: {user['username']}")
```

---

## 2. Code Execution

### POST /nexuslang/run

Execute NexusLang code.

**Endpoint:** `/api/v2/nexuslang/run`

**Headers Required:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "fn main() {\n  print(\"Hello!\")\n}\nmain()",
  "compile_to_binary": false
}
```

**Response (200 OK):**
```json
{
  "output": "Hello!\n",
  "execution_time": 45.23,
  "success": true
}
```

**Response (Error):**
```json
{
  "output": "❌ Execution Error\n\nError: ParseError at line 2...",
  "execution_time": 12.5,
  "success": false,
  "error": "ParseError: Unexpected token"
}
```

**Limits:**
- Max execution time: 10 seconds
- Max output size: 100KB
- Max code length: 1MB

**Full Example:**
```javascript
const code = `
personality {
    curiosity: 0.9
}

fn main() {
    let facts = knowledge("AI")
    print("Found facts:", facts.length)
}

main()
`;

const response = await fetch('https://api.developer.galion.app/api/v2/nexuslang/run', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ code })
});

const result = await response.json();
console.log(result.output);
```

---

### POST /nexuslang/compile

Compile code to binary format.

**Endpoint:** `/api/v2/nexuslang/compile`

**Request Body:**
```json
{
  "code": "fn main() { print(\"Hello\") }\nmain()"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "binary_size": 456,
  "compression_ratio": 2.71,
  "estimated_speedup": 13.5
}
```

**Benefits:**
- 2-3x smaller file size
- 10-15x faster AI processing
- Optimized constant pooling
- Production-ready format

---

### GET /nexuslang/examples

Get example programs.

**Endpoint:** `/api/v2/nexuslang/examples`

**Response (200 OK):**
```json
{
  "examples": [
    {
      "name": "hello_world",
      "filename": "01_hello_world.nx",
      "code": "fn main() {\n  print(\"Hello!\")\n}\nmain()",
      "description": "Basic hello world program"
    },
    {
      "name": "personality_demo",
      "filename": "02_personality_traits.nx",
      "code": "personality {\n  curiosity: 0.9\n}...",
      "description": "Demonstrates personality system"
    }
    // ... 10 more examples
  ]
}
```

---

## 3. Projects

### GET /ide/projects

List user's projects.

**Response (200 OK):**
```json
[
  {
    "id": "proj-uuid-here",
    "name": "My First Project",
    "description": "Learning NexusLang",
    "visibility": "private",
    "stars_count": 0,
    "forks_count": 0,
    "created_at": "2025-11-11T12:00:00Z",
    "updated_at": "2025-11-11T13:00:00Z",
    "file_count": 3
  }
]
```

### POST /ide/projects

Create new project.

**Request Body:**
```json
{
  "name": "My New Project",
  "description": "Optional description",
  "visibility": "private"
}
```

**Response (201 Created):**
```json
{
  "id": "new-project-uuid",
  "name": "My New Project",
  "description": "Optional description",
  "visibility": "private",
  "created_at": "2025-11-11T14:00:00Z",
  "file_count": 1
}
```

**Note:** Automatically creates `main.nx` file

---

## 4. Files

### GET /ide/projects/{project_id}/files

List files in project.

**Response:**
```json
[
  {
    "id": "file-uuid",
    "project_id": "project-uuid",
    "path": "main.nx",
    "content": "fn main() { ... }",
    "size_bytes": 1234,
    "version": 3,
    "created_at": "2025-11-11T12:00:00Z",
    "updated_at": "2025-11-11T14:30:00Z"
  }
]
```

### PUT /ide/files/{file_id}

Update file content (save).

**Request Body:**
```json
{
  "content": "// Updated code\nfn main() { print(\"Updated!\") }\nmain()"
}
```

**Response:**
```json
{
  "id": "file-uuid",
  "version": 4,
  "size_bytes": 1456,
  "updated_at": "2025-11-11T15:00:00Z"
}
```

**Note:** Version increments on each save

---

## 5. Error Handling

### Standard Error Format

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 6. Rate Limits

### Limits by Tier

| Tier | Requests/Minute | Requests/Hour | Requests/Day |
|------|-----------------|---------------|--------------|
| Free | 60 | 1,000 | 10,000 |
| Pro | 600 | 10,000 | 100,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

### Rate Limit Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699999999
```

**When limit exceeded:**
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds.",
  "retry_after": 45
}
```

---

## 7. SDKs & Libraries

### Python SDK

```python
from nexuslang import NexusClient

client = NexusClient(api_key='your-key')

# Run code
result = client.run_code('''
fn main() {
    print("Hello from Python SDK!")
}
main()
''')

print(result.output)
```

### JavaScript SDK

```javascript
import { NexusClient } from '@nexuslang/sdk'

const client = new NexusClient({ apiKey: 'your-key' })

// Run code
const result = await client.runCode(`
fn main() {
    print("Hello from JS SDK!")
}
main()
`)

console.log(result.output)
```

### REST Client Examples

**Postman Collection:** [Download](./docs/postman/nexuslang-v2.json)  
**Insomnia Workspace:** [Download](./docs/insomnia/nexuslang-v2.yaml)

---

## 📊 Usage Examples

### Complete Workflow

```javascript
// 1. Register
const register = await fetch('/api/v2/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'dev@example.com',
    username: 'developer',
    password: 'SecurePass123!'
  })
});

const { access_token } = await register.json();

// 2. Create project
const project = await fetch('/api/v2/ide/projects', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'My AI Project'
  })
});

const projectData = await project.json();

// 3. Create file
const file = await fetch(`/api/v2/ide/projects/${projectData.id}/files`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    path: 'ai_assistant.nx',
    content: 'fn main() { say("Hello!") }\nmain()'
  })
});

const fileData = await file.json();

// 4. Run code
const execution = await fetch('/api/v2/nexuslang/run', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    code: fileData.content
  })
});

const result = await execution.json();
console.log(result.output);
```

---

## 🔒 Security

### Authentication

**JWT Token Format:**
```
Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "sub": "user-uuid",
  "email": "user@example.com",
  "exp": 1699999999
}
```

**Token Expiration:** 24 hours  
**Refresh:** Login again to get new token

### Best Practices

✅ Store tokens securely (httpOnly cookies recommended)  
✅ Don't expose tokens in client-side code  
✅ Implement token refresh logic  
✅ Clear tokens on logout  
✅ Use HTTPS only in production  

---

## 📖 Interactive Documentation

### Swagger UI

Visit: https://api.developer.galion.app/docs

**Features:**
- Try all endpoints directly
- See request/response schemas
- Auto-generated from OpenAPI spec
- Examples for each endpoint

### ReDoc

Visit: https://api.developer.galion.app/redoc

**Features:**
- Clean, readable format
- Searchable
- Code examples in multiple languages
- Downloadable OpenAPI spec

---

## 🎯 Quick Reference

### Authentication Endpoints

```
POST   /api/v2/auth/register        Create account
POST   /api/v2/auth/login           Get JWT token
GET    /api/v2/auth/me              Current user info
POST   /api/v2/auth/logout          Logout (client-side)
POST   /api/v2/auth/verify-token    Verify token valid
```

### Execution Endpoints

```
POST   /api/v2/nexuslang/run        Execute code
POST   /api/v2/nexuslang/compile    Compile to binary
POST   /api/v2/nexuslang/analyze    Code analysis
GET    /api/v2/nexuslang/examples   Get example programs
```

### Project Endpoints

```
GET    /api/v2/ide/projects           List projects
POST   /api/v2/ide/projects           Create project
GET    /api/v2/ide/projects/{id}      Get project
PUT    /api/v2/ide/projects/{id}      Update project
DELETE /api/v2/ide/projects/{id}      Delete project
```

### File Endpoints

```
GET    /api/v2/ide/projects/{id}/files    List files
POST   /api/v2/ide/projects/{id}/files    Create file
GET    /api/v2/ide/files/{id}             Get file
PUT    /api/v2/ide/files/{id}             Update file
DELETE /api/v2/ide/files/{id}             Delete file
```

---

## 📞 Support

**For API questions:**
- Email: api@galion.app
- Docs: https://api.developer.galion.app/docs
- GitHub Issues: Report bugs

---

**🚀 Start building with NexusLang v2 API!**

