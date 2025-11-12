# NexusCore Cursor Rules ⭐ DEVELOPMENT STANDARDS
## AI Code Generation Standards for Cursor

**Version:** 1.0  
**Last Updated:** November 2025  
**Purpose:** Define development rules, conventions, and standards for Cursor AI code generation  
**Scope:** All NexusCore services (API Gateway, Voice, Auth, Analytics, ML Training)

---

## 📋 Quick Reference

### Technology Stack
- **Backend:** Go 1.21+ (API Gateway, Analytics), Python 3.11+ (Auth, Voice, ML)
- **Frontend:** React 18 + TypeScript + Vite
- **Database:** PostgreSQL 15 + Redis 7
- **Orchestration:** Kubernetes 1.28+
- **Observability:** Prometheus + Grafana + ELK Stack

### Code Quality Targets
- **Test Coverage:** >80% for all services
- **API Latency (p99):** <50ms
- **Uptime SLA:** 99.9%
- **Security:** Zero known vulnerabilities (Snyk/Trivy scans)

---

## 🏗️ Architecture Principles

### 1. Microservices Architecture

#### Service Boundaries
- **API Gateway:** Routing, auth middleware, rate limiting
- **Auth Service:** User authentication, JWT tokens, OAuth
- **User Service:** Profile management, settings
- **Voice Service:** STT, TTS, voice-to-voice orchestration
- **Analytics Service:** Event collection, metrics aggregation
- **Scraping Service:** Web scraping, data extraction
- **ML Training Service:** Model training, fine-tuning, serving

#### Communication Patterns
- **Synchronous:** HTTP/2 with gRPC for service-to-service
- **Asynchronous:** Redis pub/sub for events, Kafka for high-throughput
- **API Versioning:** `/api/v1`, `/api/v2` with backward compatibility

### 2. Database Design

#### Schema Standards
```sql
-- Table naming: snake_case, plural
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index naming: idx_<table>_<columns>
CREATE INDEX idx_users_email ON users(email);

-- Foreign key naming: fk_<table>_<column>
ALTER TABLE profiles ADD CONSTRAINT fk_profiles_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

#### Query Optimization
- **Always use indexed columns** in WHERE clauses
- **Limit result sets:** Default 100, max 1000 per query
- **Use prepared statements:** Prevent SQL injection
- **Avoid N+1 queries:** Use JOINs or batch loading

```go
// ❌ BAD: N+1 query problem
for _, user := range users {
    profile := db.GetProfile(user.ID) // Separate query per user
}

// ✅ GOOD: Single query with JOIN
profiles := db.GetProfilesForUsers(userIDs)
```

### 3. API Design Standards

#### REST Conventions
- **Resources:** Plural nouns (`/users`, `/posts`)
- **Actions:** HTTP verbs (GET, POST, PUT, PATCH, DELETE)
- **Nesting:** Max 2 levels (`/users/{id}/posts/{postId}`)
- **Filtering:** Query params (`/users?role=admin&limit=50`)

#### Request/Response Format
```json
// POST /api/v1/users
{
  "email": "user@example.com",
  "name": "John Doe"
}

// Response: 201 Created
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-11-09T13:30:00Z"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}

// Error Response: 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": {
      "field": "email",
      "reason": "missing_field"
    }
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### Error Codes
```go
const (
    ErrValidation      = "VALIDATION_ERROR"      // 400
    ErrUnauthorized    = "UNAUTHORIZED"          // 401
    ErrForbidden       = "FORBIDDEN"             // 403
    ErrNotFound        = "NOT_FOUND"             // 404
    ErrConflict        = "CONFLICT"              // 409
    ErrRateLimit       = "RATE_LIMIT_EXCEEDED"   // 429
    ErrInternal        = "INTERNAL_SERVER_ERROR" // 500
    ErrUnavailable     = "SERVICE_UNAVAILABLE"   // 503
)
```

---

## 🔧 Go Development Standards

