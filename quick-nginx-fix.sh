#!/bin/bash
# Quick fix for nginx configuration issue

echo "🔧 Quick Nginx Fix for RunPod"
echo "============================="

# Remove the problematic config file
echo "Removing old config file..."
rm -f /etc/nginx/sites-enabled/galion-platform

# Remove any include lines that were added
echo "Cleaning up nginx.conf..."
sed -i '/include \/etc\/nginx\/sites-enabled\/\*/d' /etc/nginx/nginx.conf

# Test nginx
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✅ Configuration is valid"
    echo "Starting nginx..."
    pkill -9 nginx 2>/dev/null || true
    nginx
    echo "✅ Nginx started successfully"

    # Test port 80
    sleep 2
    if ss -tlnp | grep -q ":80 "; then
        echo "✅ Nginx listening on port 80"
    else
        echo "❌ Nginx not listening on port 80"
    fi

    # Test localhost
    if curl -s http://localhost &>/dev/null; then
        echo "✅ Local nginx proxy working"
    else
        echo "❌ Local nginx proxy not working"
    fi

else
    echo "❌ Configuration still invalid"
    echo "Checking nginx.conf..."
    tail -20 /etc/nginx/nginx.conf
fi

echo "============================="
echo "Quick fix complete"
echo "============================="
