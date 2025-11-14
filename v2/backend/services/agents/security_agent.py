"""
Security Agent - Specialized in Security Analysis and Hardening

This agent handles:
- Vulnerability scanning and assessment
- Security policy creation and enforcement
- Code security analysis
- Infrastructure security auditing
- Compliance checking
- Threat modeling and risk assessment
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """Specialized security agent for threat analysis and security hardening."""

    def __init__(self, name: str = "security_agent", **kwargs):
        super().__init__(
            name=name,
            description="Specialized in security analysis, vulnerability assessment, and security hardening",
            capabilities=[
                "vulnerability_scanning", "threat_modeling", "security_auditing",
                "code_security", "infrastructure_security", "compliance_checking",
                "incident_response", "security_policy", "risk_assessment"
            ],
            personality={
                "expertise_level": "expert",
                "communication_style": "analytical",
                "specialties": ["security", "risk_management", "compliance"]
            },
            **kwargs
        )

        # Security knowledge base
        self.security_patterns = {
            "owasp_top_10": self._get_owasp_patterns(),
            "compliance": self._get_compliance_patterns(),
            "encryption": self._get_encryption_patterns(),
            "authentication": self._get_authentication_patterns(),
            "monitoring": self._get_security_monitoring_patterns()
        }

        # Vulnerability database (simplified)
        self.vulnerability_db = self._load_vulnerability_database()

    def _get_owasp_patterns(self) -> Dict[str, Any]:
        """Get OWASP Top 10 security patterns and fixes."""
        return {
            "injection": {
                "description": "Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query",
                "prevention": [
                    "Use parameterized queries or prepared statements",
                    "Use safe APIs that automatically escape special characters",
                    "Validate and sanitize all user inputs",
                    "Use positive whitelisting for input validation"
                ],
                "code_example": """
# SAFE: Parameterized query
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password_hash))

# UNSAFE: String concatenation
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
"""
            },
            "broken_authentication": {
                "description": "Functions related to authentication and session management are often implemented incorrectly",
                "prevention": [
                    "Use multi-factor authentication",
                    "Implement proper session management",
                    "Use secure password storage (bcrypt, Argon2)",
                    "Implement proper logout and session timeout",
                    "Use secure, random session IDs"
                ]
            },
            "sensitive_data_exposure": {
                "description": "Many web applications and APIs do not properly protect sensitive data",
                "prevention": [
                    "Encrypt sensitive data at rest and in transit",
                    "Use proper key management",
                    "Avoid storing sensitive data unnecessarily",
                    "Implement proper access controls",
                    "Use TLS 1.3 for data in transit"
                ]
            },
            "xml_external_entities": {
                "description": "Many older or poorly configured XML processors evaluate external entity references",
                "prevention": [
                    "Disable XML external entity processing",
                    "Use less complex data formats like JSON",
                    "Patch or upgrade XML processors",
                    "Use positive validation and sanitization"
                ]
            },
            "broken_access_control": {
                "description": "Restrictions on what authenticated users are allowed to do are often not properly enforced",
                "prevention": [
                    "Implement proper access control mechanisms",
                    "Use role-based access control (RBAC)",
                    "Deny by default, allow by exception",
                    "Validate permissions on every request",
                    "Use the principle of least privilege"
                ]
            }
        }

    def _get_compliance_patterns(self) -> Dict[str, Any]:
        """Get compliance frameworks and requirements."""
        return {
            "gdpr": {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "Data minimization - only collect necessary data",
                    "Purpose limitation - use data only for stated purposes",
                    "Storage limitation - retain data only as long as necessary",
                    "Data subject rights - honor access, rectification, erasure requests",
                    "Data protection by design and default",
                    "Data breach notification within 72 hours"
                ],
                "controls": [
                    "Implement data encryption at rest and in transit",
                    "Regular data protection impact assessments",
                    "Privacy by design principles",
                    "Data subject consent management",
                    "Cross-border data transfer safeguards"
                ]
            },
            "soc2": {
                "name": "SOC 2",
                "trust_principles": [
                    "Security - protection against unauthorized access",
                    "Availability - system availability for operation",
                    "Processing Integrity - accurate processing of data",
                    "Confidentiality - protection of confidential information",
                    "Privacy - collection and use of personal information"
                ],
                "controls": [
                    "Access control policies and procedures",
                    "Change management processes",
                    "Incident response procedures",
                    "Risk assessment and management",
                    "Vendor management processes"
                ]
            },
            "iso27001": {
                "name": "ISO 27001",
                "domains": [
                    "Information security policies",
                    "Organization of information security",
                    "Human resource security",
                    "Asset management",
                    "Access control",
                    "Cryptography",
                    "Physical and environmental security",
                    "Operations security",
                    "Communications security",
                    "System acquisition, development and maintenance",
                    "Supplier relationships",
                    "Information security incident management",
                    "Information security aspects of business continuity",
                    "Compliance"
                ]
            }
        }

    def _get_encryption_patterns(self) -> Dict[str, Any]:
        """Get encryption and cryptography patterns."""
        return {
            "password_hashing": """
