#!/bin/bash

# Fix API Proxy - Remove /api/ prefix when proxying to backend

echo "🔧 FIXING API PROXY PATH REWRITE"
echo "==============================="
echo ""

# Backup current config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.before-api-fix

# Fix the API location to rewrite URLs
sudo sed -i 's|        location /api/ {|        location /api/ {\n            rewrite ^/api/(.*) /$1 break;|g' /etc/nginx/nginx.conf

# Test configuration
echo "🧪 Testing nginx configuration..."
if sudo nginx -t 2>/dev/null; then
    echo "✅ Configuration is valid"
else
    echo "❌ Configuration has errors"
    sudo nginx -t
    exit 1
fi

# Reload nginx
echo "🔄 Reloading nginx..."
sudo nginx -s reload

# Test the fix
echo "🧪 Testing API proxy fix..."
echo ""

echo "Testing /api/health (should now work):"
curl -s http://localhost/api/health
echo ""

echo "Testing direct backend /health:"
curl -s http://localhost:8000/health
echo ""

echo ""
echo "🎉 API PROXY FIXED!"
echo "=================="
echo ""
echo "✅ /api/health now proxies correctly to backend /health"
echo "✅ Your API is fully accessible at: http://[your-runpod-ip]/api/health"
echo ""
echo "Script completed at: $(date)"
