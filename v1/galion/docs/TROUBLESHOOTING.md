## GALION Troubleshooting Guide
## Common Issues and Solutions

**Version:** 1.0  
**Date:** November 10, 2025

---

## Quick Diagnostic Commands

```bash
# System overview
./scripts/health-check.sh

# Check all services
docker compose ps

# Check resources
htop
docker stats

# Check logs
docker compose logs --tail=100 | grep -i error
```

---

## Issue Categories

### 1. Service Won't Start

#### Problem: Container exits immediately

**Diagnosis:**
```bash
# Check exit code
docker compose ps

# View logs
docker compose logs [service-name] --tail=50

# Check configuration
docker compose config
```

**Common Causes & Solutions:**

**A. Missing environment variable:**
```bash
# Check for required vars
docker compose config | grep "not set"

# Solution: Add to .env
nano .env
# Add missing variable
docker compose up -d
```

**B. Port already in use:**
```bash
# Check what's using port
sudo netstat -tulpn | grep :8001

# Solution: Kill process or change port
sudo kill -9 PID
# Or edit docker-compose.yml to use different port
```

**C. Out of memory:**
```bash
# Check memory
free -h
docker stats

# Solution: Restart services or increase limits
docker compose restart
# Or reduce memory limits in docker-compose.yml
```

**D. Database migration failed:**
```bash
# Check migration logs
docker compose logs app-api | grep -i migration

# Solution: Rollback and fix migration
docker compose exec postgres psql -U galion -d galion -c "SELECT * FROM alembic_version;"
# Manually fix migration or rollback
```

#### Problem: Container keeps restarting

**Diagnosis:**
```bash
# Check restart count
docker inspect [container-name] | grep RestartCount

# Watch logs
docker compose logs -f [service-name]
```

**Common Causes:**

**A. Failing health check:**
```bash
# Check health endpoint
curl http://localhost:8001/health

# Solution: Fix health check logic or endpoint
```

**B. Crash loop:**
```bash
# Check for errors in startup
docker compose logs [service-name] | head -50

# Solution: Fix configuration or code issue
```

**C. Resource limits:**
```bash
# Check if hitting memory limit
docker stats [container-name]

# Solution: Increase limit in docker-compose.yml
```

---

### 2. Database Issues

#### Problem: "Too many connections"

**Diagnosis:**
```bash
# Check active connections
docker compose exec postgres psql -U galion -c "
  SELECT count(*), state 
  FROM pg_stat_activity 
  GROUP BY state;"

# Check PgBouncer pools
docker compose exec pgbouncer psql -h 127.0.0.1 -p 6432 -U galion -d pgbouncer -c "SHOW POOLS;"
```

**Solutions:**

**A. Increase PgBouncer pool:**
```bash
# Edit configs/pgbouncer.ini
# Increase default_pool_size to 50
docker compose restart pgbouncer
```

**B. Kill idle connections:**
```bash
docker compose exec postgres psql -U galion -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE state = 'idle' 
  AND state_change < now() - interval '15 minutes';"
```

**C. Fix connection leaks in code:**
- Always use context managers
- Close connections explicitly
- Use connection pooling

#### Problem: Slow queries

**Diagnosis:**
```bash
# Find slow queries
docker compose exec postgres psql -U galion -d galion -c "
  SELECT 
    substring(query, 1, 50) as query, 
    calls, 
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(max_exec_time::numeric, 2) as max_ms
  FROM pg_stat_statements 
  WHERE mean_exec_time > 100 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;"
```

**Solutions:**

**A. Add missing indexes:**
```bash
# Run optimization script
docker compose exec -T postgres psql -U galion -d galion < scripts/optimize-db.sql
```

**B. Optimize query:**
```sql
-- Use EXPLAIN ANALYZE to understand query plan
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Add covering index if needed
CREATE INDEX idx_users_email_name ON users(email, name);
```

**C. Add query caching:**
```python
from app.core.cache import cache_response

@cache_response(ttl=300)
async def get_expensive_data():
    return await db.query(...)
```

#### Problem: Database disk full

**Diagnosis:**
```bash
# Check database size
docker compose exec postgres psql -U galion -c "
  SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
  FROM pg_database 
  ORDER BY pg_database_size(pg_database.datname) DESC;"

# Check table sizes
docker compose exec postgres psql -U galion -d galion -c "\dt+"
```

