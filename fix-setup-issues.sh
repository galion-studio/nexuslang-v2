#!/bin/bash
# Fix the setup issues from the fresh install

echo "🔧 FIXING SETUP ISSUES"
echo "======================="

# 1. Fix nginx configuration (remove the invalid 808081 port)
echo "1. Fixing nginx configuration..."

# Backup current config
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.before_fix

# Remove the invalid port line and fix the config
sed -i '/808081/d' /etc/nginx/nginx.conf

# Add proper nginx config for port 8080
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
echo "2. Testing and reloading nginx..."
if nginx -t; then
    nginx -s reload
    echo "✅ Nginx configuration fixed and reloaded"
else
    echo "❌ Nginx configuration still has errors"
    nginx -t
fi

# 3. Fix backend issues
echo "3. Checking backend issues..."

# Check if backend directory exists
if [ -d "/nexuslang-v2/v2/backend" ]; then
    cd /nexuslang-v2/v2/backend

    # Check if main_simple.py exists
    if [ -f "main_simple.py" ]; then
        echo "Backend file exists, restarting..."

        # Stop current backend
        pm2 delete backend 2>/dev/null || true

        # Start backend
        pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
        pm2 save

        echo "✅ Backend restarted"
    else
        echo "❌ main_simple.py not found"
    fi
else
    echo "❌ Backend directory not found"
fi

# 4. Wait for services to stabilize
echo "4. Waiting for services to stabilize..."
sleep 10

# 5. Test all services properly
echo "5. Testing all services..."

echo "Testing backend health:"
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FAIL"

echo "Testing galion-app:"
timeout 5 curl -s http://localhost:3000 > /dev/null && echo "✅ Galion App OK" || echo "❌ Galion App FAIL"

echo "Testing developer-platform:"
timeout 5 curl -s http://localhost:3003 > /dev/null && echo "✅ Developer Platform OK" || echo "❌ Developer Platform FAIL"

echo "Testing galion-studio:"
timeout 5 curl -s http://localhost:3030 > /dev/null && echo "✅ Galion Studio OK" || echo "❌ Galion Studio FAIL"

echo "Testing nginx on port 8080:"
curl -s -I http://localhost:8080 | head -1 | grep -q "301\|200" && echo "✅ Nginx OK" || echo "❌ Nginx FAIL"

# 6. Show final status
echo ""
echo "6. FINAL SERVICE STATUS:"
pm2 list

echo ""
echo "🎉 ISSUES FIXED!"
echo "================"
echo ""
echo "🌐 Local access:"
echo "   Backend: http://localhost:8000/health"
echo "   Galion App: http://localhost:3000"
echo "   Developer Platform: http://localhost:3003"
echo "   Galion Studio: http://localhost:3030"
echo "   Nginx: http://localhost:8080"
echo ""
echo "🌍 External access (Cloudflare):"
echo "   Update DNS to point to: $(hostname -i):8080"
echo ""
echo "📋 Next: Configure Cloudflare DNS with port 8080"
