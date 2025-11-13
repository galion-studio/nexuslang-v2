#!/bin/bash
# 🚀 Pull from GitHub and Deploy Everything on RunPod
# Run this on your RunPod instance

echo "🚀 Pulling latest code from GitHub..."

cd /workspace/project-nexus

# Pull latest changes
git pull origin main

# Make scripts executable
chmod +x MASTER_DEPLOY_ALL_PLATFORMS.sh

# Run master deployment
bash MASTER_DEPLOY_ALL_PLATFORMS.sh

echo ""
echo "🎉 Deployment complete!"
echo "Check /workspace/DEPLOYMENT_COMPLETE.txt for all your URLs!"

