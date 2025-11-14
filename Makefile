# Galion Agent System - Development and Testing Makefile

.PHONY: help install install-dev clean test test-unit test-integration test-performance test-frontend lint format type-check security-scan build-frontend docs serve serve-frontend docker-build docker-up docker-down

# Default target
help:
	@echo "🚀 Galion Agent System - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  install         Install production dependencies"
	@echo "  install-dev     Install development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint            Run all linters (black, isort, flake8)"
	@echo "  format          Auto-format code (black, isort)"
	@echo "  type-check      Run mypy type checking"
	@echo "  security-scan   Run security vulnerability scans"
	@echo ""
	@echo "Testing:"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-frontend   Run frontend tests only"
	@echo "  coverage        Generate coverage report"
	@echo ""
	@echo "Development:"
	@echo "  serve           Start development server"
	@echo "  serve-frontend  Start frontend development server"
	@echo "  build-frontend  Build frontend for production"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker images"
	@echo "  docker-up       Start all services with Docker Compose"
	@echo "  docker-down     Stop all services"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean           Clean up cache files and artifacts"
	@echo "  docs            Generate documentation"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev]
	pip install -r tests/requirements.txt
	cd admin-dashboard && npm install

# Code Quality
lint:
	@echo "🔍 Running code quality checks..."
	black --check --diff v2 tests
	isort --check-only --diff v2 tests
	flake8 v2 tests --max-line-length=100 --extend-ignore=E203,W503
	mypy v2 --ignore-missing-imports
	cd admin-dashboard && npm run lint

format:
	@echo "✨ Formatting code..."
	black v2 tests
	isort v2 tests
	cd admin-dashboard && npm run format

type-check:
	@echo "🔍 Running type checking..."
	mypy v2 --ignore-missing-imports
	cd admin-dashboard && npm run type-check

security-scan:
	@echo "🔒 Running security scans..."
	pip install safety bandit
	safety check
	bandit -r v2 -f json -o security-report.json
	cd admin-dashboard && npm audit

# Testing
test:
	@echo "🧪 Running all tests..."
	pytest tests/ -v --tb=short --cov=v2 --cov-report=html --cov-fail-under=80

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/ -v --tb=short -m "not (integration or performance or slow or external)"

test-integration:
	@echo "🔗 Running integration tests..."
	pytest tests/ -v --tb=short -m "integration"

test-performance:
	@echo "⚡ Running performance tests..."
	pytest tests/test_performance.py -v --tb=short --benchmark-only

test-frontend:
	@echo "🎨 Running frontend tests..."
	cd admin-dashboard && npm run test

coverage:
	@echo "📊 Generating coverage report..."
	pytest tests/ --cov=v2 --cov-report=html --cov-report=xml
	@echo "Coverage report generated in htmlcov/"

# Development
serve:
	@echo "🚀 Starting development server..."
	python -m uvicorn v2.backend.main:app --reload --host 0.0.0.0 --port 8010

serve-frontend:
	@echo "🎨 Starting frontend development server..."
	cd admin-dashboard && npm run dev

build-frontend:
	@echo "🔨 Building frontend for production..."
	cd admin-dashboard && npm run build

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "Services started! Access at:"
	@echo "  - Backend API: http://localhost:8010"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Admin Dashboard: http://localhost:3000"
	@echo "  - API Docs: http://localhost:8010/docs"

docker-down:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Maintenance
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	rm -rf .coverage coverage.xml coverage.json htmlcov/
	rm -rf admin-dashboard/.next admin-dashboard/out
	rm -f security-report.json bandit-results.json

docs:
	@echo "📚 Generating documentation..."
	pip install sphinx sphinx-rtd-theme
	sphinx-apidoc -f -o docs/source v2
	cd docs && make html

# Quick development workflow
dev-setup: install-dev
	@echo "✅ Development environment ready!"
	@echo "Run 'make serve' to start the backend"
	@echo "Run 'make serve-frontend' to start the frontend"

dev-test: lint test-unit
	@echo "✅ Code quality and unit tests passed!"

ci-test: lint type-check security-scan test
	@echo "✅ All CI checks passed!"

# Database operations
db-init:
	@echo "🗄️ Initializing database..."
	python -c "from v2.backend.core.database import DatabaseManager; import asyncio; asyncio.run(DatabaseManager().initialize())"

db-migrate:
	@echo "🗄️ Running database migrations..."
	python -c "from v2.backend.core.database import DatabaseManager; import asyncio; dm = DatabaseManager(); asyncio.run(dm.migrate())"

# Integration testing
test-examples:
	@echo "🧪 Testing examples..."
	python examples/integrations_demo.py

# Load testing
load-test:
	@echo "⚡ Running load tests..."
	pip install locust
	locust -f tests/load_tests.py --headless --users 100 --spawn-rate 10 --run-time 30s

# Environment setup
setup-hooks:
	@echo "🔗 Setting up git hooks..."
	cp .githooks/pre-commit .git/hooks/pre-commit
	cp .githooks/pre-push .git/hooks/pre-push
	chmod +x .git/hooks/pre-commit .git/hooks/pre-push

# Utility commands
check-deps:
	@echo "📦 Checking for outdated dependencies..."
	pip list --outdated
	cd admin-dashboard && npm outdated

update-deps:
	@echo "⬆️ Updating dependencies..."
	pip install --upgrade -e .
	pip install --upgrade -r tests/requirements.txt
	cd admin-dashboard && npm update

# Production deployment helpers
deploy-check:
	@echo "🔍 Pre-deployment checks..."
	@make lint
	@make test-unit
	@make type-check
	@echo "✅ Ready for deployment!"

# Backup and restore
backup-db:
	@echo "💾 Backing up database..."
	docker exec galion_postgres pg_dump -U galion galion > backup_$(date +%Y%m%d_%H%M%S).sql

restore-db:
	@echo "🔄 Restoring database..."
	@echo "Usage: make restore-db FILE=backup_file.sql"
	@if [ -z "$(FILE)" ]; then echo "Error: FILE parameter required"; exit 1; fi
	docker exec -i galion_postgres psql -U galion galion < $(FILE)

# Monitoring
logs:
	@echo "📋 Showing application logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "📋 Showing frontend logs..."
	docker-compose logs -f frontend

# Emergency commands
emergency-stop:
	@echo "🚨 Emergency stop - killing all related processes..."
	pkill -f "uvicorn.*galion" || true
	pkill -f "next.*dev" || true
	docker-compose down --remove-orphans || true

# Information
info:
	@echo "ℹ️ Galion System Information"
	@echo "Python version: $$(python --version)"
	@echo "Node version: $$(cd admin-dashboard && node --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$(docker-compose --version)"
	@echo ""
	@echo "Environment variables:"
	@echo "  PYTHONPATH: $$PYTHONPATH"
	@echo "  GALION_ENV: $$GALION_ENV"
