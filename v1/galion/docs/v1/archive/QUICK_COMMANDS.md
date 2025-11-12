# Quick Command Reference

## 🎯 Check Status

```powershell
# View all running Docker containers
docker ps

# Check specific service
docker ps | Select-String "galion"

# Test frontend
curl http://localhost:3000
```

## 🔄 Restart Services

```powershell
# Restart Docker services
docker-compose -f docker-compose.minimal.yml restart

# Restart specific service
docker restart galion-postgres
docker restart galion-redis

# Restart frontend: Go to the PowerShell window and press Ctrl+C, then:
npm run dev
```

## 🛑 Stop Services

```powershell
# Stop all Docker services
docker-compose -f docker-compose.minimal.yml down

# Stop frontend: Close the PowerShell window or press Ctrl+C
```

## 🚀 Start Services Again

```powershell
# Start Docker services
docker-compose -f docker-compose.minimal.yml up -d

# Start frontend (in new window)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Or manually
cd frontend
npm run dev
```

## 📊 View Logs

```powershell
# All Docker services
docker-compose -f docker-compose.minimal.yml logs -f

# Specific service
docker logs -f galion-postgres
docker logs -f galion-redis

# Frontend: Check the PowerShell window that opened
```

## 🔍 Debug

```powershell
# Check if ports are in use
netstat -ano | findstr "3000 5432 6379 9091"

# Verify services are healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test database connection
docker exec -it galion-postgres psql -U galion -d galion -c "SELECT version();"

# Test Redis
docker exec -it galion-redis redis-cli ping
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Prometheus**: http://localhost:9091
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **PgBouncer**: localhost:6432

## 📝 Common Tasks

### Clean Everything and Restart
```powershell
# Stop all
docker-compose -f docker-compose.minimal.yml down

# Remove volumes (CAUTION: Deletes data!)
docker-compose -f docker-compose.minimal.yml down -v

# Start fresh
docker-compose -f docker-compose.minimal.yml up -d
cd frontend; npm run dev
```

### Add More Services
Edit `docker-compose.minimal.yml` to add services from `services/` directory:
- auth-service
- user-service
- document-service
- permissions-service
- voice-service

---

**Built with First Principles** 🚀
Simple. Fast. Functional.

