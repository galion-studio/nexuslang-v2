# Nexus Core - Authentication Service

The authentication service handles user registration, login, and JWT token management.

## Features

- User registration with email validation
- Secure password hashing (bcrypt)
- JWT token generation and verification
- Protected endpoints with authentication
- Role-based access control (RBAC)

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   cd services/auth-service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env` if needed
   - Update database connection string

3. **Run the service:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker

```bash
# Build image
docker build -t nexus-auth-service .

# Run container
docker run -p 8000:8000 nexus-auth-service
```

## API Endpoints

### POST /api/v1/auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "status": "active",
      "email_verified": false,
      "created_at": "2024-11-07T10:30:00Z"
    },
    "message": "Registration successful"
  }
}
```

### POST /api/v1/auth/login
Login and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user"
    }
  }
}
```

### GET /api/v1/auth/me
Get current user's profile (requires authentication).

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "email_verified": false,
    "created_at": "2024-11-07T10:30:00Z",
    "last_login_at": "2024-11-07T11:00:00Z"
  }
}
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | Nexus Auth Service |
| DEBUG | Debug mode | False |
| ENVIRONMENT | Environment (development/staging/production) | development |
| DATABASE_URL | PostgreSQL connection string | Required |
| JWT_SECRET_KEY | Secret key for JWT signing | Required |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| JWT_EXPIRATION_SECONDS | Token expiration time | 3600 |
| REDIS_URL | Redis connection string | Required |
| ALLOWED_ORIGINS | CORS allowed origins | ["http://localhost:3000"] |

## Security Notes

- Passwords are hashed with bcrypt (cost factor 12)
- JWT tokens expire after 1 hour by default
- All sensitive endpoints require authentication
- CORS is configured for security
- Input validation with Pydantic

## Database Schema

The service uses the `public.users` table:

```sql
CREATE TABLE public.users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(50) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP
);
```

## Development

- Code is auto-formatted with Black
- Type hints are used throughout
- All functions are documented with docstrings
- Tests cover critical functionality

## License

[To be determined]

