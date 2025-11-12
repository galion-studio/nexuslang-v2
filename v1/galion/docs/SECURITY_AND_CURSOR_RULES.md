# SECURITY & CURSOR AGENT RULES

**Security Baselines + AI Agent Guardrails**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## MISSION

Build a secure platform with:
1. **User Security:** 2FA, encryption, privacy controls
2. **Infrastructure Security:** Least privilege, defense in depth
3. **AI Agent Safety:** Cursor rules to prevent destructive actions

**Philosophy:** Security by design, not as an afterthought.

---

## PART 1: USER SECURITY

### Authentication

**2FA Mandatory:**
- All users MUST enable 2FA within 7 days of signup
- Methods supported:
  - TOTP (Google Authenticator, Authy) – Primary
  - WebAuthn (YubiKey, Touch ID) – Beta
  - SMS (fallback, discouraged)
- Backup codes: 10 single-use codes generated at 2FA setup
- Recovery: Email verification + security questions

**Password Policy:**
- Minimum 12 characters
- Must include: uppercase, lowercase, number, symbol
- No common passwords (check against Have I Been Pwned)
- No password reuse (last 5 passwords)
- Expiry: 90 days (optional, user choice)
- Hashing: bcrypt (cost factor 12)

**Session Management:**
- JWT tokens with 15-minute expiry
- Refresh tokens with 30-day expiry
- Refresh token rotation on use
- Session binding (IP + User-Agent hash)
- Concurrent session limit: 3 devices
- Force logout on password change

**Risk-Based Authentication:**

```python
def calculate_risk_score(request):
    score = 0
    
    # IP reputation (0-30 points)
    if is_vpn(request.ip):
        score += 10
    if is_tor(request.ip):
        score += 20
    if is_known_bad_ip(request.ip):
        score += 30
    
    # Geolocation (0-20 points)
    if is_new_country(request.user, request.geo):
        score += 15
    if is_high_risk_country(request.geo):
        score += 20
    
    # Device (0-20 points)
    if is_new_device(request.user, request.device_fingerprint):
        score += 15
    if is_suspicious_user_agent(request.user_agent):
        score += 10
    
    # Behavior (0-30 points)
    if failed_login_attempts(request.user) > 3:
        score += 20
    if unusual_time_of_day(request.user, request.timestamp):
        score += 10
    
    return score

# Risk thresholds
# 0-20: Low risk → Allow
# 21-50: Medium risk → Require 2FA
# 51-70: High risk → Require 2FA + Email verification
# 71+: Critical risk → Block + Alert security team
```

**Implementation:**
- Store risk signals in Redis (TTL 24 hours)
- Log all auth events to CloudWatch
- Alert on risk score > 70

---

### Authorization

**Role-Based Access Control (RBAC):**

| Role | Permissions |
|------|-------------|
| Guest | Read public content |
| User | CRUD own data, voice interactions |
| Contributor | Create content, collaborate |
| Manager | Manage team, view analytics |
| Admin | Full access, user management |
| Owner | All permissions + billing |

**Attribute-Based Access Control (ABAC):**
- User attributes: role, department, clearance_level
- Resource attributes: sensitivity, owner, created_date
- Environment: time_of_day, ip_address, device_type

**Example Policy:**
```json
{
  "effect": "allow",
  "action": "voice:transcribe",
  "resource": "arn:galion:voice:*",
  "condition": {
    "ip_in_range": ["10.0.0.0/8", "172.16.0.0/12"],
    "time_of_day": "09:00-18:00",
    "user.role": ["user", "admin"]
  }
}
```

**Least Privilege:**
- Default deny (whitelist approach)
- Grant minimum permissions needed
- Time-bound access (expire after 24 hours for sensitive ops)
- Audit trail (who accessed what, when)

---

### Encryption

**Data at Rest:**
- Algorithm: AES-256-GCM
- Key Management: AWS KMS
- Key Rotation: Annual (automated)
- Scope:
  - RDS Postgres (database encryption)
  - ElastiCache Redis (encryption at rest)
  - S3 buckets (SSE-KMS)
  - EBS volumes (encrypted)

**Data in Transit:**
- TLS 1.3 (minimum TLS 1.2)
- Cipher suites:
  - TLS_AES_128_GCM_SHA256
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
- Certificate: ACM (auto-renewal)
- HSTS: Enabled (max-age=31536000, includeSubDomains)
- Certificate Transparency: Enabled

