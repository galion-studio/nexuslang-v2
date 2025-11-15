#!/bin/bash
# Manual step-by-step setup to avoid all script errors

echo "🔧 MANUAL GALION PLATFORM SETUP"
echo "==============================="

# Step 1: Check if repo exists
if [ ! -d "/nexuslang-v2" ]; then
    echo "❌ Repository not found. Cloning..."
    git clone https://github.com/galion-studio/nexuslang-v2.git /nexuslang-v2
    cd /nexuslang-v2
    git pull origin clean-nexuslang
else
    echo "✅ Repository exists"
    cd /nexuslang-v2
    git pull origin clean-nexuslang
fi

# Step 2: Check directories
echo ""
echo "Checking directories..."
ls -la /nexuslang-v2/ | grep -E "(galion|developer|v2)"

if [ ! -d "/nexuslang-v2/galion-app" ]; then
    echo "❌ galion-app directory missing"
    exit 1
fi

if [ ! -d "/nexuslang-v2/developer-platform" ]; then
    echo "❌ developer-platform directory missing"
    exit 1
fi

if [ ! -d "/nexuslang-v2/v2/backend" ]; then
    echo "❌ backend directory missing"
    exit 1
fi

echo "✅ All directories exist"

# Step 3: Install dependencies
echo ""
echo "Installing dependencies..."

# Python
pip3 install fastapi uvicorn psutil pydantic python-multipart

# Node.js apps
echo "Installing galion-app dependencies..."
cd /nexuslang-v2/galion-app && npm install && npm install lucide-react

echo "Installing developer-platform dependencies..."
cd /nexuslang-v2/developer-platform && npm install

echo "Installing galion-studio dependencies..."
cd /nexuslang-v2/galion-studio && npm install

# PM2
npm install -g pm2

# Step 4: Start services
echo ""
echo "Starting services..."

cd /nexuslang-v2

# Clean start
pm2 delete all 2>/dev/null || true

# Backend
echo "Starting backend..."
cd /nexuslang-v2/v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd /nexuslang-v2

# Galion Studio
echo "Starting galion-studio..."
cd /nexuslang-v2/galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd /nexuslang-v2

# Galion App
echo "Starting galion-app..."
cd /nexuslang-v2/galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd /nexuslang-v2

# Developer Platform
echo "Starting developer-platform..."
cd /nexuslang-v2/developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd /nexuslang-v2

pm2 save

# Step 5: Fix nginx
echo ""
echo "Fixing nginx..."

# Stop nginx
pkill nginx 2>/dev/null || true

# Create clean config
cat > /etc/nginx/sites-available/galion-platform << 'EOF'
# Galion Platform - Multi-Domain Nginx Routing
# Using port 8080 since port 80 is blocked by RunPod

# Upstream backend services
upstream backend_api {
    server localhost:8000;
}

upstream galion_app {
    server localhost:3000;
}

upstream developer_platform {
    server localhost:3003;
}

upstream galion_studio {
    server localhost:3030;
}

# galion.studio domain (redirects to galion.app)
server {
    listen 8080;
    server_name galion.studio www.galion.studio;
    return 301 https://galion.app$request_uri;
}

# galion.app main domain
server {
    listen 8080;
    server_name galion.app www.galion.app;

    location / {
        proxy_pass http://galion_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /_next/static {
        proxy_pass http://galion_app;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}

# api.galion.app subdomain
server {
    listen 8080;
    server_name api.galion.app;

    client_max_body_size 100M;
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    location / {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;
        proxy_set_header CF-RAY $http_cf_ray;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /docs {
        proxy_pass http://backend_api/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
    }
}

# developer.galion.app subdomain
server {
    listen 8080;
    server_name developer.galion.app;

    location / {
        proxy_pass http://developer_platform;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /_next/static {
        proxy_pass http://developer_platform;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default

# Start nginx
if nginx -t; then
    nginx
    echo "✅ Nginx configured and started on port 8080"
else
    echo "❌ Nginx config error"
    nginx -t
fi

# Step 6: Test everything
echo ""
echo "Testing services..."
sleep 15

echo -n "Backend: "
curl -s --max-time 5 http://localhost:8000/health > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Galion App: "
timeout 10 curl -s http://localhost:3000 > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Developer Platform: "
timeout 10 curl -s http://localhost:3003 > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Galion Studio: "
timeout 10 curl -s http://localhost:3030 > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "Nginx: "
curl -s --max-time 5 -I http://localhost:8080 | head -1 | grep -q "301\|200" && echo "✅ OK" || echo "❌ FAIL"

echo ""
echo "Service Status:"
pm2 list

echo ""
echo "🎉 MANUAL SETUP COMPLETE!"
echo "========================"
echo ""
echo "🌐 Local URLs:"
echo "   Backend: http://localhost:8000/health"
echo "   Galion App: http://localhost:3000"
echo "   Developer Platform: http://localhost:3003"
echo "   Galion Studio: http://localhost:3030"
echo "   Nginx: http://localhost:8080"
echo ""
echo "🌍 External Setup:"
echo "   RunPod IP: $(hostname -i)"
echo "   Configure Cloudflare DNS → $(hostname -i):8080"
