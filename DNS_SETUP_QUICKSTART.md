# ⚡ DNS Setup - 5 Minute Guide

**Goal**: Point developer.galion.app to your RunPod pod  
**Time**: 5 minutes  
**Required**: Cloudflare account with galion.app domain

---

## 🎯 Quick Steps

### Step 1: Get Your RunPod IP (1 minute)

**SSH into your RunPod pod:**
```bash
curl ifconfig.me
```

Or check RunPod Dashboard → Your Pod → Connection Info

**Example IP**: `123.45.67.89`

### Step 2: Configure DNS in Cloudflare (3 minutes)

1. Open: https://dash.cloudflare.com/
2. Select: **galion.app** domain
3. Go to: **DNS** → **Records**
4. Click: **Add record**

**Record 1: Frontend**
```
Type:    A
Name:    developer.galion.app
Content: YOUR_RUNPOD_IP
Proxy:   ON (🟠 Orange cloud) ← IMPORTANT!
TTL:     Auto
```

Click **Save**

**Record 2: API**
```
Type:    A
Name:    api.developer
Content: YOUR_RUNPOD_IP
Proxy:   ON (🟠 Orange cloud) ← IMPORTANT!
TTL:     Auto
```

Click **Save**

### Step 3: Wait for Propagation (1-5 minutes)

```bash
# Check DNS from your computer
nslookup developer.galion.app
nslookup api.developer.galion.app

# Both should resolve to Cloudflare IPs (not your RunPod IP)
# This is correct! Cloudflare proxy is working.
```

### Step 4: Configure SSL Mode (1 minute)

1. In Cloudflare: **SSL/TLS** → **Overview**
2. Set encryption mode: **Full (strict)**
3. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: TLS 1.2

---

## ✅ Verification

### Test from Your Computer

```bash
# Test HTTPS (should work with Cloudflare Tunnel)
curl -I https://developer.galion.app
# Expected: HTTP/2 200

curl https://api.developer.galion.app/health
# Expected: {"status":"healthy",...}
```

### Test in Browser

1. Open: https://developer.galion.app
2. Check: No SSL warning
3. Click: Padlock icon → Should show "Secure"
4. Try: Register, login, use IDE
5. All work? ✅ **DNS CONFIGURED!**

---

## 🐛 Troubleshooting

### DNS not resolving
- Wait 5 more minutes (propagation)
- Clear DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
- Try incognito browser

### SSL error
- Verify Cloudflare SSL mode is "Full (strict)"
- Check Cloudflare Tunnel is running: `sudo systemctl status cloudflared`
- See: `RUNPOD_SSL_SETUP_GUIDE.md`

### 502 Bad Gateway
- Services not started: `docker-compose ps`
- Start them: `docker-compose up -d`
- Check logs: `docker-compose logs backend`

---

## 🎉 Done!

Once DNS resolves and SSL works:

✅ developer.galion.app → Your NexusLang platform  
✅ api.developer.galion.app → Your API

**Time to launch!** 🚀

