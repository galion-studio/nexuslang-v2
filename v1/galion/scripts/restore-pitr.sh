#!/bin/bash
# Point-in-Time Recovery (PITR) script
# Restores database to specific timestamp
# Usage: ./scripts/restore-pitr.sh "YYYY-MM-DD HH:MM:SS"

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TARGET_TIME="$1"

if [ -z "$TARGET_TIME" ]; then
    echo -e "${RED}Error: No target time specified${NC}"
    echo "Usage: $0 'YYYY-MM-DD HH:MM:SS'"
    echo ""
    echo "Example: $0 '2025-11-10 14:30:00'"
    echo ""
    echo "Available base backups:"
    ls -lht backups/base/ 2>/dev/null | head -5 || echo "  No base backups found"
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Point-in-Time Recovery (PITR)                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${RED}WARNING: This will REPLACE all current database data!${NC}"
echo ""
echo "Target time: $TARGET_TIME"
echo ""
read -p "Type 'yes' to continue: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

BACKUP_DIR="/home/deploy/galion/backups"
WAL_ARCHIVE_DIR="$BACKUP_DIR/wal_archive"
RESTORE_DIR="/tmp/galion_pitr_restore_$$"
POSTGRES_CONTAINER="galion-postgres"

# Find latest base backup
LATEST_BASE=$(ls -t "$BACKUP_DIR"/base/base_*/base.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BASE" ]; then
    echo -e "${RED}Error: No base backup found${NC}"
    echo "Create one with: ./scripts/incremental-backup.sh backup"
    exit 1
fi

echo ""
echo -e "${YELLOW}[1/7] Using base backup: $(basename $(dirname $LATEST_BASE))${NC}"

# Create restore directory
mkdir -p "$RESTORE_DIR"

echo -e "${YELLOW}[2/7] Extracting base backup...${NC}"
tar -xzf "$LATEST_BASE" -C "$RESTORE_DIR"
echo -e "${GREEN}✓ Base backup extracted${NC}"

# Create recovery.conf for PITR
echo -e "${YELLOW}[3/7] Creating recovery configuration...${NC}"
cat > "$RESTORE_DIR/recovery.signal" <<EOF
restore_command = 'cp $WAL_ARCHIVE_DIR/%f %p'
recovery_target_time = '$TARGET_TIME'
recovery_target_action = 'promote'
EOF

cat > "$RESTORE_DIR/postgresql.auto.conf" <<EOF
restore_command = 'cp $WAL_ARCHIVE_DIR/%f %p'
recovery_target_time = '$TARGET_TIME'
EOF

echo -e "${GREEN}✓ Recovery configuration created${NC}"

# Stop all services that depend on database
echo -e "${YELLOW}[4/7] Stopping services...${NC}"
docker compose stop app-api studio-api app-voice studio-realtime app-frontend studio-frontend
echo -e "${GREEN}✓ Services stopped${NC}"

# Stop PostgreSQL
echo -e "${YELLOW}[5/7] Stopping PostgreSQL...${NC}"
docker compose stop postgres
sleep 5
echo -e "${GREEN}✓ PostgreSQL stopped${NC}"

# Backup current data (just in case)
echo -e "${YELLOW}Creating safety backup of current data...${NC}"
SAFETY_BACKUP="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S)"
sudo cp -r data/postgres "$SAFETY_BACKUP"
echo -e "${GREEN}✓ Safety backup created: $SAFETY_BACKUP${NC}"

# Replace data directory
echo -e "${YELLOW}[6/7] Restoring data directory...${NC}"
sudo rm -rf data/postgres/pgdata/*
sudo cp -r "$RESTORE_DIR"/* data/postgres/pgdata/
sudo chown -R 70:70 data/postgres/pgdata  # postgres user in container
echo -e "${GREEN}✓ Data directory restored${NC}"

# Start PostgreSQL (will perform PITR)
echo -e "${YELLOW}[7/7] Starting PostgreSQL and performing recovery...${NC}"
echo "This may take several minutes depending on WAL file count..."
docker compose up -d postgres

# Wait for recovery to complete
sleep 10

# Check if PostgreSQL is ready
MAX_WAIT=300  # 5 minutes
WAIT_COUNT=0
while ! docker compose exec -T postgres pg_isready -U galion >/dev/null 2>&1; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}✗ Recovery timed out${NC}"
        echo "Check logs: docker compose logs postgres"
        exit 1
    fi
    echo -n "."
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done

echo ""
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Restart all services
echo -e "${YELLOW}Restarting all services...${NC}"
docker compose up -d
echo -e "${GREEN}✓ All services restarted${NC}"
echo ""

# Cleanup
rm -rf "$RESTORE_DIR"

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Recovery Complete!                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Database restored to: $TARGET_TIME"
echo "Safety backup location: $SAFETY_BACKUP"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "  1. Verify data integrity:"
echo "     docker compose exec postgres psql -U galion -d galion"
echo ""
echo "  2. Test application functionality"
echo ""
echo "  3. If everything is OK, delete safety backup:"
echo "     sudo rm -rf $SAFETY_BACKUP"
echo ""
echo "  4. If something is wrong, you can restore from safety backup"
echo ""

exit 0

