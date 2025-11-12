# GALION.APP API Documentation

**Base URL:** `https://api.galion.app` (when deployed) or `http://localhost:8080` (local)  
**API Version:** v1  
**Authentication:** JWT Bearer Token

---

## 🎯 QUICK START

### 1. Register a User
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2025-11-08T10:00:00Z"
}
```

---

### 2. Login
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 3. Access Protected Endpoint
```bash
curl http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

---

## 🔐 AUTHENTICATION ENDPOINTS

### POST /api/v1/auth/register
Create a new user account.

**Request Body:**
```json
{
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "name": "string (required)"
}
```

**Success Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "role": "user",
  "created_at": "timestamp"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input
- `409 Conflict` - Email already exists
- `429 Too Many Requests` - Rate limit exceeded

---

### POST /api/v1/auth/login
Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response:** `200 OK`
```json
{
  "access_token": "string (JWT token)",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `400 Bad Request` - Missing credentials
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

---

### GET /api/v1/auth/me
Get current user info (requires authentication).

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Success Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "role": "string",
  "email_verified": false,
  "is_active": true,
  "created_at": "timestamp",
  "last_login_at": "timestamp"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Token expired

---

### POST /api/v1/auth/logout
Invalidate JWT token (requires authentication).

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Success Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

## 👤 USER ENDPOINTS

### GET /api/v1/users
List all users (admin only).

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `limit` (optional, default: 100, max: 1000)
- `offset` (optional, default: 0)

**Success Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "string",
      "name": "string",
      "role": "string",
      "created_at": "timestamp"
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not admin

---

### GET /api/v1/users/{id}
Get specific user by ID.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Success Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "role": "string",
  "email_verified": false,
  "is_active": true,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `404 Not Found` - User doesn't exist

---

### PUT /api/v1/users/{id}
Update user profile (own profile or admin).

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Request Body:**
```json
{
  "name": "string (optional)",
  "email": "string (optional, valid email)"
}
```

**Success Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "updated_at": "timestamp"
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Can't update other users
- `404 Not Found` - User doesn't exist
- `409 Conflict` - Email already taken

---

### DELETE /api/v1/users/{id}
Delete user account (own account or admin).

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Success Response:** `204 No Content`

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Can't delete other users
- `404 Not Found` - User doesn't exist

---

## 📊 ANALYTICS ENDPOINTS

### GET /api/v1/analytics/events
Query analytics events (admin only).

**Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `event_type` (optional) - Filter by event type
- `user_id` (optional) - Filter by user
- `start_date` (optional) - ISO8601 timestamp
- `end_date` (optional) - ISO8601 timestamp
- `limit` (optional, default: 100, max: 1000)
- `offset` (optional, default: 0)

**Success Response:** `200 OK`
```json
{
  "events": [
    {
      "id": 1,
      "event_type": "user.logged_in",
      "user_id": "uuid",
      "service": "auth-service",
      "timestamp": "2025-11-08T10:00:00Z",
      "data": {
        "ip_address": "192.168.1.1",
        "user_agent": "curl/7.64.1"
      }
    }
  ],
  "total": 1234,
  "limit": 100,
  "offset": 0
}
```

---

## 🏥 HEALTH & MONITORING

### GET /health
Check API Gateway health (no auth required).

**Success Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "api-gateway",
  "timestamp": "2025-11-08T10:00:00Z"
}
```

---

### GET /metrics
Prometheus metrics (no auth required).

**Success Response:** `200 OK` (Prometheus format)
```
# HELP analytics_events_processed_total Total events processed
# TYPE analytics_events_processed_total counter
analytics_events_processed_total 1234
```

---

## 🔒 AUTHENTICATION

### JWT Token Format

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user-email@example.com",
  "role": "user",
  "exp": 1699459200,
  "iat": 1699455600
}
```

**How to Use:**
1. Get token from `/api/v1/auth/login`
2. Add to requests: `Authorization: Bearer YOUR_TOKEN`
3. Token expires after 1 hour
4. Login again to get new token

---

## 📝 EVENT TYPES

Events published to Kafka and stored in analytics:

### Auth Service Events
- `user.registered` - New user created
- `user.logged_in` - User authenticated
- `user.logged_out` - User logged out

### User Service Events
- `user.updated` - Profile changed
- `user.deleted` - Account deleted

### Event Format
```json
{
  "event_type": "user.logged_in",
  "user_id": "uuid",
  "service": "auth-service",
  "timestamp": "2025-11-08T10:00:00Z",
  "data": {
    "custom": "fields",
    "vary": "by event type"
  }
}
```

---

## ⚠️ RATE LIMITING

**Limits:**
- **Default:** 60 requests per minute per IP
- **Burst:** Up to 10 requests immediately

**Headers in Response:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1699455660
```

**When Limited:** `429 Too Many Requests`
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 30
}
```

---

## 🐛 ERROR RESPONSES

### Standard Error Format
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {
    "field": "additional context"
  }
}
```

### Common Error Codes

**400 Bad Request:**
```json
{
  "error": "validation_error",
  "message": "Invalid input",
  "details": {
    "email": "Invalid email format"
  }
}
```

**401 Unauthorized:**
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing authentication token"
}
```

**403 Forbidden:**
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions"
}
```

**404 Not Found:**
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**409 Conflict:**
```json
{
  "error": "conflict",
  "message": "Email already exists"
}
```

**429 Too Many Requests:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "retry_after": 30
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "Something went wrong",
  "request_id": "req-123-456"
}
```

---

## 🧪 TESTING WITH CURL

### Complete User Flow

```bash
# 1. Register
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# 2. Login (save token)
TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.access_token')

# 3. Get profile
curl http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Update profile
curl -X PUT http://localhost:8080/api/v1/users/YOUR_USER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name"}'

# 5. Logout
curl -X POST http://localhost:8080/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🚀 INTERACTIVE API DOCS

**Swagger UI:**
- Auth Service: http://localhost:8000/docs
- User Service: http://localhost:8001/docs

**Features:**
- Try endpoints directly in browser
- See request/response schemas
- Test authentication
- No coding required

---

## 📚 MORE INFO

- **Getting Started:** See [BUILD_NOW.md](BUILD_NOW.md)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Status:** See [TRANSPARENT_STATUS.md](TRANSPARENT_STATUS.md)

---

## ✅ API STATUS

### What Works ✅
- All authentication endpoints
- All user management endpoints
- Health checks
- Metrics export
- Rate limiting
- JWT validation
- Error handling

### What Doesn't ❌
- ❌ Email verification (code exists, not configured)
- ❌ Password reset (code exists, no email service)
- ❌ OAuth/Social login (not implemented)
- ❌ Webhooks (not implemented)
- ❌ GraphQL (REST only)

### Performance
- Response time: <100ms (local testing)
- Rate limit: 60 req/min
- Token expiration: 1 hour
- Database queries: Optimized with indexes

---

**Questions?** Check Swagger UI at http://localhost:8000/docs for interactive testing.

**Ready to launch?** See [BUILD_NOW.md](BUILD_NOW.md).

