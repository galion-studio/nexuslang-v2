# GALION VPS Production Deployment - Final Checklist
## Complete Migration to TITANAXE Server (54.37.161.67)

**Version:** 1.0  
**Server:** TITANAXE VPS (16GB RAM, 100GB SSD, Ubuntu 24.04 LTS)  
**Status:** Ready to Execute

---

## Pre-Deployment Checklist

### 1. VPS Access
- [ ] Can SSH to server: `ssh root@54.37.161.67`
- [ ] Have sudo access
- [ ] Server is Ubuntu 24.04 LTS
- [ ] Server has 16GB RAM and sufficient disk space

### 2. Domain Configuration
- [ ] Own domains: galion.app, studio.galion.app
- [ ] DNS access (Cloudflare account)
- [ ] Domains pointed to 54.37.161.67
- [ ] DNS propagated (check with `dig galion.app`)

### 3. API Keys & Credentials
- [ ] OpenAI API key (for Whisper + GPT-4)
- [ ] ElevenLabs API key (for TTS)
- [ ] Grafana Cloud account (optional, for monitoring)
- [ ] Backblaze B2 account (optional, for off-site backups)

### 4. Local Setup
- [ ] Git repository cloned locally
- [ ] All configuration files reviewed
- [ ] Understand architecture (reviewed documentation)
- [ ] Backup of current state (if migrating from elsewhere)

---

## Phase 1: Server Setup (30 minutes)

### Step 1.1: Initial Server Configuration
```bash
# SSH as root
ssh root@54.37.161.67

# Run automated setup script
cd /tmp
curl -fsSL https://raw.githubusercontent.com/your-org/galion-infrastructure/main/scripts/vps-setup.sh -o vps-setup.sh
chmod +x vps-setup.sh
./vps-setup.sh
```

**What this does:**
- Installs Docker, Docker Compose, Nginx, Certbot
- Configures UFW firewall
- Installs fail2ban
- Creates deploy user
- Sets up directory structure
- Hardens SSH configuration

**Verification:**
- [ ] Docker installed: `docker --version`
- [ ] Nginx installed: `nginx -v`
- [ ] Firewall active: `sudo ufw status`
- [ ] Deploy user created: `id deploy`

### Step 1.2: Switch to Deploy User
```bash
# Switch to deploy user
su - deploy

# Verify you're in /home/deploy
pwd
```

### Step 1.3: Clone Repository
```bash
# Create galion directory
mkdir -p /home/deploy/galion
cd /home/deploy/galion

# Clone your repository
git clone https://github.com/your-org/galion-platform.git .

# Or initialize new repository
git init
```

---

## Phase 2: Configuration (15 minutes)

### Step 2.1: Generate Secrets
```bash
cd /home/deploy/galion

# Generate strong passwords and secrets
./scripts/generate-secrets.sh

# This creates .env file with:
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD  
# - JWT_SECRET
```

**Verification:**
- [ ] .env file created
- [ ] Secrets are strong (32+ characters)
- [ ] File permissions are 600

### Step 2.2: Add API Keys
```bash
# Edit .env file
nano .env

# Add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# ELEVENLABS_API_KEY=your-key-here

# Save and exit (Ctrl+X, Y, Enter)
```

**Verification:**
- [ ] OPENAI_API_KEY set
- [ ] ELEVENLABS_API_KEY set
- [ ] No placeholder values remain

### Step 2.3: Create Required Directories
```bash
# Create all required directories
mkdir -p data/{postgres,redis,uploads,logs,prometheus}
mkdir -p backups/wal_archive
mkdir -p monitoring
mkdir -p logs
mkdir -p configs
mkdir -p nginx/{sites-available,sites-enabled,conf.d}

# Set permissions
chmod 755 data backups logs
chmod 700 .env
```

---

## Phase 3: Deploy Services (20 minutes)

### Step 3.1: Build Docker Images
```bash
cd /home/deploy/galion

# Build all images
docker compose build --parallel

# This takes 5-10 minutes
```

**Verification:**
- [ ] Build completed without errors
- [ ] Images created: `docker images | grep galion`

### Step 3.2: Start Infrastructure Services
```bash
# Start PostgreSQL and Redis first
docker compose up -d postgres redis

# Wait for them to be healthy
sleep 30

# Check status
docker compose ps postgres redis

# Should show "healthy" status
```

