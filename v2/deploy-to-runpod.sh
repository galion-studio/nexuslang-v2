#!/bin/bash
# Automated Deployment Script for RunPod
# Deploy NexusLang v2 + Content Management System

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════╗"
echo "║  NexusLang v2 + Content Manager Deployment            ║"
echo "║  Deploying to RunPod                                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if environment variables are set
if [ -z "$RUNPOD_HOST" ] || [ -z "$RUNPOD_PORT" ]; then
    echo "❌ Error: RUNPOD_HOST and RUNPOD_PORT must be set"
    echo ""
    echo "Please set environment variables:"
    echo "  export RUNPOD_HOST='your-runpod-ip'"
    echo "  export RUNPOD_PORT='your-ssh-port'"
    exit 1
fi

SSH_USER="${SSH_USER:-root}"
PROJECT_PATH="/root/project-nexus"

echo "📋 Deployment Configuration:"
echo "   Host: $RUNPOD_HOST"
echo "   Port: $RUNPOD_PORT"
echo "   User: $SSH_USER"
echo ""

# Function to run remote commands
run_remote() {
    ssh -p $RUNPOD_PORT $SSH_USER@$RUNPOD_HOST "$@"
}

# Function to copy files
copy_to_remote() {
    scp -P $RUNPOD_PORT -r "$1" $SSH_USER@$RUNPOD_HOST:"$2"
}

echo "🔍 Step 1: Testing SSH connection..."
if run_remote "echo 'Connection successful'"; then
    echo "✅ SSH connection established"
else
    echo "❌ Failed to connect via SSH"
    echo "Please check your RUNPOD_HOST, RUNPOD_PORT, and SSH keys"
    exit 1
fi

echo ""
echo "📦 Step 2: Checking if repository exists..."
if run_remote "[ -d $PROJECT_PATH ]"; then
    echo "📂 Repository exists, updating..."
    run_remote "cd $PROJECT_PATH && git pull origin main"
else
    echo "📥 Cloning repository..."
    REPO_URL="${GITHUB_REPO:-https://github.com/yourusername/project-nexus.git}"
    echo "   Using repository: $REPO_URL"
    run_remote "git clone $REPO_URL $PROJECT_PATH" || {
        echo "⚠️  Clone failed, copying local files instead..."
        echo "   This will take a moment..."
        run_remote "mkdir -p $PROJECT_PATH"
        copy_to_remote "." "$PROJECT_PATH/"
    }
fi

echo ""
echo "🔧 Step 3: Installing dependencies..."
run_remote "cd $PROJECT_PATH/v2 && bash" << 'REMOTE_SCRIPT'
# Install system dependencies
apt-get update -qq
apt-get install -y -qq docker.io docker-compose postgresql-client redis-tools curl wget git

# Start Docker
systemctl start docker
systemctl enable docker

echo "✅ Dependencies installed"
REMOTE_SCRIPT

echo ""
echo "⚙️  Step 4: Setting up environment..."
run_remote "cd $PROJECT_PATH/v2 && bash" << 'REMOTE_SCRIPT'
# Generate secure environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://nexuslang:$(openssl rand -hex 16)@postgres:5432/nexuslang_v2

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# CORS
CORS_ORIGINS=["http://localhost:3100","https://developer.galion.app"]

# Ports
BACKEND_PORT=8100
FRONTEND_PORT=3100

# Storage
STORAGE_TYPE=local
MEDIA_STORAGE_PATH=/app/media_storage
MEDIA_BASE_URL=http://localhost:8100/media

# Environment
ENVIRONMENT=production
DEBUG=false
EOF
    echo "✅ Environment configured"
else
    echo "✅ Environment file exists"
fi
REMOTE_SCRIPT

echo ""
echo "🐳 Step 5: Building and starting Docker services..."
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml down"
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml pull"
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml build --no-cache"
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml up -d"

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "🗄️  Step 6: Running database migrations..."
echo "   - Creating database schema..."
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml exec -T backend python -c \"
from core.database import init_db
import asyncio
asyncio.run(init_db())
print('Database initialized')
\"" || echo "⚠️  Database init failed or already done"

echo "   - Running content manager migration..."
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml exec -T postgres psql -U nexuslang nexuslang_v2 < database/migrations/003_content_manager.sql" || echo "⚠️  Migration failed or already applied"

echo ""
echo "🔍 Step 7: Checking service health..."
if run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml ps | grep 'Up'"; then
    echo "✅ Services are running"
else
    echo "⚠️  Some services may not be running"
    echo "Logs:"
    run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml logs --tail=20"
fi

echo ""
echo "🧪 Step 8: Testing API..."
sleep 5
if run_remote "curl -s http://localhost:8100/health | grep -q 'healthy'"; then
    echo "✅ Backend API is responding"
else
    echo "⚠️  Backend API may not be ready yet"
fi

echo ""
echo "📊 Step 9: Deployment Summary..."
run_remote "cd $PROJECT_PATH/v2 && docker-compose -f docker-compose.nexuslang.yml ps"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  🎉 DEPLOYMENT COMPLETE!                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your services are running at:"
echo "   Backend:  http://$RUNPOD_HOST:8100"
echo "   Frontend: http://$RUNPOD_HOST:3100"
echo "   API Docs: http://$RUNPOD_HOST:8100/docs"
echo ""
echo "🔐 Admin Access:"
echo "   ssh -p $RUNPOD_PORT $SSH_USER@$RUNPOD_HOST"
echo ""
echo "📝 Next Steps:"
echo "   1. Setup Cloudflare Tunnel for HTTPS (see DEPLOY_RUNPOD_SECURE.md)"
echo "   2. Connect social media accounts via /content-manager/settings"
echo "   3. Create your first post at /content-manager/compose"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: v2/START_HERE_CONTENT_MANAGER.md"
echo "   - Admin Guide: v2/README_ADMIN.md"
echo ""
echo "🛠️  Useful Commands:"
echo "   View logs:    ssh -p $RUNPOD_PORT $SSH_USER@$RUNPOD_HOST 'cd $PROJECT_PATH/v2 && docker-compose logs -f'"
echo "   Restart:      ssh -p $RUNPOD_PORT $SSH_USER@$RUNPOD_HOST 'cd $PROJECT_PATH/v2 && docker-compose restart'"
echo "   Stop:         ssh -p $RUNPOD_PORT $SSH_USER@$RUNPOD_HOST 'cd $PROJECT_PATH/v2 && docker-compose down'"
echo ""
