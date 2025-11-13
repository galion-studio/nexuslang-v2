"""
Anti-Raid Infrastructure for NexusLang v2
Comprehensive security system with AI-powered threat detection and automated response

Features:
- Anti-DDoS protection with intelligent rate limiting
- Port monitoring and anomaly detection
- AI-powered security analytics using Nexus Lang v2
- Automated incident response and mitigation
- Real-time threat assessment and blocking
"""

import asyncio
import time
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import ipaddress
import socket
import psutil
import threading
from dataclasses import dataclass, field
from enum import Enum

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..services.nexuslang_executor import execute_nexuslang_code
from ..core.redis_client import get_redis

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(Enum):
    DDoS = "ddos"
    BRUTE_FORCE = "brute_force"
    PORT_SCAN = "port_scan"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


@dataclass
class SecurityEvent:
    """Represents a security event or incident"""
    id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    threat_level: ThreatLevel
    attack_type: AttackType
    confidence_score: float
    details: Dict[str, Any]
    mitigated: bool = False
    response_actions: List[str] = field(default_factory=list)


@dataclass
class IPIntelligence:
    """Intelligence data for IP addresses"""
    ip: str
    reputation_score: float
    total_requests: int
    blocked_requests: int
    last_seen: datetime
    countries: Set[str]
    user_agents: Set[str]
    attack_patterns: Dict[str, int]
    threat_level: ThreatLevel
    is_blocked: bool = False
    block_expires: Optional[datetime] = None


