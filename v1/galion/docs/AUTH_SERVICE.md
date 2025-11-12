# 🔐 Authentication Service

## Overview
The Authentication Service is the security backbone of Nexus Core, handling all user authentication, authorization, and token management.

**Technology:** Python 3.11, FastAPI, PostgreSQL  
**Port:** 8000  
**Status:** Production Ready

## Core Responsibilities
- ✅ User registration with email validation
- ✅ Secure login with password verification
- ✅ JWT token generation and validation
- ✅ Two-Factor Authentication (TOTP)
- ✅ Account security management
- ✅ Session tracking and logout
- ✅ Event publishing to Kafka

## Architecture

### Technology Stack
```
Framework:    FastAPI (Python 3.11)
Database:     PostgreSQL 15
Cache:        Redis 7
Messaging:    Kafka 7.5
Security:     bcrypt, PyJWT, pyotp
```

### Dependencies
- **PostgreSQL** - User data storage
- **Redis** - Session caching, rate limiting
- **Kafka** - Event streaming (user_registered, user_login events)

## Features in Detail

### 1. User Registration
**Endpoint:** `POST /api/v1/auth/register`

**Process:**
1. Validate email format and password strength
2. Check if email already exists
3. Hash password with bcrypt (12 rounds)
4. Create user record in database
5. Publish `user_registered` event to Kafka
6. Return user data (without password)

**Security:**
- Password hashed with bcrypt (industry standard)
- Email uniqueness enforced at database level
- Input validation with Pydantic schemas

### 2. User Login
**Endpoint:** `POST /api/v1/auth/login`

**Process:**
1. Find user by email
2. Verify password hash
3. Check account status (active/suspended/locked)
4. Check if 2FA is enabled
5. If 2FA enabled: Return 2FA challenge
6. If no 2FA: Generate JWT token
7. Update last_login_at timestamp
8. Publish `user_login` event to Kafka

**Security:**
- Constant-time password comparison
- Account status validation
- Failed login attempt tracking
- 2FA support for enhanced security

### 3. Two-Factor Authentication (2FA)
**Endpoints:**
- `POST /api/v1/2fa/setup` - Initialize 2FA setup
- `POST /api/v1/2fa/verify` - Verify and enable 2FA
- `GET /api/v1/2fa/status` - Check 2FA status
- `POST /api/v1/2fa/disable` - Disable 2FA

**Implementation:**
- TOTP (Time-based One-Time Password) using pyotp
- Compatible with Google Authenticator, Authy, etc.
- QR code generation for easy setup
- 10 backup/recovery codes (single-use)
- Secure storage of TOTP secrets (encrypted)

**2FA Flow:**
1. User initiates setup (authenticated)
2. Service generates TOTP secret
3. QR code created for authenticator app
4. 10 backup codes generated and hashed
5. User scans QR code
6. User submits code to verify
7. 2FA enabled on successful verification

**Login with 2FA:**
1. User submits email/password
2. Credentials verified
3. Service returns `requires_2fa: true` with user_id
4. User submits 2FA code (or backup code)
5. Code verified
6. JWT token issued

### 4. JWT Token Management
**Token Specification:**
- Algorithm: HS256 (HMAC with SHA-256)
- Expiration: 1 hour (3600 seconds)
- Payload: user_id, email, role, issued_at, expires_at

**Token Structure:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user",
  "iat": 1699520000,
  "exp": 1699523600
}
```

**Validation:**
- Signature verification
- Expiration check
- User existence check
- Account status validation

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(50) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    totp_verified_at TIMESTAMPTZ,
    backup_codes JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
```

## Security Model

### Password Security
- **Hashing:** bcrypt with 12 rounds (cost factor)
- **Minimum Strength:** 8 characters (configurable)
- **Storage:** Never store plain passwords
- **Comparison:** Constant-time to prevent timing attacks

### Token Security
- **Secret Key:** 256-bit random key (generated per environment)
- **Algorithm:** HS256 (HMAC-SHA256)
- **Expiration:** 1 hour (short-lived for security)
- **Refresh:** Token refresh endpoint (future feature)

