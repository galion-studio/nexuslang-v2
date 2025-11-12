# GALION Scaling Guide
## Horizontal and Vertical Scaling Strategies

**Version:** 1.0  
**Date:** November 10, 2025  
**Purpose:** Guide for scaling GALION infrastructure as traffic grows

---

## Current Architecture (Single Server - 16GB RAM)

```
┌─────────────────────────────────────────────────────────────┐
│                TITANAXE VPS (16GB RAM, 100GB SSD)           │
├─────────────────────────────────────────────────────────────┤
│  • GALION.APP (frontend + API + voice)                     │
│  • GALION.STUDIO (frontend + API + realtime)               │
│  • PostgreSQL (both databases)                             │
│  • Redis (caching + sessions)                              │
│  • Monitoring (Prometheus + exporters)                     │
└─────────────────────────────────────────────────────────────┘
```

**Capacity:** 500-1000 concurrent users  
**Cost:** $50/month VPS + $190/month APIs = $240/month

---

## Scaling Triggers

### When to Scale

Monitor these metrics (visible in Grafana):

**Scale Immediately If:**
- ✅ CPU usage sustained >70% for 15+ minutes
- ✅ Memory usage >85% for 10+ minutes
- ✅ API response time P99 >1s for 5+ minutes
- ✅ Database connections >80% of max (160/200)
- ✅ Redis memory >90% full (1.8GB/2GB)
- ✅ Disk I/O wait >20%
- ✅ Error rate >1% for 5+ minutes

**Scale Soon If:**
- ⚠️ Concurrent users >500
- ⚠️ Daily active users >2000
- ⚠️ Database size >20GB
- ⚠️ Average response time trending upward
- ⚠️ Cache hit rate <70%

---

## Scaling Options

### Option 1: Vertical Scaling (Easiest)

Upgrade to a bigger VPS on same provider.

**Pros:**
- No architecture changes
- Same configuration files
- Minimal downtime (5-10 minutes)
- Cheaper than horizontal scaling initially

**Cons:**
- Limited by largest server size
- Single point of failure remains
- Eventually need horizontal scaling anyway

**Cost Comparison:**

| Server | RAM | CPU | Storage | Monthly | Capacity |
|--------|-----|-----|---------|---------|----------|
| CPX41 (current) | 16GB | 8 vCPU | 240GB | $35 | 500-1K users |
| CPX51 | 32GB | 16 vCPU | 360GB | $50 | 2K-3K users |
| CPX61 | 64GB | 24 vCPU | 480GB | $100 | 5K-8K users |
| CCX63 | 128GB | 48 vCPU | 960GB | $400 | 20K+ users |

**When to Use:** First scaling step (500 → 3000 users)

**How to Scale Vertically:**

1. Create snapshot/backup:
   ```bash
   ./scripts/backup.sh
   ```

2. Purchase larger VPS (same provider)

3. Restore from backup on new server:
   ```bash
   ./scripts/restore.sh backups/galion_latest.dump.gz
   ```

4. Update DNS (if IP changes)

5. Verify everything works

---

### Option 2: Horizontal Scaling (Most Scalable)

Add more servers and load balance traffic.

**Pros:**
- No upper limit on capacity
- High availability (redundancy)
- Better performance (distributed load)
- Can scale specific components independently

**Cons:**
- More complex architecture
- Higher operational overhead
- Requires load balancer
- More expensive

**Architecture Evolution:**

#### Stage 1: Current (0-1K users) - $240/month
```
Server 1: Everything (16GB)
```

#### Stage 2: Separate Database (1K-3K users) - $330/month
```
Server 1: App servers (16GB) - $50
  • GALION.APP (frontend + API + voice)
  • GALION.STUDIO (frontend + API + realtime)
  
Server 2: Databases (32GB) - $90
  • PostgreSQL (both databases)
  • Redis
  • PgBouncer
```

**Benefits:** Database gets dedicated resources, easier to optimize

#### Stage 3: Add Load Balancer (3K-5K users) - $400/month
```
Load Balancer (Hetzner LB) - $6

Server 1: App servers (16GB) - $50
Server 2: App servers (16GB) - $50  [NEW]
Server 3: Databases (32GB) - $90
```

**Benefits:** High availability, distribute load, zero-downtime deployments

#### Stage 4: Database Read Replicas (5K-10K users) - $550/month
```
Load Balancer - $6

Server 1: App servers (32GB) - $90
Server 2: App servers (32GB) - $90
Server 3: Database Primary (32GB) - $90
Server 4: Database Replica (32GB) - $90  [NEW]
```

**Benefits:** Distribute read queries, faster queries, backup for failover

