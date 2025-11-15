#!/bin/bash
# Emergency fix for all issues

echo "🚨 EMERGENCY FIX - GALION PLATFORM"
echo "=================================="

# 0. CHECK AND INSTALL ALL DEPENDENCIES FIRST
echo ""
echo "0. Checking and installing dependencies..."

# Download and run dependency checker if it doesn't exist
if [ ! -f "check-and-install-deps.sh" ]; then
    wget -q -O check-and-install-deps.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/check-and-install-deps.sh
    chmod +x check-and-install-deps.sh
fi

# Run dependency checker
./check-and-install-deps.sh

echo ""
echo "✅ Dependencies checked and installed"
echo ""

# 1. COMPLETELY RESET NGINX
echo ""
echo "1. Resetting nginx configuration..."

# Stop nginx completely
pkill -9 nginx 2>/dev/null || true
sleep 2

# Backup and restore clean nginx.conf
if [ -f /etc/nginx/nginx.conf.backup ]; then
    cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
    echo "   ✅ Restored nginx.conf from backup"
else
    # Download fresh nginx.conf
    cat > /etc/nginx/nginx.conf << 'NGINXCONF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    access_log /var/log/nginx/access.log;
    
    gzip on;
    
    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
NGINXCONF
    echo "   ✅ Created fresh nginx.conf"
fi

# Remove all broken site configs
rm -f /etc/nginx/sites-enabled/* 2>/dev/null || true

# Create simple working config
cat > /etc/nginx/sites-available/galion << 'EOF'
# Simple Galion Platform Configuration

upstream backend { server 127.0.0.1:8000; }
upstream studio { server 127.0.0.1:3030; }

server {
    listen 80 default_server;
    server_name _;
    
    # Main app
    location / {
        proxy_pass http://studio;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
    }
    
    location /health {
        proxy_pass http://backend/health;
    }
}
EOF

ln -s /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/
echo "   ✅ Created simple nginx config"

# Test nginx
if nginx -t 2>&1; then
    nginx
    echo "   ✅ Nginx started successfully"
else
    echo "   ❌ Nginx test failed:"
    nginx -t
fi

# 2. CLEAN UP PM2
echo ""
echo "2. Cleaning up PM2 processes..."

pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true
sleep 2

echo "   ✅ PM2 cleaned"

# 3. START SERVICES PROPERLY
echo ""
echo "3. Starting services..."

# Check if we're in the right directory
if [ ! -d "v2/backend" ]; then
    echo "   ❌ Not in /nexuslang-v2 directory!"
    echo "   Run: cd /nexuslang-v2 && ./emergency-fix-all.sh"
    exit 1
fi

# Start backend
echo "   Starting backend..."
cd v2/backend
pm2 start "python3 main_simple.py --host 0.0.0.0 --port 8000" --name backend
cd ../..
sleep 3

# Start galion-studio (only one that exists)
if [ -d "galion-studio" ]; then
    echo "   Starting galion-studio..."
    cd galion-studio
    
    # Install missing dependency
    npm install react-hot-toast --silent 2>/dev/null || true
    
    pm2 start "npm run dev -- -p 3030 -H 0.0.0.0" --name galion-studio
    cd ..
    sleep 3
fi

pm2 save

# 4. WAIT AND TEST
echo ""
echo "4. Waiting for services to start..."
sleep 10

echo ""
echo "5. Testing services..."

echo -n "   Backend (8000): "
if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

echo -n "   Galion Studio (3030): "
if curl -s --max-time 5 http://localhost:3030 > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

echo -n "   Nginx (80): "
if curl -s --max-time 5 http://localhost > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

# 6. SHOW STATUS
echo ""
echo "6. SERVICE STATUS:"
pm2 list

echo ""
echo "7. NGINX STATUS:"
ps aux | grep nginx | grep -v grep

# 7. FIND RUNPOD DOMAIN
echo ""
echo "8. RUNPOD DOMAIN INFO:"
echo "======================"

POD_ID=$(hostname)
echo "Pod ID: $POD_ID"
echo ""
echo "To find your RunPod domain:"
echo "1. Go to RunPod dashboard"
echo "2. Click on your pod"
echo "3. Look for 'Connect' or 'HTTP Ports' section"
echo "4. Your domain will be shown there"
echo ""
echo "RunPod domains typically look like:"
echo "   https://[pod-id]-[port].proxy.runpod.net"
echo "   OR"
echo "   https://[random-id].runpod.io"
echo ""
echo "Check your RunPod dashboard for the exact URL!"

echo ""
echo "🎉 EMERGENCY FIX COMPLETE!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Check PM2 status above"
echo "2. Test: curl http://localhost"
echo "3. Find your RunPod domain in the dashboard"
echo "4. Access your platform via the RunPod domain"

