# 🎮 RunPod Ports Setup for NexusLang v2

**Exact port configuration for RunPod deployment**

---

## 🎯 PORTS YOU NEED TO EXPOSE IN RUNPOD

When creating your RunPod pod, expose these ports:

### Essential Ports (Required):

```
┌────────────────────────────────────────────┐
│ Container Port: 3000                       │
│ External Port:  3000                       │
│ Type:           HTTP                       │
│ Purpose:        Frontend (Next.js)         │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Container Port: 8000                       │
│ External Port:  8000                       │
│ Type:           HTTP                       │
│ Purpose:        Backend API (FastAPI)      │
└────────────────────────────────────────────┘
```

### Optional Ports (For Monitoring):

```
┌────────────────────────────────────────────┐
│ Container Port: 9090                       │
│ External Port:  9090                       │
│ Type:           HTTP                       │
│ Purpose:        Prometheus (Metrics)       │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Container Port: 3001                       │
│ External Port:  3001                       │
│ Type:           HTTP                       │
│ Purpose:        Grafana (Dashboards)       │
└────────────────────────────────────────────┘
```

---

## 📝 HOW TO ADD PORTS IN RUNPOD

### Step 1: Creating New Pod

1. Go to: https://www.runpod.io/console/pods
2. Click **"+ Deploy"** or **"New Pod"**
3. Scroll down to **"Expose HTTP Ports"** or **"Port Configuration"**

### Step 2: Add Ports

In the ports section, add:

**Click "+ Add Port" and enter:**

```
Port 1:
━━━━━━━━━━━━━━━━━━━━━
HTTP Port: 3000
━━━━━━━━━━━━━━━━━━━━━
```

**Click "+ Add Port" again:**

```
Port 2:
━━━━━━━━━━━━━━━━━━━━━
HTTP Port: 8000
━━━━━━━━━━━━━━━━━━━━━
```

**Optional - Add monitoring ports:**

```
Port 3 (optional):
━━━━━━━━━━━━━━━━━━━━━
HTTP Port: 9090
━━━━━━━━━━━━━━━━━━━━━

Port 4 (optional):
━━━━━━━━━━━━━━━━━━━━━
HTTP Port: 3001
━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Note Your URLs

After pod starts, RunPod will show you URLs like:

```
Frontend (Port 3000):
https://abc123xyz456-3000.proxy.runpod.net

Backend (Port 8000):
https://abc123xyz456-8000.proxy.runpod.net

Prometheus (Port 9090):
https://abc123xyz456-9090.proxy.runpod.net

Grafana (Port 3001):
https://abc123xyz456-3001.proxy.runpod.net
```

**Write these down!** You'll need them for DNS configuration.

---

## 🌐 CONNECT TO developer.galion.app

### In Cloudflare DNS (galion.app):

**Add these CNAME records:**

```
Record 1:
┌──────────────────────────────────────────────────┐
│ Type:    CNAME                                   │
│ Name:    developer                               │
│ Target:  abc123xyz456-3000.proxy.runpod.net      │ ← Your RunPod frontend URL
│ Proxy:   🟠 Proxied (orange cloud ON)           │
│ TTL:     Auto                                    │
└──────────────────────────────────────────────────┘

Record 2:
┌──────────────────────────────────────────────────┐
│ Type:    CNAME                                   │
│ Name:    api.developer                           │
│ Target:  abc123xyz456-8000.proxy.runpod.net      │ ← Your RunPod backend URL
│ Proxy:   🟠 Proxied (orange cloud ON)           │
│ TTL:     Auto                                    │
└──────────────────────────────────────────────────┘
```

**Important:** Use your actual RunPod URLs (replace abc123xyz456 with your pod ID)

---

## 🚀 COMPLETE RUNPOD DEPLOYMENT

### One-Command Deploy on RunPod:

**In RunPod terminal:**

```bash
cd /workspace && \
git clone https://github.com/galion-studio/galion-platform.git nexuslang-v2 && \
cd nexuslang-v2 && \
apt update && apt install docker-compose -y && \
cp .env.example .env && \
docker-compose -f docker-compose.runpod.yml up -d && \
sleep 120 && \
docker-compose exec -T postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql && \
cd v2/nexuslang && pip install -e . && cd ../.. && \
echo "✅ NexusLang v2 deployed on RunPod!"
```

---

## 📊 RUNPOD URL STRUCTURE

```
Your RunPod Pod ID: abc123xyz456

Generated URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend:  https://abc123xyz456-3000.proxy.runpod.net
Backend:   https://abc123xyz456-8000.proxy.runpod.net
Monitor:   https://abc123xyz456-9090.proxy.runpod.net
Dashboards: https://abc123xyz456-3001.proxy.runpod.net

Connect to developer.galion.app:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
developer.galion.app     → (CNAME) abc123xyz456-3000.proxy.runpod.net
api.developer.galion.app → (CNAME) abc123xyz456-8000.proxy.runpod.net
```

---

## ⚙️ ENVIRONMENT CONFIGURATION FOR RUNPOD

Edit `.env` on RunPod with your RunPod URLs:

```env
# RunPod Configuration
RUNPOD_POD_ID=abc123xyz456

# API URLs (use your actual RunPod URLs)
NEXT_PUBLIC_API_URL=https://abc123xyz456-8000.proxy.runpod.net
NEXT_PUBLIC_WS_URL=wss://abc123xyz456-8000.proxy.runpod.net

# Or use custom domain after Cloudflare setup
# NEXT_PUBLIC_API_URL=https://api.developer.galion.app
# NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app

# CORS
CORS_ORIGINS=https://abc123xyz456-3000.proxy.runpod.net,https://abc123xyz456-8000.proxy.runpod.net,https://developer.galion.app,https://api.developer.galion.app

# Database (internal)
POSTGRES_PASSWORD=secure_password_here
REDIS_PASSWORD=another_secure_password

# API Keys
OPENAI_API_KEY=sk-your-key
SHOPIFY_API_KEY=your-key
SHOPIFY_API_SECRET=your-secret

# Security
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
```

---

## ✅ RUNPOD CHECKLIST

**Before deployment:**
- [ ] RunPod account created
- [ ] Pod created with Ubuntu 22.04
- [ ] Ports exposed: **3000, 8000**
- [ ] Got RunPod URLs (pod-id-3000.proxy.runpod.net)

**During deployment:**
- [ ] Cloned from GitHub
- [ ] Configured .env with RunPod URLs
- [ ] Started docker-compose services
- [ ] Initialized database

**After deployment:**
- [ ] Tested RunPod URLs work
- [ ] Added CNAME records in Cloudflare
- [ ] Tested custom domain (developer.galion.app)
- [ ] Platform accessible! ✅

---

## 🎯 QUICK SUMMARY

**Ports to expose in RunPod:**
- ✅ **3000** (Frontend)
- ✅ **8000** (Backend API)
- 📊 **9090** (Prometheus - optional)
- 📊 **3001** (Grafana - optional)

**What you get:**
- `https://pod-id-3000.proxy.runpod.net` → Your frontend
- `https://pod-id-8000.proxy.runpod.net` → Your API

**Connect to developer.galion.app:**
- Add CNAME in Cloudflare
- Point to RunPod URLs
- Done!

---

**Ready to deploy on RunPod!** 🎮

**See RUNPOD_DEPLOYMENT.md for complete guide!**

