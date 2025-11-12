#!/bin/bash
# Ultra-Quick Setup for RunPod
# One command to rule them all!

set -e

echo "🎮 NexusLang v2 - RunPod Ultra-Quick Setup"
echo "=========================================="
echo ""

# Check if on RunPod
if [ ! -d "/workspace" ]; then
    echo "⚠️ Not on RunPod. Creating /workspace..."
    mkdir -p /workspace
fi

cd /workspace

# Install basics if needed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    apt-get update -qq && apt-get install -y -qq docker-compose git curl
fi

# Clone if needed
if [ ! -d "project-nexus" ]; then
    echo "📥 Cloning repository..."
    echo "Enter repository URL (or press Enter to skip):"
    read REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git clone $REPO_URL project-nexus
    else
        echo "Skipping clone. Upload files manually to /workspace/project-nexus"
        exit 0
    fi
fi

cd project-nexus

# Configure environment
if [ ! -f .env ]; then
    echo "⚙️ Configuring environment..."
    cp env.runpod.template .env
    
    # Generate secure passwords
    POSTGRES_PW=$(openssl rand -hex 16)
    REDIS_PW=$(openssl rand -hex 16)
    SECRET=$(openssl rand -hex 32)
    JWT=$(openssl rand -hex 64)
    
    # Update .env
    sed -i "s/your_secure_postgres_password_here/${POSTGRES_PW}/g" .env
    sed -i "s/your_secure_redis_password_here/${REDIS_PW}/g" .env
    sed -i "s/your_secret_key_at_least_32_characters/${SECRET}/g" .env
    sed -i "s/your_jwt_secret_at_least_64_characters/${JWT}/g" .env
    
    echo ""
    echo "🔑 Secure passwords generated!"
    echo "⚠️ IMPORTANT: Add your OpenAI API key to .env"
    echo ""
    echo "Edit .env now? (y/n)"
    read -n 1 EDIT
    echo ""
    
    if [ "$EDIT" = "y" ]; then
        nano .env
    fi
fi

# Deploy
echo ""
echo "🚀 Deploying NexusLang v2..."
chmod +x runpod-deploy.sh
./runpod-deploy.sh

echo ""
echo "✅ Setup complete! Your platform is live!"
echo ""
echo "📋 URLs saved to: /workspace/RUNPOD_URLS.txt"
echo "📖 View with: cat /workspace/RUNPOD_URLS.txt"
echo ""

