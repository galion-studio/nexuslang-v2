# Testing NexusLang v2 Integration on RunPod

**Verify both Galion and NexusLang work without conflicts**

---

## 🔍 Pre-Deployment Verification

### Check Existing Galion Services

```bash
# Check what's running
docker ps | grep galion

# Should see:
# galion-postgres
# galion-redis
# galion-backend
# galion-frontend
# (and possibly others)

# Test Galion is accessible
curl http://localhost:3000  # Galion frontend
curl http://localhost:8000/api/health  # Galion API (if this endpoint exists)
```

### Check Port Availability

```bash
# These ports should be FREE (not in use):
netstat -tuln | grep ":3100"  # Should be empty
netstat -tuln | grep ":8100"  # Should be empty

# These ports should be TAKEN (Galion):
netstat -tuln | grep ":3000"  # Should show Galion frontend
netstat -tuln | grep ":8000"  # Should show Galion backend
```

---

## 🚀 Deploy NexusLang v2

```bash
cd /workspace/project-nexus

# Run the integration deployment
chmod +x v2/deploy-nexuslang-to-runpod.sh
./v2/deploy-nexuslang-to-runpod.sh
```

**Expected output:**
```
✅ Docker found
✅ Docker Compose found
✅ Port 3100 is available
✅ Port 8100 is available
✅ NexusLang database ready
✅ NEXUSLANG V2 DEPLOYED SUCCESSFULLY!
```

---

## ✅ Post-Deployment Verification

### Test 1: Verify Galion Still Works

```bash
# Test Galion frontend (should still work)
curl -I http://localhost:3000
# Should return: HTTP/1.1 200 OK

# Test Galion backend (should still work)
curl http://localhost:8000/api/health
# Should return Galion health check

# Check Galion containers are running
docker ps | grep galion
# All Galion containers should still be running
```

**Expected:** ✅ Galion services unaffected

---

### Test 2: Verify NexusLang Works

```bash
# Test NexusLang backend health
curl http://localhost:8100/health

# Should return:
# {"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}

# Test NexusLang frontend
curl -I http://localhost:3100

# Should return: HTTP/1.1 200 OK

# Test API docs
curl http://localhost:8100/docs
# Should return HTML with OpenAPI docs
```

**Expected:** ✅ NexusLang services running

---

### Test 3: Check Resource Sharing

```bash
# Verify both services use same PostgreSQL
docker exec galion-postgres psql -U nexus -l

# Should show:
# galion          (Galion's database)
# nexuslang_v2    (NexusLang's database)

# Check Redis databases
docker exec galion-redis redis-cli -a ${REDIS_PASSWORD} INFO keyspace

# Should show:
# db0: (Galion's data)
# db1: (NexusLang's data)
```

**Expected:** ✅ Infrastructure shared cleanly

---

### Test 4: Full Functional Test

**NexusLang API:**
```bash
# Register a test user
curl -X POST http://localhost:8100/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'

# Should return JWT token

# Test code execution
curl -X POST http://localhost:8100/api/v2/nexuslang/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "code": "fn main() { print(\"Hello from NexusLang!\") }\nmain()"
  }'

# Should return execution result
```

**NexusLang IDE (Browser):**
1. Open: `http://localhost:3100/ide`
2. Register/login
3. Write code
4. Click "Run" - should execute
5. Click "Personality" - should open editor
6. Click "Compile" - should show binary stats

**Expected:** ✅ All features working

---

## 📊 Container Status

### Check All Containers

```bash
# List all running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected output:**
```
NAMES                   STATUS          PORTS
nexuslang-frontend      Up 5 minutes    0.0.0.0:3100->3000/tcp
nexuslang-backend       Up 5 minutes    0.0.0.0:8100->8000/tcp
galion-frontend         Up 2 days       0.0.0.0:3000->3000/tcp
galion-backend          Up 2 days       0.0.0.0:8000->8000/tcp
galion-postgres         Up 2 days       5432/tcp
galion-redis            Up 2 days       6379/tcp
```

---

## 📈 Resource Monitoring

### Check Memory Usage

```bash
# Docker stats
docker stats --no-stream