# Python example using bcrypt
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Usage
hashed_password = hash_password("user_password")
is_valid = verify_password("user_password", hashed_password)
""",
            "data_encryption": """
# AES encryption example
from cryptography.fernet import Fernet

def encrypt_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()

# Usage
key = Fernet.generate_key()
encrypted = encrypt_data("sensitive_data", key)
decrypted = decrypt_data(encrypted, key)
""",
            "tls_configuration": """
# Nginx SSL/TLS configuration
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL certificate
    ssl_certificate /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    # SSL/TLS settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Other security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
"""
        }

    def _get_authentication_patterns(self) -> Dict[str, Any]:
        """Get authentication and authorization patterns."""
        return {
            "jwt_authentication": """
# JWT Authentication implementation
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

# Usage
token = create_access_token({"user_id": 123})
user_data = verify_token(token)
""",
            "oauth2_implementation": """
# OAuth2 implementation with FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: str = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
""",
            "rate_limiting": """
# Rate limiting implementation
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        # Remove old requests
        self.requests[key] = [req_time for req_time in self.requests[key]
                             if now - req_time < 60]

        if len(self.requests[key]) >= self.requests_per_minute:
            return False

        self.requests[key].append(now)
        return True

# Usage
limiter = RateLimiter(requests_per_minute=60)