**Verification:**
- [ ] PostgreSQL container running and healthy
- [ ] Redis container running and healthy
- [ ] Can connect: `docker compose exec postgres pg_isready -U galion`
- [ ] Can connect: `docker compose exec redis redis-cli ping`

### Step 3.3: Start PgBouncer
```bash
# Start connection pooler
docker compose up -d pgbouncer

# Wait and verify
sleep 10
docker compose ps pgbouncer
```

### Step 3.4: Run Database Migrations
```bash
# Start app services briefly to run migrations
docker compose up -d app-api studio-api

# Wait for startup
sleep 30

# Run migrations
docker compose exec -T app-api alembic upgrade head
docker compose exec -T studio-api alembic upgrade head

# Or use migration script
./scripts/migrate.sh
```

**Verification:**
- [ ] Migrations completed without errors
- [ ] Tables created in both databases
- [ ] Check: `docker compose exec postgres psql -U galion -d galion -c "\dt"`

### Step 3.5: Create Database Indexes
```bash
# Optimize database with indexes
docker compose exec -T postgres psql -U galion < scripts/optimize-db.sql
```

**Verification:**
- [ ] Indexes created
- [ ] No errors during creation

### Step 3.6: Start All Application Services
```bash
# Start all services
docker compose up -d

# Wait for all services to be healthy
sleep 60

# Check status
docker compose ps
```

**Verification:**
- [ ] All services show "Up" or "healthy"
- [ ] No services in "Restarting" state

### Step 3.7: Verify Health Endpoints
```bash
# Test all health endpoints
curl http://localhost:8001/health  # App API
curl http://localhost:8003/health  # Studio API
curl http://localhost:8002/health  # Voice Service
curl http://localhost:8004/health  # Realtime Service
curl http://localhost:3001         # App Frontend
curl http://localhost:3003         # Studio Frontend

# Or use health check script
./scripts/health-check.sh
```

**Verification:**
- [ ] All endpoints return 200 OK
- [ ] Health status shows "healthy"

---

## Phase 4: Nginx & SSL (15 minutes)

### Step 4.1: Copy Nginx Configuration
```bash
# Copy configurations to system directories
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp nginx/sites-available/* /etc/nginx/sites-available/
sudo cp nginx/conf.d/* /etc/nginx/conf.d/

# Create symbolic links to enable sites
sudo ln -sf /etc/nginx/sites-available/galion-app /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/galion-studio /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default
```

### Step 4.2: Test Nginx Configuration
```bash
# Test configuration
sudo nginx -t

# Should show "syntax is ok"
# If errors, fix configuration files
```

**Verification:**
- [ ] Nginx test passes
- [ ] No syntax errors

### Step 4.3: Create Certbot Directory
```bash
# Create directory for Let's Encrypt challenges
sudo mkdir -p /var/www/certbot
sudo chown -R www-data:www-data /var/www/certbot
```

### Step 4.4: Reload Nginx
```bash
# Reload Nginx with new configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

### Step 4.5: Get SSL Certificates
```bash
# For GALION.APP
sudo certbot --nginx \
  -d galion.app \
  -d www.galion.app \
  -d api.galion.app \
  --non-interactive \
  --agree-tos \
  -m your-email@example.com

# For GALION.STUDIO
sudo certbot --nginx \
  -d studio.galion.app \
  -d api.studio.galion.app \
  --non-interactive \
  --agree-tos \
  -m your-email@example.com
```

**Verification:**
- [ ] Certificates obtained successfully
- [ ] Nginx reloaded automatically
- [ ] HTTPS works: `curl -I https://galion.app`

### Step 4.6: Test Auto-Renewal
```bash
# Test certificate auto-renewal
sudo certbot renew --dry-run

# Should complete without errors
```

---

## Phase 5: Monitoring Setup (10 minutes)

### Step 5.1: Verify Monitoring Services
```bash
# Check monitoring services are running
docker compose ps prometheus node-exporter cadvisor

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test metrics endpoints
curl http://localhost:9100/metrics  # Node Exporter
curl http://localhost:9187/metrics  # Postgres Exporter
curl http://localhost:9121/metrics  # Redis Exporter
```