**Solutions:**

**A. Run VACUUM:**
```bash
docker compose exec postgres psql -U galion -d galion -c "VACUUM FULL;"
```

**B. Delete old data:**
```sql
-- Delete old sessions (>30 days)
DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';

-- Delete old logs
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
```

**C. Archive old data:**
```bash
# Export old data to S3/B2
# Delete from main database
```

---

### 3. Redis Issues

#### Problem: Redis out of memory

**Diagnosis:**
```bash
# Check memory usage
docker compose exec redis redis-cli INFO memory | grep used_memory_human

# Check eviction count
docker compose exec redis redis-cli INFO stats | grep evicted_keys
```

**Solutions:**

**A. Increase maxmemory:**
```bash
# Edit docker-compose.yml
# Change: --maxmemory 2gb to --maxmemory 4gb
docker compose up -d redis
```

**B. Clear unnecessary data:**
```bash
# Clear specific database
docker compose exec redis redis-cli -n 0 FLUSHDB

# Check key count
docker compose exec redis redis-cli DBSIZE
```

**C. Review cache strategy:**
```python
# Reduce TTLs for less important data
# Increase TTLs only for frequently accessed data
# Use LRU eviction (already configured)
```

#### Problem: Redis connection timeouts

**Diagnosis:**
```bash
# Check Redis is responding
docker compose exec redis redis-cli PING

# Check connection count
docker compose exec redis redis-cli INFO clients
```

**Solutions:**

**A. Increase timeout:**
```python
# In Redis client configuration
redis_client = aioredis.from_url(
    redis_url,
    socket_timeout=5.0,  # Increase from 1.0
    socket_connect_timeout=5.0
)
```

**B. Restart Redis:**
```bash
docker compose restart redis
```

---

### 4. High CPU Usage

**Diagnosis:**
```bash
# Check overall CPU
htop

# Check per-container
docker stats

# Find CPU-intensive processes
top -o %CPU
```

**Solutions:**

**A. Optimize hot code paths:**
- Profile code to find bottlenecks
- Add caching for expensive operations
- Use async operations

**B. Scale horizontally:**
- Add more app servers
- Distribute load with load balancer

**C. Reduce request rate:**
- Enable more aggressive rate limiting
- Enable Cloudflare "Under Attack Mode"

---

### 5. High Memory Usage

**Diagnosis:**
```bash
# Check system memory
free -h

# Check Docker memory
docker stats --no-stream | sort -k4 -h -r

# Check for memory leaks
# Monitor memory usage over time in Grafana
```

**Solutions:**

**A. Restart leaking service:**
```bash
docker compose restart [service-name]
```

**B. Reduce memory limits:**
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Reduce from 1.5G
```

**C. Enable swap (temporary):**
```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**D. Upgrade server:**
- 16GB → 32GB VPS
- See docs/SCALING_GUIDE.md

---

### 6. Network Issues

#### Problem: Can't reach external APIs

**Diagnosis:**
```bash
# Test connectivity
docker compose exec app-api ping -c 3 8.8.8.8
docker compose exec app-api curl -I https://api.openai.com

# Check DNS
docker compose exec app-api nslookup api.openai.com
```

**Solutions:**

**A. DNS resolution issue:**
```bash
# Add to docker-compose.yml
dns:
  - 1.1.1.1
  - 8.8.8.8
```

**B. Firewall blocking:**
```bash
# Check UFW rules
sudo ufw status

# Allow outbound HTTPS
sudo ufw allow out 443/tcp
```

**C. Use circuit breakers:**
- Already implemented in app/core/circuit_breaker.py
- Will handle temporary API failures

#### Problem: WebSocket connections fail

**Diagnosis:**
```bash
# Check nginx WebSocket configuration
sudo nginx -t

# Test WebSocket
wscat -c wss://api.galion.app/ws
```

**Solutions:**

**A. Verify Nginx config:**
```nginx
# Should have:
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";
```

**B. Check Cloudflare:**
- Ensure WebSockets are enabled
- Settings → Network → WebSockets: ON

---

### 7. Performance Issues

#### Problem: Slow page load

