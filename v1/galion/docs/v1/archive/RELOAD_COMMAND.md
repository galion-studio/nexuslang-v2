# 🔄 NEXUS RELOAD COMMAND

**One command to clear cache and reload everything.**

---

## ⚡ QUICK START

### Windows:
```powershell
.\reload-nexus.ps1
```

### Linux/Mac:
```bash
./reload-nexus.sh
```

**Takes:** ~60 seconds  
**Result:** Fresh system with cleared cache

---

## 🎯 WHAT IT DOES

The reload command performs 6 operations:

### 1. Clear Redis Cache ✅
- Flushes all cached data
- Clears rate limit counters
- Removes session data
- Fresh start for cache

### 2. Stop Application Services ✅
- api-gateway
- auth-service
- user-service
- scraping-service
- voice-service
- analytics-service

**Note:** Database services (PostgreSQL, Redis, Kafka) keep running

### 3. Remove Containers ✅
- Forces Docker to recreate containers
- Ensures no stale state
- Clean initialization

### 4. Start All Services ✅
- Brings up entire stack
- Waits for dependencies
- Initializes health checks

### 5. Wait for Health Checks ✅
- 45-second wait for full initialization
- Progress indicator shows status
- Ensures services are ready

### 6. Verify System ✅
- Tests all service endpoints
- Shows health status
- Displays running count

---

## 📊 EXAMPLE OUTPUT

```
================================
NEXUS CORE - FULL SYSTEM RELOAD
Clearing Caches & Reloading Services
================================

[1/5] Clearing Redis cache...
✓ Redis cache cleared

[2/5] Stopping all application services...
  - Stopping api-gateway...
  - Stopping auth-service...
  - Stopping user-service...
  - Stopping scraping-service...
  - Stopping voice-service...
  - Stopping analytics-service...
✓ All services stopped

[3/5] Removing containers for clean restart...
✓ Containers removed

[4/5] Starting all services...
✓ Services restarted

[5/5] Waiting for services to be healthy...
  This takes ~45 seconds for health checks...
  ▓▓▓░░░░░░░ 25% - Services initializing...
  ▓▓▓▓▓▓░░░░ 50% - Database connections...
  ▓▓▓▓▓▓▓▓░░ 75% - Health checks running...
  ▓▓▓▓▓▓▓▓▓▓ 100% - Services ready!

================================
SYSTEM STATUS
================================

✓ API Gateway: HEALTHY
✓ Auth Service: HEALTHY
✓ User Service: HEALTHY
✓ Analytics Service: HEALTHY
✓ Voice Service: HEALTHY
✓ Scraping Service: HEALTHY

================================
Running Services: 12/12
================================
RELOAD COMPLETE!
================================

All caches cleared, all services reloaded!
```

---

## 🔧 WHEN TO USE

### Perfect For:

✅ **After Code Changes**
- Deployed new version
- Modified configuration
- Updated environment variables

✅ **Cache Issues**
- Stale data in Redis
- Rate limits stuck
- Session problems

✅ **Service Issues**
- Services not responding
- Weird behavior
- Need clean state

✅ **Testing**
- Start fresh for tests
- Clear previous data
- Consistent environment

✅ **Development**
- Switched branches
- Testing changes
- Reset to known state

### NOT Needed For:

❌ **Normal Operations** - Services run fine continuously  
❌ **Database Changes** - Use migrations instead  
❌ **Viewing Logs** - Use `docker-compose logs -f`  
❌ **Checking Status** - Use `docker-compose ps`

---

## 🚨 WHAT GETS CLEARED

### ✅ Cleared (Safe):
- Redis cache data
- Rate limit counters
- Cached API responses
- Session data (users logged out)
- Service container state

### ✅ Preserved (Safe):
- PostgreSQL database
- Kafka message history
- Docker volumes
- Environment configuration
- User accounts
- Analytics data

---

## 🛠️ ALTERNATIVE COMMANDS

### Reload Specific Service:
```powershell
# Stop service
docker-compose stop auth-service

# Remove container
docker-compose rm -f auth-service

# Start fresh
docker-compose up -d auth-service
```

### Clear Cache Only:
```powershell
# Get Redis password from .env
$pass = (Get-Content .env | Select-String "^REDIS_PASSWORD=").ToString().Split('=')[1]

# Clear cache
docker exec nexus-redis redis-cli -a $pass FLUSHALL
```

### Restart Without Cache Clear:
```powershell
docker-compose restart
```

### Full System Restart:
```powershell
# Stop everything
docker-compose down

# Start everything
docker-compose up -d
```

### Nuclear Option (Delete Everything):
```powershell
# CAUTION: Deletes all data including database
docker-compose down -v
docker-compose up -d
```

---

## 📋 TROUBLESHOOTING

### Services Stay "STARTING"

**Problem:** Health checks not passing  
**Solution:** Wait 60 seconds total, then check logs

```powershell
docker logs nexus-api-gateway
docker logs nexus-auth-service
```

### Redis Cache Clear Fails

**Problem:** Redis not running  
**Solution:** Start Redis first

```powershell
docker-compose up -d redis
# Wait 10 seconds
.\reload-nexus.ps1
```

### Services Don't Start

**Problem:** Port conflicts or Docker issues  
**Solution:** Stop everything and start fresh

```powershell
docker-compose down
docker-compose up -d
```

### "Permission Denied" on Linux

**Problem:** Script not executable  
**Solution:** Make it executable

```bash
chmod +x reload-nexus.sh
./reload-nexus.sh
```

---

## 🎓 FIRST PRINCIPLES

**Why this command exists:**

1. **Question Requirements:** Do we need complex orchestration? NO - simple script works
2. **Delete Complexity:** No Kubernetes, no fancy tools - just Docker commands
3. **Fix Fundamentals:** Cache + Container state = main issues → clear both
4. **Move Fast:** One command, 60 seconds, done
5. **Be Transparent:** Shows exactly what it's doing, verifies results

**Result:** Operations that take 5 minutes elsewhere take 60 seconds here.

---

## 📚 RELATED COMMANDS

```powershell
# Admin Terminal (full system control)
.\nexus-admin.ps1

# View Logs
docker-compose logs -f [service-name]

# Check Status
docker-compose ps

# Test API
curl.exe http://localhost:8080/health

# Build All
docker-compose build --parallel

# Stop All
docker-compose down

# Start All
docker-compose up -d
```

---

## ✅ SUCCESS INDICATORS

**Reload successful when:**
1. ✅ All 6 services show "HEALTHY"
2. ✅ Running Services: 12/12
3. ✅ API Gateway responds to health check
4. ✅ No errors in output

**If not all healthy:**
- Wait 30 more seconds
- Check logs: `docker logs nexus-[service-name]`
- Try again: `.\reload-nexus.ps1`

---

**Built with Elon Musk's First Principles - Fast, Simple, Effective** 🚀

