# 🧪 Testing Recovery & Analytics System on RunPod

## Step-by-Step Test Guide

Follow these steps to test the complete recovery and analytics system on your RunPod instance.

---

## 🔄 Step 1: Push Files to Git (From Local Machine)

On your **local Windows machine** (in Cursor terminal):

```bash
# Add all new files
git add .

# Commit
git commit -m "Add enterprise recovery and analytics system"

# Push to GitHub
git push origin main
```

---

## 📥 Step 2: Pull Files on RunPod

On your **RunPod terminal**:

```bash
# Navigate to project
cd /workspace/nexuslang-v2

# Pull latest changes
git pull origin main

# Verify files exist
ls -la recovery.py
ls -la v2/backend/scripts/
ls -la v2/backend/migrations/003_analytics.sql
```

---

## 🧪 Step 3: Test Recovery Script

```bash
# Stop any running servers
pkill -f uvicorn
pkill -f run_server

# Run recovery script
cd /workspace/nexuslang-v2
python recovery.py --verbose
```

**Expected Output**:
```
🚀 NexusLang v2 Recovery System
================================

[1/8] Installing PostgreSQL and Redis...
   ✅ System packages installed

[2/8] Starting PostgreSQL and Redis...
   ✅ Services started

[3/8] Creating database and user...
   ✅ Database configured

... (continues)

✅ Database initialized successfully
✅ Redis connected
✅ Server started on port 8000

🌐 Access Your API:
   https://YOUR-POD-ID-8000.proxy.runpod.net/docs
```

---

## 🏥 Step 4: Verify Health Checks

```bash
# Simple health check
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}

# Detailed health check
curl http://localhost:8000/health/detailed | python -m json.tool
```

**Expected**: All checks should show "healthy" or "degraded" (degraded is OK for optional components).

---

## 📊 Step 5: Test Analytics System

### 5.1 Apply Analytics Migration

```bash
cd /workspace/nexuslang-v2/v2/backend

# Run analytics migration
psql -U nexus -d nexus_v2 -f migrations/003_analytics.sql
```

**Expected Output**:
```
CREATE SCHEMA
CREATE TABLE
CREATE INDEX
... (multiple creates)
✅ Analytics schema created successfully!
```

### 5.2 Verify Analytics Tables

```bash
# Check tables exist
psql -U nexus -d nexus_v2 -c "\dt analytics.*"
```

**Expected**: Should show 8 tables in analytics schema.

### 5.3 Test Analytics API

```bash
# First, register and login to get a token
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Get dashboard metrics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/analytics/dashboard | python -m json.tool
```

**Expected**: JSON response with metrics (total_users, api_calls, etc.).

---

## 🗄️ Step 6: Test Backup System

### 6.1 Create Backup

```bash
cd /workspace/nexuslang-v2/v2/backend

# Create backup
python scripts/backup_database.py
```

**Expected Output**:
```
📊 Creating backup of database: nexus_v2
✅ Backup created: X.XX MB
🗜️  Compressing backup...
✅ Compressed: X.XX MB
   Compression ratio: X.XXx
✅ Backup saved: /workspace/backups/nexuslang_v2_backup_YYYYMMDD_HHMMSS.sql.gz
```

### 6.2 List Backups

```bash
python scripts/backup_database.py --list
```

**Expected**: Shows list of available backups.

### 6.3 Test Restore

```bash
# Restore latest backup
python scripts/restore_database.py --latest --force
```

**Expected**:
```
🔍 Validating backup...
✅ Backup file size: X.XX MB
✅ Backup file appears valid
🗜️  Decompressing backup...
✅ Decompressed successfully
🔄 Restoring database...
✅ Database restored successfully!
```

---

## 📈 Step 7: Test Prometheus Metrics

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Should show Prometheus format metrics
```

**Expected Output (excerpt)**:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/health",method="GET",status="200"} 5.0
...
```

---

## ✅ Step 8: Run Validation Tests

```bash
cd /workspace/nexuslang-v2/v2/backend

# Run validation script
python scripts/validate_deployment.py --verbose

# Expected: All tests should PASS
```

