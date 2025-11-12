#!/bin/bash
# Security Setup Script
# Run this to set up your development environment with security tools

set -e

echo "🔒 Setting up security tools for NexusLang v2..."
echo ""

# Check if Python 3.11+ is installed
echo "✓ Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  Found Python $python_version"

# Install pre-commit
echo ""
echo "✓ Installing pre-commit hooks..."
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
echo "  ✅ Pre-commit hooks installed"

# Install security tools
echo ""
echo "✓ Installing security scanning tools..."
pip install safety pip-audit bandit[toml] detect-secrets
echo "  ✅ Security tools installed"

# Generate secrets if not exist
echo ""
echo "✓ Generating secure secrets..."

if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp env.template .env
    
    # Generate JWT secret
    jwt_secret=$(openssl rand -hex 64)
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$jwt_secret/" .env
    
    # Generate DB password
    db_pass=$(openssl rand -base64 32)
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$db_pass/" .env
    sed -i "s/nexuspass/$db_pass/g" .env
    
    # Generate Redis password
    redis_pass=$(openssl rand -base64 32)
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$redis_pass/" .env
    
    echo "  ✅ Secrets generated and saved to .env"
else
    echo "  ⚠️  .env already exists, skipping..."
fi

# Create secrets baseline
echo ""
echo "✓ Creating secrets baseline..."
detect-secrets scan > .secrets.baseline
echo "  ✅ Secrets baseline created"

# Run initial security scan
echo ""
echo "✓ Running initial security scan..."
cd v2/backend

echo "  Checking dependencies..."
safety check -r requirements.txt || true

echo "  Scanning for secrets..."
detect-secrets scan . || true

echo "  Running Bandit..."
bandit -r . || true

cd ../..

# Set up Git hooks
echo ""
echo "✓ Setting up Git hooks..."
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook to run security tests

echo "🔒 Running security checks before push..."

# Run security tests
cd v2/backend
export JWT_SECRET_KEY="test-secret-for-ci-only-min-32-chars-long"
export DATABASE_URL="sqlite+aiosqlite:///./test.db"

pytest tests/test_security.py -v || {
    echo "❌ Security tests failed! Fix issues before pushing."
    exit 1
}

echo "✅ Security tests passed!"
exit 0
EOF

chmod +x .git/hooks/pre-push
echo "  ✅ Git hooks configured"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Security setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What was configured:"
echo "  ✅ Pre-commit hooks for secret detection"
echo "  ✅ Security scanning tools (safety, bandit, etc.)"
echo "  ✅ Secure secrets generated in .env"
echo "  ✅ Git pre-push hook for security tests"
echo ""
echo "Next steps:"
echo "  1. Review .env and update API keys if needed"
echo "  2. Run: cd v2/backend && pytest tests/test_security.py"
echo "  3. Read: SECURITY_DEPLOYMENT_CHECKLIST.md"
echo ""
echo "📚 Documentation:"
echo "  - SECURITY_AUDIT_REPORT.md"
echo "  - SECURITY_DEPLOYMENT_CHECKLIST.md"
echo "  - QUICK_START_SECURITY.md"
echo ""
echo "🔒 Stay secure!"

