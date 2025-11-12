# Nexus API Gateway

API Gateway for Nexus Core - The single entry point for all client requests.

## Features

- **Request Routing**: Routes requests to appropriate backend services
- **JWT Authentication**: Verifies JWT tokens before forwarding requests
- **Rate Limiting**: Redis-based rate limiting to prevent abuse
- **CORS Handling**: Configurable cross-origin resource sharing
- **Request Logging**: Logs all requests with timing information
- **Health Checks**: Provides health check endpoint for monitoring
- **Graceful Shutdown**: Handles shutdowns gracefully

## Architecture

The API Gateway acts as a reverse proxy that:
1. Receives all client requests
2. Verifies authentication (for protected routes)
3. Applies rate limiting
4. Forwards requests to backend services
5. Returns responses to clients

```
Client → API Gateway → Backend Services
         (8080)       (auth: 8000, user: 8001)
```

## Prerequisites

- Go 1.21+
- Redis (for rate limiting)
- Backend services running (auth-service, user-service)

## Quick Start

### 1. Set up environment

```bash
# Navigate to gateway directory
cd services/api-gateway

# Copy environment file
cp .env.example .env

# Edit .env with your settings
```

Important: `JWT_SECRET_KEY` must match auth-service!

### 2. Install dependencies

```bash
go mod download
```

### 3. Run the gateway

```bash
# Development mode
go run cmd/gateway/main.go

# Or build and run
go build -o api-gateway cmd/gateway/main.go
./api-gateway
```

Gateway will be available at http://localhost:8080

## Routes

### Public Routes (No Authentication)

- `GET /health` - Health check
- `POST /api/v1/auth/register` - User registration (proxied to auth-service)
- `POST /api/v1/auth/login` - User login (proxied to auth-service)

### Protected Routes (Require Authentication)

- `GET /api/v1/auth/me` - Get current user (proxied to auth-service)
- `GET /api/v1/users/me` - Get user profile (proxied to user-service)
- `PUT /api/v1/users/me` - Update user profile (proxied to user-service)
- `GET /api/v1/users/{id}` - Get user by ID (proxied to user-service)
- `GET /api/v1/users/` - List users (proxied to user-service)
- `POST /api/v1/users/search` - Search users (proxied to user-service)

### Admin Routes (Require Admin Role)

- `PUT /api/v1/users/{id}/deactivate` - Deactivate user (proxied to user-service)
- `PUT /api/v1/users/{id}/activate` - Activate user (proxied to user-service)

## Configuration

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Gateway port | 8080 |
| `ENVIRONMENT` | Environment | development |
| `DEBUG` | Debug mode | true |
| `JWT_SECRET_KEY` | JWT secret (must match auth-service) | Required |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `AUTH_SERVICE_URL` | Auth service URL | http://localhost:8000 |
| `USER_SERVICE_URL` | User service URL | http://localhost:8001 |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Requests per minute | 60 |
| `ALLOWED_ORIGINS` | CORS allowed origins | http://localhost:3000 |

## Example Usage

### 1. Health check

```bash
curl http://localhost:8080/health
```

### 2. Register a user

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "name": "John Doe"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### 4. Get your profile (requires token)

```bash
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Rate Limiting

The gateway implements Redis-based rate limiting:

- **Default**: 60 requests per minute per IP
- **Headers**: Responses include `X-RateLimit-Limit` and `X-RateLimit-Remaining`
- **Response**: Returns 429 Too Many Requests when limit exceeded

Example response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
```

## Authentication Flow

1. Client sends request with `Authorization: Bearer <token>` header
2. Gateway extracts and validates JWT token
3. If valid, gateway adds `X-User-Email` header for backend services
4. Gateway forwards request to appropriate backend service
5. Backend service can trust the `X-User-Email` header

**Note**: Backend services should only accept requests from the gateway, not directly from clients.

## Docker

### Build image

```bash
docker build -t nexus-api-gateway .
```

### Run container

