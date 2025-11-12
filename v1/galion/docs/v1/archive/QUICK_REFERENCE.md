# 🚀 GALION.APP - QUICK REFERENCE

**Status:** ✅ FULLY OPERATIONAL  
**Deployed:** November 9, 2025

---

## ⚡ ONE-COMMAND OPERATIONS

### Start All Services
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Restart All Services
```bash
docker-compose restart
```

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f auth-service
docker-compose logs -f user-service
```

---

## 🌐 ACCESS POINTS

### Application
- **API Gateway:** http://localhost:8080
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8080/health

### Monitoring
- **Grafana:** http://localhost:3000
- **Prometheus:** http://localhost:9091
- **Kafka UI:** http://localhost:8090

---

## 🔥 QUICK TESTS

### Health Check
```bash
curl http://localhost:8080/health
```

### Register User
```powershell
$body = @{
    email = "user@example.com"
    password = "SecurePass123!"
    name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8080/api/v1/auth/register" `
  -ContentType "application/json" `
  -Body $body
```

### Login & Get Token
```powershell
$body = @{
    email = "user@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8080/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body $body

$token = $response.data.token
Write-Host "Token: $token"
```

### Access Protected Endpoint
```powershell
Invoke-RestMethod -Method Get `
  -Uri "http://localhost:8080/api/v1/auth/me" `
  -Headers @{Authorization = "Bearer $token"}
```

---

## 🛠️ TROUBLESHOOTING

### Services Not Starting
```bash
# Regenerate secrets
.\generate-secrets.ps1

# Remove old containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose build
docker-compose up -d
```

### Database Connection Issues
```bash
# Wait for PostgreSQL to be ready
docker exec nexus-postgres pg_isready -U nexuscore

# Check database logs
docker logs nexus-postgres
```

### Port Already in Use
```bash
# Find process using port 8080 (example)
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F
```

---

## 📊 SERVICE REFERENCE

| Service | Port | Tech | Purpose |
|---------|------|------|---------|
| API Gateway | 8080 | Go | Main entry point |
| Auth Service | 8000 | Python | Authentication |
| User Service | 8001 | Python | User management |
| Scraping Service | 8002 | Python | Web scraping |
| Analytics Service | 9090 | Go | Event processing |
| PostgreSQL | 5432 | - | Database |
| Redis | 6379 | - | Cache |
| Kafka | 9092 | - | Events |
| Prometheus | 9091 | - | Metrics |
| Grafana | 3000 | - | Dashboards |
| Kafka UI | 8090 | - | Kafka management |

---

## 🔐 SECURITY

### Default Credentials
- **Grafana:** admin / (check `.env` for password)
- **PostgreSQL:** nexuscore / (check `.env`)
- **Redis:** (check `.env`)

### Rate Limits
- **Default:** 60 requests/minute per IP
- **Header:** X-Ratelimit-Limit, X-Ratelimit-Remaining

---

## 🎯 QUICK COMMANDS

```bash
# Full reset
docker-compose down -v && docker-compose build && docker-compose up -d

# Check resource usage
docker stats

# Clean up Docker
docker system prune -a

# Database backup
docker exec nexus-postgres pg_dump -U nexuscore nexuscore > backup.sql

# Database restore
docker exec -i nexus-postgres psql -U nexuscore nexuscore < backup.sql
```

---

## 📚 DOCUMENTATION

- **Full Report:** [DEPLOYMENT_REPORT.md](DEPLOYMENT_REPORT.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Build Guide:** [BUILD_NOW.md](BUILD_NOW.md)
- **README:** [README.md](README.md)

---

**Need Help?**
- Check logs: `docker-compose logs [service]`
- Check health: `curl http://localhost:8080/health`
- Check status: `docker-compose ps`

---

**Built with First Principles | Deployed with Speed | Ready for Scale**

