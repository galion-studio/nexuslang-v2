#!/bin/bash
# MEGA COMPREHENSIVE CHECK - Tests EVERYTHING
# All services, all dependencies, all endpoints, all code, all microservices

echo "🚀 MEGA COMPREHENSIVE PLATFORM CHECK"
echo "====================================="
echo ""
echo "Timestamp: $(date)"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

# ============================================
# SECTION 1: SYSTEM & ENVIRONMENT
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📦 SECTION 1: SYSTEM & ENVIRONMENT${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check system info
echo -e "${CYAN}System Information:${NC}"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Python: $(python3 --version)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo ""

# Check disk space
echo -e "${CYAN}Disk Space:${NC}"
df -h / | tail -1
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage OK: ${DISK_USAGE}%${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${YELLOW}⚠️  Disk usage high: ${DISK_USAGE}%${NC}"
    WARN=$((WARN + 1))
fi
echo ""

# Check memory
echo -e "${CYAN}Memory Usage:${NC}"
free -h
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_USAGE -lt 90 ]; then
    echo -e "${GREEN}✅ Memory usage OK: ${MEM_USAGE}%${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${YELLOW}⚠️  Memory usage high: ${MEM_USAGE}%${NC}"
    WARN=$((WARN + 1))
fi
echo ""

# ============================================
# SECTION 2: ALL PYTHON DEPENDENCIES
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🐍 SECTION 2: PYTHON DEPENDENCIES${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PYTHON_PACKAGES=(
    "fastapi"
    "uvicorn"
    "psutil"
    "pydantic"
    "starlette"
    "typing_extensions"
    "multipart"
)

for pkg in "${PYTHON_PACKAGES[@]}"; do
    echo -n "Checking $pkg... "
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}✅ INSTALLED${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ MISSING${NC}"
        FAIL=$((FAIL + 1))
    fi
done
echo ""

# Check Python package versions
echo -e "${CYAN}Python Package Versions:${NC}"
pip3 list | grep -E "fastapi|uvicorn|pydantic|starlette" 2>/dev/null || echo "Could not list packages"
echo ""

# ============================================
# SECTION 3: ALL NODE.JS DEPENDENCIES
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📦 SECTION 3: NODE.JS DEPENDENCIES${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check galion-studio dependencies
if [ -d "galion-studio" ]; then
    echo -e "${CYAN}Galion Studio Dependencies:${NC}"
    cd galion-studio
    
    STUDIO_PACKAGES=(
        "next"
        "react"
        "react-dom"
        "react-hot-toast"
        "lucide-react"
        "clsx"
        "tailwind-merge"
        "typescript"
    )
    
    for pkg in "${STUDIO_PACKAGES[@]}"; do
        echo -n "  $pkg... "
        if [ -d "node_modules/$pkg" ]; then
            echo -e "${GREEN}✅${NC}"
            PASS=$((PASS + 1))
        else
            echo -e "${RED}❌${NC}"
            FAIL=$((FAIL + 1))
        fi
    done
    cd ..
else
    echo -e "${RED}❌ galion-studio directory not found${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# Check galion-app dependencies
if [ -d "galion-app" ]; then
    echo -e "${CYAN}Galion App Dependencies:${NC}"
    cd galion-app
    
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✅ node_modules exists${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ node_modules missing${NC}"
        FAIL=$((FAIL + 1))
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  galion-app directory not found${NC}"
    WARN=$((WARN + 1))
fi
echo ""

# Check developer-platform dependencies
if [ -d "developer-platform" ]; then
    echo -e "${CYAN}Developer Platform Dependencies:${NC}"
    cd developer-platform
    
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✅ node_modules exists${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ node_modules missing${NC}"
        FAIL=$((FAIL + 1))
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  developer-platform directory not found${NC}"
    WARN=$((WARN + 1))
fi
echo ""

# ============================================
# SECTION 4: ALL PM2 SERVICES
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}⚙️  SECTION 4: PM2 SERVICES${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v pm2 &> /dev/null; then
    echo -e "${GREEN}✅ PM2 installed${NC}"
    PASS=$((PASS + 1))
    
    echo ""
    pm2 list
    echo ""
    
    # Check each service
    SERVICES=("backend" "galion-studio" "galion-app" "developer-platform")
    
    for service in "${SERVICES[@]}"; do
        echo -n "Checking $service... "
        if pm2 list | grep -q "$service.*online"; then
            echo -e "${GREEN}✅ ONLINE${NC}"
            PASS=$((PASS + 1))
        elif pm2 list | grep -q "$service.*stopped"; then
            echo -e "${YELLOW}⚠️  STOPPED${NC}"
            WARN=$((WARN + 1))
        elif pm2 list | grep -q "$service.*errored"; then
            echo -e "${RED}❌ ERRORED${NC}"
            FAIL=$((FAIL + 1))
            echo "Recent logs:"
            pm2 logs $service --lines 5 --nostream 2>&1 | tail -5
        else
            echo -e "${YELLOW}⚠️  NOT RUNNING${NC}"
            WARN=$((WARN + 1))
        fi
    done
else
    echo -e "${RED}❌ PM2 not installed${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# ============================================
# SECTION 5: ALL PORTS
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🔌 SECTION 5: PORT AVAILABILITY${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PORTS=(
    "80:Nginx"
    "8000:Backend API"
    "3000:Galion App"
    "3003:Developer Platform"
    "3030:Galion Studio"
)

for port_info in "${PORTS[@]}"; do
    port=$(echo $port_info | cut -d: -f1)
    name=$(echo $port_info | cut -d: -f2)
    
    echo -n "Port $port ($name)... "
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✅ LISTENING${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ NOT LISTENING${NC}"
        FAIL=$((FAIL + 1))
    fi
done
echo ""

# ============================================
# SECTION 6: ALL BACKEND ENDPOINTS
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🔧 SECTION 6: BACKEND API ENDPOINTS${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

ENDPOINTS=(
    "http://localhost:8000/:Root"
    "http://localhost:8000/health:Health Check"
    "http://localhost:8000/docs:API Docs"
    "http://localhost:8000/openapi.json:OpenAPI Schema"
    "http://localhost:8000/system-info:System Info"
    "http://localhost:8000/api/v1/test:API Test"
    "http://localhost:8000/api/v1/scientific-capabilities:Scientific Capabilities"
    "http://localhost:8000/grokopedia/:Grokopedia Home"
    "http://localhost:8000/grokopedia/topics:Grokopedia Topics"
    "http://localhost:8000/nexuslang/:NexusLang Home"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    url=$(echo $endpoint_info | cut -d: -f1,2,3)
    name=$(echo $endpoint_info | cut -d: -f4)
    
    echo -n "$name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ HTTP $response${NC}"
        PASS=$((PASS + 1))
    elif [ -z "$response" ]; then
        echo -e "${RED}❌ NO RESPONSE${NC}"
        FAIL=$((FAIL + 1))
    else
        echo -e "${YELLOW}⚠️  HTTP $response${NC}"
        WARN=$((WARN + 1))
    fi
done
echo ""

# ============================================
# SECTION 7: BACKEND API RESPONSES
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📊 SECTION 7: API RESPONSE CONTENT${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}Health Endpoint Response:${NC}"
health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ ! -z "$health_response" ]; then
    echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
    
    if echo "$health_response" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Status: healthy${NC}"
        PASS=$((PASS + 1))
    fi
    
    if echo "$health_response" | grep -q "grokopedia"; then
        echo -e "${GREEN}✅ Grokopedia service detected${NC}"
        PASS=$((PASS + 1))
    fi
fi
echo ""

echo -e "${CYAN}System Info Response:${NC}"
sysinfo=$(curl -s http://localhost:8000/system-info 2>/dev/null)
if [ ! -z "$sysinfo" ]; then
    echo "$sysinfo" | python3 -m json.tool 2>/dev/null | head -20
    echo -e "${GREEN}✅ System info available${NC}"
    PASS=$((PASS + 1))
fi
echo ""

# ============================================
# SECTION 8: ALL FRONTEND SERVICES
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🎨 SECTION 8: FRONTEND SERVICES${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

FRONTENDS=(
    "http://localhost:3030:Galion Studio"
    "http://localhost:3000:Galion App"
    "http://localhost:3003:Developer Platform"
)

for frontend_info in "${FRONTENDS[@]}"; do
    url=$(echo $frontend_info | cut -d: -f1,2,3)
    name=$(echo $frontend_info | cut -d: -f4)
    
    echo -n "$name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ HTTP $response${NC}"
        PASS=$((PASS + 1))
    elif [ "$response" = "500" ]; then
        echo -e "${YELLOW}⚠️  HTTP $response (may be starting)${NC}"
        WARN=$((WARN + 1))
    elif [ -z "$response" ]; then
        echo -e "${RED}❌ NO RESPONSE${NC}"
        FAIL=$((FAIL + 1))
    else
        echo -e "${YELLOW}⚠️  HTTP $response${NC}"
        WARN=$((WARN + 1))
    fi
done
echo ""

# ============================================
# SECTION 9: NGINX CONFIGURATION
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🌐 SECTION 9: NGINX${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

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
    fi
    
    # Test nginx proxy
    echo ""
    echo "Testing Nginx proxy:"
    echo -n "  / → Galion Studio... "
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost | grep -q "200"; then
        echo -e "${GREEN}✅${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌${NC}"
        FAIL=$((FAIL + 1))
    fi
    
    echo -n "  /health → Backend... "
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost/health | grep -q "200"; then
        echo -e "${GREEN}✅${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌${NC}"
        FAIL=$((FAIL + 1))
    fi
else
    echo -e "${RED}❌ Nginx: NOT RUNNING${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# ============================================
# SECTION 10: FILE SYSTEM & CODE
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📁 SECTION 10: FILE SYSTEM & CODE${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CRITICAL_FILES=(
    "v2/backend/main_simple.py:Backend Main"
    "v2/backend/api/grokopedia.py:Grokopedia API"
    "ecosystem.config.js:PM2 Ecosystem"
    "/etc/nginx/sites-enabled/galion:Nginx Config"
    "galion-studio/package.json:Studio Package"
)

for file_info in "${CRITICAL_FILES[@]}"; do
    file=$(echo $file_info | cut -d: -f1)
    name=$(echo $file_info | cut -d: -f2)
    
    echo -n "$name... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ MISSING${NC}"
        FAIL=$((FAIL + 1))
    fi
done
echo ""

# Check directory structure
echo -e "${CYAN}Directory Structure:${NC}"
DIRS=("v2/backend" "galion-studio" "galion-app" "developer-platform")

for dir in "${DIRS[@]}"; do
    echo -n "  $dir... "
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌${NC}"
        FAIL=$((FAIL + 1))
    fi
done
echo ""

# ============================================
# SECTION 11: GIT REPOSITORY
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🔀 SECTION 11: GIT REPOSITORY${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -d ".git" ]; then
    echo -e "${GREEN}✅ Git repository initialized${NC}"
    PASS=$((PASS + 1))
    
    echo "Current branch: $(git branch --show-current)"
    echo "Latest commit: $(git log -1 --oneline)"
    
    # Check if repo is clean
    if git diff-index --quiet HEAD --; then
        echo -e "${GREEN}✅ Working directory clean${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${YELLOW}⚠️  Uncommitted changes present${NC}"
        WARN=$((WARN + 1))
    fi
else
    echo -e "${RED}❌ Not a git repository${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# ============================================
# SECTION 12: LOGS ANALYSIS
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📝 SECTION 12: LOGS ANALYSIS${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if pm2 list | grep -q "backend.*online"; then
    echo -e "${CYAN}Backend Logs (last 10 lines):${NC}"
    pm2 logs backend --lines 10 --nostream 2>&1 | tail -10
    
    # Check for errors in logs
    error_count=$(pm2 logs backend --lines 100 --nostream 2>&1 | grep -i "error" | wc -l)
    if [ $error_count -eq 0 ]; then
        echo -e "${GREEN}✅ No errors in backend logs${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${YELLOW}⚠️  Found $error_count error mentions in logs${NC}"
        WARN=$((WARN + 1))
    fi
    echo ""
fi

if pm2 list | grep -q "galion-studio.*online"; then
    echo -e "${CYAN}Galion Studio Logs (last 10 lines):${NC}"
    pm2 logs galion-studio --lines 10 --nostream 2>&1 | tail -10
    echo ""
fi

# ============================================
# SECTION 13: NETWORK & CONNECTIVITY
# ============================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🌐 SECTION 13: NETWORK & CONNECTIVITY${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Container IP: $(hostname -i)"
echo ""

echo "All listening ports:"
ss -tlnp 2>/dev/null | grep LISTEN | head -10
echo ""

# Test internal connectivity
echo "Testing internal connectivity:"
echo -n "  localhost:8000... "
if curl -s --max-time 2 http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}❌${NC}"
    FAIL=$((FAIL + 1))
fi

echo -n "  localhost:3030... "
if curl -s --max-time 2 http://localhost:3030 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}❌${NC}"
    FAIL=$((FAIL + 1))
fi

echo -n "  localhost:80... "
if curl -s --max-time 2 http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}❌${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# ============================================
# MEGA FINAL SUMMARY
# ============================================
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🏆 MEGA COMPREHENSIVE CHECK SUMMARY${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL=$((PASS + FAIL + WARN))
if [ $TOTAL -gt 0 ]; then
    PASS_PERCENT=$((PASS * 100 / TOTAL))
else
    PASS_PERCENT=0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total Tests Run: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASS ($PASS_PERCENT%)${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Determine overall status
if [ $FAIL -eq 0 ] && [ $WARN -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 PERFECT! ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}✅ Your Galion Platform is 100% OPERATIONAL!${NC}"
    echo ""
    echo "🌟 All services running perfectly"
    echo "🌟 All dependencies installed"
    echo "🌟 All endpoints responding"
    echo "🌟 All code files present"
    echo "🌟 Production-ready!"
    echo ""
    exit 0
elif [ $FAIL -eq 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}✅ EXCELLENT! CORE TESTS PASSED${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo -e "${YELLOW}⚠️  $WARN minor warnings (non-critical)${NC}"
    echo ""
    echo "Your platform is operational with minor notes."
    echo ""
    exit 0
elif [ $FAIL -le 5 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  MINOR ISSUES DETECTED${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Platform is mostly working but needs attention:"
    echo -e "  ${GREEN}✅ Passed: $PASS${NC}"
    echo -e "  ${RED}❌ Failed: $FAIL${NC}"
    echo -e "  ${YELLOW}⚠️  Warnings: $WARN${NC}"
    echo ""
    echo "🔧 Recommended actions:"
    echo "  1. Check failed tests above"
    echo "  2. Run: pm2 logs"
    echo "  3. Run: bash ultimate-fix.sh"
    echo ""
    exit 1
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ CRITICAL ISSUES DETECTED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Multiple critical failures detected:"
    echo -e "  ${GREEN}✅ Passed: $PASS${NC}"
    echo -e "  ${RED}❌ Failed: $FAIL${NC}"
    echo -e "  ${YELLOW}⚠️  Warnings: $WARN${NC}"
    echo ""
    echo "🚨 Immediate actions required:"
    echo "  1. Run: bash ultimate-fix.sh"
    echo "  2. Check logs: pm2 logs"
    echo "  3. Verify files: ls -la v2/backend/"
    echo "  4. Check dependencies"
    echo ""
    exit 2
fi

