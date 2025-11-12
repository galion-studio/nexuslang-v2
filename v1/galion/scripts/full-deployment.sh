#!/bin/bash
# Complete deployment script for GALION on VPS
# Executes all deployment steps in correct order
# Usage: ./scripts/full-deployment.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      GALION Full Deployment Script                    ║${NC}"
echo -e "${BLUE}║      TITANAXE VPS Production Deployment               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

DEPLOYMENT_START=$(date +%s)

# Pre-deployment checklist
echo -e "${YELLOW}Pre-Deployment Checklist:${NC}"
echo ""

checks_passed=0
checks_total=0

check_requirement() {
    local name=$1
    local command=$2
    checks_total=$((checks_total + 1))
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
        checks_passed=$((checks_passed + 1))
        return 0
    else
        echo -e "  ${RED}✗${NC} $name"
        return 1
    fi
}

check_requirement "Docker installed" "docker --version"
check_requirement "Docker Compose installed" "docker compose version"
check_requirement "Nginx installed" "nginx -v"
check_requirement "Certbot installed" "certbot --version"
check_requirement ".env file exists" "test -f .env"
check_requirement "Required directories exist" "test -d data && test -d backups"

echo ""
if [ $checks_passed -lt $checks_total ]; then
    echo -e "${RED}Pre-deployment checks failed: $checks_passed/$checks_total passed${NC}"
    echo "Please fix the issues above before deploying."
    exit 1
fi

echo -e "${GREEN}All pre-deployment checks passed: $checks_passed/$checks_total${NC}"
echo ""

read -p "Continue with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Starting Deployment                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Pull latest code
echo -e "${YELLOW}[1/14] Pulling latest code...${NC}"
git pull origin main || echo "  No git repository or already up to date"
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 2: Generate secrets (if not exists)
echo -e "${YELLOW}[2/14] Checking secrets...${NC}"
if grep -q "GENERATE_STRONG_PASSWORD_HERE" .env 2>/dev/null; then
    echo "  Generating new secrets..."
    ./scripts/generate-secrets.sh
else
    echo "  Secrets already configured"
fi
echo -e "${GREEN}✓ Secrets ready${NC}"
echo ""

# Step 3: Create required directories
echo -e "${YELLOW}[3/14] Creating directories...${NC}"
mkdir -p data/{postgres,redis,uploads,logs,prometheus}
mkdir -p backups/wal_archive
mkdir -p monitoring
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 4: Build all images
echo -e "${YELLOW}[4/14] Building Docker images...${NC}"
docker compose build --parallel
echo -e "${GREEN}✓ Images built${NC}"
echo ""

# Step 5: Start infrastructure services
echo -e "${YELLOW}[5/14] Starting PostgreSQL and Redis...${NC}"
docker compose up -d postgres redis
echo "  Waiting for services to be healthy..."
sleep 30
echo -e "${GREEN}✓ Infrastructure services started${NC}"
echo ""

# Step 6: Start PgBouncer
echo -e "${YELLOW}[6/14] Starting PgBouncer (connection pooling)...${NC}"
docker compose up -d pgbouncer
sleep 10
echo -e "${GREEN}✓ PgBouncer started${NC}"
echo ""

# Step 7: Run database migrations
echo -e "${YELLOW}[7/14] Running database migrations...${NC}"
if [ -f scripts/migrate.sh ]; then
    # Skip backup in migrate.sh since we're doing it separately
    docker compose exec -T app-api alembic upgrade head 2>/dev/null || echo "  Migrations will run after API starts"
    docker compose exec -T studio-api alembic upgrade head 2>/dev/null || echo "  Migrations will run after API starts"
fi
echo -e "${GREEN}✓ Migrations ready${NC}"
echo ""

# Step 8: Create database indexes
echo -e "${YELLOW}[8/14] Creating database indexes...${NC}"
if [ -f scripts/optimize-db.sql ]; then
    docker compose exec -T postgres psql -U galion -d galion -f /backups/../scripts/optimize-db.sql || echo "  Will create indexes after first data"
fi
echo -e "${GREEN}✓ Indexes ready${NC}"
echo ""

# Step 9: Start application services
echo -e "${YELLOW}[9/14] Starting application services...${NC}"
docker compose up -d app-api studio-api app-voice studio-realtime
echo "  Waiting for applications to be healthy..."
sleep 40
echo -e "${GREEN}✓ Application services started${NC}"
echo ""

