#!/bin/bash
# Complete fresh setup for RunPod container

echo "🚀 GALION PLATFORM - FRESH RUNPOD SETUP"
echo "========================================"

# 1. Clone the repository
echo "1. Cloning repository..."
git clone https://github.com/galion-studio/nexuslang-v2.git /nexuslang-v2
cd /nexuslang-v2

# 2. Install system dependencies
echo "2. Installing system packages..."
apt update && apt install -y python3-pip nodejs npm nginx

# 3. Install Python dependencies
echo "3. Installing Python dependencies..."
pip3 install fastapi uvicorn psutil pydantic python-multipart

# 4. Install Node.js dependencies
echo "4. Installing Node.js dependencies..."
cd galion-studio && npm install && cd ..
cd galion-app && npm install && npm install lucide-react && cd ..
cd developer-platform && npm install && cd ..

# 5. Install PM2 globally
echo "5. Installing PM2..."
npm install -g pm2

cd /nexuslang-v2

# 6. Start all services
echo "6. Starting all services..."

# Stop any existing
pm2 delete all 2>/dev/null || true

# Start backend
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Start galion-studio
cd galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd ..

# Start galion-app
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ..

# Start developer-platform
cd developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ..

# Save PM2 config
pm2 save

# 7. Configure Nginx for port 8080 (since port 80 is blocked)
echo "7. Configuring Nginx for port 8080..."

# Create fresh nginx config
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

# Enable the site
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t && nginx -s reload

# 8. Test all services
echo "8. Testing all services..."

echo "Testing backend..."
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FAIL"

echo "Testing galion-app..."
curl -s http://localhost:3000 && echo "✅ Galion App OK" || echo "❌ Galion App FAIL"

echo "Testing developer-platform..."
curl -s http://localhost:3003 && echo "✅ Developer Platform OK" || echo "❌ Developer Platform FAIL"

echo "Testing galion-studio..."
curl -s http://localhost:3030 && echo "✅ Galion Studio OK" || echo "❌ Galion Studio FAIL"

echo "Testing nginx on port 8080..."
curl -s -I http://localhost:8080 | head -1 | grep -q "301\|200" && echo "✅ Nginx OK" || echo "❌ Nginx FAIL"

# 9. Show status
echo "9. Service Status:"
pm2 list

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "🌐 Your services are running on:"
echo "   Backend API: http://localhost:8000"
echo "   Galion App: http://localhost:3000"
echo "   Developer Platform: http://localhost:3003"
echo "   Galion Studio: http://localhost:3030"
echo "   Nginx Proxy: http://localhost:8080"
echo ""
echo "🌍 External access (after Cloudflare setup):"
echo "   https://galion.app → port 8080"
echo "   https://api.galion.app/health → port 8080"
echo "   https://developer.galion.app → port 8080"
echo ""
echo "📋 Next: Update Cloudflare DNS to point to your RunPod IP + port 8080"
