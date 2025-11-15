#!/bin/bash
# ============================================
# Comprehensive Platform Testing Script
# Tests ALL services, endpoints, and functionality
# ============================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

print_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
}

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    HTTP_CODE=$(curl -s -o /tmp/test_response.txt -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$HTTP_CODE" = "$expected" ]; then
        echo -e "${GREEN}✓${NC} $name: HTTP $HTTP_CODE"
        ((PASS++))
        return 0
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${RED}✗${NC} $name: NOT RESPONDING"
        ((FAIL++))
        return 1
    else
        echo -e "${YELLOW}⚠${NC} $name: HTTP $HTTP_CODE (expected $expected)"
        ((WARN++))
        return 1
    fi
}

test_json_endpoint() {
    local name="$1"
    local url="$2"
    local key="$3"
    
    RESPONSE=$(curl -s "$url" 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "$key"; then
        echo -e "${GREEN}✓${NC} $name: JSON valid, contains '$key'"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} $name: Invalid JSON or missing '$key'"
        echo "   Response: $(echo "$RESPONSE" | head -c 100)"
        ((FAIL++))
        return 1
    fi
}

# START TESTING
clear
print_header "🧪 COMPREHENSIVE PLATFORM TEST"

echo -e "${BLUE}Test Date:${NC} $(date)"
echo -e "${BLUE}RunPod IP:${NC} 213.173.105.83"
echo -e "${BLUE}Location:${NC} /nexuslang-v2"
echo ""

# ============================================
# TEST 1: PM2 Services
# ============================================
print_header "TEST 1: PM2 SERVICE STATUS"

echo -e "${BLUE}Checking PM2 services...${NC}"
pm2 jlist > /tmp/pm2_services.json

for service in backend galion-studio galion-app developer-platform; do
    if pm2 describe $service > /dev/null 2>&1; then
        STATUS=$(pm2 jlist | grep -A 10 "\"name\":\"$service\"" | grep "\"status\"" | cut -d'"' -f4)
        MEMORY=$(pm2 jlist | grep -A 10 "\"name\":\"$service\"" | grep "\"memory\"" | cut -d':' -f2 | cut -d',' -f1)
        
        if [ "$STATUS" = "online" ]; then
            echo -e "${GREEN}✓${NC} $service: ONLINE (Memory: $MEMORY bytes)"
            ((PASS++))
        else
            echo -e "${RED}✗${NC} $service: $STATUS"
            ((FAIL++))
        fi
    else
        echo -e "${RED}✗${NC} $service: NOT FOUND IN PM2"
        ((FAIL++))
    fi
done

# ============================================
# TEST 2: Backend API Endpoints
# ============================================
print_header "TEST 2: BACKEND API ENDPOINTS"

test_json_endpoint "Health Check" "http://localhost:8000/health" "healthy"
test_endpoint "API Documentation" "http://localhost:8000/docs" "200"
test_endpoint "OpenAPI Schema" "http://localhost:8000/openapi.json" "200"
test_json_endpoint "System Info" "http://localhost:8000/system-info" "cpu"

# Test Grokopedia
test_endpoint "Grokopedia Base" "http://localhost:8000/grokopedia/" "200"
test_endpoint "Grokopedia Topics" "http://localhost:8000/grokopedia/topics" "200"

# Test NexusLang
test_endpoint "NexusLang Compile" "http://localhost:8000/nexuslang/compile" "405"

# ============================================
# TEST 3: Frontend Services
# ============================================
print_header "TEST 3: FRONTEND SERVICES"

test_endpoint "Galion Studio Home" "http://localhost:3030" "200"
test_endpoint "Galion App Home" "http://localhost:3000" "200"
test_endpoint "Developer Platform Home" "http://localhost:3003" "200"

# ============================================
# TEST 4: Port Listening
# ============================================
print_header "TEST 4: PORT AVAILABILITY"

echo -e "${BLUE}Checking which ports are listening...${NC}"

for port in 8000 3000 3003 3030; do
    if ss -tlnp 2>/dev/null | grep -q ":$port " || netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✓${NC} Port $port: LISTENING"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} Port $port: NOT LISTENING"
        ((FAIL++))
    fi
done

# ============================================
# TEST 5: File Structure
# ============================================
print_header "TEST 5: FILE STRUCTURE"

echo -e "${BLUE}Checking critical directories and files...${NC}"

CRITICAL_PATHS=(
    "/nexuslang-v2/v2/backend/main_simple.py"
    "/nexuslang-v2/galion-studio/app"
    "/nexuslang-v2/galion-app/app"
    "/nexuslang-v2/developer-platform/app"
    "/nexuslang-v2/shared/styles/design-tokens.css"
    "/nexuslang-v2/galion-app/lib/utils.ts"
    "/nexuslang-v2/galion-app/components/ui"
)

for path in "${CRITICAL_PATHS[@]}"; do
    if [ -e "$path" ]; then
        echo -e "${GREEN}✓${NC} $path"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $path: MISSING"
        ((FAIL++))
    fi
done