### Project Structure
```
services/api-gateway/
├── cmd/
│   └── gateway/
│       └── main.go              # Entry point
├── internal/                     # Private application code
│   ├── auth/
│   │   ├── middleware.go
│   │   └── jwt.go
│   ├── proxy/
│   │   └── reverse_proxy.go
│   └── middleware/
│       ├── logging.go
│       ├── ratelimit.go
│       └── cors.go
├── pkg/                          # Public library code
│   └── logger/
│       └── logger.go
├── Dockerfile
├── go.mod
├── go.sum
└── README.md
```

### Code Style

#### Naming Conventions
```go
// Exported (public) names: PascalCase
type UserService struct {}
func (s *UserService) CreateUser() {}

// Unexported (private) names: camelCase
type userRepository struct {}
func (r *userRepository) findByEmail() {}

// Constants: PascalCase
const MaxRetries = 3

// Acronyms: Keep capitalization (HTTP, API, ID)
type HTTPClient struct {}  // Not HttpClient
type UserID string         // Not UserId
```

#### Error Handling
```go
// ❌ BAD: Ignoring errors
data, _ := os.ReadFile("config.json")

// ✅ GOOD: Always check errors
data, err := os.ReadFile("config.json")
if err != nil {
    return fmt.Errorf("failed to read config: %w", err)
}

// ✅ GOOD: Wrap errors with context
if err := db.CreateUser(user); err != nil {
    return fmt.Errorf("CreateUser(%s): %w", user.Email, err)
}
```

#### Concurrency
```go
// ✅ GOOD: Use context for cancellation
func ProcessData(ctx context.Context, data []Item) error {
    for _, item := range data {
        select {
        case <-ctx.Done():
            return ctx.Err() // Graceful cancellation
        default:
            if err := process(item); err != nil {
                return err
            }
        }
    }
    return nil
}

// ✅ GOOD: Use sync.WaitGroup for goroutines
var wg sync.WaitGroup
for _, task := range tasks {
    wg.Add(1)
    go func(t Task) {
        defer wg.Done()
        processTask(t)
    }(task)
}
wg.Wait()

// ✅ GOOD: Use channels for communication
results := make(chan Result, len(tasks))
for _, task := range tasks {
    go func(t Task) {
        results <- processTask(t)
    }(task)
}
```

### Testing Standards

#### Unit Tests
```go
// File: user_service_test.go
func TestUserService_CreateUser(t *testing.T) {
    tests := []struct {
        name    string
        input   *User
        wantErr bool
    }{
        {
            name:    "valid user",
            input:   &User{Email: "test@example.com"},
            wantErr: false,
        },
        {
            name:    "missing email",
            input:   &User{Email: ""},
            wantErr: true,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            svc := NewUserService()
            err := svc.CreateUser(tt.input)
            
            if (err != nil) != tt.wantErr {
                t.Errorf("CreateUser() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

#### Test Coverage
```bash
# Run tests with coverage
go test -v -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Enforce minimum coverage (CI/CD)
go test -cover ./... | grep -E 'coverage: [0-9]+' | awk '{print $2}' | \
  awk -F% '{if ($1 < 80) {print "Coverage below 80%"; exit 1}}'
```

---

## 🐍 Python Development Standards

### Project Structure
```
services/auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings (Pydantic)
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── api/                     # Routes
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── users.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   └── test_auth.py
├── Dockerfile
├── requirements.txt
└── README.md
```

### Code Style (PEP 8 + Black)

#### Naming Conventions
```python
# Functions/variables: snake_case
def create_user(email: str) -> User:
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"

# Private members: Leading underscore
class User:
    def __init__(self, email: str):
        self._email = email  # Private attribute
    
    def _validate(self):     # Private method
        pass
```

#### Type Hints (Mandatory)
```python
from typing import Optional, List, Dict

def get_user(user_id: str) -> Optional[User]:
    """Retrieve user by ID.
    
    Args:
        user_id: UUID string
    
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()

async def get_users(
    skip: int = 0, 
    limit: int = 100
) -> List[User]:
    """Get paginated users."""
    return await db.query(User).offset(skip).limit(limit).all()
```

### FastAPI Best Practices

#### Router Organization
```python
# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account with email and password"
)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user."""
    try:
        return await service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