### Step 5.2: Configure Grafana Cloud (Optional)
```bash
# 1. Sign up at https://grafana.com
# 2. Create free account
# 3. Get Prometheus remote_write URL and credentials
# 4. Add to monitoring/prometheus.yml (already has placeholder)
# 5. Update with your credentials
nano monitoring/prometheus.yml

# 6. Restart Prometheus
docker compose restart prometheus
```

### Step 5.3: Import Dashboards
- Log in to Grafana Cloud
- Go to Dashboards → Import
- Import dashboard IDs:
  - 1860 (Node Exporter)
  - 193 (Docker)
  - 9628 (PostgreSQL)
  - 11835 (Redis)

---

## Phase 6: Security Hardening (10 minutes)

### Step 6.1: Configure fail2ban
```bash
# Copy fail2ban configuration
sudo cp configs/fail2ban-nginx.conf /etc/fail2ban/jail.d/nginx.conf

# Restart fail2ban
sudo systemctl restart fail2ban

# Verify
sudo fail2ban-client status
```

### Step 6.2: Setup Cloudflare
Follow `docs/CLOUDFLARE_SETUP.md`:
- [ ] Add domains to Cloudflare
- [ ] Configure DNS (proxied)
- [ ] Set SSL/TLS to "Full (strict)"
- [ ] Enable Bot Fight Mode
- [ ] Configure firewall rules
- [ ] Enable WebSockets
- [ ] Set up page rules for caching

### Step 6.3: Test Security
```bash
# Test SSL configuration
curl -I https://galion.app | grep "Strict-Transport-Security"

# Test rate limiting
for i in {1..110}; do curl -s -o /dev/null -w "%{http_code}\n" https://api.galion.app/health; done
# Should get 429 (rate limited) after 100 requests

# Check firewall
sudo ufw status verbose
```

---

## Phase 7: Backup Configuration (5 minutes)

### Step 7.1: Test Backup Script
```bash
# Run manual backup
./scripts/backup.sh

# Verify backup created
ls -lht backups/*.dump.gz | head -3
```

**Verification:**
- [ ] Backup files created
- [ ] Both databases backed up (galion + galion_studio)
- [ ] Files are compressed

### Step 7.2: Setup Automated Backups
```bash
# Add cron jobs
crontab -e

# Add these lines:
0 2 * * * /home/deploy/galion/scripts/backup.sh >> /home/deploy/galion/logs/backup.log 2>&1
*/5 * * * * /home/deploy/galion/scripts/health-check.sh >> /home/deploy/galion/logs/health.log 2>&1
0 0 * * 0 /home/deploy/galion/scripts/incremental-backup.sh backup >> /home/deploy/galion/logs/incremental-backup.log 2>&1
```

### Step 7.3: Setup Incremental Backups
```bash
# Configure WAL archiving for PITR
./scripts/incremental-backup.sh setup

# Restart PostgreSQL
docker compose restart postgres

# Create first base backup
./scripts/incremental-backup.sh backup
```

### Step 7.4: Configure Off-site Backups (Optional)
```bash
# Install B2 CLI
pip3 install b2sdk

# Configure B2
b2 authorize-account YOUR_KEY_ID YOUR_APPLICATION_KEY

# Test upload
b2 upload-file galion-backups backups/test.txt test.txt

# Add B2_BUCKET_NAME to .env
echo "B2_BUCKET_NAME=galion-backups" >> .env
```

---

## Phase 8: Testing & Verification (15 minutes)

### Step 8.1: Run Full Health Check
```bash
./scripts/health-check.sh > verification-report.txt

# Review report
cat verification-report.txt
```

**Expected:**
- All containers running
- All health checks passing
- Memory usage <80%
- Disk usage <50%

### Step 8.2: Test External Access
```bash
# Test HTTPS endpoints
curl -I https://galion.app
curl -I https://api.galion.app/health
curl -I https://studio.galion.app
curl -I https://api.studio.galion.app/health
```

**Verification:**
- [ ] All return 200 OK
- [ ] SSL certificates valid
- [ ] Cloudflare headers present

### Step 8.3: Test Application Functionality

**GALION.APP:**
- [ ] Can access https://galion.app
- [ ] Can register new user
- [ ] Can log in
- [ ] Can start voice conversation (if voice implemented)

**GALION.STUDIO:**
- [ ] Can access https://studio.galion.app
- [ ] Can create workspace
- [ ] Can create project
- [ ] Can create task

