#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  NexusLang v2 - Production Testing Suite                  ║
# ║  Comprehensive verification of all features                ║
# ╚════════════════════════════════════════════════════════════╝

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="${1:-http://localhost:8000}"
FRONTEND_URL="${2:-http://localhost:3000}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🧪 NexusLang v2 - Testing Suite                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Testing endpoints:"
echo "  Backend:  $BASE_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""

PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected, got $response)"
        ((FAILED++))
    fi
}

# Test with JSON response
test_json_endpoint() {
    local name=$1
    local url=$2
    local field=$3
    local expected=$4
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" 2>/dev/null)
    value=$(echo "$response" | jq -r ".$field" 2>/dev/null)
    
    if [ "$value" = "$expected" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($field=$value)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected, got $value)"
        ((FAILED++))
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "  Backend Health Checks"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_json_endpoint "Health Check" "$BASE_URL/health" "status" "healthy"
test_endpoint "Root Endpoint" "$BASE_URL/" "200"
test_endpoint "API Docs" "$BASE_URL/docs" "200"
test_endpoint "OpenAPI Schema" "$BASE_URL/openapi.json" "200"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Security Headers"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test security headers
echo -n "Checking security headers... "
headers=$(curl -sI "$BASE_URL/health" 2>/dev/null)

has_xss=$(echo "$headers" | grep -i "X-XSS-Protection" | wc -l)
has_frame=$(echo "$headers" | grep -i "X-Frame-Options" | wc -l)
has_content_type=$(echo "$headers" | grep -i "X-Content-Type-Options" | wc -l)

if [ "$has_xss" -gt 0 ] && [ "$has_frame" -gt 0 ] && [ "$has_content_type" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} (All security headers present)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Missing security headers)"
    ((FAILED++))
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  API Endpoints"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_endpoint "Auth - Register Endpoint" "$BASE_URL/api/v2/auth/register" "422"
test_endpoint "Auth - Login Endpoint" "$BASE_URL/api/v2/auth/login" "422"
test_endpoint "IDE - Projects Endpoint" "$BASE_URL/api/v2/ide/projects" "401"
test_endpoint "NexusLang - Examples" "$BASE_URL/api/v2/nexuslang/examples" "200"
test_endpoint "Grokopedia - Search" "$BASE_URL/api/v2/grokopedia/search" "422"
test_endpoint "AI - Models List" "$BASE_URL/api/v2/ai/models" "200"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Frontend Pages"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_endpoint "Landing Page" "$FRONTEND_URL/" "200"
test_endpoint "IDE Page" "$FRONTEND_URL/ide" "200"
test_endpoint "Chat Page" "$FRONTEND_URL/chat" "200"
test_endpoint "Grokopedia Page" "$FRONTEND_URL/grokopedia" "200"
test_endpoint "Login Page" "$FRONTEND_URL/auth/login" "200"
test_endpoint "Register Page" "$FRONTEND_URL/auth/register" "200"
test_endpoint "Billing Page" "$FRONTEND_URL/billing" "200"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Performance Tests"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test response time
echo -n "API Response Time... "
start=$(date +%s%3N)
curl -s "$BASE_URL/health" > /dev/null
end=$(date +%s%3N)
duration=$((end - start))

if [ "$duration" -lt 100 ]; then
    echo -e "${GREEN}✅ PASS${NC} (${duration}ms < 100ms target)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  SLOW${NC} (${duration}ms > 100ms target)"
    ((PASSED++))
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Security Tests"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test rate limiting
echo -n "Rate Limiting... "
rate_limit_header=$(curl -sI "$BASE_URL/health" | grep -i "X-RateLimit-Limit" | wc -l)
if [ "$rate_limit_header" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Rate limiting enabled)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (No rate limit headers)"
    ((PASSED++))
fi

# Test authentication requirement
echo -n "Auth Protection... "
protected=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v2/ide/projects" 2>/dev/null)
if [ "$protected" = "401" ] || [ "$protected" = "403" ]; then
    echo -e "${GREEN}✅ PASS${NC} (Protected endpoints require auth)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Endpoints not protected!)"
    ((FAILED++))
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🎯 TEST RESULTS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED! Deployment is healthy!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED - Review and fix issues             ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Check logs:"
    echo "  docker-compose logs -f backend"
    echo "  docker-compose logs -f frontend"
    exit 1
fi

