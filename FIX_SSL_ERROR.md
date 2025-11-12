# Fix SSL Error for api.developer.galion.app

**Error:** ERR_SSL_VERSION_OR_CIPHER_MISMATCH

## Root Cause

Your origin server is missing valid SSL certificates. The nginx configuration points to certificates that don't exist yet.

---

## Solution Options

### Option 1: Cloudflare Origin Certificates (RECOMMENDED - Fast & Easy)

This is the fastest solution when using Cloudflare proxied DNS.

#### Step 1: Get Cloudflare Origin Certificate

1. Log into Cloudflare Dashboard
2. Select your `galion.app` domain
3. Go to **SSL/TLS** → **Origin Server**
4. Click **"Create Certificate"**
5. Configure:
   - **Hostnames:** 
     - `developer.galion.app`
     - `api.developer.galion.app`
     - `*.developer.galion.app` (optional - for wildcards)
   - **Certificate Validity:** 15 years
   - **Private Key Type:** RSA (2048)
6. Click **"Create"**
7. **IMPORTANT:** Copy both the certificate and private key - you won't see them again!

#### Step 2: Set Cloudflare SSL/TLS Mode

1. In Cloudflare Dashboard → **SSL/TLS** → **Overview**
2. Set **SSL/TLS encryption mode** to: **Full (strict)**
3. Enable these settings:
   - **Always Use HTTPS:** ON
   - **Automatic HTTPS Rewrites:** ON
   - **Minimum TLS Version:** TLS 1.2

#### Step 3: Install Certificates on Server

**On Windows (Local Testing):**

```powershell
# Create certificate directory
New-Item -Path "C:\nginx\certs" -ItemType Directory -Force

# Save certificate (paste from Cloudflare)
notepad "C:\nginx\certs\developer.galion.app.pem"

# Save private key (paste from Cloudflare)
notepad "C:\nginx\certs\developer.galion.app.key"
```

**On Linux Server:**

```bash
# SSH into your server
ssh user@your-server-ip

# Create directory
sudo mkdir -p /etc/cloudflare/certs

# Create certificate file
sudo nano /etc/cloudflare/certs/developer.galion.app.pem
# Paste the certificate from Cloudflare, then Ctrl+X, Y, Enter

# Create private key file
sudo nano /etc/cloudflare/certs/developer.galion.app.key
# Paste the private key from Cloudflare, then Ctrl+X, Y, Enter

# Set proper permissions
sudo chmod 600 /etc/cloudflare/certs/developer.galion.app.key
sudo chmod 644 /etc/cloudflare/certs/developer.galion.app.pem
```

#### Step 4: Update Nginx Configuration

The nginx config needs to point to the Cloudflare certificates instead of Let's Encrypt.

I'll update the file for you.

#### Step 5: Test and Restart Nginx

```bash
# Test nginx configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx

# Check nginx status
sudo systemctl status nginx
```

---

### Option 2: Let's Encrypt (More Complex)

If you prefer Let's Encrypt instead:

#### Important: Temporarily Disable Cloudflare Proxy

Let's Encrypt needs direct access to your server:

1. Go to Cloudflare Dashboard → DNS
2. Click on the orange cloud icons for:
   - `developer.galion.app`
   - `api.developer.galion.app`
3. Turn them to **DNS only** (gray cloud)
4. Wait 2-3 minutes for DNS propagation

#### Install Certbot

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d developer.galion.app -d api.developer.galion.app

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommend: Yes)
```

#### Re-enable Cloudflare Proxy

After certbot succeeds:

1. Go back to Cloudflare Dashboard → DNS
2. Re-enable proxy (orange cloud) for both records
3. Change SSL/TLS mode to **Full (strict)**

---

## Quick Fix (If You Just Want to Test Locally)

If you're testing locally and don't need proper SSL yet:

1. **Option A:** Use HTTP only (not recommended for production)
2. **Option B:** Use Cloudflare Tunnel (handles SSL automatically)

### Using Cloudflare Tunnel (No SSL Config Needed)

Cloudflare Tunnel handles SSL for you:

1. Install cloudflared:

```bash
# On Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# On Windows
# Download from: https://github.com/cloudflare/cloudflared/releases
```

2. Authenticate:

```bash
cloudflared tunnel login
```

3. Create tunnel:

```bash
cloudflared tunnel create nexuslang-v2
```

4. Configure tunnel (edit `cloudflare-tunnel.yml`):

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /root/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: developer.galion.app
    service: http://localhost:3000
  - hostname: api.developer.galion.app
    service: http://localhost:8000
  - service: http_status:404
```

5. Run tunnel:

```bash
cloudflared tunnel run nexuslang-v2
```

---

## Troubleshooting

### Test SSL Configuration

```bash
# Test SSL handshake
openssl s_client -connect api.developer.galion.app:443 -servername api.developer.galion.app

# Should show certificate details
# Look for "Verify return code: 0 (ok)"
```

### Check Nginx Logs

```bash
# Check error logs
sudo tail -f /var/log/nginx/error.log

# Check access logs
sudo tail -f /var/log/nginx/developer.galion.app.error.log
```

### Common Issues

**Issue:** Still getting SSL error after installing certificates
- **Fix:** Clear browser cache and cookies, try incognito mode
- **Fix:** Wait 5-10 minutes for Cloudflare cache to clear
- **Fix:** Purge Cloudflare cache in dashboard

**Issue:** Certificate paths wrong in nginx
- **Fix:** Update nginx config to point to correct certificate locations

**Issue:** Permission denied errors
- **Fix:** Ensure nginx user can read certificate files:
  ```bash
  sudo chown root:root /etc/cloudflare/certs/*
  sudo chmod 644 /etc/cloudflare/certs/*.pem
  sudo chmod 600 /etc/cloudflare/certs/*.key
  ```

---

## Recommended Immediate Actions

1. **Get Cloudflare Origin Certificate** (5 minutes)
2. **Update nginx configuration** (2 minutes)
3. **Restart nginx** (1 minute)
4. **Test in browser** (1 minute)

**Total time:** ~10 minutes

---

## Next Step

Tell me which option you prefer:

1. **Cloudflare Origin Certificate** (I'll help you set it up)
2. **Let's Encrypt** (I'll guide you through it)
3. **Cloudflare Tunnel** (No nginx config needed)

Or if you already have the certificates, let me know where they are and I'll update the nginx config!

