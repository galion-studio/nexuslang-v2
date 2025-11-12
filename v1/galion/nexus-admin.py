#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJECT NEXUS - ADMIN CONTROL CENTER
Owner Backdoor Access - Built on Musk's Principles

Delete the unnecessary. Optimize what remains. Ship it.
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# Fix Windows encoding issues
if os.name == 'nt':
    try:
        # Try to set UTF-8 encoding
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# ============================================================================
# STYLING - Zero external dependencies (First Principles)
# ============================================================================

class Style:
    """Terminal styling without external libraries"""
    # Colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    # Icons - Windows-safe fallbacks
    try:
        # Try Unicode first
        CHECK = '✓'
        CROSS = '✗'
        ARROW = '→'
        BULLET = '•'
        STAR = '★'
        WARNING = '⚠'
        LOCK = '[ADMIN]'  # Emoji fallback for Windows
        ROCKET = '[GO]'   # Emoji fallback for Windows
        FIRE = '[HOT]'    # Emoji fallback for Windows
    except:
        # ASCII fallbacks for problematic terminals
        CHECK = '+'
        CROSS = 'X'
        ARROW = '->'
        BULLET = '*'
        STAR = '*'
        WARNING = '!'
        LOCK = '[ADMIN]'
        ROCKET = '[GO]'
        FIRE = '[HOT]'

