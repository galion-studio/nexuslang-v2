# 🚀 START TESTING NOW - NexusLang v2 Recovery & Analytics

**Everything is ready! Here's how to test it on RunPod.**

---

## 📋 Pre-Test Checklist

- [ ] You have RunPod instance running
- [ ] Port 8000 is exposed in RunPod dashboard
- [ ] You're currently on your local Windows machine in Cursor

---

## Step 1: Push Code to Git (RIGHT NOW!)

Run these commands in your **Cursor terminal** (Windows):

```bash
# Add all new files
git add .

# Commit with message
git commit -m "Add enterprise recovery and analytics system - instant deployment ready"

# Push to GitHub
git push origin main
```

**✅ After this completes, move to RunPod!**

---

## Step 2: On RunPod Terminal

Copy and paste these commands **ONE BY ONE** into your RunPod terminal:

### 2.1 Pull Latest Code

```bash
cd /workspace/nexuslang-v2
git pull origin main
```

### 2.2 Verify Files

```bash
# Check recovery script exists
ls -la recovery.py

# Check analytics migration
ls -la v2/backend/migrations/003_analytics.sql

# Check backup scripts
ls -la v2/backend/scripts/
```

### 2.3 Install Missing Dependency

```bash
pip install psutil
```

### 2.4 Run the Recovery Script!

```bash
# This is the big test!
python recovery.py
```

**Watch it run! It should:**
1. Install PostgreSQL and Redis
2. Create database and user
3. Install Python packages
4. Fix all imports
5. Start the server
6. Run health checks
7. Complete in < 2 minutes!

---

## Step 3: Apply Analytics Migration

```bash
cd /workspace/nexuslang-v2/v2/backend

# Apply the analytics schema
sudo -u postgres psql -d nexus_v2 -f migrations/003_analytics.sql
```

**Expected**: Should see "✅ Analytics schema created successfully!"

---

## Step 4: Restart Server with Analytics

```bash
# Stop current server
pkill -f uvicorn

# Start with analytics enabled
nohup python run_server.py > /tmp/nexus.log 2>&1 &

# Wait for startup
sleep 5

# Test
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}`

---

## Step 5: Test Analytics

### 5.1 Register a Test User

```bash
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'
```

### 5.2 Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}'
```

**Copy the `access_token` from the response!**

### 5.3 Test Analytics Endpoints

```bash
# Replace YOUR_TOKEN with the token from step 5.2
TOKEN="paste-your-token-here"

# Get dashboard metrics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/analytics/dashboard | python -m json.tool

# Get real-time stats
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/analytics/realtime/stats | python -m json.tool
```

**Expected**: JSON with analytics data!

---

## Step 6: Test Backup System

```bash
cd /workspace/nexuslang-v2/v2/backend

# Create backup
python scripts/backup_database.py

# List backups
python scripts/backup_database.py --list

# Test restore
python scripts/restore_database.py --list
```

**Expected**: Backup created in `/workspace/backups/`

---

## Step 7: Test Health Checks

```bash
# Detailed health check
curl http://localhost:8000/health/detailed | python -m json.tool

# Prometheus metrics
curl http://localhost:8000/metrics | head -30
```

**Expected**: All health checks pass or show "degraded" (acceptable)

---

## Step 8: Run Validation Suite

```bash
cd /workspace/nexuslang-v2/v2/backend

# Run automated tests
python scripts/validate_deployment.py --verbose --report test_report.json

# View report
cat test_report.json | python -m json.tool
```

**Expected**: "Overall Status: PASS" with 8/8 tests passed

---

## Step 9: Configure Volumes (Optional but Recommended)

```bash
cd /workspace/nexuslang-v2

# Configure persistent storage
bash configure_volumes.sh
```

**This ensures data persists across pod restarts!**

---

## Step 10: Access Your API

### In Your Browser:

Open these URLs:

1. **API Docs**: `https://4fb77d7346b2-8000.proxy.runpod.net/docs`
2. **Health**: `https://4fb77d7346b2-8000.proxy.runpod.net/health`
3. **Detailed Health**: `https://4fb77d7346b2-8000.proxy.runpod.net/health/detailed`
4. **Metrics**: `https://4fb77d7346b2-8000.proxy.runpod.net/metrics`

**(Replace `4fb77d7346b2` with your actual pod ID)**

---

## ✅ Success Checklist

After completing all steps, you should have:

- [ ] Recovery script completed in < 2 minutes ⚡
- [ ] Server running on port 8000 🚀
- [ ] Health check returns "healthy" 💚
- [ ] Analytics schema created 📊
- [ ] Can register and login users 👤
- [ ] Analytics API returns metrics 📈
- [ ] Database backup created 💾
- [ ] Validation tests all pass ✅
- [ ] Can access API docs in browser 📚
- [ ] Prometheus metrics exposed 📊

---

## 🎯 What You've Achieved

If all tests pass, you now have:

1. ✅ **Sub-2-minute recovery** from any pod restart
2. ✅ **Complete analytics** tracking every platform action
3. ✅ **Automated backups** with retention and S3 support
4. ✅ **Zero data loss** with volume persistence
5. ✅ **Enterprise monitoring** with Prometheus/Grafana
6. ✅ **Comprehensive health checks** for all components
7. ✅ **Automated testing** for deployment validation
8. ✅ **Cost tracking** for AI usage
9. ✅ **Performance monitoring** for all endpoints
10. ✅ **Production-ready** infrastructure

---

## 🐛 If Something Fails

### Recovery Script Issues?
```bash
# Check logs
tail -100 /tmp/nexus.log

# Try manual mode
python recovery.py --manual --verbose
```

### Analytics Migration Fails?
```bash
# Check if database exists
psql -U nexus -d nexus_v2 -c "\l"

# Grant permissions
sudo -u postgres psql -d nexus_v2 -c "GRANT ALL ON SCHEMA public TO nexus;"

# Retry migration
psql -U nexus -d nexus_v2 -f migrations/003_analytics.sql
```

### Server Won't Start?
```bash
# Check what's using port 8000
lsof -i :8000

# Kill it
pkill -f uvicorn

# Try again
python run_server.py
```

---

## 📞 Need Help?

Check these docs:
- **Quick Start**: `RUNPOD_QUICK_DEPLOY.md`
- **Complete Guide**: `RECOVERY_SYSTEM_GUIDE.md`
- **Testing Guide**: `TEST_ON_RUNPOD.md`
- **Copy-Paste Commands**: `COPY_TO_RUNPOD.txt`

---

## 🎉 YOU'RE READY!

**Time to test your enterprise-grade recovery and analytics system!**

**Start with Step 1 above and work through each step.** 

**Good luck! 🚀**

---

*P.S. - After testing, share your test_report.json to show everything works!*

