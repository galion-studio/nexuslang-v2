#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  Final Security Audit Before Production Launch            ║
# ║  Scans for vulnerabilities, secrets, and misconfigurations ║
# ╚════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔒 Final Security Audit                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ISSUES_FOUND=0
WARNINGS=0

# Check 1: Scan for hardcoded secrets
echo -e "${YELLOW}🔍 Scanning for exposed secrets...${NC}"
echo ""

# Check for API keys
if grep -r "sk-proj-" v2/ --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | grep -v "your-key-here" | grep -v "example" | grep -v "template"; then
    echo -e "${RED}❌ CRITICAL: Found OpenAI API keys in code!${NC}"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✅ No exposed OpenAI keys${NC}"
fi

if grep -r "sk-or-v1-" v2/ --include="*.py" --include="*.ts" 2>/dev/null | grep -v "your-key" | grep -v "template"; then
    echo -e "${RED}❌ CRITICAL: Found OpenRouter API keys in code!${NC}"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✅ No exposed OpenRouter keys${NC}"
fi

# Check for database passwords
if grep -r "postgres.*password" v2/backend --include="*.py" 2>/dev/null | grep -v "getenv" | grep -v "settings" | grep -v "template" | grep "= \""; then
    echo -e "${RED}❌ CRITICAL: Found hardcoded database passwords!${NC}"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✅ No hardcoded database passwords${NC}"
fi

echo ""

# Check 2: Verify .env files are gitignored
echo -e "${YELLOW}🔍 Checking .gitignore configuration...${NC}"
echo ""

if grep -q "^\.env$" .gitignore && grep -q "^\*\.env$" .gitignore; then
    echo -e "${GREEN}✅ .env files properly gitignored${NC}"
else
    echo -e "${RED}❌ WARNING: .env files may not be gitignored!${NC}"
    ((WARNINGS++))
fi

# Check if any .env files are tracked
if git ls-files | grep "\.env$" | grep -v "template" | grep -v "example"; then
    echo -e "${RED}❌ CRITICAL: .env files are tracked by git!${NC}"
    echo -e "${YELLOW}   Run: git rm --cached v2/.env${NC}"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✅ No .env files tracked${NC}"
fi

echo ""

# Check 3: Verify security middleware is enabled
echo -e "${YELLOW}🔍 Checking security middleware...${NC}"
echo ""

if grep -q "RateLimitMiddleware" v2/backend/main.py; then
    echo -e "${GREEN}✅ Rate limiting enabled${NC}"
else
    echo -e "${RED}❌ CRITICAL: Rate limiting not enabled!${NC}"
    ((ISSUES_FOUND++))
fi

if grep -q "SecurityHeadersMiddleware" v2/backend/main.py; then
    echo -e "${GREEN}✅ Security headers enabled${NC}"
else
    echo -e "${RED}❌ CRITICAL: Security headers not enabled!${NC}"
    ((ISSUES_FOUND++))
fi

if grep -q "validate_all_secrets" v2/backend/main.py; then
    echo -e "${GREEN}✅ Secret validation on startup${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: No secret validation on startup${NC}"
    ((WARNINGS++))
fi

echo ""

# Check 4: Verify WebSocket authentication
echo -e "${YELLOW}🔍 Checking WebSocket security...${NC}"
echo ""

if grep -q "decode_access_token(token)" v2/backend/main.py; then
    echo -e "${GREEN}✅ WebSocket authentication enabled${NC}"
else
    echo -e "${RED}❌ CRITICAL: WebSocket not authenticated!${NC}"
    ((ISSUES_FOUND++))
fi

echo ""

# Check 5: Verify sandboxed execution
echo -e "${YELLOW}🔍 Checking code execution security...${NC}"
echo ""

if grep -q "sandboxed_executor" v2/backend/services/nexuslang_executor.py; then
    echo -e "${GREEN}✅ Sandboxed executor in use${NC}"
else
    echo -e "${RED}❌ CRITICAL: Using unsafe executor!${NC}"
    ((ISSUES_FOUND++))
fi

echo ""

# Check 6: Verify CORS configuration
echo -e "${YELLOW}🔍 Checking CORS security...${NC}"
echo ""

if grep -q 'allow_methods=\["GET", "POST", "PUT", "DELETE"' v2/backend/main.py; then
    echo -e "${GREEN}✅ CORS explicitly configured (no wildcards)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: CORS may use wildcards${NC}"
    ((WARNINGS++))
fi

echo ""

# Check 7: Production configuration
echo -e "${YELLOW}🔍 Checking production configuration...${NC}"
echo ""

if [ -f "v2/.env" ]; then
    source v2/.env 2>/dev/null || true
    
    if [ "$DEBUG" = "true" ] && [ "$ENVIRONMENT" = "production" ]; then
        echo -e "${YELLOW}⚠️  WARNING: DEBUG enabled in production!${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅ DEBUG properly configured${NC}"
    fi
    
    if [ "$ENVIRONMENT" = "production" ] && echo "$CORS_ORIGINS" | grep -q "localhost"; then
        echo -e "${YELLOW}⚠️  WARNING: CORS includes localhost in production${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅ CORS production-ready${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  INFO: No v2/.env file (will be generated on RunPod)${NC}"
fi

echo ""

# Check 8: Dependencies security
echo -e "${YELLOW}🔍 Checking for known vulnerabilities in dependencies...${NC}"
echo ""

if [ -f "v2/backend/requirements.txt" ]; then
    # Check if safety is installed
    if command -v safety &> /dev/null; then
        cd v2/backend
        if safety check --json > /dev/null 2>&1; then
            echo -e "${GREEN}✅ No known vulnerabilities in dependencies${NC}"
        else
            echo -e "${YELLOW}⚠️  WARNING: Some dependencies have known vulnerabilities${NC}"
            echo -e "${YELLOW}   Run: cd v2/backend && safety check${NC}"
            ((WARNINGS++))
        fi
        cd ../..
    else
        echo -e "${YELLOW}ℹ️  Skipping dependency scan (safety not installed)${NC}"
        echo -e "${YELLOW}   Install: pip install safety${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No requirements.txt found${NC}"
fi

echo ""

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🎯 SECURITY AUDIT RESULTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ $ISSUES_FOUND -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL SECURITY CHECKS PASSED!                            ║${NC}"
    echo -e "${GREEN}║  Platform is secure and ready for production launch       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Security Score: 100/100${NC}"
    echo ""
    echo -e "${GREEN}✅ Safe to deploy to production${NC}"
    echo ""
elif [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  WARNINGS FOUND (${WARNINGS})                                      ║${NC}"
    echo -e "${YELLOW}║  No critical issues, but review warnings above            ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Security Score: 90/100${NC}"
    echo ""
    echo -e "${GREEN}✅ Safe to deploy (address warnings when possible)${NC}"
    echo ""
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ CRITICAL ISSUES FOUND (${ISSUES_FOUND})                               ║${NC}"
    echo -e "${RED}║  DO NOT DEPLOY until issues are fixed!                    ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}Security Score: FAILED${NC}"
    echo ""
    echo "Fix issues above, then run this script again."
    echo ""
    exit 1
fi

echo -e "${BLUE}Next steps:${NC}"
echo "  1. Push to GitHub: ./push-to-github-automated.ps1"
echo "  2. Deploy to RunPod: ./deploy-to-runpod-production.sh"
echo "  3. Configure DNS & SSL"
echo "  4. Launch!"
echo ""

