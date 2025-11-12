#!/bin/bash
# Quick Security Scan Script
# Run this anytime to check your codebase security

echo "🔒 Running comprehensive security scan..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track issues found
ISSUES_FOUND=0

# Change to backend directory
cd v2/backend

# 1. Dependency vulnerabilities
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Checking dependency vulnerabilities..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pip-audit -r requirements.txt 2>/dev/null; then
    echo -e "${GREEN}✅ No known vulnerabilities in dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in dependencies!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 2. Secret scanning
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Scanning for exposed secrets..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if detect-secrets scan --baseline ../../.secrets.baseline . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ No secrets detected${NC}"
else
    echo -e "${RED}❌ Potential secrets found!${NC}"
    detect-secrets scan .
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 3. Static security analysis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Running static security analysis (Bandit)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if bandit -r . -ll 2>/dev/null; then
    echo -e "${GREEN}✅ No high/medium severity issues found${NC}"
else
    echo -e "${YELLOW}⚠️  Security issues found (see above)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 4. Security tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Running security test suite..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
export JWT_SECRET_KEY="test-secret-for-ci-only-min-32-chars-long"
export DATABASE_URL="sqlite+aiosqlite:///./test.db"

if pytest tests/test_security.py -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✅ All security tests passed${NC}"
else
    echo -e "${RED}❌ Security tests failed!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 5. Check for hardcoded credentials
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Checking for hardcoded credentials..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CREDS=$(grep -r "password.*=.*['\"]" . --include="*.py" | grep -v "password_hash" | grep -v "test" | grep -v ".pyc" || true)
if [ -z "$CREDS" ]; then
    echo -e "${GREEN}✅ No hardcoded credentials found${NC}"
else
    echo -e "${RED}❌ Possible hardcoded credentials:${NC}"
    echo "$CREDS"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 6. Check environment configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Checking environment configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$JWT_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET_KEY not set in environment${NC}"
fi

if [ -f "../../.env" ]; then
    if grep -q "your-secret-key-change-in-production" ../../.env; then
        echo -e "${RED}❌ Default secrets found in .env!${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ .env file configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
fi
echo ""

# 7. Check security headers configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Checking security headers configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if grep -q "SecurityHeadersMiddleware" main.py; then
    echo -e "${GREEN}✅ Security headers middleware configured${NC}"
else
    echo -e "${RED}❌ Security headers middleware not configured!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if grep -q "RateLimitMiddleware" main.py; then
    echo -e "${GREEN}✅ Rate limiting middleware configured${NC}"
else
    echo -e "${RED}❌ Rate limiting middleware not configured!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# Summary
cd ../..
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SECURITY SCAN SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo ""
    echo "Your codebase looks secure. Deploy with confidence! 🚀"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES_FOUND issue(s) that need attention${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review the issues above"
    echo "  2. Fix critical/high priority issues"
    echo "  3. Run this script again to verify fixes"
    echo "  4. Check: SECURITY_AUDIT_REPORT.md for details"
    echo ""
    exit 1
fi

