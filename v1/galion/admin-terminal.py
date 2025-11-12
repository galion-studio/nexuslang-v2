#!/usr/bin/env python3
"""
PROJECT NEXUS - ADMIN TERMINAL
Built with Elon Musk's First Principles:
1. Delete unnecessary parts
2. Optimize what remains
3. Ship it fast
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Color codes for terminal (no external dependencies - KISS principle)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display admin terminal banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║                     PROJECT NEXUS - ADMIN CORE                    ║
║                    Authorized Access Only                         ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
{Colors.YELLOW}⚡ ADMIN BACKDOOR ACTIVE - FULL SYSTEM CONTROL{Colors.ENDC}
{Colors.GREEN}Owner: Gigabyte | Access Level: GOD MODE | Build: ALPHA{Colors.ENDC}
"""
    print(banner)

def get_docker_service_status() -> Dict[str, str]:
    """Get status of all Docker services"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}\t{{.State}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        services = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    name = parts[0].replace('nexus-', '')
                    status = parts[1]
                    state = parts[2]
                    services[name] = f"{state} - {status}"
        
        return services
    except Exception as e:
        return {"error": str(e)}

def get_system_info() -> Dict[str, str]:
    """Get system information"""
    info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": sys.platform,
        "python": sys.version.split()[0],
    }
    
    # Get Docker info
    try:
        result = subprocess.run(['docker', 'version', '--format', '{{.Server.Version}}'],
                              capture_output=True, text=True, timeout=5)
        info["docker"] = result.stdout.strip()
    except:
        info["docker"] = "N/A"
    
    return info

def print_service_status():
    """Display service status dashboard"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔═══ SERVICE STATUS ═══╗{Colors.ENDC}")
    
    services = get_docker_service_status()
    
    if "error" in services:
        print(f"{Colors.RED}✗ Docker Error: {services['error']}{Colors.ENDC}")
        print(f"{Colors.YELLOW}→ Run 'docker ps' manually or start Docker{Colors.ENDC}")
        return
    
    if not services:
        print(f"{Colors.YELLOW}⚠ No services running{Colors.ENDC}")
        return
    
    # Define core services
    core_services = ['api-gateway', 'auth-service', 'user-service', 'analytics-service',
                    'postgres', 'redis', 'kafka', 'zookeeper', 'prometheus', 'grafana']
    
    for service in core_services:
        if service in services:
            status = services[service]
            if 'running' in status.lower() or 'up' in status.lower():
                print(f"{Colors.GREEN}✓{Colors.ENDC} {service:20} {Colors.GREEN}{status}{Colors.ENDC}")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} {service:20} {Colors.RED}{status}{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}○{Colors.ENDC} {service:20} {Colors.YELLOW}Not Found{Colors.ENDC}")
    
    # Show any other services
    other = set(services.keys()) - set(core_services)
    if other:
        print(f"\n{Colors.CYAN}Additional Services:{Colors.ENDC}")
        for service in other:
            print(f"  • {service}: {services[service]}")

def print_system_overview():
    """Display system overview"""
    info = get_system_info()
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔═══ SYSTEM OVERVIEW ═══╗{Colors.ENDC}")
    print(f"{Colors.BLUE}Timestamp:{Colors.ENDC} {info['timestamp']}")
    print(f"{Colors.BLUE}Platform:{Colors.ENDC}  {info['os']}")
    print(f"{Colors.BLUE}Python:{Colors.ENDC}    {info['python']}")
    print(f"{Colors.BLUE}Docker:{Colors.ENDC}    {info['docker']}")

def get_recent_logs(service: str, lines: int = 20) -> str:
    """Get recent logs from a service"""
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', str(lines), f'nexus-{service}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"