**End-to-End Encryption (Future):**
- Voice recordings encrypted client-side
- Keys derived from user password (PBKDF2, 100k iterations)
- Server cannot decrypt (zero-knowledge)

**Standards Alignment:**
- NIST 800-53 (SC-8, SC-13, SC-28)
- FIPS 140-3 (use FIPS endpoints for KMS)
- PQC-ready (plan for hybrid X25519+Kyber)

---

### Privacy & Data Governance

**GDPR Compliance:**
- Legal basis: Consent (voice data), Contract (service usage)
- Data minimization: Collect only what's needed
- Purpose limitation: Use data only for stated purpose
- Storage limitation: Delete after retention period
- Right to access: User dashboard to view all data
- Right to erasure: Delete account + all data within 30 days
- Right to portability: Export data in JSON format
- Data Protection Officer: Designated (email: dpo@galion.app)

**CCPA Compliance:**
- Notice at collection: Privacy policy linked at signup
- Right to know: User dashboard
- Right to delete: Same as GDPR
- Right to opt-out: Disable voice data capture
- Do Not Sell: We don't sell data (stated in policy)

**Data Residency:**
- EU users: Data stored in `eu-central-1`
- US users: Data stored in `us-east-1`
- No cross-region transfer except anonymized aggregates
- Routing: Geo-based (CloudFront + Lambda@Edge)

**PII Taxonomy:**

| Data Type | PII Level | Retention | Encryption |
|-----------|-----------|-----------|------------|
| Email | High | Account lifetime | KMS |
| Password hash | High | Account lifetime | bcrypt |
| Voice recordings | High | 90 days | KMS + Client-side |
| Transcripts | Medium | 90 days | KMS |
| IP address | Medium | 30 days | Hashed |
| Device fingerprint | Low | 90 days | Hashed |
| Usage analytics | Low | 2 years | Anonymized |

**Data Loss Prevention (DLP):**
- Automated PII detection (AWS Macie)
- Redaction: Credit cards, SSNs, phone numbers
- Manual review: Weekly audit of flagged data
- Alerts: Email + Slack on PII exposure

---

### Incident Response

**Phases:**
1. **Preparation:** Runbooks, contact list, tools
2. **Detection:** GuardDuty, Security Hub, CloudWatch Alarms
3. **Containment:** Isolate affected resources, revoke credentials
4. **Eradication:** Patch vulnerabilities, remove malware
5. **Recovery:** Restore from backups, verify integrity
6. **Lessons Learned:** Post-mortem, update runbooks

**Severity Levels:**

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| P0 | Data breach, system down | 15 min | CEO + CTO |
| P1 | Security vulnerability | 1 hour | CTO + Security |
| P2 | Service degradation | 4 hours | Engineering |
| P3 | Minor issue | 24 hours | Engineering |

**Contacts:**
- Security Team: security@galion.app
- On-Call: PagerDuty rotation
- Legal: legal@galion.app
- PR: pr@galion.app

**Breach Notification:**
- GDPR: 72 hours to supervisory authority
- CCPA: No specific timeline (reasonable)
- Users: Email within 72 hours
- Public: Blog post if > 1000 users affected

---

## PART 2: INFRASTRUCTURE SECURITY

### Network Security

**Defense in Depth:**
```
Internet
  ↓
Cloudflare (WAF, DDoS protection)
  ↓
AWS Shield (DDoS)
  ↓
ALB (HTTPS only, ACM cert)
  ↓
Security Groups (least privilege)
  ↓
ECS Tasks (private subnets, no public IP)
  ↓
RDS/Redis (private subnets, SG whitelist)
```

**Security Groups (Least Privilege):**
- ALB SG: Allow 443 from Cloudflare IPs only
- ECS SG: Allow all from ALB SG only
- RDS SG: Allow 5432 from ECS SG only
- Redis SG: Allow 6379 from ECS SG only
- No 0.0.0.0/0 ingress rules (except ALB from Cloudflare)

**WAF Rules (Beta):**
- Rate limiting: 100 requests/5min per IP
- Geo-blocking: Allow US, EU only (alpha)
- SQL injection: AWS Managed Rules
- XSS: AWS Managed Rules
- Known bad IPs: AWS IP Reputation List
- Custom: Block user-agents (scrapers, bots)

