# Complete Deployment Guide for Three Galion Apps on RunPod

## Overview

This deployment sets up three separate applications on a single RunPod instance:

1. **developer.galion.app** (Port 3000/8000) - NexusLang v2 IDE platform
2. **galion.app** (Port 3100/8100) - Voice-first AI assistant
3. **galion.studio** (Port 3200/8200) - B2B collaborative workspace

All apps share PostgreSQL, Redis, and Elasticsearch running on the same instance.

---

## Quick Start (5 Steps)

### Step 1: Configure Environment

```bash
# Copy template
cp env.runpod.multi-apps .env

# Generate secure secrets
./generate-secrets.sh

# Edit .env and add the generated secrets
nano .env
```

### Step 2: Install Dependencies

```bash
chmod +x install-dependencies.sh
./install-dependencies.sh
```

### Step 3: Deploy All Apps

```bash
chmod +x deploy-all-apps.sh
./deploy-all-apps.sh
```

### Step 4: Setup Cloudflare Tunnels (Optional)

```bash
# Get tunnel tokens from Cloudflare dashboard first
# Add them to .env file

chmod +x setup-cloudflare-tunnels.sh
./setup-cloudflare-tunnels.sh
```

### Step 5: Verify Deployment

```bash
chmod +x test-deployment.sh
./test-deployment.sh
```

---

## Detailed Instructions

### Prerequisites

- RunPod instance with 16GB+ RAM, 4+ vCPU
- Code uploaded to `/workspace/nexuslang-v2/`
- Cloudflare account (for public domains)

### Port Assignments

| App | Frontend | Backend | Description |
|-----|----------|---------|-------------|
| developer.galion.app | 3000 | 8000 | NexusLang v2 |
| galion.app | 3100 | 8100 | Voice AI |
| galion.studio | 3200 | 8200 | Collaborative |
| Shared | - | 5432 | PostgreSQL |
| Shared | - | 6379 | Redis |
| Shared | - | 9200 | Elasticsearch |
| Monitoring | 3001 | 9090 | Grafana/Prometheus |

### Access URLs

#### RunPod Proxy URLs (Always Available)

Replace `POD_ID` with your actual pod ID (from `hostname` command):

- Frontend: `https://POD_ID-3000.proxy.runpod.net`
- Backend: `https://POD_ID-8000.proxy.runpod.net`
- Galion App: `https://POD_ID-3100.proxy.runpod.net`
- Galion Studio: `https://POD_ID-3200.proxy.runpod.net`

#### Public URLs (After Cloudflare Setup)

- https://developer.galion.app
- https://galion.app
- https://galion.studio

---

## Configuration Files Created

| File | Purpose |
|------|---------|
| `docker-compose.multi-apps.yml` | Multi-app orchestration |
| `env.runpod.multi-apps` | Environment template |
| `cloudflare-tunnel-developer-galion-app.yml` | Developer tunnel config |
| `cloudflare-tunnel-galion-app.yml` | Galion.app tunnel config |
| `cloudflare-tunnel-galion-studio.yml` | Galion.studio tunnel config |
| `install-dependencies.sh` | Dependency installer |
| `generate-secrets.sh` | Secret generator |
| `deploy-all-apps.sh` | Main deployment script |
| `setup-cloudflare-tunnels.sh` | Tunnel setup script |
| `test-deployment.sh` | Testing script |

---

## Cloudflare Tunnel Setup

### Get Tunnel Tokens

1. Go to https://dash.cloudflare.com
2. Select account → **Zero Trust** → **Access** → **Tunnels**
3. Click **"Create a tunnel"**
4. Name it: `developer-galion-app`
5. Select connector: **Docker**
6. Copy the token
7. Add to `.env`: `CF_TUNNEL_TOKEN_DEVELOPER=your-token`
8. Repeat for `galion-app` and `galion-studio`

### Configure Public Hostnames

In Cloudflare dashboard, for each tunnel, add public hostnames:

**developer-galion-app tunnel:**
- `developer.galion.app` → `http://localhost:3000`
- `api.developer.galion.app` → `http://localhost:8000`

**galion-app tunnel:**
- `galion.app` → `http://localhost:3100`
- `api.galion.app` → `http://localhost:8100`

**galion-studio tunnel:**
- `galion.studio` → `http://localhost:3200`
- `api.galion.studio` → `http://localhost:8200`

---

## Management Commands

### View Logs

