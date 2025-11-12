#!/bin/bash
# Automated backup script for GALION databases
# Usage: ./scripts/backup.sh
# Cron: 0 2 * * * /home/deploy/galion/scripts/backup.sh >> /home/deploy/galion/logs/backup.log 2>&1

set -e

# Configuration
BACKUP_DIR="/home/deploy/galion/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y%m%d)
POSTGRES_CONTAINER="galion-postgres"
POSTGRES_USER="galion"
RETENTION_DAYS=30

# Backblaze B2 (optional - set in .env)
B2_BUCKET="${B2_BUCKET_NAME:-}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      GALION Backup Script                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Starting backup: $(date)"
echo ""

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if PostgreSQL container is running
if ! docker ps | grep -q "$POSTGRES_CONTAINER"; then
    echo -e "${RED}Error: PostgreSQL container is not running${NC}"
    exit 1
fi

# Backup GALION.APP database
echo -e "${YELLOW}[1/4] Backing up galion database...${NC}"
docker exec "$POSTGRES_CONTAINER" pg_dump -U "$POSTGRES_USER" -Fc galion > "$BACKUP_DIR/galion_${DATE}.dump"
if [ $? -eq 0 ]; then
    GALION_SIZE=$(du -h "$BACKUP_DIR/galion_${DATE}.dump" | cut -f1)
    echo -e "${GREEN}✓ galion backup complete ($GALION_SIZE)${NC}"
else
    echo -e "${RED}✗ galion backup failed${NC}"
    exit 1
fi

# Backup GALION.STUDIO database
echo -e "${YELLOW}[2/4] Backing up galion_studio database...${NC}"
docker exec "$POSTGRES_CONTAINER" pg_dump -U "$POSTGRES_USER" -Fc galion_studio > "$BACKUP_DIR/galion_studio_${DATE}.dump"
if [ $? -eq 0 ]; then
    STUDIO_SIZE=$(du -h "$BACKUP_DIR/galion_studio_${DATE}.dump" | cut -f1)
    echo -e "${GREEN}✓ galion_studio backup complete ($STUDIO_SIZE)${NC}"
else
    echo -e "${RED}✗ galion_studio backup failed${NC}"
    exit 1
fi

# Compress backups
echo -e "${YELLOW}[3/4] Compressing backups...${NC}"
gzip -f "$BACKUP_DIR/galion_${DATE}.dump"
gzip -f "$BACKUP_DIR/galion_studio_${DATE}.dump"
echo -e "${GREEN}✓ Compression complete${NC}"

# Upload to Backblaze B2 (if configured)
if [ -n "$B2_BUCKET" ] && command -v b2 >/dev/null 2>&1; then
    echo -e "${YELLOW}[4/4] Uploading to Backblaze B2...${NC}"
    
    # Upload galion backup
    if b2 upload-file "$B2_BUCKET" "$BACKUP_DIR/galion_${DATE}.dump.gz" "backups/galion_${DATE}.dump.gz" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ galion backup uploaded to B2${NC}"
    else
        echo -e "${RED}✗ Failed to upload galion backup to B2${NC}"
    fi
    
    # Upload studio backup
    if b2 upload-file "$B2_BUCKET" "$BACKUP_DIR/galion_studio_${DATE}.dump.gz" "backups/galion_studio_${DATE}.dump.gz" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ galion_studio backup uploaded to B2${NC}"
    else
        echo -e "${RED}✗ Failed to upload galion_studio backup to B2${NC}"
    fi
else
    echo -e "${YELLOW}[4/4] Skipping B2 upload (not configured)${NC}"
fi

# Clean up old backups (keep last 30 days)
echo ""
echo -e "${YELLOW}Cleaning up old backups (keeping last ${RETENTION_DAYS} days)...${NC}"
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete
OLD_COUNT=$(find "$BACKUP_DIR" -name "*.dump.gz" | wc -l)
echo -e "${GREEN}✓ Cleanup complete (${OLD_COUNT} backups retained)${NC}"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Backup Complete!                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Backup files:"
echo "  - galion_${DATE}.dump.gz ($GALION_SIZE compressed)"
echo "  - galion_studio_${DATE}.dump.gz ($STUDIO_SIZE compressed)"
echo ""
echo "Location: $BACKUP_DIR"
echo "Completed: $(date)"
echo ""

# Log to file
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Backup completed successfully" >> "$BACKUP_DIR/backup.log"

exit 0

