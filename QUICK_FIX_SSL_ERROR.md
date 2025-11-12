# 🔥 QUICK FIX: SSL Error on api.developer.galion.app

**Error:** `ERR_SSL_VERSION_OR_CIPHER_MISMATCH`

**Root Cause:** Missing or invalid SSL certificates on your origin server

**Fix Time:** ~10 minutes

---

## 🚀 Fastest Solution: Cloudflare Origin Certificate

### Step 1: Get Certificate from Cloudflare (2 minutes)

1. Go to: https://dash.cloudflare.com/
2. Select: **galion.app** domain
3. Navigate: **SSL/TLS** → **Origin Server**
4. Click: **"Create Certificate"**
5. Add hostnames:
   - `developer.galion.app`
   - `api.developer.galion.app`
   - `*.developer.galion.app`
6. Set validity: **15 years**
7. Click **"Create"**
8. **⚠️ IMPORTANT:** Copy both certificate and private key (you can't see them again!)

### Step 2: Configure Cloudflare SSL Settings (1 minute)

1. Go to: **SSL/TLS** → **Overview**
2. Set encryption mode to: **Full (strict)**
3. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: TLS 1.2

### Step 3: Install Certificates on Server (5 minutes)

**Option A: Using the automated script (recommended)**

```bash
# Upload the script to your server
# Then run:
chmod +x install-cloudflare-certs.sh
sudo ./install-cloudflare-certs.sh
```

**Option B: Manual installation**

```bash
# SSH into your server
ssh user@your-server-ip

# Create directory
sudo mkdir -p /etc/cloudflare/certs

# Create certificate file
sudo nano /etc/cloudflare/certs/developer.galion.app.pem
# Paste the certificate, Ctrl+X, Y, Enter

# Create private key file
sudo nano /etc/cloudflare/certs/developer.galion.app.key
# Paste the private key, Ctrl+X, Y, Enter

# Set permissions
sudo chmod 600 /etc/cloudflare/certs/developer.galion.app.key
sudo chmod 644 /etc/cloudflare/certs/developer.galion.app.pem
```

### Step 4: Update Nginx Configuration (2 minutes)

Edit: `/etc/nginx/sites-available/developer.galion.app`

```bash
sudo nano /etc/nginx/sites-available/developer.galion.app
```

Find these lines and uncomment/update them:

```nginx
# Change from:
ssl_certificate /etc/letsencrypt/live/developer.galion.app/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/developer.galion.app/privkey.pem;

# To:
ssl_certificate /etc/cloudflare/certs/developer.galion.app.pem;
ssl_certificate_key /etc/cloudflare/certs/developer.galion.app.key;
```

Do this for BOTH server blocks (frontend and API)!

### Step 5: Restart Nginx (1 minute)

```bash
# Test configuration
sudo nginx -t

# If test passes, restart
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### Step 6: Test (1 minute)

```bash
# Test SSL connection
curl -I https://api.developer.galion.app

# Should return: HTTP/2 200 or similar (not SSL error)
```

Or open in browser:
- https://developer.galion.app
- https://api.developer.galion.app

---

## ✅ Checklist

- [ ] Got Cloudflare Origin Certificate
- [ ] Set Cloudflare SSL mode to "Full (strict)"
- [ ] Installed certificate files on server
- [ ] Updated nginx configuration
- [ ] Tested nginx config (`sudo nginx -t`)
- [ ] Restarted nginx
- [ ] Verified site works in browser
- [ ] Cleared browser cache if needed

---

## 🐛 Still Not Working?

### Issue: "SSL handshake failed"
**Fix:** Check file permissions
```bash
ls -la /etc/cloudflare/certs/
# Should show: 
# -rw-r--r-- root root developer.galion.app.pem
# -rw------- root root developer.galion.app.key
```

### Issue: "Certificate not trusted"
**Fix:** Ensure Cloudflare SSL mode is "Full (strict)" NOT "Flexible"

### Issue: "Still showing SSL error"
**Fix:** 
1. Clear browser cache (Ctrl+Shift+Delete)
2. Try incognito/private mode
3. Wait 2-3 minutes for changes to propagate
4. Purge Cloudflare cache (in dashboard)

### Issue: Nginx test fails
**Fix:** Check nginx error log
```bash
sudo tail -50 /var/log/nginx/error.log
```

---

## 📚 Need More Help?

- **Full Guide:** See `FIX_SSL_ERROR.md`
- **Nginx Config:** See `v2/infrastructure/nginx/developer.galion.app.conf`
- **Cloudflare Setup:** See `CLOUDFLARE_SETUP_DEVELOPER.md`

---

## 🎯 Summary

The error happens because your server needs SSL certificates. Cloudflare Origin Certificates are the easiest solution when using Cloudflare's proxy (orange cloud). The certificates tell browsers "this connection is secure" while Cloudflare handles the public-facing SSL.

**Key Point:** With Cloudflare proxied DNS:
- Cloudflare ↔ User: Cloudflare's certificates (automatic)
- Your Server ↔ Cloudflare: Origin certificates (you install these)

That's why you need to install the Origin certificates on your server!

---

**Time to fix:** 10 minutes  
**Difficulty:** Easy  
**Cost:** Free

🚀 **You got this!**