# Should show reasonable memory usage for all containers
# NexusLang backend: ~500MB-1GB
# NexusLang frontend: ~300MB-500MB
```

### Check Database Connections

```bash
# PostgreSQL connections
docker exec galion-postgres psql -U nexus -d postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Should show connections to both 'galion' and 'nexuslang_v2'
```

---

## 🐛 Troubleshooting

### NexusLang Backend Won't Start

```bash
# Check logs
cd v2
docker-compose -f docker-compose.nexuslang.yml logs nexuslang-backend

# Common issues:
# - Database connection: Check POSTGRES_PASSWORD
# - Port conflict: Check nothing else uses 8100
# - Network: Verify galion-network exists
```

**Fix:**
```bash
# Restart with fresh state
docker-compose -f docker-compose.nexuslang.yml down
docker-compose -f docker-compose.nexuslang.yml up -d
```

### Frontend Can't Connect to Backend

```bash
# Check NEXT_PUBLIC_API_URL
docker-compose -f docker-compose.nexuslang.yml exec nexuslang-frontend env | grep NEXT_PUBLIC

# Should show: NEXT_PUBLIC_API_URL=http://localhost:8100
```

**Fix:**
```bash
# Rebuild frontend with correct env
docker-compose -f docker-compose.nexuslang.yml up -d --build nexuslang-frontend
```

### Database Issues

```bash
# Check if nexuslang_v2 database exists
docker exec galion-postgres psql -U nexus -l | grep nexuslang

# If missing, create it:
docker exec galion-postgres psql -U nexus -d postgres -c "CREATE DATABASE nexuslang_v2;"
```

---

## ✅ Success Checklist

After deployment, verify all these work:

### Galion (Existing - Should Not Be Affected)
- [ ] http://localhost:3000 accessible
- [ ] http://localhost:8000 responds
- [ ] Galion containers running
- [ ] No errors in Galion logs

### NexusLang (New)
- [ ] http://localhost:3100 shows NexusLang IDE
- [ ] http://localhost:8100/health returns healthy status
- [ ] http://localhost:8100/docs shows API documentation
- [ ] Can register new user
- [ ] Can create project
- [ ] Can run code
- [ ] Can save files
- [ ] Personality editor works
- [ ] Binary compilation works

### Infrastructure (Shared)
- [ ] PostgreSQL has both databases (galion, nexuslang_v2)
- [ ] Redis has both DB 0 and DB 1
- [ ] No unusual CPU/memory spikes
- [ ] No port conflicts
- [ ] All containers healthy

---

## 🎯 Quick Smoke Test

Run this complete test sequence:

```bash
#!/bin/bash
echo "🧪 Running smoke tests..."

# Test Galion
echo "1. Testing Galion..."
curl -f http://localhost:3000 > /dev/null && echo "✅ Galion frontend OK" || echo "❌ Galion frontend FAIL"

# Test NexusLang
echo "2. Testing NexusLang..."
curl -f http://localhost:8100/health > /dev/null && echo "✅ NexusLang backend OK" || echo "❌ NexusLang backend FAIL"
curl -f http://localhost:3100 > /dev/null && echo "✅ NexusLang frontend OK" || echo "❌ NexusLang frontend FAIL"

# Test databases
echo "3. Testing databases..."
docker exec galion-postgres psql -U nexus -l | grep -q "nexuslang_v2" && echo "✅ NexusLang database exists" || echo "❌ Database missing"

echo "🎉 Smoke tests complete!"
```

---

## 📞 Support

If tests fail, check:
1. `v2/docker-compose.nexuslang.yml` - Correct configuration
2. `v2/backend/.env` - Correct credentials
3. Docker logs - Error messages
4. Port availability - No conflicts

---

**When all tests pass: ✅ Ready for production!** 🚀

