# 🛠️ Utility Scripts

**Collection of helper scripts for deployment, management, and maintenance**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Deployment Scripts](#deployment-scripts)
- [Database Scripts](#database-scripts)
- [Monitoring Scripts](#monitoring-scripts)
- [Maintenance Scripts](#maintenance-scripts)
- [Testing Scripts](#testing-scripts)
- [Usage Guidelines](#usage-guidelines)

---

## 🎯 Overview

This directory contains utility scripts for various operational tasks. All scripts are documented and tested for reliability.

---

## 🚀 Deployment Scripts

### runpod-diagnose-and-fix.sh

**Purpose**: Automated diagnostic and deployment for RunPod

**Usage**:
```bash
chmod +x runpod-diagnose-and-fix.sh
./runpod-diagnose-and-fix.sh
```

**What it does**:
- ✅ Checks environment and dependencies
- ✅ Kills conflicting processes
- ✅ Installs missing packages
- ✅ Tests Python imports
- ✅ Starts the server
- ✅ Verifies deployment
- ✅ Shows public IP

**Requirements**:
- Bash 4.0+
- Root or sudo access
- Internet connection

---

### runpod-start-simple.sh

**Purpose**: Start simplified server with minimal dependencies

**Usage**:
```bash
chmod +x runpod-start-simple.sh
./runpod-start-simple.sh
```

**What it does**:
- Stops existing servers
- Starts `main_simple.py`
- Tests health endpoint
- Shows access URLs

**Best for**:
- When imports fail
- Quick deployments
- Testing

---

### runpod-start-server.sh

**Purpose**: Start full-featured server with all modules

**Usage**:
```bash
chmod +x runpod-start-server.sh
./runpod-start-server.sh
```

**What it does**:
- Installs all dependencies
- Starts `main.py` with all features
- Comprehensive logging
- Production-ready configuration

**Best for**:
- Production deployments
- Full functionality needed
- Development with all features

---

### runpod-stop-server.sh

**Purpose**: Safely stop running server

**Usage**:
```bash
chmod +x runpod-stop-server.sh
./runpod-stop-server.sh
```

**What it does**:
- Finds running server processes
- Gracefully stops them
- Cleans up PID files
- Verifies shutdown

---

## 🗄️ Database Scripts

### v2/backend/scripts/setup_database.py

**Purpose**: Initialize database schema and tables

**Usage**:
```bash
cd v2/backend
python scripts/setup_database.py
```

**What it does**:
- Creates database if not exists
- Runs migrations
- Sets up initial schema
- Creates admin user

**Configuration**:
```python
# Uses DATABASE_URL from environment
export DATABASE_URL=postgresql://user:pass@localhost:5432/nexus
```

---

### v2/backend/scripts/seed_database.py

**Purpose**: Populate database with sample data

**Usage**:
```bash
cd v2/backend
python scripts/seed_database.py
```

**What it does**:
- Adds sample users
- Creates test projects
- Populates knowledge base
- Sets up templates

**Options**:
```bash
# Seed with specific data
python scripts/seed_database.py --users 100 --projects 50

# Reset and seed
python scripts/seed_database.py --reset
```

---

### v2/backend/scripts/optimize_database.py

**Purpose**: Optimize database performance

**Usage**:
```bash
cd v2/backend
python scripts/optimize_database.py
```

**What it does**:
- Analyzes table statistics
- Rebuilds indexes
- Vacuums tables
- Updates query planner stats

**Schedule**: Run weekly or after large data imports

---

## 📊 Monitoring Scripts

### platform-status.ps1

**Purpose**: Check overall platform health (Windows)

**Usage**:
```powershell
.\platform-status.ps1
```

**What it shows**:
- Server status
- Database connectivity
- Redis connectivity
- API endpoints health
- Resource usage

---

### status-check.ps1

**Purpose**: Quick health check (Windows)

**Usage**:
```powershell
.\status-check.ps1
```

**What it checks**:
- Backend server
- Frontend server
- Database
- Essential services

---

### monitor-agents.sh

**Purpose**: Monitor AI agent system (Linux/Mac)

**Usage**:
```bash
chmod +x monitor-agents.sh
./monitor-agents.sh
```

**What it monitors**:
- Agent orchestrator status
- Active agents
- Queue lengths
- Processing times
- Error rates

---

## 🔧 Maintenance Scripts

### backup-restore.sh

**Purpose**: Backup and restore database

**Usage**:
```bash
# Backup
./backup-restore.sh backup

# Restore
./backup-restore.sh restore backup-20251114.sql
```

**What it does**:
- Creates timestamped backups
- Compresses backup files
- Stores in backup directory
- Supports restore from backup

---

### security-audit.sh

**Purpose**: Run security checks

**Usage**:
```bash
chmod +x security-audit.sh
./security-audit.sh
```

**What it checks**:
- File permissions
- Environment variables
- Open ports
- Dependency vulnerabilities
- SSL certificates

---

### optimize-performance.sh

**Purpose**: Optimize system performance

**Usage**:
```bash
chmod +x optimize-performance.sh
./optimize-performance.sh
```

**What it does**:
- Clears caches
- Optimizes databases
- Removes old logs
- Restarts services
- Updates indexes

---

## 🧪 Testing Scripts

### test-api-endpoints.py

**Purpose**: Test all API endpoints

**Usage**:
```bash
python test-api-endpoints.py
```

**What it tests**:
- All API endpoints
- Response codes
- Response times
- Data validation
- Error handling

**Output**: Generates test report

---

### test-integration.py

**Purpose**: Integration testing

**Usage**:
```bash
python test-integration.py
```

**What it tests**:
- End-to-end workflows
- Service integration
- Database operations
- External API calls

---

### performance-test.py

**Purpose**: Performance benchmarking

**Usage**:
```bash
python performance-test.py
```

**What it tests**:
- API response times
- Concurrent user handling
- Database query performance
- Memory usage
- CPU utilization

---

## 📖 Usage Guidelines

### Before Running Scripts

1. **Read the script**: Understand what it does
2. **Check requirements**: Ensure dependencies are met
3. **Backup data**: For destructive operations
4. **Test first**: Run in development before production

### Best Practices

1. **Use version control**: Track script changes
2. **Log output**: Save logs for debugging
3. **Error handling**: Check exit codes
4. **Documentation**: Update this README when adding scripts

### Script Template

```bash
#!/bin/bash
# ============================================================================
# Script Name
# ============================================================================
# Description: What this script does
# Usage: ./script-name.sh [options]
# Requirements: List of requirements
# Author: Your name
# Date: YYYY-MM-DD

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/script-name.log"

# Logging function
log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

# Main function
main() {
    log_info "Starting script..."
    
    # Your code here
    
    log_info "Script completed successfully"
}

# Run main function
main "$@"
```

### Python Script Template

```python
#!/usr/bin/env python3
"""
Script Name
===========

Description: What this script does
Usage: python script_name.py [options]
Requirements: List of requirements
Author: Your name
Date: YYYY-MM-DD
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    logger.info("Starting script...")
    
    try:
        # Your code here
        
        logger.info("Script completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## 🔐 Security Considerations

### Sensitive Data

- **Never commit** secrets or credentials
- Use environment variables for secrets
- Encrypt sensitive configuration
- Use `.gitignore` for private files

### Script Permissions

```bash
# Make executable (owner only)
chmod 700 script.sh

# Make executable (all users)
chmod 755 script.sh

# Check permissions
ls -l script.sh
```

### Running as Root

```bash
# Avoid running as root when possible
# Use sudo only when necessary

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root privileges"
    exit 1
fi
```

---

## 📋 Script Inventory

### Deployment

| Script | Platform | Purpose |
|--------|----------|---------|
| `runpod-diagnose-and-fix.sh` | RunPod | Auto-deploy with diagnostics |
| `runpod-start-simple.sh` | RunPod | Start simplified server |
| `runpod-start-server.sh` | RunPod | Start full server |
| `runpod-stop-server.sh` | RunPod | Stop server |
| `deploy-production-full.sh` | Linux | Full production deployment |
| `deploy-local.ps1` | Windows | Local development setup |

### Database

| Script | Purpose |
|--------|---------|
| `setup_database.py` | Initialize database |
| `seed_database.py` | Populate with data |
| `optimize_database.py` | Performance optimization |
| `backup-restore.sh` | Backup/restore |

### Monitoring

| Script | Platform | Purpose |
|--------|----------|---------|
| `platform-status.ps1` | Windows | Platform health check |
| `status-check.ps1` | Windows | Quick health check |
| `monitor-agents.sh` | Linux | Monitor AI agents |
| `health-check.sh` | Linux | System health |

### Testing

| Script | Purpose |
|--------|---------|
| `test-api-endpoints.py` | Test APIs |
| `test-integration.py` | Integration tests |
| `performance-test.py` | Performance tests |
| `validate_system.py` | System validation |

---

## 🆘 Troubleshooting

### Script Won't Run

```bash
# Make executable
chmod +x script.sh

# Check shebang
head -1 script.sh

# Should be: #!/bin/bash or #!/usr/bin/env python3
```

### Permission Denied

```bash
# Check permissions
ls -l script.sh

# Make executable
chmod +x script.sh

# Or run with interpreter
bash script.sh
python script.py
```

### Script Fails

```bash
# Run with debugging
bash -x script.sh

# Check logs
tail -f /var/log/script.log

# Verify environment
env | grep -i script
```

---

## 📚 Additional Resources

- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [Python Documentation](https://docs.python.org/)
- [Main Project README](../README.md)
- [Deployment Guide](../RUNPOD_DEPLOYMENT_README.md)

---

## 🤝 Contributing

### Adding New Scripts

1. Create script following template
2. Test thoroughly
3. Document in this README
4. Add usage examples
5. Update inventory table

### Script Guidelines

- Use descriptive names
- Include usage help
- Add error handling
- Log important actions
- Test before committing

---

**Built with ❤️ by the Galion Studio team**

**Last Updated**: November 14, 2025
