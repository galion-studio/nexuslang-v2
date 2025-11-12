# Three Galion Apps Deployment - Complete Package

## 🎯 What This Does

Deploys three separate applications on a single RunPod instance:

1. **developer.galion.app** - NexusLang v2 IDE, Grokopedia, Voice, Community
2. **galion.app** - Voice-first AI assistant for science
3. **galion.studio** - B2B collaborative workspace platform

## 🚀 Quick Deploy (One Command)

```bash
chmod +x RUNPOD_DEPLOY_MASTER.sh
./RUNPOD_DEPLOY_MASTER.sh
```

This will:
- ✅ Install all dependencies
- ✅ Deploy all 3 apps
- ✅ Start PostgreSQL, Redis, Elasticsearch
- ✅ Test deployment
- ✅ Optionally setup Cloudflare tunnels

**Time:** ~10-15 minutes

---

## 📦 Files Created

### Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.multi-apps.yml` | Multi-app orchestration |
| `env.runpod.multi-apps` | Environment variables template |

### Cloudflare Tunnel Configs

| File | Domain |
|------|--------|
| `cloudflare-tunnel-developer-galion-app.yml` | developer.galion.app |
| `cloudflare-tunnel-galion-app.yml` | galion.app |
| `cloudflare-tunnel-galion-studio.yml` | galion.studio |

### Deployment Scripts

| Script | Purpose |
|--------|---------|
| `RUNPOD_DEPLOY_MASTER.sh` | ⭐ **Main script - run this!** |
| `install-dependencies.sh` | Install Node.js, npm, Python deps |
| `generate-secrets.sh` | Generate secure passwords |
| `deploy-all-apps.sh` | Start all apps and services |
| `setup-cloudflare-tunnels.sh` | Setup public domain access |
| `test-deployment.sh` | Test all deployments |

### Documentation

| File | Content |
|------|---------|
| `README_DEPLOYMENT.md` | This file |
| `DEPLOYMENT_COMPLETE_GUIDE.md` | Detailed deployment guide |
| `UPLOAD_TO_RUNPOD_GUIDE.md` | How to upload code |

---

## 📋 Prerequisites

- [x] RunPod instance (16GB+ RAM, 4+ vCPU)
- [x] Code at `/workspace/nexuslang-v2/`
- [x] OpenRouter API key (already in env)
- [ ] Cloudflare account (optional, for public domains)

---

## 🏗️ Architecture

```
developer.galion.app → Port 3000/8000
galion.app          → Port 3100/8100
galion.studio       → Port 3200/8200

Shared Services:
- PostgreSQL (5432)
- Redis (6379)
- Elasticsearch (9200)
```

---

## 🔧 Manual Deployment (Step by Step)

If you prefer manual control:

### Step 1: Configure Environment

```bash
cp env.runpod.multi-apps .env
./generate-secrets.sh
nano .env  # Add generated secrets
```

### Step 2: Install Dependencies

```bash
chmod +x install-dependencies.sh
./install-dependencies.sh
```

### Step 3: Deploy Apps

```bash
chmod +x deploy-all-apps.sh
./deploy-all-apps.sh
```

### Step 4: Test

```bash
chmod +x test-deployment.sh
./test-deployment.sh
```

### Step 5: Setup Cloudflare (Optional)

```bash
# Get tokens from Cloudflare dashboard first
chmod +x setup-cloudflare-tunnels.sh
./setup-cloudflare-tunnels.sh
```

---

## 🌐 Access URLs

### RunPod Proxy (Always Available)

Replace `POD_ID` with your pod ID (run `hostname` to get it):

- **developer.galion.app**
  - Frontend: `https://POD_ID-3000.proxy.runpod.net`
  - Backend: `https://POD_ID-8000.proxy.runpod.net`

- **galion.app**
  - Frontend: `https://POD_ID-3100.proxy.runpod.net`
  - Backend: `https://POD_ID-8100.proxy.runpod.net`

- **galion.studio**
  - Frontend: `https://POD_ID-3200.proxy.runpod.net`
  - Backend: `https://POD_ID-8200.proxy.runpod.net`

