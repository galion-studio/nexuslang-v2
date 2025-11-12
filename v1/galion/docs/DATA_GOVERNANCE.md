# DATA GOVERNANCE

**GDPR + CCPA Compliance Strategy**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## OVERVIEW

**Mission:** Handle user data with radical transparency and full compliance.

**Regulations:**
- GDPR (EU General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- Future: CPRA, VCDPA, CPA, etc.

**Principles:**
1. **Transparency:** Users know what data we collect and why
2. **Minimization:** Collect only what's necessary
3. **Purpose Limitation:** Use data only for stated purposes
4. **Storage Limitation:** Delete data when no longer needed
5. **Security:** Protect data with encryption and access controls
6. **User Rights:** Easy access, correction, deletion, portability

---

## DATA INVENTORY

### Personal Data Collected

| Data Type | Category | Purpose | Legal Basis | Retention |
|-----------|----------|---------|-------------|-----------|
| Email | Identity | Account, communication | Contract | Account lifetime |
| Password hash | Security | Authentication | Contract | Account lifetime |
| Name (optional) | Identity | Personalization | Consent | Account lifetime |
| Voice recordings | Biometric | Voice recognition training | Consent | 90 days |
| Voice transcripts | Usage | Service improvement | Consent | 90 days |
| IP address | Technical | Security, fraud prevention | Legitimate interest | 30 days |
| Device fingerprint | Technical | Security | Legitimate interest | 90 days |
| Usage analytics | Behavioral | Service improvement | Legitimate interest | 2 years (anonymized) |
| Payment info | Financial | Billing | Contract | 7 years (legal requirement) |
| Support tickets | Communication | Customer service | Contract | 3 years |

### Special Categories (GDPR Art. 9)

**Biometric Data:**
- Voice recordings (for voice recognition)
- Legal basis: Explicit consent
- Extra protections: Client-side encryption, separate storage, strict access controls

**Health Data:**
- None collected (not applicable)

---

## LEGAL BASIS

### GDPR (EU Users)

**Contract (Art. 6(1)(b)):**
- Email, password: Necessary to provide service
- Payment info: Necessary for billing

**Consent (Art. 6(1)(a)):**
- Voice recordings: Opt-in with clear explanation
- Marketing emails: Opt-in checkbox (not pre-checked)
- Analytics cookies: Cookie banner with opt-out

**Legitimate Interest (Art. 6(1)(f)):**
- IP address, device fingerprint: Fraud prevention, security
- Usage analytics: Service improvement (anonymized)

**Legal Obligation (Art. 6(1)(c)):**
- Payment records: Tax compliance (7 years)

### CCPA (California Users)

**Categories Collected:**
- Identifiers (email, IP)
- Commercial information (purchase history)
- Internet activity (usage analytics)
- Biometric information (voice recordings)

**Business Purpose:**
- Provide service
- Improve service quality
- Fraud prevention
- Legal compliance

**No Sale of Data:**
- We do not sell personal information
- Stated clearly in privacy policy

---

## DATA RESIDENCY

### Regional Storage

**EU Users:**
- Data stored in: `eu-central-1` (Frankfurt)
- Processing: Within EU only
- Transfers: None (except anonymized aggregates)

**US Users:**
- Data stored in: `us-east-1` (Virginia)
- Processing: Within US only
- Transfers: None (except anonymized aggregates)

**Routing Logic:**
```python
def route_user_data(user_ip: str, user_country: str) -> str:
    # Determine region based on IP geolocation
    if user_country in EU_COUNTRIES:
        return "eu-central-1"
    elif user_country in ["US", "CA", "MX"]:
        return "us-east-1"
    else:
        # Default to US (with consent)
        return "us-east-1"

# Store region in user profile
user.data_region = route_user_data(request.ip, request.geo.country)
```

### Cross-Border Transfers

**EU → US (if needed):**
- Mechanism: Standard Contractual Clauses (SCCs)
- Supplementary measures: Encryption, access controls
- Data: Only anonymized aggregates

**US → EU (if needed):**
- Mechanism: SCCs
- Data: Only anonymized aggregates

**No transfers for:**
- Voice recordings (stay in region)
- PII (stay in region)
- Raw usage data (stay in region)

---

## USER RIGHTS

### GDPR Rights

**1. Right to Access (Art. 15):**
- User dashboard: View all personal data
- Export: JSON format, includes all data
- Response time: Instant (dashboard), 30 days (export)

**2. Right to Rectification (Art. 16):**
- User dashboard: Edit profile, email, name
- Request: Email support@galion.app
- Response time: 7 days

**3. Right to Erasure (Art. 17):**
- User dashboard: "Delete Account" button
- Process: Delete all data within 30 days
- Exceptions: Legal obligations (payment records for 7 years)
- Confirmation: Email sent when complete

**4. Right to Restriction (Art. 18):**
- User dashboard: "Pause Account" (stop processing)
- Effect: No voice capture, no analytics, no emails
- Response time: Instant

**5. Right to Data Portability (Art. 20):**
- User dashboard: "Export Data" button
- Format: JSON (machine-readable)
- Includes: All personal data, usage history, voice transcripts
- Response time: Instant (< 1 GB), 24 hours (> 1 GB)

**6. Right to Object (Art. 21):**
- User dashboard: Opt-out toggles
- Marketing emails: Unsubscribe link
- Analytics: Cookie banner opt-out
- Voice capture: Consent toggle

**7. Right to Withdraw Consent (Art. 7(3)):**
- User dashboard: Toggle off consent
- Effect: Stop voice capture, delete existing recordings
- Response time: Instant

### CCPA Rights

**1. Right to Know:**
- Same as GDPR Right to Access
- Categories collected, purposes, sources, third parties

**2. Right to Delete:**
- Same as GDPR Right to Erasure
- Exceptions: Legal obligations, fraud prevention

**3. Right to Opt-Out of Sale:**
- Not applicable (we don't sell data)
- Stated in privacy policy

**4. Right to Non-Discrimination:**
- No price differences for exercising rights
- No service quality differences

---

## DATA LIFECYCLE

### Collection

**Consent Flow:**
```
User signs up
  ↓
Privacy policy shown (summary + full text)
  ↓
User checks "I agree" (required)
  ↓
Account created
  ↓
First voice interaction
  ↓
Voice consent dialog shown
  ↓
User chooses "Allow" or "Deny"
  ↓
If Allow: Voice capture enabled
If Deny: Voice works but no capture
```

**Consent Storage:**
```json
{
  "user_id": "uuid",
  "consents": [
    {
      "type": "terms_of_service",
      "version": "1.0",
      "granted_at": "2025-11-09T10:00:00Z",
      "ip": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    },
    {
      "type": "voice_capture",
      "version": "1.0",
      "granted_at": "2025-11-09T10:05:00Z",
      "ip": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

### Processing

**Purpose Limitation:**
- Voice recordings: Only for voice recognition training
- Transcripts: Only for service improvement
- Usage analytics: Only for product development
- No secondary uses without new consent

**Data Minimization:**
- Don't collect name if not needed
- Don't collect location if not needed
- Anonymize analytics after 30 days

### Storage

**Encryption:**
- At rest: AES-256-GCM (KMS)
- In transit: TLS 1.3
- Client-side (future): User-controlled keys

**Access Controls:**
- Role-based: Only authorized employees
- Audit logs: All access logged
- MFA required: For admin access

**Backups:**
- Encrypted: Same as primary storage
- Retention: 7 days (RDS), 30 days (S3)
- Deletion: When primary data deleted

### Retention

**Retention Periods:**

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| Email, password | Account lifetime | Service provision |
| Voice recordings | 90 days | Training data collection |
| Voice transcripts | 90 days | Service improvement |
| IP address | 30 days | Security, fraud prevention |
| Usage analytics | 2 years (anonymized) | Product development |
| Payment records | 7 years | Legal requirement (tax) |
| Support tickets | 3 years | Legal requirement (disputes) |

**Automated Deletion:**
```python
# Daily cron job
def delete_expired_data():
    # Voice recordings older than 90 days
    delete_s3_objects(
        bucket="galion-app-data-us",
        prefix="raw/audio/voice_captures/",
        older_than_days=90
    )
    
    # IP addresses older than 30 days
    delete_db_records(
        table="auth_logs",
        column="created_at",
        older_than_days=30
    )
    
    # Anonymize analytics older than 30 days
    anonymize_db_records(
        table="usage_analytics",
        columns=["user_id", "ip", "device_fingerprint"],
        older_than_days=30
    )
```

### Deletion

**Account Deletion Flow:**
```
User clicks "Delete Account"
  ↓
Confirmation dialog (explain consequences)
  ↓
User confirms
  ↓
Account marked for deletion (30-day grace period)
  ↓
Email sent: "Account scheduled for deletion"
  ↓
30 days pass
  ↓
Automated deletion job runs:
  1. Delete voice recordings (S3)
  2. Delete transcripts (S3)
  3. Delete user profile (RDS)
  4. Delete auth logs (RDS)
  5. Anonymize usage analytics (RDS)
  6. Keep payment records (legal requirement)
  ↓
Email sent: "Account deleted"
```

**Right to Be Forgotten:**
- Immediate deletion (no grace period) if requested
- Exceptions: Legal obligations (payment records)
- Confirmation: Email + deletion certificate

---

## DATA PROTECTION IMPACT ASSESSMENT (DPIA)

**When Required (GDPR Art. 35):**
- High risk processing (biometric data)
- Large-scale processing
- New technologies

**Voice Capture DPIA:**

**1. Description:**
- Collect voice recordings for training
- Store in S3 (encrypted)
- Process with Whisper (STT)
- Retain for 90 days

**2. Necessity & Proportionality:**
- Necessary: Yes (improve voice recognition accuracy)
- Proportionate: Yes (limited retention, user consent)

**3. Risks:**
- Unauthorized access (mitigated by encryption, access controls)
- Data breach (mitigated by encryption, monitoring)
- Re-identification (mitigated by anonymization after 90 days)

**4. Measures:**
- Encryption at rest (KMS)
- Encryption in transit (TLS 1.3)
- Access controls (IAM, MFA)
- Audit logs (CloudTrail)
- Automated deletion (90 days)
- User consent (opt-in)

**5. Conclusion:**
- Risks acceptable with mitigations
- Proceed with voice capture

---

## DATA BREACH RESPONSE

### Detection

**Monitoring:**
- GuardDuty: Threat detection
- Macie: PII exposure
- CloudTrail: Unauthorized access
- CloudWatch: Anomalous activity

**Alerts:**
- Email: security@galion.app
- Slack: #security-alerts
- PagerDuty: On-call engineer

### Containment

**Immediate Actions:**
1. Isolate affected resources (security group changes)
2. Revoke compromised credentials (IAM)
3. Enable MFA on all accounts
4. Snapshot affected data (forensics)

### Assessment

**Questions:**
- What data was accessed?
- How many users affected?
- Was data exfiltrated?
- What was the attack vector?

**Severity:**
- P0: > 1000 users, sensitive data (PII, payment info)
- P1: 100-1000 users, less sensitive data
- P2: < 100 users, non-sensitive data

### Notification

**GDPR (72 hours to supervisory authority):**
```
To: [Supervisory Authority]
Subject: Data Breach Notification

Date: 2025-11-09
Organization: Galion.app
DPO: dpo@galion.app

Breach Details:
- Date discovered: 2025-11-09 10:00 UTC
- Date occurred: 2025-11-08 22:00 UTC (estimated)
- Data affected: Email addresses, voice transcripts
- Users affected: 500 (EU users only)
- Cause: SQL injection vulnerability
- Mitigation: Vulnerability patched, passwords reset

Risk Assessment:
- Likelihood of harm: Medium
- Severity of harm: Low (no payment info, no passwords)

Measures Taken:
- Patched vulnerability
- Reset all user passwords
- Enabled MFA for all users
- Notified affected users

Contact: security@galion.app
```

**Users (72 hours):**
```
Subject: Security Incident Notification

Dear [User],

We are writing to inform you of a security incident that may have affected your account.

What Happened:
On November 8, 2025, we discovered unauthorized access to our database. The attacker accessed email addresses and voice transcripts for 500 users, including yours.

What Was NOT Affected:
- Passwords (encrypted, not compromised)
- Payment information (not accessed)
- Voice recordings (not accessed)

What We're Doing:
- Patched the vulnerability
- Reset your password (you'll need to set a new one)
- Enabled mandatory 2FA for all accounts
- Hired external security firm to audit our systems

What You Should Do:
1. Set a new password (link below)
2. Enable 2FA (required)
3. Monitor your email for suspicious activity
4. Contact us with questions: security@galion.app

We sincerely apologize for this incident. Your trust is our priority.

Galion.app Security Team
```

---

## PRIVACY POLICY (SUMMARY)

**Full policy:** https://galion.app/privacy

**What We Collect:**
- Email, password (to provide service)
- Voice recordings (with your consent, to improve accuracy)
- Usage data (to improve service)

**Why We Collect:**
- Provide voice-first AI service
- Improve voice recognition accuracy
- Prevent fraud and abuse

**How We Protect:**
- Encryption (AES-256 at rest, TLS 1.3 in transit)
- Access controls (only authorized employees)
- Regular security audits

**Your Rights:**
- Access your data (user dashboard)
- Delete your data (delete account button)
- Export your data (export button)
- Opt-out of voice capture (consent toggle)

**Data Retention:**
- Voice recordings: 90 days
- Account data: Until you delete your account
- Payment records: 7 years (legal requirement)

**Contact:**
- Privacy questions: privacy@galion.app
- Data Protection Officer: dpo@galion.app

---

## COMPLIANCE CHECKLIST

### GDPR

- [ ] Privacy policy published
- [ ] Cookie banner with opt-out
- [ ] Consent flows implemented
- [ ] User dashboard (access, delete, export)
- [ ] Data Processing Agreement (DPA) with vendors
- [ ] DPIA for voice capture
- [ ] DPO appointed
- [ ] Breach notification process
- [ ] Records of processing activities
- [ ] Data retention policies

### CCPA

- [ ] Privacy policy published
- [ ] "Do Not Sell" link (not applicable, but stated)
- [ ] User dashboard (know, delete)
- [ ] Non-discrimination policy
- [ ] Authorized agent process
- [ ] Verifiable consumer request process

### General

- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Access controls (RBAC)
- [ ] Audit logs (CloudTrail)
- [ ] Automated deletion (lifecycle policies)
- [ ] Security monitoring (GuardDuty, Macie)
- [ ] Incident response plan
- [ ] Employee training (annual)

---

**Built with First Principles**  
**Status:** Compliance Ready  
**Let's respect user privacy.** 🔐

