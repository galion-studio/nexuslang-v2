#!/bin/bash
# Test Galion Platform Setup

echo "🧪 GALION PLATFORM - COMPREHENSIVE TEST"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
total_tests=0
passed_tests=0
failed_tests=0

test_passed() {
    echo -e "${GREEN}✅ $1${NC}"
    ((passed_tests++))
    ((total_tests++))
}

test_failed() {
    echo -e "${RED}❌ $1${NC}"
    ((failed_tests++))
    ((total_tests++))
}

test_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((total_tests++))
}

echo "Testing PM2 services..."
echo "----------------------"

# Test PM2 daemon
if pm2 list &>/dev/null; then
    test_passed "PM2 daemon running"
else
    test_failed "PM2 daemon not running"
fi

# Test each service
services=("backend" "galion-studio" "galion-app" "developer-platform")
for service in "${services[@]}"; do
    if pm2 describe "$service" &>/dev/null; then
        status=$(pm2 jlist | jq -r ".[] | select(.name==\"$service\") | .pm2_env.status")
        if [ "$status" = "online" ]; then
            test_passed "$service: online"
        else
            test_failed "$service: $status"
        fi
    else
        test_failed "$service: not found"
    fi
done

echo ""
echo "Testing local services..."
echo "------------------------"

# Test backend
if curl -s http://localhost:8000/health &>/dev/null; then
    test_passed "Backend API (port 8000): responding"
else
    test_failed "Backend API (port 8000): not responding"
fi

# Test galion-app
if curl -s http://localhost:3000 &>/dev/null; then
    test_passed "Galion App (port 3000): responding"
else
    test_failed "Galion App (port 3000): not responding"
fi

# Test developer-platform
if curl -s http://localhost:3003 &>/dev/null; then
    test_passed "Developer Platform (port 3003): responding"
else
    test_failed "Developer Platform (port 3003): not responding"
fi

# Test galion-studio
if curl -s http://localhost:3030 &>/dev/null; then
    test_passed "Galion Studio (port 3030): responding"
else
    test_failed "Galion Studio (port 3030): not responding"
fi

echo ""
echo "Testing Nginx..."
echo "---------------"

# Test nginx config
if nginx -t &>/dev/null; then
    test_passed "Nginx configuration: valid"
else
    test_failed "Nginx configuration: invalid"
fi

# Test port 80
if ss -tlnp | grep -q ":80 "; then
    test_passed "Nginx listening on port 80"
else
    test_failed "Nginx not listening on port 80"
fi

# Test nginx proxy
if curl -s http://localhost &>/dev/null; then
    test_passed "Nginx proxy: working"
else
    test_failed "Nginx proxy: not working"
fi

echo ""
echo "Testing external domains..."
echo "--------------------------"

# Test domains (these will fail until Cloudflare is configured)
domains=("https://galion.app" "https://api.galion.app/health" "https://developer.galion.app" "https://galion.studio")

for domain in "${domains[@]}"; do
    if curl -s --max-time 5 "$domain" &>/dev/null; then
        test_passed "$domain: reachable"
    else
        test_warning "$domain: not reachable (Cloudflare not configured?)"
    fi
done

echo ""
echo "📊 TEST SUMMARY"
echo "==============="
echo "Total tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $failed_tests"
echo "Warnings: $((total_tests - passed_tests - failed_tests))"

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Your Galion Platform is ready!"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Check the errors above and fix them."
fi

echo ""
echo "💡 NEXT STEPS:"
echo "1. Configure Cloudflare DNS records"
echo "2. Test external access to your domains"
echo "3. Monitor logs: pm2 logs"

echo ""
echo "📄 LOG FILES:"
echo "PM2 logs: pm2 logs"
echo "Nginx access: tail -f /var/log/nginx/access.log"
echo "Nginx error: tail -f /var/log/nginx/error.log"