### Step 8.4: Run Load Test
```bash
# Light load test (10 concurrent users)
k6 run --vus 10 --duration 1m tests/load/api-test.js

# Review results
# - Check success rate (should be 100%)
# - Check response times (should be <500ms)
```

### Step 8.5: Verify Monitoring
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'

# All should be "up"

# Access Prometheus UI
echo "Open http://54.37.161.67:9090 in browser"

# Check Grafana Cloud (if configured)
# Log in and verify metrics are flowing
```

### Step 8.6: Test Backup & Restore
```bash
# Run backup
./scripts/backup.sh

# Test restore (on test database)
docker compose exec postgres psql -U galion -c "CREATE DATABASE test_restore;"

# Restore latest backup to test database
gunzip -c backups/galion_latest.dump.gz | \
  docker compose exec -T postgres pg_restore -U galion -d test_restore

# Verify
docker compose exec postgres psql -U galion -d test_restore -c "SELECT COUNT(*) FROM users;"

# Clean up test database
docker compose exec postgres psql -U galion -c "DROP DATABASE test_restore;"
```

**Verification:**
- [ ] Backup runs without errors
- [ ] Restore works correctly
- [ ] Data integrity verified

---

## Phase 9: Production Readiness (10 minutes)

### Step 9.1: Security Final Checks
- [ ] Root login disabled
- [ ] Password authentication disabled
- [ ] fail2ban active: `sudo fail2ban-client status`
- [ ] Firewall configured: `sudo ufw status`
- [ ] SSL/TLS certificates valid
- [ ] Security headers present in responses
- [ ] Cloudflare DDoS protection enabled

### Step 9.2: Performance Optimization
- [ ] Database indexes created
- [ ] PgBouncer connection pooling active
- [ ] Redis caching configured
- [ ] Nginx caching enabled
- [ ] Cloudflare CDN active
- [ ] Compression enabled (gzip/brotli)

### Step 9.3: Monitoring & Alerting
- [ ] Prometheus collecting metrics
- [ ] All exporters running
- [ ] Grafana dashboards created
- [ ] Critical alerts configured
- [ ] Alert channels working (email/Slack)

### Step 9.4: Backup & DR
- [ ] Daily backups automated (cron)
- [ ] Backup verification passing
- [ ] Off-site backups configured (B2)
- [ ] PITR configured (WAL archiving)
- [ ] DR procedures documented

---

## Phase 10: Go Live (5 minutes)

### Step 10.1: Final Smoke Tests
```bash
# Run complete verification
./scripts/verify-deployment.sh