def clear():
    """Clear screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def box(text: str, width: int = 70, color: str = Style.CYAN) -> str:
    """Create a box around text - Windows compatible"""
    lines = text.split('\n')
    
    # Use simple ASCII box drawing for Windows compatibility
    if os.name == 'nt':
        top = f"{color}+{'-' * (width-2)}+{Style.RESET}"
        bottom = f"{color}+{'-' * (width-2)}+{Style.RESET}"
        border = '|'
    else:
        # Unicode box drawing for Linux/Mac
        top = f"{color}╔{'═' * (width-2)}╗{Style.RESET}"
        bottom = f"{color}╚{'═' * (width-2)}╝{Style.RESET}"
        border = '║'
    
    result = [top]
    for line in lines:
        padding = width - len(line) - 4
        result.append(f"{color}{border}{Style.RESET} {line}{' ' * padding} {color}{border}{Style.RESET}")
    result.append(bottom)
    
    return '\n'.join(result)

def progress_bar(current: int, total: int, width: int = 40, label: str = "") -> str:
    """Create a progress bar - Windows compatible"""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    
    # Use simple ASCII for Windows compatibility
    if os.name == 'nt':
        bar = '=' * filled + '-' * (width - filled)
    else:
        bar = '█' * filled + '░' * (width - filled)
    
    return f"{label} [{Style.GREEN}{bar}{Style.RESET}] {int(percent * 100)}%"

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================

class SystemMonitor:
    """Monitor system and Docker services"""
    
    @staticmethod
    def get_docker_services() -> Dict[str, Dict[str, str]]:
        """Get all Docker service information"""
        try:
            # Get container info
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', 
                 '{{.Names}}\t{{.Status}}\t{{.State}}\t{{.Ports}}'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=(os.name == 'nt')
            )
            
            services = {}
            for line in result.stdout.strip().split('\n'):
                if line and 'nexus-' in line:
                    parts = line.split('\t')
                    name = parts[0].replace('nexus-', '')
                    services[name] = {
                        'status': parts[1] if len(parts) > 1 else 'unknown',
                        'state': parts[2] if len(parts) > 2 else 'unknown',
                        'ports': parts[3] if len(parts) > 3 else ''
                    }
            
            return services
        except Exception as e:
            return {'error': {'status': str(e), 'state': 'error', 'ports': ''}}
    
    @staticmethod
    def get_service_health(service: str) -> Tuple[bool, str]:
        """Check if service is healthy"""
        try:
            result = subprocess.run(
                ['docker', 'inspect', f'nexus-{service}', 
                 '--format', '{{.State.Health.Status}}'],
                capture_output=True,
                text=True,
                timeout=3,
                shell=(os.name == 'nt')
            )
            
            health = result.stdout.strip()
            if health == 'healthy':
                return True, 'healthy'
            elif health == 'unhealthy':
                return False, 'unhealthy'
            else:
                # No health check defined, check if running
                result = subprocess.run(
                    ['docker', 'inspect', f'nexus-{service}', 
                     '--format', '{{.State.Running}}'],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    shell=(os.name == 'nt')
                )
                running = result.stdout.strip() == 'true'
                return running, 'running' if running else 'stopped'
        except:
            return False, 'unknown'
    
    @staticmethod
    def get_resource_usage(service: str) -> Dict[str, str]:
        """Get resource usage for a service"""
        try:
            result = subprocess.run(
                ['docker', 'stats', f'nexus-{service}', '--no-stream', 
                 '--format', '{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'],
                capture_output=True,
                text=True,
                timeout=3,
                shell=(os.name == 'nt')
            )
            
            parts = result.stdout.strip().split('\t')
            return {
                'cpu': parts[0] if len(parts) > 0 else 'N/A',
                'memory': parts[1] if len(parts) > 1 else 'N/A',
                'network': parts[2] if len(parts) > 2 else 'N/A'
            }
        except:
            return {'cpu': 'N/A', 'memory': 'N/A', 'network': 'N/A'}

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

class Dashboard:
    """Main admin dashboard"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
    
    def render_header(self):
        """Render dashboard header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Windows-compatible box drawing
        if os.name == 'nt':
            header = f"""
{Style.BOLD}{Style.CYAN}
+-----------------------------------------------------------------------+
|                  PROJECT NEXUS - ADMIN CONTROL CENTER                 |
|                         OWNER BACKDOOR ACCESS                         |
+-----------------------------------------------------------------------+
{Style.RESET}
{Style.YELLOW}{Style.LOCK} ADMIN BACKDOOR ACTIVE{Style.RESET} | {Style.GREEN}Access Level: GOD MODE{Style.RESET} | {Style.CYAN}Build: ALPHA{Style.RESET}
{Style.DIM}Owner: Gigabyte | Timestamp: {timestamp}{Style.RESET}
"""
        else:
            header = f"""
{Style.BOLD}{Style.CYAN}
╔═══════════════════════════════════════════════════════════════════════╗
║                  PROJECT NEXUS - ADMIN CONTROL CENTER                 ║
║                         OWNER BACKDOOR ACCESS                         ║
╚═══════════════════════════════════════════════════════════════════════╝
{Style.RESET}
{Style.YELLOW}{Style.LOCK} ADMIN BACKDOOR ACTIVE{Style.RESET} | {Style.GREEN}Access Level: GOD MODE{Style.RESET} | {Style.CYAN}Build: ALPHA{Style.RESET}
{Style.DIM}Owner: Gigabyte | Timestamp: {timestamp}{Style.RESET}
"""
        print(header)
    
    def render_services(self):
        """Render service status"""
        services = self.monitor.get_docker_services()
        
        # Windows-compatible header
        if os.name == 'nt':
            print(f"\n{Style.BOLD}{Style.CYAN}+=== SERVICE STATUS ===+{Style.RESET}\n")
        else:
            print(f"\n{Style.BOLD}{Style.CYAN}╔═══ SERVICE STATUS ═══╗{Style.RESET}\n")
        
        if 'error' in services:
            print(f"{Style.RED}{Style.CROSS} Docker Error: {services['error']['status']}{Style.RESET}")
            print(f"{Style.YELLOW}{Style.ARROW} Start Docker Desktop or Docker service{Style.RESET}")
            return
        
        if not services:
            print(f"{Style.YELLOW}{Style.WARNING} No services found - Run 'start' to launch{Style.RESET}")
            return
        
        # Core services list
        core = ['api-gateway', 'auth-service', 'user-service', 'analytics-service',
                'postgres', 'redis', 'kafka', 'zookeeper']
        
        monitoring = ['prometheus', 'grafana', 'kafka-ui']
        
        # Display core services
        print(f"{Style.BOLD}Core Services:{Style.RESET}")
        self._render_service_list(services, core)
        
        # Display monitoring services
        print(f"\n{Style.BOLD}Monitoring:{Style.RESET}")
        self._render_service_list(services, monitoring)
        
        # Display other services
        other = set(services.keys()) - set(core) - set(monitoring)
        if other:
            print(f"\n{Style.BOLD}Other Services:{Style.RESET}")
            self._render_service_list(services, list(other))
        
        # Service count summary
        running = sum(1 for s in services.values() if 'running' in s['state'].lower())
        total = len(services)
        print(f"\n{progress_bar(running, total, 30, 'System Health')}")
    
    def _render_service_list(self, services: Dict, service_list: List[str]):
        """Render a list of services"""
        for service in service_list:
            if service in services:
                info = services[service]
                state = info['state'].lower()
                
                if 'running' in state:
                    icon = f"{Style.GREEN}{Style.CHECK}{Style.RESET}"
                    status = f"{Style.GREEN}{info['status']}{Style.RESET}"
                elif 'exited' in state:
                    icon = f"{Style.RED}{Style.CROSS}{Style.RESET}"
                    status = f"{Style.RED}{info['status']}{Style.RESET}"
                else:
                    icon = f"{Style.YELLOW}{Style.WARNING}{Style.RESET}"
                    status = f"{Style.YELLOW}{info['status']}{Style.RESET}"
                
                # Show ports if available
                ports = f" ({info['ports']})" if info['ports'] else ""
                print(f"  {icon} {service:25} {status}{Style.DIM}{ports}{Style.RESET}")
            else:
                print(f"  {Style.DIM}{Style.BULLET} {service:25} Not Found{Style.RESET}")
    
    def render_quick_stats(self):
        """Render quick statistics"""
        if os.name == 'nt':
            print(f"\n{Style.BOLD}{Style.CYAN}+=== QUICK ACCESS ===+{Style.RESET}\n")
        else:
            print(f"\n{Style.BOLD}{Style.CYAN}╔═══ QUICK ACCESS ═══╗{Style.RESET}\n")
        
        endpoints = [
            ("API Gateway", "http://localhost:8080", "Main API endpoint"),
            ("Grafana Dashboard", "http://localhost:3000", "Monitoring & Metrics"),
            ("Prometheus", "http://localhost:9091", "Metrics Database"),
            ("Kafka UI", "http://localhost:8090", "Message Queue Manager"),
        ]
        
        for name, url, desc in endpoints:
            print(f"  {Style.CYAN}{Style.BULLET}{Style.RESET} {name:20} {Style.BLUE}{url:30}{Style.RESET} {Style.DIM}{desc}{Style.RESET}")
    
    def render_commands(self):
        """Render available commands"""
        if os.name == 'nt':
            print(f"\n{Style.BOLD}{Style.CYAN}+=== ADMIN COMMANDS ===+{Style.RESET}\n")
        else:
            print(f"\n{Style.BOLD}{Style.CYAN}╔═══ ADMIN COMMANDS ═══╗{Style.RESET}\n")
        
        commands = [
            ("status", "Refresh dashboard"),
            ("start", "Start all services"),
            ("stop", "Stop all services"),
            ("restart <service>", "Restart specific service"),
            ("logs <service>", "View service logs"),
            ("users", "Manage users (admin backdoor)"),
            ("monitor", "Real-time monitoring mode"),
            ("help", "Show all commands"),
        ]
        
        for cmd, desc in commands:
            print(f"  {Style.GREEN}{cmd:25}{Style.RESET} {Style.DIM}{desc}{Style.RESET}")
    
    def render_full(self):
        """Render full dashboard"""
        clear()
        self.render_header()
        self.render_services()
        self.render_quick_stats()
        self.render_commands()
        print()

# ============================================================================
# ADMIN COMMANDS
# ============================================================================

class AdminCommands:
    """Execute admin commands"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
        self.dashboard = Dashboard()
    
    def execute(self, command: str):
        """Execute a command"""
        parts = command.strip().split()
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Route to appropriate handler
        handlers = {
            'status': self.cmd_status,
            'start': self.cmd_start,
            'stop': self.cmd_stop,
            'restart': self.cmd_restart,
            'logs': self.cmd_logs,
            'exec': self.cmd_exec,
            'db': self.cmd_db,
            'redis': self.cmd_redis,
            'users': self.cmd_users,
            'monitor': self.cmd_monitor,
            'backup': self.cmd_backup,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'q': self.cmd_exit,
        }
        
        handler = handlers.get(cmd)
        if handler:
            handler(args)
        else:
            print(f"{Style.RED}{Style.CROSS} Unknown command: {cmd}{Style.RESET}")
            print(f"{Style.YELLOW}Type 'help' for available commands{Style.RESET}")
    
    def cmd_status(self, args: List[str]):
        """Refresh dashboard"""
        self.dashboard.render_full()
    
    def cmd_start(self, args: List[str]):
        """Start all services"""
        print(f"{Style.YELLOW}Starting Project Nexus...{Style.RESET}")
        
        try:
            # Start with docker-compose
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                capture_output=True,
                text=True,
                shell=(os.name == 'nt')
            )
            
            if result.returncode == 0:
                print(f"{Style.GREEN}{Style.CHECK} Services started successfully{Style.RESET}")
                
                # Show startup progress
                print(f"\n{Style.CYAN}Waiting for services to initialize...{Style.RESET}")
                time.sleep(2)
                
                # Check service health
                services = ['postgres', 'redis', 'kafka', 'api-gateway']
                for i, service in enumerate(services):
                    time.sleep(1)
                    healthy, status = self.monitor.get_service_health(service)
                    icon = Style.CHECK if healthy else Style.CROSS
                    color = Style.GREEN if healthy else Style.YELLOW
                    print(f"  {color}{icon} {service}: {status}{Style.RESET}")
                
                print(f"\n{Style.GREEN}{Style.ROCKET} System ready!{Style.RESET}")
            else:
                print(f"{Style.RED}{Style.CROSS} Error starting services:{Style.RESET}")
                print(result.stderr)
        
        except FileNotFoundError:
            print(f"{Style.RED}{Style.CROSS} docker-compose not found{Style.RESET}")
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_stop(self, args: List[str]):
        """Stop all services"""
        print(f"{Style.YELLOW}Stopping all services...{Style.RESET}")
        
        try:
            subprocess.run(
                ['docker-compose', 'down'],
                check=True,
                shell=(os.name == 'nt')
            )
            print(f"{Style.GREEN}{Style.CHECK} Services stopped{Style.RESET}")
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_restart(self, args: List[str]):
        """Restart a service"""
        if not args:
            print(f"{Style.YELLOW}Usage: restart <service-name>{Style.RESET}")
            return
        
        service = args[0]
        print(f"{Style.YELLOW}Restarting nexus-{service}...{Style.RESET}")
        
        try:
            subprocess.run(
                ['docker', 'restart', f'nexus-{service}'],
                check=True,
                shell=(os.name == 'nt')
            )
            print(f"{Style.GREEN}{Style.CHECK} Service restarted{Style.RESET}")
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_logs(self, args: List[str]):
        """View service logs"""
        if not args:
            print(f"{Style.YELLOW}Usage: logs <service-name> [lines]{Style.RESET}")
            return
        
        service = args[0]
        lines = args[1] if len(args) > 1 else '50'
        
        print(f"\n{Style.CYAN}Last {lines} lines from {service}:{Style.RESET}\n")
        
        try:
            result = subprocess.run(
                ['docker', 'logs', '--tail', lines, f'nexus-{service}'],
                shell=(os.name == 'nt')
            )
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_exec(self, args: List[str]):
        """Execute command in container"""
        if len(args) < 2:
            print(f"{Style.YELLOW}Usage: exec <service> <command>{Style.RESET}")
            return
        
        service = args[0]
        command = ' '.join(args[1:])
        
        try:
            subprocess.run(
                ['docker', 'exec', '-it', f'nexus-{service}', 'sh', '-c', command],
                shell=(os.name == 'nt')
            )
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_db(self, args: List[str]):
        """Open PostgreSQL CLI"""
        print(f"{Style.CYAN}Opening PostgreSQL CLI...{Style.RESET}")
        print(f"{Style.DIM}(Use \\q to exit){Style.RESET}\n")
        
        try:
            subprocess.run(
                ['docker', 'exec', '-it', 'nexus-postgres', 
                 'psql', '-U', 'nexuscore', 'nexuscore'],
                shell=(os.name == 'nt')
            )
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_redis(self, args: List[str]):
        """Open Redis CLI"""
        print(f"{Style.CYAN}Opening Redis CLI...{Style.RESET}")
        print(f"{Style.DIM}(Use exit to quit){Style.RESET}\n")
        
        try:
            subprocess.run(
                ['docker', 'exec', '-it', 'nexus-redis', 'redis-cli'],
                shell=(os.name == 'nt')
            )
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_users(self, args: List[str]):
        """User management (admin backdoor)"""
        print(f"\n{Style.CYAN}{Style.LOCK} ADMIN BACKDOOR - USER MANAGEMENT{Style.RESET}\n")
        
        # Show quick user query options
        print(f"{Style.YELLOW}Quick Actions:{Style.RESET}")
        print(f"  1. List all users")
        print(f"  2. Create admin user")
        print(f"  3. Delete user")
        print(f"  4. Query custom SQL\n")
        
        try:
            choice = input(f"{Style.CYAN}Select option (1-4):{Style.RESET} ").strip()
            
            if choice == '1':
                print(f"\n{Style.CYAN}Querying users...{Style.RESET}\n")
                subprocess.run(
                    ['docker', 'exec', 'nexus-postgres', 
                     'psql', '-U', 'nexuscore', 'nexuscore', '-c',
                     'SELECT id, email, name, role, created_at FROM users;'],
                    shell=(os.name == 'nt')
                )
            
            elif choice == '2':
                email = input("Admin email: ").strip()
                name = input("Admin name: ").strip()
                print(f"{Style.YELLOW}Creating admin user...{Style.RESET}")
                # User would need to call auth service API here
                print(f"{Style.CYAN}Use: curl -X POST http://localhost:8080/api/v1/auth/register{Style.RESET}")
            
            elif choice == '4':
                print(f"\n{Style.CYAN}Opening PostgreSQL CLI for custom queries...{Style.RESET}\n")
                self.cmd_db([])
        
        except KeyboardInterrupt:
            print(f"\n{Style.YELLOW}Cancelled{Style.RESET}")
    
    def cmd_monitor(self, args: List[str]):
        """Real-time monitoring mode"""
        print(f"{Style.CYAN}Starting real-time monitor... (Ctrl+C to exit){Style.RESET}\n")
        
        try:
            while True:
                clear()
                self.dashboard.render_full()
                
                print(f"{Style.DIM}Refreshing in 5 seconds...{Style.RESET}")
                time.sleep(5)
        
        except KeyboardInterrupt:
            print(f"\n{Style.CYAN}Monitor stopped{Style.RESET}")
    
    def cmd_backup(self, args: List[str]):
        """Backup database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nexus_backup_{timestamp}.sql"
        
        print(f"{Style.YELLOW}Creating database backup...{Style.RESET}")
        
        try:
            with open(filename, 'w') as f:
                subprocess.run(
                    ['docker', 'exec', 'nexus-postgres',
                     'pg_dump', '-U', 'nexuscore', 'nexuscore'],
                    stdout=f,
                    check=True,
                    shell=(os.name == 'nt')
                )
            
            print(f"{Style.GREEN}{Style.CHECK} Backup created: {filename}{Style.RESET}")
        except Exception as e:
            print(f"{Style.RED}{Style.CROSS} Error: {e}{Style.RESET}")
    
    def cmd_help(self, args: List[str]):
        """Show help"""
        # Windows-compatible header
        if os.name == 'nt':
            header = f"{Style.BOLD}{Style.CYAN}+=== PROJECT NEXUS - ADMIN COMMANDS ===+{Style.RESET}"
        else:
            header = f"{Style.BOLD}{Style.CYAN}╔═══ PROJECT NEXUS - ADMIN COMMANDS ═══╗{Style.RESET}"
        
        help_text = f"""
{header}

