# 🚀 QUICK START: Security Setup in 5 Minutes

Too busy to read 600 pages of documentation? Here's the TL;DR.

## ⚡ 5-Minute Security Setup

### Step 1: Generate Secrets (1 minute)

```bash
# Generate JWT secret
openssl rand -hex 64

# Generate database password
openssl rand -base64 32

# Generate Redis password  
openssl rand -base64 32
```

### Step 2: Set Environment Variables (2 minutes)

```bash
# Copy and edit
cp env.template .env

# Set these (REQUIRED):
JWT_SECRET_KEY=<your-64-char-hex-from-step-1>
DATABASE_URL=postgresql://user:<password>@localhost/nexuslang
POSTGRES_PASSWORD=<your-db-password-from-step-1>
REDIS_PASSWORD=<your-redis-password-from-step-1>
```

### Step 3: Run Security Tests (1 minute)

```bash
cd v2/backend
pip install -r requirements.txt
pytest tests/test_security.py -v
```

All tests should pass.

### Step 4: Start Server (30 seconds)

```bash
python main.py
```

### Step 5: Verify Security (30 seconds)

```bash
# Check security headers
curl -I http://localhost:8000/health

# Should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-RateLimit-Limit: 100
```

---

## ✅ You're Secure!

Your basic security is now active:

- ✅ Rate limiting
- ✅ Security headers
- ✅ Sandboxed code execution
- ✅ Audit logging
- ✅ Strong password requirements
- ✅ WebSocket authentication

---

## 🚨 Before Production

1. ✅ Complete `SECURITY_DEPLOYMENT_CHECKLIST.md`
2. ✅ Set up HTTPS
3. ✅ Configure firewall
4. ✅ Set up monitoring

---

## 📚 Full Documentation

- **Audit Report**: `SECURITY_AUDIT_REPORT.md`
- **Deployment Checklist**: `SECURITY_DEPLOYMENT_CHECKLIST.md`
- **Implementation Summary**: `SECURITY_IMPLEMENTATION_SUMMARY.md`

---

**That's it! You're secured with industry best practices. 🔒**

