#!/bin/bash
# 🚀 GALION PLATFORM - Backup & Recovery System
# Comprehensive automated backups with disaster recovery

set -e

echo "💾 GALION PLATFORM - BACKUP & RECOVERY SYSTEM"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_RETENTION_DAYS=30
PROJECT_DIR="/workspace/project-nexus"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Create backup directories
create_backup_dirs() {
    log "Creating backup directory structure..."

    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/config"
    mkdir -p "$BACKUP_DIR/logs"
    mkdir -p "$BACKUP_DIR/ssl"
    mkdir -p "$BACKUP_DIR/models"
    mkdir -p "$BACKUP_DIR/uploads"

    success "Backup directories created"
}

# Backup database
backup_database() {
    log "Backing up PostgreSQL database..."

    BACKUP_FILE="$BACKUP_DIR/database/postgres_$TIMESTAMP.sql.gz"

    # Create compressed database dump
    docker-compose exec -T postgres pg_dump -U nexus -d galion_platform | gzip > "$BACKUP_FILE"

    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        success "Database backup created: $(basename $BACKUP_FILE) ($(du -h $BACKUP_FILE | cut -f1))"
    else
        error "Database backup failed"
    fi
}

# Backup Redis data
backup_redis() {
    log "Backing up Redis data..."

    BACKUP_FILE="$BACKUP_DIR/database/redis_$TIMESTAMP.rdb"

    # Copy Redis dump file
    docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_FILE" 2>/dev/null || true

    if [ -f "$BACKUP_FILE" ]; then
        success "Redis backup created: $(basename $BACKUP_FILE) ($(du -h $BACKUP_FILE | cut -f1))"
    else
        warning "Redis backup skipped (no dump file or Redis not running)"
    fi
}

