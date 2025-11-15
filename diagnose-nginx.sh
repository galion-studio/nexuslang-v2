#!/bin/bash

echo "🔍 GALION ECOSYSTEM - NGINX DIAGNOSTICS"
echo "======================================="

echo ""
echo "📊 Checking nginx status..."
echo ""

# Check if nginx is running
echo "1. Nginx processes:"
ps aux | grep nginx | grep -v grep
echo ""

# Check port 80 binding
echo "2. Port 80 binding:"
ss -tlnp | grep :80
echo ""

# Check nginx configuration
echo "3. Configuration test:"
sudo nginx -t 2>&1
echo ""

# Check error logs
echo "4. Recent error logs:"
sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No error logs found"
echo ""

# Test local endpoints
echo "5. Local endpoint tests:"
echo "Health endpoint:"
curl -s http://localhost/health 2>/dev/null || echo "Failed to connect"
echo ""
echo "API endpoint:"
curl -s http://localhost/api/health 2>/dev/null || echo "Failed to connect"
echo ""

# Check backend
echo "6. Backend status:"
curl -s http://localhost:8000/health 2>/dev/null || echo "Backend not responding"
echo ""

echo "✅ DIAGNOSTICS COMPLETE"
