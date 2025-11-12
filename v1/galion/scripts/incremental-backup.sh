#!/bin/bash
# Incremental backup script with WAL archiving
# Enables point-in-time recovery (PITR)
# Usage: ./scripts/incremental-backup.sh setup|backup

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="/home/deploy/galion/backups"
WAL_ARCHIVE_DIR="$BACKUP_DIR/wal_archive"
BASE_BACKUP_DIR="$BACKUP_DIR/base"
POSTGRES_CONTAINER="galion-postgres"
POSTGRES_USER="galion"

# Create required directories
mkdir -p "$WAL_ARCHIVE_DIR"
mkdir -p "$BASE_BACKUP_DIR"

case "${1:-}" in
    setup)
        echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║      Setting Up Incremental Backups                    ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        echo -e "${YELLOW}Configuring PostgreSQL for WAL archiving...${NC}"
        
        # Configure WAL archiving
        docker compose exec -T postgres psql -U "$POSTGRES_USER" <<EOF
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'test ! -f /backups/wal_archive/%f && cp %p /backups/wal_archive/%f';
ALTER SYSTEM SET archive_timeout = 300;
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET max_replication_slots = 10;
SELECT pg_reload_conf();
EOF
        
        echo -e "${GREEN}✓ PostgreSQL configured for WAL archiving${NC}"
        echo ""
        echo -e "${YELLOW}Note: Restart PostgreSQL for changes to take full effect:${NC}"
        echo "  docker compose restart postgres"
        echo ""
        echo -e "${GREEN}Setup complete! Run './scripts/incremental-backup.sh backup' to create base backup.${NC}"
        ;;
        
    backup)
        echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║      Creating Base Backup                              ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        DATE=$(date +%Y%m%d_%H%M%S)
        BACKUP_NAME="base_${DATE}"
        
        echo -e "${YELLOW}Creating base backup: $BACKUP_NAME${NC}"
        
        # Create base backup using pg_basebackup
        docker compose exec -T postgres pg_basebackup \
            -U "$POSTGRES_USER" \
            -D "/backups/base/$BACKUP_NAME" \
            -Ft \
            -z \
            -P \
            -X stream
        
        if [ $? -eq 0 ]; then
            BACKUP_SIZE=$(du -sh "$BASE_BACKUP_DIR/$BACKUP_NAME" | cut -f1)
            echo -e "${GREEN}✓ Base backup created: $BACKUP_SIZE${NC}"
            echo ""
            echo "Location: $BASE_BACKUP_DIR/$BACKUP_NAME"
            echo ""
            echo -e "${YELLOW}WAL files are continuously archived to: $WAL_ARCHIVE_DIR${NC}"
            echo "This enables point-in-time recovery to any moment after this backup."
            echo ""
            
            # Log success
            echo "$(date +%Y-%m-%d\ %H:%M:%S) - Base backup created: $BACKUP_NAME" >> "$BACKUP_DIR/incremental.log"
        else
            echo -e "${RED}✗ Base backup failed${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo "Usage: $0 {setup|backup}"
        echo ""
        echo "Commands:"
        echo "  setup  - Configure PostgreSQL for incremental backups"
        echo "  backup - Create base backup (run after setup)"
        echo ""
        echo "Examples:"
        echo "  ./scripts/incremental-backup.sh setup"
        echo "  ./scripts/incremental-backup.sh backup"
        exit 1
        ;;
esac

exit 0

