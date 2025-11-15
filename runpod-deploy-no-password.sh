#!/bin/bash
# ============================================
# Deploy Script - No Password Required
# Works with public GitHub repository
# ============================================

cd /nexuslang-v2 || exit 1

echo "🚀 Deploying from GitHub..."
echo ""

# Set git to use public HTTPS (no password needed)
git remote set-url origin https://github.com/galion-studio/nexuslang-v2.git

# Pull latest code (public repo, no password)
echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/clean-nexuslang

echo "✓ Code updated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q fastapi uvicorn psutil pydantic python-multipart

for app in galion-studio galion-app developer-platform; do
  if [ -d "$app" ]; then
    cd "$app" && npm install --silent && cd /nexuslang-v2
  fi
done

echo "✓ Dependencies installed"
echo ""

# Restart services
echo "🔄 Restarting services..."
pm2 delete all 2>/dev/null || true

cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd /nexuslang-v2

cd galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd /nexuslang-v2

cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd /nexuslang-v2

cd developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd /nexuslang-v2

pm2 save

echo ""
echo "✅ All services started!"
echo ""

pm2 status

echo ""
echo "🌐 Platform ready at:"
echo "  • http://213.173.105.83:8000/docs"
echo "  • http://213.173.105.83:3030"
echo "  • http://213.173.105.83:3000"
echo "  • http://213.173.105.83:3003"
echo ""