# ============================================
# TEST 6: Dependencies
# ============================================
print_header "TEST 6: PYTHON DEPENDENCIES"

PYTHON_DEPS=("fastapi" "uvicorn" "psutil" "pydantic")
for dep in "${PYTHON_DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python: $dep installed"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} Python: $dep MISSING"
        ((FAIL++))
    fi
done

# ============================================
# TEST 7: Node.js Dependencies
# ============================================
print_header "TEST 7: NODE.JS DEPENDENCIES"

cd /nexuslang-v2/galion-app
echo -e "${BLUE}Checking galion-app dependencies...${NC}"

NODE_DEPS=("next" "react" "lucide-react" "clsx" "tailwind-merge")
for dep in "${NODE_DEPS[@]}"; do
    if npm list "$dep" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} galion-app: $dep installed"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠${NC} galion-app: $dep missing or not listed"
        ((WARN++))
    fi
done

# ============================================
# TEST 8: System Resources
# ============================================
print_header "TEST 8: SYSTEM RESOURCES"

echo -e "${BLUE}Memory Usage:${NC}"
free -h | grep -E "Mem|Swap"
echo ""

echo -e "${BLUE}Disk Usage:${NC}"
df -h / | grep -v "Filesystem"
echo ""

echo -e "${BLUE}CPU Load:${NC}"
uptime
echo ""

# ============================================
# TEST 9: Process Check
# ============================================
print_header "TEST 9: RUNNING PROCESSES"

echo -e "${BLUE}Python processes:${NC}"
PYTHON_COUNT=$(ps aux | grep "python3.*main_simple" | grep -v grep | wc -l)
echo "   Backend workers: $PYTHON_COUNT"

echo -e "${BLUE}Node processes:${NC}"
NODE_COUNT=$(ps aux | grep "node.*next" | grep -v grep | wc -l)
echo "   Next.js servers: $NODE_COUNT"

echo -e "${BLUE}PM2 daemon:${NC}"
if ps aux | grep "PM2" | grep -v grep > /dev/null; then
    echo -e "   ${GREEN}✓${NC} PM2 running"
    ((PASS++))
else
    echo -e "   ${RED}✗${NC} PM2 not running"
    ((FAIL++))
fi

# ============================================
# TEST 10: Git Status
# ============================================
print_header "TEST 10: GIT STATUS"

cd /nexuslang-v2
echo -e "${BLUE}Current branch:${NC}"
git branch --show-current

echo -e "${BLUE}Latest commit:${NC}"
git log -1 --oneline

echo -e "${BLUE}Git status:${NC}"
if git diff-index --quiet HEAD --; then
    echo -e "   ${GREEN}✓${NC} Clean working directory"
    ((PASS++))
else
    echo -e "   ${YELLOW}⚠${NC} Uncommitted changes"
    ((WARN++))
fi

# ============================================
# TEST 11: Error Logs
# ============================================
print_header "TEST 11: RECENT ERRORS"

echo -e "${BLUE}Checking for recent errors in logs...${NC}"

for service in backend galion-studio galion-app developer-platform; do
    if pm2 describe $service > /dev/null 2>&1; then
        ERROR_COUNT=$(pm2 logs $service --lines 100 --nostream --err 2>/dev/null | grep -i "error" | wc -l)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}⚠${NC} $service: $ERROR_COUNT errors in last 100 lines"
            ((WARN++))
        else
            echo -e "${GREEN}✓${NC} $service: No errors"
            ((PASS++))
        fi
    fi
done

# ============================================
# TEST 12: External Access
# ============================================
print_header "TEST 12: EXTERNAL ACCESS READINESS"

echo -e "${BLUE}Checking if services are accessible externally...${NC}"

EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
echo "   External IP: $EXTERNAL_IP"

echo ""
echo "   URLs to test from browser:"
echo "   • http://$EXTERNAL_IP:8000/docs"
echo "   • http://$EXTERNAL_IP:3000"
echo "   • http://$EXTERNAL_IP:3003"
echo "   • http://$EXTERNAL_IP:3030"

# ============================================
# FINAL SUMMARY
# ============================================
print_header "📊 TEST SUMMARY"

TOTAL=$((PASS + FAIL + WARN))
echo -e "${GREEN}✓ Passed:${NC}  $PASS / $TOTAL"
echo -e "${RED}✗ Failed:${NC}  $FAIL / $TOTAL"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARN / $TOTAL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   ✅ ALL CRITICAL TESTS PASSED!${NC}"
    echo -e "${GREEN}============================================${NC}"
elif [ $FAIL -le 3 ]; then
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}   ⚠ MOSTLY WORKING (Minor issues)${NC}"
    echo -e "${YELLOW}============================================${NC}"
else
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}   ❌ MULTIPLE FAILURES DETECTED${NC}"
    echo -e "${RED}============================================${NC}"
fi

echo ""
echo -e "${BLUE}Final Status:${NC}"
pm2 status

echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  View logs:    pm2 logs"
echo "  Restart all:  pm2 restart all"
echo "  Deploy:       wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/runpod-deploy-simple.sh | bash"
echo ""