#### Stage 5: Multi-Region (10K+ users) - $1200+/month
```
Region 1 (US):
  • Load Balancer
  • 2× App servers
  • Database Primary + Replica
  
Region 2 (EU):
  • Load Balancer
  • 2× App servers
  • Database Replica (read-only)
  
Database Replication:
  • Primary in US
  • Replicas in US + EU
```

**Benefits:** Global low latency, geographic redundancy

---

## Implementation Guides

### Vertical Scaling Steps

**Preparation (30 minutes):**
1. Create full backup
2. Document current configuration
3. Test backup restore locally
4. Purchase new VPS

**Migration (1-2 hours):**
1. Stop services on old server:
   ```bash
   docker compose down
   ```

2. Create final backup:
   ```bash
   ./scripts/backup.sh
   ```

3. Copy data to new server:
   ```bash
   rsync -avz --progress /home/deploy/galion/ deploy@NEW_SERVER_IP:/home/deploy/galion/
   ```

4. Start services on new server:
   ```bash
   cd /home/deploy/galion
   docker compose up -d
   ```

5. Verify health:
   ```bash
   ./scripts/health-check.sh
   ```

6. Update DNS if IP changed

**Rollback Plan:**
- Keep old server running for 24 hours
- Can switch DNS back if issues occur

---

### Horizontal Scaling: Add Load Balancer

**Step 1: Configure Hetzner Load Balancer**

1. Go to Hetzner Cloud Console
2. Create Load Balancer:
   - Name: galion-lb
   - Location: Same as servers
   - Type: LB11 ($6/month)

3. Add Targets:
   - Server 1 (current)
   - Server 2 (new, identical setup)

4. Add Services:
   ```yaml
   Service 1:
     Protocol: HTTPS
     Port: 443
     Destination Port: 443
     Health Check:
       Protocol: HTTP
       Port: 80
       Path: /health
       Interval: 10s
   
   Service 2:
     Protocol: HTTP
     Port: 80
     Destination Port: 80
   ```

5. Point DNS to Load Balancer IP (not server IP)

**Step 2: Configure Servers for Load Balancer**

Both servers need identical configuration:

1. Same `.env` file
2. Same code version
3. Connected to same database server
4. No local state (all state in DB/Redis)

**Step 3: Session Affinity**

Configure sticky sessions in load balancer:
- Use cookie: `galion_session_id`
- Ensures user stays on same server during session

---

### Horizontal Scaling: Database Replication

**Step 1: Configure Primary Database**

On Server 3 (Database Primary):

1. Update `postgresql.conf`:
   ```bash
   cp configs/postgresql-primary.conf /path/to/postgres/data/
   ```

2. Configure replication user:
   ```sql
   CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';
   ```

3. Update `pg_hba.conf`:
   ```
   # Allow replication connections
   host replication replicator 10.0.0.0/8 md5
   ```

4. Restart PostgreSQL:
   ```bash
   docker compose restart postgres
   ```

**Step 2: Set Up Replica**

On Server 4 (Database Replica):

1. Stop PostgreSQL if running

2. Remove existing data:
   ```bash
   rm -rf data/postgres/*
   ```

3. Create base backup from primary:
   ```bash
   pg_basebackup -h PRIMARY_IP -U replicator -D data/postgres/pgdata -P -R
   ```

4. Start PostgreSQL:
   ```bash
   docker compose up -d postgres
   ```

5. Verify replication:
   ```sql
   -- On primary
   SELECT * FROM pg_stat_replication;
   
   -- On replica
   SELECT pg_is_in_recovery();  -- Should return true
   ```

**Step 3: Configure Apps to Use Replica**

Update app configuration to use read replica for read queries:

```python
# database.py
from sqlalchemy import create_engine

# Primary database (write operations)
engine_primary = create_engine(DATABASE_URL_PRIMARY)

# Replica database (read operations)
engine_replica = create_engine(DATABASE_URL_REPLICA)

# Use replica for read-only queries
async def get_user(user_id: str):
    async with engine_replica.begin() as conn:
        result = await conn.execute(...)
        return result

# Use primary for writes
async def update_user(user_id: str, data: dict):
    async with engine_primary.begin() as conn:
        result = await conn.execute(...)
        return result
```

---

## Cost-Benefit Analysis

### Vertical Scaling Costs

| Stage | Server | RAM | Monthly | Total with APIs | Break-even Users |
|-------|--------|-----|---------|-----------------|------------------|
| Current | CPX41 | 16GB | $35 | $225 | 500 |
| Scale 1 | CPX51 | 32GB | $50 | $240 | 2000 |
| Scale 2 | CPX61 | 64GB | $100 | $290 | 5000 |
| Scale 3 | CCX63 | 128GB | $400 | $590 | 20000 |

