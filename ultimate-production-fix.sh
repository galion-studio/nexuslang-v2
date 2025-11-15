#!/bin/bash
# Ultimate Production Fix - Works from any state

set -e

echo "🚀 ULTIMATE PRODUCTION FIX"
echo "=========================="
echo ""

# Go to the right directory
cd /nexuslang-v2 2>/dev/null || cd /workspace 2>/dev/null || { echo "Cannot find project directory"; exit 1; }

echo "Working directory: $(pwd)"
echo ""

# ============================================
# STEP 1: PULL LATEST CODE
# ============================================
echo "1️⃣  Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/clean-nexuslang
echo "✅ Code updated"
echo ""

# ============================================
# STEP 2: VERIFY FILES EXIST
# ============================================
echo "2️⃣  Verifying files..."

if [ ! -f "v2/backend/main_simple.py" ]; then
    echo "❌ main_simple.py still missing after git pull"
    echo "Checking what we have..."
    ls -la v2/backend/ | head -20
    exit 1
fi

echo "✅ All files present"
echo ""

# ============================================
# STEP 3: STOP EVERYTHING
# ============================================
echo "3️⃣  Stopping services..."
pm2 kill 2>/dev/null || true
pkill -9 nginx 2>/dev/null || true
sleep 2
echo "✅ Services stopped"
echo ""

# ============================================
# STEP 4: INSTALL DEPENDENCIES
# ============================================
echo "4️⃣  Installing dependencies..."

pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart 2>&1 | grep -v "Requirement already satisfied" || true

if [ -d "galion-studio" ]; then
    cd galion-studio
    npm install --silent 2>&1 | tail -1
    npm install react-hot-toast lucide-react --silent 2>&1 | tail -1
    cd ..
fi

echo "✅ Dependencies installed"
echo ""

# ============================================
# STEP 5: CREATE PM2 ECOSYSTEM
# ============================================
echo "5️⃣  Creating PM2 ecosystem..."

cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'backend',
      script: 'python3',
      args: 'main_simple.py --host 0.0.0.0 --port 8000',
      cwd: '/nexuslang-v2/v2/backend',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'galion-studio',
      script: 'npm',
      args: 'run dev -- -p 3030 -H 0.0.0.0',
      cwd: '/nexuslang-v2/galion-studio',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PORT: '3030'
      }
    }
  ]
};
EOF

echo "✅ Ecosystem created"
echo ""

# ============================================
# STEP 6: CONFIGURE NGINX
# ============================================
echo "6️⃣  Configuring Nginx..."

rm -f /etc/nginx/sites-enabled/*

cat > /etc/nginx/nginx.conf << 'NGINXCONF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100M;
    
    gzip on;
    
    include /etc/nginx/sites-enabled/*;
}
NGINXCONF

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
    }
    
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
    }
    
    location /health {
        proxy_pass http://backend/health;
    }
}
SITECONF

ln -s /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/

nginx -t && echo "✅ Nginx configured" || { echo "❌ Nginx config failed"; exit 1; }
echo ""

# ============================================
# STEP 7: START SERVICES
# ============================================
echo "7️⃣  Starting services..."

pm2 start ecosystem.config.js
sleep 5

nginx

pm2 save

echo "✅ Services started"
echo ""

# ============================================
# STEP 8: WAIT AND TEST
# ============================================
echo "8️⃣  Testing services..."
sleep 10

echo -n "Backend: "
curl -sf http://localhost:8000/health > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Studio: "
curl -sf http://localhost:3030 > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Nginx: "
curl -sf http://localhost > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo ""

# ============================================
# STEP 9: SHOW STATUS
# ============================================
echo "9️⃣  Status:"
pm2 list

echo ""
echo "🎉 SETUP COMPLETE!"
echo ""
echo "Access: http://localhost"
echo "API: http://localhost:8000/health"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Commands:"
echo "  pm2 logs          - View logs"
echo "  pm2 restart all   - Restart services"
echo ""