#### Dependency Injection
```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Validate JWT token and return user."""
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    user = await db.get_user(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

# Usage in route
@router.get("/me")
async def get_current_user_profile(
    user: User = Depends(get_current_user)
):
    return user
```

### Testing (pytest + pytest-asyncio)

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get auth headers for protected endpoints."""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# tests/test_users.py
def test_create_user(client):
    response = client.post("/api/v1/users", json={
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

def test_get_current_user(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()
```

---

## ⚛️ React/TypeScript Standards

### Project Structure
```
frontend/
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── Button.module.css
│   │   └── index.ts
│   ├── pages/                   # Route components
│   │   ├── Home/
│   │   │   └── HomePage.tsx
│   │   └── Dashboard/
│   │       └── DashboardPage.tsx
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   └── useVoice.ts
│   ├── services/                # API clients
│   │   ├── api.ts
│   │   └── auth.service.ts
│   ├── store/                   # State management (Zustand)
│   │   └── authStore.ts
│   ├── types/                   # TypeScript types
│   │   └── user.types.ts
│   ├── utils/                   # Helper functions
│   │   └── format.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### Component Structure

```typescript
// components/Button/Button.tsx
import React from 'react';
import styles from './Button.module.css';

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
}) => {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]}`}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
};

// components/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

### State Management (Zustand)

```typescript
// store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          throw new Error('Login failed');
        }

        const { user, access_token } = await response.json();
        set({ user, accessToken: access_token, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, accessToken: null, isAuthenticated: false });
      },

      refreshToken: async () => {
        // Implement token refresh logic
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        accessToken: state.accessToken 
      }),
    }
  )
);
```

---

## 🐳 Docker & Kubernetes Standards

### Dockerfile Best Practices

```dockerfile
# services/api-gateway/Dockerfile

# Use specific version tags (not "latest")
FROM golang:1.21-alpine AS builder

# Set working directory
WORKDIR /app

# Copy dependency files first (cache optimization)
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo \
    -ldflags '-s -w' \
    -o /bin/gateway ./cmd/gateway

# Final stage: minimal image
FROM alpine:3.18

# Add ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN addgroup -g 1000 app && adduser -D -u 1000 -G app app

# Copy binary from builder
COPY --from=builder /bin/gateway /bin/gateway

# Use non-root user
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/bin/gateway", "healthcheck"]

# Run binary
ENTRYPOINT ["/bin/gateway"]
```

### Kubernetes Manifests

```yaml
# k8s/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: production
  labels:
    app: api-gateway
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
        version: v1
    spec:
      serviceAccountName: api-gateway
      containers:
      - name: gateway
        image: ghcr.io/galion/api-gateway:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: connection-string
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
```

---

## 🔐 Security Standards

### Authentication & Authorization

```go
// internal/auth/middleware.go
package auth

import (
	"context"
	"net/http"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

type contextKey string

const UserContextKey contextKey = "user"

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract token from Authorization header
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
			return
		}

		// Bearer token format
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			http.Error(w, "Invalid Authorization header format", http.StatusUnauthorized)
			return
		}

		token := parts[1]

		// Validate JWT
		claims, err := validateJWT(token)
		if err != nil {
			http.Error(w, "Invalid token", http.StatusUnauthorized)
			return
		}

		// Add user to context
		ctx := context.WithValue(r.Context(), UserContextKey, claims.UserID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func validateJWT(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return jwtSecret, nil
	})

	if err != nil || !token.Valid {
		return nil, err
	}

	claims, ok := token.Claims.(*Claims)
	if !ok {
		return nil, jwt.ErrInvalidKey
	}

	return claims, nil
}

type Claims struct {
	UserID string `json:"sub"`
	Email  string `json:"email"`
	jwt.RegisteredClaims
}
```

### Input Validation

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @validator('name')
    def name_no_special_chars(cls, v):
        """Prevent XSS in name field."""
        if re.search(r'[<>]', v):
            raise ValueError('Name cannot contain HTML tags')
        return v.strip()
```

---

## 📊 Observability Standards

### Logging

```go
// pkg/logger/logger.go
package logger

import (
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var Log *zap.Logger

func Init(environment string) {
	var config zap.Config

	if environment == "production" {
		config = zap.NewProductionConfig()
	} else {
		config = zap.NewDevelopmentConfig()
	}

	config.EncoderConfig.TimeKey = "timestamp"
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

	var err error
	Log, err = config.Build()
	if err != nil {
		panic(err)
	}
}

// Usage
import "github.com/galion/api-gateway/pkg/logger"

logger.Log.Info("User created",
	zap.String("user_id", userID),
	zap.String("email", email),
	zap.Duration("duration", time.Since(start)),
)

logger.Log.Error("Database connection failed",
	zap.Error(err),
	zap.String("database", "postgres"),
)
```

### Metrics (Prometheus)

```go
// pkg/metrics/metrics.go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	HTTPRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "path", "status"},
	)

	HTTPRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1},
		},
		[]string{"method", "path"},
	)

	ActiveConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "active_connections",
			Help: "Number of active connections",
		},
	)
)

// Usage
import "time"

start := time.Now()
// ... handle request ...
duration := time.Since(start).Seconds()

HTTPRequestsTotal.WithLabelValues("GET", "/api/v1/users", "200").Inc()
HTTPRequestDuration.WithLabelValues("GET", "/api/v1/users").Observe(duration)
```

---

## ✅ Pre-Commit Checklist

### Before Every Commit
- [ ] Code passes linter (`golangci-lint`, `pylint`, `eslint`)
- [ ] Tests pass (`go test`, `pytest`, `npm test`)
- [ ] Test coverage >80%
- [ ] No secrets in code (`trufflehog`, `detect-secrets`)
- [ ] Security scan passed (`trivy`, `snyk`)
- [ ] Documentation updated (if public API changed)

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "Running pre-commit checks..."

# 1. Linting
echo "Linting Go code..."
golangci-lint run ./...

echo "Linting Python code..."
pylint app/

# 2. Tests
echo "Running tests..."
go test -v -cover ./...
pytest --cov=app --cov-report=term-missing

# 3. Security
echo "Scanning for secrets..."
trufflehog filesystem . --fail

echo "Scanning for vulnerabilities..."
trivy fs . --severity HIGH,CRITICAL --exit-code 1

echo "✅ All checks passed!"
```

---

## 📚 Documentation Standards

### Code Comments

```go
// CreateUser creates a new user account.
//
// This function validates the input, hashes the password, and stores
// the user in the database. It returns the created user with an ID.
//
// Parameters:
//   - email: User's email address (must be unique)
//   - password: Plain text password (will be hashed)
//
// Returns:
//   - *User: Created user object
//   - error: Validation or database error
//
// Example:
//
//	user, err := CreateUser("user@example.com", "password123")
//	if err != nil {
//	    log.Fatal(err)
//	}
func CreateUser(email, password string) (*User, error) {
	// Implementation...
}
```

### README Template

```markdown
# Service Name

Brief description of the service.

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

- Go 1.21+
- PostgreSQL 15+
- Redis 7+

## Installation

\```bash
# Clone repository
git clone https://github.com/galion/service-name.git

# Install dependencies
go mod download

# Run migrations
go run migrations/*.go

# Start service
go run cmd/service/main.go
\```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://...` |
| `REDIS_URL` | Redis connection string | `redis://...` |
| `PORT` | HTTP server port | `8080` |

## API Documentation

See [API.md](./API.md) for detailed API documentation.

## Testing

\```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific test
go test -v -run TestCreateUser
\```

## Deployment

See [docs/deployment.md](./docs/deployment.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT License. See [LICENSE](./LICENSE).
```

---

## 📝 Document Control

**Document Owner:** CTO  
**Classification:** Internal - Required Reading  
**Review Cycle:** Monthly  
**Next Review:** December 2025  

**Version History:**
- v1.0 (Nov 2025): Initial release
- v0.9 (Nov 2025): Team review
- v0.5 (Oct 2025): Draft

---

**🚀 Follow these standards for consistent, high-quality code. Happy coding!**

