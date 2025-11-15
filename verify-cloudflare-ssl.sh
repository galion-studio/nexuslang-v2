#!/bin/bash
# ============================================
# Verify Cloudflare SSL Configuration
# ============================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  CLOUDFLARE SSL VERIFICATION${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

DOMAINS=("api.galion.studio" "studio.galion.studio" "app.galion.studio" "dev.galion.studio")

for domain in "${DOMAINS[@]}"; do
    echo -e "${BLUE}Checking${NC} $domain"
    echo ""
    
    # DNS check
    echo -n "  DNS Resolution: "
    if nslookup $domain > /dev/null 2>&1; then
        IP=$(nslookup $domain 2>/dev/null | grep -A1 "Name:" | grep "Address" | tail -1 | awk '{print $2}')
        
        # Check if it's a Cloudflare IP (104.x.x.x or 172.x.x.x range)
        if echo "$IP" | grep -qE "^(104\.|172\.6[4-7]\.|172\.7[0-1]\.)"; then
            echo -e "${GREEN}✓ Cloudflare IP${NC} ($IP)"
        else
            echo -e "${YELLOW}⚠ Non-Cloudflare IP${NC} ($IP)"
        fi
    else
        echo -e "${RED}✗ Not resolving${NC}"
    fi
    
    # HTTPS check
    echo -n "  HTTPS Access: "
    HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "https://$domain/health" 2>/dev/null || echo "000")
    if [ "$HTTPS_CODE" = "200" ]; then
        echo -e "${GREEN}✓ HTTP $HTTPS_CODE${NC}"
    elif [ "$HTTPS_CODE" = "000" ]; then
        echo -e "${RED}✗ No response${NC}"
    else
        echo -e "${YELLOW}⚠ HTTP $HTTPS_CODE${NC}"
    fi
    
    # SSL Certificate check
    echo -n "  SSL Certificate: "
    SSL_INFO=$(echo | timeout 5 openssl s_client -connect $domain:443 -servername $domain 2>/dev/null | grep "subject=")
    if [ -n "$SSL_INFO" ]; then
        echo -e "${GREEN}✓ Valid${NC}"
    else
        echo -e "${YELLOW}⚠ Check manually${NC}"
    fi
    
    # HTTP to HTTPS redirect
    echo -n "  HTTP Redirect: "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "http://$domain" 2>/dev/null)
    if [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Working${NC}"
    else
        echo -e "${YELLOW}⚠ Not configured${NC}"
    fi
    
    echo ""
done

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  CLOUDFLARE FEATURES CHECK${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check Cloudflare headers
echo -ne "Cloudflare Proxy: "
CF_HEADER=$(curl -s -I https://api.galion.studio 2>/dev/null | grep -i "cf-ray")
if [ -n "$CF_HEADER" ]; then
    echo -e "${GREEN}✓ Active${NC}"
else
    echo -e "${YELLOW}⚠ Not detected${NC}"
fi

echo -ne "HTTPS Redirect: "
REDIRECT=$(curl -s -I http://api.galion.studio 2>/dev/null | grep -i "location: https")
if [ -n "$REDIRECT" ]; then
    echo -e "${GREEN}✓ Enabled${NC}"
else
    echo -e "${YELLOW}⚠ Not configured${NC}"
fi

echo -ne "Compression: "
COMPRESSION=$(curl -s -H "Accept-Encoding: gzip, br" -I https://api.galion.studio 2>/dev/null | grep -i "content-encoding")
if [ -n "$COMPRESSION" ]; then
    echo -e "${GREEN}✓ Enabled${NC}"
else
    echo -e "${YELLOW}⚠ Not detected${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✅ SSL Verification Complete${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

echo "If any checks failed:"
echo "1. Review CLOUDFLARE_SETUP.md"
echo "2. Check Cloudflare dashboard DNS settings"
echo "3. Wait for DNS propagation (2-10 minutes)"
echo "4. Ensure 'Proxy' is enabled (orange cloud)"
echo "5. Verify SSL mode is set to 'Full'"
echo ""

