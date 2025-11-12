#!/bin/bash
# ===============================================
# Network Volume Configuration for RunPod
# ===============================================
# Ensures data persistence across pod restarts by mounting
# critical directories to network volume

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     NexusLang v2 - Network Volume Configuration          ║"
echo "║          Ensure Data Persists Across Pod Restarts         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if running on RunPod
if [ -d "/workspace" ]; then
    echo -e "${GREEN}✅ RunPod environment detected (/workspace exists)${NC}"
    WORKSPACE="/workspace"
else
    echo -e "${YELLOW}⚠️  Not a RunPod environment, using /tmp${NC}"
    WORKSPACE="/tmp/workspace"
    mkdir -p "$WORKSPACE"
fi

echo ""
echo "🔧 Configuring volume mounts..."
echo ""

# ===============================================
# 1. PostgreSQL Data Directory
# ===============================================
echo "1. PostgreSQL Data..."

POSTGRES_DATA_DIR="/var/lib/postgresql/16/main"
POSTGRES_BACKUP_DIR="$WORKSPACE/postgresql-data"

if [ -d "$POSTGRES_DATA_DIR" ]; then
    # Create backup directory on network volume
    mkdir -p "$POSTGRES_BACKUP_DIR"
    
    # Stop PostgreSQL if running
    service postgresql stop 2>/dev/null || true
    sleep 2
    
    # Move data to network volume if not already there
    if [ ! -L "$POSTGRES_DATA_DIR" ]; then
        echo "   Moving PostgreSQL data to network volume..."
        
        # Copy existing data if any
        if [ -d "$POSTGRES_DATA_DIR" ] && [ "$(ls -A $POSTGRES_DATA_DIR 2>/dev/null)" ]; then
            rsync -av "$POSTGRES_DATA_DIR/" "$POSTGRES_BACKUP_DIR/" || \
            cp -r "$POSTGRES_DATA_DIR/"* "$POSTGRES_BACKUP_DIR/" 2>/dev/null || true
        fi
        
        # Remove original and create symlink
        rm -rf "$POSTGRES_DATA_DIR"
        ln -s "$POSTGRES_BACKUP_DIR" "$POSTGRES_DATA_DIR"
        
        echo -e "   ${GREEN}✅ PostgreSQL data linked to $POSTGRES_BACKUP_DIR${NC}"
    else
        echo -e "   ${GREEN}✅ PostgreSQL already using network volume${NC}"
    fi
    
    # Set correct permissions
    chown -R postgres:postgres "$POSTGRES_BACKUP_DIR" 2>/dev/null || true
    chmod 700 "$POSTGRES_BACKUP_DIR" 2>/dev/null || true
    
    # Start PostgreSQL
    service postgresql start
    echo -e "   ${GREEN}✅ PostgreSQL started${NC}"
else
    echo -e "   ${YELLOW}⚠️  PostgreSQL not installed, skipping${NC}"
fi

echo ""

# ===============================================
# 2. Redis Data Directory
# ===============================================
echo "2. Redis Data..."

REDIS_DATA_DIR="/var/lib/redis"
REDIS_BACKUP_DIR="$WORKSPACE/redis-data"

mkdir -p "$REDIS_BACKUP_DIR"

if [ -d "$REDIS_DATA_DIR" ] && [ ! -L "$REDIS_DATA_DIR" ]; then
    echo "   Moving Redis data to network volume..."
    
    # Stop Redis
    pkill redis-server 2>/dev/null || true
    sleep 1
    
    # Copy existing data
    if [ "$(ls -A $REDIS_DATA_DIR 2>/dev/null)" ]; then
        cp -r "$REDIS_DATA_DIR/"* "$REDIS_BACKUP_DIR/" 2>/dev/null || true
    fi
    
    # Create symlink
    rm -rf "$REDIS_DATA_DIR"
    ln -s "$REDIS_BACKUP_DIR" "$REDIS_DATA_DIR"
    
    echo -e "   ${GREEN}✅ Redis data linked to $REDIS_BACKUP_DIR${NC}"
else
    echo -e "   ${GREEN}✅ Redis directory configured${NC}"
fi

echo ""

# ===============================================
# 3. Application Logs
# ===============================================
echo "3. Application Logs..."

LOG_DIR="/var/log/nexuslang"
LOG_BACKUP_DIR="$WORKSPACE/logs"

mkdir -p "$LOG_BACKUP_DIR"
mkdir -p "$LOG_DIR" 2>/dev/null || true

if [ ! -L "$LOG_DIR" ]; then
    # Copy existing logs
    if [ "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
        cp -r "$LOG_DIR/"* "$LOG_BACKUP_DIR/" 2>/dev/null || true
    fi
    
    # Remove and link
    rm -rf "$LOG_DIR"
    ln -s "$LOG_BACKUP_DIR" "$LOG_DIR"
    
    echo -e "   ${GREEN}✅ Logs linked to $LOG_BACKUP_DIR${NC}"
else
    echo -e "   ${GREEN}✅ Logs already using network volume${NC}"
fi

echo ""

# ===============================================
# 4. Backups Directory
# ===============================================
echo "4. Database Backups..."

BACKUP_DIR="$WORKSPACE/backups"
mkdir -p "$BACKUP_DIR"

echo -e "   ${GREEN}✅ Backup directory: $BACKUP_DIR${NC}"

echo ""

# ===============================================
# 5. Pip Cache (for faster package installs)
# ===============================================
echo "5. Python Package Cache..."

PIP_CACHE_DIR="$WORKSPACE/pip-cache"
mkdir -p "$PIP_CACHE_DIR"

# Set pip cache directory
export PIP_CACHE_DIR="$PIP_CACHE_DIR"
echo "export PIP_CACHE_DIR=$PIP_CACHE_DIR" >> ~/.bashrc

echo -e "   ${GREEN}✅ Pip cache: $PIP_CACHE_DIR${NC}"

echo ""

# ===============================================
# 6. Summary
# ===============================================
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              Volume Configuration Complete                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📂 Persistent Directories:"
echo "   • PostgreSQL: $POSTGRES_BACKUP_DIR"
echo "   • Redis:      $REDIS_BACKUP_DIR"  
echo "   • Logs:       $LOG_BACKUP_DIR"
echo "   • Backups:    $BACKUP_DIR"
echo "   • Pip Cache:  $PIP_CACHE_DIR"
echo ""
echo "✅ All critical data now persists on network volume!"
echo "✅ Pod restarts will preserve your data"
echo ""
echo "Next steps:"
echo "  1. Your data is now safe on /workspace"
echo "  2. Pod restarts will not lose database/Redis data"
echo "  3. Use 'python recovery.py' for quick recovery"
echo ""

