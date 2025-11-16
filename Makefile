# ============================================
# GALION VOICE API - MAKEFILE
# ============================================
# Common development commands

.PHONY: help setup dev prod clean test lint format docs

# Default target
help:
	@echo "🚀 Galion Voice API - Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make setup     - Setup development environment"
	@echo "  make dev       - Start development services"
	@echo "  make prod      - Start production services"
	@echo "  make clean     - Clean up Docker containers and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make test      - Run all tests"
	@echo "  make test-backend  - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint      - Run linters"
	@echo "  make format    - Format code"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs      - Generate documentation"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy    - Deploy to production"
	@echo "  make backup    - Create backup"
	@echo ""

# Setup development environment
setup:
	@echo "🚀 Setting up development environment..."
	./scripts/setup-dev.sh

# Start development services
dev:
	@echo "🚀 Starting development services..."
	if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose up -d; \
	else \
		docker compose up -d; \
	fi
	@echo "📡 Services starting..."
	@echo "   - Frontend: http://localhost:3003"
	@echo "   - Backend: http://localhost:8000"
	@echo "   - API Docs: http://localhost:8000/docs"

# Start production services
prod:
	@echo "🚀 Starting production services..."
	if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker-compose.prod.yml up -d; \
	else \
		docker compose -f docker-compose.prod.yml up -d; \
	fi

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	./scripts/cleanup.sh

# Run all tests
test: test-backend test-frontend

# Run backend tests
test-backend:
	@echo "🧪 Running backend tests..."
	cd v2/backend && python -m pytest tests/ -v

# Run frontend tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	cd galion-app && npm test

# Run linters
lint:
	@echo "🔍 Running linters..."
	cd v2/backend && python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	cd galion-app && npm run lint

# Format code
format:
	@echo "🎨 Formatting code..."
	cd v2/backend && python -m black . && python -m isort .
	cd galion-app && npm run format

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	cd v2/backend && python -m pdoc --html --output-dir docs .
	cd galion-app && npm run build-docs

# Deploy to production
deploy:
	@echo "🚀 Deploying to production..."
	./scripts/deploy-production.sh

# Create backup
backup:
	@echo "💾 Creating backup..."
	./scripts/backup.sh

# View logs
logs:
	@echo "📋 Viewing logs..."
	if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose logs -f; \
	else \
		docker compose logs -f; \
	fi

# Check health
health:
	@echo "💓 Checking service health..."
	@echo "Backend: $$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo 'not running')"
	@echo "Frontend: $$(curl -s -I http://localhost:3003 | head -1 | cut -d' ' -f2 2>/dev/null || echo 'not running')"

# Stop all services
stop:
	@echo "🛑 Stopping all services..."
	if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose down; \
	else \
		docker compose down; \
	fi

# Restart services
restart:
	@echo "🔄 Restarting services..."
	if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose restart; \
	else \
		docker compose restart; \
	fi
