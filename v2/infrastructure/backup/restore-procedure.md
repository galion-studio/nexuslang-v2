# Project Nexus - Disaster Recovery Procedure

**Last Updated:** November 11, 2025  
**Recovery Time Objective (RTO):** 30 minutes  
**Recovery Point Objective (RPO):** 1 hour

---

## 🚨 When to Use This Guide

Use this procedure when:
- Primary server is down/compromised
- Database is corrupted
- Ransomware attack
- Data center failure
- Complete system rebuild needed

---

## 📋 Prerequisites

Before starting recovery, ensure you have:

- [ ] Access to backup files (local or B2)
- [ ] Server credentials (root/sudo access)
- [ ] Environment variables backup (`.env` file)
- [ ] Domain DNS access
- [ ] Approximately 30-60 minutes of time

---

## 🔄 Recovery Procedure

### Phase 1: Preparation (5 minutes)

#### 1.1 Assess the Situation

```bash
# Check if services are running
docker ps

# Check disk space
df -h

# Check recent logs
tail -f /var/log/syslog
```

#### 1.2 Notify Team

- Update status page
- Notify users via Twitter/Discord
- Document the incident

#### 1.3 Stop All Services

```bash
cd /path/to/project-nexus
docker-compose down
```

---

### Phase 2: Fresh Infrastructure (10 minutes)

#### 2.1 Provision New Server (if needed)

If starting from scratch:

```bash
# SSH into new server
ssh root@new-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt install docker-compose -y

# Install required tools
apt install -y postgresql-client git python3-pip rclone
```

#### 2.2 Clone Repository

```bash
# Clone project
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Checkout correct version/branch
git checkout main
```

#### 2.3 Restore Environment Variables

```bash
# Copy backed up .env file
nano .env

# Or restore from secure location
# scp backup-server:/secure/nexus.env .env

# Verify all secrets are present
grep -E "JWT_SECRET_KEY|ENCRYPTION_MASTER_KEY|POSTGRES_PASSWORD|REDIS_PASSWORD" .env
```

---

### Phase 3: Database Recovery (10 minutes)

#### 3.1 Download Backup from B2

```bash
# Configure rclone (if not already done)
rclone config

# List available backups
rclone ls b2:nexus-backups/backups/

# Download latest backup
mkdir -p /tmp/restore
rclone copy b2:nexus-backups/backups/nexus_db_daily_LATEST.sql.gz /tmp/restore/

# Download metadata
rclone copy b2:nexus-backups/backups/nexus_db_daily_LATEST.json /tmp/restore/
```

#### 3.2 Verify Backup Integrity

```bash
# Check backup metadata
cat /tmp/restore/nexus_db_daily_LATEST.json

# Verify checksum
sha256sum /tmp/restore/nexus_db_daily_LATEST.sql.gz

# Compare with metadata checksum
# (Should match the checksum in JSON file)
```

#### 3.3 Start Database Service

```bash
# Start only PostgreSQL
docker-compose up -d postgres

# Wait for it to be ready
docker-compose logs -f postgres
# Look for: "database system is ready to accept connections"
```

#### 3.4 Restore Database

```bash
# Restore from backup
docker exec -i nexus-postgres pg_restore \
  -U nexus \
  -d nexus_v2 \
  --clean \
  --if-exists \
  --verbose \
  /tmp/restore/nexus_db_daily_LATEST.sql.gz

# Or if file is on host:
docker cp /tmp/restore/nexus_db_daily_LATEST.sql.gz nexus-postgres:/tmp/
docker exec nexus-postgres pg_restore \
  -U nexus \
  -d nexus_v2 \
  --clean \
  --if-exists \
  /tmp/nexus_db_daily_LATEST.sql.gz
```

#### 3.5 Verify Database

```bash
# Connect to database
docker exec -it nexus-postgres psql -U nexus -d nexus_v2

# Check tables exist
\dt

# Check user count (should match expected)
SELECT COUNT(*) FROM users;

# Check recent data
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;

# Exit
\q
```

---

### Phase 4: Service Recovery (5 minutes)

#### 4.1 Start All Services

```bash
# Start all services
docker-compose up -d

# Watch logs for errors
docker-compose logs -f
```

#### 4.2 Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check database connectivity
docker exec nexus-backend python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

#### 4.3 Verify Critical Functions

```bash
# Test user login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# Test NexusLang execution
curl -X POST http://localhost:8000/api/v2/nexuslang/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"code": "print(\"Hello World\")"}'
```

---

