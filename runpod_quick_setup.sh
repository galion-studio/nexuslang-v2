#!/bin/bash
# 🚀 Quick RunPod Setup - One Command Deployment
# Run this on your RunPod instance

echo "🚀 Galion Ecosystem - Quick Setup for RunPod"
echo "=============================================="
echo ""

# Download and run the complete deployment script
curl -fsSL https://raw.githubusercontent.com/yourusername/project-nexus/main/RUNPOD_AUTO_DEPLOY_COMPLETE.sh -o /tmp/deploy.sh

chmod +x /tmp/deploy.sh

bash /tmp/deploy.sh

echo ""
echo "✅ Setup complete! Your platform is now running."