### Horizontal Scaling Costs

| Components | Monthly | Total with APIs | Capacity |
|------------|---------|-----------------|----------|
| 2× App (16GB) + 1× DB (32GB) + LB | $156 | $346 | 3000 users |
| 2× App (32GB) + 1× DB (32GB) + 1× Replica + LB | $276 | $466 | 8000 users |
| 4× App (32GB) + 2× DB (64GB) + LB | $456 | $646 | 15000 users |

**Recommendation:** 
- Use vertical scaling until you hit CPX61 limits (~5K users)
- Then switch to horizontal scaling for better HA and performance

---

## Monitoring Scaling Needs

### Dashboard to Watch

Create Grafana dashboard with these panels:

**System Resources:**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network I/O

**Application Metrics:**
- Requests per second
- Response time (P50, P95, P99)
- Error rate (%)
- Active users

**Database Metrics:**
- Connection count
- Query latency
- Cache hit ratio
- Replication lag (when using replicas)

**Business Metrics:**
- Daily active users (DAU)
- Monthly active users (MAU)
- Concurrent users
- API calls per user

### Automated Scaling Alerts

Set up alerts in Grafana (already configured in `monitoring/alerts.yml`):

- "HighCPUUsage" → Consider scaling
- "HighMemoryUsage" → Consider scaling
- "DatabaseConnectionsHigh" → Add PgBouncer or scale DB
- "HighAPILatency" → Optimize or scale
- "HighConcurrentUsers" → Scale soon

---

## Scaling Checklist

### Before Scaling
- [ ] Review current metrics (CPU, memory, latency)
- [ ] Identify bottlenecks (CPU, memory, DB, network)
- [ ] Create full backup
- [ ] Test backup restore
- [ ] Document current configuration
- [ ] Estimate new capacity requirements
- [ ] Calculate costs
- [ ] Plan rollback strategy

### During Scaling
- [ ] Announce maintenance window (if needed)
- [ ] Create backups
- [ ] Provision new resources
- [ ] Configure new servers
- [ ] Test new setup
- [ ] Switch traffic (DNS or load balancer)
- [ ] Monitor closely for 24 hours

### After Scaling
- [ ] Verify all services healthy
- [ ] Check performance metrics improved
- [ ] Test all critical user paths
- [ ] Update documentation
- [ ] Remove old resources (after 7 days)
- [ ] Review costs

---

## Stateless Design Principles

For horizontal scaling to work, ensure:

**✅ DO:**
- Store sessions in Redis (not in-memory)
- Store files in shared storage (S3 or shared volume)
- Use database for all persistent data
- Use external cache (Redis), not local cache
- Generate idempotent API operations
- Use database transactions properly

**❌ DON'T:**
- Store session data in application memory
- Use local file system for uploads
- Use in-memory caching
- Rely on server state
- Use server-side WebSocket state (use Redis pub/sub)

**Verify Statelessness:**
```bash
# Should be able to kill and restart any container
docker compose restart app-api

# Application should recover without data loss
# Sessions should persist (stored in Redis)
# No user-facing errors
```

---

## Load Balancer Configuration

When using Hetzner Load Balancer:

**Algorithm:** Least Connections
- Distributes load based on active connections
- Better than round-robin for varying request durations

**Health Checks:**
```yaml
Protocol: HTTP
Path: /health/ready
Port: 80
Interval: 10s
Timeout: 5s
Retries: 3
```

**Sticky Sessions:** Enable
- Cookie name: `galion_lb`
- Ensures user stays on same server
- Important for WebSocket connections

---

## Database Scaling Strategies

### Strategy 1: Vertical Scaling
Upgrade database server (16GB → 32GB → 64GB)

**Good for:** Up to 50K active users

### Strategy 2: Read Replicas
Add read-only replica servers

**Good for:** Read-heavy workloads (90%+ reads)

**Implementation:**
```python
# Use replica for reads
users = await db_replica.query("SELECT * FROM users")

# Use primary for writes
await db_primary.execute("INSERT INTO users ...")
```

### Strategy 3: Database Sharding
Split data across multiple databases

**Good for:** 100K+ users, multi-tenant SaaS

**Example Sharding:**
- Shard 1: Users A-M
- Shard 2: Users N-Z

**Complex, only do if absolutely necessary!**

### Strategy 4: Managed Database (Hybrid)
Move to managed PostgreSQL while keeping app on VPS

**Providers:**
- Hetzner Managed PostgreSQL: $20-200/month
- DigitalOcean Managed Database: $15-280/month
- AWS RDS: $25-500/month

**Pros:** Automated backups, updates, monitoring  
**Cons:** More expensive, less control

---

