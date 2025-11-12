...
# GALION Operations Runbook
## Day-to-Day Operations Guide for Production

**Version:** 1.0  
**Date:** November 10, 2025  
**Audience:** DevOps, SRE, Oncall Engineers

---

## Quick Reference

### Essential Commands
```bash
# Check status
docker compose ps
./scripts/health-check.sh

# View logs
docker compose logs -f [service-name]

# Restart service
docker compose restart [service-name]

# Deploy updates
./scripts/deploy.sh

# Run backup
./scripts/backup.sh

# Check resources
htop
docker stats
```

### Service Ports
- App API: 8001
- Studio API: 8003
- Voice Service: 8002
- Realtime Service: 8004
- App Frontend: 3001
- Studio Frontend: 3003
- PostgreSQL: 5432
- PgBouncer: 6432
- Redis: 6379
- Prometheus: 9090

### Important URLs
- App: https://galion.app
- Studio: https://studio.galion.app
- Prometheus: http://YOUR_IP:9090
- Grafana: https://grafana.com

---

## Daily Checks (5 minutes)

Run every morning:

```bash
# 1. Check all services are running
docker compose ps

# 2. Check system resources
free -h
df -h

# 3. Check last night's backup
ls -lht backups/ | head -3

# 4. Check for errors in logs
docker compose logs --since 24h | grep -i error | tail -20

# 5. Check Grafana for alerts
# Visit Grafana dashboard, check for red alerts
```

**Expected Results:**
- All containers show "Up" status
- Memory usage < 85%
- Disk usage < 80%
- Backup completed successfully
- No critical errors in logs
- No active alerts in Grafana

---

## Weekly Maintenance (15 minutes)

Run every Sunday:

```bash
# 1. Update system packages
sudo apt update && sudo apt list --upgradable

# 2. Clean Docker resources
docker system prune -f

# 3. Test backup restore
./scripts/restore.sh backups/galion_latest.dump.gz

# 4. Review slow queries
docker compose exec postgres psql -U galion -d galion -c "
  SELECT query, calls, mean_exec_time, max_exec_time 
  FROM pg_stat_statements 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;"

# 5. Check SSL certificate expiry
sudo certbot certificates

# 6. Review security logs
sudo fail2ban-client status
sudo tail -100 /var/log/auth.log | grep "Failed password"

# 7. Update documentation if needed
```

---

## Monthly Tasks (30 minutes)

Run first Monday of each month:

```bash
# 1. Security audit
sudo rkhunter --check
sudo lynis audit system

# 2. Performance review
# Check Grafana dashboards for trends:
# - Average response times
# - Error rates
# - Resource usage
# - User growth

# 3. Database maintenance
docker compose exec postgres psql -U galion -d galion -c "VACUUM ANALYZE;"
docker compose exec postgres psql -U galion -d galion_studio -c "VACUUM ANALYZE;"

# 4. Review and optimize costs
# Check if resource usage justifies current server size

# 5. Update dependencies
# Review and update Docker images
# Review and update Python/Node packages

# 6. Test disaster recovery
# Run full restore from backup on test environment

# 7. Review and update runbooks
```

---

## Common Issues & Solutions

### Issue: Service Won't Start

**Symptoms:** Container exits immediately or shows "Restarting"

**Diagnosis:**
```bash
# Check logs
docker compose logs [service-name]

# Check recent changes
git log --oneline -10

# Check disk space
df -h
```

**Solutions:**
1. **Out of memory:**
   ```bash
   docker compose restart [service-name]
   # If persists, increase memory limit in docker-compose.yml
   ```

2. **Database connection failed:**
   ```bash
   # Check if PostgreSQL is running
   docker compose ps postgres
   
   # Check DATABASE_URL in .env
   cat .env | grep DATABASE_URL
   
   # Test connection
   docker compose exec postgres psql -U galion -c "SELECT 1;"
   ```

3. **Missing environment variable:**
   ```bash
   # Check for required variables
   docker compose config | grep "not set"
   
   # Add missing variables to .env
   nano .env
   ```

### Issue: High Memory Usage

**Symptoms:** Memory >85%, services slow or OOM killed

**Diagnosis:**
```bash
# Check overall memory
free -h

# Check per-container memory
docker stats

# Find memory hogs
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -h -r
```

**Solutions:**
1. **Restart memory-leaking service:**
   ```bash
   docker compose restart [service-name]
   ```

2. **Clear Redis cache:**
   ```bash
   docker compose exec redis redis-cli FLUSHDB
   ```

3. **Reduce PostgreSQL memory:**
   ```bash
   # Edit configs/postgresql.conf
   # Reduce shared_buffers from 2GB to 1.5GB
   docker compose restart postgres
   ```

