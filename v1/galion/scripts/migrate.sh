#!/bin/bash
# Database migration script
# Runs Alembic migrations for both GALION.APP and GALION.STUDIO
# Usage: ./scripts/migrate.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Database Migration                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if containers are running
if ! docker compose ps postgres | grep -q "running"; then
    echo -e "${RED}Error: PostgreSQL container is not running${NC}"
    echo "Start services with: docker compose up -d postgres"
    exit 1
fi

# Backup before migration
echo -e "${YELLOW}Creating backup before migration...${NC}"
./scripts/backup.sh
echo ""

# Run migrations for GALION.APP
echo -e "${YELLOW}Running migrations for GALION.APP...${NC}"
if docker compose ps app-api | grep -q "running"; then
    docker compose exec -T app-api alembic upgrade head
    echo -e "${GREEN}✓ GALION.APP migrations complete${NC}"
else
    echo -e "${RED}Warning: app-api container not running, skipping${NC}"
fi
echo ""

# Run migrations for GALION.STUDIO
echo -e "${YELLOW}Running migrations for GALION.STUDIO...${NC}"
if docker compose ps studio-api | grep -q "running"; then
    docker compose exec -T studio-api alembic upgrade head
    echo -e "${GREEN}✓ GALION.STUDIO migrations complete${NC}"
else
    echo -e "${RED}Warning: studio-api container not running, skipping${NC}"
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Migration Complete!                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Log migration
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Database migration completed" >> logs/migration.log

exit 0

