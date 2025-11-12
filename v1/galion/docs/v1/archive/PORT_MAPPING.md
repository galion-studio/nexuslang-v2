# 🔌 NEXUS PORT MAPPING & CATEGORIZATION

**Last Updated:** November 9, 2025  
**Purpose:** Organized port structure to avoid conflicts and enable easy scaling

---

## 📊 PORT CATEGORIES

All ports are bound to `127.0.0.1` (localhost only) except the API Gateway for security.

### 🌐 PUBLIC FACING (8000-8099)
*Services accessible from the internet*

| Port | Service | Description | Access |
|------|---------|-------------|--------|
| **8080** | API Gateway | Main entry point for all API requests | Public (0.0.0.0) |

---

### 🔐 INTERNAL SERVICES (8100-8199)
*Microservices accessible only via API Gateway*

| Port | Service | Internal Port | Description |
|------|---------|---------------|-------------|
| **8100** | Auth Service | 8000 | User authentication & JWT tokens |
| **8101** | User Service | 8001 | User profile management |
| **8102** | Scraping Service | 8002 | AI-powered web scraping |
| **8103** | Voice Service | 8003 | Voice interface (STT/TTS) |
| **8104** | Document Service | 8004 | Document verification |
| **8105** | Permissions Service | 8005 | RBAC & access control |

---

### 💾 DATA STORES (5400-5499)
*Primary databases and cache systems*

| Port | Service | Internal Port | Description |
|------|---------|---------------|-------------|
| **5432** | PostgreSQL | 5432 | Main database (standard port kept) |
| **5479** | Redis | 6379 | Cache, sessions, rate limiting |

---

### 📨 MESSAGE QUEUE (9200-9299)
*Event streaming and message broker*

| Port | Service | Internal Port | Description |
|------|---------|---------------|-------------|
| **9200** | Kafka | 9093 | Event streaming broker |
| N/A | Zookeeper | 2181 | Kafka coordination (internal only) |

---

### 📈 MONITORING & ANALYTICS (9300-9399)
*Dashboards, metrics, and system monitoring*

| Port | Service | Internal Port | Description |
|------|---------|---------------|-------------|
| **9300** | Grafana | 3000 | Metrics dashboards & visualization |
| **9301** | Prometheus | 9090 | Metrics collection & storage |
| **9302** | Analytics Service | 9090 | Event processing & analytics |
| **9303** | Kafka UI | 8080 | Kafka management interface |

---

## 🎯 QUICK ACCESS URLS

### Main Application
- **API Gateway:** http://localhost:8080
- **API Health:** http://localhost:8080/health
- **API Docs:** http://localhost:8080/docs (if available)

### Internal Services (Development Only)
- **Auth Service:** http://localhost:8100
- **User Service:** http://localhost:8101
- **Scraping Service:** http://localhost:8102
- **Voice Service:** http://localhost:8103
- **Document Service:** http://localhost:8104
- **Permissions Service:** http://localhost:8105

### Data Stores (Development Access)
```bash
# PostgreSQL
psql -h localhost -p 5432 -U postgres -d nexus

# Redis CLI
redis-cli -h localhost -p 5479
```

### Monitoring Dashboards
- **Grafana:** http://localhost:9300 *(New port - no conflicts!)*
- **Prometheus:** http://localhost:9301
- **Kafka UI:** http://localhost:9303

### Message Queue
- **Kafka (external):** localhost:9200

---

## 🔧 WHY THIS STRUCTURE?

### Benefits
1. **No Port Conflicts** - Each service in its own range
2. **Easy to Remember** - Logical grouping by function
3. **Room to Grow** - 100 ports per category
4. **Security First** - Only API Gateway public by default
5. **Quick Troubleshooting** - Port number tells you the service type

### Port Selection Logic
- **8000-8099**: Public services (currently just API Gateway)
- **8100-8199**: Internal microservices (easy sequential numbering)
- **5400-5499**: Data stores (standard DB port range)
- **9200-9299**: Message queuing (high port, messaging semantics)
- **9300-9399**: Monitoring tools (high port, administrative)

---

## 🚨 CONFLICT RESOLUTION

### Previous Conflicts Fixed
- **Grafana 3000 → 9300** - Port 3000 commonly used by React/Next.js
- **Redis 6379 → 5479** - Avoid default Redis conflicts
- **Kafka 9093 → 9200** - Better categorization