**Expected Output**:
```
🧪 NexusLang v2 Deployment Validation

✅ PASS: Health Endpoint
✅ PASS: Detailed Health Check
✅ PASS: API Documentation
✅ PASS: User Registration
✅ PASS: User Login
✅ PASS: Authenticated Endpoint
✅ PASS: Analytics Endpoints

📊 Test Summary
Total Tests: 8
✅ Passed: 8
❌ Failed: 0
Success Rate: 100.0%

Overall Status: PASS
```

---

## 🔄 Step 9: Test Pod Restart Recovery

This is the ultimate test!

### 9.1 Create Test Data

```bash
# Register a few users and create some events
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@test.com","password":"Pass123!"}'

curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user2","email":"user2@test.com","password":"Pass123!"}'
```

### 9.2 Create Backup

```bash
cd /workspace/nexuslang-v2/v2/backend
python scripts/backup_database.py
```

### 9.3 Restart Your Pod

Go to RunPod dashboard and restart your pod.

### 9.4 After Restart - Quick Recovery

```bash
# After pod restarts, run recovery
cd /workspace/nexuslang-v2
python recovery.py

# Should complete in < 2 minutes and restore your data!
```

### 9.5 Verify Data Restored

```bash
# Check users still exist
psql -U nexus -d nexus_v2 -c "SELECT username FROM users;"

# Should show user1 and user2
```

---

## 📊 Step 10: Test Analytics Features

### 10.1 Generate Some Events

```bash
# Make some API calls to generate events
for i in {1..10}; do
  curl http://localhost:8000/health
  sleep 1
done
```

### 10.2 Query Analytics

```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Get dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/analytics/dashboard?days=1 | python -m json.tool

# Get real-time stats
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/analytics/realtime/stats | python -m json.tool

# Get events
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v2/analytics/events?limit=20" | python -m json.tool
```

**Expected**: Should see metrics showing your test activity!

---

## 🎯 Success Checklist

After completing all steps, verify:

- [ ] Recovery script completes in < 2 minutes
- [ ] Server starts successfully
- [ ] Health check returns "healthy"
- [ ] Detailed health shows all components working
- [ ] Analytics tables created
- [ ] Can create database backup
- [ ] Can restore from backup
- [ ] Analytics API returns metrics
- [ ] Prometheus metrics exposed
- [ ] Validation tests all pass
- [ ] Data persists after pod restart
- [ ] Analytics tracks events correctly

---

## 🐛 Troubleshooting

### Recovery Script Fails?

```bash
# Check what failed
python recovery.py --manual --verbose

# View detailed logs
tail -100 /tmp/nexus.log
```

### Analytics Migration Fails?

```bash
# Check if schema exists
psql -U nexus -d nexus_v2 -c "\dn"

# Manually create schema
psql -U nexus -d nexus_v2 -c "CREATE SCHEMA IF NOT EXISTS analytics;"

# Run migration again
psql -U nexus -d nexus_v2 -f migrations/003_analytics.sql
```

### Backup/Restore Fails?

```bash
# Check PostgreSQL is running
service postgresql status

# Check permissions
ls -la /workspace/backups/

# Try manual pg_dump
pg_dump -U nexus -d nexus_v2 > test_backup.sql
```

### Analytics Not Tracking?

```bash
# Check if analytics tables exist
psql -U nexus -d nexus_v2 -c "SELECT COUNT(*) FROM analytics.events;"

# Check middleware is loaded
curl http://localhost:8000/health

# View recent events
psql -U nexus -d nexus_v2 -c "SELECT * FROM analytics.events ORDER BY timestamp DESC LIMIT 5;"
```

---

## 📝 Reporting Test Results

After testing, document your results:

```bash
# Generate validation report
python scripts/validate_deployment.py --report deployment_report.json

# View report
cat deployment_report.json
```

Share this report to confirm all tests passed!

---

## 🎊 Expected Final State

After all tests pass, you should have:

1. ✅ NexusLang v2 API running on port 8000
2. ✅ PostgreSQL with analytics schema
3. ✅ Redis connected
4. ✅ Database backup created in `/workspace/backups`
5. ✅ Analytics tracking all requests
6. ✅ Health checks all green
7. ✅ Can recover from pod restart in < 2 minutes
8. ✅ Data persists across restarts

---

**Ready to test? Start with Step 1 and work through each step!** 🚀

If anything fails, check the Troubleshooting section above.

