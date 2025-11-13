"""
Health Monitoring Dashboard for Nexus Services
Real-time dashboard showing service status, performance metrics, and alerts.
"""

import psutil
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

# Configuration
LOG_DIR = Path("/workspace/logs")
STATUS_FILE = LOG_DIR / "service_status.json"


class HealthDashboard:
    """
    Real-time health monitoring dashboard.
    Displays service status, resource usage, and performance metrics.
    """
    
    def __init__(self):
        self.services = {
            "postgres": {"port": 5432, "name": "PostgreSQL"},
            "redis": {"port": 6379, "name": "Redis"},
            "backend": {"port": 8000, "name": "Backend API"},
            "developer-frontend": {"port": 3000, "name": "developer.galion.app"},
            "galion-studio": {"port": 3001, "name": "galion.studio"}
        }
    
    def check_port(self, port: int) -> bool:
        """Check if a port is listening."""
        try:
            result = subprocess.run(
                f"lsof -i :{port} -t",
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_service_status(self) -> Dict:
        """Get current status of all services."""
        status = {}
        
        for service_id, config in self.services.items():
            is_running = self.check_port(config["port"])
            status[service_id] = {
                "name": config["name"],
                "port": config["port"],
                "status": "running" if is_running else "stopped",
                "timestamp": datetime.now().isoformat()
            }
        
        return status
    
    def get_system_metrics(self) -> Dict:
        """Get system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total / (1024 ** 3),  # GB
                    "used": memory.used / (1024 ** 3),
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total / (1024 ** 3),
                    "used": disk.used / (1024 ** 3),
                    "percent": disk.percent
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_response_times(self) -> Dict:
        """Measure response times for HTTP services."""
        import requests
        
        response_times = {}
        
        # Backend API
        try:
            start = time.time()
            requests.get("http://localhost:8000/health", timeout=5)
            response_times["backend"] = round((time.time() - start) * 1000, 2)  # ms
        except:
            response_times["backend"] = None
        
        # Developer Frontend
        try:
            start = time.time()
            requests.get("http://localhost:3000", timeout=5)
            response_times["developer-frontend"] = round((time.time() - start) * 1000, 2)
        except:
            response_times["developer-frontend"] = None
        
        # Galion Studio
        try:
            start = time.time()
            requests.get("http://localhost:3001", timeout=5)
            response_times["galion-studio"] = round((time.time() - start) * 1000, 2)
        except:
            response_times["galion-studio"] = None
        
        return response_times
    
    def render_dashboard(self):
        """Render the dashboard to console."""
        # Clear screen
        print("\033[2J\033[H")
        
        # Header
        print("=" * 80)
        print(" " * 20 + "NEXUS HEALTH MONITORING DASHBOARD")
        print(" " * 25 + f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Service Status
        print("SERVICE STATUS:")
        print("-" * 80)
        services = self.get_service_status()
        for service_id, data in services.items():
            status_icon = "✅" if data["status"] == "running" else "❌"
            print(f"  {status_icon} {data['name']:25} Port: {data['port']:5} Status: {data['status']:10}")
        print()
        
        # System Metrics
        print("SYSTEM RESOURCES:")
        print("-" * 80)
        metrics = self.get_system_metrics()
        if "error" not in metrics:
            print(f"  CPU:    {metrics['cpu']['percent']:6.2f}% ({metrics['cpu']['count']} cores)")
            print(f"  Memory: {metrics['memory']['percent']:6.2f}% ({metrics['memory']['used']:.2f}GB / {metrics['memory']['total']:.2f}GB)")
            print(f"  Disk:   {metrics['disk']['percent']:6.2f}% ({metrics['disk']['used']:.2f}GB / {metrics['disk']['total']:.2f}GB)")
        else:
            print(f"  Error: {metrics['error']}")
        print()
        
        # Response Times
        print("RESPONSE TIMES:")
        print("-" * 80)
        response_times = self.get_response_times()
        for service, time_ms in response_times.items():
            if time_ms is not None:
                status = "✅" if time_ms < 2000 else "⚠️"
                print(f"  {status} {service:25} {time_ms:8.2f} ms")
            else:
                print(f"  ❌ {service:25} Not responding")
        print()
        
        # Alerts
        print("ALERTS:")
        print("-" * 80)
        alerts = self.get_alerts(services, metrics, response_times)
        if alerts:
            for alert in alerts:
                print(f"  🚨 {alert}")
        else:
            print("  ✅ No alerts")
        print()
        
        # Footer
        print("=" * 80)
        print("Press Ctrl+C to exit | Refresh: 30s")
        print("=" * 80)
    
    def get_alerts(self, services: Dict, metrics: Dict, response_times: Dict) -> List[str]:
        """Generate alerts based on current state."""
        alerts = []
        
        # Service down alerts
        for service_id, data in services.items():
            if data["status"] != "running":
                alerts.append(f"{data['name']} is not running!")
        
        # Resource alerts
        if "error" not in metrics:
            if metrics["cpu"]["percent"] > 90:
                alerts.append(f"High CPU usage: {metrics['cpu']['percent']:.1f}%")
            if metrics["memory"]["percent"] > 90:
                alerts.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
            if metrics["disk"]["percent"] > 90:
                alerts.append(f"High disk usage: {metrics['disk']['percent']:.1f}%")
        
        # Response time alerts
        for service, time_ms in response_times.items():
            if time_ms and time_ms > 5000:
                alerts.append(f"{service} slow response: {time_ms:.0f}ms")
        
        return alerts
    
    def run(self, interval: int = 30):
        """Run the dashboard with auto-refresh."""
        print("Starting Nexus Health Dashboard...")
        print("Press Ctrl+C to exit")
        print()
        
        try:
            while True:
                self.render_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
    
    def export_status(self, filename: str = None):
        """Export current status to JSON file."""
        if filename is None:
            filename = LOG_DIR / f"health_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": self.get_service_status(),
            "system": self.get_system_metrics(),
            "response_times": self.get_response_times()
        }
        
        with open(filename, 'w') as f:
            json.dump(status, f, indent=2)
        
        return filename


def main():
    """Main entry point for dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nexus Health Monitoring Dashboard")
    parser.add_argument("--interval", type=int, default=30, help="Refresh interval in seconds")
    parser.add_argument("--export", action="store_true", help="Export status to JSON and exit")
    parser.add_argument("--once", action="store_true", help="Display once and exit")
    
    args = parser.parse_args()
    
    dashboard = HealthDashboard()
    
    if args.export:
        filename = dashboard.export_status()
        print(f"Status exported to: {filename}")
    elif args.once:
        dashboard.render_dashboard()
    else:
        dashboard.run(interval=args.interval)


if __name__ == "__main__":
    main()

