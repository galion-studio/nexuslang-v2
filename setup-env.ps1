# ==============================================================================
# PROJECT NEXUS - Environment Setup Script
# Generates .env file with secure keys
# ==============================================================================

Write-Host ""
Write-Host "PROJECT NEXUS - Environment Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Generate secure random passwords
Write-Host "Generating secure passwords..." -ForegroundColor Yellow

$POSTGRES_PASS = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
$REDIS_PASS = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
$SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
$JWT_SECRET = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 128 | ForEach-Object {[char]$_})
$GRAFANA_PASS = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})

Write-Host "Secure passwords generated" -ForegroundColor Green

# Create .env file content
$envContent = @"
# ==============================================================================
#                PROJECT NEXUS - ENVIRONMENT CONFIGURATION
#                         NexusLang v2 Platform
#                           November 2025
# ==============================================================================
#
# SECURITY WARNING: This file contains sensitive credentials
# NEVER commit this file to version control
# Keep this file secure and backed up safely
#

# ==============================================================================
# REQUIRED - CORE INFRASTRUCTURE (ALREADY CONFIGURED)
# ==============================================================================

# Database - PostgreSQL with pgvector
POSTGRES_USER=nexus
POSTGRES_PASSWORD=$POSTGRES_PASS
POSTGRES_DB=nexus_v2
DATABASE_URL=postgresql://nexus:$POSTGRES_PASS@postgres:5432/nexus_v2

# Cache - Redis
REDIS_PASSWORD=$REDIS_PASS
REDIS_URL=redis://:$REDIS_PASS@redis:6379/0

# Security Keys - JWT and Application
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

# Search - Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Monitoring - Grafana
GRAFANA_PASSWORD=$GRAFANA_PASS
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_PASS

# ==============================================================================
# AI/ML SERVICES - REQUIRED FOR AI FEATURES
# ==============================================================================

# OpenAI API - For GPT models and Whisper STT
# Get your key from: https://platform.openai.com/api-keys
# Pricing: Pay-as-you-go, ~`$0.002/1K tokens (GPT-4)
OPENAI_API_KEY=
OPENAI_ORG_ID=
OPENAI_WHISPER_MODEL=whisper-1

# OpenRouter API - For enhanced AI routing and fallbacks
# Get your key from: https://openrouter.ai/keys
# Pricing: Pay per model used
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4-turbo

# ==============================================================================
# VOICE SERVICES - OPTIONAL (for voice features)
# ==============================================================================

# ElevenLabs API - Text-to-Speech
# Get your key from: https://elevenlabs.io/speech-synthesis
# Free tier: 10,000 characters/month
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_monolingual_v1

# Voice Settings
VOICE_MAX_AUDIO_SIZE_MB=10
VOICE_MAX_DURATION_SECONDS=30
VOICE_RATE_LIMIT_PER_HOUR=100

# ==============================================================================
# E-COMMERCE - OPTIONAL (for marketplace features)
# ==============================================================================

# Shopify Integration
# Get credentials from: https://partners.shopify.com/
# Required only if using Shopify marketplace integration
SHOPIFY_API_KEY=
SHOPIFY_API_SECRET=
SHOPIFY_ACCESS_TOKEN=
SHOPIFY_WEBHOOK_SECRET=
SHOPIFY_STORE_URL=

# ==============================================================================
# SOCIAL MEDIA PLATFORMS - OPTIONAL (for content management)
# ==============================================================================

# Twitter/X API
# Get from: https://developer.twitter.com/
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TWITTER_BEARER_TOKEN=

# Reddit API
# Get from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=
REDDIT_USER_AGENT=NexusLang-Bot/1.0

# LinkedIn API
# Get from: https://www.linkedin.com/developers/
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=

# Facebook/Instagram API
# Get from: https://developers.facebook.com/
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_ACCESS_TOKEN=

# TikTok API
# Get from: https://developers.tiktok.com/
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=

# YouTube API
# Get from: https://console.cloud.google.com/
YOUTUBE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=

# Product Hunt API
# Get from: https://api.producthunt.com/v2/docs
PRODUCTHUNT_API_KEY=

# Dev.to API
# Get from: https://dev.to/settings/extensions
DEV_TO_API_KEY=

# ==============================================================================
# CLOUD SERVICES - OPTIONAL (for production deployment)
# ==============================================================================

