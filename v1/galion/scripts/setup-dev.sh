#!/bin/bash
# Setup script for local development environment

echo "🚀 Setting up Nexus Core Development Environment"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start infrastructure
echo "📦 Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if postgres is ready
if docker exec nexus-postgres pg_isready -U nexuscore &> /dev/null; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready. Check logs with: docker logs nexus-postgres"
    exit 1
fi

# Check if redis is ready
if docker exec nexus-redis redis-cli ping &> /dev/null; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready. Check logs with: docker logs nexus-redis"
    exit 1
fi

echo ""
echo "✨ Infrastructure is ready!"
echo ""
echo "📝 Next steps:"
echo "   1. Set up auth service:"
echo "      cd services/auth-service"
echo "      python -m venv venv"
echo "      source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "      pip install -r requirements.txt"
echo "      uvicorn app.main:app --reload"
echo ""
echo "   2. Access the API documentation:"
echo "      http://localhost:8000/docs"
echo ""
echo "   3. Test the database connection:"
echo "      docker exec -it nexus-postgres psql -U nexuscore -d nexuscore"
echo ""

