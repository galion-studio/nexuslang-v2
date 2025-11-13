#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for RunPod
Shows service status, resource usage, and logs
"""

import subprocess
import time
import os
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_service_status(port):
    """Check if service is running on port"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'http://localhost:{port}/health'],
            capture_output=True,
            timeout=2
        )
        return "🟢 UP" if result.returncode == 0 else "🔴 DOWN"
    except:
        return "🔴 DOWN"

def get_process_count(pattern):
    """Count processes matching pattern"""
    try:
        result = subprocess.run(
            ['pgrep', '-fc', pattern],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() or "0"
    except:
        return "0"

def get_resource_usage():
    """Get CPU and memory usage"""
    try:
        # CPU usage
        cpu = subprocess.run(
            ['top', '-bn1'],
            capture_output=True,
            text=True
        ).stdout.split('\n')[2].split()[1]
        
        # Memory usage
        mem = subprocess.run(
            ['free', '-h'],
            capture_output=True,
            text=True
        ).stdout.split('\n')[1].split()
        
        return cpu, mem[2], mem[1]
    except:
        return "N/A", "N/A", "N/A"

def get_recent_logs(log_file, lines=5):
    """Get recent log entries"""
    try:
        result = subprocess.run(
            ['tail', '-n', str(lines), log_file],
            capture_output=True,
            text=True
        )
        return result.stdout
    except:
        return "No logs available"

def main():
    """Main dashboard loop"""
    while True:
        clear_screen()
        
        print("=" * 80)
        print(" 🚀 GALION ECOSYSTEM - RUNPOD MONITORING DASHBOARD")
        print("=" * 80)
        print(f" Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Service Status
        print("📊 SERVICE STATUS:")
        print("-" * 80)
        print(f"  Backend (8000):        {get_service_status(8000)}")
        print(f"  Frontend (3000):       {get_service_status(3000)}")
        print(f"  Galion Studio (3001):  {get_service_status(3001)}")
        print()
        
        # Process Counts
        print("🔢 PROCESS COUNTS:")
        print("-" * 80)
        print(f"  Backend processes:     {get_process_count('uvicorn')}")
        print(f"  Frontend processes:    {get_process_count('node.*3000')}")
        print(f"  Studio processes:      {get_process_count('node.*3001')}")
        print(f"  LocalTunnel processes: {get_process_count('lt --port')}")
        print()
        
        # Resource Usage
        cpu, mem_used, mem_total = get_resource_usage()
        print("💻 RESOURCE USAGE:")
        print("-" * 80)
        print(f"  CPU Usage:   {cpu}")
        print(f"  Memory:      {mem_used} / {mem_total}")
        print()
        
        # Recent Backend Logs
        print("📝 RECENT BACKEND LOGS:")
        print("-" * 80)
        logs = get_recent_logs('/workspace/logs/backend.log', 3)
        for line in logs.split('\n')[-3:]:
            if line.strip():
                print(f"  {line[:76]}")
        print()
        
        # URLs
        print("🌐 PUBLIC URLS:")
        print("-" * 80)
        print("  Backend:  https://nexuslang-backend.loca.lt/docs")
        print("  Frontend: https://nexuslang-frontend.loca.lt")
        print("  Studio:   https://nexuslang-studio.loca.lt")
        print()
        
        print("=" * 80)
        print(" Press Ctrl+C to exit | Refreshing every 10 seconds...")
        print("=" * 80)
        
        time.sleep(10)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard closed.")
        exit(0)

