# Cloudflare DNS Setup for NexusLang v2

**Connect nexuslang.galion.app to your RunPod deployment**

---

## 🎯 Overview

Your RunPod deployment is running on:
- **Frontend:** Port 3100
- **Backend:** Port 8100

RunPod provides proxy URLs like:
- `https://abc123xyz-3100.proxy.runpod.net` (frontend)
- `https://abc123xyz-8100.proxy.runpod.net` (backend)

We'll map these to:
- `https://nexuslang.galion.app` (frontend)
- `https://api.nexuslang.galion.app` (backend)

---

## 📋 Step-by-Step Instructions

### Step 1: Get Your RunPod URLs

**In RunPod Dashboard:**
1. Go to your pod
2. Click on the pod name
3. Find "TCP Port Mappings" section
4. Look for:
   - Port **3100** → Copy the external URL
   - Port **8100** → Copy the external URL

**Example:**
```
Port 3100: https://abc123xyz456-3100.proxy.runpod.net
Port 8100: https://abc123xyz456-8100.proxy.runpod.net
```

**Write these down!** ✍️

---

### Step 2: Add DNS Records in Cloudflare

**Login to Cloudflare:**
1. Go to https://dash.cloudflare.com
2. Select `galion.app` domain
3. Click "DNS" in the left sidebar

**Add Record 1 (Frontend):**
```
┌─────────────────────────────────────────────────────────┐
│ Type:    CNAME                                          │
│ Name:    nexuslang                                      │
│ Target:  abc123xyz456-3100.proxy.runpod.net            │ ← Your actual RunPod URL
│ Proxy:   🟠 Proxied (orange cloud ON)                  │
│ TTL:     Auto                                           │
└─────────────────────────────────────────────────────────┘
```

Click "Save"

**Add Record 2 (Backend API):**
```
┌─────────────────────────────────────────────────────────┐
│ Type:    CNAME                                          │
│ Name:    api.nexuslang                                  │
│ Target:  abc123xyz456-8100.proxy.runpod.net            │ ← Your actual RunPod URL
│ Proxy:   🟠 Proxied (orange cloud ON)                  │
│ TTL:     Auto                                           │
└─────────────────────────────────────────────────────────┘
```

Click "Save"

**Important:** Make sure the orange cloud (Proxied) is ON for both records!

---

### Step 3: Wait for DNS Propagation

**Usually takes:** 1-5 minutes (sometimes up to 1 hour)

**Check propagation:**
```bash
# Check if DNS is resolving
nslookup nexuslang.galion.app

# Or use online tool:
# https://dnschecker.org/#CNAME/nexuslang.galion.app
```

---

### Step 4: Update Environment Variables

**On your RunPod server:**

```bash
cd /workspace/project-nexus/v2

# Update frontend env to use custom domain
docker-compose -f docker-compose.nexuslang.yml down

# Edit environment (or set in docker-compose)
export NEXT_PUBLIC_API_URL=https://api.nexuslang.galion.app
export NEXT_PUBLIC_WS_URL=wss://api.nexuslang.galion.app

# Restart with new env
docker-compose -f docker-compose.nexuslang.yml up -d
```

**Or edit `docker-compose.nexuslang.yml` directly:**
```yaml
environment:
  NEXT_PUBLIC_API_URL: https://api.nexuslang.galion.app
  NEXT_PUBLIC_WS_URL: wss://api.nexuslang.galion.app
```

---

### Step 5: Update Backend CORS

**Edit `v2/backend/core/config.py` or `.env`:**

Add your custom domains to CORS_ORIGINS:
```python
CORS_ORIGINS: List[str] = [
    "https://nexuslang.galion.app",
    "https://api.nexuslang.galion.app",
    "https://*.proxy.runpod.net"
]
```

**Restart backend:**
```bash
cd v2
docker-compose -f docker-compose.nexuslang.yml restart nexuslang-backend
```

---

### Step 6: Configure Cloudflare SSL

**In Cloudflare Dashboard → SSL/TLS:**

1. **Encryption Mode:** Select "Full (strict)"
2. **Always Use HTTPS:** Turn ON
3. **Automatic HTTPS Rewrites:** Turn ON
4. **Minimum TLS Version:** TLS 1.2

**Why:** Ensures secure connection between Cloudflare and RunPod

---

### Step 7: Test Custom Domains

**Open in browser:**
```
https://nexuslang.galion.app/ide
```

**Should see:**
- ✅ NexusLang IDE loads
- ✅ No SSL warnings
- ✅ Can register/login
- ✅ Can run code
- ✅ API calls work

**Test API directly:**
```bash
curl https://api.nexuslang.galion.app/health

# Should return:
# {"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}
```

---

## 🎯 Final Verification Checklist

### URLs Working:
- [ ] https://nexuslang.galion.app (frontend)
- [ ] https://api.nexuslang.galion.app/health (backend)
- [ ] https://api.nexuslang.galion.app/docs (API docs)

### Galion Unaffected:
- [ ] https://galion.app still works (or http://localhost:3000)
- [ ] Galion API still works (port 8000)
- [ ] No performance degradation

### Features Working:
- [ ] Can register new user
- [ ] Can login
- [ ] Can create project
- [ ] Can write and run code
- [ ] Can save files
- [ ] Personality editor works
- [ ] Binary compilation works
- [ ] Examples load correctly

---

## 📊 Port Summary

```
╔═══════════════════════════════════════════════════════╗
║  PORT ALLOCATION SUMMARY                              ║
╠═══════════════════════════════════════════════════════╣
║  Galion.app (existing):                               ║
║    • Frontend:     3000  ✅ KEEP                      ║
║    • Backend:      8000  ✅ KEEP                      ║
║    • PostgreSQL:   5432  ✅ SHARED                    ║
║    • Redis:        6379  ✅ SHARED                    ║
║    • Grafana:      3001  ✅ KEEP                      ║
║    • Prometheus:   9090  ✅ KEEP                      ║
╠═══════════════════════════════════════════════════════╣
║  NexusLang v2 (new):                                  ║
║    • Frontend:     3100  ✨ NEW                       ║
║    • Backend:      8100  ✨ NEW                       ║
║    • PostgreSQL:   5432  ✨ SHARED (separate DB)     ║
║    • Redis:        6379  ✨ SHARED (DB 1)            ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🔧 Useful Commands

```bash
# View NexusLang logs
cd v2
docker-compose -f docker-compose.nexuslang.yml logs -f

# Restart NexusLang
docker-compose -f docker-compose.nexuslang.yml restart

# Stop NexusLang (keeps Galion running)
docker-compose -f docker-compose.nexuslang.yml down

# Start NexusLang again
docker-compose -f docker-compose.nexuslang.yml up -d

# Check health
curl http://localhost:8100/health
curl http://localhost:3100
```

---

## 🎉 Success!

When all tests pass:
- ✅ Galion continues running normally
- ✅ NexusLang runs on ports 3100/8100
- ✅ Both share infrastructure efficiently
- ✅ Accessible via custom domains
- ✅ Ready for users!

---

**🚀 Share your deployment:**

```
NexusLang v2 Alpha is live!
https://nexuslang.galion.app/ide

Try the AI-native language with:
⚡ Binary compilation
🧠 Personality system
📚 Knowledge integration
```

---

**Need help?** See `v2/TROUBLESHOOTING.md` or check logs!

