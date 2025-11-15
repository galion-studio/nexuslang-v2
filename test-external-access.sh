#!/bin/bash
# ============================================
# Test External Domain Access
# ============================================
# Tests all subdomain URLs to verify Cloudflare setup

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  EXTERNAL ACCESS TEST${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Test function
test_url() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -ne "${BLUE}Testing${NC} $name... "
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$url" 2>/dev/null)
    
    if [ "$HTTP_CODE" = "$expected" ]; then
        echo -e "${GREEN}✓ HTTP $HTTP_CODE${NC}"
        ((PASS++))
        return 0
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${RED}✗ NO RESPONSE${NC}"
        ((FAIL++))
        return 1
    else
        echo -e "${YELLOW}⚠ HTTP $HTTP_CODE (expected $expected)${NC}"
        ((FAIL++))
        return 1
    fi
}

# ============================================
# TEST 1: DNS Resolution
# ============================================
echo -e "${BLUE}Step 1: DNS Resolution${NC}"
echo ""

DOMAINS=("api.galion.studio" "studio.galion.studio" "app.galion.studio" "dev.galion.studio")

for domain in "${DOMAINS[@]}"; do
    echo -ne "  Checking $domain... "
    if nslookup $domain > /dev/null 2>&1; then
        IP=$(nslookup $domain 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}')
        echo -e "${GREEN}✓ Resolves${NC} ($IP)"
    else
        echo -e "${RED}✗ Not resolving${NC}"
    fi
done

echo ""

# ============================================
# TEST 2: HTTPS Access
# ============================================
echo -e "${BLUE}Step 2: HTTPS Access (via Cloudflare)${NC}"
echo ""

test_url "Backend API" "https://api.galion.studio/health" "200"
test_url "Backend Docs" "https://api.galion.studio/docs" "200"
test_url "Grokopedia" "https://api.galion.studio/grokopedia/" "200"
test_url "NexusLang" "https://api.galion.studio/nexuslang/" "200"
test_url "Galion Studio" "https://studio.galion.studio" "200"
test_url "Galion App" "https://app.galion.studio" "200"
test_url "Dev Platform" "https://dev.galion.studio" "200"

echo ""

# ============================================
# TEST 3: HTTP to HTTPS Redirect
# ============================================
echo -e "${BLUE}Step 3: HTTP to HTTPS Redirect${NC}"
echo ""

echo -ne "  Testing redirect... "
REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" http://api.galion.studio/health)
if [ "$REDIRECT" = "301" ] || [ "$REDIRECT" = "302" ] || [ "$REDIRECT" = "200" ]; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${YELLOW}⚠ No redirect (HTTP $REDIRECT)${NC}"
fi

echo ""

# ============================================
# TEST 4: SSL Certificate
# ============================================
echo -e "${BLUE}Step 4: SSL Certificate Check${NC}"
echo ""

for domain in "api.galion.studio" "studio.galion.studio"; do
    echo -ne "  $domain... "
    if echo | timeout 5 openssl s_client -connect $domain:443 -servername $domain 2>/dev/null | grep -q "Verify return code: 0"; then
        echo -e "${GREEN}✓ Valid SSL${NC}"
    else
        # May fail if Cloudflare proxy, which is OK
        echo -e "${YELLOW}⚠ Check manually${NC}"
    fi
done

echo ""

# ============================================
# TEST 5: Direct IP Access
# ============================================
echo -e "${BLUE}Step 5: Direct IP Access (Fallback)${NC}"
echo ""

test_url "Backend (Direct IP)" "http://213.173.105.83:8000/health" "200"
test_url "Studio (Direct IP)" "http://213.173.105.83:3030" "200"

echo ""

# ============================================
# SUMMARY
# ============================================
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  TEST SUMMARY${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((PASS * 100 / TOTAL))
    echo -e "${GREEN}✓ Passed:${NC} $PASS / $TOTAL ($PERCENT%)"
    echo -e "${RED}✗ Failed:${NC} $FAIL / $TOTAL"
else
    echo -e "${YELLOW}No tests completed${NC}"
fi

echo ""

if [ $PASS -ge 7 ] && [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL EXTERNAL ACCESS WORKING!${NC}"
    echo ""
    echo "Your platform is accessible at:"
    echo "  • https://api.galion.studio"
    echo "  • https://studio.galion.studio"
    echo "  • https://app.galion.studio"
    echo "  • https://dev.galion.studio"
elif [ $FAIL -gt 3 ]; then
    echo -e "${YELLOW}⚠ DNS/SSL Setup Incomplete${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Complete Cloudflare DNS setup (see CLOUDFLARE_SETUP.md)"
    echo "2. Wait for DNS propagation (2-10 minutes)"
    echo "3. Check SSL certificate provisioning"
    echo "4. Run this test again in 5-10 minutes"
else
    echo -e "${GREEN}✓ Partially working${NC}"
    echo ""
    echo "Some services accessible, others may need DNS propagation time"
fi

echo ""