4. **Scale vertically:**
   ```bash
   # Upgrade to bigger VPS
   # See docs/SCALING_GUIDE.md
   ```

### Issue: Database Connection Pool Exhausted

**Symptoms:** "Too many connections" errors

**Diagnosis:**
```bash
# Check active connections
docker compose exec postgres psql -U galion -c "
  SELECT count(*) as connections, state 
  FROM pg_stat_activity 
  GROUP BY state;"

# Check PgBouncer pools
docker compose exec pgbouncer psql -h 127.0.0.1 -p 6432 -U galion -d pgbouncer -c "SHOW POOLS;"
```

**Solutions:**
1. **Increase PgBouncer pool size:**
   ```bash
   # Edit configs/pgbouncer.ini
   # Increase default_pool_size from 25 to 50
   docker compose restart pgbouncer
   ```

2. **Kill idle connections:**
   ```bash
   docker compose exec postgres psql -U galion -c "
     SELECT pg_terminate_backend(pid) 
     FROM pg_stat_activity 
     WHERE state = 'idle' 
     AND state_change < now() - interval '10 minutes';"
   ```

3. **Fix connection leaks in code:**
   ```python
   # Always use connection context managers
   async with engine.begin() as conn:
       result = await conn.execute(...)
   # Connection automatically closed
   ```

### Issue: High API Latency

**Symptoms:** API responses >500ms, user complaints

**Diagnosis:**
```bash
# Check Grafana for P99 latency

# Check slow queries
docker compose exec postgres psql -U galion -d galion -c "
  SELECT query, calls, mean_exec_time, max_exec_time 
  FROM pg_stat_statements 
  WHERE mean_exec_time > 100 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;"

# Check Redis hit rate
docker compose exec redis redis-cli info stats | grep keyspace
```

**Solutions:**
1. **Add missing indexes:**
   ```bash
   # Run optimization script
   docker compose exec -T postgres psql -U galion -d galion < scripts/optimize-db.sql
   ```

2. **Increase cache TTLs:**
   ```python
   # In app/core/cache.py
   @cache_response(ttl=600)  # Increase from 300 to 600 seconds
   ```

3. **Add query result caching:**
   ```python
   from app.core.cache import cache_response
   
   @cache_response(ttl=300, key_prefix="users")
   async def get_user(user_id: str):
       # Query will be cached for 5 minutes
       return await db.query(...)
   ```

### Issue: Out of Disk Space

**Symptoms:** Services crash, "No space left" errors

**Diagnosis:**
```bash
# Check disk usage
df -h

# Find large files
du -sh /home/deploy/galion/* | sort -h | tail -10

# Check Docker disk usage
docker system df
```

**Solutions:**
1. **Clean Docker:**
   ```bash
   docker system prune -a --volumes -f
   ```

2. **Clean old backups:**
   ```bash
   # Keep only last 7 days
   find backups/ -name "*.dump.gz" -mtime +7 -delete
   ```

3. **Clean logs:**
   ```bash
   # Truncate large log files
   sudo journalctl --vacuum-time=7d
   sudo truncate -s 0 /var/log/nginx/*.log
   ```

4. **Rotate logs:**
   ```bash
   # Already configured in docker-compose.yml
   # Logs limited to 10MB × 3 files per container
   ```

### Issue: SSL Certificate Expired

**Symptoms:** Browser shows "Certificate expired" error

**Diagnosis:**
```bash
# Check certificate status
sudo certbot certificates

# Check expiry date
echo | openssl s_client -servername galion.app -connect galion.app:443 2>/dev/null | openssl x509 -noout -dates
```

**Solutions:**
```bash
# Renew certificates
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx

# Verify
curl -I https://galion.app
```

**Prevention:** Certbot auto-renewal runs daily via systemd timer

---

## Incident Response

### Severity Levels

**P0 - Critical (Response: Immediate)**
- Complete site outage
- Data loss
- Security breach

**P1 - High (Response: <15 min)**
- Partial outage
- High error rate (>5%)
- Performance degradation (>2s response)

**P2 - Medium (Response: <1 hour)**
- Single service down (with redundancy)
- Moderate performance issues
- Non-critical feature broken

**P3 - Low (Response: <1 day)**
- Minor bugs
- Cosmetic issues
- Enhancement requests

### Incident Response Steps

**1. Acknowledge (1 minute)**
```bash
# Check Grafana alerts
# Acknowledge in Slack/PagerDuty
# Post in incident channel
```

**2. Assess (2 minutes)**
```bash
# Run health check
./scripts/health-check.sh

# Check what changed recently
git log --since="1 hour ago"

# Check metrics
# CPU, memory, disk, error rate
```

**3. Mitigate (5-30 minutes)**
```bash
# Restart failing service
docker compose restart [service-name]

# If database issue, restart DB
docker compose restart postgres

# If under attack, enable Cloudflare "Under Attack Mode"

# If out of resources, scale up
```