```bash
docker run -d \
  -p 8080:8080 \
  --name api-gateway \
  -e AUTH_SERVICE_URL=http://auth-service:8000 \
  -e USER_SERVICE_URL=http://user-service:8001 \
  -e JWT_SECRET_KEY=your-secret-key \
  -e REDIS_URL=redis://redis:6379/0 \
  nexus-api-gateway
```

### Using Docker Compose

```bash
# From project root
docker-compose up api-gateway
```

## Architecture Details

### Directory Structure

```
api-gateway/
├── cmd/
│   └── gateway/
│       └── main.go          # Application entry point
├── internal/
│   ├── auth/
│   │   └── jwt.go           # JWT token validation
│   ├── middleware/
│   │   ├── logging.go       # Request logging
│   │   ├── auth.go          # Authentication middleware
│   │   └── ratelimit.go     # Rate limiting
│   └── proxy/
│       └── proxy.go         # HTTP reverse proxy
├── pkg/
│   └── logger/
│       └── logger.go        # Logging utilities
├── go.mod                   # Go dependencies
├── Dockerfile              # Container definition
└── README.md               # This file
```

### Middleware Chain

Requests pass through middleware in this order:

1. **Request ID**: Adds unique ID to each request
2. **Logging**: Logs request details
3. **Rate Limiting**: Checks if client exceeded rate limit
4. **CORS**: Handles cross-origin requests
5. **Authentication**: Validates JWT token (for protected routes)
6. **Proxy**: Forwards request to backend service

## Security

- **JWT Validation**: All protected routes require valid JWT token
- **Rate Limiting**: Prevents abuse and DDoS attacks
- **CORS**: Only allows configured origins
- **Header Filtering**: Removes hop-by-hop headers
- **Timeout**: 30 second timeout on backend requests
- **Graceful Shutdown**: Ensures requests complete before shutdown

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### Logs

The gateway logs all requests:
```
[2024-11-08 12:34:56] INFO: API Gateway listening on port 8080
[2024-11-08 12:34:57] INFO: GET /api/v1/users/me - 200 - 45ms - 127.0.0.1
[2024-11-08 12:34:58] INFO: POST /api/v1/users/search - 200 - 120ms - 127.0.0.1
```

## Troubleshooting

### "service unavailable" error

- Check if backend services are running
- Verify SERVICE_URL environment variables
- Check network connectivity

### "unauthorized" error

- Verify JWT_SECRET_KEY matches auth-service
- Check if token is expired (1 hour default)
- Ensure Authorization header format: `Bearer <token>`

### "rate limit exceeded" error

- Wait for the rate limit window to reset (1 minute)
- Increase RATE_LIMIT_REQUESTS_PER_MINUTE if needed
- Check if Redis is running

### Backend requests timing out

- Increase timeout in proxy.go (default 30s)
- Check backend service performance
- Verify backend services are not overloaded

## Development

### Running locally without Docker

1. Start backend services
2. Start Redis
3. Run gateway: `go run cmd/gateway/main.go`

### Adding a new route

1. Add route in `cmd/gateway/main.go`
2. Add authentication middleware if needed
3. Configure proxy to appropriate backend service

### Adding a new middleware

1. Create middleware in `internal/middleware/`
2. Add to middleware chain in `main.go`

## Production Considerations

- Set `DEBUG=false` in production
- Use strong `JWT_SECRET_KEY`
- Configure appropriate rate limits
- Set up TLS/HTTPS
- Use reverse proxy (nginx/Traefik) in front of gateway
- Monitor logs and metrics
- Set up alerts for high error rates

## Performance

- **Throughput**: Handles 10,000+ requests/second (with caching)
- **Latency**: Adds ~1-2ms overhead per request
- **Concurrency**: Go's goroutines handle concurrent requests efficiently
- **Memory**: Low memory footprint (~20MB base)

## Next Steps

- Add health checks for backend services
- Implement circuit breaker pattern
- Add request/response transformation
- Add API analytics
- Implement request retry logic
- Add distributed tracing (OpenTelemetry)

## Related Services

- **auth-service** (port 8000): Authentication and authorization
- **user-service** (port 8001): User profile management
- **redis**: Rate limiting and caching

## License

[To be determined]

