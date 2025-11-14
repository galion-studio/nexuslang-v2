"""
Monitoring Agent for Galion Platform v2.2
Provides system health monitoring, performance tracking, and automated alerting.

"Your imagination is the end."
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import psutil
import asyncio

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities

logger = logging.getLogger(__name__)

class MonitoringAgent(BaseAgent):
    """
    AI Monitoring Agent

    Specializes in:
    - System health monitoring
    - Performance metrics tracking
    - Automated alerting and notifications
    - Predictive maintenance
    - Resource usage analysis
    - Incident response
    """

    def __init__(self):
        personality = PersonalityTraits(
            analytical=0.95,    # Highly analytical for metrics analysis
            creative=0.4,       # Limited creativity needed
            empathetic=0.6,     # Moderate empathy for alert communications
            precision=0.98,     # Extremely precise with metrics and thresholds
            helpful=0.9,        # Very helpful in identifying and resolving issues
            humor=0.1,          # Serious topic, minimal humor
            directness=0.9,     # Direct about system issues
            curiosity=0.7       # Curious about system behavior patterns
        )

        capabilities = AgentCapabilities(
            can_execute_code=False,      # No code execution needed
            can_access_filesystem=False, # No file access
            can_make_api_calls=True,     # Can call monitoring APIs
            can_generate_content=True,   # Generates reports and alerts
            can_analyze_data=True,       # Analyzes system metrics
            can_interact_with_users=True, # Alerts and notifications
            can_schedule_tasks=True,     # Scheduled monitoring
            can_monitor_systems=True,    # Core monitoring capability
            supported_languages=["en"],  # English for alerts
            expertise_domains=[
                "system_monitoring",
                "performance_analysis",
                "incident_detection",
                "capacity_planning",
                "health_checks",
                "alert_management"
            ],
            tool_access=["system_metrics", "monitoring_apis", "alert_systems"]
        )

        super().__init__(
            name="Monitoring",
            personality=personality,
            capabilities=capabilities,
            description="System monitoring and health management specialist",
            version="2.0.0"
        )

        # Monitoring thresholds
        self.thresholds = {
            "cpu_usage": 80.0,      # Percent
            "memory_usage": 85.0,   # Percent
            "disk_usage": 90.0,     # Percent
            "response_time": 1000,  # Milliseconds
            "error_rate": 5.0,      # Percent
            "uptime_minimum": 99.5  # Percent
        }

        # Monitoring history
        self.metrics_history = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": [],
            "response_times": []
        }

        self.max_history_size = 1000  # Keep last 1000 readings

    async def execute(
        self,
        prompt: str,
        context: Optional[AgentContext] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute monitoring request.

        Provides system status, analyzes metrics, or generates reports.
        """
        start_time = datetime.now()

        try:
            # Analyze the monitoring request
            query_analysis = await self.analyze_monitoring_query(prompt)

            # Route to appropriate monitoring function
            if query_analysis["query_type"] == "system_status":
                response = await self.get_system_status()
            elif query_analysis["query_type"] == "performance_report":
                response = await self.generate_performance_report()
            elif query_analysis["query_type"] == "alert_check":
                response = await self.check_alerts()
            elif query_analysis["query_type"] == "health_assessment":
                response = await self.assess_system_health()
            elif query_analysis["query_type"] == "capacity_analysis":
                response = await self.analyze_capacity()
            else:
                response = await self.provide_general_monitoring_info()

            # Record metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self.record_metrics()

            return AgentResult(
                success=True,
                response=response,
                cost=0.015,  # Low cost for monitoring
                execution_time=execution_time,
                metadata={
                    "query_type": query_analysis["query_type"],
                    "system_metrics": await self.get_current_metrics(),
                    "alerts_active": await self.check_active_alerts()
                }
            )

        except Exception as e:
            logger.error(f"Monitoring execution failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                success=False,
                response="Unable to complete monitoring request due to system error.",
                cost=0.01,
                execution_time=execution_time,
                error=str(e)
            )

    async def analyze_monitoring_query(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze monitoring query to determine request type.
        """
        prompt_lower = prompt.lower()

        analysis = {
            "query_type": "general_status",
            "urgency": "normal",
            "scope": "overview"
        }

        # Determine query type
        if any(word in prompt_lower for word in ["status", "health", "overview", "summary"]):
            analysis["query_type"] = "system_status"
        elif any(word in prompt_lower for word in ["performance", "metrics", "report", "analysis"]):
            analysis["query_type"] = "performance_report"
        elif any(word in prompt_lower for word in ["alert", "warning", "error", "issue"]):
            analysis["query_type"] = "alert_check"
            analysis["urgency"] = "high"
        elif any(word in prompt_lower for word in ["health", "assessment", "check"]):
            analysis["query_type"] = "health_assessment"
        elif any(word in prompt_lower for word in ["capacity", "resources", "scaling"]):
            analysis["query_type"] = "capacity_analysis"

        return analysis

    async def get_system_status(self) -> str:
        """Get current system status overview"""
        metrics = await self.get_current_metrics()

        response = "# System Status Overview\n\n"
        response += f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # CPU Status
        cpu_percent = metrics.get("cpu_percent", 0)
        cpu_status = "🟢 Normal" if cpu_percent < self.thresholds["cpu_usage"] else "🔴 High"
        response += f"## CPU Usage\n{cpu_status}: {cpu_percent:.1f}%\n\n"

        # Memory Status
        memory_percent = metrics.get("memory_percent", 0)
        memory_status = "🟢 Normal" if memory_percent < self.thresholds["memory_usage"] else "🔴 High"
        response += f"## Memory Usage\n{memory_status}: {memory_percent:.1f}%\n\n"

        # Disk Status
        disk_percent = metrics.get("disk_percent", 0)
        disk_status = "🟢 Normal" if disk_percent < self.thresholds["disk_usage"] else "🔴 High"
        response += f"## Disk Usage\n{disk_status}: {disk_percent:.1f}%\n\n"

        # Network Status
        network_status = "🟢 Normal"  # Would check actual network metrics
        response += f"## Network Status\n{network_status}\n\n"

        # Overall Status
        overall_status = self.calculate_overall_status(metrics)
        response += f"## Overall System Health\n{overall_status}\n\n"

        return response

    async def generate_performance_report(self) -> str:
        """Generate detailed performance report"""
        response = "# Performance Report\n\n"
        response += f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += f"**Analysis Period**: Last {len(self.metrics_history['cpu'])} readings\n\n"

        # CPU Analysis
        cpu_readings = self.metrics_history.get("cpu", [])
        if cpu_readings:
            avg_cpu = sum(cpu_readings) / len(cpu_readings)
            max_cpu = max(cpu_readings)
            response += f"## CPU Performance\n"
            response += f"- Average Usage: {avg_cpu:.1f}%\n"
            response += f"- Peak Usage: {max_cpu:.1f}%\n"
            response += f"- Threshold: {self.thresholds['cpu_usage']}%\n\n"

        # Memory Analysis
        memory_readings = self.metrics_history.get("memory", [])
        if memory_readings:
            avg_memory = sum(memory_readings) / len(memory_readings)
            max_memory = max(memory_readings)
            response += f"## Memory Performance\n"
            response += f"- Average Usage: {avg_memory:.1f}%\n"
            response += f"- Peak Usage: {max_memory:.1f}%\n"
            response += f"- Threshold: {self.thresholds['memory_usage']}%\n\n"

        # Trends Analysis
        response += "## Performance Trends\n"
        response += "- CPU: " + self.analyze_trend(cpu_readings) + "\n"
        response += "- Memory: " + self.analyze_trend(memory_readings) + "\n\n"

        # Recommendations
        response += "## Recommendations\n"
        recommendations = await self.generate_recommendations()
        response += recommendations

        return response

    async def check_alerts(self) -> str:
        """Check for active alerts and issues"""
        alerts = await self.check_active_alerts()

        response = "# System Alerts\n\n"
        response += f"**Checked**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if not alerts:
            response += "✅ **No active alerts**\n\n"
            response += "All systems are operating within normal parameters.\n"
        else:
            response += f"⚠️ **{len(alerts)} active alert(s)**\n\n"
            for alert in alerts:
                response += f"## {alert['severity'].upper()} - {alert['component']}\n"
                response += f"**Issue**: {alert['message']}\n"
                response += f"**Threshold**: {alert['threshold']}\n"
                response += f"**Current**: {alert['current']}\n\n"

        return response

    async def assess_system_health(self) -> str:
        """Provide comprehensive health assessment"""
        metrics = await self.get_current_metrics()

        response = "# System Health Assessment\n\n"
        response += f"**Assessment Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Component Health Scores
        health_scores = {
            "CPU": self.calculate_health_score(metrics.get("cpu_percent", 0), self.thresholds["cpu_usage"]),
            "Memory": self.calculate_health_score(metrics.get("memory_percent", 0), self.thresholds["memory_usage"]),
            "Disk": self.calculate_health_score(metrics.get("disk_percent", 0), self.thresholds["disk_usage"])
        }

        for component, score in health_scores.items():
            status_icon = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            response += f"## {component} Health\n"
            response += f"{status_icon} Health Score: {score}/100\n\n"

        # Overall Assessment
        overall_score = sum(health_scores.values()) / len(health_scores)
        overall_status = "Excellent" if overall_score >= 90 else "Good" if overall_score >= 80 else "Fair" if overall_score >= 70 else "Poor"

        response += f"## Overall Assessment\n"
        response += f"**Health Score**: {overall_score:.1f}/100\n"
        response += f"**Status**: {overall_status}\n\n"

        if overall_score < 80:
            response += "## Recommended Actions\n"
            response += "- Review resource usage patterns\n"
            response += "- Consider scaling resources\n"
            response += "- Check for performance bottlenecks\n"
            response += "- Review recent configuration changes\n"

        return response

    async def analyze_capacity(self) -> str:
        """Analyze system capacity and scaling needs"""
        metrics = await self.get_current_metrics()

        response = "# Capacity Analysis\n\n"
        response += f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Current Usage vs Capacity
        response += "## Current Resource Utilization\n\n"

        cpu_usage = metrics.get("cpu_percent", 0)
        memory_usage = metrics.get("memory_percent", 0)
        disk_usage = metrics.get("disk_percent", 0)

        response += f"- CPU: {cpu_usage:.1f}% of capacity\n"
        response += f"- Memory: {memory_usage:.1f}% of capacity\n"
        response += f"- Disk: {disk_usage:.1f}% of capacity\n\n"

        # Scaling Recommendations
        response += "## Scaling Recommendations\n\n"

        if cpu_usage > 85:
            response += "⚠️ **CPU Scaling Recommended**\n"
            response += "- Consider increasing CPU cores or upgrading instance type\n\n"

        if memory_usage > 85:
            response += "⚠️ **Memory Scaling Recommended**\n"
            response += "- Consider increasing RAM or optimizing memory usage\n\n"

        if disk_usage > 85:
            response += "⚠️ **Storage Scaling Recommended**\n"
            response += "- Consider increasing disk space or implementing data archiving\n\n"

        if max(cpu_usage, memory_usage, disk_usage) < 70:
            response += "✅ **Current capacity is adequate**\n"
            response += "- No immediate scaling required\n"
            response += "- Monitor usage trends for future planning\n"

        return response

    async def provide_general_monitoring_info(self) -> str:
        """Provide general monitoring information"""
        response = "# System Monitoring Information\n\n"

        response += "I can help you monitor and analyze system performance. Here are the key areas I cover:\n\n"

        response += "## Monitoring Capabilities\n\n"
        response += "• **Real-time Metrics**: CPU, memory, disk, and network usage\n"
        response += "• **Performance Analysis**: Response times and throughput\n"
        response += "• **Health Checks**: Automated system health assessment\n"
        response += "• **Alert Management**: Proactive issue detection and notification\n"
        response += "• **Capacity Planning**: Resource usage analysis and scaling recommendations\n"
        response += "• **Trend Analysis**: Historical performance pattern identification\n\n"

        response += "## Available Commands\n\n"
        response += "• 'Show system status' - Current system overview\n"
        response += "• 'Generate performance report' - Detailed metrics analysis\n"
        response += "• 'Check alerts' - Active issues and warnings\n"
        response += "• 'Assess system health' - Comprehensive health evaluation\n"
        response += "• 'Analyze capacity' - Scaling and resource recommendations\n\n"

        response += "What would you like to monitor or analyze?"

        return response

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "error": str(e)
            }

    async def record_metrics(self):
        """Record current metrics to history"""
        metrics = await self.get_current_metrics()

        # Add to history (keeping only recent readings)
        for key in ["cpu_percent", "memory_percent", "disk_percent"]:
            if key in metrics:
                self.metrics_history[key[:-8]].append(metrics[key])  # Remove '_percent'
                if len(self.metrics_history[key[:-8]]) > self.max_history_size:
                    self.metrics_history[key[:-8]].pop(0)

    async def check_active_alerts(self) -> List[Dict[str, Any]]:
        """Check for active alerts based on thresholds"""
        alerts = []
        metrics = await self.get_current_metrics()

        # CPU Alert
        if metrics.get("cpu_percent", 0) > self.thresholds["cpu_usage"]:
            alerts.append({
                "severity": "warning",
                "component": "CPU",
                "message": "High CPU usage detected",
                "current": f"{metrics['cpu_percent']:.1f}%",
                "threshold": f"{self.thresholds['cpu_usage']}%"
            })

        # Memory Alert
        if metrics.get("memory_percent", 0) > self.thresholds["memory_usage"]:
            alerts.append({
                "severity": "warning",
                "component": "Memory",
                "message": "High memory usage detected",
                "current": f"{metrics['memory_percent']:.1f}%",
                "threshold": f"{self.thresholds['memory_usage']}%"
            })

        # Disk Alert
        if metrics.get("disk_percent", 0) > self.thresholds["disk_usage"]:
            alerts.append({
                "severity": "critical",
                "component": "Disk",
                "message": "High disk usage detected",
                "current": f"{metrics['disk_percent']:.1f}%",
                "threshold": f"{self.thresholds['disk_usage']}%"
            })

        return alerts

    def calculate_overall_status(self, metrics: Dict[str, Any]) -> str:
        """Calculate overall system status"""
        cpu = metrics.get("cpu_percent", 0)
        memory = metrics.get("memory_percent", 0)
        disk = metrics.get("disk_percent", 0)

        avg_usage = (cpu + memory + disk) / 3

        if avg_usage < 60:
            return "🟢 Excellent - All systems operating normally"
        elif avg_usage < 75:
            return "🟡 Good - Minor resource usage"
        elif avg_usage < 85:
            return "🟠 Fair - Moderate resource usage"
        else:
            return "🔴 Critical - High resource usage, immediate attention needed"

    def calculate_health_score(self, current: float, threshold: float) -> float:
        """Calculate health score based on current value and threshold"""
        if current <= threshold * 0.7:  # Well below threshold
            return 100.0
        elif current <= threshold:  # At or near threshold
            return 80.0 - ((current - threshold * 0.7) / (threshold * 0.3)) * 20.0
        else:  # Above threshold
            return max(0.0, 60.0 - ((current - threshold) / threshold) * 40.0)

    def analyze_trend(self, readings: List[float]) -> str:
        """Analyze trend in readings"""
        if len(readings) < 2:
            return "Insufficient data"

        recent = readings[-10:] if len(readings) >= 10 else readings
        avg_recent = sum(recent) / len(recent)

        earlier = readings[-20:-10] if len(readings) >= 20 else readings[:len(readings)//2]
        if earlier:
            avg_earlier = sum(earlier) / len(earlier)
            change = avg_recent - avg_earlier

            if abs(change) < 5:
                return "Stable"
            elif change > 0:
                return f"Increasing (+{change:.1f})"
            else:
                return f"Decreasing ({change:.1f})"

        return "Analyzing..."

    async def generate_recommendations(self) -> str:
        """Generate performance recommendations"""
        recommendations = ""

        cpu_readings = self.metrics_history.get("cpu", [])
        memory_readings = self.metrics_history.get("memory", [])

        if cpu_readings and max(cpu_readings) > 90:
            recommendations += "• Consider CPU optimization or scaling\n"

        if memory_readings and max(memory_readings) > 90:
            recommendations += "• Implement memory optimization strategies\n"

        if not recommendations:
            recommendations = "• System performance is within acceptable ranges\n"
            recommendations += "• Continue regular monitoring\n"

        return recommendations

