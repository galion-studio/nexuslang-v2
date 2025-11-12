# 🚀 NexusLang v2 - RunPod Quick Deploy Guide

**Deploy your AI-powered platform in under 3 minutes!**

---

## ⚡ Super Quick Start (Copy-Paste These Commands)

### On Your RunPod Terminal:

```bash
# 1. Navigate to workspace
cd /workspace/nexuslang-v2/v2/backend

# 2. Add your OpenRouter API key to .env
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://nexus:9k3mNp8rT2xQv5jL6wYz4cB1nF7dK0sA@localhost:5432/nexus_v2
REDIS_URL=redis://:7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s@localhost:6379/0
JWT_SECRET=2xR7kP9mL4vN8qT3wH6yJ1zB5cF0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG
SECRET_KEY=4jL9mK2pX7vN1qR8wT3yH6zB5cF0sD4gA
OPENROUTER_API_KEY=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
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
CORS_ORIGINS=["*"]
EOF

# 3. Run the recovery script (does everything!)
python recovery.py
```

**That's it!** Your API is now live!

---

## 🌐 Access Your Deployed API

After deployment completes, access your API at:

**RunPod URL**:
- Docs: `https://YOUR-POD-ID-8000.proxy.runpod.net/docs`
- Health: `https://YOUR-POD-ID-8000.proxy.runpod.net/health`
- API: `https://YOUR-POD-ID-8000.proxy.runpod.net`

**Custom Domain** (if configured):
- API: `https://api.developer.galion.app`

---

## 🔧 What The Recovery Script Does

When you run `python recovery.py`, it automatically:

1. ✅ Installs PostgreSQL 16 with pgvector extension
2. ✅ Installs and starts Redis
3. ✅ Creates database and user
4. ✅ Installs all Python packages (with caching)
5. ✅ Fixes all import issues
6. ✅ Restores latest database backup (if available)
7. ✅ Runs database migrations
8. ✅ Starts the backend server
9. ✅ Runs comprehensive health checks
10. ✅ Displays access URLs

**Total Time**: Under 2 minutes!

---

## 📦 Persistent Data (No More Data Loss!)

### Configure Volumes Once:

```bash
cd /workspace/nexuslang-v2
bash configure_volumes.sh
```

This ensures:
- ✅ PostgreSQL data persists across pod restarts
- ✅ Redis data persists
- ✅ Logs persist
- ✅ Backups persist
- ✅ Pip cache persists (faster reinstalls)

After this, **pod restarts won't lose your data!**

---

## 📊 Access Analytics Dashboard

After logging in:

```bash
# Get JWT token from login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Access analytics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v2/analytics/dashboard
```

**Analytics Features**:
- Daily/Monthly Active Users (DAU/MAU)
- API request rates and response times
- AI usage by model
- Token consumption and costs
- Error rates and types
- Feature usage statistics
- Real-time metrics

---

## 🗄️ Database Backups

### Automatic Backups:

```bash
# Start backup scheduler (runs daily at 3 AM)
nohup python scripts/backup_scheduler.py > /tmp/backup.log 2>&1 &
```

### Manual Backup:

```bash
# Create backup now
python scripts/backup_database.py

# List backups
python scripts/backup_database.py --list
```

### Restore from Backup:

```bash
# Restore latest
python scripts/restore_database.py --latest --force
```

Backups are stored in `/workspace/backups` (persists on network volume).

---

## 🔄 After Pod Restart

If your pod restarts, just run:

```bash
cd /workspace/nexuslang-v2
python recovery.py
```

Everything will be restored automatically!

---

## 🎯 Expose Port in RunPod

Make sure port 8000 is exposed in your RunPod dashboard:

1. Go to RunPod Dashboard
2. Find your pod
3. Click "Edit"
4. Under "Expose HTTP Ports", add: `8000`
5. Click "Save"

---

## ✅ Verify Deployment

Run the validation script:

```bash
cd v2/backend
python scripts/validate_deployment.py --verbose
```

This will test:
- ✅ All API endpoints
- ✅ Database connectivity
- ✅ Authentication flow
- ✅ Analytics system
- ✅ Health checks

---

## 📈 Monitor Your Platform

### Quick Health Check

```bash
curl http://localhost:8000/health/detailed | jq
```

### View Recent Events

```bash
psql -U nexus -d nexus_v2 -c \
  "SELECT event_type, COUNT(*) FROM analytics.events GROUP BY event_type ORDER BY count DESC LIMIT 10;"
```

### Check AI Usage

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v2/analytics/ai | jq
```

---

## 🎊 Success!

You now have:

- ✅ **Production-ready NexusLang v2 API**
- ✅ **Comprehensive analytics tracking**
- ✅ **Automated backup/restore**
- ✅ **Data persistence across restarts**
- ✅ **Health monitoring**
- ✅ **Prometheus metrics**
- ✅ **< 2 minute recovery time**

**Your platform is ready to change the world! 🚀**

---

## 🆘 Troubleshooting

### Server won't start?

```bash
# Check logs
tail -100 /tmp/nexus.log

# Run health checks
curl http://localhost:8000/health/detailed
```

### Database issues?

```bash
# Check PostgreSQL status
service postgresql status

# Restart PostgreSQL
service postgresql restart

# Verify database exists
psql -U nexus -d nexus_v2 -c "\dt"
```

### Redis issues?

```bash
# Check Redis
redis-cli ping

# Restart Redis
pkill redis-server
redis-server --daemonize yes --requirepass 7aH2pW9xR4mN8qL3vK6jT1yB5cZ0fG2s
```

---

**Need help?** Check `RECOVERY_SYSTEM_GUIDE.md` for detailed documentation!