# Should show all tests passing
```

### Step 10.2: Monitor Launch
- [ ] Watch Grafana dashboards
- [ ] Monitor Docker logs: `docker compose logs -f`
- [ ] Check error rates
- [ ] Monitor resource usage

### Step 10.3: Announce Launch
- [ ] Update status page
- [ ] Post on social media
- [ ] Email early adopters
- [ ] Monitor user feedback

---

## Post-Launch Monitoring (First 48 Hours)

### Hour 1-6: Intensive Monitoring
Check every 30 minutes:
- [ ] All services healthy
- [ ] No error spikes
- [ ] Response times normal
- [ ] No resource issues
- [ ] Backup scheduled correctly

### Hour 6-24: Active Monitoring
Check every 2 hours:
- [ ] System stable
- [ ] No degradation over time
- [ ] Memory not leaking
- [ ] Disk space stable

### Hour 24-48: Standard Monitoring
Check every 4 hours:
- [ ] Performance metrics within targets
- [ ] No unusual patterns
- [ ] User feedback positive
- [ ] Ready to hand off to normal operations

---

## Success Metrics - Week 1

After first week, verify these metrics:

### Reliability
- [ ] Uptime: >99.9% (less than 1 hour downtime)
- [ ] Zero data loss incidents
- [ ] All backups successful (7/7 days)

### Performance
- [ ] API response time P99: <500ms
- [ ] Page load time: <2s
- [ ] Database queries: <100ms average
- [ ] Cache hit rate: >70%

### Resource Usage
- [ ] Memory usage: <85% (13.6GB / 16GB)
- [ ] CPU usage: <70% average
- [ ] Disk usage: <60% (60GB / 100GB)
- [ ] Database connections: <60% of max

### User Experience
- [ ] No user-reported errors
- [ ] Features working as expected
- [ ] Voice interaction functional
- [ ] Positive feedback from early users

---

## Troubleshooting Common Issues

### Issue: Service won't start
**Solution:** Check logs and review `docs/TROUBLESHOOTING.md`

### Issue: High memory usage
**Solution:** Restart services or reduce container limits

### Issue: SSL certificate error
**Solution:** Re-run certbot

### Issue: Database connection errors
**Solution:** Check PostgreSQL is running and credentials in .env

**For detailed troubleshooting, see: `docs/TROUBLESHOOTING.md`**

---

## Key Files Reference

### Configuration Files
- `docker-compose.yml` - Main orchestration
- `.env` - Environment variables (secrets)
- `configs/postgresql.conf` - Database tuning
- `configs/pgbouncer.ini` - Connection pooling
- `nginx/nginx.conf` - Web server config

### Scripts
- `scripts/vps-setup.sh` - Initial server setup
- `scripts/generate-secrets.sh` - Generate passwords
- `scripts/full-deployment.sh` - Complete deployment
- `scripts/deploy.sh` - Zero-downtime updates
- `scripts/backup.sh` - Daily backups
- `scripts/restore.sh` - Restore from backup
- `scripts/health-check.sh` - Health verification
- `scripts/migrate.sh` - Database migrations

### Documentation
- `docs/RUNBOOK.md` - Daily operations
- `docs/TROUBLESHOOTING.md` - Issue resolution
- `docs/SCALING_GUIDE.md` - How to scale
- `docs/MONITORING_GUIDE.md` - Observability
- `docs/DISASTER_RECOVERY.md` - DR procedures
- `docs/CLOUDFLARE_SETUP.md` - CDN setup

---

## Next Steps After Deployment

### Week 1: Stabilization
- Monitor intensively
- Fix any issues immediately
- Tune performance
- Collect user feedback
- Document any new issues

### Week 2-4: Optimization
- Optimize based on real usage patterns
- Add missing features
- Improve performance
- Scale if needed (unlikely)

### Month 2-3: Growth
- Add more features
- Onboard more users
- Monitor growth metrics
- Plan for scaling

### Month 4+: Scale
- When hitting resource limits
- Follow `docs/SCALING_GUIDE.md`
- Add servers or upgrade
- Maintain high quality

---

## Emergency Contacts

### Primary
- Oncall Engineer: [Your Name]
- Phone: [Phone]
- Email: [Email]

### Vendors
- Hetzner Support: https://www.hetzner.com/support
- Cloudflare Support: https://support.cloudflare.com

---

## Final Pre-Launch Checklist

### Technical
- [ ] All services deployed and healthy
- [ ] SSL certificates valid
- [ ] Monitoring operational
- [ ] Backups configured and tested
- [ ] Load tested (100+ users)
- [ ] Security hardened
- [ ] Documentation complete

### Operational
- [ ] Oncall schedule set
- [ ] Incident response plan ready
- [ ] Runbooks accessible
- [ ] Team trained
- [ ] Communication channels ready

### Business
- [ ] Terms of Service published
- [ ] Privacy Policy published
- [ ] GDPR compliance verified
- [ ] Support channels ready
- [ ] Pricing configured (if applicable)

---

**When all checks pass:**

🎉 **CONGRATULATIONS! You're ready to go live!** 🎉

---

## Post-Deployment Actions

1. **Monitor Closely:**
   - First 6 hours: Check every 30 min
   - Next 18 hours: Check every 2 hours
   - After 24 hours: Normal monitoring

2. **Collect Feedback:**
   - Ask early users for feedback
   - Monitor error reports
   - Track user behavior

3. **Iterate Quickly:**
   - Fix critical bugs within 24 hours
   - Deploy improvements daily
   - Document learnings

4. **Prepare for Scale:**
   - Monitor growth metrics
   - Plan scaling strategy
   - Review costs monthly

---

**You've built a production-ready, scalable platform!**

**Now go ship and iterate!** 🚀

---

**Version:** 1.0  
**Completed:** November 10, 2025  
**Status:** ✅ Production Ready

**Built with Elon Musk's First Principles**  
**Simple. Scalable. Reliable.**

