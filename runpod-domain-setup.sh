#!/bin/bash
# Configure Galion Platform for RunPod domain access

echo "🚀 RUNPOD DOMAIN CONFIGURATION"
echo "=============================="

# Get RunPod info
POD_ID=$(hostname | cut -d'-' -f1)
RUNPOD_IP=$(hostname -i | grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' | head -1)

echo "Pod ID: $POD_ID"
echo "RunPod IP: $RUNPOD_IP"

# 1. Fix nginx configuration
echo ""
echo "1. Fixing nginx configuration..."

pkill nginx 2>/dev/null || true
sleep 2

# Clean up corrupted config
sed -i 's/808080/8080/g' /etc/nginx/nginx.conf 2>/dev/null || true

# Create proper nginx config for RunPod
cat > /etc/nginx/sites-available/galion-runpod << 'EOF'
# Galion Platform - RunPod Domain Configuration

upstream backend_api { server localhost:8000; }
upstream galion_studio { server localhost:3030; }

# Default server - serve galion studio
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    location / {
        proxy_pass http://galion_studio;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # API routes
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
    }
}

# HTTPS redirect (if SSL is enabled)
server {
    listen 443 ssl http2;
    server_name _;

    # SSL configuration (RunPod provides SSL)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://galion_studio;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
    }
}
EOF

# Enable the config
ln -sf /etc/nginx/sites-available/galion-runpod /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/galion*

# Test and start nginx
if nginx -t; then
    nginx
    echo "✅ Nginx configured and started"
else
    echo "❌ Nginx configuration failed"
    nginx -t
fi

# 2. Test services
echo ""
echo "2. Testing services..."

echo -n "Galion Studio: "
if curl -s --max-time 5 http://localhost > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

echo -n "Backend API: "
if curl -s --max-time 5 http://localhost/health > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

# 3. Show RunPod domain info
echo ""
echo "3. RUNPOD DOMAIN ACCESS:"
echo "========================"

# Try to determine the RunPod domain
# RunPod domains typically follow: https://[pod-id]-[port].[region].runpod.net
echo "Your Galion Platform is now accessible at:"
echo ""
echo "🌐 HTTP:  http://$POD_ID-80.tcp.runpod.net"
echo "🔒 HTTPS: https://$POD_ID-443.tcp.runpod.net"
echo ""
echo "📱 Direct access:"
echo "   http://$RUNPOD_IP (if port 80 is exposed)"
echo ""
echo "🧪 Test commands:"
echo "   curl http://$POD_ID-80.tcp.runpod.net"
echo "   curl https://$POD_ID-443.tcp.runpod.net"
echo ""
echo "📋 Available endpoints:"
echo "   / - Galion Studio (main app)"
echo "   /api/ - Backend API routes"
echo "   /health - Health check"

# 4. Final status
echo ""
echo "4. SERVICE STATUS:"
pm2 list

echo ""
echo "🎉 RUNPOD DOMAIN CONFIGURATION COMPLETE!"
echo "========================================="
echo ""
echo "Your Galion Platform is now accessible via RunPod's domain system!"
echo "Share these URLs with your users:"
echo ""
echo "🌐 http://$POD_ID-80.tcp.runpod.net"
echo "🔒 https://$POD_ID-443.tcp.runpod.net"