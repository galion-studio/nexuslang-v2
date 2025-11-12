# GALION Disaster Recovery Plan
## Complete DR Strategy and Procedures

**Version:** 1.0  
**Date:** November 10, 2025  
**Classification:** Critical - Operations

---

## Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

### Targets

**RTO (Recovery Time Objective):**
- **Critical services:** <30 minutes
- **Complete system:** <2 hours
- **Full functionality:** <4 hours

**RPO (Recovery Point Objective):**
- **Database:** <24 hours (daily backups)
- **With PITR:** <5 minutes (WAL archiving)
- **Files/uploads:** <24 hours

---

## Disaster Scenarios

### Scenario 1: Single Service Failure

**Impact:** One service down (e.g., app-api), others running

**Detection Time:** <2 minutes (automated alerts)

**Recovery Steps:**
```bash
# 1. Restart service
docker compose restart app-api

# 2. If doesn't work, check logs
docker compose logs app-api --tail=100

# 3. If configuration issue, fix and redeploy
./scripts/deploy.sh

# 4. If code issue, rollback
git revert HEAD
docker compose up -d --build app-api
```

**Estimated RTO:** 5-15 minutes

---

### Scenario 2: Database Corruption

**Impact:** Database unreadable, all services affected

**Detection Time:** <2 minutes (health checks fail)

**Recovery Steps:**

**Option A: Restore from daily backup (RPO: 24h)**
```bash
# 1. Stop services
docker compose stop app-api studio-api

# 2. Backup corrupted data (forensics)
sudo cp -r data/postgres /tmp/corrupted_postgres_$(date +%s)

# 3. Restore from backup
./scripts/restore.sh backups/galion_latest.dump.gz

# 4. Restart services
docker compose up -d

# 5. Verify
./scripts/verify-deployment.sh
```

**Estimated RTO:** 20-40 minutes  
**Data Loss:** Up to 24 hours

**Option B: Point-in-Time Recovery (RPO: 5min)**
```bash
# 1. Stop services
docker compose stop app-api studio-api

# 2. Run PITR
./scripts/restore-pitr.sh "$(date -d '5 minutes ago' '+%Y-%m-%d %H:%M:%S')"

# 3. Verify data
docker compose exec postgres psql -U galion -d galion -c "SELECT COUNT(*) FROM users;"

# 4. Restart services
docker compose up -d
```

**Estimated RTO:** 30-60 minutes  
**Data Loss:** <5 minutes

---

### Scenario 3: Complete Server Failure

**Impact:** Entire VPS down, all services unavailable

**Detection Time:** <2 minutes (automated alerts)

**Recovery Steps:**

**Option A: Restore on Same Server (if accessible)**
```bash
# 1. SSH to server
ssh deploy@54.37.161.67

# 2. Check system status
uptime
df -h
free -h

# 3. If server is up but services are down
cd /home/deploy/galion
docker compose down
docker compose up -d

# 4. If Docker is broken
sudo systemctl restart docker
docker compose up -d

# 5. If system is corrupted, reboot
sudo reboot
# Wait 2 minutes, SSH back in
docker compose up -d
```

**Estimated RTO:** 10-30 minutes

**Option B: Migrate to New Server**
```bash
# 1. Provision new VPS (Hetzner/DigitalOcean)

# 2. Run setup script
ssh root@NEW_IP
curl -fsSL https://raw.githubusercontent.com/galion/infrastructure/main/scripts/vps-setup.sh | bash

# 3. Clone repository
su - deploy
git clone YOUR_REPO /home/deploy/galion
cd /home/deploy/galion

# 4. Copy .env from backup
# Restore from password manager or encrypted backup

# 5. Restore database from Backblaze B2
# Download latest backup
b2 download-file galion-backups backups/galion_latest.dump.gz

# 6. Start services
docker compose up -d

# 7. Restore database
./scripts/restore.sh backups/galion_latest.dump.gz

# 8. Update DNS to new IP
# Point galion.app to NEW_IP in Cloudflare

# 9. Get SSL certificates
sudo certbot --nginx -d galion.app -d api.galion.app

# 10. Verify
./scripts/verify-deployment.sh
```

**Estimated RTO:** 1-2 hours  
**Data Loss:** Up to 24 hours (depends on last backup)

---

### Scenario 4: Data Center Outage

**Impact:** Entire region unavailable (Hetzner data center down)

**Detection Time:** <5 minutes

**Recovery Steps:**

**Prerequisites:**
- Off-site backups (Backblaze B2)
- Encrypted .env backup
- Documentation accessible (GitHub)

**Recovery:**
1. Provision VPS in different region/provider
2. Follow Scenario 3, Option B steps
3. Restore from B2 backup
4. Update DNS

**Estimated RTO:** 2-4 hours

---

### Scenario 5: Security Breach

**Impact:** Unauthorized access, potential data theft

**Detection Time:** <1 hour (depends on breach type)

**Immediate Response:**