def execute_admin_command(command: str):
    """Execute admin commands"""
    parts = command.strip().split()
    
    if not parts:
        return
    
    cmd = parts[0].lower()
    
    if cmd == 'status':
        clear_screen()
        print_banner()
        print_system_overview()
        print_service_status()
    
    elif cmd == 'logs':
        if len(parts) < 2:
            print(f"{Colors.YELLOW}Usage: logs <service-name> [lines]{Colors.ENDC}")
            return
        service = parts[1]
        lines = int(parts[2]) if len(parts) > 2 else 20
        print(f"\n{Colors.CYAN}Recent logs from {service}:{Colors.ENDC}\n")
        print(get_recent_logs(service, lines))
    
    elif cmd == 'restart':
        if len(parts) < 2:
            print(f"{Colors.YELLOW}Usage: restart <service-name>{Colors.ENDC}")
            return
        service = parts[1]
        print(f"{Colors.YELLOW}Restarting nexus-{service}...{Colors.ENDC}")
        try:
            subprocess.run(['docker', 'restart', f'nexus-{service}'], check=True)
            print(f"{Colors.GREEN}✓ Service restarted{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'start':
        print(f"{Colors.YELLOW}Starting all services...{Colors.ENDC}")
        try:
            subprocess.run(['docker-compose', 'up', '-d'], check=True)
            print(f"{Colors.GREEN}✓ Services started{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'stop':
        print(f"{Colors.YELLOW}Stopping all services...{Colors.ENDC}")
        try:
            subprocess.run(['docker-compose', 'down'], check=True)
            print(f"{Colors.GREEN}✓ Services stopped{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'exec':
        if len(parts) < 3:
            print(f"{Colors.YELLOW}Usage: exec <service-name> <command>{Colors.ENDC}")
            return
        service = parts[1]
        exec_cmd = ' '.join(parts[2:])
        try:
            result = subprocess.run(
                ['docker', 'exec', '-it', f'nexus-{service}', 'sh', '-c', exec_cmd],
                check=True
            )
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'db':
        print(f"{Colors.CYAN}Opening PostgreSQL CLI...{Colors.ENDC}")
        try:
            subprocess.run(['docker', 'exec', '-it', 'nexus-postgres', 
                          'psql', '-U', 'nexuscore', 'nexuscore'])
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'redis':
        print(f"{Colors.CYAN}Opening Redis CLI...{Colors.ENDC}")
        try:
            subprocess.run(['docker', 'exec', '-it', 'nexus-redis', 'redis-cli'])
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
    
    elif cmd == 'help':
        print_help()
    
    elif cmd in ['exit', 'quit', 'q']:
        print(f"{Colors.CYAN}Goodbye!{Colors.ENDC}")
        sys.exit(0)
    
    else:
        print(f"{Colors.RED}Unknown command: {cmd}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Type 'help' for available commands{Colors.ENDC}")

def print_help():
    """Display help menu"""
    help_text = f"""
{Colors.CYAN}{Colors.BOLD}╔═══ ADMIN COMMANDS ═══╗{Colors.ENDC}

{Colors.GREEN}System Control:{Colors.ENDC}
  status                    - Show service status dashboard
  start                     - Start all services
  stop                      - Stop all services
  restart <service>         - Restart specific service

{Colors.GREEN}Monitoring:{Colors.ENDC}
  logs <service> [lines]    - View service logs (default: 20 lines)
  exec <service> <command>  - Execute command in service container

{Colors.GREEN}Database Access:{Colors.ENDC}
  db                        - Open PostgreSQL CLI
  redis                     - Open Redis CLI

{Colors.GREEN}Examples:{Colors.ENDC}
  logs api-gateway 50       - Show 50 lines from API Gateway
  restart auth-service      - Restart auth service
  exec postgres ls -la      - List files in postgres container

{Colors.YELLOW}Other:{Colors.ENDC}
  help                      - Show this help
  exit, quit, q             - Exit admin terminal
"""
    print(help_text)

def interactive_mode():
    """Run in interactive mode"""
    clear_screen()
    print_banner()
    print_system_overview()
    print_service_status()
    print(f"\n{Colors.YELLOW}Type 'help' for commands or 'exit' to quit{Colors.ENDC}\n")
    
    while True:
        try:
            command = input(f"{Colors.BOLD}{Colors.CYAN}nexus-admin>{Colors.ENDC} ")
            execute_admin_command(command)
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}Use 'exit' to quit{Colors.ENDC}")
        except EOFError:
            break

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Project Nexus Admin Terminal',
        epilog='Run without arguments for interactive mode'
    )
    parser.add_argument('command', nargs='*', help='Command to execute')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    if args.command:
        # Single command mode
        execute_admin_command(' '.join(args.command))
    else:
        # Interactive mode
        interactive_mode()

if __name__ == '__main__':
    main()

