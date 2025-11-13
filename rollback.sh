#!/bin/bash
#
# Rollback Script for Galion Ecosystem
# Reverts to previous version if deployment fails
#
# Usage: ./rollback.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

COMPOSE_FILE="docker-compose.production.yml"

echo -e "${YELLOW}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          Galion Ecosystem Rollback Script              ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}⚠️  This will rollback to the previous deployment${NC}"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback canceled"
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Stopping current deployment...${NC}"
docker-compose -f $COMPOSE_FILE down
echo ""

echo -e "${GREEN}Step 2: Reverting code to previous commit...${NC}"
git reset --hard HEAD~1
echo ""

echo -e "${GREEN}Step 3: Rebuilding and restarting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d --build
echo ""

echo -e "${GREEN}Step 4: Verifying rollback...${NC}"
sleep 15

./health-check.sh

echo ""
echo -e "${GREEN}✅ Rollback complete!${NC}"
echo ""