**DDoS Protection:**
- Cloudflare (Layer 3/4/7)
- AWS Shield Standard (Layer 3/4)
- AWS Shield Advanced (optional, $3k/month)

---

### Compute Security

**ECS Task Security:**
- Non-root user (UID 1000)
- Read-only root filesystem
- No privileged mode
- Drop all capabilities except NET_BIND_SERVICE
- Secrets via Secrets Manager (not env vars)
- Image scanning (ECR + Clair)

**Example Task Definition:**
```json
{
  "containerDefinitions": [{
    "name": "api-gateway",
    "image": "galion/api-gateway:latest",
    "user": "1000",
    "readonlyRootFilesystem": true,
    "linuxParameters": {
      "capabilities": {
        "drop": ["ALL"],
        "add": ["NET_BIND_SERVICE"]
      }
    },
    "secrets": [
      {
        "name": "DB_PASSWORD",
        "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:db-password"
      }
    ]
  }]
}
```

**EC2 Instance Security:**
- AMI: ECS-optimized (patched monthly)
- SSM Session Manager (no SSH keys)
- IMDSv2 required (prevent SSRF)
- CloudWatch agent (logs, metrics)
- Auto-patching: AWS Systems Manager Patch Manager

**Container Image Security:**
- Base images: Official (nginx, python, node)
- Scan on build: Trivy, Grype
- Scan on push: ECR (Clair)
- Vulnerability threshold: Block on HIGH/CRITICAL
- SBOM: Generate with Syft

---

### Data Security

**RDS Security:**
- Encryption at rest: AES-256 (KMS)
- Encryption in transit: TLS (require SSL)
- IAM authentication: Enabled (no passwords)
- Backups: Encrypted, 7-day retention
- Multi-AZ: Yes (beta)
- Public access: Disabled
- VPC: Private subnets only

**S3 Security:**
- Block public access: Enabled (all 4 settings)
- Encryption: SSE-KMS (default)
- Versioning: Enabled
- MFA Delete: Enabled (prod)
- Bucket policies: Least privilege
- Access logging: Enabled (to separate bucket)
- Object Lock: Enabled (compliance mode, 7 years for audit logs)

**Secrets Management:**
- AWS Secrets Manager (not env vars)
- Rotation: Automatic (30 days for DB passwords)
- Access: IAM roles only (no IAM users)
- Audit: CloudTrail logs all access
- Encryption: KMS (separate key per secret type)

---

### Monitoring & Logging

**CloudWatch Logs:**
- All ECS tasks → `/ecs/galion/{service}`
- ALB access logs → S3 (encrypted)
- VPC Flow Logs → S3 (encrypted)
- CloudTrail → S3 (encrypted, immutable)
- Retention: 90 days (CloudWatch), 7 years (S3)

**GuardDuty:**
- Threat detection (ML-based)
- Findings: SNS → Security team
- Auto-remediation: Lambda (isolate compromised instances)

**Security Hub:**
- Aggregate findings (GuardDuty, Macie, Inspector)
- Compliance checks: CIS AWS Foundations, PCI DSS
- Weekly reports: Email to security team

**CloudTrail:**
- All API calls logged
- Multi-region: Yes
- Log file validation: Enabled
- S3 bucket: Separate account (security account)
- Alerts: Unauthorized API calls, root account usage

**Metrics & Alarms:**
- Failed login attempts (> 10/min)
- Unauthorized API calls
- Root account usage
- Security group changes
- IAM policy changes
- S3 bucket policy changes

---

## PART 3: CURSOR AGENT GUARDRAILS

### Problem Statement

**Risk:** Giving Cursor "full control" could lead to:
- Accidental deletion of critical files (database schemas, configs)
- Destructive git operations (force push, hard reset)
- Unauthorized API calls (delete production resources)
- Infinite loops (expensive AWS bills)
- Data exfiltration (copy sensitive data to external services)

**Goal:** Enable Cursor to be productive while preventing catastrophic errors.

---

### Cursor Safety Rules

**1. File System Restrictions**

