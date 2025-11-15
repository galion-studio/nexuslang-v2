#!/bin/bash
# Diagnose HTTP 521 errors from Cloudflare

echo "🔍 DIAGNOSING CLOUDFLARE HTTP 521 ERRORS"
echo "=========================================="

echo "HTTP 521 means: Cloudflare can reach server, but server isn't responding"
echo ""

# Check if nginx is running
echo "1. Checking nginx status..."
if pgrep nginx > /dev/null; then
    echo "✅ Nginx process is running"
else
    echo "❌ Nginx process is NOT running"
fi

# Check if port 80 is listening
echo ""
echo "2. Checking port 80..."
if ss -tlnp | grep -q ":80 "; then
    echo "✅ Port 80 is listening:"
    ss -tlnp | grep ":80 "
else
    echo "❌ Port 80 is NOT listening"
fi

# Test local nginx
echo ""
echo "3. Testing local nginx..."
if curl -s -I http://localhost | head -1 | grep -q "200\|404\|301"; then
    echo "✅ Local nginx responds:"
    curl -s -I http://localhost | head -3
else
    echo "❌ Local nginx does NOT respond"
    curl -v http://localhost 2>&1 | head -10
fi

# Check nginx configuration
echo ""
echo "4. Testing nginx configuration..."
if nginx -t 2>/dev/null; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration is INVALID"
    nginx -t
fi

# Check nginx error logs
echo ""
echo "5. Checking nginx error logs..."
if [ -f /var/log/nginx/error.log ]; then
    echo "Last 5 lines of nginx error log:"
    tail -5 /var/log/nginx/error.log
else
    echo "No nginx error log found"
fi

# Check if ports are exposed in RunPod
echo ""
echo "6. Checking RunPod port exposure..."
echo "RunPod IP: $(hostname -i)"
echo ""
echo "Make sure these ports are exposed in RunPod settings:"
echo "  - Port 80 (HTTP) - for nginx"
echo "  - Port 443 (HTTPS) - handled by Cloudflare"
echo ""
echo "Check RunPod dashboard → Your pod → Settings → Exposed Ports"

# Test direct IP access (bypass Cloudflare)
echo ""
echo "7. Testing direct IP access (bypasses Cloudflare)..."
DIRECT_IP=$(hostname -i)
echo "Testing: http://$DIRECT_IP"
if curl -s -I http://$DIRECT_IP | head -1 | grep -q "200\|404\|301"; then
    echo "✅ Direct IP access works - RunPod port 80 is exposed"
else
    echo "❌ Direct IP access fails - Port 80 may not be exposed in RunPod"
fi

# Check PM2 services
echo ""
echo "8. Checking PM2 services..."
pm2 list | tail -n +4  # Skip header

# Test individual services locally
echo ""
echo "9. Testing individual services locally..."
services=("8000:Backend" "3000:Galion App" "3003:Developer Platform" "3030:Galion Studio")
for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo "✅ $name (port $port): responding"
    else
        echo "❌ $name (port $port): NOT responding"
    fi
done

echo ""
echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="
echo ""
echo "If port 80 is not listening:"
echo "  - Check nginx is running: pgrep nginx"
echo "  - Restart nginx: pkill nginx && nginx"
echo ""
echo "If local nginx doesn't respond:"
echo "  - Check nginx config: nginx -t"
echo "  - View config: cat /etc/nginx/nginx.conf"
echo ""
echo "If direct IP access fails:"
echo "  - Port 80 is NOT exposed in RunPod settings"
echo "  - Go to RunPod dashboard → Your pod → Settings → Exposed Ports"
echo "  - Add port 80 as TCP"
echo ""
echo "If everything works locally but Cloudflare gives 521:"
echo "  - Wait for DNS propagation (up to 10 minutes)"
echo "  - Check Cloudflare DNS records are correct"
echo "  - Verify proxy status is enabled (orange cloud)"