class AntiRaidInfrastructure:
    """
    Comprehensive anti-raid security system
    Integrates multiple protection layers with AI-powered decision making
    """

    def __init__(self):
        self.redis = get_redis()
        self.is_active = True

        # Rate limiting
        self.rate_limits = {
            'global': {'requests': 1000, 'window': 60},  # 1000 req/min globally
            'per_ip': {'requests': 100, 'window': 60},   # 100 req/min per IP
            'per_endpoint': {'requests': 50, 'window': 60}, # 50 req/min per endpoint
            'login_attempts': {'requests': 5, 'window': 300}, # 5 login attempts per 5 min
        }

        # DDoS protection
        self.ddos_thresholds = {
            'requests_per_second': 50,
            'concurrent_connections': 100,
            'bandwidth_mbps': 100,
        }

        # Port monitoring
        self.monitored_ports = {8000, 3000, 6379, 5432}  # API, Frontend, Redis, Postgres
        self.port_anomalies = defaultdict(list)

        # AI-powered threat detection
        self.nexus_ai_enabled = True
        self.threat_detection_model = None

        # Response systems
        self.auto_response_enabled = True
        self.response_actions = {
            ThreatLevel.LOW: ['log', 'monitor'],
            ThreatLevel.MEDIUM: ['log', 'rate_limit', 'monitor'],
            ThreatLevel.HIGH: ['log', 'block_ip', 'alert_admin', 'rate_limit'],
            ThreatLevel.CRITICAL: ['log', 'block_ip', 'shutdown_service', 'alert_admin'],
        }

        # Intelligence database
        self.ip_intelligence: Dict[str, IPIntelligence] = {}
        self.security_events: List[SecurityEvent] = []

        # Monitoring threads
        self.monitoring_threads = []
        self.monitoring_active = False

    async def initialize(self):
        """Initialize the anti-raid infrastructure"""
        logger.info("🔒 Initializing Anti-Raid Infrastructure...")

        # Load existing IP intelligence from database
        await self._load_ip_intelligence()

        # Start monitoring threads
        self._start_monitoring()

        # Initialize Nexus Lang AI model for threat detection
        if self.nexus_ai_enabled:
            await self._initialize_ai_model()

        logger.info("✅ Anti-Raid Infrastructure initialized")

    async def _load_ip_intelligence(self):
        """Load IP intelligence data from database"""
        try:
            # This would load from a dedicated security database table
            # For now, we'll initialize with empty data
            pass
        except Exception as e:
            logger.error(f"Failed to load IP intelligence: {e}")

    def _start_monitoring(self):
        """Start background monitoring threads"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # Port monitoring thread
        port_thread = threading.Thread(target=self._monitor_ports, daemon=True)
        port_thread.start()
        self.monitoring_threads.append(port_thread)

        # DDoS monitoring thread
        ddos_thread = threading.Thread(target=self._monitor_ddos, daemon=True)
        ddos_thread.start()
        self.monitoring_threads.append(ddos_thread)

        # Traffic analysis thread
        traffic_thread = threading.Thread(target=self._analyze_traffic, daemon=True)
        traffic_thread.start()
        self.monitoring_threads.append(traffic_thread)

        logger.info("📊 Security monitoring threads started")

    def _monitor_ports(self):
        """Monitor network ports for suspicious activity"""
        while self.monitoring_active:
            try:
                for port in self.monitored_ports:
                    # Check for unusual connection patterns
                    connections = self._get_port_connections(port)
                    anomalies = self._detect_port_anomalies(port, connections)

                    if anomalies:
                        for anomaly in anomalies:
                            asyncio.run(self._handle_port_anomaly(port, anomaly))

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Port monitoring error: {e}")
                time.sleep(60)

    def _monitor_ddos(self):
        """Monitor for DDoS attacks"""
        while self.monitoring_active:
            try:
                # Check global request rates
                global_rate = self._get_global_request_rate()
                if global_rate > self.ddos_thresholds['requests_per_second']:
                    asyncio.run(self._handle_ddos_attack(global_rate))

                # Check concurrent connections
                connections = self._get_concurrent_connections()
                if connections > self.ddos_thresholds['concurrent_connections']:
                    asyncio.run(self._handle_connection_flood(connections))

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"DDoS monitoring error: {e}")
                time.sleep(30)

    def _analyze_traffic(self):
        """Analyze traffic patterns for threats"""
        while self.monitoring_active:
            try:
                # Analyze request patterns
                patterns = self._analyze_request_patterns()
                threats = self._identify_threats(patterns)

                for threat in threats:
                    asyncio.run(self._handle_threat(threat))

                time.sleep(60)  # Analyze every minute

            except Exception as e:
                logger.error(f"Traffic analysis error: {e}")
                time.sleep(120)

    async def check_request(self, ip: str, endpoint: str, method: str, user_agent: str) -> bool:
        """
        Check if a request should be allowed
        Returns True if allowed, False if blocked
        """
        # Check IP intelligence
        ip_intel = self.ip_intelligence.get(ip)
        if ip_intel and ip_intel.is_blocked:
            if ip_intel.block_expires and datetime.now() > ip_intel.block_expires:
                # Block expired, unblock IP
                ip_intel.is_blocked = False
                ip_intel.block_expires = None
            else:
                await self._log_security_event(
                    ip=ip,
                    user_agent=user_agent,
                    endpoint=endpoint,
                    method=method,
                    threat_level=ThreatLevel.HIGH,
                    attack_type=AttackType.SUSPICIOUS_ACTIVITY,
                    confidence_score=0.95,
                    details={"reason": "IP blocked due to previous malicious activity"}
                )
                return False

        # Rate limiting checks
        if not await self._check_rate_limits(ip, endpoint):
            await self._handle_rate_limit_exceeded(ip, endpoint, user_agent)
            return False

        # AI-powered threat detection
        if self.nexus_ai_enabled:
            threat_assessment = await self._assess_threat_with_ai(ip, endpoint, method, user_agent)
            if threat_assessment['threat_level'] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._handle_ai_detected_threat(threat_assessment)
                return False

        return True

    async def _check_rate_limits(self, ip: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()

        # Global rate limit
        global_key = f"ratelimit:global:{int(current_time / self.rate_limits['global']['window'])}"
        global_count = await self.redis.incr(global_key)
        await self.redis.expire(global_key, self.rate_limits['global']['window'])

        if global_count > self.rate_limits['global']['requests']:
            return False

        # Per-IP rate limit
        ip_key = f"ratelimit:ip:{ip}:{int(current_time / self.rate_limits['per_ip']['window'])}"
        ip_count = await self.redis.incr(ip_key)
        await self.redis.expire(ip_key, self.rate_limits['per_ip']['window'])

        if ip_count > self.rate_limits['per_ip']['requests']:
            return False

        # Per-endpoint rate limit
        endpoint_key = f"ratelimit:endpoint:{endpoint}:{int(current_time / self.rate_limits['per_endpoint']['window'])}"
        endpoint_count = await self.redis.incr(endpoint_key)
        await self.redis.expire(endpoint_key, self.rate_limits['per_endpoint']['window'])

        if endpoint_count > self.rate_limits['per_endpoint']['requests']:
            return False

        return True

    async def _assess_threat_with_ai(self, ip: str, endpoint: str, method: str, user_agent: str) -> Dict:
        """Use Nexus Lang v2 AI to assess threat level"""
        if not self.nexus_ai_enabled:
            return {'threat_level': ThreatLevel.LOW, 'confidence': 0.1}

        try:
            # Prepare data for AI analysis
            request_data = {
                'ip': ip,
                'endpoint': endpoint,
                'method': method,
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat(),
                'ip_intelligence': self.ip_intelligence.get(ip, {}),
            }

            # Nexus Lang AI analysis code
            ai_code = f'''
            analyze_security_threat({request_data})
            '''

            result = await execute_nexuslang_code(ai_code)

            return {
                'threat_level': ThreatLevel(result.get('threat_level', 'low')),
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', ''),
                'recommendations': result.get('recommendations', [])
            }

        except Exception as e:
            logger.error(f"AI threat assessment failed: {e}")
            return {'threat_level': ThreatLevel.LOW, 'confidence': 0.1}

    async def _handle_rate_limit_exceeded(self, ip: str, endpoint: str, user_agent: str):
        """Handle rate limit violations"""
        await self._log_security_event(
            ip=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method='RATE_LIMITED',
            threat_level=ThreatLevel.MEDIUM,
            attack_type=AttackType.DDoS,
            confidence_score=0.8,
            details={"violation": "rate_limit_exceeded"}
        )

        # Temporary block IP
        await self._block_ip(ip, duration_minutes=15, reason="Rate limit exceeded")

    async def _handle_ai_detected_threat(self, threat_assessment: Dict):
        """Handle threats detected by AI"""
        threat_level = threat_assessment['threat_level']

        # Execute automated response based on threat level
        if self.auto_response_enabled:
            actions = self.response_actions.get(threat_level, ['log'])

            for action in actions:
                if action == 'block_ip':
                    await self._block_ip(threat_assessment.get('ip'), duration_minutes=60)
                elif action == 'shutdown_service':
                    await self._emergency_shutdown()
                elif action == 'alert_admin':
                    await self._alert_admin(threat_assessment)

    async def _block_ip(self, ip: str, duration_minutes: int, reason: str = ""):
        """Block an IP address temporarily"""
        if ip not in self.ip_intelligence:
            self.ip_intelligence[ip] = IPIntelligence(
                ip=ip,
                reputation_score=0.5,
                total_requests=0,
                blocked_requests=0,
                last_seen=datetime.now(),
                countries=set(),
                user_agents=set(),
                attack_patterns={},
                threat_level=ThreatLevel.MEDIUM
            )

        ip_intel = self.ip_intelligence[ip]
        ip_intel.is_blocked = True
        ip_intel.block_expires = datetime.now() + timedelta(minutes=duration_minutes)
        ip_intel.reputation_score -= 0.2  # Decrease reputation

        # Store in Redis for fast lookups
        block_key = f"blocked_ip:{ip}"
        await self.redis.setex(block_key, duration_minutes * 60, "1")

        logger.warning(f"🚫 Blocked IP {ip} for {duration_minutes} minutes: {reason}")

    async def _emergency_shutdown(self):
        """Emergency shutdown of services"""
        logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")
        # This would trigger service shutdown procedures
        # For now, just log the critical event
        await self._alert_admin({
            'type': 'emergency_shutdown',
            'reason': 'Critical threat detected',
            'timestamp': datetime.now()
        })

    async def _alert_admin(self, alert_data: Dict):
        """Send alerts to administrators"""
        # This would integrate with your notification system
        logger.warning(f"🚨 Admin Alert: {alert_data}")

        # Store alert in database for admin panel
        # Send email/SMS notifications
        # Trigger Slack/Discord webhooks

    async def _log_security_event(self, ip: str, user_agent: str, endpoint: str,
                                method: str, threat_level: ThreatLevel,
                                attack_type: AttackType, confidence_score: float,
                                details: Dict):
        """Log security events for analysis"""
        event = SecurityEvent(
            id=f"event_{int(time.time())}_{hash(ip)}",
            timestamp=datetime.now(),
            ip_address=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            threat_level=threat_level,
            attack_type=attack_type,
            confidence_score=confidence_score,
            details=details
        )

        self.security_events.append(event)

        # Keep only recent events (last 1000)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        # Log to database for admin panel
        logger.info(f"🔍 Security Event: {threat_level.value} {attack_type.value} from {ip}")

    # Helper methods for monitoring
    def _get_port_connections(self, port: int) -> List[Dict]:
        """Get current connections to a port"""
        try:
            # This would use system tools to monitor connections
            # For now, return mock data
            return [
                {'ip': '192.168.1.1', 'port': port, 'state': 'ESTABLISHED'},
                {'ip': '10.0.0.1', 'port': port, 'state': 'ESTABLISHED'},
            ]
        except Exception:
            return []

    def _detect_port_anomalies(self, port: int, connections: List[Dict]) -> List[Dict]:
        """Detect anomalous connection patterns"""
        anomalies = []

        # Simple anomaly detection logic
        if len(connections) > 50:  # Too many connections
            anomalies.append({
                'type': 'connection_flood',
                'severity': 'high',
                'details': f'{len(connections)} connections to port {port}'
            })

        return anomalies

    def _get_global_request_rate(self) -> float:
        """Get current global request rate"""
        # This would integrate with your metrics system
        return 25.0  # Mock value

    def _get_concurrent_connections(self) -> int:
        """Get number of concurrent connections"""
        # This would use system monitoring
        return 45  # Mock value

    def _analyze_request_patterns(self) -> Dict:
        """Analyze request patterns for threats"""
        # This would analyze logs and metrics
        return {}  # Mock data

    def _identify_threats(self, patterns: Dict) -> List[Dict]:
        """Identify potential threats from patterns"""
        # AI-powered threat identification
        return []  # Mock data

    async def _handle_port_anomaly(self, port: int, anomaly: Dict):
        """Handle detected port anomalies"""
        await self._log_security_event(
            ip="system",
            user_agent="port_monitor",
            endpoint=f"port_{port}",
            method="MONITOR",
            threat_level=ThreatLevel(anomaly.get('severity', 'medium')),
            attack_type=AttackType.PORT_SCAN,
            confidence_score=0.7,
            details=anomaly
        )

    async def _handle_ddos_attack(self, rate: float):
        """Handle DDoS attack detection"""
        await self._log_security_event(
            ip="global",
            user_agent="ddos_monitor",
            endpoint="all",
            method="DDoS",
            threat_level=ThreatLevel.HIGH,
            attack_type=AttackType.DDoS,
            confidence_score=0.9,
            details={"attack_rate": rate, "threshold": self.ddos_thresholds['requests_per_second']}
        )

        # Implement DDoS mitigation (rate limiting, IP blocking, etc.)
        if self.auto_response_enabled:
            # Enable emergency rate limiting
            await self._enable_emergency_rate_limiting()

    async def _handle_connection_flood(self, connections: int):
        """Handle connection flood attacks"""
        await self._log_security_event(
            ip="global",
            user_agent="connection_monitor",
            endpoint="all",
            method="CONNECTION_FLOOD",
            threat_level=ThreatLevel.CRITICAL,
            attack_type=AttackType.DDoS,
            confidence_score=0.95,
            details={"connections": connections, "threshold": self.ddos_thresholds['concurrent_connections']}
        )

    async def _handle_threat(self, threat: Dict):
        """Handle identified threats"""
        threat_level = ThreatLevel(threat.get('level', 'low'))
        await self._log_security_event(
            ip=threat.get('ip', 'unknown'),
            user_agent=threat.get('user_agent', 'unknown'),
            endpoint=threat.get('endpoint', 'unknown'),
            method=threat.get('method', 'unknown'),
            threat_level=threat_level,
            attack_type=AttackType(threat.get('type', 'suspicious_activity')),
            confidence_score=threat.get('confidence', 0.5),
            details=threat
        )

    async def _enable_emergency_rate_limiting(self):
        """Enable emergency rate limiting during attacks"""
        # Reduce all rate limits by 50% during emergency
        for limit_type in self.rate_limits:
            self.rate_limits[limit_type]['requests'] = max(
                10,  # Minimum 10 requests
                self.rate_limits[limit_type]['requests'] // 2
            )

        logger.warning("🚨 Emergency rate limiting enabled")

    # Admin panel integration methods
    async def get_security_dashboard_data(self) -> Dict:
        """Get data for the security dashboard"""
        return {
            'active_threats': len([e for e in self.security_events if not e.mitigated]),
            'blocked_ips': len([ip for ip in self.ip_intelligence.values() if ip.is_blocked]),
            'recent_events': self.security_events[-10:],
            'threat_levels': {
                'low': len([e for e in self.security_events if e.threat_level == ThreatLevel.LOW]),
                'medium': len([e for e in self.security_events if e.threat_level == ThreatLevel.MEDIUM]),
                'high': len([e for e in self.security_events if e.threat_level == ThreatLevel.HIGH]),
                'critical': len([e for e in self.security_events if e.threat_level == ThreatLevel.CRITICAL]),
            },
            'attack_types': defaultdict(int),
            'system_status': 'active' if self.is_active else 'inactive'
        }

    async def unblock_ip(self, ip: str) -> bool:
        """Manually unblock an IP address"""
        if ip in self.ip_intelligence:
            self.ip_intelligence[ip].is_blocked = False
            self.ip_intelligence[ip].block_expires = None

            # Remove from Redis
            block_key = f"blocked_ip:{ip}"
            await self.redis.delete(block_key)

            logger.info(f"✅ Manually unblocked IP: {ip}")
            return True

        return False

    async def shutdown(self):
        """Shutdown the anti-raid infrastructure"""
        logger.info("🛑 Shutting down Anti-Raid Infrastructure...")
        self.monitoring_active = False
        self.is_active = False

        # Wait for monitoring threads to finish
        for thread in self.monitoring_threads:
            thread.join(timeout=5)

        logger.info("✅ Anti-Raid Infrastructure shutdown complete")


# Global instance
_anti_raid_system: Optional[AntiRaidInfrastructure] = None


async def get_anti_raid_system() -> AntiRaidInfrastructure:
    """Get the global anti-raid system instance"""
    global _anti_raid_system
    if _anti_raid_system is None:
        _anti_raid_system = AntiRaidInfrastructure()
        await _anti_raid_system.initialize()
    return _anti_raid_system


async def check_request_security(ip: str, endpoint: str, method: str, user_agent: str) -> bool:
    """Check if a request passes security checks"""
    system = await get_anti_raid_system()
    return await system.check_request(ip, endpoint, method, user_agent)
