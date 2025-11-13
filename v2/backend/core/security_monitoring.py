"""
Security Monitoring System
Track and respond to security threats in real-time.

Features:
- Failed login detection
- Suspicious activity tracking
- Automated IP blocking
- Brute force protection
- Rate limiting enforcement
"""

import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Redis connection for security tracking
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=1,  # Use DB 1 for security (separate from auth)
        decode_responses=True,
        password=os.getenv("REDIS_PASSWORD", "")
    )
    redis_client.ping()
except:
    redis_client = None
    logger.warning("Redis unavailable for security monitoring")


class SecurityMonitor:
    """
    Real-time security monitoring and threat response.
    
    Tracks:
    - Failed login attempts
    - Suspicious patterns
    - Rate limit violations
    - Blocked IPs
    """
    
    def __init__(self):
        self.redis = redis_client
    
    def record_failed_login(self, email: str, ip_address: str):
        """
        Record failed login attempt.
        
        Tracks failures by email and IP.
        Auto-blocks after threshold exceeded.
        """
        if not self.redis:
            return
        
        # Increment failure counters
        email_key = f"failed_login:email:{email}"
        ip_key = f"failed_login:ip:{ip_address}"
        
        # Increment with 1-hour expiry
        self.redis.incr(email_key)
        self.redis.expire(email_key, 3600)
        
        self.redis.incr(ip_key)
        self.redis.expire(ip_key, 3600)
        
        # Check thresholds
        email_failures = int(self.redis.get(email_key) or 0)
        ip_failures = int(self.redis.get(ip_key) or 0)
        
        # Block if too many failures
        if email_failures >= 5:
            logger.warning(f"Email {email} exceeded failed login threshold")
            self.block_email_temporarily(email, duration_minutes=30)
        
        if ip_failures >= 10:
            logger.warning(f"IP {ip_address} exceeded failed login threshold")
            self.block_ip(ip_address, duration_minutes=60)
    
    def record_successful_login(self, email: str, ip_address: str):
        """
        Record successful login.
        
        Resets failure counters.
        """
        if not self.redis:
            return
        
        email_key = f"failed_login:email:{email}"
        ip_key = f"failed_login:ip:{ip_address}"
        
        # Reset failure counters
        self.redis.delete(email_key)
        self.redis.delete(ip_key)
    
    def is_email_blocked(self, email: str) -> bool:
        """Check if email is temporarily blocked."""
        if not self.redis:
            return False
        
        return self.redis.exists(f"blocked:email:{email}") > 0
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        if not self.redis:
            return False
        
        # Check both temporary and permanent blocks
        temp_blocked = self.redis.exists(f"blocked:ip:temp:{ip_address}") > 0
        perm_blocked = self.redis.exists(f"blocked:ip:perm:{ip_address}") > 0
        
        return temp_blocked or perm_blocked
    
    def block_email_temporarily(self, email: str, duration_minutes: int = 30):
        """Block email temporarily."""
        if not self.redis:
            return
        
        key = f"blocked:email:{email}"
        self.redis.setex(key, duration_minutes * 60, "1")
        logger.info(f"Blocked email {email} for {duration_minutes} minutes")
    
    def block_ip(self, ip_address: str, duration_minutes: Optional[int] = None):
        """
        Block IP address.
        
        Args:
            ip_address: IP to block
            duration_minutes: Duration (None = permanent)
        """
        if not self.redis:
            return
        
        if duration_minutes:
            # Temporary block
            key = f"blocked:ip:temp:{ip_address}"
            self.redis.setex(key, duration_minutes * 60, "1")
            logger.info(f"Blocked IP {ip_address} for {duration_minutes} minutes")
        else:
            # Permanent block
            key = f"blocked:ip:perm:{ip_address}"
            self.redis.set(key, "1")
            logger.warning(f"Permanently blocked IP {ip_address}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address."""
        if not self.redis:
            return
        
        self.redis.delete(f"blocked:ip:temp:{ip_address}")
        self.redis.delete(f"blocked:ip:perm:{ip_address}")
        logger.info(f"Unblocked IP {ip_address}")
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of all blocked IPs."""
        if not self.redis:
            return []
        
        temp_keys = self.redis.keys("blocked:ip:temp:*")
        perm_keys = self.redis.keys("blocked:ip:perm:*")
        
        temp_ips = [key.replace("blocked:ip:temp:", "") for key in temp_keys]
        perm_ips = [key.replace("blocked:ip:perm:", "") for key in perm_keys]
        
        return temp_ips + perm_ips
    
    def record_suspicious_activity(
        self,
        user_id: Optional[int],
        ip_address: str,
        activity_type: str,
        details: Dict
    ):
        """
        Record suspicious activity for analysis.
        
        Examples:
        - Rapid API calls
        - Unusual access patterns
        - Privilege escalation attempts
        - Data scraping
        """
        if not self.redis:
            return
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "ip_address": ip_address,
            "activity_type": activity_type,
            "details": details
        }
        
        # Store in list with 7-day expiry
        key = f"suspicious:log"
        self.redis.lpush(key, str(event))
        self.redis.ltrim(key, 0, 9999)  # Keep last 10000 events
        self.redis.expire(key, 7 * 24 * 3600)  # 7 days
        
        logger.warning(f"Suspicious activity: {activity_type} from {ip_address}")
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        if not self.redis:
            return {"status": "Redis unavailable"}
        
        return {
            "blocked_ips_count": len(self.get_blocked_ips()),
            "blocked_ips": self.get_blocked_ips(),
            "suspicious_events_count": self.redis.llen("suspicious:log"),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global security monitor instance
_monitor_instance = None

def get_security_monitor() -> SecurityMonitor:
    """Get global security monitor instance (singleton)."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SecurityMonitor()
    return _monitor_instance