### Public Domains (After Cloudflare Setup)

- https://developer.galion.app
- https://galion.app
- https://galion.studio

---

## 🐛 Troubleshooting

### Quick Fixes

```bash
# View logs
tail -f /tmp/developer-backend.log
tail -f /tmp/galion-app-backend.log

# Restart everything
./deploy-all-apps.sh

# Test status
./test-deployment.sh

# Stop all services
pkill -f uvicorn && pkill -f next && pkill -f cloudflared
```

### Common Issues

**Service won't start:**
```bash
# Check logs
tail -f /tmp/developer-backend.log

# Check port availability
netstat -tulpn | grep 8000
```

**Database connection failed:**
```bash
# Start PostgreSQL
service postgresql start

# Test connection
psql -h localhost -U nexus -d galion_platform -c "SELECT 1;"
```

**Frontend not loading:**
```bash
# Wait for Next.js compilation (30s)
sleep 30

# Check logs
tail -f /tmp/developer-frontend.log
```

---

## 📊 Service Status

Check running services:

```bash
# View all processes
ps aux | grep -E 'uvicorn|next|cloudflared|postgres|redis'

# Check specific ports
netstat -tulpn | grep -E '3000|3100|3200|8000|8100|8200'

# Run full test
./test-deployment.sh
```

---

## 🔐 Security Notes

- All passwords are generated randomly
- OpenRouter API key is already configured
- Cloudflare provides automatic HTTPS
- CORS is configured per domain
- Rate limiting is enabled

---

## 📚 Additional Documentation

For more details, see:

- **DEPLOYMENT_COMPLETE_GUIDE.md** - Full deployment guide with troubleshooting
- **UPLOAD_TO_RUNPOD_GUIDE.md** - How to upload code to RunPod
- **docker-compose.multi-apps.yml** - Service configuration
- **env.runpod.multi-apps** - Environment variables reference

---

## ✅ Success Checklist

After deployment, verify:

- [ ] All scripts executed without errors
- [ ] PostgreSQL running (port 5432)
- [ ] Redis running (port 6379)
- [ ] developer.galion.app accessible
- [ ] galion.app accessible (if code uploaded)
- [ ] galion.studio accessible (if code uploaded)
- [ ] RunPod proxy URLs work
- [ ] Cloudflare tunnels running (if configured)
- [ ] Public domains accessible (if Cloudflare setup)

---

## 🚀 Next Steps

1. **Test all apps** using RunPod proxy URLs
2. **Configure Cloudflare** for public domains
3. **Monitor logs** for errors
4. **Setup backups** for database
5. **Configure monitoring** dashboards
6. **Add SSL certificates** (if not using Cloudflare)
7. **Document API endpoints**
8. **Setup CI/CD** for updates

---

## 💡 Tips

- Use `screen` or `tmux` to keep services running after SSH disconnect
- Set up automatic restarts with `systemd` services
- Monitor resource usage with `htop`
- Setup log rotation for `/tmp/*.log` files
- Backup database regularly with `pg_dump`
- Use Grafana (port 3001) for metrics visualization

---

## 🆘 Support

**Need help?**

1. Run `./test-deployment.sh` to diagnose
2. Check logs in `/tmp/` directory
3. Review `DEPLOYMENT_COMPLETE_GUIDE.md`
4. Verify .env file has all required variables

**Common Commands:**

```bash
# View all logs
ls -la /tmp/*.log

# Check service health
curl http://localhost:8000/health
curl http://localhost:8100/health
curl http://localhost:8200/health

# Restart specific app
pkill -f "uvicorn.*8000" && cd /workspace/nexuslang-v2/v2/backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

**Status:** ✅ All configuration files created and ready for deployment  
**Total Scripts:** 6 deployment scripts + 1 master script  
**Total Configs:** 3 Cloudflare tunnels + 1 Docker Compose + 1 Environment template  
**Documentation:** 3 comprehensive guides

**Ready to deploy!** Run: `./RUNPOD_DEPLOY_MASTER.sh`