{Style.GREEN}{Style.BOLD}System Control:{Style.RESET}
  status                     - Refresh dashboard
  start                      - Start all services (docker-compose up -d)
  stop                       - Stop all services (docker-compose down)
  restart <service>          - Restart specific service

{Style.GREEN}{Style.BOLD}Monitoring & Logs:{Style.RESET}
  logs <service> [lines]     - View service logs (default: 50 lines)
  monitor                    - Real-time monitoring mode (auto-refresh)
  exec <service> <command>   - Execute command in container

{Style.GREEN}{Style.BOLD}Database Access:{Style.RESET}
  db                         - Open PostgreSQL CLI
  redis                      - Open Redis CLI
  backup                     - Backup database to SQL file

{Style.GREEN}{Style.BOLD}Admin Backdoor:{Style.RESET}
  users                      - User management (list, create, delete)

{Style.GREEN}{Style.BOLD}Examples:{Style.RESET}
  logs api-gateway 100       - Show 100 lines from API Gateway
  restart auth-service       - Restart authentication service
  exec postgres psql -U nexuscore   - Run psql command
  monitor                    - Watch services in real-time

{Style.YELLOW}{Style.BOLD}Other:{Style.RESET}
  help                       - Show this help
  exit, quit, q              - Exit admin terminal