**Phase 1: Contain (15 minutes)**
```bash
# 1. Enable Cloudflare "Under Attack Mode"
# Via Cloudflare dashboard

# 2. Block attacker IP
sudo ufw deny from ATTACKER_IP

# 3. Isolate compromised service
docker compose stop COMPROMISED_SERVICE

# 4. Snapshot current state (forensics)
sudo cp -r data/ /tmp/breach_snapshot_$(date +%s)
```

**Phase 2: Assess (30 minutes)**
```bash
# 1. Review access logs
sudo grep ATTACKER_IP /var/log/nginx/access.log > breach_analysis.log

# 2. Check database for unauthorized changes
docker compose exec postgres psql -U galion -d galion -c "
  SELECT * FROM audit_logs 
  WHERE created_at > 'BREACH_START_TIME'
  ORDER BY created_at DESC;"

# 3. Check for data exfiltration
sudo grep -i "select.*from.*users" /var/log/nginx/access.log

# 4. Check for backdoors
find . -name "*.php" -o -name "*.sh" -mtime -1
```

**Phase 3: Recover (60 minutes)**
```bash
# 1. Rotate all secrets
./scripts/generate-secrets.sh

# 2. Force logout all users
docker compose exec redis redis-cli FLUSHALL

# 3. Restore from clean backup (before breach)
./scripts/restore-pitr.sh "TIME_BEFORE_BREACH"

# 4. Deploy new secrets
docker compose up -d

# 5. Audit all code changes
git log --since="BREACH_TIME"
```

**Phase 4: Notify (ASAP)**
- Email affected users
- Notify authorities if required (GDPR: 72 hours)
- Post incident report
- Force password resets

**Estimated RTO:** 2-4 hours  
**Compliance:** GDPR notification within 72 hours

---

## Backup Strategy

### Backup Types

**1. Daily Full Backups**
- Frequency: Daily at 2 AM
- Retention: 30 days
- Location: Local + Backblaze B2
- Script: `scripts/backup.sh`

**2. Incremental Backups (WAL Archiving)**
- Frequency: Continuous
- Retention: 7 days
- Location: Local
- Enables: Point-in-time recovery
- Setup: `scripts/incremental-backup.sh setup`

**3. Configuration Backups**
- Frequency: On every change
- Location: Git repository
- Includes: docker-compose.yml, configs/, nginx/

**4. Code Backups**
- Frequency: On every commit
- Location: GitHub
- Includes: All source code

### Backup Verification

**Monthly Test:**
```bash
# 1. Restore to test database
./scripts/restore.sh backups/galion_latest.dump.gz

# 2. Verify data integrity
docker compose exec postgres psql -U galion -d galion -c "
  SELECT COUNT(*) as user_count FROM users;
  SELECT COUNT(*) as task_count FROM tasks;
"

# 3. Compare with production counts
# Should match within small margin

# 4. Test PITR
./scripts/restore-pitr.sh "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')"
```

### Off-site Backup to Backblaze B2

**Setup:**
```bash
# 1. Create B2 account: https://www.backblaze.com/b2

# 2. Create bucket: galion-backups

# 3. Get credentials (Application Key)

# 4. Install B2 CLI
pip3 install b2sdk
b2 authorize-account YOUR_KEY_ID YOUR_APPLICATION_KEY

# 5. Test upload
b2 upload-file galion-backups backups/test.txt test.txt

# 6. Automated sync (already in backup.sh)
# Verify B2_BUCKET_NAME is set in .env
```

**Verification:**
```bash
# List remote backups
b2 ls galion-backups

# Download backup
b2 download-file-by-name galion-backups backups/galion_latest.dump.gz galion_latest.dump.gz
```

---

## Recovery Procedures

### Procedure 1: Service Recovery

**When:** Single service failed

**Steps:**
1. Identify failed service from alerts
2. Run `./scripts/health-check.sh`
3. Restart service: `docker compose restart [service]`
4. If not fixed, check logs
5. If code issue, rollback deployment
6. Monitor for 1 hour

**Verification:**
- Service health check passes
- No errors in logs
- Metrics return to normal
- Users can access features

---

### Procedure 2: Database Recovery

**When:** Database corrupted or lost

**Steps:**
1. Stop all services accessing database
2. Assess damage (can DB start?)
3. If repairable, run VACUUM FULL
4. If not, restore from backup
5. Run database migrations
6. Create indexes
7. Restart all services
8. Verify data integrity

**Verification:**
- Database accepts connections
- All tables present
- Row counts match expected
- Application works correctly

---

### Procedure 3: Complete System Recovery

**When:** Entire server lost

**Steps:**
1. Provision new VPS
2. Run vps-setup.sh
3. Clone repository
4. Restore .env from secure backup
5. Download database backup from B2
6. Restore database
7. Start all services
8. Update DNS
9. Get new SSL certificates
10. Verify all functionality

**Verification:**
- All services running
- Database data correct
- Users can log in
- All features working
- Monitoring operational

---

## Post-Incident Actions

### Immediate (Within 1 hour)
- [ ] Verify system stability
- [ ] Document what happened
- [ ] Create timeline of events
- [ ] Identify root cause

