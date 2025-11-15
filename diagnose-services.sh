#!/bin/bash
# Diagnose service issues

echo "🔍 DIAGNOSING SERVICE ISSUES"
echo "============================"

# Check PM2 services
echo "PM2 Services:"
pm2 list

echo ""
echo "Checking ports..."

# Check what ports are actually listening
echo "Listening ports:"
ss -tlnp | grep -E ":(3000|3003|3030|8000) "

echo ""
echo "Testing services directly..."

# Test backend
echo -n "Backend (8000): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health && echo "OK" || echo "FAIL"

# Test galion-app
echo -n "Galion App (3000): "
timeout 5 curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 && echo "OK" || echo "FAIL/TIMEOUT"

# Test developer-platform
echo -n "Developer Platform (3003): "
timeout 5 curl -s -o /dev/null -w "%{http_code}" http://localhost:3003 && echo "OK" || echo "FAIL/TIMEOUT"

# Test galion-studio
echo -n "Galion Studio (3030): "
timeout 5 curl -s -o /dev/null -w "%{http_code}" http://localhost:3030 && echo "OK" || echo "FAIL/TIMEOUT"

echo ""
echo "Checking PM2 logs..."

# Check recent logs for each service
for service in backend galion-app developer-platform galion-studio; do
    echo ""
    echo "Last 5 lines of $service logs:"
    pm2 logs $service --lines 5 --nostream 2>/dev/null || echo "No logs available"
done

echo ""
echo "Checking if services are actually running..."

# Check processes
ps aux | grep -E "(node|python)" | grep -v grep

echo ""
echo "Checking nginx proxy..."
curl -s -I http://localhost | head -5