**Allowlist Approach:**
```yaml
# .cursor/rules.yaml
filesystem:
  allowed_paths:
    - services/*/app/**/*.py
    - services/*/app/**/*.go
    - services/*/Dockerfile
    - services/*/requirements.txt
    - services/*/go.mod
    - docs/**/*.md
    - infrastructure/terraform/**/*.tf
    - scripts/**/*.sh
    - scripts/**/*.ps1
  
  blocked_paths:
    - .git/**
    - .env
    - .env.*
    - database/init.sql
    - database/migrations/**
    - k8s/secrets.yaml
    - **/*.pem
    - **/*.key
    - **/id_rsa*
  
  read_only_paths:
    - README.md
    - LICENSE
    - .gitignore
    - docker-compose.yml
    - docker-compose.*.yml
```

**2. Command Restrictions**

**Blocked Commands:**
```yaml
commands:
  blocked:
    # Destructive git operations
    - git push --force
    - git push -f
    - git reset --hard
    - git clean -fd
    - git branch -D
    
    # Destructive file operations
    - rm -rf /
    - rm -rf *
    - dd if=*
    - mkfs.*
    
    # Destructive AWS operations
    - aws s3 rb --force
    - aws rds delete-db-instance
    - aws ec2 terminate-instances
    - aws iam delete-*
    
    # Destructive Docker operations
    - docker system prune -a
    - docker volume rm $(docker volume ls -q)
    
    # Dangerous network operations
    - curl * | bash
    - wget * | sh
    - nc -e /bin/sh
```

**Require Confirmation:**
```yaml
commands:
  require_confirmation:
    - git push
    - git merge
    - git rebase
    - docker-compose down -v
    - terraform apply
    - terraform destroy
    - aws s3 rm --recursive
    - kubectl delete
```

**3. Dry-Run Mode**

**Always Preview Changes:**
```python
class CursorSafetyWrapper:
    def execute_command(self, command: str) -> dict:
        # Parse command
        parsed = parse_command(command)
        
        # Check if blocked
        if is_blocked(parsed):
            return {"error": "Command blocked by safety rules"}
        
        # Check if requires confirmation
        if requires_confirmation(parsed):
            # Show dry-run preview
            preview = dry_run(parsed)
            
            # Ask user for confirmation
            confirmed = ask_user_confirmation(preview)
            
            if not confirmed:
                return {"error": "User cancelled operation"}
        
        # Execute command
        result = run_command(parsed)
        
        # Log to audit trail
        log_command(parsed, result)
        
        return result
```

**4. Rate Limiting**

**Prevent Infinite Loops:**
```yaml
rate_limits:
  commands_per_minute: 30
  api_calls_per_minute: 60
  file_writes_per_minute: 100
  total_cost_per_hour: $10  # AWS API calls
```

**5. Sandboxing**

**Isolated Temp Directories:**
```yaml
sandbox:
  temp_dir: /tmp/cursor-sandbox-{session_id}/
  auto_cleanup: true
  max_size: 1GB
  allowed_network: false  # No outbound connections from sandbox
```

**6. Audit Logging**

**Log All Actions:**
```python
# .cursor/audit.log
{
  "timestamp": "2025-11-09T10:30:00Z",
  "session_id": "abc123",
  "user": "admin@galion.app",
  "ip": "192.168.1.100",
  "command": "terraform apply",
  "files_modified": ["infrastructure/terraform/main.tf"],
  "result": "success",
  "cost": "$0.05"
}
```

**7. Dual Control**

**Critical Operations Require Two Approvals:**
```yaml
dual_control:
  required_for:
    - terraform destroy
    - aws rds delete-db-instance
    - git push origin main --force
    - kubectl delete namespace production
  
  approvers:
    - admin@galion.app
    - cto@galion.app
```

---

### Cursor Personality & Commands

**Admin Personality V2 (Grok-inspired):**

**Traits:**
- Direct and honest (no BS)
- Proactive (suggests improvements)
- Safety-conscious (warns before destructive ops)
- Humorous (lightens the mood)
- Transparent (explains reasoning)

**Example Interactions:**

**User:** "Delete all logs"  
**Cursor:** "🚨 Hold up! That's a destructive operation. Which logs specifically? Options:
1. CloudWatch logs (last 30 days)
2. Local log files (./logs/)
3. S3 archived logs (last 90 days)
Also, are you sure? Logs are useful for debugging. Maybe archive instead?"

**User:** "Deploy to production"  
**Cursor:** "✅ Deploying to production. Here's what I'm doing:
1. Running tests (30s)
2. Building Docker images (2m)
3. Pushing to ECR (1m)
4. Updating ECS services (3m)
5. Health checks (1m)
Total ETA: ~7 minutes. I'll notify you when done. ☕"