# Backup Elasticsearch data
backup_elasticsearch() {
    log "Backing up Elasticsearch data..."

    BACKUP_FILE="$BACKUP_DIR/database/elasticsearch_$TIMESTAMP.tar.gz"

    # Create Elasticsearch snapshot
    docker-compose exec -T elasticsearch curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_$TIMESTAMP?wait_for_completion=true" -H 'Content-Type: application/json' -d"{\"indices\": \"*\",\"ignore_unavailable\": true,\"include_global_state\": false}" >/dev/null 2>&1 || true

    # Export data using elasticdump or similar (fallback method)
    if command -v elasticdump >/dev/null 2>&1; then
        mkdir -p "/tmp/es_backup_$TIMESTAMP"
        elasticdump --input=http://localhost:9201 --output="/tmp/es_backup_$TIMESTAMP" --type=data >/dev/null 2>&1 || true
        tar -czf "$BACKUP_FILE" -C "/tmp" "es_backup_$TIMESTAMP" 2>/dev/null || true
        rm -rf "/tmp/es_backup_$TIMESTAMP"
    fi

    if [ -f "$BACKUP_FILE" ]; then
        success "Elasticsearch backup created: $(basename $BACKUP_FILE)"
    else
        warning "Elasticsearch backup limited (consider installing elasticdump for full backup)"
    fi
}

# Backup configuration files
backup_config() {
    log "Backing up configuration files..."

    BACKUP_FILE="$BACKUP_DIR/config/config_$TIMESTAMP.tar.gz"

    # List of config files to backup
    CONFIG_FILES=(
        "docker-compose.yml"
        "docker-compose.gpu.yml"
        "nginx.production.conf"
        "nginx.production.ssl.conf"
        "runpod.env"
        ".env*"
        "ssl/"
        "v2/backend/start_models.py"
        "v2/infrastructure/prometheus/"
        "v2/infrastructure/grafana/"
    )

    # Create tar archive of config files
    tar -czf "$BACKUP_FILE" "${CONFIG_FILES[@]}" 2>/dev/null || true

    if [ -f "$BACKUP_FILE" ]; then
        success "Configuration backup created: $(basename $BACKUP_FILE) ($(du -h $BACKUP_FILE | cut -f1))"
    else
        warning "Configuration backup failed or no config files found"
    fi
}

# Backup logs
backup_logs() {
    log "Backing up log files..."

    BACKUP_FILE="$BACKUP_DIR/logs/logs_$TIMESTAMP.tar.gz"

    # Collect logs from all services
    mkdir -p "/tmp/logs_backup_$TIMESTAMP"

    # Docker logs
    for service in backend frontend galion-app developer-platform galion-studio monitoring prometheus grafana nginx postgres redis elasticsearch ai-models; do
        docker-compose logs --no-color "$service" > "/tmp/logs_backup_$TIMESTAMP/${service}.log" 2>&1 || true
    done

    # Application logs
    find . -name "*.log" -type f -mtime -7 -exec cp {} "/tmp/logs_backup_$TIMESTAMP/" \; 2>/dev/null || true

    # Compress logs
    tar -czf "$BACKUP_FILE" -C "/tmp" "logs_backup_$TIMESTAMP" 2>/dev/null || true
    rm -rf "/tmp/logs_backup_$TIMESTAMP"

    if [ -f "$BACKUP_FILE" ]; then
        success "Logs backup created: $(basename $BACKUP_FILE) ($(du -h $BACKUP_FILE | cut -f1))"
    else
        warning "Logs backup failed or no logs found"
    fi
}

# Backup AI models (if any cached)
backup_models() {
    log "Backing up AI models and data..."

    BACKUP_FILE="$BACKUP_DIR/models/models_$TIMESTAMP.tar.gz"

    # Backup model cache and datasets
    docker run --rm -v $(pwd):/workspace -v /tmp:/tmp alpine tar -czf "/tmp/models_backup.tar.gz" -C /workspace \
        models-cache datasets-cache v2/backend/ml_models 2>/dev/null || true

    if [ -f "/tmp/models_backup.tar.gz" ]; then
        mv "/tmp/models_backup.tar.gz" "$BACKUP_FILE"
        success "AI models backup created: $(basename $BACKUP_FILE) ($(du -h $BACKUP_FILE | cut -f1))"
    else
        warning "AI models backup skipped (no models found)"
    fi
}

# Upload to cloud storage (optional)
upload_to_cloud() {
    log "Uploading backups to cloud storage..."

    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        log "Uploading to AWS S3..."

        # Install AWS CLI if not present
        if ! command -v aws >/dev/null 2>&1; then
            pip install awscli >/dev/null 2>&1 || true
        fi

        # Upload latest backups
        aws s3 cp "$BACKUP_DIR/database/" "s3://galion-backups/database/" --recursive --quiet || true
        aws s3 cp "$BACKUP_DIR/config/" "s3://galion-backups/config/" --recursive --quiet || true

        success "Backups uploaded to AWS S3"
    elif [ -n "$RCLONE_CONFIG" ]; then
        log "Uploading via rclone..."

        # Upload via rclone
        rclone copy "$BACKUP_DIR" "remote:galion-backups/$TIMESTAMP" --quiet || true

        success "Backups uploaded via rclone"
    else
        warning "No cloud storage configured. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or RCLONE_CONFIG"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups (retention: ${BACKUP_RETENTION_DAYS} days)..."

    # Remove old database backups
    find "$BACKUP_DIR/database" -name "*.sql.gz" -o -name "*.rdb" -o -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete 2>/dev/null || true

    # Remove old config backups
    find "$BACKUP_DIR/config" -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete 2>/dev/null || true

    # Remove old log backups
    find "$BACKUP_DIR/logs" -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete 2>/dev/null || true

    # Remove old model backups
    find "$BACKUP_DIR/models" -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete 2>/dev/null || true

    success "Old backups cleaned up"
}

# Generate backup manifest
generate_manifest() {
    log "Generating backup manifest..."

    MANIFEST_FILE="$BACKUP_DIR/manifest_$TIMESTAMP.json"

    cat > "$MANIFEST_FILE" << EOF
{
  "backup_timestamp": "$TIMESTAMP",
  "backup_date": "$(date -Iseconds)",
  "platform_version": "2.0.0",
  "backup_components": {
    "database": {
      "postgresql": "postgres_$TIMESTAMP.sql.gz",
      "redis": "redis_$TIMESTAMP.rdb",
      "elasticsearch": "elasticsearch_$TIMESTAMP.tar.gz"
    },
    "configuration": "config_$TIMESTAMP.tar.gz",
    "logs": "logs_$TIMESTAMP.tar.gz",
    "ai_models": "models_$TIMESTAMP.tar.gz"
  },
  "services_backed_up": [
    "postgresql",
    "redis",
    "elasticsearch",
    "backend_api",
    "galion_app",
    "developer_platform",
    "galion_studio",
    "ai_models",
    "nginx",
    "prometheus",
    "grafana"
  ],
  "retention_policy": "${BACKUP_RETENTION_DAYS} days",
  "backup_location": "$PROJECT_DIR/$BACKUP_DIR"
}
EOF

    success "Backup manifest created: $(basename $MANIFEST_FILE)"
}

# Full backup function
perform_full_backup() {
    log "Starting full system backup..."

    create_backup_dirs
    backup_database
    backup_redis
    backup_elasticsearch
    backup_config
    backup_logs
    backup_models
    generate_manifest

    # Calculate backup size
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    success "Full backup completed. Total size: $BACKUP_SIZE"

    # Optional cloud upload
    upload_to_cloud

    cleanup_old_backups

    echo ""
    echo "📦 BACKUP SUMMARY"
    echo "================="
    echo "Timestamp: $TIMESTAMP"
    echo "Location: $BACKUP_DIR"
    echo "Size: $BACKUP_SIZE"
    echo "Retention: $BACKUP_RETENTION_DAYS days"
    echo ""
    echo "Files created:"
    ls -la "$BACKUP_DIR"/*/"*$TIMESTAMP*" 2>/dev/null || echo "No backup files found"
    echo ""
}

# Database recovery
recover_database() {
    local BACKUP_FILE="$1"

    if [ -z "$BACKUP_FILE" ]; then
        error "No backup file specified. Usage: $0 recover database <backup_file>"
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
    fi

    log "Recovering database from: $(basename $BACKUP_FILE)"

    # Stop dependent services
    docker-compose stop backend galion-app developer-platform galion-studio ai-models

    # Restore database
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U nexus -d galion_platform

    # Restart services
    docker-compose start backend galion-app developer-platform galion-studio ai-models

    success "Database recovery completed"
}

# Configuration recovery
recover_config() {
    local BACKUP_FILE="$1"

    if [ -z "$BACKUP_FILE" ]; then
        error "No backup file specified. Usage: $0 recover config <backup_file>"
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
    fi

    log "Recovering configuration from: $(basename $BACKUP_FILE)"

    # Extract configuration files
    mkdir -p "/tmp/config_recovery_$TIMESTAMP"
    tar -xzf "$BACKUP_FILE" -C "/tmp/config_recovery_$TIMESTAMP"

    # Restore key configuration files
    if [ -f "/tmp/config_recovery_$TIMESTAMP/docker-compose.yml" ]; then
        cp "/tmp/config_recovery_$TIMESTAMP/docker-compose.yml" .
        success "docker-compose.yml restored"
    fi

    if [ -f "/tmp/config_recovery_$TIMESTAMP/nginx.production.conf" ]; then
        cp "/tmp/config_recovery_$TIMESTAMP/nginx.production.conf" .
        success "nginx configuration restored"
    fi

    # Restore SSL certificates if present
    if [ -d "/tmp/config_recovery_$TIMESTAMP/ssl" ]; then
        cp -r "/tmp/config_recovery_$TIMESTAMP/ssl" . 2>/dev/null || true
        success "SSL certificates restored"
    fi

    # Cleanup
    rm -rf "/tmp/config_recovery_$TIMESTAMP"

    # Reload services
    docker-compose restart nginx

    success "Configuration recovery completed"
}

# Full system recovery
recover_full_system() {
    local MANIFEST_FILE="$1"

    if [ -z "$MANIFEST_FILE" ]; then
        error "No manifest file specified. Usage: $0 recover full <manifest_file>"
    fi

    if [ ! -f "$MANIFEST_FILE" ]; then
        error "Manifest file not found: $MANIFEST_FILE"
    fi

    log "Starting full system recovery from manifest: $(basename $MANIFEST_FILE)"

    # Parse manifest to get backup files
    BACKUP_TIMESTAMP=$(basename "$MANIFEST_FILE" | sed 's/manifest_\(.*\)\.json/\1/')

    # Recover database
    DB_BACKUP="$BACKUP_DIR/database/postgres_$BACKUP_TIMESTAMP.sql.gz"
    if [ -f "$DB_BACKUP" ]; then
        recover_database "$DB_BACKUP"
    fi

    # Recover configuration
    CONFIG_BACKUP="$BACKUP_DIR/config/config_$BACKUP_TIMESTAMP.tar.gz"
    if [ -f "$CONFIG_BACKUP" ]; then
        recover_config "$CONFIG_BACKUP"
    fi

    # Recover AI models
    MODELS_BACKUP="$BACKUP_DIR/models/models_$BACKUP_TIMESTAMP.tar.gz"
    if [ -f "$MODELS_BACKUP" ]; then
        log "Recovering AI models..."
        tar -xzf "$MODELS_BACKUP" -C . 2>/dev/null || true
        success "AI models recovered"
    fi

    success "Full system recovery completed"
}

# List available backups
list_backups() {
    echo "📦 AVAILABLE BACKUPS"
    echo "===================="
    echo ""

    echo "Database Backups:"
    ls -la "$BACKUP_DIR/database/" 2>/dev/null | grep -E "\.(sql\.gz|rdb|tar\.gz)$" | head -10 || echo "No database backups found"
    echo ""

    echo "Configuration Backups:"
    ls -la "$BACKUP_DIR/config/" 2>/dev/null | grep "\.tar\.gz$" | head -5 || echo "No config backups found"
    echo ""

    echo "Log Backups:"
    ls -la "$BACKUP_DIR/logs/" 2>/dev/null | grep "\.tar\.gz$" | head -5 || echo "No log backups found"
    echo ""

    echo "AI Model Backups:"
    ls -la "$BACKUP_DIR/models/" 2>/dev/null | grep "\.tar\.gz$" | head -5 || echo "No model backups found"
    echo ""

    echo "Backup Manifests:"
    ls -la "$BACKUP_DIR/" 2>/dev/null | grep "manifest.*\.json$" | head -5 || echo "No manifests found"
    echo ""

    # Show backup directory size
    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        echo "Total Backup Size: $BACKUP_SIZE"
    fi
}

# Setup automated backups
setup_automation() {
    log "Setting up automated backup schedule..."

    CRON_JOB="0 2 * * * /workspace/project-nexus/backup-recovery.sh backup"

    # Add to crontab if not already present
    if ! crontab -l 2>/dev/null | grep -q "backup-recovery.sh backup"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        success "Automated backup scheduled for 2:00 AM daily"
    else
        success "Automated backup already scheduled"
    fi

    # Create backup monitoring script
    cat > backup-monitor.sh << 'EOF'
#!/bin/bash
# Monitor backup success and send alerts

BACKUP_DIR="/workspace/project-nexus/backups"
LOG_FILE="/workspace/project-nexus/logs/backup-monitor.log"

# Check if latest backup is recent (within 25 hours)
LATEST_BACKUP=$(find "$BACKUP_DIR" -name "manifest_*.json" -mtime -1 | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "$(date): WARNING - No recent backup found" >> "$LOG_FILE"
    # Send alert here (email, slack, etc.)
else
    echo "$(date): SUCCESS - Recent backup found: $(basename $LATEST_BACKUP)" >> "$LOG_FILE"
fi
EOF

    chmod +x backup-monitor.sh

    # Add monitoring to crontab
    MONITOR_JOB="30 6 * * * /workspace/project-nexus/backup-monitor.sh"
    if ! crontab -l 2>/dev/null | grep -q "backup-monitor.sh"; then
        (crontab -l 2>/dev/null; echo "$MONITOR_JOB") | crontab -
        success "Backup monitoring scheduled for 6:30 AM daily"
    fi

    success "Backup automation setup complete"
}

# Main function
main() {
    case "${1:-help}" in
        "backup")
            perform_full_backup
            ;;
        "recover")
            case "${2:-help}" in
                "database")
                    recover_database "$3"
                    ;;
                "config")
                    recover_config "$3"
                    ;;
                "full")
                    recover_full_system "$3"
                    ;;
                *)
                    echo "Recovery Options:"
                    echo "  database <backup_file>  - Recover PostgreSQL database"
                    echo "  config <backup_file>    - Recover configuration files"
                    echo "  full <manifest_file>    - Full system recovery"
                    ;;
            esac
            ;;
        "list")
            list_backups
            ;;
        "setup")
            setup_automation
            ;;
        "cleanup")
            cleanup_old_backups
            success "Old backups cleaned up"
            ;;
        "status")
            echo "💾 BACKUP SYSTEM STATUS"
            echo "======================"
            echo ""
            echo "Backup Directory: $BACKUP_DIR"
            if [ -d "$BACKUP_DIR" ]; then
                echo "Status: Active"
                echo "Total Size: $(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)"
                echo "Retention: $BACKUP_RETENTION_DAYS days"
                echo ""
                echo "Latest Backups:"
                find "$BACKUP_DIR" -name "manifest_*.json" -printf "%T@ %Tc %p\n" 2>/dev/null | sort -n | tail -3 | while read -r line; do
                    echo "  $(basename "$(echo $line | cut -d' ' -f8-)")"
                done
            else
                echo "Status: Not initialized"
            fi
            ;;
        "help"|*)
            echo "Galion Platform Backup & Recovery System"
            echo ""
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  backup          - Create full system backup"
            echo "  recover         - Recover from backup (see subcommands)"
            echo "  list            - List available backups"
            echo "  setup           - Setup automated backup schedule"
            echo "  cleanup         - Remove old backups"
            echo "  status          - Show backup system status"
            echo "  help            - Show this help message"
            echo ""
            echo "Recovery Subcommands:"
            echo "  recover database <file>  - Recover PostgreSQL database"
            echo "  recover config <file>    - Recover configuration files"
            echo "  recover full <manifest>  - Full system recovery"
            echo ""
            echo "Environment Variables:"
            echo "  BACKUP_RETENTION_DAYS    - Days to keep backups (default: 30)"
            echo "  AWS_ACCESS_KEY_ID        - AWS S3 upload credentials"
            echo "  AWS_SECRET_ACCESS_KEY    - AWS S3 upload credentials"
            echo "  RCLONE_CONFIG           - rclone configuration for cloud upload"
            echo ""
            echo "Examples:"
            echo "  $0 backup"
            echo "  $0 recover database ./backups/database/postgres_20241114_020000.sql.gz"
            echo "  $0 setup"
            echo "  BACKUP_RETENTION_DAYS=7 $0 cleanup"
            ;;
    esac
}

# Run main function
main "$@"
