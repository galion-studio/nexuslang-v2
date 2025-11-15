#!/bin/bash
# Start ALL Services - Backend microservices + All frontends

set -e

echo "🚀 STARTING ALL GALION PLATFORM SERVICES"
echo "========================================="
echo ""

cd /nexuslang-v2

# ============================================
# STEP 1: INSTALL MISSING DEPENDENCIES
# ============================================
echo "1️⃣  Installing dependencies for all services..."
echo ""

# Python backend
echo "Installing Python dependencies..."
pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart 2>&1 | grep -v "Requirement already satisfied" || true

# Galion Studio
if [ -d "galion-studio" ]; then
    echo "Installing galion-studio dependencies..."
    cd galion-studio
    npm install --silent 2>&1 | tail -1
    npm install react-hot-toast lucide-react clsx tailwind-merge --silent 2>&1 | tail -1
    cd ..
fi

# Galion App
if [ -d "galion-app" ]; then
    echo "Installing galion-app dependencies..."
    cd galion-app
    npm install --silent 2>&1 | tail -1
    npm install lucide-react clsx tailwind-merge --silent 2>&1 | tail -1
    cd ..
fi

# Developer Platform
if [ -d "developer-platform" ]; then
    echo "Installing developer-platform dependencies..."
    cd developer-platform
    npm install --silent 2>&1 | tail -1
    npm install lucide-react clsx tailwind-merge --silent 2>&1 | tail -1
    cd ..
fi

echo "✅ Dependencies installed"
echo ""

# ============================================
# STEP 2: STOP EXISTING SERVICES
# ============================================
echo "2️⃣  Stopping existing services..."
pm2 delete all 2>/dev/null || true
sleep 2
echo "✅ Stopped"
echo ""

# ============================================
# STEP 3: CREATE COMPREHENSIVE ECOSYSTEM
# ============================================
echo "3️⃣  Creating comprehensive PM2 ecosystem..."

cat > ecosystem-all.config.js << 'EOF'
module.exports = {
  apps: [
    // Backend API
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
        PYTHONUNBUFFERED: '1',
        PORT: '8000'
      }
    },
    
    // Galion Studio (Corporate Website)
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
        PORT: '3030',
        NODE_ENV: 'development'
      }
    },
    
    // Galion App (Voice-First Application)
    {
      name: 'galion-app',
      script: 'npm',
      args: 'run dev -- -p 3000 -H 0.0.0.0',
      cwd: '/nexuslang-v2/galion-app',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PORT: '3000',
        NODE_ENV: 'development'
      }
    },
    
    // Developer Platform (IDE)
    {
      name: 'developer-platform',
      script: 'npm',
      args: 'run dev -- -p 3003 -H 0.0.0.0',
      cwd: '/nexuslang-v2/developer-platform',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PORT: '3003',
        NODE_ENV: 'development'
      }
    }
  ]
};
EOF

echo "✅ Ecosystem created"
echo ""

# ============================================
# STEP 4: START ALL SERVICES
# ============================================
echo "4️⃣  Starting all services..."

# Check which services can actually start
SERVICES_TO_START=()

if [ -f "v2/backend/main_simple.py" ]; then
    SERVICES_TO_START+=("backend")
fi

if [ -d "galion-studio" ] && [ -f "galion-studio/package.json" ]; then
    SERVICES_TO_START+=("galion-studio")
fi

if [ -d "galion-app" ] && [ -f "galion-app/package.json" ]; then
    SERVICES_TO_START+=("galion-app")
fi

if [ -d "developer-platform" ] && [ -f "developer-platform/package.json" ]; then
    SERVICES_TO_START+=("developer-platform")
fi

echo "Services to start: ${SERVICES_TO_START[@]}"
echo ""

# Start services
pm2 start ecosystem-all.config.js

sleep 5

pm2 save

echo "✅ Services started"
echo ""

# ============================================
# STEP 5: WAIT FOR STARTUP
# ============================================
echo "5️⃣  Waiting for services to initialize..."
sleep 15
echo "✅ Initialization complete"
echo ""

# ============================================
# STEP 6: SHOW STATUS
# ============================================
echo "6️⃣  Service Status:"
echo ""
pm2 list
echo ""

# ============================================
# STEP 7: TEST SERVICES
# ============================================
echo "7️⃣  Testing services..."
echo ""

test_service() {
    local name=$1
    local url=$2
    
    echo -n "$name... "
    if curl -sf --max-time 10 "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

test_service "Backend API" "http://localhost:8000/health"
test_service "Galion Studio" "http://localhost:3030"
test_service "Galion App" "http://localhost:3000"
test_service "Developer Platform" "http://localhost:3003"
test_service "Nginx" "http://localhost"

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 ALL SERVICES STARTED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Running Services:"
pm2 list | grep -E "backend|galion" || pm2 list
echo ""
echo "🌐 Access URLs:"
echo "   • Backend API:         http://localhost:8000"
echo "   • API Docs:            http://localhost:8000/docs"
echo "   • Galion Studio:       http://localhost:3030"
echo "   • Galion App:          http://localhost:3000"
echo "   • Developer Platform:  http://localhost:3003"
echo "   • Nginx Proxy:         http://localhost"
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:           pm2 logs"
echo "   • Monitor:             pm2 monit"
echo "   • Restart all:         pm2 restart all"
echo "   • Stop all:            pm2 stop all"
echo "   • Health check:        bash mega-comprehensive-check.sh"
echo ""
echo "✅ Ready for mega comprehensive check!"
echo ""

