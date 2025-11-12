# VPS QUICK START GUIDE
## GALION.APP & GALION.STUDIO Migration - Essential Commands

**Version:** 1.0  
**Date:** November 10, 2025

---

## ⚡ 30-MINUTE QUICK START

### Step 1: Server Setup (10 minutes)

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Run setup script
curl -fsSL https://raw.githubusercontent.com/galion/infrastructure/main/scripts/vps-setup.sh | bash

# The script will:
# - Update system packages
# - Install Docker, Docker Compose, Nginx, Certbot
# - Configure firewall (UFW)
# - Create deploy user
# - Set up fail2ban
```

### Step 2: Clone & Configure (10 minutes)

```bash
# Switch to deploy user
su - deploy

# Clone repository
git clone https://github.com/galion/platform.git /home/deploy/galion
cd /home/deploy/galion

# Generate secrets
./scripts/generate-secrets.sh

# Edit .env file
nano .env
# Add your API keys: OPENAI_API_KEY, ELEVENLABS_API_KEY
```

### Step 3: Deploy Everything (10 minutes)

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# Watch logs
docker compose logs -f

# Get SSL certificates
sudo certbot --nginx -d galion.app -d api.galion.app -d studio.galion.app
```

**Done! Your apps are now live at:**
- https://galion.app
- https://studio.galion.app

---

## 🔧 ESSENTIAL COMMANDS

### Docker Management

```bash
# View all containers
docker compose ps

# View logs
docker compose logs -f [service-name]

# Restart a service
docker compose restart [service-name]

# Rebuild and restart
docker compose up -d --build [service-name]

# Stop all services
docker compose down

# Start all services
docker compose up -d

# Remove everything (DANGEROUS!)
docker compose down -v  # Deletes volumes too!
```

### Database Management

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U galion -d galion

# Create backup
docker compose exec postgres pg_dump -U galion -Fc galion > backup_$(date +%Y%m%d).dump

# Restore backup
docker compose exec -T postgres pg_restore -U galion -d galion < backup_20251110.dump

# View database size
docker compose exec postgres psql -U galion -c "\l+"

# View table sizes
docker compose exec postgres psql -U galion -d galion -c "\dt+"
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
```

### SSL Certificate Management

```bash
# Get new certificate
sudo certbot --nginx -d your-domain.com

# Renew all certificates
sudo certbot renew

# Test renewal (dry run)
sudo certbot renew --dry-run

# List certificates
sudo certbot certificates

# Delete certificate
sudo certbot delete --cert-name your-domain.com
```

### Monitoring

```bash
# System resources
htop           # Interactive process viewer
free -h        # Memory usage
df -h          # Disk usage
iostat         # CPU and I/O stats

# Docker resource usage
docker stats

# Disk space used by Docker
docker system df

# Clean up unused Docker resources
docker system prune -a --volumes

# View system logs
sudo journalctl -f
```

### Backup & Restore

```bash
# Manual backup
./scripts/backup.sh

# List backups
ls -lh /home/deploy/galion/backups/

# Restore from backup
./scripts/restore.sh backup_20251110.dump.gz
```

---

## 🚨 EMERGENCY PROCEDURES

### Service is Down

```bash
# 1. Check which service is down
docker compose ps

# 2. View logs
docker compose logs [service-name]

# 3. Restart service
docker compose restart [service-name]

# 4. If that doesn't work, rebuild
docker compose up -d --build [service-name]
```

### Database Connection Issues

```bash
# 1. Check if PostgreSQL is running
docker compose ps postgres

# 2. Check PostgreSQL logs
docker compose logs postgres

# 3. Test connection
docker compose exec postgres psql -U galion -c "SELECT 1;"

# 4. Restart PostgreSQL
docker compose restart postgres
```

### Out of Disk Space

```bash
# 1. Check disk usage
df -h

# 2. Find large files
du -h /home/deploy/galion | sort -h | tail -20

# 3. Clean Docker
docker system prune -a --volumes -f

# 4. Clean old backups (keep last 7 days)
find /home/deploy/galion/backups -mtime +7 -delete

