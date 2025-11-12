#!/bin/bash
# NexusLang v2 - Initialization Script
# Sets up the development environment

set -e

echo "🚀 Initializing NexusLang v2 Platform..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose found"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo -e "${BLUE}ℹ${NC} Please edit .env and add your API keys"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p v2/database/migrations
mkdir -p v2/database/seeds
mkdir -p logs
mkdir -p backups

# Generate secrets if needed
if grep -q "change_this" .env; then
    echo -e "${YELLOW}⚠${NC} Generating secure secrets..."
    # Generate random secrets (requires openssl)
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -base64 32)
        JWT_SECRET=$(openssl rand -base64 32)
        POSTGRES_PASSWORD=$(openssl rand -base64 16)
        REDIS_PASSWORD=$(openssl rand -base64 16)
        
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
        sed -i.bak "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
        
        rm .env.bak
        echo -e "${GREEN}✓${NC} Secrets generated"
    fi
fi

# Pull Docker images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec -T postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql

echo ""
echo -e "${GREEN}✅ NexusLang v2 Platform initialized successfully!${NC}"
echo ""
echo "Services available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys (OpenAI, Shopify)"
echo "  2. Restart services: docker-compose restart"
echo "  3. Visit http://localhost:3000 to get started"
echo ""

