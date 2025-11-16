#!/bin/bash
# ============================================
# GALION BACKUP SCRIPT
# ============================================
# Create backups of database, code, and configuration

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="galion_backup_${DATE}"

echo "💾 Creating Galion backup: ${BACKUP_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Function to print status
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Create backup archive
print_status "Creating code and configuration backup..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='backups' \
    --exclude='.env' \
    .

# Backup database if running in Docker
if docker ps | grep -q galion-postgres; then
    print_status "Backing up PostgreSQL database..."
    docker exec galion-postgres pg_dump -U galion galion > "${BACKUP_DIR}/${BACKUP_NAME}.sql"
fi

# Backup Redis data if running
if docker ps | grep -q galion-redis; then
    print_status "Backing up Redis data..."
    docker exec galion-redis redis-cli SAVE
    docker cp galion-redis:/data/dump.rdb "${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb"
fi

# Calculate backup size
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
print_success "Backup created: ${BACKUP_SIZE}"

# Clean old backups (keep last 7)
print_status "Cleaning old backups..."
cd "${BACKUP_DIR}"
ls -t *.tar.gz | tail -n +8 | xargs -r rm -f
ls -t *.sql | tail -n +8 | xargs -r rm -f
ls -t *_redis.rdb | tail -n +8 | xargs -r rm -f

# List current backups
echo ""
echo "📦 Current backups in ${BACKUP_DIR}:"
ls -lh "${BACKUP_DIR}" | grep -E "\.(tar\.gz|sql|rdb)$"

echo ""
print_success "Backup completed successfully!"
echo "📁 Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📅 Date: $(date)"

