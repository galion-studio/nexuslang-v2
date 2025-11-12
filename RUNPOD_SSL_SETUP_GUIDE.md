# 🔒 RunPod + Cloudflare SSL Setup for developer.galion.app

**Mission**: Get `developer.galion.app` and `api.developer.galion.app` working with SSL on RunPod

**Time**: 15 minutes  
**Difficulty**: Easy

---

## 🎯 What You Need

1. **RunPod Pod** with code deployed
2. **Cloudflare Account** with galion.app domain
3. **10 minutes** of focused time

---

## ⚡ Quick Setup (3 Steps)

### Step 1: Get Cloudflare Origin Certificates (5 minutes)

1. Open: https://dash.cloudflare.com/
2. Select: **galion.app** domain
3. Navigate: **SSL/TLS** → **Origin Server**
4. Click: **"Create Certificate"**
5. Configure:
   ```
   Hostnames:
   - developer.galion.app
   - api.developer.galion.app
   - *.developer.galion.app
   
   Validity: 15 years
   Key Type: RSA (2048)
   ```
6. Click **"Create"**
7. **CRITICAL**: Copy BOTH the certificate and private key (you can't see them again!)

### Step 2: Install Certificates on RunPod (5 minutes)

**SSH into your RunPod pod:**

```bash
# Create certificate directory
sudo mkdir -p /etc/cloudflare/certs

# Create certificate file (paste from Cloudflare)
sudo nano /etc/cloudflare/certs/developer.galion.app.pem
# Paste the CERTIFICATE, then Ctrl+X, Y, Enter

# Create private key file (paste from Cloudflare)
sudo nano /etc/cloudflare/certs/developer.galion.app.key
# Paste the PRIVATE KEY, then Ctrl+X, Y, Enter

# Set permissions (critical for security!)
sudo chmod 600 /etc/cloudflare/certs/developer.galion.app.key
sudo chmod 644 /etc/cloudflare/certs/developer.galion.app.pem
sudo chown root:root /etc/cloudflare/certs/*
```

### Step 3: Configure Cloudflare SSL Settings (2 minutes)

1. In Cloudflare Dashboard: **SSL/TLS** → **Overview**
2. Set **SSL/TLS encryption mode** to: **Full (strict)**
3. Enable:
   - ✅ **Always Use HTTPS**: ON
   - ✅ **Automatic HTTPS Rewrites**: ON
   - ✅ **Minimum TLS Version**: TLS 1.2

---

## 🌐 DNS Configuration

In Cloudflare Dashboard → **DNS**:

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | developer.galion.app | YOUR_RUNPOD_IP | 🟠 Proxied |
| A | api.developer | YOUR_RUNPOD_IP | 🟠 Proxied |

**Important**: Both must be **Proxied** (orange cloud) for Cloudflare SSL to work!

---

## 🔧 RunPod Nginx Configuration

**If using nginx on RunPod**, update the config:

```bash
# Copy nginx config to RunPod
sudo cp /workspace/project-nexus/v2/infrastructure/nginx/developer.galion.app.conf \
     /etc/nginx/sites-available/developer.galion.app

# Edit to uncomment Cloudflare certificate lines
sudo nano /etc/nginx/sites-available/developer.galion.app

# Find and uncomment these lines:
# ssl_certificate /etc/cloudflare/certs/developer.galion.app.pem;
# ssl_certificate_key /etc/cloudflare/certs/developer.galion.app.key;

# Comment out Let's Encrypt lines:
# ssl_certificate /etc/letsencrypt/...
# ssl_certificate_key /etc/letsencrypt/...

# Enable site
sudo ln -s /etc/nginx/sites-available/developer.galion.app \
           /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl restart nginx
```

---

## 🎯 Alternative: Skip Nginx, Use Cloudflare Tunnel

**Easier option**: Use Cloudflare Tunnel (no SSL cert setup needed!)

```bash
# On RunPod pod
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create nexuslang-v2
# Note the tunnel ID shown

# Configure tunnel
nano ~/.cloudflared/config.yml
```

**Add this config:**
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: developer.galion.app
    service: http://localhost:3000
  - hostname: api.developer.galion.app
    service: http://localhost:8000
  - service: http_status:404
```

**Start tunnel:**
```bash
cloudflared tunnel run nexuslang-v2

# Or run as service:
sudo cloudflared service install
sudo systemctl start cloudflared
```

**In Cloudflare DNS**, add:
```
Type: CNAME
Name: developer.galion.app
Content: YOUR_TUNNEL_ID.cfargotunnel.com
Proxy: Yes (🟠)
```

---

## ✅ Verification

### Test SSL Connection

```bash
# Test from your computer
curl -I https://api.developer.galion.app

# Should return: HTTP/2 200 (not SSL error)
```

### Test in Browser

1. Open: https://developer.galion.app
2. Check: No SSL warnings
3. Click lock icon: Should show valid certificate

### Test API

```bash
# Health check
curl https://api.developer.galion.app/health

# Should return: {"status":"healthy",...}
```

---

## 🐛 Troubleshooting

### Issue: "ERR_SSL_VERSION_OR_CIPHER_MISMATCH"

**Fix**: Certificate files not found or incorrect permissions

```bash
# Verify files exist
ls -la /etc/cloudflare/certs/

# Should show:
# -rw-r--r-- developer.galion.app.pem
# -rw------- developer.galion.app.key

# Fix permissions if wrong
sudo chmod 600 /etc/cloudflare/certs/*.key
sudo chmod 644 /etc/cloudflare/certs/*.pem
```

### Issue: "Connection Refused"

**Fix**: Services not running or firewall blocking

```bash
# Check if services running
docker-compose ps

# Check ports
netstat -tlnp | grep -E '3000|8000'

# Test locally first
curl http://localhost:8000/health
```

### Issue: "DNS Not Resolving"

**Fix**: DNS propagation delay (wait 2-5 minutes)

```bash
# Check DNS
nslookup developer.galion.app
dig developer.galion.app

# Should show Cloudflare IPs, not your RunPod IP
```

---

## 🚀 Recommended Approach

**For developer.galion.app on RunPod:**

I recommend **Cloudflare Tunnel** because:
- ✅ No SSL certificates to manage
- ✅ Automatic HTTPS
- ✅ Works from behind NAT
- ✅ No nginx configuration needed
- ✅ Built-in DDoS protection
- ✅ Just works™

**Steps:**
1. Install cloudflared on RunPod
2. Create tunnel
3. Point DNS to tunnel
4. Start services
5. Done!

---

## 📋 Checklist

- [ ] Cloudflare Origin Certificate generated
- [ ] Certificate and key copied
- [ ] Files saved in /etc/cloudflare/certs/
- [ ] Permissions set correctly (600 for key, 644 for cert)
- [ ] Cloudflare SSL mode: "Full (strict)"
- [ ] DNS records created (Proxied)
- [ ] Nginx configured (if using nginx)
- [ ] OR Cloudflare Tunnel configured
- [ ] Services started on RunPod
- [ ] Tested: curl https://api.developer.galion.app/health
- [ ] Tested: Open https://developer.galion.app in browser
- [ ] No SSL errors in browser

---

## ⏱️ Time Breakdown

| Task | Time |
|------|------|
| Get Cloudflare certificate | 3 min |
| Install on RunPod | 4 min |
| Configure Cloudflare settings | 2 min |
| DNS configuration | 2 min |
| Verification | 2 min |
| **Total** | **13 min** |

---

## 💡 Pro Tips

1. **Save certificates locally** as backup
2. **Use Cloudflare Tunnel** for simplicity
3. **Test locally first**: `curl http://localhost:8000/health`
4. **Wait for DNS**: Can take 2-5 minutes to propagate
5. **Clear browser cache** if SSL error persists

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ `https://developer.galion.app` loads with no SSL warning
2. ✅ Browser shows lock icon (secure connection)
3. ✅ API health check returns 200 OK
4. ✅ No CORS errors in browser console
5. ✅ Frontend can make API calls successfully

---

**Next**: Configure environment files and start services!

See: `QUICK_FIX_SSL_ERROR.md` for more troubleshooting.