## Cost Projections

### Year 1 Growth Scenario

| Month | Users | Architecture | Monthly Cost | Cumulative |
|-------|-------|--------------|--------------|------------|
| 1-3 | 0-500 | Single 16GB VPS | $240 | $720 |
| 4-6 | 500-2K | Single 32GB VPS | $290 | $1,590 |
| 7-9 | 2K-5K | 32GB VPS + DB | $380 | $2,730 |
| 10-12 | 5K-10K | 2× App + DB + Replica | $550 | $4,380 |

**Year 1 Total Infrastructure Cost:** $4,380

Compare to AWS: ~$18,000 for same capacity  
**Savings:** $13,620 (76%)

---

## Performance Optimization Before Scaling

Before adding servers, optimize what you have:

### 1. Database Optimization
- [ ] Add missing indexes (run `scripts/optimize-db.sql`)
- [ ] Optimize slow queries (check `log_min_duration_statement`)
- [ ] Increase shared_buffers if memory available
- [ ] Tune work_mem for complex queries
- [ ] Enable connection pooling (PgBouncer)

### 2. Application Optimization
- [ ] Add caching (Redis) for expensive queries
- [ ] Implement pagination for list endpoints
- [ ] Use async operations where possible
- [ ] Optimize N+1 queries (eager loading)
- [ ] Add database query result caching
- [ ] Profile code for bottlenecks

### 3. Frontend Optimization
- [ ] Enable code splitting
- [ ] Lazy load components
- [ ] Optimize images (WebP, compress)
- [ ] Use CDN for static assets (Cloudflare)
- [ ] Minify JS/CSS
- [ ] Enable service worker caching

### 4. Infrastructure Optimization
- [ ] Increase Nginx worker_connections
- [ ] Enable HTTP/2 and HTTP/3
- [ ] Configure response caching
- [ ] Enable compression (gzip, brotli)
- [ ] Tune kernel parameters (sysctl)

**Rule of Thumb:** 
Optimization can often double your capacity for $0 cost.  
Always optimize before scaling!

---

## Testing Scaled Architecture

After scaling, run these tests:

### 1. Load Test
```bash
k6 run --vus 500 --duration 10m tests/load/api-test.js
```

### 2. Stress Test
```bash
k6 run tests/load/stress-test.js
```

### 3. Failover Test
```bash
# Kill one app server
docker compose stop app-api

# Verify app still works (load balancer redirects traffic)
curl https://api.galion.app/health

# Bring server back up
docker compose up -d app-api
```

### 4. Database Failover Test
```bash
# Promote replica to primary
docker compose exec postgres-replica psql -c "SELECT pg_promote();"

# Update app configuration to use new primary
# Verify writes work
```

---

## Emergency Scaling Procedures

### If Server is Overloaded RIGHT NOW:

**Quick fixes (5 minutes):**
```bash
# 1. Restart services to clear memory leaks
docker compose restart app-api studio-api

# 2. Clear unnecessary data
docker system prune -a -f

# 3. Enable aggressive caching in Nginx
# Edit nginx.conf, increase cache sizes

# 4. Enable Cloudflare "Under Attack Mode"
# Challenges all visitors before allowing access
```

**Medium-term (1 hour):**
- Upgrade to larger VPS
- Enable CDN caching aggressively
- Add rate limiting

**Long-term (1 day):**
- Add second app server
- Set up load balancer
- Database optimization

---

## Scaling Decision Tree

```
Is performance degraded?
├─ YES → Continue
└─ NO  → Don't scale yet, monitor

Is CPU or Memory at >80%?
├─ YES → Vertical scaling (upgrade VPS)
└─ NO  → Continue

Is database the bottleneck?
├─ YES → Separate database server or read replicas
└─ NO  → Continue

Are you serving global traffic?
├─ YES → Multi-region deployment
└─ NO  → Horizontal scaling (load balancer + multiple app servers)

Have you optimized code first?
├─ NO  → Optimize before scaling!
└─ YES → Proceed with scaling
```

---

## Key Takeaways

1. **Monitor First:** Use Grafana to identify actual bottlenecks
2. **Optimize Before Scaling:** Can double capacity for free
3. **Vertical First:** Easier, cheaper for <5K users
4. **Horizontal Later:** When you need HA or >5K users
5. **Test Everything:** Load tests, failover tests
6. **Plan Rollback:** Always have a way back
7. **Document Changes:** Update architecture docs
8. **Monitor After:** Watch metrics closely for 48 hours

---

**Remember: Premature optimization is the root of all evil.**  
**But premature scaling is expensive and complex.**  
**Scale when data says you should, not when fear says you might.**

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Next Review:** When reaching 500 concurrent users

