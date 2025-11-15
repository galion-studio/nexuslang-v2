#!/bin/bash
# Comprehensive Health Check for Galion Platform
# Tests all services, endpoints, and system health

echo "🏥 COMPREHENSIVE HEALTH CHECK"
echo "=============================="
echo ""
echo "Timestamp: $(date)"
echo "Hostname: $(hostname)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

# ============================================
# TEST 1: PM2 SERVICE STATUS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 1: PM2 SERVICE STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v pm2 &> /dev/null; then
    echo -e "${GREEN}✅ PM2 installed${NC}"
    PASS=$((PASS + 1))
    
    echo ""
    pm2 list
    echo ""
    
    # Check backend
    if pm2 list | grep -q "backend.*online"; then
        echo -e "${GREEN}✅ Backend: ONLINE${NC}"
        PASS=$((PASS + 1))
    elif pm2 list | grep -q "backend"; then
        echo -e "${RED}❌ Backend: ERRORED${NC}"
        FAIL=$((FAIL + 1))
        echo "Recent backend logs:"
        pm2 logs backend --lines 10 --nostream 2>&1 | tail -10
    else
        echo -e "${YELLOW}⚠️  Backend: NOT RUNNING${NC}"
        WARN=$((WARN + 1))
    fi
    
    # Check galion-studio
    if pm2 list | grep -q "galion-studio.*online"; then
        echo -e "${GREEN}✅ Galion Studio: ONLINE${NC}"
        PASS=$((PASS + 1))
    elif pm2 list | grep -q "galion-studio"; then
        echo -e "${RED}❌ Galion Studio: ERRORED${NC}"
        FAIL=$((FAIL + 1))
        echo "Recent galion-studio logs:"
        pm2 logs galion-studio --lines 10 --nostream 2>&1 | tail -10
    else
        echo -e "${YELLOW}⚠️  Galion Studio: NOT RUNNING${NC}"
        WARN=$((WARN + 1))
    fi
else
    echo -e "${RED}❌ PM2 not installed${NC}"
    FAIL=$((FAIL + 1))
fi

echo ""

# ============================================
# TEST 2: NGINX STATUS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 2: NGINX STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if pgrep nginx > /dev/null; then
    echo -e "${GREEN}✅ Nginx: RUNNING${NC}"
    PASS=$((PASS + 1))
    
    echo "Nginx processes:"
    ps aux | grep nginx | grep -v grep | head -3
    
    # Test nginx config
    if nginx -t 2>&1 | grep -q "successful"; then
        echo -e "${GREEN}✅ Nginx config: VALID${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ Nginx config: INVALID${NC}"
        FAIL=$((FAIL + 1))
        nginx -t
    fi
else
    echo -e "${RED}❌ Nginx: NOT RUNNING${NC}"
    FAIL=$((FAIL + 1))
fi

echo ""