### Avoiding Future Conflicts
When adding new services:
1. Identify service category
2. Use next available port in that range
3. Update this documentation
4. Update docker-compose.yml with category comment

---

## 📝 ADDING NEW SERVICES

### Template for docker-compose.yml

```yaml
# [Service Name] - [Description]
service-name:
  build: ./services/service-name
  container_name: nexus-service-name
  # PORT CATEGORY: [Category Name] ([Range])
  ports:
    - "127.0.0.1:[HOST_PORT]:[CONTAINER_PORT]"  # [Service Name] - [Access Type]
```

### Port Assignment Rules
1. **Determine category** (Public/Internal/Data/Queue/Monitor)
2. **Check next available** port in range
3. **Add category comment** in docker-compose.yml
4. **Update this document**
5. **Test for conflicts** before committing

### Available Ranges
- Public (8000-8099): 99 ports available
- Internal (8100-8199): 94 ports available (6 used)
- Data (5400-5499): 98 ports available (2 used)
- Queue (9200-9299): 99 ports available (1 used)
- Monitor (9300-9399): 96 ports available (4 used)

---

## 🔄 MIGRATION GUIDE

### If Services Won't Start After Update

1. **Stop all containers:**
```powershell
docker-compose down
```

2. **Remove old containers:**
```powershell
docker-compose rm -f
```

3. **Update any hardcoded URLs** in your code:
```bash
# Old URLs → New URLs
localhost:8000 → localhost:8100  # Auth Service
localhost:8001 → localhost:8101  # User Service
localhost:8002 → localhost:8102  # Scraping Service
localhost:8003 → localhost:8103  # Voice Service
localhost:8004 → localhost:8104  # Document Service
localhost:8005 → localhost:8105  # Permissions Service
localhost:3000 → localhost:9300  # Grafana
localhost:9091 → localhost:9301  # Prometheus
localhost:8090 → localhost:9303  # Kafka UI
localhost:9093 → localhost:9200  # Kafka
```

4. **Restart services:**
```powershell
docker-compose up -d
```

5. **Verify all services:**
```powershell
docker-compose ps
curl http://localhost:8080/health
```

---

## 🛡️ SECURITY NOTES

### Port Binding Strategy
- **127.0.0.1**: Only accessible from host machine (secure)
- **0.0.0.0**: Accessible from network (only API Gateway)

### Production Recommendations
1. **Use firewall rules** to restrict access
2. **Enable TLS/SSL** on API Gateway
3. **Use VPN/Bastion** for monitoring tools
4. **Never expose data stores** to public internet
5. **Implement rate limiting** on API Gateway

---

## 📞 TROUBLESHOOTING

### Port Already in Use
```powershell
# Find what's using the port (Windows)
netstat -ano | findstr :[PORT]

# Kill the process
taskkill /PID [PID] /F
```

### Service Not Responding
```powershell
# Check if container is running
docker ps | findstr nexus

# Check logs
docker logs nexus-[service-name]

# Restart specific service
docker-compose restart [service-name]
```

### Can't Access on New Port
1. Verify service is running: `docker ps`
2. Check port mapping: `docker port nexus-[service-name]`
3. Test locally: `curl http://localhost:[PORT]/health`
4. Check firewall rules

---

## ✅ VALIDATION CHECKLIST

After changing ports:

- [ ] Updated docker-compose.yml
- [ ] Updated PORT_MAPPING.md (this file)
- [ ] Updated README.md access URLs
- [ ] Stopped old containers
- [ ] Started services with new ports
- [ ] Verified all services healthy
- [ ] Updated any documentation
- [ ] Updated monitoring configs (Prometheus targets)
- [ ] Tested API endpoints
- [ ] Verified Grafana dashboards load

---

## 📊 PORT USAGE SUMMARY

| Category | Ports Used | Ports Available | Utilization |
|----------|------------|-----------------|-------------|
| Public | 1/100 | 99 | 1% |
| Internal | 6/100 | 94 | 6% |
| Data Stores | 2/100 | 98 | 2% |
| Message Queue | 1/100 | 99 | 1% |
| Monitoring | 4/100 | 96 | 4% |
| **TOTAL** | **14** | **486** | **3%** |

**Plenty of room to grow!** 🚀

---

**Questions?** Open an issue or check docker-compose.yml for current configuration.

**Last Port Assignment:** 9303 (Kafka UI)  
**Next Available Ports:** 8106 (Internal), 9201 (Queue), 9304 (Monitor)


