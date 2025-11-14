#!/bin/bash
# Nexus Lang V2 Scientific Knowledge Enhancement - RunPod Environment Template
# ============================================================================
#
# This script sets up the environment variables needed for RunPod deployment.
# Copy this file and customize the values for your deployment.
#
# Usage:
#   source runpod-env-template.sh
#   # Then edit the variables below
#   ./deploy-runpod.sh deploy

# ============================================================================
# REQUIRED SETTINGS - YOU MUST CONFIGURE THESE
# ============================================================================

# RunPod API Key (REQUIRED)
# Get from: https://runpod.io/console/user/settings
export RUNPOD_API_KEY="your_runpod_api_key_here"

# ============================================================================
# OPTIONAL SETTINGS - Defaults provided
# ============================================================================

# Docker Configuration
export DOCKER_REGISTRY="runpod"
export IMAGE_TAG="latest"

# Application Settings
export LOG_LEVEL="INFO"
export PYTHONPATH="/workspace"

# Agent Configuration
export MAX_CONCURRENT_AGENTS="5"
export AGENT_TIMEOUT="60"

# Transparency System
export TRANSPARENCY_RETENTION_DAYS="30"
export TRANSPARENCY_LOG_LEVEL="INFO"

# Caching
export CACHE_TTL="3600"
export CACHE_MAX_SIZE="1000"

# API Settings
export REQUEST_TIMEOUT="30"
export RATE_LIMIT_REQUESTS_PER_MINUTE="100"
export RATE_LIMIT_BURST="20"

# External API Keys (Optional)
# Wikipedia API: No key required
# PubChem API: No key required
# arXiv API: No key required
# CrossRef API: No key required
# Wolfram Alpha API: Get from https://products.wolframalpha.com/api/
export WOLFRAM_ALPHA_APP_ID="your_wolfram_alpha_app_id_here"

# ============================================================================
# ADVANCED SETTINGS - Usually don't need to change
# ============================================================================

# GPU Configuration (automatically set by RunPod)
export CUDA_VISIBLE_DEVICES="0"
export TORCH_USE_CUDA_DSA="1"

# Memory Management
export MEMORY_LIMIT_MB="16384"
export GPU_MEMORY_LIMIT_MB="16384"

# Network Configuration
export HOST="0.0.0.0"
export API_PORT="8000"
export DASHBOARD_PORT="8080"

# Database Configuration (SQLite for RunPod)
export DATABASE_URL="sqlite:////workspace/data/scientific.db"
export DATABASE_ECHO="false"

# Logging Configuration
export LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
export LOG_FILE="/workspace/logs/scientific.log"
export LOG_MAX_SIZE="100MB"
export LOG_BACKUP_COUNT="5"

# Security Settings
export SECRET_KEY="your_secret_key_here"
export API_KEY_ENABLED="false"
export CORS_ORIGINS="*"

# Performance Tuning
export WORKERS="2"
export THREADS_PER_WORKER="4"
export MAX_REQUESTS_PER_WORKER="1000"
export WORKER_TIMEOUT="300"

# Health Check Configuration
export HEALTH_CHECK_INTERVAL="30"
export HEALTH_CHECK_TIMEOUT="10"
export HEALTH_CHECK_RETRIES="3"

# ============================================================================
# MONITORING & METRICS
# ============================================================================

# Prometheus Metrics (if enabled)
export METRICS_ENABLED="false"
export METRICS_PORT="9090"

# External Monitoring
export HEALTH_CHECK_URL="https://hc-ping.com/your-uuid-here"

# ============================================================================
# BACKUP & RECOVERY
# ============================================================================

# Backup Configuration
export BACKUP_ENABLED="true"
export BACKUP_SCHEDULE="0 2 * * *"
export BACKUP_RETENTION_DAYS="30"
export BACKUP_PATH="/workspace/backups"

# ============================================================================
# INTEGRATION SETTINGS
# ============================================================================

# Webhook URLs for notifications
export DEPLOY_SUCCESS_WEBHOOK="https://hooks.slack.com/your-webhook-url"
export DEPLOY_FAILURE_WEBHOOK="https://hooks.slack.com/your-webhook-url"
export HEALTH_ALERT_WEBHOOK="https://hooks.slack.com/your-webhook-url"

# External Service URLs
export WIKIPEDIA_API_URL="https://en.wikipedia.org/api/rest_v1"
export PUBCHEM_API_URL="https://pubchem.ncbi.nlm.nih.gov/rest/pug"
export ARXIV_API_URL="http://export.arxiv.org/api/query"
export CROSSREF_API_URL="https://api.crossref.org"

# ============================================================================
# CUSTOMIZATION SETTINGS
# ============================================================================

# Agent Personality Settings
export PHYSICS_AGENT_CONFIDENCE_THRESHOLD="0.8"
export CHEMISTRY_AGENT_CONFIDENCE_THRESHOLD="0.85"
export MATHEMATICS_AGENT_CONFIDENCE_THRESHOLD="0.9"

# First Principles Configuration
export FIRST_PRINCIPLES_MAX_DEPTH="10"
export FIRST_PRINCIPLES_TIMEOUT="120"

# Transparency Configuration
export TRANSPARENCY_DETAIL_LEVEL="high"
export TRANSPARENCY_INCLUDE_METADATA="true"
export TRANSPARENCY_COMPRESS_OLD_DATA="true"

# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

echo "Nexus Lang V2 Scientific Knowledge Enhancement - Environment Setup"
echo "=================================================================="
echo ""
echo "This script configures environment variables for RunPod deployment."
echo ""
echo "REQUIRED: Configure your RunPod API key:"
echo "  1. Get your API key from: https://runpod.io/console/user/settings"
echo "  2. Replace 'your_runpod_api_key_here' with your actual key"
echo ""
echo "OPTIONAL: Review and customize other settings as needed."
echo ""
echo "USAGE:"
echo "  # Edit this file with your settings"
echo "  source runpod-env-template.sh"
echo "  ./deploy-runpod.sh deploy"
echo ""
echo "MONITORING:"
echo "  ./deploy-runpod.sh status    # Check deployment status"
echo "  ./deploy-runpod.sh logs      # View deployment logs"
echo "  ./deploy-runpod.sh test      # Test the deployment"
echo ""
echo "For security, never commit actual API keys to version control!"

# ============================================================================
# VALIDATION - Check required settings
# ============================================================================

if [ "$RUNPOD_API_KEY" = "your_runpod_api_key_here" ]; then
    echo ""
    echo "⚠️  WARNING: RunPod API key not configured!"
    echo "   Please edit this file and set your actual RUNPOD_API_KEY"
    echo ""
fi

echo "Environment configuration loaded."
echo "Ready to deploy with: ./deploy-runpod.sh deploy"
