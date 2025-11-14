#!/bin/bash
# Fix nginx proxy to route to FastAPI app

echo "🔧 Fixing nginx proxy configuration"
echo "===================================="

# Check nginx configuration
echo "1. Checking nginx status..."
systemctl status nginx 2>/dev/null || echo "nginx not managed by systemctl"

echo ""
echo "2. Checking nginx processes..."
ps aux | grep nginx | grep -v grep

echo ""
echo "3. Checking nginx config..."
ls -la /etc/nginx/ 2>/dev/null || echo "nginx config not in /etc/nginx/"

echo ""
echo "4. Current nginx config (if accessible)..."
cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/nginx.conf 2>/dev/null | head -20 || echo "Cannot access nginx config"

echo ""
echo "=========================================="
echo "OPTIONS TO FIX:"
echo ""
echo "Option 1: Configure nginx to proxy to FastAPI"
echo "Option 2: Use a different port (like 3000, 5000, 9000)"
echo "Option 3: Stop nginx and use port 80 directly"
echo ""
echo "Which option would you like to try?"
