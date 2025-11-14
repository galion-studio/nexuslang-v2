#!/bin/bash
# NexusLang v2 Backup and Restore Script
# Production-ready backup and disaster recovery system

set -e

# Configuration
BACKUP_ROOT_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT_DIR/$TIMESTAMP"
LOG_FILE="./backup_$TIMESTAMP.log"

# Database settings (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-galion_platform}"
DB_USER="${DB_USER:-nexus}"
DB_PASSWORD="${DB_PASSWORD:-dev_password_2025}"

# Redis settings
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-dev_redis_2025}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log "SUCCESS: $1"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
    log "INFO: $1"
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
    log "WARNING: $1"
}

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_DIR" || error "Failed to create backup directory"
    info "Backup directory created: $BACKUP_DIR"
}

# Backup PostgreSQL database
backup_database() {
    info "Starting PostgreSQL database backup..."

    local db_backup_file="$BACKUP_DIR/database_backup.sql"
    local db_backup_compressed="$BACKUP_DIR/database_backup.sql.gz"

    # Export database
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$db_backup_file.dump" || error "Database backup failed"

    # Also create SQL dump for compatibility
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --format=plain \
        --no-owner \
        --no-privileges > "$db_backup_file" || error "SQL dump creation failed"

    # Compress SQL dump
    gzip "$db_backup_file" || warning "Compression failed, keeping uncompressed file"

    # Calculate backup size
    local backup_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    success "Database backup completed - Size: $backup_size"
}

# Backup Redis data
backup_redis() {
    info "Starting Redis data backup..."

    local redis_backup_file="$BACKUP_DIR/redis_backup.rdb"

    # Trigger Redis SAVE command
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" SAVE || error "Redis SAVE command failed"

    # Copy RDB file (if running in Docker, adjust path)
    if docker ps | grep -q redis; then
        local container_id=$(docker ps -q --filter "name=redis")
        docker cp "$container_id:/data/dump.rdb" "$redis_backup_file" || warning "Redis backup from container failed"
    else
        cp "/var/lib/redis/dump.rdb" "$redis_backup_file" 2>/dev/null || warning "Redis backup from local filesystem failed"
    fi

    if [ -f "$redis_backup_file" ]; then
        local redis_size=$(du -sh "$redis_backup_file" | cut -f1)
        success "Redis backup completed - Size: $redis_size"
    else
        warning "Redis backup file not found - Redis might not be using RDB persistence"
    fi
}

# Backup configuration files
backup_configs() {
    info "Backing up configuration files..."

    local config_files=(".env" "docker-compose.yml" "nginx.conf" "production.env")

    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            cp "$config_file" "$BACKUP_DIR/"
            info "Backed up: $config_file"
        fi
    done

    success "Configuration files backup completed"
}

# Backup application data
backup_app_data() {
    info "Backing up application data..."

    # Backup uploaded files/media (if any)
    if [ -d "uploads" ] && [ "$(ls -A uploads 2>/dev/null)" ]; then
        cp -r uploads "$BACKUP_DIR/"
        info "Backed up uploads directory"
    fi

    # Backup logs
    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        cp -r logs "$BACKUP_DIR/"
        info "Backed up logs directory"
    fi

    success "Application data backup completed"
}

# Create backup manifest
create_manifest() {
    info "Creating backup manifest..."

    local manifest_file="$BACKUP_DIR/backup_manifest.txt"

    cat > "$manifest_file" << EOF
NexusLang v2 Backup Manifest
============================
Backup Date: $(date)
Backup ID: $TIMESTAMP
Backup Location: $BACKUP_DIR

Database Information:
- Host: $DB_HOST:$DB_PORT
- Database: $DB_NAME
- User: $DB_USER

Redis Information:
- Host: $REDIS_HOST:$REDIS_PORT

Backup Contents:
$(find "$BACKUP_DIR" -type f -exec basename {} \; | sort)

System Information:
- OS: $(uname -s)
- Kernel: $(uname -r)
- Docker: $(docker --version 2>/dev/null || echo "Not available")

Backup created by: $(whoami)@$(hostname)
EOF

    success "Backup manifest created: $manifest_file"
}

# Verify backup integrity
verify_backup() {
    info "Verifying backup integrity..."

    local errors=0

    # Check database backup
    if [ -f "$BACKUP_DIR/database_backup.sql.dump" ]; then
        # Test if dump file is valid (basic check)
        if ! file "$BACKUP_DIR/database_backup.sql.dump" | grep -q "PostgreSQL custom database dump"; then
            warning "Database backup file may be corrupted"
            ((errors++))
        fi
    else
        warning "Database backup file not found"
        ((errors++))
    fi

    # Check configuration files
    if [ ! -f "$BACKUP_DIR/.env" ] && [ ! -f "$BACKUP_DIR/production.env" ]; then
        warning "No environment configuration found in backup"
        ((errors++))
    fi

    if [ $errors -eq 0 ]; then
        success "Backup integrity verification passed"
    else
        warning "Backup integrity verification found $errors issues"
    fi

    return $errors
}

# Restore database
restore_database() {
    info "Restoring PostgreSQL database..."

    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
    fi

    # Create database if it doesn't exist
    PGPASSWORD="$DB_PASSWORD" createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$DB_NAME" 2>/dev/null || info "Database already exists"

    # Terminate active connections
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" || true

    # Drop and recreate database
    PGPASSWORD="$DB_PASSWORD" dropdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        --if-exists "$DB_NAME" || true

    PGPASSWORD="$DB_PASSWORD" createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$DB_NAME" || error "Failed to create database"

    # Restore from backup
    PGPASSWORD="$DB_PASSWORD" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-owner \
        --no-privileges \
        --verbose \
        "$backup_file" || error "Database restore failed"

    success "Database restore completed"
}

