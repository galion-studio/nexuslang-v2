#!/bin/bash
# Automated Backup Script for RunPod
# Backs up database, code, and configurations

BACKUP_DIR="/workspace/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="galion_backup_${TIMESTAMP}"

echo "📦 Starting backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
sudo -u postgres pg_dump nexus_db > "$BACKUP_DIR/${BACKUP_NAME}_database.sql"

# Backup environment files
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" \
    /workspace/project-nexus/v2/backend/.env \
    /workspace/project-nexus/v2/frontend/.env.local \
    /workspace/project-nexus/galion-studio/.env.local \
    2>/dev/null || true

# Backup logs
echo "Backing up logs..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_logs.tar.gz" /workspace/logs/*.log 2>/dev/null || true

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "galion_backup_*" -mtime +7 -delete

echo "✅ Backup complete: $BACKUP_DIR/$BACKUP_NAME"
echo "Files created:"
ls -lh "$BACKUP_DIR/$BACKUP_NAME"*

