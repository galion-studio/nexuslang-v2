#!/bin/bash
# Complete fix for all issues - backend, frontend, nginx, dependencies

echo "🚨 FIX ALL ISSUES - COMPREHENSIVE REPAIR"
echo "========================================="
echo ""

# Ensure we're in the right directory
if [ ! -d "v2/backend" ]; then
    echo "❌ Not in /nexuslang-v2 directory"
    echo "Run: cd /nexuslang-v2 && bash fix-all-issues-now.sh"
    exit 1
fi

# ============================================
# STEP 1: STOP EVERYTHING
# ============================================
echo "1️⃣  STOPPING ALL SERVICES"
echo "========================="

pm2 kill 2>/dev/null || true
pkill -9 nginx 2>/dev/null || true
pkill -f "main_simple.py" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

sleep 2
echo "✅ All services stopped"
echo ""

# ============================================
# STEP 2: INSTALL ALL DEPENDENCIES
# ============================================
echo "2️⃣  INSTALLING DEPENDENCIES"
echo "============================"

# Python backend
echo "Installing Python dependencies..."
pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart
echo "✅ Python dependencies installed"

# Galion Studio
if [ -d "galion-studio" ]; then
    echo "Installing galion-studio dependencies..."
    cd galion-studio
    npm install --silent 2>/dev/null || npm install
    npm install react-hot-toast lucide-react clsx tailwind-merge --silent 2>/dev/null || true
    cd ..
    echo "✅ Galion Studio dependencies installed"
fi

echo ""

# ============================================
# STEP 3: FIX NGINX CONFIGURATION
# ============================================
echo "3️⃣  FIXING NGINX CONFIGURATION"
echo "==============================="

# Remove all broken configs
rm -f /etc/nginx/sites-enabled/* 2>/dev/null || true

# Create clean nginx.conf
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
    
    include /etc/nginx/sites-enabled/*;
}
NGINXCONF

# Create working site config
cat > /etc/nginx/sites-available/galion << 'SITECONF'
upstream backend { server 127.0.0.1:8000; }
upstream studio { server 127.0.0.1:3030; }

server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://studio;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
SITECONF

ln -s /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/

if nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx configuration fixed"
else
    echo "❌ Nginx configuration failed:"
    nginx -t
fi

echo ""

# ============================================
# STEP 4: START BACKEND
# ============================================
echo "4️⃣  STARTING BACKEND"
echo "===================="

cd v2/backend

# Test imports
echo "Testing backend imports..."
python3 << 'PYTEST'
try:
    import fastapi, uvicorn, psutil, pydantic
    from starlette.middleware.cors import CORSMiddleware
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)
PYTEST

if [ $? -eq 0 ]; then
    # Start with PM2
    pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
    echo "✅ Backend started"
else
    echo "❌ Backend imports failed"
    exit 1
fi

cd ../..
sleep 5

echo ""

# ============================================
# STEP 5: START GALION STUDIO
# ============================================
echo "5️⃣  STARTING GALION STUDIO"
echo "==========================="

if [ -d "galion-studio" ]; then
    cd galion-studio
    pm2 start npm --name galion-studio -- run dev -- -p 3030 -H 0.0.0.0
    echo "✅ Galion Studio started"
    cd ..
    sleep 5
else
    echo "⚠️  galion-studio directory not found"
fi

echo ""

# ============================================
# STEP 6: START NGINX
# ============================================
echo "6️⃣  STARTING NGINX"
echo "=================="

nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx started"
else
    echo "❌ Nginx failed to start"
fi

echo ""

# ============================================
# STEP 7: SAVE PM2 STATE
# ============================================
pm2 save

# ============================================
# STEP 8: WAIT AND TEST
# ============================================
echo "7️⃣  TESTING SERVICES"
echo "===================="

echo "Waiting 10 seconds for services to fully start..."
sleep 10

test_service() {
    local name=$1
    local url=$2
    echo -n "Testing $name... "
    if curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo "✅ WORKING"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

test_service "Backend" "http://localhost:8000/health"
test_service "Galion Studio" "http://localhost:3030"
test_service "Nginx" "http://localhost"

echo ""

# ============================================
# STEP 9: SHOW STATUS
# ============================================
echo "8️⃣  SERVICE STATUS"
echo "=================="

pm2 list

echo ""
echo "Nginx processes:"
ps aux | grep nginx | grep -v grep

echo ""

# ============================================
# STEP 10: CHECK LOGS FOR ERRORS
# ============================================
echo "9️⃣  CHECKING FOR ERRORS"
echo "======================="

echo ""
echo "Backend logs (last 10 lines):"
pm2 logs backend --lines 10 --nostream 2>&1 | tail -10

echo ""
echo "Galion Studio logs (last 10 lines):"
pm2 logs galion-studio --lines 10 --nostream 2>&1 | tail -10

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo "🎉 FIX COMPLETE!"
echo "================"
echo ""

# Count online services
ONLINE_COUNT=$(pm2 list | grep -c "online")

if [ $ONLINE_COUNT -ge 2 ]; then
    echo "✅ SUCCESS! $ONLINE_COUNT services are online"
    echo ""
    echo "Your Galion Platform is ready!"
    echo ""
    echo "Access via:"
    echo "  - http://localhost (Nginx → Galion Studio)"
    echo "  - http://localhost:3030 (Galion Studio direct)"
    echo "  - http://localhost:8000/health (Backend health)"
    echo ""
    echo "Find your RunPod public URL in the dashboard!"
else
    echo "⚠️  Only $ONLINE_COUNT services online"
    echo ""
    echo "Check logs with:"
    echo "  pm2 logs backend"
    echo "  pm2 logs galion-studio"
    echo ""
    echo "Try restarting:"
    echo "  pm2 restart all"
fi

echo ""
echo "Quick commands:"
echo "  pm2 list          - Check status"
echo "  pm2 logs          - View all logs"
echo "  pm2 restart all   - Restart services"
echo ""

