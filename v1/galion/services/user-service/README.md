# Nexus User Service

User profile management, search, and admin operations for Nexus Core.

## Features

- **Profile Management**: Users can view and update their profiles
- **User Search**: Search users by name, email, role
- **Admin Operations**: Activate/deactivate user accounts
- **JWT Authentication**: Secure token-based authentication
- **Pagination**: Efficient handling of large user lists

## Prerequisites

- Python 3.11+
- PostgreSQL database (shared with auth-service)
- Redis (for caching)
- Running auth-service (for user creation)

## Quick Start

### 1. Set up environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows PowerShell:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Important: `JWT_SECRET_KEY` must match the auth-service for token verification!

### 3. Run the service

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8001

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

Service will be available at http://localhost:8001

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## API Endpoints

### Public Endpoints

- `GET /health` - Health check

### Authenticated Endpoints

- `GET /api/v1/users/me` - Get current user's profile
- `PUT /api/v1/users/me` - Update current user's profile
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/` - List all users (paginated)
- `POST /api/v1/users/search` - Search users

### Admin Endpoints

- `PUT /api/v1/users/{user_id}/deactivate` - Deactivate user account
- `PUT /api/v1/users/{user_id}/activate` - Activate user account

## Example Usage

### 1. Get your profile

```bash
curl http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Update your profile

```bash
curl -X PUT http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "bio": "Software engineer passionate about AI",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

### 3. Search for users

```bash
curl -X POST http://localhost:8001/api/v1/users/search \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "john",
    "limit": 10,
    "offset": 0
  }'
```

### 4. Get user by ID

```bash
curl http://localhost:8001/api/v1/users/{user_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py -v
```

## Docker

### Build image

```bash
docker build -t nexus-user-service .
```

### Run container

```bash
docker run -d \
  -p 8001:8001 \
  --name user-service \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  nexus-user-service
```

### Using Docker Compose

```bash
# From project root
docker-compose up user-service
```

## Architecture

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── database.py          # Database connection
├── dependencies.py      # Authentication dependencies
├── api/
│   └── v1/
│       └── users.py     # User endpoints
├── models/
│   └── user.py          # User database model
├── schemas/
│   └── user.py          # Pydantic schemas
└── services/
    └── user.py          # Business logic
```

## Dependencies

- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM for database access
- **Pydantic**: Data validation
- **python-jose**: JWT token handling
- **PostgreSQL**: Primary database

## Configuration

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Nexus User Service" |
| `DEBUG` | Debug mode | False |
| `ENVIRONMENT` | Environment | "development" |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT (must match auth-service) | Required |
| `JWT_ALGORITHM` | JWT algorithm | "HS256" |
| `REDIS_URL` | Redis connection string | Required |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka servers | Required |

## Troubleshooting

### "Could not validate credentials"

- Make sure JWT_SECRET_KEY matches auth-service
- Check if token is expired (1 hour default)
- Verify token format: `Bearer <token>`

### "Connection refused" (Database)

- Check if PostgreSQL is running
- Verify DATABASE_URL is correct
- Ensure database exists and user has permissions

### "User not found"

- User must be created via auth-service first
- This service does NOT create users, only manages them

## Development

### Adding a new endpoint

1. Add schema in `app/schemas/user.py`
2. Add business logic in `app/services/user.py`
3. Add endpoint in `app/api/v1/users.py`
4. Write tests in `tests/`

### Code style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add comments for complex logic

## Next Steps

- Add Redis caching for user profiles
- Add Kafka events for user updates
- Add email notifications
- Add user analytics
- Add rate limiting

## Related Services

- **auth-service** (port 8000): User registration and login
- **api-gateway** (port 8080): Main entry point, routes requests
- **analytics-service**: Event tracking and metrics

## License

[To be determined]

