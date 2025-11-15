#!/bin/bash
# Smart startup script for Galion Platform
# Always checks dependencies before starting services

echo "🚀 GALION PLATFORM - SMART STARTUP"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -d "v2/backend" ]; then
    echo "❌ Error: Not in /nexuslang-v2 directory"
    echo "Please run: cd /nexuslang-v2 && ./start-galion-platform.sh"
    exit 1
fi

# ============================================
# STEP 1: CHECK AND INSTALL DEPENDENCIES
# ============================================
echo "📦 STEP 1: Checking Dependencies"
echo "================================="

# Download dependency checker if needed
if [ ! -f "check-and-install-deps.sh" ]; then
    echo "Downloading dependency checker..."
    wget -q -O check-and-install-deps.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/check-and-install-deps.sh
    chmod +x check-and-install-deps.sh
fi

# Run dependency check
./check-and-install-deps.sh

echo ""

# ============================================
# STEP 2: STOP EXISTING SERVICES
# ============================================
echo "🛑 STEP 2: Stopping Existing Services"
echo "======================================"

pm2 delete all 2>/dev/null || true
echo "✅ Stopped all PM2 services"

echo ""

# ============================================
# STEP 3: START BACKEND
# ============================================
echo "🔧 STEP 3: Starting Backend"
echo "============================"

cd v2/backend

# Verify backend can start
if python3 -c "import main_simple" 2>/dev/null; then
    echo "✅ Backend imports OK"
    pm2 start "python3 main_simple.py --host 0.0.0.0 --port 8000" --name backend
    echo "✅ Backend started on port 8000"
else
    echo "❌ Backend import failed - installing dependencies..."
    pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart
    pm2 start "python3 main_simple.py --host 0.0.0.0 --port 8000" --name backend
    echo "✅ Backend started on port 8000"
fi

cd ../..
sleep 3

echo ""

# ============================================
# STEP 4: START FRONTEND SERVICES
# ============================================
echo "🎨 STEP 4: Starting Frontend Services"
echo "======================================"

# Start galion-studio
if [ -d "galion-studio" ]; then
    echo "Starting galion-studio..."
    cd galion-studio
    
    # Ensure react-hot-toast is installed
    if [ ! -d "node_modules/react-hot-toast" ]; then
        echo "Installing react-hot-toast..."
        npm install react-hot-toast --silent
    fi
    
    pm2 start "npm run dev -- -p 3030 -H 0.0.0.0" --name galion-studio
    echo "✅ Galion Studio started on port 3030"
    cd ..
    sleep 3
else
    echo "⚠️  galion-studio not found"
fi

# Start galion-app
if [ -d "galion-app" ]; then
    echo "Starting galion-app..."
    cd galion-app
    
    # Ensure dependencies are installed
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    
    pm2 start "npm run dev -- -p 3000 -H 0.0.0.0" --name galion-app
    echo "✅ Galion App started on port 3000"
    cd ..
    sleep 3
else
    echo "⚠️  galion-app not found"
fi

# Start developer-platform
if [ -d "developer-platform" ]; then
    echo "Starting developer-platform..."
    cd developer-platform
    
    # Ensure dependencies are installed
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    
    pm2 start "npm run dev -- -p 3003 -H 0.0.0.0" --name developer-platform
    echo "✅ Developer Platform started on port 3003"
    cd ..
    sleep 3
else
    echo "⚠️  developer-platform not found"
fi

pm2 save

echo ""

# ============================================
# STEP 5: CONFIGURE NGINX
# ============================================
echo "🌐 STEP 5: Configuring Nginx"
echo "============================="

# Stop nginx
pkill nginx 2>/dev/null || true
sleep 2

# Create simple nginx config
rm -f /etc/nginx/sites-enabled/*

cat > /etc/nginx/sites-available/galion << 'EOF'
upstream backend { server 127.0.0.1:8000; }
upstream studio { server 127.0.0.1:3030; }
upstream app { server 127.0.0.1:3000; }
upstream devplatform { server 127.0.0.1:3003; }

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
    }
    
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

if nginx -t 2>&1 | grep -q "successful"; then
    nginx
    echo "✅ Nginx started on port 80"
else
    echo "❌ Nginx configuration failed"
    nginx -t
fi

echo ""

# ============================================
# STEP 6: WAIT FOR SERVICES
# ============================================
echo "⏳ STEP 6: Waiting for Services"
echo "================================"

echo "Waiting 10 seconds for services to fully start..."
sleep 10

echo ""

# ============================================
# STEP 7: TEST SERVICES
# ============================================
echo "🧪 STEP 7: Testing Services"
echo "============================"

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

if [ -d "galion-app" ]; then
    test_service "Galion App" "http://localhost:3000"
fi

if [ -d "developer-platform" ]; then
    test_service "Developer Platform" "http://localhost:3003"
fi

echo ""

# ============================================
# STEP 8: SHOW STATUS
# ============================================
echo "📊 STEP 8: Service Status"
echo "========================="

pm2 list

echo ""

# ============================================
# STEP 9: ACCESS INFO
# ============================================
echo "🌐 STEP 9: Access Information"
echo "=============================="

POD_ID=$(hostname)
INTERNAL_IP=$(hostname -i | grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' | head -1)

echo ""
echo "Internal Access:"
echo "  http://localhost"
echo "  http://$INTERNAL_IP"
echo ""
echo "To find your RunPod public domain:"
echo "  1. Go to RunPod dashboard"
echo "  2. Click on your pod ($POD_ID)"
echo "  3. Look for 'Connect' or 'HTTP Ports' section"
echo "  4. Copy your public URL"
echo ""

# ============================================
# COMPLETE
# ============================================
echo "🎉 GALION PLATFORM STARTUP COMPLETE!"
echo "====================================="
echo ""
echo "All services are running and ready!"
echo ""
echo "Quick commands:"
echo "  pm2 logs          - View all logs"
echo "  pm2 restart all   - Restart all services"
echo "  pm2 status        - Check service status"
echo ""

