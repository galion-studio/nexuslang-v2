#!/bin/bash
# Health check script for all GALION services
# Usage: ./scripts/health-check.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      GALION Health Check                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Time: $(date)"
echo ""

# Check Docker
echo -e "${YELLOW}=== Docker Status ===${NC}"
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi
echo ""

# Check containers
echo -e "${YELLOW}=== Container Status ===${NC}"
docker compose ps
echo ""

# Check services health
echo -e "${YELLOW}=== Service Health ===${NC}"

check_service() {
    local name=$1
    local url=$2
    
    if curl -f -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $name${NC}"
        return 0
    else
        echo -e "${RED}✗ $name${NC}"
        return 1
    fi
}

check_service "GALION.APP API     " "http://localhost:8001/health"
check_service "GALION.APP Frontend" "http://localhost:3001"
check_service "GALION.APP Voice   " "http://localhost:8002/health"
check_service "GALION.STUDIO API  " "http://localhost:8003/health"
check_service "GALION.STUDIO Frontend" "http://localhost:3003"
check_service "GALION.STUDIO Realtime" "http://localhost:8004/health"

echo ""

# Check database
echo -e "${YELLOW}=== Database ===${NC}"
if docker compose exec -T postgres pg_isready -U galion >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
    
    # Get database sizes
    GALION_SIZE=$(docker compose exec -T postgres psql -U galion -d galion -t -c "SELECT pg_size_pretty(pg_database_size('galion'));" 2>/dev/null | xargs)
    STUDIO_SIZE=$(docker compose exec -T postgres psql -U galion -d galion_studio -t -c "SELECT pg_size_pretty(pg_database_size('galion_studio'));" 2>/dev/null | xargs)
    
    echo "  galion database: $GALION_SIZE"
    echo "  galion_studio database: $STUDIO_SIZE"
else
    echo -e "${RED}✗ PostgreSQL is not ready${NC}"
fi
echo ""

# Check Redis
echo -e "${YELLOW}=== Redis ===${NC}"
if docker compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is responding${NC}"
    
    # Get Redis info
    REDIS_MEM=$(docker compose exec -T redis redis-cli info memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
    REDIS_KEYS=$(docker compose exec -T redis redis-cli dbsize 2>/dev/null | tr -d '\r')
    
    echo "  Memory used: $REDIS_MEM"
    echo "  Keys: $REDIS_KEYS"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi
echo ""

# Check disk space
echo -e "${YELLOW}=== Disk Space ===${NC}"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')

if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓ Disk space OK${NC}"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠ Disk space warning${NC}"
else
    echo -e "${RED}✗ Disk space critical${NC}"
fi
echo "  Used: ${DISK_USAGE}%"
echo "  Available: $DISK_AVAIL"
echo ""

# Check memory
echo -e "${YELLOW}=== Memory ===${NC}"
MEM_TOTAL=$(free -h | awk 'NR==2 {print $2}')
MEM_USED=$(free -h | awk 'NR==2 {print $3}')
MEM_AVAIL=$(free -h | awk 'NR==2 {print $7}')
MEM_PERCENT=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')

if [ "$MEM_PERCENT" -lt 80 ]; then
    echo -e "${GREEN}✓ Memory OK${NC}"
elif [ "$MEM_PERCENT" -lt 90 ]; then
    echo -e "${YELLOW}⚠ Memory warning${NC}"
else
    echo -e "${RED}✗ Memory critical${NC}"
fi
echo "  Total: $MEM_TOTAL"
echo "  Used: $MEM_USED ($MEM_PERCENT%)"
echo "  Available: $MEM_AVAIL"
echo ""

# Check Docker resource usage
echo -e "${YELLOW}=== Container Resources ===${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep galion
echo ""

# Check last backup
echo -e "${YELLOW}=== Backups ===${NC}"
if [ -d "backups" ]; then
    LAST_BACKUP=$(ls -t backups/*.dump.gz 2>/dev/null | head -1)
    if [ -n "$LAST_BACKUP" ]; then
        BACKUP_AGE=$(( ($(date +%s) - $(stat -c %Y "$LAST_BACKUP")) / 86400 ))
        BACKUP_SIZE=$(du -h "$LAST_BACKUP" | cut -f1)
        
        if [ "$BACKUP_AGE" -eq 0 ]; then
            echo -e "${GREEN}✓ Backup today${NC}"
        elif [ "$BACKUP_AGE" -eq 1 ]; then
            echo -e "${GREEN}✓ Backup yesterday${NC}"
        elif [ "$BACKUP_AGE" -lt 7 ]; then
            echo -e "${YELLOW}⚠ Last backup $BACKUP_AGE days ago${NC}"
        else
            echo -e "${RED}✗ Last backup $BACKUP_AGE days ago${NC}"
        fi
        
        echo "  File: $(basename $LAST_BACKUP)"
        echo "  Size: $BACKUP_SIZE"
    else
        echo -e "${RED}✗ No backups found${NC}"
    fi
else
    echo -e "${RED}✗ Backup directory not found${NC}"
fi
echo ""

# Check external URLs (if configured)
if command -v curl >/dev/null 2>&1; then
    echo -e "${YELLOW}=== External URLs ===${NC}"
    
    check_url() {
        local name=$1
        local url=$2
        
        HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" -m 5 "$url" 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
            echo -e "${GREEN}✓ $name ($HTTP_CODE)${NC}"
        elif [ "$HTTP_CODE" = "000" ]; then
            echo -e "${YELLOW}⚠ $name (timeout)${NC}"
        else
            echo -e "${RED}✗ $name ($HTTP_CODE)${NC}"
        fi
    }
    
    check_url "galion.app          " "https://galion.app"
    check_url "api.galion.app      " "https://api.galion.app/health"
    check_url "studio.galion.app   " "https://studio.galion.app"
    check_url "api.studio.galion.app" "https://api.studio.galion.app/health"
    echo ""
fi

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Health Check Complete                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

exit 0

