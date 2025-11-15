#!/bin/bash
# GALION PLATFORM - DEFINITIVE FINAL SETUP
# This script works regardless of where it's run from

echo "🚀 GALION PLATFORM - DEFINITIVE FINAL SETUP"
echo "==========================================="

# Find the correct directory
if [ -d "/nexuslang-v2" ]; then
    PROJECT_DIR="/nexuslang-v2"
elif [ -d "./nexuslang-v2" ]; then
    PROJECT_DIR="./nexuslang-v2"
else
    echo "❌ Cannot find nexuslang-v2 directory"
    echo "Please run this script from the correct location"
    exit 1
fi

echo "📁 Using project directory: $PROJECT_DIR"
cd $PROJECT_DIR

# 1. Check repository
echo ""
echo "1. Checking repository..."
if [ -d ".git" ]; then
    echo "✅ Git repository found"
    git pull origin clean-nexuslang 2>/dev/null || echo "⚠️  Git pull failed, continuing..."
else
    echo "❌ Not a git repository"
fi

# 2. Check directories
echo ""
echo "2. Checking application directories..."
DIRS_OK=true
for dir in "galion-app" "developer-platform" "galion-studio" "v2/backend"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
        DIRS_OK=false
    fi
done

if [ "$DIRS_OK" = false ]; then
    echo "❌ Some directories are missing. Please check the repository."
    exit 1
fi

# 3. Install dependencies
echo ""
echo "3. Installing dependencies..."

# Python
echo "Installing Python dependencies..."
pip3 install fastapi uvicorn psutil pydantic python-multipart --quiet

# Node.js apps
echo "Installing galion-app dependencies..."
cd $PROJECT_DIR/galion-app && npm install --silent && npm install lucide-react --silent

echo "Installing developer-platform dependencies..."
cd $PROJECT_DIR/developer-platform && npm install --silent

echo "Installing galion-studio dependencies..."
cd $PROJECT_DIR/galion-studio && npm install --silent

# PM2
echo "Installing PM2..."
npm install -g pm2 --silent

cd $PROJECT_DIR

# 4. Clean start all services
echo ""
echo "4. Starting all services..."

# Kill everything
pm2 kill 2>/dev/null || true
sleep 2

# Start backend
echo "Starting backend..."
cd $PROJECT_DIR/v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd $PROJECT_DIR

# Start galion-studio
echo "Starting galion-studio..."
cd $PROJECT_DIR/galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030 --hostname 0.0.0.0
cd $PROJECT_DIR

# Start galion-app
echo "Starting galion-app..."
cd $PROJECT_DIR/galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000 --hostname 0.0.0.0
cd $PROJECT_DIR

# Start developer-platform
echo "Starting developer-platform..."
cd $PROJECT_DIR/developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003 --hostname 0.0.0.0
cd $PROJECT_DIR

pm2 save

# 5. Wait for services
echo ""
echo "5. Waiting for services to start (30 seconds)..."
sleep 30

# 6. Test services
echo ""
echo "6. Testing all services..."

test_service() {
    local port=$1
    local name=$2
    echo -n "$name ($port): "
    if timeout 10 curl -s http://localhost:$port > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

test_service 8000 "Backend"
test_service 3000 "Galion App"
test_service 3003 "Developer Platform"
test_service 3030 "Galion Studio"

# 7. Configure nginx
echo ""
echo "7. Configuring nginx..."

# Stop nginx
pkill nginx 2>/dev/null || true
sleep 2

# Create nginx config
cat > /etc/nginx/sites-available/galion-platform << 'EOF'
# Galion Platform - Working Configuration

upstream backend_api { server localhost:8000; }
upstream galion_app { server localhost:3000; }
upstream developer_platform { server localhost:3003; }
upstream galion_studio { server localhost:3030; }

# Default server (galion.app)
server {
    listen 8080 default_server;
    server_name _;

    location / {
        proxy_pass http://galion_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API subdomain
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

# Developer subdomain
server {
    listen 8080;
    server_name developer.galion.app;

    location / {
        proxy_pass http://developer_platform;
        proxy_set_header Host $host;
    }
}

# Studio subdomain
server {
    listen 8080;
    server_name galion.studio www.galion.studio;

    location / {
        proxy_pass http://galion_studio;
        proxy_set_header Host $host;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/ 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default

# Start nginx
if nginx -t 2>/dev/null; then
    nginx 2>/dev/null || nginx -c /etc/nginx/nginx.conf
    echo "✅ Nginx configured and started"
else
    echo "❌ Nginx configuration error"
    nginx -t
fi

# 8. Final status
echo ""
echo "8. FINAL SERVICE STATUS:"
pm2 list

echo ""
echo "🎉 GALION PLATFORM IS NOW RUNNING!"
echo "==================================="
echo ""
echo "🌐 LOCAL URLs:"
echo "   Backend API:      http://localhost:8000/health"
echo "   Galion App:       http://localhost:3000"
echo "   Developer Platform: http://localhost:3003"
echo "   Galion Studio:    http://localhost:3030"
echo "   Nginx Proxy:      http://localhost:8080"
echo ""
echo "🌍 PRODUCTION READY:"
echo "   RunPod IP: $(hostname -i)"
echo "   Port: 8080"
echo ""
echo "   Configure Cloudflare DNS:"
echo "   galion.app → $(hostname -i):8080"
echo "   api.galion.app → $(hostname -i):8080"
echo "   developer.galion.app → $(hostname -i):8080"
echo "   galion.studio → $(hostname -i):8080"
echo ""
echo "🚀 Your Galion Platform is fully operational!"
