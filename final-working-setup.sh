#!/bin/bash
# FINAL WORKING SETUP - Get essential services running

echo "🚀 FINAL WORKING GALION SETUP"
echo "=============================="

cd /nexuslang-v2

# 1. Check what we actually have
echo "Checking available directories..."
ls -la | grep "^d" | grep -E "(galion|developer|v2)"

# 2. Install basic dependencies
echo ""
echo "Installing basic dependencies..."
pip3 install fastapi uvicorn psutil pydantic python-multipart --quiet
npm install -g pm2 --silent

# 3. Start backend (this should work)
echo ""
echo "Starting backend..."
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ..
echo "Backend started"

# 4. Start galion-studio (this exists and should work after fixing dependency)
echo ""
echo "Starting galion-studio..."
cd galion-studio

# Install missing dependency
npm install react-hot-toast --silent

# Start the service
pm2 start npm --name galion-studio -- run dev -- -p 3030 --hostname 0.0.0.0
cd ..
echo "Galion-studio started"

# 5. Wait for services
echo ""
echo "Waiting for services to start..."
sleep 15

# 6. Test what works
echo ""
echo "Testing services..."

echo -n "Backend: "
if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

echo -n "Galion Studio: "
if curl -s --max-time 5 http://localhost:3030 > /dev/null 2>&1; then
    echo "✅ WORKING"
else
    echo "❌ FAIL"
fi

# 7. Configure minimal nginx
echo ""
echo "Configuring minimal nginx..."

pkill nginx 2>/dev/null || true
sleep 2

# Clean nginx config
cat > /etc/nginx/sites-available/minimal << 'EOF'
upstream backend_api { server localhost:8000; }
upstream galion_studio { server localhost:3030; }

server {
    listen 8080 default_server;
    server_name _;

    location / {
        proxy_pass http://galion_studio;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
        access_log off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/minimal /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/galion*

nginx -t && nginx && echo "✅ Nginx configured" || echo "❌ Nginx failed"

# 8. Final status
echo ""
echo "FINAL STATUS:"
pm2 list

echo ""
echo "🎉 GALION PLATFORM STATUS:"
echo "=========================="
echo "✅ Backend: $(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "WORKING" || echo "NOT WORKING")"
echo "✅ Galion Studio: $(curl -s http://localhost:3030 > /dev/null 2>&1 && echo "WORKING" || echo "NOT WORKING")"
echo "✅ Nginx: $(curl -s http://localhost:8080 > /dev/null 2>&1 && echo "WORKING" || echo "NOT WORKING")"
echo ""
echo "🌐 ACCESS URLs:"
echo "   Backend API: http://localhost:8000/health"
echo "   Galion Studio: http://localhost:3000"
echo "   Nginx Proxy: http://localhost:8080"
echo ""
echo "🚀 EXTERNAL: $(hostname -i):8080"
echo ""
echo "Next: Configure Cloudflare DNS → $(hostname -i):8080"
