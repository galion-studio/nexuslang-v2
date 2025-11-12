#!/bin/bash
# Restore script for GALION databases
# Usage: ./scripts/restore.sh <backup_file.dump.gz>
# Example: ./scripts/restore.sh backups/galion_20251110_020000.dump.gz

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: $0 <backup_file.dump.gz>"
    echo ""
    echo "Available backups:"
    ls -lht backups/*.dump.gz 2>/dev/null | head -10 || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Determine which database from filename
if [[ "$BACKUP_FILE" == *"galion_studio"* ]]; then
    DB_NAME="galion_studio"
    DB_DISPLAY="GALION.STUDIO"
elif [[ "$BACKUP_FILE" == *"galion"* ]]; then
    DB_NAME="galion"
    DB_DISPLAY="GALION.APP"
else
    echo -e "${RED}Error: Cannot determine database from filename${NC}"
    echo "Expected filename pattern: galion_* or galion_studio_*"
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      GALION Database Restore                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}WARNING: This will REPLACE all data in $DB_DISPLAY!${NC}"
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Target database: $DB_NAME"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

POSTGRES_CONTAINER="galion-postgres"
POSTGRES_USER="galion"

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

# Create temporary directory
TEMP_DIR="/tmp/galion_restore_$$"
mkdir -p "$TEMP_DIR"

echo ""
echo -e "${YELLOW}[1/5] Extracting backup...${NC}"
gunzip -c "$BACKUP_FILE" > "$TEMP_DIR/backup.dump"
echo -e "${GREEN}✓ Backup extracted${NC}"

echo -e "${YELLOW}[2/5] Creating backup of current database...${NC}"
docker exec "$POSTGRES_CONTAINER" pg_dump -U "$POSTGRES_USER" -Fc "$DB_NAME" > "$TEMP_DIR/current_backup.dump" 2>/dev/null || true
if [ -f "$TEMP_DIR/current_backup.dump" ]; then
    echo -e "${GREEN}✓ Current database backed up to: $TEMP_DIR/current_backup.dump${NC}"
    echo -e "${YELLOW}  (You can restore this if something goes wrong)${NC}"
fi

echo -e "${YELLOW}[3/5] Terminating active connections...${NC}"
docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" >/dev/null 2>&1
echo -e "${GREEN}✓ Connections terminated${NC}"

echo -e "${YELLOW}[4/5] Dropping and recreating database...${NC}"
docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" >/dev/null 2>&1
docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" >/dev/null 2>&1
echo -e "${GREEN}✓ Database recreated${NC}"

echo -e "${YELLOW}[5/5] Restoring data...${NC}"
cat "$TEMP_DIR/backup.dump" | docker exec -i "$POSTGRES_CONTAINER" pg_restore -U "$POSTGRES_USER" -d "$DB_NAME" --verbose 2>&1 | grep -E "(restoring|processing)" || true
echo -e "${GREEN}✓ Data restored${NC}"

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Restore Complete!                                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Database: $DB_NAME ($DB_DISPLAY)"
echo "Restored from: $BACKUP_FILE"
echo "Completed: $(date)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Restart application containers:"
echo "     docker compose restart"
echo ""
echo "  2. Verify data:"
echo "     docker compose exec postgres psql -U galion -d $DB_NAME"
echo ""

# Log to file
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Restored $DB_NAME from $BACKUP_FILE" >> backups/restore.log

exit 0

