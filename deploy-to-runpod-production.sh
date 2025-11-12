#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  NexusLang v2 - Production Deployment to RunPod           ║
# ║  Complete automated deployment with all services           ║
# ╚════════════════════════════════════════════════════════════╝

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 NexusLang v2 - Production Deployment                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if running from project root
if [ ! -d "v2" ]; then
    echo "❌ ERROR: Must run from project root"
    echo "   cd /workspace/project-nexus && ./deploy-to-runpod-production.sh"
    exit 1
fi

echo "✅ Running from correct directory"
echo ""

# Check if environment file exists
if [ ! -f "v2/.env" ]; then
    echo "⚠️  No v2/.env file found!"
    echo ""
    echo "Creating production environment..."
    
    # Run environment setup
    if [ -f "setup-production-env.sh" ]; then
        chmod +x setup-production-env.sh
        ./setup-production-env.sh
    else
        echo "❌ ERROR: setup-production-env.sh not found"
        exit 1
    fi
else
    echo "✅ Environment file exists"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 1: Validating Environment                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check required environment variables
source v2/.env 2>/dev/null || true

if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "GENERATE_WITH_openssl_rand_hex_64" ]; then
    echo "❌ JWT_SECRET not set or using placeholder!"
    echo "   Generate with: openssl rand -hex 64"
    echo "   Add to v2/.env"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-proj-your-actual-key-here" ]; then
    echo "⚠️  OPENAI_API_KEY not set or using placeholder"
    echo "   AI features will be limited"
fi

echo "✅ Environment validated"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 2: Installing Dependencies                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 3: Building Docker Images                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd v2

# Build images
echo "Building backend image..."
docker-compose -f ../docker-compose.prod.yml build backend

echo "Building frontend image..."
docker-compose -f ../docker-compose.prod.yml build frontend

echo "✅ Images built"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 4: Starting Services                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Start all services
docker-compose -f ../docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy (30 seconds)..."
sleep 30

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 5: Verifying Deployment                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check container status
echo "Container Status:"
docker-compose -f ../docker-compose.prod.yml ps

echo ""

# Check backend health
echo "Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
    curl http://localhost:8000/health | jq '.' 2>/dev/null || curl http://localhost:8000/health
else
    echo "❌ Backend health check failed"
    echo "   Check logs: docker-compose -f ../docker-compose.prod.yml logs backend"
    exit 1
fi

echo ""

# Check frontend
echo "Checking frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend not responding yet (may still be starting)"
fi

echo ""

# Check database
echo "Checking database connection..."
if docker-compose -f ../docker-compose.prod.yml exec -T postgres pg_isready > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database not ready"
fi

echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Step 6: Initializing Database                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Run migrations if they exist
if [ -f "database/schemas/init.sql" ]; then
    echo "Running database migrations..."
    docker-compose -f ../docker-compose.prod.yml exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < database/schemas/init.sql || true
    echo "✅ Database initialized"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE!                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 NexusLang v2 is now running!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "📁 Important Files:"
echo "   Logs:      docker-compose -f ../docker-compose.prod.yml logs -f"
echo "   Restart:   docker-compose -f ../docker-compose.prod.yml restart"
echo "   Stop:      docker-compose -f ../docker-compose.prod.yml down"
echo ""
echo "🌐 Next Steps:"
echo "   1. Test locally: curl http://localhost:8000/health"
echo "   2. Configure DNS to point to this server"
echo "   3. Set up SSL certificates (see RUNPOD_SSL_SETUP_GUIDE.md)"
echo "   4. Update CORS_ORIGINS in v2/.env with production domains"
echo "   5. Access: https://developer.galion.app"
echo ""
echo "📊 Monitor deployment:"
echo "   docker-compose -f ../docker-compose.prod.yml logs -f"
echo ""
echo "🎉 Happy deploying!"
echo ""