{Style.CYAN}Built with Elon Musk's First Principles: Delete, Optimize, Ship.{Style.RESET}
"""
        print(help_text)
    
    def cmd_exit(self, args: List[str]):
        """Exit terminal"""
        print(f"{Style.CYAN}Goodbye!{Style.RESET}")
        sys.exit(0)

# ============================================================================
# INTERACTIVE SHELL
# ============================================================================

def interactive_mode():
    """Run interactive admin shell"""
    admin = AdminCommands()
    
    # Show initial dashboard
    admin.dashboard.render_full()
    
    print(f"{Style.YELLOW}Type 'help' for commands or 'exit' to quit{Style.RESET}\n")
    
    while True:
        try:
            command = input(f"{Style.BOLD}{Style.CYAN}nexus-admin>{Style.RESET} ")
            admin.execute(command)
        except KeyboardInterrupt:
            print(f"\n{Style.YELLOW}Use 'exit' to quit{Style.RESET}")
        except EOFError:
            break

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Project Nexus Admin Terminal - Owner Backdoor Access',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nexus-admin.py              # Interactive mode
  python nexus-admin.py status       # Show status once
  python nexus-admin.py start        # Start all services
  python nexus-admin.py logs api-gateway 100
        """
    )
    parser.add_argument('command', nargs='*', help='Command to execute (optional)')
    parser.add_argument('--version', action='version', version='Nexus Admin 1.0 Alpha')
    
    args = parser.parse_args()
    
    if args.command:
        # Single command mode
        admin = AdminCommands()
        admin.execute(' '.join(args.command))
    else:
        # Interactive mode
        interactive_mode()

if __name__ == '__main__':
    main()