**Diagnosis:**
```bash
# Test page load time
curl -w "@curl-format.txt" -o /dev/null -s https://galion.app

# Check Cloudflare cache hit rate
# Via Cloudflare dashboard → Analytics

# Check Nginx cache
sudo du -sh /var/cache/nginx/
```

**Solutions:**

**A. Enable more caching:**
```nginx
# In nginx config
proxy_cache_valid 200 1h;
proxy_cache_valid 404 1m;
```

**B. Optimize frontend:**
- Code splitting
- Lazy loading
- Compress images
- Use CDN for assets

**C. Enable HTTP/2 and HTTP/3:**
- Already configured in nginx
- Verify in browser DevTools

#### Problem: High API latency

**See:** "High API Latency" section in RUNBOOK.md

**Quick fixes:**
```bash
# 1. Add database indexes
./scripts/optimize-db.sql

# 2. Increase cache TTLs
# Edit app/core/cache.py

# 3. Enable query caching
# Add @cache_response decorator

# 4. Profile slow endpoints
# Use FastAPI /metrics endpoint
```

---

### 8. Deployment Failures

#### Problem: Deployment script fails

**Diagnosis:**
```bash
# Check last deployment log
tail -50 logs/deployment.log

# Check Git status
git status

# Check for uncommitted changes
git diff
```

**Solutions:**

**A. Merge conflicts:**
```bash
git fetch origin
git reset --hard origin/main
./scripts/deploy.sh
```

**B. Build failures:**
```bash
# Check Docker build logs
docker compose build --no-cache [service-name]

# Fix Dockerfile or dependencies
```

**C. Health check timeouts:**
```bash
# Increase wait time in deploy.sh
# Or fix health check endpoint
```

#### Problem: Zero-downtime deployment causes brief outage

**Cause:** Old container killed before new is ready

**Solution:**
```bash
# In scripts/deploy.sh, increase wait time:
sleep 30  # Change to 60 for slower-starting services

# Or implement proper health polling:
while ! curl -f http://localhost:8001/health/ready; do
    sleep 2
done
```

---

### 9. Monitoring Issues

#### Problem: Prometheus not scraping metrics

**Diagnosis:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.'

# Check if exporters are running
docker compose ps | grep exporter

# Test metrics endpoint
curl http://localhost:8001/metrics
```

**Solutions:**

**A. Restart Prometheus:**
```bash
docker compose restart prometheus
```

**B. Fix service metrics endpoint:**
```python
# Add prometheus-fastapi-instrumentator to requirements.txt
# In main.py:
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**C. Check network connectivity:**
```bash
# Services must be on same Docker network
docker network inspect galion-network
```

#### Problem: Grafana Cloud not receiving data

**Diagnosis:**
```bash
# Check remote_write configuration
cat monitoring/prometheus.yml | grep remote_write

# Check Prometheus logs
docker compose logs prometheus | grep remote_write
```

**Solutions:**

**A. Verify credentials:**
```bash
# Check GRAFANA_CLOUD_USERNAME and API_KEY in .env
cat .env | grep GRAFANA

# Test authentication
curl -u USER:PASSWORD https://prometheus-prod-XX.grafana.net/api/prom/push
```

**B. Check network connectivity:**
```bash
docker compose exec prometheus curl -I https://prometheus-prod-XX.grafana.net
```

---

### 10. Backup & Recovery Issues

#### Problem: Backup fails

**Diagnosis:**
```bash
# Check backup logs
tail -50 logs/backup.log

# Check disk space
df -h

# Test PostgreSQL access
docker compose exec postgres pg_dump -U galion galion | head -10
```

**Solutions:**

**A. Out of disk space:**
```bash
# Clean old backups
find backups/ -name "*.dump.gz" -mtime +30 -delete

# Clean Docker
docker system prune -a -f
```

**B. PostgreSQL not responding:**
```bash
# Restart PostgreSQL
docker compose restart postgres

# Check if healthy
docker compose exec postgres pg_isready -U galion
```

**C. Permission issues:**
```bash
# Fix permissions
sudo chown -R deploy:deploy backups/
chmod +x scripts/backup.sh
```

#### Problem: Restore fails

**Diagnosis:**
```bash
# Check if backup file exists
ls -lh backups/galion_*.dump.gz

# Test backup file integrity
gunzip -t backups/galion_latest.dump.gz
```

**Solutions:**

