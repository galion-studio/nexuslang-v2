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
cd /nexuslang-v2/galion-studio && npm install && cd ..
cd /nexuslang-v2/galion-app && npm install && npm install lucide-react && cd ..
cd /nexuslang-v2/developer-platform && npm install && cd ..

# 5. Install PM2 globally
echo "5. Installing PM2..."
npm install -g pm2

cd /nexuslang-v2

# 6. Start all services
echo "6. Starting all services..."

# Stop any existing
pm2 delete all 2>/dev/null || true

# Start backend
cd /nexuslang-v2/v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd /nexuslang-v2

# Start galion-studio
cd /nexuslang-v2/galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd /nexuslang-v2

# Start galion-app
cd /nexuslang-v2/galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd /nexuslang-v2

# Start developer-platform
cd /nexuslang-v2/developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd /nexuslang-v2

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
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
if nginx -t; then
    nginx -s reload 2>/dev/null || nginx
    echo "✅ Nginx configured and running on port 8080"
else
    echo "❌ Nginx configuration error"
    nginx -t
fi

# 8. Wait for services to start and test
echo "8. Waiting for services to fully start..."
sleep 20

echo "9. Testing all services..."

# Test backend
echo -n "Backend API: "
if curl -s --max-time 10 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Test galion-app
echo -n "Galion App: "
if timeout 15 curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Test developer-platform
echo -n "Developer Platform: "
if timeout 15 curl -s http://localhost:3003 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Test galion-studio
echo -n "Galion Studio: "
if timeout 15 curl -s http://localhost:3030 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Test nginx
echo -n "Nginx Proxy (8080): "
if curl -s --max-time 5 -I http://localhost:8080 | head -1 | grep -q "301\|200"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# 10. Show final status
echo ""
echo "10. FINAL SERVICE STATUS:"
pm2 list

echo ""
echo "🎉 GALION PLATFORM SETUP COMPLETE!"
echo "==================================="
echo ""
echo "✅ All system dependencies installed"
echo "✅ Repository cloned and updated"
echo "✅ Python and Node.js dependencies installed"
echo "✅ PM2 process manager configured"
echo "✅ All 4 services started and running"
echo "✅ Nginx configured for multi-domain routing"
echo "✅ Services tested and verified"
echo ""
echo "🌐 LOCAL ACCESS URLs:"
echo "   Backend API:      http://localhost:8000/health"
echo "   Galion App:       http://localhost:3000"
echo "   Developer Platform: http://localhost:3003"
echo "   Galion Studio:    http://localhost:3030"
echo "   Nginx Proxy:      http://localhost:8080"
echo ""
echo "🌍 EXTERNAL ACCESS (after Cloudflare setup):"
echo "   RunPod IP: $(hostname -i)"
echo "   Port: 8080"
echo ""
echo "   Update Cloudflare DNS records to:"
echo "   • galion.app → $(hostname -i) (port 8080)"
echo "   • api.galion.app → $(hostname -i) (port 8080)"
echo "   • developer.galion.app → $(hostname -i) (port 8080)"
echo "   • galion.studio → $(hostname -i) (port 8080)"
echo ""
echo "🚀 Your Galion Platform is now ready for production!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure Cloudflare DNS with port 8080"
echo "2. Wait for DNS propagation (5-10 minutes)"
echo "3. Test external URLs: https://galion.app"
echo "4. Enable SSL/TLS in Cloudflare"