**4. Resolve (varies)**
```bash
# Fix root cause
# Deploy fix if needed
./scripts/deploy.sh

# Verify fix
./scripts/verify-deployment.sh
```

**5. Document (15 minutes)**
```bash
# Create post-mortem
# Document in docs/incidents/YYYY-MM-DD-incident-name.md
# Share learnings with team
```

---

## Oncall Playbook

### On Taking Oncall
- [ ] Test SSH access to server
- [ ] Verify you can access Grafana
- [ ] Review recent changes/deployments
- [ ] Check current system health
- [ ] Read any handover notes

### During Oncall
- [ ] Monitor Slack for alerts
- [ ] Check Grafana dashboards daily
- [ ] Be available for incidents
- [ ] Document any issues encountered

### On Handing Off Oncall
- [ ] Document any ongoing issues
- [ ] Share any workarounds implemented
- [ ] Update runbook if you learned something new
- [ ] Brief next oncall engineer

---

## Monitoring & Alerts

### Grafana Dashboards

**System Overview:**
- CPU usage (all cores)
- Memory usage
- Disk I/O
- Network traffic

**Application Metrics:**
- Request rate (req/s)
- Error rate (%)
- Response time (P50, P95, P99)
- Active users

**Database Metrics:**
- Connections (active/idle)
- Query latency
- Cache hit ratio
- Replication lag

**Business Metrics:**
- New user registrations
- Active users (1h, 24h, 7d)
- API calls per endpoint
- Voice interactions

### Alert Priority

**Critical (P0) - Page immediately:**
- API down >1 minute
- Database down >1 minute
- Memory >95%
- Disk space <5%

**Warning (P1) - Slack notification:**
- API latency >1s
- Error rate >1%
- Memory >85%
- Disk space <15%
- Database connections >80%

**Info - Email/dashboard only:**
- High concurrent users (scaling trigger)
- Low cache hit rate
- Unusual traffic patterns

---

## Performance Optimization

### Quick Wins

**1. Add missing indexes:**
```bash
# Run optimization script
docker compose exec -T postgres psql -U galion -d galion < scripts/optimize-db.sql
```

**2. Increase cache TTLs:**
```bash
# Edit app/core/cache.py
# Increase TTL for stable data
```

**3. Enable more aggressive caching in Nginx:**
```nginx
# Edit nginx/*.conf
# Increase proxy_cache_valid times
```

**4. Optimize database queries:**
```bash
# Find N+1 queries
# Add eager loading
# Use select_related() / prefetch_related()
```

### When to Optimize

Optimize if:
- Average response time trending upward
- Cache hit rate <70%
- Database CPU >60%
- Slow query count increasing

Don't optimize if:
- Performance is acceptable
- No user complaints
- Resources not constrained

**Rule:** Measure first, optimize second.

---

## Backup & Recovery

### Daily Backups

Automated via cron:
```bash
# Runs daily at 2 AM
0 2 * * * /home/deploy/galion/scripts/backup.sh
```

Verify backups:
```bash
# Check last backup
ls -lht backups/*.dump.gz | head -1

# Should be <24 hours old
```

### Manual Backup

```bash
# Create immediate backup
./scripts/backup.sh

# Verify backup
ls -lh backups/
```

### Restore from Backup

```bash
# List available backups
ls -lht backups/*.dump.gz

# Restore specific backup
./scripts/restore.sh backups/galion_20251110_020000.dump.gz

# Verify data
docker compose exec postgres psql -U galion -d galion -c "SELECT COUNT(*) FROM users;"
```

### Point-in-Time Recovery

```bash
# Restore to specific timestamp
./scripts/restore-pitr.sh "2025-11-10 14:30:00"

# Requires: Incremental backups configured
# Setup: ./scripts/incremental-backup.sh setup
```

---

## Deployment Procedures

### Regular Deployment (Zero Downtime)

```bash
# 1. Pull latest code
cd /home/deploy/galion
git pull origin main

# 2. Run deployment script
./scripts/deploy.sh

# 3. Verify deployment
./scripts/verify-deployment.sh

# 4. Monitor for 1 hour
# Watch Grafana for anomalies
```

### Emergency Rollback

```bash
# 1. Check previous image
docker images | grep galion-app-api

# 2. Tag old version as latest
docker tag galion-app-api:old galion-app-api:latest

# 3. Restart with old image
docker compose up -d --no-deps app-api

# 4. Verify
curl http://localhost:8001/health
```

### Database Migration

```bash
# 1. Create backup
./scripts/backup.sh

# 2. Run migration
./scripts/migrate.sh

# 3. Verify schema
docker compose exec postgres psql -U galion -d galion -c "\dt"

# 4. Test application
./scripts/verify-deployment.sh
```

