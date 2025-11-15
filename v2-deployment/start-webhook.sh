#!/bin/bash
# Start the V2 deployment webhook on RunPod

echo "🚀 Starting V2 Deployment Webhook..."

# Install Flask if not installed
pip3 install flask

# Go to project directory
cd /nexuslang-v2/v2-deployment

# Start webhook with PM2
pm2 start python3 --name "deploy-webhook" -- deploy-webhook.py

# Show status
pm2 status

echo ""
echo "✅ Webhook started on port 7000!"
echo ""
echo "📝 Expose port 7000 in RunPod dashboard to use it remotely"
echo "📝 Or use it locally: curl http://localhost:7000/health"
echo ""