**A. Corrupted backup:**
```bash
# Use older backup
ls -lht backups/*.dump.gz
./scripts/restore.sh backups/galion_OLDER.dump.gz
```

**B. Database already exists:**
```bash
# Drop and recreate
docker compose exec postgres psql -U galion -c "DROP DATABASE galion;"
docker compose exec postgres psql -U galion -c "CREATE DATABASE galion;"
# Then run restore again
```

---

### 11. SSL Certificate Issues

#### Problem: Certificate expired

**Symptoms:** Browser shows "Certificate expired"

**Solution:**
```bash
# Renew immediately
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx

# Verify
curl -I https://galion.app | grep -i strict-transport
```

#### Problem: Certificate renewal fails

**Diagnosis:**
```bash
# Check Certbot logs
sudo tail -100 /var/log/letsencrypt/letsencrypt.log

# Test renewal
sudo certbot renew --dry-run
```

**Solutions:**

**A. Port 80 not accessible:**
```bash
# Check firewall
sudo ufw status

# Ensure port 80 open
sudo ufw allow 80/tcp
```

**B. Nginx config issue:**
```bash
# Ensure /.well-known/acme-challenge/ is accessible
sudo nginx -t
```

**C. Rate limit hit:**
```bash
# Let's Encrypt rate limit: 5 failures per hour
# Wait 1 hour and try again
```

---

### 12. High Load / Performance

#### Problem: Site is slow

**Diagnosis:**
```bash
# Check load average
uptime

# Check resource usage
htop

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.galion.app/health

# Check database performance
docker compose exec postgres psql -U galion -d galion -c "
  SELECT * FROM pg_stat_statements 
  ORDER BY mean_exec_time DESC 
  LIMIT 5;"
```

**Immediate Actions:**

**A. Enable Cloudflare "Under Attack Mode":**
- Log in to Cloudflare
- Toggle "Under Attack Mode" ON
- Reduces load by challenging visitors

**B. Restart services:**
```bash
docker compose restart
```

**C. Increase rate limiting:**
```bash
# Edit nginx config
# Reduce rate from 100/min to 50/min temporarily
sudo nano /etc/nginx/sites-available/galion-app
sudo nginx -s reload
```

**Long-term Solutions:**

1. Add database indexes
2. Implement caching
3. Optimize slow queries
4. Scale horizontally (add servers)
5. Upgrade to larger VPS

---

### 13. Security Issues

#### Problem: Suspicious traffic detected

**Diagnosis:**
```bash
# Check access logs
sudo tail -1000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# Check fail2ban
sudo fail2ban-client status sshd
sudo fail2ban-client status nginx-badbots

# Check for SQL injection attempts
sudo grep -i "union.*select" /var/log/nginx/access.log
```

**Solutions:**

**A. Block IP:**
```bash
# Via UFW
sudo ufw deny from SUSPICIOUS_IP

# Via Cloudflare
# Add IP to block list in Cloudflare dashboard
```

**B. Enable stricter security:**
```bash
# Cloudflare → Security Level → High
# Enable "Under Attack Mode" temporarily
```

**C. Review code for vulnerabilities:**
```bash
# Run security scan
docker run --rm -v $(pwd):/src aquasec/trivy fs /src
```

#### Problem: Unauthorized access attempt

**Response:**

1. **Isolate:**
   ```bash
   # Block IP immediately
   sudo ufw deny from ATTACKER_IP
   ```

2. **Assess damage:**
   ```bash
   # Check database for unauthorized changes
   docker compose exec postgres psql -U galion -d galion -c "
     SELECT * FROM audit_logs 
     WHERE ip_address = 'ATTACKER_IP';"
   ```

3. **Rotate secrets:**
   ```bash
   # Generate new secrets
   ./scripts/generate-secrets.sh
   
   # Force logout all users
   docker compose exec redis redis-cli FLUSHDB
   
   # Redeploy
   docker compose up -d
   ```

4. **Document and report:**
   - Create incident report
   - Notify affected users
   - Report to authorities if required

---

### 14. Deployment Rollback

#### Problem: New deployment causes issues

**Quick Rollback:**
```bash
# 1. Check previous images
docker images | grep galion

# 2. Find last working version
docker images galion-app-api --format "{{.Tag}} {{.CreatedAt}}"

# 3. Tag as latest
docker tag galion-app-api:PREVIOUS_TAG galion-app-api:latest

# 4. Restart services
docker compose up -d --no-deps app-api

# 5. Verify
curl http://localhost:8001/health
```

