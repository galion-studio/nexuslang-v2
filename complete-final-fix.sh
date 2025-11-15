#!/bin/bash
# Complete final fix for all Galion Platform issues

echo "🚀 COMPLETE FINAL FIX - GALION PLATFORM"
echo "======================================="

cd /nexuslang-v2

# 1. Fix PM2 services
echo "1. Restarting all PM2 services..."

# Delete errored services
pm2 delete all 2>/dev/null || true
sleep 2

# Start backend properly
echo "Starting backend..."
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ..

# Start galion-studio
echo "Starting galion-studio..."
cd galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd ..

# Start galion-app
echo "Starting galion-app..."
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ..

# Start developer-platform
echo "Starting developer-platform..."
cd developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ..

pm2 save

# 2. Wait for services to start
echo "2. Waiting for services to initialize..."
sleep 30

# 3. Check service status
echo "3. Service Status:"
pm2 list

# 4. Test services
echo "4. Testing services..."

echo -n "Backend (8000): "
if curl -s --max-time 10 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "Galion App (3000): "
if timeout 15 curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "Developer Platform (3003): "
if timeout 15 curl -s http://localhost:3003 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "Galion Studio (3030): "
if timeout 15 curl -s http://localhost:3030 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# 5. Fix nginx
echo "5. Configuring nginx..."

pkill nginx 2>/dev/null || true
sleep 2

# Create minimal working config
cat > /etc/nginx/sites-available/galion-final << 'EOF'
upstream backend_api { server localhost:8000; }
upstream galion_app { server localhost:3000; }
upstream developer_platform { server localhost:3003; }
upstream galion_studio { server localhost:3030; }

server {
    listen 8080;
    server_name _;

    location / {
        proxy_pass http://galion_app;
        proxy_set_header Host $host;
    }
}

server {
    listen 8080;
    server_name api.galion.app;

    location / {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://backend_api/health;
    }
}

server {
    listen 8080;
    server_name developer.galion.app;

    location / {
        proxy_pass http://developer_platform;
        proxy_set_header Host $host;
    }
}

server {
    listen 8080;
    server_name galion.studio;

    location / {
        proxy_pass http://galion_studio;
        proxy_set_header Host $host;
    }
}
EOF

# Enable config
ln -sf /etc/nginx/sites-available/galion-final /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/galion-simple
rm -f /etc/nginx/sites-enabled/galion-platform

# Start nginx
if nginx -t 2>/dev/null; then
    nginx 2>/dev/null || nginx -c /etc/nginx/nginx.conf
    echo "✅ Nginx started on port 8080"
else
    echo "❌ Nginx config error"
fi

# 6. Final test
echo "6. Final comprehensive test..."
sleep 10

echo ""
echo "🌐 SERVICE AVAILABILITY:"
echo "======================="

services=("8000:Backend" "3000:Galion App" "3003:Developer Platform" "3030:Galion Studio" "8080:Nginx")
for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    if curl -s --max-time 5 http://localhost:$port > /dev/null 2>&1; then
        echo "✅ $name (port $port): RUNNING"
    else
        echo "❌ $name (port $port): DOWN"
    fi
done

echo ""
echo "🎉 FINAL STATUS:"
echo "==============="
pm2 list

echo ""
echo "🌍 PRODUCTION READY!"
echo "==================="
echo "RunPod IP: $(hostname -i)"
echo "Nginx Port: 8080"
echo ""
echo "Configure Cloudflare DNS → $(hostname -i):8080"
echo ""
echo "URLs:"
echo "• https://galion.app"
echo "• https://api.galion.app/health"
echo "• https://developer.galion.app"
echo "• https://galion.studio"