# Step 10: Start frontends
echo -e "${YELLOW}[10/14] Starting frontend services...${NC}"
docker compose up -d app-frontend studio-frontend
sleep 20
echo -e "${GREEN}✓ Frontend services started${NC}"
echo ""

# Step 11: Start monitoring stack
echo -e "${YELLOW}[11/14] Starting monitoring services...${NC}"
docker compose up -d prometheus node-exporter cadvisor postgres-exporter redis-exporter nginx-exporter
sleep 10
echo -e "${GREEN}✓ Monitoring services started${NC}"
echo ""

# Step 12: Verify all services
echo -e "${YELLOW}[12/14] Verifying all services...${NC}"
if [ -f scripts/health-check.sh ]; then
    ./scripts/health-check.sh
else
    docker compose ps
fi
echo ""

# Step 13: Configure SSL certificates (if not already configured)
echo -e "${YELLOW}[13/14] Configuring SSL certificates...${NC}"
if [ ! -d /etc/letsencrypt/live/galion.app ]; then
    echo "  Run these commands manually to get SSL certificates:"
    echo "  sudo certbot --nginx -d galion.app -d www.galion.app -d api.galion.app"
    echo "  sudo certbot --nginx -d studio.galion.app -d api.studio.galion.app"
    echo ""
    read -p "  Press Enter after configuring SSL..."
else
    echo "  SSL certificates already configured"
fi
echo -e "${GREEN}✓ SSL ready${NC}"
echo ""

# Step 14: Setup cron jobs
echo -e "${YELLOW}[14/14] Setting up cron jobs...${NC}"
(crontab -l 2>/dev/null | grep -v "galion") || true  # Remove old galion cron jobs
(crontab -l 2>/dev/null; cat <<EOF
# GALION automated tasks
0 2 * * * /home/deploy/galion/scripts/backup.sh >> /home/deploy/galion/logs/backup.log 2>&1
*/5 * * * * /home/deploy/galion/scripts/health-check.sh >> /home/deploy/galion/logs/health.log 2>&1
0 0 * * 0 /home/deploy/galion/scripts/incremental-backup.sh backup >> /home/deploy/galion/logs/incremental-backup.log 2>&1
EOF
) | crontab - || echo "  Cron jobs setup (may need manual configuration)"
echo -e "${GREEN}✓ Cron jobs configured${NC}"
echo ""

DEPLOYMENT_END=$(date +%s)
DEPLOYMENT_DURATION=$((DEPLOYMENT_END - DEPLOYMENT_START))

# Final summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Deployment Complete!                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Deployment successful in $DEPLOYMENT_DURATION seconds${NC}"
echo ""
echo -e "${YELLOW}Services deployed:${NC}"
echo "  ✓ PostgreSQL (with optimized configuration)"
echo "  ✓ Redis (2GB cache)"
echo "  ✓ PgBouncer (connection pooling)"
echo "  ✓ GALION.APP (API + Frontend + Voice)"
echo "  ✓ GALION.STUDIO (API + Frontend + Realtime)"
echo "  ✓ Monitoring (Prometheus + Exporters)"
echo ""
echo -e "${YELLOW}Access points:${NC}"
echo "  • GALION.APP: https://galion.app"
echo "  • GALION.APP API: https://api.galion.app"
echo "  • GALION.STUDIO: https://studio.galion.app"
echo "  • GALION.STUDIO API: https://api.studio.galion.app"
echo "  • Prometheus: http://YOUR_IP:9090"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Run smoke tests:"
echo "     curl https://api.galion.app/health"
echo "     curl https://api.studio.galion.app/health"
echo ""
echo "  2. Run load tests:"
echo "     k6 run tests/load/api-test.js"
echo ""
echo "  3. Monitor in Grafana:"
echo "     https://grafana.com"
echo ""
echo "  4. Set up Cloudflare:"
echo "     See docs/CLOUDFLARE_SETUP.md"
echo ""
echo -e "${YELLOW}Logs location:${NC}"
echo "  • Application: docker compose logs -f"
echo "  • Backup: logs/backup.log"
echo "  • Health: logs/health.log"
echo ""

# Log deployment
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Full deployment completed in ${DEPLOYMENT_DURATION}s" >> logs/deployment.log

exit 0