# ============================================
# TEST 3: PORT AVAILABILITY
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 3: PORT AVAILABILITY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_port() {
    local port=$1
    local name=$2
    
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✅ Port $port ($name): LISTENING${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ Port $port ($name): NOT LISTENING${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_port 80 "Nginx"
check_port 8000 "Backend API"
check_port 3030 "Galion Studio"

echo ""

# ============================================
# TEST 4: BACKEND API ENDPOINTS
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 4: BACKEND API ENDPOINTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-5}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ HTTP $response${NC}"
        PASS=$((PASS + 1))
        return 0
    elif [ -z "$response" ]; then
        echo -e "${RED}❌ NO RESPONSE${NC}"
        FAIL=$((FAIL + 1))
        return 1
    else
        echo -e "${YELLOW}⚠️  HTTP $response${NC}"
        WARN=$((WARN + 1))
        return 1
    fi
}

test_endpoint "http://localhost:8000/health" "Health Check"
test_endpoint "http://localhost:8000/" "Root Endpoint"
test_endpoint "http://localhost:8000/docs" "API Documentation"
test_endpoint "http://localhost:8000/system-info" "System Info"
test_endpoint "http://localhost:8000/api/v1/test" "API Test"

echo ""

# ============================================
# TEST 5: BACKEND API RESPONSE CONTENT
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 5: BACKEND API RESPONSE CONTENT${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "Health endpoint response:"
health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ ! -z "$health_response" ]; then
    echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
    
    if echo "$health_response" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Health status: healthy${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${YELLOW}⚠️  Health status: unknown${NC}"
        WARN=$((WARN + 1))
    fi
else
    echo -e "${RED}❌ No response from health endpoint${NC}"
    FAIL=$((FAIL + 1))
fi

echo ""

# ============================================
# TEST 6: FRONTEND SERVICES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 6: FRONTEND SERVICES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "http://localhost:3030" "Galion Studio Direct" 10

echo ""

# ============================================
# TEST 7: NGINX PROXY
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 7: NGINX PROXY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "http://localhost" "Nginx → Galion Studio" 10
test_endpoint "http://localhost/health" "Nginx → Backend Health" 5

echo ""

# ============================================
# TEST 8: FILE SYSTEM
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 8: FILE SYSTEM${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_file() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $name: EXISTS${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ $name: MISSING${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_file "v2/backend/main_simple.py" "Backend main file"
check_file "ecosystem.config.js" "PM2 ecosystem"
check_file "/etc/nginx/sites-enabled/galion" "Nginx config"

if [ -d "galion-studio" ]; then
    echo -e "${GREEN}✅ galion-studio directory: EXISTS${NC}"
    PASS=$((PASS + 1))
    
    if [ -d "galion-studio/node_modules" ]; then
        echo -e "${GREEN}✅ galion-studio node_modules: EXISTS${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ galion-studio node_modules: MISSING${NC}"
        FAIL=$((FAIL + 1))
    fi
else
    echo -e "${RED}❌ galion-studio directory: MISSING${NC}"
    FAIL=$((FAIL + 1))
fi

echo ""

# ============================================
# TEST 9: SYSTEM RESOURCES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 9: SYSTEM RESOURCES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h / | tail -1

echo ""
echo "CPU Load:"
uptime

echo ""

# ============================================
# TEST 10: DEPENDENCIES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 10: PYTHON DEPENDENCIES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_python_package() {
    local package=$1
    
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ $package${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_python_package "fastapi"
check_python_package "uvicorn"
check_python_package "psutil"
check_python_package "pydantic"

echo ""

# ============================================
# TEST 11: LOGS CHECK
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 11: RECENT LOGS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if pm2 list | grep -q "backend.*online"; then
    echo "Backend logs (last 5 lines):"
    pm2 logs backend --lines 5 --nostream 2>&1 | tail -5
    echo ""
fi

if pm2 list | grep -q "galion-studio.*online"; then
    echo "Galion Studio logs (last 5 lines):"
    pm2 logs galion-studio --lines 5 --nostream 2>&1 | tail -5
    echo ""
fi

# ============================================
# TEST 12: NETWORK CONNECTIVITY
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 12: NETWORK CONNECTIVITY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "Container IP:"
hostname -i

echo ""
echo "Listening ports:"
ss -tlnp 2>/dev/null | grep LISTEN | grep -E ':(80|8000|3030)' || echo "No services listening"

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 HEALTH CHECK SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL=$((PASS + FAIL + WARN))
PASS_PERCENT=$((PASS * 100 / TOTAL))

echo "Total Tests: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASS ($PASS_PERCENT%)${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARN${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 ALL CRITICAL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}✅ Your Galion Platform is HEALTHY and PRODUCTION-READY!${NC}"
    echo ""
    echo "🌐 Access URLs:"
    echo "   • Main App: http://localhost"
    echo "   • Backend API: http://localhost:8000/health"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitoring:"
    echo "   • PM2 Status: pm2 list"
    echo "   • PM2 Logs: pm2 logs"
    echo "   • PM2 Monitor: pm2 monit"
    echo ""
    exit 0
elif [ $FAIL -le 3 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  MINOR ISSUES DETECTED${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Some services may need attention, but core functionality is working."
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   • Check logs: pm2 logs"
    echo "   • Restart services: pm2 restart all"
    echo "   • Re-run setup: bash ultimate-fix.sh"
    echo ""
    exit 1
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ CRITICAL ISSUES DETECTED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Multiple services are not working correctly."
    echo ""
    echo "🔧 Recommended Actions:"
    echo "   1. Run: bash ultimate-fix.sh"
    echo "   2. Check logs: pm2 logs"
    echo "   3. Verify files: ls -la v2/backend/"
    echo ""
    exit 2
fi