def rate_limited(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not limiter.is_allowed("global"):
            raise HTTPException(status_code=429, detail="Too many requests")
        return func(*args, **kwargs)
    return wrapper
"""
        }

    def _get_security_monitoring_patterns(self) -> Dict[str, Any]:
        """Get security monitoring and alerting patterns."""
        return {
            "siem_correlation_rules": """
# Example SIEM correlation rules
{
  "rules": [
    {
      "name": "Brute Force Attack",
      "description": "Multiple failed login attempts from same IP",
      "conditions": [
        {
          "field": "event_type",
          "operator": "equals",
          "value": "failed_login"
        },
        {
          "field": "source_ip",
          "operator": "count",
          "value": 5,
          "time_window": "5m"
        }
      ],
      "severity": "high",
      "actions": ["alert", "block_ip"]
    },
    {
      "name": "Data Exfiltration",
      "description": "Large data transfer to external IP",
      "conditions": [
        {
          "field": "bytes_out",
          "operator": "greater_than",
          "value": "100MB"
        },
        {
          "field": "destination_ip",
          "operator": "not_in_network",
          "value": "internal_network"
        }
      ],
      "severity": "critical",
      "actions": ["alert", "quarantine"]
    }
  ]
}
""",
            "log_analysis_patterns": """
# Security log analysis patterns
SECURITY_PATTERNS = {
    "failed_login": r"Failed login attempt for user (\w+) from IP (\d+\.\d+\.\d+\.\d+)",
    "suspicious_activity": r"Unusual activity detected: (\w+)",
    "privilege_escalation": r"User (\w+) attempted privilege escalation",
    "data_access": r"Unauthorized access attempt to (\w+)",
    "malware_detected": r"Malware signature detected: (\w+)",
    "brute_force": r"Multiple failed attempts from IP (\d+\.\d+\.\d+\.\d+)",
    "sql_injection": r"Potential SQL injection detected in query: (.+)",
    "xss_attempt": r"Cross-site scripting attempt detected: (.+)"
}
""",
            "threat_intelligence": """
# Threat intelligence integration
THREAT_SOURCES = [
    {
        "name": "AlienVault OTX",
        "url": "https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}",
        "api_key_required": true
    },
    {
        "name": "VirusTotal",
        "url": "https://www.virustotal.com/api/v3/ip_addresses/{ip}",
        "api_key_required": true
    },
    {
        "name": "AbuseIPDB",
        "url": "https://api.abuseipdb.com/api/v3/check?ipAddress={ip}",
        "api_key_required": true
    }
]
"""
        }

    def _load_vulnerability_database(self) -> Dict[str, Any]:
        """Load a simplified vulnerability database."""
        return {
            "CVE-2021-44228": {
                "name": "Log4Shell",
                "severity": "critical",
                "description": "Remote code execution vulnerability in Apache Log4j",
                "affected_versions": ["2.0-beta9 to 2.14.1"],
                "cvss_score": 10.0,
                "remediation": "Upgrade to Log4j 2.17.0 or later"
            },
            "CVE-2021-34527": {
                "name": "PrintNightmare",
                "severity": "critical",
                "description": "Windows Print Spooler remote code execution vulnerability",
                "affected_versions": ["Windows 7 to Windows 11"],
                "cvss_score": 8.8,
                "remediation": "Disable Print Spooler service or apply security updates"
            },
            "SQL_INJECTION": {
                "name": "SQL Injection",
                "severity": "high",
                "description": "Injection of malicious SQL code",
                "cvss_score": 8.0,
                "remediation": "Use parameterized queries and input validation"
            }
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security-related tasks."""
        task_type = task.get("type", "")
        operation = task.get("operation", "")

        if task_type == "vulnerability_scan":
            return await self._handle_vulnerability_scan(task)
        elif task_type == "security_audit":
            return await self._handle_security_audit(task)
        elif task_type == "threat_modeling":
            return await self._handle_threat_modeling(task)
        elif task_type == "compliance_check":
            return await self._handle_compliance_check(task)
        elif task_type == "incident_response":
            return await self._handle_incident_response(task)
        else:
            # Use general task execution for other security tasks
            return await super().execute_task(task)

    async def _handle_vulnerability_scan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vulnerability scanning tasks."""
        scan_type = task.get("scan_type", "code")

        if scan_type == "code":
            return await self._scan_code_vulnerabilities(task)
        elif scan_type == "infrastructure":
            return await self._scan_infrastructure_vulnerabilities(task)
        elif scan_type == "dependencies":
            return await self._scan_dependency_vulnerabilities(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown scan type: {scan_type}"
            }

    async def _handle_security_audit(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security audit tasks."""
        audit_type = task.get("audit_type", "general")

        try:
            findings = []
            recommendations = []

            if audit_type == "infrastructure":
                findings, recommendations = await self._audit_infrastructure(task)
            elif audit_type == "application":
                findings, recommendations = await self._audit_application(task)
            elif audit_type == "network":
                findings, recommendations = await self._audit_network(task)

            risk_score = self._calculate_risk_score(findings)

            return {
                "status": "completed",
                "result": {
                    "audit_type": audit_type,
                    "findings": findings,
                    "recommendations": recommendations,
                    "risk_score": risk_score,
                    "risk_level": self._get_risk_level(risk_score)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Security audit failed: {str(e)}"
            }

    async def _handle_threat_modeling(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle threat modeling tasks."""
        system_description = task.get("system_description", "")
        assets = task.get("assets", [])
        trust_boundaries = task.get("trust_boundaries", [])

        try:
            # Identify threats using STRIDE model
            threats = self._identify_threats_stride(assets, trust_boundaries)

            # Assess risks
            risk_assessment = self._assess_threats(threats)

            # Generate mitigation strategies
            mitigations = self._generate_mitigations(threats)

            return {
                "status": "completed",
                "result": {
                    "system_description": system_description,
                    "threats": threats,
                    "risk_assessment": risk_assessment,
                    "mitigations": mitigations,
                    "modeling_method": "STRIDE"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Threat modeling failed: {str(e)}"
            }

    async def _scan_code_vulnerabilities(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Scan code for security vulnerabilities."""
        code_content = task.get("code", "")
        language = task.get("language", "python")

        try:
            vulnerabilities = []

            # Check for common vulnerabilities
            if language == "python":
                vulnerabilities.extend(self._scan_python_vulnerabilities(code_content))
            elif language == "javascript":
                vulnerabilities.extend(self._scan_javascript_vulnerabilities(code_content))

            # OWASP Top 10 checks
            vulnerabilities.extend(self._check_owasp_top_10(code_content))

            # Calculate severity
            severity_counts = {
                "critical": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
                "high": len([v for v in vulnerabilities if v.get("severity") == "high"]),
                "medium": len([v for v in vulnerabilities if v.get("severity") == "medium"]),
                "low": len([v for v in vulnerabilities if v.get("severity") == "low"])
            }

            return {
                "status": "completed",
                "result": {
                    "scan_type": "code",
                    "language": language,
                    "vulnerabilities": vulnerabilities,
                    "severity_counts": severity_counts,
                    "total_vulnerabilities": len(vulnerabilities)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Code vulnerability scan failed: {str(e)}"
            }

    def _scan_python_vulnerabilities(self, code: str) -> List[Dict[str, Any]]:
        """Scan Python code for vulnerabilities."""
        vulnerabilities = []

        # Check for SQL injection
        if re.search(r"cursor\.execute\(.*\+.*\)", code, re.IGNORECASE):
            vulnerabilities.append({
                "type": "sql_injection",
                "severity": "high",
                "description": "Potential SQL injection vulnerability detected",
                "line": "N/A",
                "recommendation": "Use parameterized queries instead of string concatenation"
            })

        # Check for hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*['\"]([^'\"]{8,})['\"]",
            r"secret\s*=\s*['\"]([^'\"]{8,})['\"]",
            r"api_key\s*=\s*['\"]([^'\"]{10,})['\"]"
        ]

        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "hardcoded_secret",
                    "severity": "high",
                    "description": "Hardcoded secret detected in code",
                    "line": "N/A",
                    "recommendation": "Use environment variables or secret management system"
                })
                break

        # Check for unsafe deserialization
        if "pickle.loads" in code or "yaml.unsafe_load" in code:
            vulnerabilities.append({
                "type": "unsafe_deserialization",
                "severity": "critical",
                "description": "Unsafe deserialization detected",
                "line": "N/A",
                "recommendation": "Avoid using pickle or use safe alternatives like JSON"
            })

        return vulnerabilities

    def _scan_javascript_vulnerabilities(self, code: str) -> List[Dict[str, Any]]:
        """Scan JavaScript code for vulnerabilities."""
        vulnerabilities = []

        # Check for XSS vulnerabilities
        if re.search(r"innerHTML\s*=\s*.*\+.*", code) or re.search(r"document\.write\(.*\+.*\)", code):
            vulnerabilities.append({
                "type": "xss",
                "severity": "high",
                "description": "Potential XSS vulnerability detected",
                "line": "N/A",
                "recommendation": "Use textContent instead of innerHTML or sanitize input"
            })

        # Check for eval usage
        if "eval(" in code:
            vulnerabilities.append({
                "type": "code_injection",
                "severity": "critical",
                "description": "Use of eval() detected",
                "line": "N/A",
                "recommendation": "Avoid using eval(), use safer alternatives"
            })

        return vulnerabilities

    def _check_owasp_top_10(self, code: str) -> List[Dict[str, Any]]:
        """Check code against OWASP Top 10."""
        vulnerabilities = []

        # Injection checks
        if re.search(r"(SELECT|INSERT|UPDATE|DELETE).*\+.*FROM", code, re.IGNORECASE):
            vulnerabilities.append({
                "type": "owasp_a01_injection",
                "severity": "high",
                "description": "OWASP A01 - Injection vulnerability detected",
                "owasp_category": "A01:2021-Injection",
                "recommendation": "Use parameterized queries or prepared statements"
            })

        # Broken authentication checks
        if re.search(r"password.*=\s*['\"]([^'\"]{0,7})['\"]", code):
            vulnerabilities.append({
                "type": "owasp_a02_broken_auth",
                "severity": "medium",
                "description": "OWASP A02 - Weak password policy detected",
                "owasp_category": "A02:2021-Cryptographic Failures",
                "recommendation": "Implement strong password requirements"
            })

        return vulnerabilities

    async def _audit_infrastructure(self, task: Dict[str, Any]) -> tuple:
        """Audit infrastructure security."""
        findings = []
        recommendations = []

        # Check for common infrastructure issues
        infrastructure_checks = [
            {
                "check": "exposed_ports",
                "description": "Sensitive ports exposed to public internet",
                "severity": "high",
                "recommendation": "Use security groups or firewalls to restrict access"
            },
            {
                "check": "outdated_software",
                "description": "Systems running outdated software",
                "severity": "medium",
                "recommendation": "Implement automated patching and updates"
            },
            {
                "check": "weak_encryption",
                "description": "Weak encryption protocols in use",
                "severity": "high",
                "recommendation": "Use TLS 1.3 and strong cipher suites"
            }
        ]

        findings.extend(infrastructure_checks)
        recommendations.append("Implement regular security scanning and monitoring")
        recommendations.append("Use infrastructure as code for consistent security")

        return findings, recommendations

    async def _audit_application(self, task: Dict[str, Any]) -> tuple:
        """Audit application security."""
        findings = []
        recommendations = []

        # Application security checks
        app_checks = [
            {
                "check": "input_validation",
                "description": "Insufficient input validation",
                "severity": "high",
                "recommendation": "Implement comprehensive input validation and sanitization"
            },
            {
                "check": "session_management",
                "description": "Weak session management",
                "severity": "medium",
                "recommendation": "Implement secure session handling with proper timeouts"
            }
        ]

        findings.extend(app_checks)
        recommendations.append("Implement security headers (CSP, HSTS, etc.)")
        recommendations.append("Regular security code reviews and testing")

        return findings, recommendations

    def _identify_threats_stride(self, assets: List[str], trust_boundaries: List[str]) -> List[Dict[str, Any]]:
        """Identify threats using STRIDE model."""
        threats = []

        stride_categories = [
            {"category": "Spoofing", "description": "Impersonating something or someone else"},
            {"category": "Tampering", "description": "Modifying data or code"},
            {"category": "Repudiation", "description": "Denying an action occurred"},
            {"category": "Information Disclosure", "description": "Exposing information to unauthorized parties"},
            {"category": "Denial of Service", "description": "Making a system unavailable"},
            {"category": "Elevation of Privilege", "description": "Gaining higher privileges than allowed"}
        ]

        for asset in assets:
            for stride in stride_categories:
                threats.append({
                    "asset": asset,
                    "category": stride["category"],
                    "description": f"{stride['description']} affecting {asset}",
                    "likelihood": "medium",
                    "impact": "high",
                    "risk_level": "medium"
                })

        return threats

    def _assess_threats(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess identified threats."""
        risk_levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for threat in threats:
            risk_level = threat.get("risk_level", "low")
            risk_levels[risk_level] += 1

        total_risk_score = (
            risk_levels["critical"] * 10 +
            risk_levels["high"] * 7 +
            risk_levels["medium"] * 4 +
            risk_levels["low"] * 1
        )

        return {
            "risk_distribution": risk_levels,
            "total_threats": len(threats),
            "overall_risk_score": total_risk_score,
            "risk_assessment": "high" if total_risk_score > 50 else "medium" if total_risk_score > 20 else "low"
        }

    def _generate_mitigations(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mitigation strategies for threats."""
        mitigations = []

        for threat in threats:
            category = threat.get("category", "")

            if category == "Spoofing":
                mitigation = "Implement multi-factor authentication and digital signatures"
            elif category == "Tampering":
                mitigation = "Use integrity checks (hashing) and access controls"
            elif category == "Repudiation":
                mitigation = "Implement comprehensive logging and digital signatures"
            elif category == "Information Disclosure":
                mitigation = "Use encryption and access controls"
            elif category == "Denial of Service":
                mitigation = "Implement rate limiting and resource quotas"
            elif category == "Elevation of Privilege":
                mitigation = "Use principle of least privilege and regular audits"
            else:
                mitigation = "Implement appropriate security controls"

            mitigations.append({
                "threat": f"{threat.get('category')} - {threat.get('asset')}",
                "mitigation_strategy": mitigation,
                "priority": threat.get("risk_level", "medium")
            })

        return mitigations

    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score from findings."""
        severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1
        }

        total_score = 0
        for finding in findings:
            severity = finding.get("severity", "low")
            total_score += severity_weights.get(severity, 1)

        return min(total_score, 100)  # Cap at 100

    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