**Complete Rollback:**
```bash
# 1. Revert code
git log --oneline -10
git reset --hard PREVIOUS_COMMIT

# 2. Rebuild and deploy
docker compose build
docker compose up -d

# 3. Restore database if needed
./scripts/restore.sh backups/BEFORE_DEPLOYMENT.dump.gz
```

---

### 15. Email Not Sending

(If email is configured)

**Diagnosis:**
```bash
# Check SMTP settings in .env
cat .env | grep SMTP

# Test SMTP connection
docker compose exec app-api python -c "
import smtplib
try:
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    print('SMTP connection successful')
except Exception as e:
    print(f'SMTP connection failed: {e}')
"
```

**Solutions:**

**A. Wrong SMTP credentials:**
```bash
# Update .env with correct credentials
nano .env

# Restart services
docker compose restart app-api
```

**B. SMTP port blocked:**
```bash
# Test port 587
telnet smtp.gmail.com 587

# Try alternative port 465 (SSL)
```

**C. Gmail App Password:**
- Don't use regular password
- Generate App Password in Google Account settings
- Use that in SMTP_PASSWORD

---

## Emergency Procedures

### Complete System Down

**Steps:**

1. **Check if VPS is accessible:**
   ```bash
   ping 54.37.161.67
   ssh deploy@54.37.161.67
   ```

2. **If can't SSH:**
   - Log in to Hetzner console
   - Access via VNC/serial console
   - Check system logs

3. **If can SSH:**
   ```bash
   # Check services
   docker compose ps
   
   # Restart everything
   docker compose down
   docker compose up -d
   ```

4. **If still down:**
   ```bash
   # Reboot server (last resort)
   sudo reboot
   
   # Wait 2 minutes
   # SSH back in
   # Start services
   cd /home/deploy/galion
   docker compose up -d
   ```

### Database Corruption

**Steps:**

1. **Stop all services:**
   ```bash
   docker compose stop app-api studio-api
   ```

2. **Attempt repair:**
   ```bash
   docker compose exec postgres pg_ctl -D /var/lib/postgresql/data/pgdata reload
   ```

3. **If repair fails, restore from backup:**
   ```bash
   ./scripts/restore.sh backups/galion_latest.dump.gz
   ```

4. **Worst case - Point-in-time recovery:**
   ```bash
   ./scripts/restore-pitr.sh "2025-11-10 23:59:59"
   ```

---

## Getting Help

### Before Asking for Help

1. Run health check:
   ```bash
   ./scripts/health-check.sh > health-report.txt
   ```

2. Collect logs:
   ```bash
   docker compose logs --since 1h > logs-report.txt
   ```

3. Check recent changes:
   ```bash
   git log --oneline -10 > git-log.txt
   ```

4. Take screenshots of:
   - Error messages
   - Grafana dashboards
   - Resource usage (htop)

### Where to Get Help

1. **Documentation:**
   - This troubleshooting guide
   - docs/RUNBOOK.md
   - docs/SCALING_GUIDE.md

2. **Community:**
   - GitHub Issues
   - Discord server
   - Stack Overflow

3. **Professional Support:**
   - Email: support@galion.app
   - Emergency: oncall@galion.app

---

## Prevention Best Practices

### 1. Always Test Before Deploying
```bash
# Test locally
docker compose up --build

# Run tests
pytest tests/

# Load test
k6 run tests/load/api-test.js
```

### 2. Monitor Continuously
- Check Grafana daily
- Set up alerts
- Review metrics weekly

### 3. Backup Regularly
- Automated daily backups (already configured)
- Test restores monthly
- Keep 30 days of backups

### 4. Document Everything
- Update runbook with new issues
- Document configuration changes
- Keep architecture diagrams current

### 5. Plan for Failure
- Have rollback plan
- Keep old Docker images
- Test disaster recovery
- Practice incident response

---

**Remember:** Most issues have simple solutions. Check the basics first:
1. Are services running?
2. Are resources available (CPU, memory, disk)?
3. Can services communicate (network)?
4. Are credentials correct?
5. What changed recently?

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Contributions:** Add your solutions as you encounter new issues!

