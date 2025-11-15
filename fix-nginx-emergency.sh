#!/bin/bash
# Emergency nginx fix for 808081 port error

echo "🚨 EMERGENCY NGINX FIX"
echo "======================="

# Stop nginx
pkill nginx 2>/dev/null || true

# Check current nginx config
echo "Current nginx.conf around line 65:"
sed -n '60,70p' /etc/nginx/nginx.conf

# Fix the invalid port
echo ""
echo "Fixing invalid port..."
sed -i 's/808081/8080/g' /etc/nginx/nginx.conf

# Verify the fix
echo "After fix:"
sed -n '60,70p' /etc/nginx/nginx.conf

# Test nginx config
echo ""
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx config is now valid"

    # Start nginx
    nginx
    echo "✅ Nginx started successfully"

    # Test port 8080
    sleep 2
    if curl -s -I http://localhost:8080 | head -1 | grep -q "301\|200"; then
        echo "✅ Nginx responding on port 8080"
    else
        echo "❌ Nginx not responding on port 8080"
    fi

else
    echo "❌ Nginx config still invalid"
    nginx -t
fi

echo ""
echo "======================="
echo "Emergency fix complete"
