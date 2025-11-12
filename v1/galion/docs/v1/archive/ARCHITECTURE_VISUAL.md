# GALION VPS Architecture - Visual Reference
## Production Infrastructure Overview

**Server:** TITANAXE VPS (54.37.161.67)  
**Capacity:** 16GB RAM, 100GB SSD  
**OS:** Ubuntu 24.04 LTS

---

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   CLOUDFLARE CDN                            │
│  • DDoS Protection (free)                                   │
│  • SSL/TLS Termination                                      │
│  • Static Asset Caching                                     │
│  • Bot Protection                                           │
│  • Rate Limiting (optional)                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  NGINX REVERSE PROXY                        │
│  Ports: 80 (HTTP → HTTPS redirect), 443 (HTTPS)            │
│  • Load Balancing (upstream configuration)                  │
│  • SSL/TLS (Let's Encrypt certificates)                     │
│  • Caching (1.5GB: API + Static)                           │
│  • Compression (gzip + brotli)                              │
│  • Rate Limiting (100-200 req/min)                          │
│  • Security Headers (HSTS, CSP, X-Frame)                    │
│  • Connection Pooling (keepalive)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
┌─────▼────────┐              ┌─────▼────────┐
│ GALION.APP   │              │ GALION.STUDIO│
│              │              │              │
│ Frontend     │              │ Frontend     │
│ Port: 3001   │              │ Port: 3003   │
│ (React)      │              │ (Next.js)    │
│ Mem: 384MB   │              │ Mem: 512MB   │
└──────┬───────┘              └──────┬───────┘
       │                             │
┌──────▼───────┐              ┌──────▼───────┐
│ API          │              │ API          │
│ Port: 8001   │              │ Port: 8003   │
│ (FastAPI)    │              │ (FastAPI)    │
│ Mem: 1.5GB   │              │ Mem: 1.5GB   │
└──────┬───────┘              └──────┬───────┘
       │                             │
┌──────▼───────┐              ┌──────▼───────┐
│ Voice Service│              │ Realtime Svc │
│ Port: 8002   │              │ Port: 8004   │
│ (Node.js)    │              │ (Socket.IO)  │
│ Mem: 1.5GB   │              │ Mem: 512MB   │
└──────┬───────┘              └──────┬───────┘
       │                             │
       └──────────────┬──────────────┘
                      │
         ┌────────────▼────────────┐
         │     PGBOUNCER            │
         │  Connection Pooler       │
         │  Port: 6432              │
         │  1000 clients → 100 DB   │
         │  Mem: 128MB              │
         └────────────┬─────────────┘
                      │
         ┌────────────▼─────────────┐
         │     POSTGRESQL 15         │
         │  Databases:               │
         │    • galion               │
         │    • galion_studio        │
         │  Port: 5432               │
         │  Mem: 1.5GB               │
         │  Storage: 20GB+           │
         │                           │
         │  Features:                │
         │    • WAL archiving (PITR) │
         │    • Replication ready    │
         │    • Optimized for SSD    │
         │    • Connection pooling   │
         └───────────────────────────┘

         ┌────────────────────────────┐
         │     REDIS 7                │
         │  Multi-DB:                 │
         │    DB 0: App sessions      │
         │    DB 1: Voice cache       │
         │    DB 2: Studio sessions   │
         │    DB 3: Realtime data     │
         │    DB 4: Rate limiting     │
         │  Port: 6379                │
         │  Mem: 2GB max              │
         │  Persistence: AOF + RDB    │
         └────────────────────────────┘
```

---

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MONITORING STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                   PROMETHEUS                          │ │
│  │  Port: 9090                                           │ │
│  │  Retention: 30 days                                   │ │
│  │  Mem: 512MB                                           │ │
│  │                                                       │ │
│  │  Scrapes metrics from:                                │ │
│  │    • Application APIs (/metrics)                      │ │
│  │    • Node Exporter (system)                           │ │
│  │    • cAdvisor (containers)                            │ │
│  │    • Postgres Exporter (database)                     │ │
│  │    • Redis Exporter (cache)                           │ │
│  │    • Nginx Exporter (web server)                      │ │
│  │                                                       │ │
│  │  Evaluates 18 alert rules                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │               GRAFANA CLOUD (Optional)                │ │
│  │  • Dashboards & Visualization                         │ │
│  │  • Long-term storage (14 days)                        │ │
│  │  • Alerting (email, Slack, PagerDuty)                 │ │
│  │  • Free tier: 10K series, 50GB logs                   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### User Request Journey

```
1. USER
   │
   ├─> https://galion.app
   │
2. CLOUDFLARE CDN
   │
   ├─> Check cache (static assets)
   │   ├─ HIT → Return cached (edge location)
   │   └─ MISS → Continue ↓
   │
3. NGINX (54.37.161.67:443)
   │
   ├─> SSL/TLS termination
   ├─> Security checks
   ├─> Rate limiting
   ├─> Check cache (API responses)
   │   ├─ HIT → Return cached
   │   └─ MISS → Continue ↓
   │
4. APPLICATION (Docker Container)
   │
   ├─> galion-app-frontend:3001 (React SPA)
   │   └─> Returns index.html
   │
   └─> galion-app-api:8001 (FastAPI)
       │
       ├─> Auth check (JWT token)
       ├─> Rate limiting check (Redis)
       ├─> Check cache (Redis)
       │   ├─ HIT → Return cached
       │   └─ MISS → Continue ↓
       │
       ├─> Database query (via PgBouncer)
       │   │
       │   ├─> PgBouncer:6432 (connection pool)
       │   │   └─> PostgreSQL:5432
       │   │       ├─> Execute query
       │   │       └─> Return result
       │   │
       │   └─> Cache result (Redis, 5 min TTL)
       │
       └─> Return response
```

**Total Latency Breakdown:**
- Cloudflare cache HIT: ~10-50ms (edge location)
- Nginx cache HIT: ~5-20ms (server)
- Redis cache HIT: ~1-5ms
- Database query: ~10-100ms
- **Average API call:** ~50-150ms
- **P99 API call:** <500ms

---

## Memory Allocation Strategy

```
TOTAL RAM: 16GB (16,384 MB)
├── SYSTEM RESERVED: ~3GB
│   ├── OS kernel: ~500MB
│   ├── System processes: ~1GB
│   ├── Disk cache: ~1.5GB
│   └── Buffer: ~1GB (safety)
│
└── DOCKER CONTAINERS: ~11GB
    ├── PostgreSQL: 1536MB (1.5GB)
    │   └── shared_buffers: 2GB inside container
    ├── Redis: 2048MB (2GB)
    ├── PgBouncer: 128MB
    ├── App API: 1536MB
    ├── Studio API: 1536MB
    ├── Voice Service: 1536MB
    ├── Realtime Service: 512MB
    ├── App Frontend: 384MB
    ├── Studio Frontend: 512MB
    ├── Prometheus: 512MB
    ├── cAdvisor: 256MB
    └── Exporters (5×): 640MB (128MB each)
    
ACTUAL USAGE (typical): ~9GB
BUFFER FOR SPIKES: ~2GB
SYSTEM OVERHEAD: ~3GB
────────────────────────
SAFE OPERATION: ✅
```

---

## Network Flow

```
EXTERNAL:
  Port 80  → Nginx → Redirect to 443
  Port 443 → Nginx → Upstreams

INTERNAL (Docker Network):
  galion-app-frontend:3000    → Users see :3001
  galion-app-api:8000         → Users see :8001
  galion-studio-frontend:3000 → Users see :3003
  galion-studio-api:8000      → Users see :8003
  galion-voice:8000           → Users see :8002
  galion-realtime:8000        → Users see :8004
  
DATABASES (Localhost only):
  postgres:5432    → 127.0.0.1:5432
  pgbouncer:6432   → 127.0.0.1:6432
  redis:6379       → 127.0.0.1:6379
  
MONITORING (Localhost only):
  prometheus:9090  → 127.0.0.1:9090
  node-exporter:9100
  postgres-exporter:9187
  redis-exporter:9121
  cadvisor:8080
  nginx-exporter:9113
```

**Security:** All database and monitoring ports are localhost-only.

---

## Data Flow

### Write Operations (Create/Update/Delete)

```
User Request
   ↓
API (validate, authorize)
   ↓
Database (via PgBouncer)
   ↓
Write to PostgreSQL
   ↓
Invalidate cache (Redis)
   ↓
Return success
   ↓
Publish event (optional, for real-time)
```

### Read Operations (GET requests)

```
User Request
   ↓
API (validate, authorize)
   ↓
Check Redis cache
   ├─ HIT → Return immediately (1-5ms)
   └─ MISS ↓
      ↓
Query Database (via PgBouncer)
      ↓
PostgreSQL executes query
      ↓
Cache result in Redis
      ↓
Return to user
```

**Cache Layers:**
1. Cloudflare Edge (global, CDN)
2. Nginx Proxy (server, 1.5GB)
3. Redis (application, 2GB)
4. PostgreSQL (database, internal caching)

---

## Scaling Evolution

### Phase 1: Single Server (Current)
```
[TITANAXE 16GB]
  • All services
  • 500-1K users
  • $226/month
```

### Phase 2: Vertical Scale
```
[TITAN 32GB]
  • All services
  • 2K-3K users
  • $290/month
```

### Phase 3: Separate Database
```
[App Server 16GB]     [DB Server 32GB]
  • GALION.APP          • PostgreSQL
  • GALION.STUDIO       • Redis
  • Services            • PgBouncer
  
  3K-5K users
  $380/month
```

### Phase 4: Add Load Balancer
```
                [Hetzner LB]
                   ↙    ↘
[App Server 1]      [App Server 2]
   16GB                16GB
    ↓                    ↓
        [DB Server 32GB]
        
  5K-8K users
  $550/month
```

### Phase 5: Add Read Replica
```
              [Hetzner LB]
                 ↙    ↘
[App Server 1]    [App Server 2]
     ↓                 ↓
     └─────┬───────────┘
           ↓
    [DB Primary 32GB]
           │
    (Replication)
           ↓
    [DB Replica 32GB]
    (Read queries)
    
  8K-15K users
  $700/month
```

---

## Security Layers

```
LAYER 1: CLOUDFLARE
├── DDoS Protection (L3/L4/L7)
├── Bot Protection
├── IP Blocking
├── Rate Limiting
└── WAF Rules

LAYER 2: UFW FIREWALL
├── Port 22 (SSH) - Key auth only
├── Port 80 (HTTP) - Redirects to 443
├── Port 443 (HTTPS) - SSL/TLS
└── All other ports: BLOCKED

LAYER 3: FAIL2BAN
├── SSH brute force protection
├── Nginx auth failure detection
├── Bad bot detection
├── Proxy attempt blocking
└── Auto-ban for 1-7 days

LAYER 4: NGINX
├── Rate limiting (IP-based)
├── Connection limits
├── Request size limits
├── Security headers
└── SSL/TLS hardening

LAYER 5: APPLICATION
├── JWT authentication
├── Input validation
├── SQL injection prevention
├── XSS protection
├── CSRF protection
└── Rate limiting (Redis-backed)

LAYER 6: DATABASE
├── Password authentication
├── Connection limits (200 max)
├── Localhost-only access
├── Row-level security (future)
└── Audit logging
```

**Defense in Depth:** 6 layers of security

---

## Backup Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKUP ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CONTINUOUS (Real-time)                                     │
│  └─> WAL Archiving                                          │
│      ├─ PostgreSQL writes WAL files                         │
│      ├─ Archived to /backups/wal_archive/                  │
│      └─ Enables Point-in-Time Recovery                      │
│                                                             │
│  DAILY (Automated - 2 AM)                                   │
│  └─> Full Database Backup                                   │
│      ├─ Both databases (galion + galion_studio)            │
│      ├─ Compressed (gzip)                                   │
│      ├─ 30-day retention                                    │
│      └─ Stored locally + uploaded to Backblaze B2          │
│                                                             │
│  WEEKLY (Sunday midnight)                                   │
│  └─> Base Backup (for PITR)                                │
│      ├─ pg_basebackup (binary format)                       │
│      ├─ Compressed and archived                             │
│      └─ Foundation for incremental restores                 │
│                                                             │
│  STORAGE LOCATIONS:                                         │
│  ├─ Local: /home/deploy/galion/backups/                   │
│  ├─ WAL Archive: /home/deploy/galion/backups/wal_archive/ │
│  └─ Off-site: Backblaze B2 (b2://galion-backups/)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

RECOVERY CAPABILITIES:
├── Standard Restore: Latest backup (RPO: 24 hours)
├── PITR: Any point in time (RPO: 5 minutes)
└── RTO: 30-120 minutes depending on method
```

---

## Caching Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  3-LAYER CACHING SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 1: CLOUDFLARE CDN (Edge)                             │
│  ├─ Static assets: 7-30 days TTL                           │
│  ├─ Global edge locations                                   │
│  ├─ Unlimited bandwidth (free tier)                         │
│  └─ Hit rate target: >90% for static                        │
│                                                             │
│  LAYER 2: NGINX PROXY CACHE (Server)                        │
│  ├─ API responses: 1-60 min TTL                            │
│  ├─ Static assets: 7 days TTL                              │
│  ├─ Size: 1.5GB (1GB API + 500MB static)                   │
│  └─ Hit rate target: >50% for API                           │
│                                                             │
│  LAYER 3: REDIS (Application)                               │
│  ├─ Session data: 24 hours TTL                             │
│  ├─ User profiles: 5 minutes TTL                           │
│  ├─ Query results: 1-5 minutes TTL                         │
│  ├─ Real-time data: 30 seconds TTL                         │
│  ├─ Size: 2GB                                               │
│  └─ Hit rate target: >70%                                   │
│                                                             │
│  CACHE INVALIDATION:                                        │
│  ├─ On data update → Invalidate Redis                      │
│  ├─ On deployment → Clear application cache                 │
│  └─ On config change → Clear all caches                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EXPECTED PERFORMANCE:
├── Cache HIT: 1-50ms (depending on layer)
├── Cache MISS: 50-200ms (database query)
└── Overall cache hit rate: 70-80%
```

---

## Resource Allocation by Function

```
COMPUTE (CPU):
├── API Services (app + studio): 40%
├── Voice Processing: 25%
├── Database: 20%
├── Nginx: 5%
├── Redis: 5%
└── Monitoring: 5%

MEMORY (RAM):
├── Applications: 6.5GB (59%)
├── Database: 1.5GB (14%)
├── Redis: 2GB (18%)
├── Monitoring: 1GB (9%)
└── System: 3GB buffer

STORAGE (Disk):
├── PostgreSQL data: 20-30GB
├── Redis persistence: 2-4GB
├── Docker images: 10-15GB
├── Backups: 20-30GB
├── Logs: 2-5GB
└── Available: 30-40GB
```

---

## Horizontal Scaling Architecture (Future)

### When You Need to Scale Beyond 16GB

```
                    [Hetzner Load Balancer $6/mo]
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    [Server 1]           [Server 2]           [Server 3]
   App Services         App Services         App Services
      16GB                  16GB                  16GB
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
  [DB Primary 32GB]    [DB Replica 32GB]   [DB Replica 32GB]
         │                    │                    │
   All Writes          Read Queries         Read Queries
         │                    │                    │
         └─────> Streaming Replication <──────────┘
         
CAPACITY: 10K-20K concurrent users
COST: ~$700/month (still 50% cheaper than AWS)
HIGH AVAILABILITY: Multi-server redundancy
ZERO DOWNTIME: Rolling deployments
```

---

## Monitoring Metrics Hierarchy

```
BUSINESS METRICS (What matters to users)
├── Uptime %
├── Response time
├── Error rate
├── Active users
└── Feature usage

APPLICATION METRICS (How app performs)
├── Request rate
├── Response time per endpoint
├── Error rate per endpoint
├── Cache hit rate
└── Queue lengths

INFRASTRUCTURE METRICS (Resources)
├── CPU usage %
├── Memory usage %
├── Disk I/O
├── Network I/O
└── Container health

DATABASE METRICS (Data layer)
├── Connection count
├── Query latency
├── Cache hit ratio
├── Replication lag
└── Database size

EXTERNAL METRICS (Dependencies)
├── OpenAI API latency
├── ElevenLabs API latency
├── Circuit breaker state
└── External API error rate
```

**Monitoring Philosophy:**
Start with business metrics (what users care about),  
Then drill down to infrastructure metrics (root cause).

---

## Deployment Flow

```
CODE CHANGE
   │
   ├─> git commit & push
   │
   ▼
GIT REPOSITORY (GitHub)
   │
   ├─> Webhook trigger (optional CI/CD)
   │
   ▼
VPS SERVER
   │
   ├─> ./scripts/deploy.sh
   │
   ▼
ZERO-DOWNTIME DEPLOYMENT
   │
   ├─> For each service:
   │   ├─ Build new image
   │   ├─ Start new container
   │   ├─ Wait for healthy
   │   ├─ Stop old container
   │   └─ Verify success
   │
   ▼
VERIFICATION
   │
   ├─> ./scripts/verify-deployment.sh
   ├─> Health checks
   ├─> Smoke tests
   └─> Monitor metrics
   
DONE! ✅
   
Deployment Time: 3-5 minutes
Downtime: 0 seconds
Rollback: If verification fails
```

---

## Disaster Recovery Flow

```
DISASTER OCCURS
   │
   ├─> Alerts fire (Grafana, PagerDuty)
   │
   ▼
ONCALL NOTIFIED
   │
   ├─> Assess severity
   │
   ▼
RECOVERY DECISION
   │
   ├──> Minor: Restart service (5 min)
   ├──> Moderate: Restore from backup (30 min)
   ├──> Major: PITR restore (60 min)
   └──> Critical: Migrate to new server (120 min)
   │
   ▼
EXECUTE RECOVERY
   │
   ├─> Follow docs/DISASTER_RECOVERY.md
   │
   ▼
VERIFY SYSTEM
   │
   ├─> ./scripts/verify-deployment.sh
   ├─> Test all functionality
   └─> Monitor for 24 hours
   │
   ▼
POST-MORTEM
   │
   ├─> Document incident
   ├─> Identify root cause
   ├─> Implement prevention
   └─> Update runbooks

RESOLUTION TIME:
├── P0 (Critical): <2 hours
├── P1 (High): <15 minutes
├── P2 (Medium): <1 hour
└── P3 (Low): <1 day
```

---

## Quick Command Reference

### Status Checks
```bash
docker compose ps                       # All containers
./scripts/health-check.sh               # Full health check
htop                                    # System resources
docker stats                            # Container resources
```

### Logs
```bash
docker compose logs -f                  # All logs
docker compose logs -f app-api          # Specific service
sudo tail -f /var/log/nginx/access.log  # Nginx access
sudo tail -f /var/log/nginx/error.log   # Nginx errors
```

### Deployment
```bash
./scripts/deploy.sh                     # Zero-downtime update
./scripts/full-deployment.sh            # Complete deployment
./scripts/migrate.sh                    # Database migration
```

### Backup & Restore
```bash
./scripts/backup.sh                     # Manual backup
./scripts/restore.sh BACKUP_FILE        # Restore from backup
./scripts/incremental-backup.sh setup   # Enable PITR
```

### Monitoring
```bash
curl http://localhost:9090              # Prometheus UI
# Then open in browser
```

---

## File Size Reference

```
LIGHTWEIGHT (<10KB):
├── .env.example
├── app/middleware/__init__.py
└── requirements-circuit-breaker.txt

MEDIUM (10-50KB):
├── docker-compose.yml (22KB)
├── configs/postgresql.conf (4KB)
├── monitoring/prometheus.yml (3KB)
├── monitoring/alerts.yml (5KB)
└── app/middleware/rate_limit.py (8KB)

LARGE (50-200KB):
├── nginx/nginx.conf (4KB)
├── nginx/sites-available/* (8KB total)
├── app/core/cache.py (10KB)
├── app/core/circuit_breaker.py (8KB)
├── app/api/health.py (6KB)
└── scripts/* (40KB total)

DOCUMENTATION (200KB+):
└── docs/* (200KB total)
```

**Total Repository Size:** ~500KB (excluding Docker images)

---

## Next Steps Visualization

```
YOU ARE HERE → [Documentation Complete]
                         │
                         ▼
               [Execute Deployment]
               ./scripts/full-deployment.sh
                         │
                         ▼
                    [2 Hours]
                         │
                         ▼
               [System Running] ✅
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    [Monitor]       [Optimize]      [Scale]
    Daily           Week 1-4        Month 4+
         │               │               │
         ▼               ▼               ▼
   [Grafana]     [Performance]   [More Servers]
   [Alerts]      [Caching]       [Load Balancer]
   [Logs]        [Indexes]       [Replicas]
```

---

**This is your complete reference guide.**  
**Bookmark this file.**  
**Everything you need is documented.**  
**Now go deploy!** 🚀

---

**Version:** 1.0  
**Created:** November 10, 2025  
**Status:** Complete Reference

