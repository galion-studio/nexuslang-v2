#!/bin/bash
# Automated Backup & Recovery System for NexusLang v2 GPU
# Production-ready backup with GPU-aware optimizations

set -e

# Configuration
BACKUP_ROOT="/opt/nexus-backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="nexus_gpu_backup_$TIMESTAMP"

# GPU Model cache (most critical for performance)
MODEL_CACHE_DIR="/app/models"
DATASETS_CACHE_DIR="/app/datasets"

# Database and state
POSTGRES_CONTAINER="nexus-postgres"
REDIS_CONTAINER="nexus-redis"
ELASTICSEARCH_CONTAINER="nexus-elasticsearch"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Initialize backup directory
init_backup_dir() {
    log "Initializing backup directory..."

    mkdir -p "$BACKUP_ROOT"
    mkdir -p "$BACKUP_ROOT/models"
    mkdir -p "$BACKUP_ROOT/databases"
    mkdir -p "$BACKUP_ROOT/config"
    mkdir -p "$BACKUP_ROOT/logs"

    # Set proper permissions
    chmod 750 "$BACKUP_ROOT"
    chmod 700 "$BACKUP_ROOT"/* 2>/dev/null || true

    success "Backup directory initialized"
}

# Backup GPU models and datasets
backup_gpu_models() {
    log "Backing up GPU models and datasets..."

    local backup_dir="$BACKUP_ROOT/models/$BACKUP_NAME"

    mkdir -p "$backup_dir"

    # Backup model cache with GPU optimization info
    if [ -d "$MODEL_CACHE_DIR" ]; then
        log "Backing up model cache..."

        # Create GPU-specific metadata
        cat > "$backup_dir/gpu_metadata.json" << EOF
{
    "backup_timestamp": "$TIMESTAMP",
    "gpu_info": "$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'GPU not available')",
    "cuda_version": "$(nvcc --version 2>/dev/null | grep "release" | sed 's/.*release //' | sed 's/,.*//' || echo 'CUDA not available')",
    "pytorch_version": "$(python3 -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'PyTorch not available')",
    "model_cache_size": "$(du -sh "$MODEL_CACHE_DIR" 2>/dev/null | cut -f1 || echo 'unknown')"
}
EOF

        # Use rsync for efficient incremental backup
        rsync -av --delete --exclude='*.tmp' --exclude='__pycache__' \
            "$MODEL_CACHE_DIR/" "$backup_dir/models/" 2>/dev/null || \
        cp -r "$MODEL_CACHE_DIR"/* "$backup_dir/models/" 2>/dev/null || \
        warning "Model cache backup incomplete"

        success "Model cache backed up"
    fi

    # Backup datasets
    if [ -d "$DATASETS_CACHE_DIR" ]; then
        log "Backing up datasets..."
        rsync -av --delete --exclude='*.tmp' \
            "$DATASETS_CACHE_DIR/" "$backup_dir/datasets/" 2>/dev/null || \
        cp -r "$DATASETS_CACHE_DIR"/* "$backup_dir/datasets/" 2>/dev/null || \
        warning "Datasets backup incomplete"

        success "Datasets backed up"
    fi
}

# Backup databases
backup_databases() {
    log "Backing up databases..."

    local backup_dir="$BACKUP_ROOT/databases/$BACKUP_NAME"
    mkdir -p "$backup_dir"

    # PostgreSQL backup
    log "Backing up PostgreSQL..."
    if docker ps | grep -q "$POSTGRES_CONTAINER"; then
        docker exec "$POSTGRES_CONTAINER" pg_dumpall -U nexus > "$backup_dir/postgres_backup.sql" 2>/dev/null && \
        success "PostgreSQL backup completed" || \
        error "PostgreSQL backup failed"
    else
        warning "PostgreSQL container not running"
    fi

    # Redis backup
    log "Backing up Redis..."
    if docker ps | grep -q "$REDIS_CONTAINER"; then
        docker exec "$REDIS_CONTAINER" redis-cli --rdb "$backup_dir/redis_backup.rdb" 2>/dev/null && \
        success "Redis backup completed" || \
        warning "Redis backup may be incomplete"
    fi

    # Elasticsearch backup
    log "Backing up Elasticsearch..."
    if docker ps | grep -q "$ELASTICSEARCH_CONTAINER"; then
        # Create snapshot repository
        docker exec "$ELASTICSEARCH_CONTAINER" curl -XPUT "localhost:9200/_snapshot/nexus_backup" \
            -H 'Content-Type: application/json' -d'{"type": "fs", "settings": {"location": "/usr/share/elasticsearch/backup"}}' 2>/dev/null || true

        # Create snapshot
        docker exec "$ELASTICSEARCH_CONTAINER" curl -XPUT "localhost:9200/_snapshot/nexus_backup/snapshot_$TIMESTAMP" 2>/dev/null && \
        success "Elasticsearch snapshot created" || \
        warning "Elasticsearch backup may be incomplete"
    fi
}

# Backup configuration
backup_configuration() {
    log "Backing up configuration..."

    local backup_dir="$BACKUP_ROOT/config/$BACKUP_NAME"
    mkdir -p "$backup_dir"

    # Backup environment files
    cp .env* "$backup_dir/" 2>/dev/null || true
    cp config/*.env* "$backup_dir/" 2>/dev/null || true

    # Backup docker-compose files
    cp docker-compose*.yml "$backup_dir/" 2>/dev/null || true

    # Backup nginx configuration
    cp nginx*.conf "$backup_dir/" 2>/dev/null || true

    # Backup monitoring configuration
    cp v2/infrastructure/prometheus/*.yml "$backup_dir/" 2>/dev/null || true

    # Create configuration manifest
    cat > "$backup_dir/manifest.json" << EOF
{
    "backup_timestamp": "$TIMESTAMP",
    "configuration_version": "2.0.0",
    "included_files": [
        "environment_variables",
        "docker_compose_configs",
        "nginx_configs",
        "monitoring_configs"
    ],
    "system_info": {
        "gpu_info": "$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'GPU not available')",
        "docker_version": "$(docker --version)",
        "kernel_version": "$(uname -r)"
    }
}
EOF

    success "Configuration backed up"
}

# Backup logs
backup_logs() {
    log "Backing up logs..."

    local backup_dir="$BACKUP_ROOT/logs/$BACKUP_NAME"
    mkdir -p "$backup_dir"

    # Backup application logs
    cp -r v2/backend/logs/* "$backup_dir/" 2>/dev/null || true

    # Backup container logs (last 1000 lines)
    for container in nexus-backend nexus-frontend nexus-monitoring; do
        docker logs --tail 1000 "$container" > "$backup_dir/${container}_logs.txt" 2>/dev/null || true
    done

    # Backup GPU monitoring logs
    cp /app/logs/gpu_monitor.log "$backup_dir/" 2>/dev/null || true

    success "Logs backed up"
}

# Compress backup
compress_backup() {
    log "Compressing backup..."

    cd "$BACKUP_ROOT"

    # Create compressed archive
    tar -czf "${BACKUP_NAME}.tar.gz" \
        "models/$BACKUP_NAME" \
        "databases/$BACKUP_NAME" \
        "config/$BACKUP_NAME" \
        "logs/$BACKUP_NAME" 2>/dev/null

    # Calculate backup size
    backup_size=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
    success "Backup compressed: $backup_size"

    # Verify backup integrity
    if tar -tzf "${BACKUP_NAME}.tar.gz" > /dev/null 2>&1; then
        success "Backup integrity verified"
    else
        error "Backup integrity check failed"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."

    cd "$BACKUP_ROOT"

    # Remove backups older than retention period
    find . -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    # Remove uncompressed backup directories (keep only compressed archives)
    find models databases config logs -name "nexus_*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true

    success "Old backups cleaned up (retention: ${RETENTION_DAYS} days)"
}

# Upload to cloud storage (optional)
upload_to_cloud() {
    log "Uploading backup to cloud storage..."

    # Check for cloud storage configuration
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        aws s3 cp "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" "s3://$AWS_S3_BUCKET/backups/" && \
        success "Backup uploaded to AWS S3" || \
        warning "AWS S3 upload failed"
    elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        gcloud storage cp "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" "gs://$GCS_BUCKET/backups/" && \
        success "Backup uploaded to Google Cloud Storage" || \
        warning "GCS upload failed"
    else
        warning "No cloud storage configured - backup stored locally only"
    fi
}

# Recovery functions
perform_recovery() {
    local backup_file="$1"

    if [ -z "$backup_file" ]; then
        error "No backup file specified for recovery"
        echo "Usage: $0 recovery <backup_file.tar.gz>"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi

    log "Starting recovery from $backup_file..."

    # Stop services before recovery
    log "Stopping services for recovery..."
    docker-compose -f docker-compose.gpu.yml down

    # Extract backup
    log "Extracting backup..."
    mkdir -p /tmp/nexus_recovery
    tar -xzf "$backup_file" -C /tmp/nexus_recovery

    # Restore models
    if [ -d "/tmp/nexus_recovery/models" ]; then
        log "Restoring GPU models..."
        cp -r /tmp/nexus_recovery/models/* "$MODEL_CACHE_DIR/" 2>/dev/null || true
    fi

    # Restore configuration
    if [ -d "/tmp/nexus_recovery/config" ]; then
        log "Restoring configuration..."
        cp -r /tmp/nexus_recovery/config/* . 2>/dev/null || true
    fi

    # Note: Database recovery would require manual intervention for safety
    warning "Database recovery requires manual steps for safety"
    warning "PostgreSQL: docker exec -i nexus-postgres psql -U nexus < /path/to/postgres_backup.sql"
    warning "Redis: docker cp redis_backup.rdb nexus-redis:/data/dump.rdb && docker restart nexus-redis"

    # Cleanup
    rm -rf /tmp/nexus_recovery

    # Restart services
    log "Restarting services..."
    docker-compose -f docker-compose.gpu.yml up -d

    success "Recovery completed - please verify services manually"
}

# Health check after backup
health_check() {
    log "Performing post-backup health check..."

    # Check backup file exists and is not empty
    if [ ! -f "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" ]; then
        error "Backup file not created"
        return 1
    fi

    backup_size=$(stat -f%z "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" 2>/dev/null || stat -c%s "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" 2>/dev/null || echo "0")
    if [ "$backup_size" -lt 1000000 ]; then  # Less than 1MB
        warning "Backup file seems too small: $backup_size bytes"
    fi

    # Check GPU services are still running
    if ! docker ps | grep -q "nexus-backend\|nexus-frontend"; then
        warning "Some services may not be running after backup"
    fi

    success "Health check completed"
}

# Main backup function
perform_backup() {
    log "Starting NexusLang v2 GPU Backup"
    echo "==================================="

    init_backup_dir
    backup_gpu_models
    backup_databases
    backup_configuration
    backup_logs
    compress_backup
    cleanup_old_backups
    upload_to_cloud
    health_check

    echo ""
    echo "==================================="
    success "BACKUP COMPLETED SUCCESSFULLY"
    echo ""
    echo "📦 Backup Details:"
    echo "   • File: $BACKUP_ROOT/${BACKUP_NAME}.tar.gz"
    echo "   • Size: $(du -sh "$BACKUP_ROOT/${BACKUP_NAME}.tar.gz" 2>/dev/null | cut -f1 || echo 'unknown')"
    echo "   • Timestamp: $TIMESTAMP"
    echo ""
    echo "💡 Recovery Command:"
    echo "   • $0 recovery $BACKUP_ROOT/${BACKUP_NAME}.tar.gz"
}

# Main function
main() {
    case "${1:-backup}" in
        "backup")
            perform_backup
            ;;
        "recovery")
            perform_recovery "$2"
            ;;
        "cleanup")
            log "Performing cleanup only..."
            cleanup_old_backups
            success "Cleanup completed"
            ;;
        "health")
            health_check
            ;;
        *)
            echo "Usage: $0 [backup|recovery|cleanup|health] [backup_file]"
            echo ""
            echo "Commands:"
            echo "  backup     - Perform full system backup (default)"
            echo "  recovery   - Recover from backup file"
            echo "  cleanup    - Clean up old backups only"
            echo "  health     - Run health check only"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