# 5. Clean logs
sudo journalctl --vacuum-time=7d
sudo truncate -s 0 /var/log/nginx/*.log
```

### Server Unresponsive

```bash
# 1. Check if you can SSH
ssh deploy@YOUR_VPS_IP

# 2. Check system load
uptime
htop

# 3. Check memory
free -h

# 4. If out of memory, restart services
docker compose restart

# 5. Reboot server (last resort)
sudo reboot
```

### SSL Certificate Expired

```bash
# 1. Renew certificate
sudo certbot renew --force-renewal

# 2. Reload Nginx
sudo systemctl reload nginx

# 3. Test
curl -I https://galion.app
```

---

## 📊 MONITORING URLS

```bash
# Prometheus
http://YOUR_VPS_IP:9090

# Check API health
curl https://api.galion.app/health
curl https://api.studio.galion.app/health

# Check PostgreSQL
docker compose exec postgres pg_isready -U galion

# Check Redis
docker compose exec redis redis-cli ping
```

---

## 🔐 SECURITY CHECKLIST

```bash
# Check firewall status
sudo ufw status

# Check fail2ban status
sudo fail2ban-client status sshd

# View failed login attempts
sudo tail /var/log/auth.log

# Check for rootkits (install rkhunter)
sudo apt install rkhunter -y
sudo rkhunter --check

# Check for security updates
sudo apt update
sudo apt list --upgradable
```

---

## 💰 COST CALCULATOR

### Current Setup (Single VPS)

| Item | Monthly Cost |
|------|--------------|
| Hetzner CPX51 (32GB) | $50 |
| Backblaze B2 (100GB) | $0.50 |
| Cloudflare (Free) | $0 |
| OpenAI APIs | $55 |
| ElevenLabs API | $135 |
| **TOTAL** | **$240.50** |

### Scaling Scenarios

**Scenario 1: Vertical Scaling (1000 users)**
```
VPS: Hetzner CPX51 → CPX61 (64GB)
Cost: $50 → $100/month
Total: $290/month
```

**Scenario 2: Horizontal Scaling (2000+ users)**
```
VPS 1: App servers (CPX41) - $35
VPS 2: Database (CPX51) - $50
Load Balancer (Hetzner) - $6
Managed PostgreSQL - $20
Total: $111 + APIs = $301/month
```

**Scenario 3: High Availability (5000+ users)**
```
VPS 1: App server 1 (CPX51) - $50
VPS 2: App server 2 (CPX51) - $50
VPS 3: Database primary (CPX51) - $50
VPS 4: Database replica (CPX41) - $35
Load Balancer - $6
Total: $191 + APIs = $381/month
```

---

## 📈 PERFORMANCE BENCHMARKS

### Expected Performance (Single VPS)

| Metric | Target | How to Check |
|--------|--------|--------------|
| API Response Time | <200ms | `curl -w "@curl-format.txt" https://api.galion.app/health` |
| Page Load Time | <2s | Chrome DevTools Network tab |
| Database Query Time | <50ms | Check app logs |
| Concurrent Users | 500-1000 | Load test with k6 or Locust |
| Uptime | >99.5% | UptimeRobot |

### Load Testing

```bash
# Install k6
sudo apt install k6 -y

# Run load test (100 users for 5 minutes)
k6 run --vus 100 --duration 5m load-test.js

# Monitor during test
watch -n 1 docker stats
```

---

## 🔄 UPDATE & DEPLOYMENT

### Zero-Downtime Deployment

```bash
# 1. Pull latest code
cd /home/deploy/galion
git pull origin main

# 2. Build new images
docker compose build

# 3. Deploy services one by one (no downtime)
docker compose up -d --no-deps --build app-api
sleep 10  # Wait for health check
docker compose up -d --no-deps --build app-frontend

# 4. Verify
curl https://api.galion.app/health
```

### Rollback

```bash
# 1. View previous images
docker images | grep galion

# 2. Tag old version
docker tag galion-app-api:old galion-app-api:latest

# 3. Restart with old image
docker compose up -d --no-deps app-api
```

---

## 🎯 DAILY CHECKLIST

### Morning (5 minutes)
```bash
□ Check if all services are running: docker compose ps
□ Check disk space: df -h
□ Check last night's backup: ls -lh backups/
□ Check error logs: docker compose logs --tail=50 | grep ERROR
□ Check Grafana for alerts
```

### Weekly (15 minutes)
```bash
□ Update system packages: sudo apt update && sudo apt upgrade
□ Clean Docker: docker system prune -f
□ Test backup restore: ./scripts/test-restore.sh
□ Review access logs for suspicious activity
□ Check SSL certificate expiry: sudo certbot certificates
```

### Monthly (30 minutes)
```bash
□ Full security audit: sudo rkhunter --check
□ Review and optimize database: VACUUM ANALYZE
□ Check performance metrics in Grafana
□ Update documentation
□ Review and optimize costs
```

---

## 📞 SUPPORT

### Logs Location
```
Application Logs:  /home/deploy/galion/data/logs/
Nginx Logs:        /var/log/nginx/
System Logs:       /var/log/syslog
Docker Logs:       docker compose logs
```

### Configuration Files
```
Docker Compose:    /home/deploy/galion/docker-compose.yml
Environment:       /home/deploy/galion/.env
Nginx:            /etc/nginx/sites-available/
SSL Certs:        /etc/letsencrypt/live/
```

### Backup Files
```
Local Backups:     /home/deploy/galion/backups/
Remote Backups:    Backblaze B2 bucket
```

---

## 🚀 AUTOMATION SCRIPTS

### Auto-Update Script

Create `/home/deploy/galion/scripts/auto-update.sh`:

```bash
#!/bin/bash
# Auto-update and deploy (use with caution in production!)

set -e

cd /home/deploy/galion

# Pull latest code
git pull origin main

# Build and deploy
docker compose build
docker compose up -d --no-deps app-api
docker compose up -d --no-deps app-frontend
docker compose up -d --no-deps studio-api
docker compose up -d --no-deps studio-frontend

# Wait for services to be ready
sleep 30

# Health check
curl -f https://api.galion.app/health || exit 1
curl -f https://api.studio.galion.app/health || exit 1

echo "Deployment successful at $(date)"
```

### Health Check Script

Create `/home/deploy/galion/scripts/health-check.sh`:

```bash
#!/bin/bash
# Health check all services

echo "=== GALION Health Check ===" 
echo "Time: $(date)"
echo ""

# Check Docker services
echo "Docker Services:"
docker compose ps

# Check API endpoints
echo ""
echo "API Health:"
curl -s https://api.galion.app/health | jq '.'
curl -s https://api.studio.galion.app/health | jq '.'

# Check database
echo ""
echo "Database:"
docker compose exec -T postgres pg_isready -U galion

# Check disk space
echo ""
echo "Disk Space:"
df -h / | tail -1

# Check memory
echo ""
echo "Memory:"
free -h | grep Mem

echo ""
echo "=== Health Check Complete ==="
```

Make executable:
```bash
chmod +x /home/deploy/galion/scripts/*.sh
```

---

## 💡 PRO TIPS

### Speed Up Docker Builds
```bash
# Use BuildKit
export DOCKER_BUILDKIT=1
docker compose build

# Build with cache
docker compose build --parallel
```

### Reduce Log Size
```bash
# Limit log file size in docker-compose.yml
services:
  app-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitor Resource Usage
```bash
# Install ctop (Docker monitoring)
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop

# Run
ctop
```

### Secure Environment Variables
```bash
# Instead of .env file, use Docker secrets
echo "my-secret-password" | docker secret create postgres_password -

# Use in docker-compose.yml
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

---

## 📖 ADDITIONAL RESOURCES

- **Full Migration Plan:** `VPS_MIGRATION_PLAN.md`
- **Original AWS Plan:** `galion-app-deployment.md`
- **Studio Plan:** `galion-studio-plan.md`

---

**Built with ⚡ Simplicity & Speed ⚡**

**Keep it simple. Keep it running. Keep shipping.**

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** READY TO USE

**DEPLOY NOW!** 🚀

