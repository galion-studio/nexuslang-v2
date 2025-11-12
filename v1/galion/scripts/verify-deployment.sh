#!/bin/bash
# Post-deployment verification script
# Runs comprehensive tests to verify deployment success
# Usage: ./scripts/verify-deployment.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Post-Deployment Verification                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

total_tests=0
passed_tests=0

run_test() {
    local test_name=$1
    local test_command=$2
    total_tests=$((total_tests + 1))
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

# ==================== CONTAINER STATUS ====================
echo -e "${YELLOW}1. Container Status${NC}"
run_test "All containers running" "docker compose ps | grep -q 'Up'"
run_test "PostgreSQL healthy" "docker compose ps postgres | grep -q 'healthy'"
run_test "Redis healthy" "docker compose ps redis | grep -q 'healthy'"
run_test "PgBouncer running" "docker compose ps pgbouncer | grep -q 'Up'"
run_test "App API healthy" "docker compose ps app-api | grep -q 'healthy'"
run_test "Studio API healthy" "docker compose ps studio-api | grep -q 'healthy'"
echo ""

# ==================== HEALTH ENDPOINTS ====================
echo -e "${YELLOW}2. Health Endpoints${NC}"
run_test "App API health" "curl -f -s http://localhost:8001/health | grep -q 'healthy'"
run_test "App API ready" "curl -f -s http://localhost:8001/health/ready | grep -q 'ready'"
run_test "Studio API health" "curl -f -s http://localhost:8003/health | grep -q 'healthy'"
run_test "Studio API ready" "curl -f -s http://localhost:8003/health/ready | grep -q 'ready'"
run_test "Voice service health" "curl -f -s http://localhost:8002/health"
run_test "Realtime service health" "curl -f -s http://localhost:8004/health"
echo ""

# ==================== DATABASE CONNECTIVITY ====================
echo -e "${YELLOW}3. Database Connectivity${NC}"
run_test "PostgreSQL connection" "docker compose exec -T postgres pg_isready -U galion"
run_test "Database galion exists" "docker compose exec -T postgres psql -U galion -lqt | grep -q galion"
run_test "Database galion_studio exists" "docker compose exec -T postgres psql -U galion -lqt | grep -q galion_studio"
run_test "PgBouncer connection" "docker compose exec -T pgbouncer psql -h 127.0.0.1 -p 6432 -U galion -d pgbouncer -c 'SHOW POOLS'"
echo ""

# ==================== REDIS CONNECTIVITY ====================
echo -e "${YELLOW}4. Redis Connectivity${NC}"
run_test "Redis ping" "docker compose exec -T redis redis-cli ping"
run_test "Redis info" "docker compose exec -T redis redis-cli info server"
echo ""

# ==================== SYSTEM RESOURCES ====================
echo -e "${YELLOW}5. System Resources${NC}"

# Memory check
MEM_PERCENT=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
if [ "$MEM_PERCENT" -lt 90 ]; then
    echo -e "  ${GREEN}✓${NC} Memory usage: ${MEM_PERCENT}% (< 90%)"
    passed_tests=$((passed_tests + 1))
else
    echo -e "  ${RED}✗${NC} Memory usage: ${MEM_PERCENT}% (>= 90%)"
fi
total_tests=$((total_tests + 1))

# Disk check
DISK_PERCENT=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_PERCENT" -lt 80 ]; then
    echo -e "  ${GREEN}✓${NC} Disk usage: ${DISK_PERCENT}% (< 80%)"
    passed_tests=$((passed_tests + 1))
else
    echo -e "  ${RED}✗${NC} Disk usage: ${DISK_PERCENT}% (>= 80%)"
fi
total_tests=$((total_tests + 1))

# CPU load (simplified check)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
echo -e "  ${GREEN}✓${NC} Load average: $LOAD_AVG"
echo ""

# ==================== MONITORING ====================
echo -e "${YELLOW}6. Monitoring Services${NC}"
run_test "Prometheus running" "curl -f -s http://localhost:9090/-/healthy"
run_test "Node Exporter metrics" "curl -f -s http://localhost:9100/metrics | grep -q node_cpu"
run_test "Postgres Exporter metrics" "curl -f -s http://localhost:9187/metrics | grep -q pg_up"
run_test "Redis Exporter metrics" "curl -f -s http://localhost:9121/metrics | grep -q redis_up"
run_test "cAdvisor metrics" "curl -f -s http://localhost:8080/metrics | grep -q container_memory"
echo ""

# ==================== NGINX CONFIGURATION ====================
echo -e "${YELLOW}7. Nginx Configuration${NC}"
run_test "Nginx configuration valid" "sudo nginx -t"
run_test "Nginx status page" "curl -f -s http://localhost/nginx_status"
echo ""

# ==================== SSL CERTIFICATES ====================
echo -e "${YELLOW}8. SSL Certificates${NC}"
if [ -d /etc/letsencrypt/live/galion.app ]; then
    echo -e "  ${GREEN}✓${NC} SSL certificates found"
    passed_tests=$((passed_tests + 1))
    
    # Check expiry
    CERT_EXPIRY=$(sudo certbot certificates 2>/dev/null | grep "Expiry Date" | head -1 | awk '{print $3}')
    echo "    Expiry: $CERT_EXPIRY"
else
    echo -e "  ${YELLOW}⚠${NC} SSL certificates not configured yet"
    echo "    Run: sudo certbot --nginx -d galion.app -d api.galion.app"
fi
total_tests=$((total_tests + 1))
echo ""

# ==================== EXTERNAL URLS ====================
echo -e "${YELLOW}9. External URLs (if DNS configured)${NC}"

test_url() {
    local name=$1
    local url=$2
    total_tests=$((total_tests + 1))
    
    HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" -m 5 "$url" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} $name (200 OK)"
        passed_tests=$((passed_tests + 1))
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "  ${YELLOW}⚠${NC} $name (timeout - DNS not configured?)"
    else
        echo -e "  ${RED}✗${NC} $name ($HTTP_CODE)"
    fi
}

test_url "galion.app" "https://galion.app"
test_url "api.galion.app" "https://api.galion.app/health"
test_url "studio.galion.app" "https://studio.galion.app"
test_url "api.studio.galion.app" "https://api.studio.galion.app/health"
echo ""

# ==================== PERFORMANCE METRICS ====================
echo -e "${YELLOW}10. Performance Metrics${NC}"

# API response time
echo -n "  Testing API response time... "
START_TIME=$(date +%s%N)
curl -f -s http://localhost:8001/health >/dev/null 2>&1
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds

if [ "$RESPONSE_TIME" -lt 200 ]; then
    echo -e "${GREEN}✓${NC} ${RESPONSE_TIME}ms (< 200ms)"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${YELLOW}⚠${NC} ${RESPONSE_TIME}ms (>= 200ms)"
fi
total_tests=$((total_tests + 1))
echo ""

# ==================== BACKUP CONFIGURATION ====================
echo -e "${YELLOW}11. Backup Configuration${NC}"
run_test "Backup directory exists" "test -d backups"
run_test "Backup script exists" "test -f scripts/backup.sh"
run_test "Restore script exists" "test -f scripts/restore.sh"
run_test "Incremental backup script exists" "test -f scripts/incremental-backup.sh"

# Check if cron jobs are configured
if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    echo -e "  ${GREEN}✓${NC} Backup cron job configured"
    passed_tests=$((passed_tests + 1))
else
    echo -e "  ${YELLOW}⚠${NC} Backup cron job not configured"
fi
total_tests=$((total_tests + 1))
echo ""

# ==================== FINAL SUMMARY ====================
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Verification Summary                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

PASS_RATE=$((passed_tests * 100 / total_tests))

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}All tests passed: $passed_tests/$total_tests (100%)${NC}"
    echo ""
    echo -e "${GREEN}✓ Deployment is production-ready!${NC}"
    EXIT_CODE=0
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "${YELLOW}Most tests passed: $passed_tests/$total_tests ($PASS_RATE%)${NC}"
    echo ""
    echo -e "${YELLOW}⚠ Deployment is functional but has some issues.${NC}"
    echo "Review the failed tests above."
    EXIT_CODE=0
else
    echo -e "${RED}Many tests failed: $passed_tests/$total_tests ($PASS_RATE%)${NC}"
    echo ""
    echo -e "${RED}✗ Deployment has critical issues!${NC}"
    echo "Please fix the failures before going live."
    EXIT_CODE=1
fi

echo ""
echo -e "${YELLOW}Recommended next steps:${NC}"
echo "  1. Monitor Grafana dashboards"
echo "  2. Run load test: k6 run tests/load/api-test.js"
echo "  3. Test user registration and login"
echo "  4. Test voice interaction"
echo "  5. Review logs: docker compose logs -f"
echo ""

# Log verification
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Verification: $passed_tests/$total_tests passed" >> logs/verification.log

exit $EXIT_CODE

