#!/bin/bash

# Galion Ecosystem - Final Deployment Verification
# Comprehensive check of all services and endpoints

set -e

echo "🎯 GALION ECOSYSTEM - FINAL DEPLOYMENT CHECK"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counter for checks
TOTAL_CHECKS=0
PASSED_CHECKS=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

((TOTAL_CHECKS++))

# 1. Check if we're in the right directory
echo "📍 DIRECTORY CHECK"
echo "=================="
if [[ "$(basename $(pwd))" == "nexuslang-v2" ]]; then
    check_pass "In correct project directory (nexuslang-v2)"
else
    check_fail "Not in nexuslang-v2 directory"
fi

echo ""

# 2. Check PM2 status
echo "🚀 PM2 SERVICES CHECK"
echo "====================="
((TOTAL_CHECKS++))
if command -v pm2 &> /dev/null; then
    check_pass "PM2 is installed"
else
    check_fail "PM2 is not installed"
fi

((TOTAL_CHECKS++))
PM2_STATUS=$(pm2 jlist 2>/dev/null)
if [[ $? -eq 0 ]]; then
    BACKEND_COUNT=$(echo "$PM2_STATUS" | jq -r '.[] | select(.name == "galion-backend") | .pm2_env.status' 2>/dev/null | grep -c "online" || echo "0")
    if [[ "$BACKEND_COUNT" -gt 0 ]]; then
        check_pass "Backend service is running ($BACKEND_COUNT instance(s))"
    else
        check_fail "Backend service is not running"
    fi
else
    check_fail "Cannot check PM2 status"
fi

echo ""

# 3. Check backend direct access
echo "🔧 BACKEND DIRECT ACCESS CHECK"
echo "=============================="
((TOTAL_CHECKS++))
BACKEND_RESPONSE=$(curl -s --max-time 5 http://localhost:8000/health 2>/dev/null)
if [[ $? -eq 0 ]] && [[ "$BACKEND_RESPONSE" == *"healthy"* ]]; then
    check_pass "Backend direct access working"
    echo "   Response: $BACKEND_RESPONSE"
else
    check_fail "Backend direct access failed"
fi

echo ""

# 4. Check nginx status
echo "🌐 NGINX STATUS CHECK"
echo "====================="
((TOTAL_CHECKS++))
if pgrep -x "nginx" > /dev/null; then
    check_pass "Nginx is running"
else
    check_fail "Nginx is not running"
fi

((TOTAL_CHECKS++))
if ss -tlnp | grep -q :80; then
    check_pass "Nginx listening on port 80"
else
    check_fail "Nginx not listening on port 80"
fi

echo ""

# 5. Check nginx endpoints
echo "🔗 NGINX ENDPOINTS CHECK"
echo "========================"

# Health endpoint
((TOTAL_CHECKS++))
HEALTH_RESPONSE=$(curl -s --max-time 5 http://localhost/health 2>/dev/null)
if [[ "$HEALTH_RESPONSE" == "healthy" ]]; then
    check_pass "Health endpoint (/health) working"
else
    check_fail "Health endpoint failed"
fi

# Root endpoint
((TOTAL_CHECKS++))
ROOT_RESPONSE=$(curl -s --max-time 5 http://localhost/ 2>/dev/null)
if [[ "$ROOT_RESPONSE" == *"Galion Ecosystem"* ]]; then
    check_pass "Root endpoint (/) working"
else
    check_fail "Root endpoint failed"
fi

# API endpoint
((TOTAL_CHECKS++))
API_RESPONSE=$(curl -s --max-time 5 http://localhost/api/health 2>/dev/null)
if [[ "$API_RESPONSE" == *"healthy"* ]] && [[ "$API_RESPONSE" == *"status"* ]]; then
    check_pass "API endpoint (/api/health) working"
    echo "   Response: $API_RESPONSE"
else
    check_fail "API endpoint failed or returning wrong response"
fi

echo ""

# 6. Check nginx configuration
echo "⚙️  NGINX CONFIGURATION CHECK"
echo "============================"
((TOTAL_CHECKS++))
if sudo nginx -t 2>/dev/null; then
    check_pass "Nginx configuration is valid"
else
    check_fail "Nginx configuration has errors"
    sudo nginx -t
fi

echo ""

# 7. Check system resources
echo "💻 SYSTEM RESOURCES CHECK"
echo "========================="
((TOTAL_CHECKS++))
MEMORY_USAGE=$(free -h | grep "Mem:" | awk '{print $3 "/" $2}')
if [[ -n "$MEMORY_USAGE" ]]; then
    check_pass "System memory: $MEMORY_USAGE"
else
    check_warn "Could not check memory usage"
fi

((TOTAL_CHECKS++))
DISK_USAGE=$(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')
if [[ -n "$DISK_USAGE" ]]; then
    check_pass "Disk usage: $DISK_USAGE"
else
    check_warn "Could not check disk usage"
fi

echo ""

# 8. Network connectivity check
echo "🌍 NETWORK CONNECTIVITY CHECK"
echo "============================="
((TOTAL_CHECKS++))
if curl -s --max-time 5 https://www.google.com > /dev/null 2>&1; then
    check_pass "Internet connectivity working"
else
    check_warn "Internet connectivity check failed"
fi

echo ""

# 9. Final summary
echo "📊 FINAL DEPLOYMENT SUMMARY"
echo "=========================="

SUCCESS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

if [[ $SUCCESS_RATE -eq 100 ]]; then
    echo -e "${GREEN}🎉 PERFECT DEPLOYMENT! (100% success rate)${NC}"
    echo ""
    echo "✅ All services are running correctly"
    echo "✅ API is fully accessible via nginx proxy"
    echo "✅ Backend is responding with health data"
    echo "✅ System resources are normal"
    echo ""
    echo "🚀 YOUR GALION ECOSYSTEM IS PRODUCTION READY!"
    echo ""
    echo "🌐 Access your API at: http://[your-runpod-ip]/api/health"
    echo "💚 Health check at: http://[your-runpod-ip]/health"
    echo "ℹ️  API info at: http://[your-runpod-ip]/"
    echo ""
    echo "🔧 Remember to expose port 80 in RunPod dashboard!"
elif [[ $SUCCESS_RATE -ge 80 ]]; then
    echo -e "${YELLOW}⚠️  MOSTLY WORKING ($SUCCESS_RATE% success rate)${NC}"
    echo ""
    echo "Most services are operational but some issues remain."
    echo "Check the failed tests above for details."
else
    echo -e "${RED}❌ DEPLOYMENT ISSUES ($SUCCESS_RATE% success rate)${NC}"
    echo ""
    echo "Several critical services are not working."
    echo "Review the failed tests above and fix them."
fi

echo ""
echo "📈 Test Results: $PASSED_CHECKS/$TOTAL_CHECKS passed ($SUCCESS_RATE%)"
echo ""
echo "Script completed at: $(date)"
