# Nexus Core - Testing Guide

Complete guide for testing the Nexus Core platform.

## Testing Strategy

We follow a multi-layered testing approach:

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test service interactions
3. **End-to-End Tests** - Test complete user workflows
4. **API Tests** - Test API contracts
5. **Load Tests** - Test system performance

## Prerequisites

- Docker installed and running
- All services running (or available)
- Postman (for API testing)
- Python 3.11+ with pytest (for Python services)
- Go 1.21+ (for Go services)

## Quick Test (5 Minutes)

### 1. Start the infrastructure

```bash
# From project root
docker-compose up -d postgres redis
```

Wait for services to be healthy:
```bash
docker-compose ps
```

### 2. Test Auth Service

```bash
cd services/auth-service

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

Expected output: All tests pass ✅

### 3. Test User Service

```bash
cd services/user-service

# Use same virtual environment or create new one
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

Expected output: All tests pass ✅

### 4. Test API Gateway

```bash
cd services/api-gateway

# Run Go tests (when added)
go test ./... -v
```

## Unit Testing

### Auth Service Tests

Location: `services/auth-service/tests/test_auth.py`

**What's tested:**
- User registration
- User login
- JWT token generation
- Password hashing
- Protected endpoints
- Duplicate email detection
- Input validation

**Run specific tests:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test class
pytest tests/test_auth.py::TestUserRegistration -v

# Run specific test
pytest tests/test_auth.py::TestUserRegistration::test_register_success -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

**Coverage report:**
Open `htmlcov/index.html` in your browser to see detailed coverage.

### User Service Tests

Location: `services/user-service/tests/test_users.py`

**What's tested:**
- Get user profile
- Update user profile
- User search
- User list pagination
- Admin operations (activate/deactivate)
- Authorization checks

**Run tests:**
```bash
cd services/user-service
pytest tests/ -v --cov=app
```

## Integration Testing

Integration tests verify that services work together correctly.

### Manual Integration Test

**Test Flow: Register → Login → Update Profile → Search**

1. **Start all services:**
```bash
docker-compose up -d
```

2. **Register a user:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "integration@test.com",
    "password": "TestPassword123",
    "name": "Integration Test"
  }'
```

Save the user ID from response.

3. **Login:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "integration@test.com",
    "password": "TestPassword123"
  }'
```

Save the token from response.

4. **Get profile through gateway:**
```bash
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

5. **Update profile:**
```bash
curl -X PUT http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "bio": "Integration test bio"
  }'
```

6. **Search for user:**
```bash
curl -X POST http://localhost:8080/api/v1/users/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "integration",
    "limit": 10,
    "offset": 0
  }'
```

**Success criteria:** All requests return 200/201 and correct data.

## API Testing with Postman

### 1. Import Collection

1. Open Postman
2. Click "Import"
3. Select `docs/POSTMAN_COLLECTION.json`
4. Collection "Nexus Core API" will be imported

### 2. Set Environment Variables

In Postman, set these collection variables:
- `base_url`: http://localhost:8080
- `auth_token`: (will be set automatically after login)
- `user_id`: (will be set automatically after registration)

### 3. Run Collection

**Manual testing:**
1. Run "Register User" - should return 201
2. Run "Login" - should return 200 and set auth_token
3. Run "Get Current User" - should return user data
4. Run "Update My Profile" - should update profile
5. Run "Search Users" - should find users

**Automated testing:**
1. Click "..." next to collection name
2. Select "Run collection"
3. Click "Run Nexus Core API"
4. All tests should pass ✅

### 4. Test Scripts

The collection includes test scripts that:
- Automatically extract and save tokens
- Verify response codes
- Validate response data
- Chain requests together

## End-to-End Testing

Complete user workflows from registration to usage.

### Scenario 1: New User Onboarding

```bash
# 1. Register
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123","name":"Test User"}'

# 2. Login (save token)
TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123"}' \
  | jq -r '.data.token')

# 3. Get profile
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Update profile
curl -X PUT http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bio":"E2E test user"}'
```

### Scenario 2: Admin User Management

```bash
# 1. Login as admin
ADMIN_TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"AdminPass123"}' \
  | jq -r '.data.token')

# 2. Search for user
USER_ID=$(curl -X POST http://localhost:8080/api/v1/users/search \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"user@test.com"}' \
  | jq -r '.users[0].id')

# 3. Deactivate user
curl -X PUT http://localhost:8080/api/v1/users/$USER_ID/deactivate \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 4. Activate user
curl -X PUT http://localhost:8080/api/v1/users/$USER_ID/activate \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Performance Testing

### Load Testing with k6 (Optional)

Install k6: https://k6.io/docs/getting-started/installation/

Create `load-test.js`:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
};

export default function () {
  let res = http.get('http://localhost:8080/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
```

Run test:
```bash
k6 run load-test.js
```

### Expected Performance

- **Health check**: < 5ms
- **Auth endpoints**: < 100ms
- **User endpoints**: < 150ms
- **Search endpoints**: < 300ms
- **Throughput**: 1000+ req/s per service

## Rate Limit Testing

Test that rate limiting works:

```bash
# Send 70 requests (limit is 60/minute)
for i in {1..70}; do
  curl http://localhost:8080/health -i | grep "429"
done
```

Should see "429 Too Many Requests" after ~60 requests.

## Security Testing

### 1. Test Authentication

```bash
# Should fail without token
curl http://localhost:8080/api/v1/users/me
# Expected: 401 Unauthorized

# Should fail with invalid token
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer invalid-token"
# Expected: 401 Unauthorized

# Should fail with expired token
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer expired-token-here"
# Expected: 401 Unauthorized
```

### 2. Test Authorization

```bash
# Regular user trying admin endpoint (should fail)
curl -X PUT http://localhost:8080/api/v1/users/USER_ID/deactivate \
  -H "Authorization: Bearer REGULAR_USER_TOKEN"
# Expected: 403 Forbidden
```

### 3. Test Input Validation

```bash
# Invalid email
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"not-an-email","password":"Pass123","name":"Test"}'
# Expected: 422 Validation Error

# Short password
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"short","name":"Test"}'
# Expected: 422 Validation Error
```

## Continuous Integration

### GitHub Actions (Example)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: nexuscore
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: nexuscore_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Test Auth Service
        run: |
          cd services/auth-service
          pip install -r requirements.txt
          pytest tests/ -v --cov=app
      
      - name: Test User Service
        run: |
          cd services/user-service
          pip install -r requirements.txt
          pytest tests/ -v --cov=app
```

## Troubleshooting Tests

### Tests fail with "Connection refused"

- Make sure PostgreSQL and Redis are running
- Check `docker-compose ps`
- Verify DATABASE_URL and REDIS_URL in .env

### Tests fail with "ModuleNotFoundError"

- Activate virtual environment
- Run `pip install -r requirements.txt`

### Specific test fails

- Run just that test: `pytest tests/test_auth.py::test_name -v`
- Check test output for detailed error
- Verify test database is clean

### API tests return 500

- Check service logs: `docker-compose logs auth-service`
- Verify all environment variables are set
- Check database connection

## Test Coverage Goals

- **Unit Tests**: > 80% code coverage
- **Integration Tests**: All service interactions
- **API Tests**: All endpoints tested
- **E2E Tests**: Key user workflows
- **Performance**: Meets SLA requirements

## Next Steps

1. Add automated E2E test suite
2. Add load testing to CI/CD
3. Add security scanning
4. Add mutation testing
5. Add contract testing for service APIs

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Postman Learning](https://learning.postman.com/)
- [k6 Documentation](https://k6.io/docs/)