---

## Scaling Operations

### Vertical Scaling (Upgrade Server)

See `docs/SCALING_GUIDE.md` for detailed steps.

**Quick version:**
```bash
# 1. Backup everything
./scripts/backup.sh

# 2. Provision new larger VPS

# 3. Sync data
rsync -avz /home/deploy/galion/ deploy@NEW_IP:/home/deploy/galion/

# 4. Start services on new server
ssh deploy@NEW_IP
cd galion
docker compose up -d

# 5. Update DNS

# 6. Monitor for 24 hours

# 7. Decommission old server
```

### Horizontal Scaling (Add Server)

See `docs/SCALING_GUIDE.md` for detailed steps.

**Quick version:**
```bash
# 1. Provision new server (identical to current)

# 2. Deploy same configuration
# Copy .env, configs, code

# 3. Start services
docker compose up -d

# 4. Add to load balancer
# Configure in Hetzner Cloud Console

# 5. Monitor traffic distribution
```

---

## Security Operations

### Review Access Logs

```bash
# Check for suspicious activity
sudo tail -1000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# Check for failed login attempts
docker compose logs auth-service | grep "Login failed"

# Check fail2ban status
sudo fail2ban-client status sshd
```

### Update Security Rules

```bash
# Update fail2ban configuration
sudo nano /etc/fail2ban/jail.d/nginx.conf
sudo systemctl restart fail2ban

# Update Cloudflare firewall rules
# Via Cloudflare dashboard

# Update rate limits
# Edit nginx/*.conf or app/middleware/rate_limit.py
```

### Security Incident Response

**If you suspect a security breach:**

1. **Isolate:**
   ```bash
   # Enable Cloudflare "Under Attack Mode"
   # Block suspicious IPs in firewall
   sudo ufw deny from SUSPICIOUS_IP
   ```

2. **Assess:**
   ```bash
   # Check access logs
   sudo tail -10000 /var/log/nginx/access.log | grep SUSPICIOUS_IP
   
   # Check for unauthorized database access
   docker compose exec postgres psql -U galion -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Contain:**
   ```bash
   # Rotate all secrets
   ./scripts/generate-secrets.sh
   
   # Force logout all users
   docker compose exec redis redis-cli FLUSHDB
   
   # Deploy new secrets
   docker compose up -d
   ```

4. **Report:**
   - Document what happened
   - Notify affected users
   - Report to authorities if required (GDPR)

---

## Useful Commands

### Docker Management

```bash
# View all containers
docker compose ps

# View logs (last 100 lines)
docker compose logs --tail=100

# Follow logs
docker compose logs -f [service-name]

# Restart specific service
docker compose restart [service-name]

# Rebuild and restart
docker compose up -d --build [service-name]

# Stop all services
docker compose down

# Start all services
docker compose up -d

# View resource usage
docker stats

# Clean up
docker system prune -a -f
```

### Database Management

```bash
# Connect to database
docker compose exec postgres psql -U galion -d galion

# Run query
docker compose exec postgres psql -U galion -d galion -c "SELECT COUNT(*) FROM users;"

# List databases
docker compose exec postgres psql -U galion -c "\l"

# List tables
docker compose exec postgres psql -U galion -d galion -c "\dt"

# Check table sizes
docker compose exec postgres psql -U galion -d galion -c "\dt+"

# Vacuum and analyze
docker compose exec postgres psql -U galion -d galion -c "VACUUM ANALYZE;"
```

### Redis Management

```bash
# Connect to Redis
docker compose exec redis redis-cli

# Check memory usage
docker compose exec redis redis-cli INFO memory

# Check keyspace
docker compose exec redis redis-cli INFO keyspace

# Get key count
docker compose exec redis redis-cli DBSIZE

# Clear all data (DANGEROUS!)
docker compose exec redis redis-cli FLUSHALL

# Clear specific database
docker compose exec redis redis-cli -n 0 FLUSHDB
```

### Nginx Management

```bash
# Test configuration
sudo nginx -t

# Reload configuration (no downtime)
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log

# Check status
sudo systemctl status nginx
```

---

## Contact Information

### Primary Oncall
- Name: [Your Name]
- Phone: [Your Phone]
- Email: [Your Email]

### Secondary Oncall
- Name: [Backup Person]
- Phone: [Backup Phone]

### Escalation
- CTO: [CTO Contact]
- Infrastructure Team: [Team Channel]

---

## Change Log

**Version 1.0 (2025-11-10):**
- Initial runbook creation
- Based on production deployment

**Updates:**
- Update this runbook as you learn
- Document new issues and solutions
- Add new procedures as needed

---

**Remember:** 
- Always backup before making changes
- Test in staging first (when you have one)
- Monitor closely after changes
- Document everything

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Next Review:** December 2025