# Cloudflare - CDN, DNS, and R2 Storage
# Get from: https://dash.cloudflare.com/
CLOUDFLARE_ZONE_ID=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_KEY=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_EMAIL=

# Cloudflare R2 Storage (S3-compatible object storage)
CLOUDFLARE_R2_ACCOUNT_ID=
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=
CLOUDFLARE_R2_BUCKET_NAME=nexus-content
CLOUDFLARE_R2_PUBLIC_URL=https://content.galion.app

# Cloudflare Tunnel (for secure production deployment)
CLOUDFLARE_TUNNEL_TOKEN=
CLOUDFLARE_TUNNEL_ID=

# Alternative S3-Compatible Storage
S3_ENDPOINT=
S3_BUCKET=nexuslang-storage
S3_ACCESS_KEY=
S3_SECRET_KEY=

# ==============================================================================
# EMAIL SERVICE - OPTIONAL (for notifications)
# ==============================================================================

# SMTP Configuration
# For Gmail: Enable "App Passwords" in Google Account settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@nexuslang.dev

# ==============================================================================
# MONITORING - OPTIONAL (for production)
# ==============================================================================

# Sentry - Error Tracking
# Get from: https://sentry.io/
SENTRY_DSN=
SENTRY_ENVIRONMENT=development

# ==============================================================================
# APPLICATION SETTINGS
# ==============================================================================

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS - Allowed Origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# Security Settings
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_REQUEST_LOGGING=true
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
SESSION_TIMEOUT_MINUTES=60

# Feature Flags
ENABLE_GROKOPEDIA=true
ENABLE_VOICE=true
ENABLE_COMMUNITY=true
ENABLE_BILLING=true

# Billing/Credits
FREE_TIER_CREDITS=100
PRO_TIER_CREDITS=10000
ENTERPRISE_TIER_CREDITS=999999
CREDIT_COST_PER_1K_TOKENS=1

# Domain Configuration
PRIMARY_DOMAIN=localhost
API_DOMAIN=localhost:8000
APP_DOMAIN=localhost:3000
GRAFANA_DOMAIN=localhost:3001

# ==============================================================================
# QUICK START CHECKLIST
# ==============================================================================
#
# 1. Core infrastructure is ready (PostgreSQL, Redis, JWT keys generated)
# 
# 2. ADD THESE KEYS to get started with AI features:
#    - OPENAI_API_KEY (Required for NexusLang AI)
#    - Get from: https://platform.openai.com/api-keys
#
# 3. START YOUR SERVICES:
#    Run: docker-compose up -d
#
# 4. ACCESS YOUR SERVICES:
#    - Frontend: http://localhost:3000
#    - Backend API: http://localhost:8000
#    - API Docs: http://localhost:8000/docs
#    - Grafana: http://localhost:3001 (admin/$GRAFANA_PASS)
#    - PostgreSQL: localhost:5432
#    - Redis: localhost:6379
#
# 5. OPTIONAL: Add other API keys as needed for specific features
#
# ==============================================================================
"@

# Write .env file
Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "DONE - .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GENERATED CREDENTIALS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Grafana Admin:" -ForegroundColor White
Write-Host "     Username: admin" -ForegroundColor Gray
Write-Host "     Password: $GRAFANA_PASS" -ForegroundColor Gray
Write-Host ""
Write-Host "  Database:" -ForegroundColor White
Write-Host "     User: nexus" -ForegroundColor Gray
Write-Host "     Password: [Generated - see .env file]" -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Get your OpenAI API key:" -ForegroundColor White
Write-Host "     https://platform.openai.com/api-keys" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Add it to .env file:" -ForegroundColor White
Write-Host "     Open .env and add your key to OPENAI_API_KEY=" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Start the services:" -ForegroundColor White
Write-Host "     docker-compose up -d" -ForegroundColor Green
Write-Host ""
Write-Host "  4. Access your platform:" -ForegroundColor White
Write-Host "     Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "     Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "     API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "     Grafana:   http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SECURITY REMINDER:" -ForegroundColor Red
Write-Host "   - .env file contains sensitive data" -ForegroundColor Yellow
Write-Host "   - NEVER commit .env to version control" -ForegroundColor Yellow
Write-Host "   - Keep it backed up securely" -ForegroundColor Yellow
Write-Host ""