# Restore Redis data
restore_redis() {
    info "Restoring Redis data..."

    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        error "Redis backup file not found: $backup_file"
    fi

    # Stop Redis service
    if docker ps | grep -q redis; then
        docker-compose stop redis
        sleep 2

        # Copy backup file to container
        local container_id=$(docker ps -aq --filter "name=redis" | head -1)
        docker cp "$backup_file" "$container_id:/data/dump.rdb"

        # Start Redis service
        docker-compose start redis
    else
        warning "Redis container not found, manual restore required"
        info "Copy $backup_file to Redis data directory and restart Redis"
    fi

    success "Redis restore instructions provided"
}

# Cleanup old backups
cleanup_old_backups() {
    info "Cleaning up old backups..."

    local max_backups=${MAX_BACKUPS:-10}

    # Count current backups
    local backup_count=$(find "$BACKUP_ROOT_DIR" -maxdepth 1 -type d -name "20*" | wc -l)

    if [ "$backup_count" -gt "$max_backups" ]; then
        local to_delete=$((backup_count - max_backups))
        info "Deleting $to_delete old backups..."

        find "$BACKUP_ROOT_DIR" -maxdepth 1 -type d -name "20*" -printf '%T@ %p\n' | \
            sort -n | head -n "$to_delete" | cut -d' ' -f2- | xargs rm -rf

        success "Old backups cleaned up"
    else
        info "No old backups to clean up ($backup_count <= $max_backups)"
    fi
}

# Main functions
backup() {
    info "Starting NexusLang v2 backup process..."

    create_backup_dir
    backup_database
    backup_redis
    backup_configs
    backup_app_data
    create_manifest
    verify_backup
    cleanup_old_backups

    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    BACKUP COMPLETE!                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📦 Backup Location: $BACKUP_DIR"
    echo "📊 Total Size: $total_size"
    echo "📋 Manifest: $BACKUP_DIR/backup_manifest.txt"
    echo "📝 Log: $LOG_FILE"
    echo ""
    echo "💡 To restore: $0 restore $TIMESTAMP"
    echo ""

    success "Backup process completed successfully"
}

restore() {
    local backup_id="$1"

    if [ -z "$backup_id" ]; then
        error "Backup ID required. Usage: $0 restore <backup_id>"
    fi

    local restore_dir="$BACKUP_ROOT_DIR/$backup_id"

    if [ ! -d "$restore_dir" ]; then
        error "Backup directory not found: $restore_dir"
    fi

    info "Starting restore from backup: $backup_id"

    # Stop services
    docker-compose down

    # Restore database
    if [ -f "$restore_dir/database_backup.sql.dump" ]; then
        restore_database "$restore_dir/database_backup.sql.dump"
    fi

    # Restore Redis
    if [ -f "$restore_dir/redis_backup.rdb" ]; then
        restore_redis "$restore_dir/redis_backup.rdb"
    fi

    # Restore configuration
    if [ -f "$restore_dir/.env" ]; then
        cp "$restore_dir/.env" .env
        info "Environment file restored"
    fi

    # Start services
    docker-compose up -d

    # Run health checks
    sleep 10
    if curl -f -s http://localhost:8010/health >/dev/null 2>&1; then
        success "Restore completed successfully - services are healthy"
    else
        warning "Restore completed but health checks failed - manual verification required"
    fi
}

list_backups() {
    info "Available backups:"

    if [ ! -d "$BACKUP_ROOT_DIR" ]; then
        info "No backups found"
        return
    fi

    echo "ID                   Date/Time           Size"
    echo "-------------------- ------------------- --------"
    find "$BACKUP_ROOT_DIR" -maxdepth 1 -type d -name "20*" -printf '%P\n' | \
        sort -r | head -20 | while read -r backup_id; do
        backup_path="$BACKUP_ROOT_DIR/$backup_id"
        if [ -f "$backup_path/backup_manifest.txt" ]; then
            backup_date=$(stat -c %y "$backup_path" 2>/dev/null | cut -d'.' -f1 || echo "Unknown")
            backup_size=$(du -sh "$backup_path" 2>/dev/null | cut -f1 || echo "Unknown")
            printf "%-20s %-19s %-8s\n" "$backup_id" "${backup_date:0:19}" "$backup_size"
        fi
    done
}

# Main script logic
case "${1:-help}" in
    "backup")
        backup
        ;;
    "restore")
        restore "$2"
        ;;
    "list")
        list_backups
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "help"|*)
        echo "NexusLang v2 Backup and Restore Script"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  backup     - Create a new backup"
        echo "  restore    - Restore from backup (requires backup ID)"
        echo "  list       - List available backups"
        echo "  cleanup    - Remove old backups (keeps MAX_BACKUPS, default 10)"
        echo "  help       - Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  MAX_BACKUPS    - Maximum number of backups to keep (default: 10)"
        echo "  DB_HOST        - PostgreSQL host (default: localhost)"
        echo "  DB_PORT        - PostgreSQL port (default: 5432)"
        echo "  DB_NAME        - Database name (default: galion_platform)"
        echo "  DB_USER        - Database user (default: nexus)"
        echo "  DB_PASSWORD    - Database password"
        echo "  REDIS_HOST     - Redis host (default: localhost)"
        echo "  REDIS_PORT     - Redis port (default: 6379)"
        echo "  REDIS_PASSWORD - Redis password"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore 20241113_143052"
        echo "  MAX_BACKUPS=5 $0 cleanup"
        ;;
esac
