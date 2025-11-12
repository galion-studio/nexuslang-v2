# 🌐 API Gateway

## Overview
The API Gateway is the single entry point for all client requests to Nexus Core. It provides authentication, rate limiting, request routing, and a unified API interface while hiding the complexity of the microservices architecture.

**Technology:** Go 1.21, Gorilla Mux, Redis  
**Port:** 8080  
**Status:** Production Ready

## Core Responsibilities
- ✅ Request routing to backend services
- ✅ JWT token validation
- ✅ Rate limiting (60 requests/minute)
- ✅ CORS configuration
- ✅ Security headers
- ✅ Request ID tracking
- ✅ Centralized logging
- ✅ Health check aggregation

## Architecture

### Technology Stack
```
Language:     Go 1.21
Router:       Gorilla Mux
Cache:        Redis 7
Monitoring:   Prometheus
```

### Routing Rules
```
/api/v1/auth/*     → Auth Service (port 8000)     [No Auth Required]
/api/v1/users/*    → User Service (port 8001)     [Auth Required]
/api/v1/content/*  → Content Service (port 8002)  [Auth Required]
/health            → Gateway Health Check          [No Auth Required]
/metrics           → Prometheus Metrics            [No Auth Required]
```

## Features

### 1. Request Routing
Intelligent proxy that forwards requests to the appropriate backend service based on URL path.

**Routing Logic:**
- Match URL prefix
- Forward to backend service
- Preserve headers and body
- Return response to client

### 2. Authentication Middleware
Validates JWT tokens for protected routes.

**Process:**
1. Extract token from Authorization header
2. Verify signature using shared secret
3. Check expiration
4. Decode user claims
5. Inject user context into request
6. Forward to backend service

**Protected Routes:**
- `/api/v1/users/*`
- `/api/v1/content/*`
- Any route not in public list

### 3. Rate Limiting
Redis-based sliding window rate limiter.

**Configuration:**
- Limit: 60 requests per minute per IP
- Storage: Redis (distributed across instances)
- Response: 429 Too Many Requests
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining

### 4. Security Headers
Automatically adds security headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

### 5. Request ID Tracking
Generates unique ID for every request for distributed tracing.

**Flow:**
1. Check for X-Request-ID header
2. If absent, generate UUID
3. Add to request context
4. Forward to backend services
5. Include in response headers
6. Log in all services

## Configuration

### Environment Variables
```bash
# Server
PORT=8080
ENVIRONMENT=production
DEBUG=false

# JWT
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256

# Backend Services
AUTH_SERVICE_URL=http://auth-service:8000
USER_SERVICE_URL=http://user-service:8001
CONTENT_SERVICE_URL=http://content-service:8002

# Redis
REDIS_URL=redis://redis:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://galion.app
```

## Middleware Pipeline
Every request flows through this pipeline (in order):

1. **CORS** - Handle preflight and origin validation
2. **Request ID** - Generate/extract unique request ID
3. **Logging** - Log request details
4. **Rate Limiter** - Check rate limits
5. **Authentication** - Validate JWT (if required)
6. **Proxy** - Forward to backend service

## Monitoring

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### Prometheus Metrics
```
GET /metrics

Metrics:
- api_gateway_up (gauge)
- http_requests_total (counter)
- http_request_duration_seconds (histogram)
- rate_limit_hits_total (counter)
```

## Performance

| Metric | Value |
|--------|-------|
| Average Latency | < 10ms (gateway only) |
| Max Throughput | 10,000 requests/sec |
| Read Timeout | 15 seconds |
| Write Timeout | 15 seconds |
| Idle Timeout | 60 seconds |
| Max Connections | Unlimited (Go handles efficiently) |

## Error Responses

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Unauthorized | Missing/invalid JWT token |
| 429 | Too Many Requests | Rate limit exceeded |
| 502 | Bad Gateway | Backend service unavailable |
| 503 | Service Unavailable | Gateway overloaded |
| 504 | Gateway Timeout | Backend timeout (15s) |

## Development

### Local Setup
```bash
cd services/api-gateway

# Install dependencies
go mod download

# Run gateway
go run cmd/gateway/main.go
```

### Testing
```bash
# Unit tests
go test ./...

# Integration tests
go test -tags=integration ./...

# Load testing
hey -n 10000 -c 100 http://localhost:8080/health
```

## Production Deployment

### Docker
```bash
docker build -t nexus-api-gateway .
docker run -d -p 8080:8080 --env-file .env nexus-api-gateway
```

### Scaling
- Deploy multiple instances behind load balancer
- Stateless design (no local sessions)
- Shared Redis for rate limiting
- Auto-scale based on CPU (target: 70%)

## Security

### Production Checklist
- ✅ Use strong JWT secret
- ✅ Enable HTTPS/TLS
- ✅ Configure CORS properly
- ✅ Enable rate limiting
- ✅ Monitor suspicious patterns
- ✅ Implement IP whitelist/blacklist
- ✅ Use security headers
- ✅ Log all requests

---

**Last Updated:** November 9, 2024  
**Service Version:** 1.0.0  
**Status:** ✅ Production Ready

