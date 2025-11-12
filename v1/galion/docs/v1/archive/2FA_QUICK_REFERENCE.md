# 2FA Quick Reference Card

## 🚀 Deploy (One Command)
```powershell
.\deploy-2fa.ps1
```

## 🧪 Test (One Command)
```powershell
.\test-2fa.ps1
```

## 📡 API Endpoints

### Setup & Management
```bash
# Get QR code and backup codes
POST /api/v1/2fa/setup
Authorization: Bearer {token}

# Verify and enable
POST /api/v1/2fa/verify
{"code": "123456"}

# Check status
GET /api/v1/2fa/status

# Disable
POST /api/v1/2fa/disable
{"password": "...", "code": "123456"}

# Regenerate backup codes
POST /api/v1/2fa/backup-codes/regenerate
```

### Login Flow
```bash
# Step 1: Login with password
POST /api/v1/auth/login
{"email": "...", "password": "..."}
# Response: {"requires_2fa": true, "user_id": "..."}

# Step 2: Complete with 2FA
POST /api/v1/auth/login/2fa?user_id={id}&code={code}
# Response: {"token": "..."}
```

## 🔑 cURL Examples

### Setup 2FA
```bash
TOKEN="your_jwt_token"

curl -X POST http://localhost:8001/api/v1/2fa/setup \
  -H "Authorization: Bearer $TOKEN"
```

### Verify 2FA
```bash
curl -X POST http://localhost:8001/api/v1/2fa/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
```

### Login with 2FA
```bash
# Step 1
RESPONSE=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}')

USER_ID=$(echo $RESPONSE | jq -r '.data.user_id')

# Step 2
curl -X POST "http://localhost:8001/api/v1/auth/login/2fa?user_id=$USER_ID&code=123456"
```

## 🐍 Python Example

```python
import requests
import pyotp

BASE_URL = "http://localhost:8001"

# Login
r = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                  json={"email": "user@example.com", "password": "pass"})
token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# Setup 2FA
r = requests.post(f"{BASE_URL}/api/v1/2fa/setup", headers=headers)
secret = r.json()["data"]["secret"]
backup_codes = r.json()["data"]["backup_codes"]

# Generate TOTP code
totp = pyotp.TOTP(secret)
code = totp.now()

# Verify
r = requests.post(f"{BASE_URL}/api/v1/2fa/verify", 
                  headers=headers, 
                  json={"code": code})

# Login with 2FA
r = requests.post(f"{BASE_URL}/api/v1/auth/login",
                  json={"email": "user@example.com", "password": "pass"})
user_id = r.json()["data"]["user_id"]

code = totp.now()
r = requests.post(f"{BASE_URL}/api/v1/auth/login/2fa",
                  params={"user_id": user_id, "code": code})
token = r.json()["data"]["token"]
```

## 📱 Generate TOTP Code

### Python
```python
import pyotp
totp = pyotp.TOTP('YOUR_SECRET')
print(totp.now())  # Current 6-digit code
```

### JavaScript
```javascript
const speakeasy = require('speakeasy');
const code = speakeasy.totp({
  secret: 'YOUR_SECRET',
  encoding: 'base32'
});
```

### Command Line
```bash
python -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET').now())"
```

## 🗄️ Database Schema

```sql
-- Added to users table
totp_enabled BOOLEAN DEFAULT false
totp_secret VARCHAR(32)
totp_verified_at TIMESTAMP
backup_codes JSONB DEFAULT '[]'
backup_codes_generated_at TIMESTAMP
```

## 🔐 Security Notes

- ✅ Backup codes stored HASHED (PBKDF2-SHA256)
- ✅ TOTP secrets in base32 (required for verification)
- ✅ 30-second time window with ±30s tolerance
- ✅ Single-use backup codes
- ✅ Password required to disable 2FA

## 🐛 Troubleshooting

### "Invalid verification code"
- Check device time sync
- Try previous/next code
- Use backup code
- Regenerate if needed

### "2FA already enabled"
- Disable first: `POST /api/v1/2fa/disable`
- Or use different test account

### Database error
- Apply migration: `.\deploy-2fa.ps1`
- Or manually: `docker exec nexus-postgres psql -U postgres -d nexus_db -f /docker-entrypoint-initdb.d/migrations/004_add_2fa_support.sql`

## 📊 Response Examples

### Setup Response
```json
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,...",
    "backup_codes": [
      "1A2B-3C4D",
      "5E6F-7G8H",
      ...
    ]
  }
}
```

### Login Response (2FA Required)
```json
{
  "success": true,
  "data": {
    "requires_2fa": true,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Please provide your 2FA code"
  }
}
```

### Status Response
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "verified_at": "2024-01-15T10:30:00Z",
    "backup_codes_count": 8
  }
}
```

## 🎯 Key Files

```
services/auth-service/
├── app/
│   ├── api/v1/twofa.py          # 2FA endpoints
│   ├── services/twofa.py        # TOTP/backup code logic
│   └── schemas/twofa.py         # API schemas
├── 2FA_IMPLEMENTATION.md        # Full documentation
└── requirements.txt             # pyotp, qrcode, Pillow

database/migrations/
└── 004_add_2fa_support.sql     # Database schema

Root:
├── test-2fa.ps1                # Test script
├── deploy-2fa.ps1              # Deploy script
└── 2FA_BUILD_COMPLETE.md       # Build summary
```

## 🌐 Supported Apps

- Google Authenticator
- Microsoft Authenticator
- Authy
- 1Password
- LastPass Authenticator
- Any RFC 6238 TOTP app

## ⚡ Quick Commands

```powershell
# Deploy
.\deploy-2fa.ps1

# Test
.\test-2fa.ps1

# Check health
curl http://localhost:8001/health

# API docs
start http://localhost:8001/docs

# View logs
docker logs nexus-auth-service -f

# Restart
docker-compose restart auth-service
```

---

**Ready to ship!** 🚀