### 2FA Security
- **TOTP:** 30-second time window, 6-digit codes
- **Secret Storage:** Encrypted TOTP secrets
- **Backup Codes:** Hashed with bcrypt, single-use
- **Rate Limiting:** 5 attempts per minute per user

### Account Protection
- **Account Statuses:**
  - `active` - Normal operation
  - `suspended` - Temporarily disabled (admin action)
  - `locked` - Automatically locked (security trigger)
  - `inactive` - User-initiated deactivation

## Configuration

### Environment Variables
```bash
# Server
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nexuscore

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=user-events

# Security
BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://galion.app
```

## API Documentation

### Interactive Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **HTML Docs:** [auth-service.html](../api-docs/auth-service.html)

### Authentication Flow
```
1. Register: POST /api/v1/auth/register
   → Returns: User data

2. Login: POST /api/v1/auth/login
   → Returns: JWT token (or 2FA challenge)

3. Use Token: Include in header
   Authorization: Bearer {token}

4. Get Profile: GET /api/v1/auth/me
   → Returns: Current user data
```

## Event Publishing

### Kafka Events
```json
// user_registered
{
  "event_type": "user_registered",
  "user_id": "uuid",
  "service": "auth-service",
  "timestamp": "2024-11-09T10:30:00Z",
  "data": {
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}

// user_login
{
  "event_type": "user_login",
  "user_id": "uuid",
  "service": "auth-service",
  "timestamp": "2024-11-09T15:45:00Z",
  "data": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "2fa_used": true
  }
}
```

## Monitoring

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "kafka": "connected"
}
```

### Metrics (Prometheus)
- `auth_registrations_total` - Total registrations
- `auth_logins_total` - Total successful logins
- `auth_login_failures_total` - Failed login attempts
- `auth_2fa_setups_total` - 2FA activations
- `auth_request_duration_seconds` - Request latency

## Error Handling

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - User registered
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account suspended/locked
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "detail": "Email already registered",
  "status_code": 400,
  "timestamp": "2024-11-09T10:30:00Z"
}
```

## Development

### Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd services/auth-service
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start service
uvicorn app.main:app --reload --port 8000
```

### Testing
```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test specific endpoint
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

## Production Deployment

### Docker
```bash
# Build image
docker build -t nexus-auth-service .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name auth-service \
  nexus-auth-service
```

### Health Checks
- **Endpoint:** `GET /health`
- **Interval:** 10 seconds
- **Timeout:** 5 seconds
- **Retries:** 3

### Scaling
- **Horizontal:** Multiple instances behind load balancer
- **Database:** PostgreSQL connection pooling (10 connections per instance)
- **Redis:** Shared cache across instances
- **Stateless:** No local session storage

## Security Considerations

### Production Checklist
- ✅ Use strong JWT_SECRET_KEY (256-bit random)
- ✅ Enable HTTPS/TLS in production
- ✅ Set secure CORS origins
- ✅ Enable rate limiting
- ✅ Monitor failed login attempts
- ✅ Rotate secrets periodically
- ✅ Enable database SSL connections
- ✅ Implement account lockout after N failed attempts
- ✅ Log all authentication events
- ✅ Enable audit logging

## Troubleshooting

### Common Issues

**Issue:** Database connection failed  
**Fix:** Check DATABASE_URL, ensure PostgreSQL is running

**Issue:** JWT token invalid  
**Fix:** Ensure JWT_SECRET_KEY matches across all services

**Issue:** 2FA codes not working  
**Fix:** Check server time sync (TOTP requires accurate time)

**Issue:** Kafka events not published  
**Fix:** Verify Kafka broker connectivity, check KAFKA_BROKERS

## Future Enhancements
- 🔜 OAuth2 provider support (Google, GitHub)
- 🔜 Magic link authentication (passwordless)
- 🔜 Token refresh mechanism
- 🔜 Account recovery flow
- 🔜 Email verification
- 🔜 Password reset via email
- 🔜 Biometric authentication support
- 🔜 Security audit logging
- 🔜 Account activity dashboard

## Support
- **API Docs:** http://localhost:8000/docs
- **Status Page:** [nexus-status.html](../nexus-status.html)
- **Issues:** GitHub Issues

---

**Last Updated:** November 9, 2024  
**Service Version:** 1.0.0  
**Status:** ✅ Production Ready