**User:** "Why is the API slow?"  
**Cursor:** "🔍 Investigating... Found 3 issues:
1. RDS CPU at 85% (needs scaling)
2. No Redis caching on /api/users (easy fix)
3. N+1 queries in user_service.py:42 (needs optimization)
Want me to fix #2 and #3 now? #1 requires AWS changes (your approval needed)."

**Command Grammar:**

**Natural Language:**
- "Show me the logs for auth-service"
- "Deploy voice-service to alpha"
- "Scale RDS to db.t4g.large"
- "What's the status of all services?"

**Structured Commands:**
```bash
# Cursor CLI
cursor status              # Show system status
cursor logs <service>      # Show logs
cursor deploy <service>    # Deploy service
cursor scale <resource>    # Scale resource
cursor rollback <service>  # Rollback deployment
cursor backup <database>   # Backup database
cursor restore <backup>    # Restore from backup
```

---

### Implementation

**1. Install Cursor Safety Extension:**
```bash
# .cursor/extensions/safety.py
import os
import re
from typing import List, Dict

class CursorSafety:
    def __init__(self, config_path: str = ".cursor/rules.yaml"):
        self.config = load_yaml(config_path)
        self.audit_log = AuditLog(".cursor/audit.log")
    
    def check_command(self, command: str) -> Dict:
        # Check if blocked
        if self.is_blocked(command):
            return {"allowed": False, "reason": "Command blocked"}
        
        # Check if requires confirmation
        if self.requires_confirmation(command):
            preview = self.dry_run(command)
            return {"allowed": False, "preview": preview, "requires_confirmation": True}
        
        # Check rate limits
        if self.exceeds_rate_limit():
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        return {"allowed": True}
    
    def is_blocked(self, command: str) -> bool:
        for pattern in self.config["commands"]["blocked"]:
            if re.match(pattern, command):
                return True
        return False
    
    def requires_confirmation(self, command: str) -> bool:
        for pattern in self.config["commands"]["require_confirmation"]:
            if re.match(pattern, command):
                return True
        return False
    
    def dry_run(self, command: str) -> str:
        # Simulate command and show what would happen
        # (implementation depends on command type)
        pass
    
    def log_command(self, command: str, result: Dict):
        self.audit_log.write({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result
        })
```

**2. Configure Cursor Settings:**
```json
// .cursor/settings.json
{
  "safety": {
    "enabled": true,
    "rules_file": ".cursor/rules.yaml",
    "audit_log": ".cursor/audit.log",
    "require_confirmation": true,
    "dry_run_by_default": true
  },
  "personality": {
    "style": "grok_v2",
    "traits": ["direct", "proactive", "safety_conscious", "humorous"],
    "adaptation": {
      "user_tone": true,
      "user_expertise": true,
      "time_of_day": true
    }
  }
}
```

---

## SECURITY CHECKLIST

### Pre-Launch (Alpha)

- [ ] 2FA mandatory for all users
- [ ] Password policy enforced
- [ ] JWT tokens with short expiry
- [ ] TLS 1.3 on all endpoints
- [ ] RDS encryption at rest
- [ ] S3 encryption at rest
- [ ] Secrets in Secrets Manager (not env vars)
- [ ] Security groups (least privilege)
- [ ] GuardDuty enabled
- [ ] CloudTrail enabled
- [ ] Cursor safety rules configured

### Post-Launch (Beta)

- [ ] WAF enabled on ALB
- [ ] Rate limiting (100 req/5min)
- [ ] Geo-blocking (US, EU only)
- [ ] Multi-AZ RDS
- [ ] Automated backups (7 days)
- [ ] Security Hub enabled
- [ ] Macie enabled (PII scanning)
- [ ] Penetration testing (external firm)
- [ ] Bug bounty program (HackerOne)

### Production (1.0)

- [ ] SOC 2 Type I audit started
- [ ] ISO 27001 certification started
- [ ] DDoS protection (Shield Advanced)
- [ ] Web Application Firewall (advanced rules)
- [ ] Incident response runbooks
- [ ] Security training for all employees
- [ ] Third-party security audits (quarterly)
- [ ] Compliance audits (annual)

---

**Built with First Principles**  
**Status:** Ready to Secure  
**Let's lock it down.** 🔒