### Short-term (Within 24 hours)
- [ ] Write post-mortem document
- [ ] Share with team
- [ ] Create action items to prevent recurrence
- [ ] Update runbooks

### Long-term (Within 1 week)
- [ ] Implement preventive measures
- [ ] Update monitoring/alerts
- [ ] Test recovery procedures
- [ ] Review DR plan

### Post-Mortem Template

```markdown
# Incident Post-Mortem: [TITLE]

**Date:** YYYY-MM-DD
**Duration:** X hours
**Impact:** [Description]
**Root Cause:** [What actually caused it]

## Timeline
- HH:MM - [Event]
- HH:MM - [Detection]
- HH:MM - [Response started]
- HH:MM - [Issue resolved]

## What Went Well
- [Good things during incident response]

## What Went Wrong
- [Things that didn't work]

## Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]

## Lessons Learned
- [Key takeaways]
```

---

## DR Testing Schedule

### Monthly DR Drill

**Test Procedure:**
```bash
# 1. Create test environment (locally or on test VPS)

# 2. Restore from latest backup
./scripts/restore.sh backups/galion_latest.dump.gz

# 3. Verify application works

# 4. Test point-in-time recovery
./scripts/restore-pitr.sh "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')"

# 5. Document results
# - Time taken
# - Issues encountered
# - Improvements needed

# 6. Update DR plan based on findings
```

### Quarterly Full DR Exercise

**Simulate complete system failure:**

1. Provision new VPS
2. Full recovery from backups
3. Update DNS
4. Test all functionality
5. Time the entire process
6. Document and improve

**Goal:** Complete recovery in <2 hours

---

## Emergency Contacts

### Primary Oncall
- Name: [Your Name]
- Phone: [Phone]
- Email: [Email]

### Secondary Oncall
- Name: [Backup]
- Phone: [Phone]
- Email: [Email]

### Vendor Support
- Hetzner Support: https://www.hetzner.com/support
- Cloudflare Support: https://support.cloudflare.com
- Database Expert: [Name/Company]

### Escalation Path
1. Oncall Engineer (0-15 min)
2. Senior Engineer (15-30 min)
3. CTO (30-60 min)
4. CEO (60+ min, major incident)

---

## DR Resources Checklist

### Must-Have for DR

- [ ] Off-site backups (Backblaze B2)
- [ ] Encrypted .env backup (password manager)
- [ ] Documentation (GitHub, accessible externally)
- [ ] DNS provider access (Cloudflare)
- [ ] VPS provider access (Hetzner)
- [ ] Credit card for emergency provisioning
- [ ] Emergency contacts list
- [ ] Post-mortem templates

### Nice-to-Have

- [ ] Standby VPS (hot spare)
- [ ] Multi-region setup
- [ ] Automated failover
- [ ] DR testing environment
- [ ] Incident response team
- [ ] 24/7 monitoring service

---

## Communication Plan

### During Incident

**Internal:**
1. Post in #incidents Slack channel
2. Update status every 30 minutes
3. Assign roles (incident commander, communicator, etc.)

**External:**
1. Status page update (if you have one)
2. Twitter/social media update
3. Email major customers
4. Post in Discord/community

**Template:**
```
We're experiencing [ISSUE] affecting [SERVICES].
We're actively working on a fix.
ETA for resolution: [TIME]
We'll update you in 30 minutes.
```

### After Incident

**Communication:**
1. Post resolution announcement
2. Thank users for patience
3. Share post-mortem (if appropriate)
4. Explain what was learned

**Template:**
```
The issue affecting [SERVICES] has been resolved.
Duration: [X hours]
Cause: [EXPLANATION]
Prevention: [STEPS TAKEN]
We apologize for the inconvenience.
```

---

## Regular DR Maintenance

### Weekly
- [ ] Verify backups completed successfully
- [ ] Check backup sizes (not too large/small)
- [ ] Verify off-site backups uploaded

### Monthly
- [ ] Test backup restore
- [ ] Review DR plan
- [ ] Update contact information
- [ ] Test alerting system

### Quarterly
- [ ] Full DR drill
- [ ] Update documentation
- [ ] Review and update RTO/RPO targets
- [ ] Train new team members on DR procedures

---

## Appendix: Important Information

### Server Details
- Provider: Hetzner
- IP: 54.37.161.67
- RAM: 16GB
- Storage: 100GB SSD
- OS: Ubuntu 24.04 LTS

### Service Architecture
- See: docker-compose.yml
- Containers: 11 total
- Databases: 2 (galion, galion_studio)

### Backup Locations
- Local: `/home/deploy/galion/backups/`
- Remote: Backblaze B2 bucket `galion-backups`

### Documentation
- GitHub: https://github.com/your-org/galion-platform
- Runbook: docs/RUNBOOK.md
- Troubleshooting: docs/TROUBLESHOOTING.md
- Scaling: docs/SCALING_GUIDE.md

---

**Test your DR plan before you need it.**  
**Hope for the best, prepare for the worst.**  
**Document everything, test regularly.**

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Next DR Drill:** December 10, 2025

