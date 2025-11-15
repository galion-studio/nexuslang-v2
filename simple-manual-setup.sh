#!/bin/bash
# Simple manual setup - run this from /nexuslang-v2 directory

echo "🔧 SIMPLE MANUAL SETUP"
echo "======================"

# Check current directory
if [ "$(basename $(pwd))" != "nexuslang-v2" ]; then
    echo "❌ Please run this from the /nexuslang-v2 directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ Running from correct directory: $(pwd)"

# 1. Install dependencies
echo ""
echo "1. Installing dependencies..."

# Python
pip3 install fastapi uvicorn psutil pydantic python-multipart --quiet

# Node apps
echo "Installing galion-app..."
cd galion-app && npm install --silent && npm install lucide-react --silent && cd ..

echo "Installing developer-platform..."
cd developer-platform && npm install --silent && cd ..

echo "Installing galion-studio..."
cd galion-studio && npm install --silent && cd ..

# PM2
npm install -g pm2 --silent

# 2. Start services
echo ""
echo "2. Starting services..."

# Kill existing
pm2 kill 2>/dev/null || true
sleep 2

# Backend
echo "Starting backend..."
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Galion Studio
echo "Starting galion-studio..."
cd galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030 --hostname 0.0.0.0
cd ..

# Galion App
echo "Starting galion-app..."
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000 --hostname 0.0.0.0
cd ..

# Developer Platform
echo "Starting developer-platform..."
cd developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003 --hostname 0.0.0.0
cd ..

pm2 save

# 3. Wait and test
echo ""
echo "3. Waiting for services..."
sleep 20

echo "Testing services:"
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FAIL"
curl -s http://localhost:3000 && echo "✅ Galion App OK" || echo "❌ Galion App FAIL"
curl -s http://localhost:3003 && echo "✅ Developer Platform OK" || echo "❌ Developer Platform FAIL"
curl -s http://localhost:3030 && echo "✅ Galion Studio OK" || echo "❌ Galion Studio FAIL"

# 4. Configure nginx
echo ""
echo "4. Configuring nginx..."

pkill nginx 2>/dev/null || true
sleep 2

cat > /etc/nginx/sites-available/galion << 'EOF'
upstream backend_api { server localhost:8000; }
upstream galion_app { server localhost:3000; }
upstream developer_platform { server localhost:3003; }
upstream galion_studio { server localhost:3030; }

server {
    listen 8080 default_server;
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
EOF

ln -sf /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default

nginx -t && nginx && echo "✅ Nginx configured"

# 5. Final status
echo ""
echo "5. FINAL STATUS:"
pm2 list

echo ""
echo "🎉 SETUP COMPLETE!"
echo "RunPod IP: $(hostname -i)"
echo "Port: 8080"
echo ""
echo "Test: curl http://localhost:8080"
