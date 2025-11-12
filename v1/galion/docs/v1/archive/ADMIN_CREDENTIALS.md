# 🔐 ADMIN ACCOUNT CREDENTIALS

## Admin Login Information

### ✅ **ADMIN ACCOUNT DETAILS**

```
📧 Email:    admin@galion.app
🔑 Password: Admin123!
👤 Role:     admin
📛 Name:     Admin User
```

---

## How to Login

### 🌐 Web Application
1. Navigate to: **http://localhost:3000/login**
2. Enter email: `admin@galion.app`
3. Enter password: `Admin123!`
4. Click "Sign in"

### 🔗 API Direct Access
**Login Endpoint:** `POST http://localhost:8100/api/v1/auth/login`

```json
{
  "email": "admin@galion.app",
  "password": "Admin123!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "user": {
      "id": "0e42b9cd-c657-438d-b740-79b8ea8afe7f",
      "email": "admin@galion.app",
      "name": "Admin User",
      "role": "admin",
      "status": "active"
    }
  }
}
```

---

## Account Details

| Field | Value |
|-------|-------|
| **User ID** | `0e42b9cd-c657-438d-b740-79b8ea8afe7f` |
| **Email** | `admin@galion.app` |
| **Password** | `Admin123!` |
| **Name** | Admin User |
| **Role** | **admin** (full access) |
| **Status** | active |
| **Email Verified** | false |
| **Age Verified** | true |
| **Badge** | Explorer |
| **Subscription** | free |
| **Created** | 2025-11-09 20:36:38 UTC |

---

## Test the QR Code Login

1. **Open the login page:**
   ```
   http://localhost:3000/login
   ```

2. **Click "QR Code Login" button**
   - A beautiful dark modal will appear
   - Real QR code will be displayed
   - System polls for authentication every 2 seconds

3. **Test the QR endpoints:**
   ```powershell
   # Create QR session
   Invoke-RestMethod -Uri "http://localhost:8100/api/v1/auth/qr/create" -Method POST
   
   # Check session status
   Invoke-RestMethod -Uri "http://localhost:8100/api/v1/auth/qr/status/{session_id}" -Method GET
   ```

---

## PowerShell Quick Login Test

```powershell
# Test admin login
$body = @{
    email = "admin@galion.app"
    password = "Admin123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8100/api/v1/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host "✅ Logged in as: $($response.data.user.name)"
Write-Host "🔑 Role: $($response.data.user.role)"
Write-Host "🎫 Token: $($response.data.token.Substring(0,50))..."
```

---

## cURL Quick Login Test

```bash
# Test admin login (bash/Linux)
curl -X POST http://localhost:8100/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@galion.app","password":"Admin123!"}'
```

---

## Additional Test Accounts

### Regular User Account
```
📧 Email:    user@galion.app  
🔑 Password: User123!
👤 Role:     user
```

To create additional users:
```powershell
$newUser = @{
    email = "user@galion.app"
    password = "User123!"
    name = "Test User"
    date_of_birth = "1995-01-01"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/api/v1/auth/register" `
    -Method POST `
    -Body $newUser `
    -ContentType "application/json"
```

---

## Service URLs

| Service | URL | Auth Required |
|---------|-----|---------------|
| **Frontend (Login)** | http://localhost:3000/login | No |
| **Frontend (Dashboard)** | http://localhost:3000/dashboard | Yes |
| **API Gateway** | http://localhost:8080 | Varies |
| **Auth Service** | http://localhost:8100 | No (for login/register) |
| **Auth API Docs** | http://localhost:8100/docs | No |
| **User Service** | http://localhost:8101 | Yes |
| **Grafana** | http://localhost:9300 | Yes (admin/admin) |
| **Kafka UI** | http://localhost:9303 | No |
| **Prometheus** | http://localhost:9301 | No |

---

## Security Notes

⚠️ **IMPORTANT:** These are development credentials only!

- Change the admin password in production
- Use strong passwords (16+ characters)
- Enable 2FA for admin accounts
- Never commit credentials to git
- Rotate passwords regularly
- Monitor admin account activity

### Change Password
```powershell
# Update password in database
docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -c "
  UPDATE public.users 
  SET password_hash = crypt('NewSecurePassword123!', gen_salt('bf', 12))
  WHERE email = 'admin@galion.app';
"
```

---

## Troubleshooting

### Can't Login?
1. **Check service status:**
   ```powershell
   docker-compose ps
   ```

2. **Check auth service logs:**
   ```powershell
   docker logs nexus-auth-service --tail 50
   ```

3. **Verify account exists:**
   ```powershell
   docker exec nexus-postgres psql -U nexuscore -d nexuscore -c "SELECT email, role, status FROM public.users WHERE email = 'admin@galion.app';"
   ```

### Reset Admin Password
```powershell
docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -c "
  UPDATE public.users 
  SET password_hash = crypt('Admin123!', gen_salt('bf', 12))
  WHERE email = 'admin@galion.app';
"
```

---

## Database Connection

If you need direct database access:

```powershell
# Connect to PostgreSQL
docker exec -it nexus-postgres psql -U nexuscore -d nexuscore

# View all users
SELECT id, email, name, role, status, created_at FROM public.users;

# View admin users only
SELECT * FROM public.users WHERE role = 'admin';
```

**Database Credentials:**
```
Host:     localhost
Port:     5432
Database: nexuscore
User:     nexuscore
Password: EtRhSmDVMbRheJWpSWRhAVqcMukhTnRP
```

---

## Features Available to Admin

As an **admin** user, you have access to:

✅ All user management features  
✅ Analytics and metrics  
✅ Document verification  
✅ Permission management  
✅ Voice service controls  
✅ System settings  
✅ User administration  
✅ Subscription management  
✅ QR code login (new!)  

---

## Quick Access Links

- **Login Page:** http://localhost:3000/login
- **Dashboard:** http://localhost:3000/dashboard
- **User Management:** http://localhost:3000/users
- **Settings:** http://localhost:3000/settings
- **Analytics:** http://localhost:3000/analytics
- **API Documentation:** http://localhost:8100/docs

---

**Created:** November 9, 2025  
**Status:** ✅ Active  
**Environment:** Development  
**Version:** 1.0.0

🎉 **Your admin account is ready to use!**