### Phase 5: DNS & SSL (3 minutes)

#### 5.1 Update DNS

```bash
# Point domain to new server IP
# (via Cloudflare dashboard or DNS provider)

# Check DNS propagation
dig galion.app
dig nexuslang.dev
```

#### 5.2 Configure SSL

```bash
# If using Cloudflare: SSL is automatic
# If using Let's Encrypt:

docker-compose run --rm certbot \
  certonly --webroot \
  -w /var/www/certbot \
  -d galion.app \
  -d api.galion.app \
  --email admin@galion.app \
  --agree-tos \
  --no-eff-email
```

---

### Phase 6: Verification & Monitoring (5 minutes)

#### 6.1 Smoke Tests

```bash
# Run automated tests
cd v2/backend
pytest tests/test_security.py -v

# Check all endpoints
curl -I https://galion.app
curl -I https://api.galion.app/health
curl -I https://nexuslang.dev
```

#### 6.2 Monitor Metrics

```bash
# Check Prometheus
open http://server-ip:9090

# Check Grafana
open http://server-ip:3001

# Verify metrics are being collected
```

#### 6.3 Update Status

- Mark incident as resolved
- Update status page
- Notify users of restoration
- Document what happened

---

## 🎯 Recovery Checklist

Use this checklist during recovery:

### Infrastructure
- [ ] New server provisioned (if needed)
- [ ] Docker and dependencies installed
- [ ] Repository cloned
- [ ] Environment variables restored

### Database
- [ ] Backup downloaded from B2
- [ ] Backup integrity verified
- [ ] PostgreSQL started
- [ ] Database restored
- [ ] Data verified

### Services
- [ ] All containers started
- [ ] Health checks passing
- [ ] Critical functions tested
- [ ] Logs reviewed for errors

### Network
- [ ] DNS updated
- [ ] SSL certificates installed
- [ ] Domains accessible
- [ ] HTTPS working

### Verification
- [ ] User login works
- [ ] API endpoints responding
- [ ] Frontend loading
- [ ] Monitoring active

### Communication
- [ ] Team notified of resolution
- [ ] Users notified
- [ ] Incident documented
- [ ] Postmortem scheduled

---

## 📞 Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| **Primary Admin** | Your Name | your-email@example.com |
| **VPS Provider** | Hetzner/OVH | support link |
| **Backup Provider** | Backblaze B2 | support link |
| **DNS Provider** | Cloudflare | support link |

---

## 🔄 Backup Locations

1. **Primary:** `/var/backups/nexus` (on VPS)
2. **Secondary:** `/mnt/backup/nexus` (on VPS, different disk)
3. **Offsite:** `b2:nexus-backups/backups/` (Backblaze B2)
4. **Git:** Private GitHub repository (configs only)

---

## 🚀 Alternative: Quick Docker Recovery

If infrastructure is intact, quick recovery:

```bash
# Pull latest images
docker-compose pull

# Restore from most recent backup
./v2/infrastructure/backup/quick-restore.sh

# Restart services
docker-compose up -d
```

---

## 📊 Recovery Metrics

Track these during recovery:

- **Detection Time:** When issue was first noticed
- **Response Time:** Time until recovery started
- **Recovery Time:** Time until services restored
- **Data Loss:** Amount of data lost (should be < 1 hour)

**Target RTO:** 30 minutes  
**Target RPO:** 1 hour

---

## 🛡️ Post-Recovery Actions

After successful recovery:

1. **Incident Report:** Document what happened
2. **Root Cause Analysis:** Why did it happen?
3. **Preventive Measures:** How to prevent recurrence?
4. **Update Procedures:** Improve this document
5. **Team Review:** Debrief with team
6. **Backup Verification:** Test restore process

---

## 🔒 Security Considerations

If recovery was due to security incident:

- [ ] Rotate all secrets (JWT, encryption keys, passwords)
- [ ] Review access logs
- [ ] Check for unauthorized access
- [ ] Scan for malware
- [ ] Update security policies
- [ ] Notify affected users (if data breach)

---

## ✅ Recovery Complete

When all checks pass:

```bash
echo "🎉 Recovery complete! Services are operational."
echo "📊 Check monitoring dashboards"
echo "📝 Document the incident"
echo "🔄 Schedule backup verification"
```

---

**Remember:** The best disaster recovery is disaster prevention.
- Test backups monthly
- Monitor proactively
- Keep documentation updated
- Train team on procedures

---

**Built with resilience. Restored with confidence.** 🛡️

