#!/bin/bash

# Galion Ecosystem - Complete Deployment Script
# One-command deployment for RunPod

set -e

echo "🚀 GALION ECOSYSTEM - COMPLETE DEPLOYMENT"
echo "========================================="
echo ""

# Function to show progress
show_step() {
    echo ""
    echo "📋 STEP $1: $2"
    echo "========================================"
}

# STEP 1: Update system
show_step "1" "Update system and install dependencies"
sudo apt update
sudo apt install -y nginx nodejs npm python3 python3-pip git curl

# STEP 2: Clone repository
show_step "2" "Clone repository"
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2
chmod +x *.sh

# STEP 3: Setup nginx
show_step "3" "Setup nginx reverse proxy"
sudo bash runpod-nginx-setup.sh

# STEP 4: Install PM2
show_step "4" "Install PM2 globally"
npm install -g pm2

# STEP 5: Install frontend dependencies
show_step "5" "Install frontend dependencies"
cd galion-app && npm install && cd ..
cd galion-studio && npm install && cd ..
cd developer-platform && npm install && cd ..

# STEP 6: Install backend dependencies
show_step "6" "Install backend dependencies"
cd v2/backend && pip3 install fastapi uvicorn psutil && cd ../..

# STEP 7: Start services
show_step "7" "Start all services"
cd galion-studio && pm2 start npm --name "galion-studio" -- run start -- -p 3001 && cd ..
cd developer-platform && pm2 start npm --name "developer-platform" -- run start -- -p 3002 && cd ..
cd galion-app && pm2 start npm --name "galion-app" -- run start -- -p 3003 && cd ..
cd v2/backend && pm2 start python3 --name "galion-backend" -- main_simple.py --host 0.0.0.0 --port 8000 && cd ../..

# STEP 8: Configure PM2
show_step "8" "Configure PM2 for auto-start"
pm2 save
pm2 startup

# STEP 9: Final verification
show_step "9" "Final verification"
echo ""
echo "🔍 PM2 Status:"
pm2 status
echo ""

echo "🧪 Health Check:"
curl -s http://localhost/health
echo ""

echo "🚀 API Test:"
curl -s http://localhost/api/health
echo ""

# Final message
echo ""
echo "🎉 GALION ECOSYSTEM DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "📋 NEXT STEPS:"
echo "=============="
echo "1. Go to RunPod dashboard"
echo "2. Settings → TCP Ports → Add: 80"
echo "3. Wait 30-60 seconds"
echo "4. Access your API: http://[your-pod-id]-80.proxy.runpod.net/api/health"
echo ""
echo "🌐 AVAILABLE ENDPOINTS:"
echo "- Health: http://[pod-id]-80.proxy.runpod.net/health"
echo "- API: http://[pod-id]-80.proxy.runpod.net/api/health"
echo "- Info: http://[pod-id]-80.proxy.runpod.net/"
echo ""
echo "🚀 Your scientific AI platform is ready for production!"
echo ""
echo "Script completed at: $(date)"