```bash
# Backend logs
tail -f /tmp/developer-backend.log
tail -f /tmp/galion-app-backend.log
tail -f /tmp/galion-studio-backend.log

# Frontend logs  
tail -f /tmp/developer-frontend.log
tail -f /tmp/galion-app-frontend.log
tail -f /tmp/galion-studio-frontend.log

# Tunnel logs
tail -f /tmp/cf-tunnel-developer.log
tail -f /tmp/cf-tunnel-app.log
tail -f /tmp/cf-tunnel-studio.log
```

### Stop Services

```bash
# Stop all backends/frontends
pkill -f uvicorn
pkill -f next

# Stop tunnels
pkill -f cloudflared

# Stop databases
service postgresql stop
pkill -f redis-server
```

### Restart Services

```bash
# Restart everything
./deploy-all-apps.sh

# Restart only Cloudflare tunnels
./setup-cloudflare-tunnels.sh
```

### Check Status

```bash
# Run full test
./test-deployment.sh

# Check processes
ps aux | grep uvicorn
ps aux | grep next
ps aux | grep cloudflared

# Check ports
netstat -tulpn | grep -E '3000|3100|3200|8000|8100|8200'
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
tail -f /tmp/developer-backend.log

# Check if port is in use
lsof -i :8000

# Kill and restart
pkill -f uvicorn
./deploy-all-apps.sh
```

### Database Connection Failed

```bash
# Check PostgreSQL
service postgresql status
service postgresql start

# Test connection
psql -h localhost -U nexus -d galion_platform -c "SELECT 1;"
```

### Frontend Not Loading

```bash
# Wait 30 seconds for Next.js to compile
sleep 30

# Check if Node.js is running
ps aux | grep next

# Check logs
tail -f /tmp/developer-frontend.log
```

### Cloudflare Tunnel Not Working

```bash
# Check tunnel status
ps aux | grep cloudflared

# Check logs
tail -f /tmp/cf-tunnel-developer.log

# Verify token in .env
grep CF_TUNNEL_TOKEN .env

# Restart tunnel
pkill -f cloudflared
./setup-cloudflare-tunnels.sh
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    RunPod Instance                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ PostgreSQL   │  │    Redis     │  │Elasticsea-││
│  │  (5432)      │  │   (6379)     │  │rch (9200) ││
│  └──────────────┘  └──────────────┘  └───────────┘ │
│         │                  │                │       │
│  ───────┴──────────────────┴────────────────┴────  │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ developer.galion.app (NexusLang v2)         │   │
│  │  Frontend: 3000 │ Backend: 8000             │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ galion.app (Voice AI)                       │   │
│  │  Frontend: 3100 │ Backend: 8100             │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ galion.studio (Collaborative)               │   │
│  │  Frontend: 3200 │ Backend: 8200             │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ Cloudflare Tunnels (3 instances)            │   │
│  │  developer.galion.app → Port 3000/8000      │   │
│  │  galion.app → Port 3100/8100                │   │
│  │  galion.studio → Port 3200/8200             │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │ Cloudflare Network    │
             │  ├─ developer.galion.app
             │  ├─ galion.app
             │  └─ galion.studio
             └───────────────────────┘
```

---

## Success Checklist

- [ ] Environment configured (`.env` file created)
- [ ] Secrets generated and added
- [ ] Dependencies installed
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] developer.galion.app backend running (port 8000)
- [ ] developer.galion.app frontend running (port 3000)
- [ ] galion.app backend running (port 8100)
- [ ] galion.app frontend running (port 3100)
- [ ] galion.studio backend running (port 8200)
- [ ] galion.studio frontend running (port 3200)
- [ ] Cloudflare tunnels configured
- [ ] Cloudflare tunnels running
- [ ] Public URLs accessible

---

## Next Steps

1. **Test all apps locally** using RunPod proxy URLs
2. **Configure Cloudflare** for public domain access
3. **Monitor logs** for any errors
4. **Setup SSL certificates** if not using Cloudflare
5. **Configure backups** for database
6. **Setup monitoring** with Grafana
7. **Add custom domains** in Cloudflare
8. **Configure rate limiting** if needed
9. **Setup CI/CD** for automated deployments
10. **Document API endpoints** for each app

---

## Support

For issues or questions:
- Check logs in `/tmp/` directory
- Run `./test-deployment.sh` to diagnose issues
- Review `docker-compose.multi-apps.yml` for service configuration
- Check Cloudflare tunnel status in dashboard

---

**Deployment Date:** $(date)  
**Pod ID:** $(hostname)  
**Status:** All configuration files created and ready for deployment

