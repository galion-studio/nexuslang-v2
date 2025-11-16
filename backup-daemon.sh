#!/bin/bash
################################################################################
# GALION PLATFORM - BACKGROUND BACKUP DAEMON
#
# Runs continuously in the background, creating full platform backups every
# 15 minutes including databases, user configurations, analytics, and all
# three platform services.
#
# Features:
# - Automatic backup every 15 minutes
# - Backs up databases, configs, analytics
# - Full snapshots of all 3 platforms
# - Compression (tar.gz)
# - Rotation (keeps last 10 backups)
# - Integrity verification
# - Transparent logging
#
# Usage: Launched automatically by universal-manager.sh
################################################################################

# Configuration
BACKUP_DIR="/var/backups/galion-platform"
PROJECT_DIR="/nexuslang-v2"
LOG_FILE="/var/log/galion-platform/backup-daemon.log"
PID_FILE="/var/run/galion-backup.pid"
STATUS_FILE="/var/run/galion-last-backup"
BACKUP_INTERVAL=900  # 15 minutes in seconds
MAX_BACKUPS=10

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Logging function
log_backup() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Backup databases
backup_databases() {
    local backup_dir=$1
    log_backup "Backing up databases..."
    
    # Check if databases are configured
    if [ -d "$PROJECT_DIR/databases" ]; then
        cp -r "$PROJECT_DIR/databases" "$backup_dir/databases" 2>/dev/null || true
        log_backup "Databases backed up"
    else
        log_backup "No databases found to backup"
    fi
}

# Backup user configurations
backup_user_configs() {
    local backup_dir=$1
    log_backup "Backing up user configurations..."
    
    mkdir -p "$backup_dir/configs"
    
    # Backup PM2 configuration
    if [ -f "$PROJECT_DIR/ecosystem-universal.config.js" ]; then
        cp "$PROJECT_DIR/ecosystem-universal.config.js" "$backup_dir/configs/"
    fi
    
    # Backup Nginx configuration
    if [ -f "/etc/nginx/sites-enabled/galion" ]; then
        cp "/etc/nginx/sites-enabled/galion" "$backup_dir/configs/nginx-galion.conf"
    fi
    
    # Backup environment files
    find "$PROJECT_DIR" -name ".env*" -type f -exec cp {} "$backup_dir/configs/" \; 2>/dev/null || true
    
    log_backup "User configurations backed up"
}

# Backup analytics data
backup_analytics() {
    local backup_dir=$1
    log_backup "Backing up analytics data..."
    
    # Check if analytics directory exists
    if [ -d "$PROJECT_DIR/analytics" ]; then
        cp -r "$PROJECT_DIR/analytics" "$backup_dir/analytics" 2>/dev/null || true
        log_backup "Analytics data backed up"
    else
        log_backup "No analytics data found to backup"
    fi
    
    # Backup PM2 logs (last 1000 lines of each)
    mkdir -p "$backup_dir/logs"
    for log in /var/log/galion-platform/*.log; do
        if [ -f "$log" ]; then
            tail -1000 "$log" > "$backup_dir/logs/$(basename $log)" 2>/dev/null || true
        fi
    done
    
    log_backup "Logs backed up"
}

# Backup platform service
backup_platform() {
    local service_name=$1
    local backup_dir=$2
    
    log_backup "Backing up $service_name..."
    
    local service_path="$PROJECT_DIR/$service_name"
    
    if [ -d "$service_path" ]; then
        mkdir -p "$backup_dir/$service_name"
        
        # Copy all files except node_modules, .next, __pycache__
        rsync -a \
            --exclude 'node_modules' \
            --exclude '.next' \
            --exclude '__pycache__' \
            --exclude '*.pyc' \
            --exclude '.git' \
            "$service_path/" "$backup_dir/$service_name/" 2>/dev/null || true
        
        log_backup "$service_name backed up"
    else
        log_backup "$service_name not found, skipping"
    fi
}

# Rotate old backups
rotate_backups() {
    log_backup "Rotating old backups..."
    
    # Count existing backups
    local backup_count=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    
    if [ $backup_count -gt $MAX_BACKUPS ]; then
        # Delete oldest backups
        local to_delete=$((backup_count - MAX_BACKUPS))
        ls -1t "$BACKUP_DIR"/*.tar.gz | tail -$to_delete | xargs rm -f
        log_backup "Deleted $to_delete old backup(s)"
    fi
    
    log_backup "Backup rotation complete (keeping last $MAX_BACKUPS)"
}

# Verify backup integrity
verify_backup() {
    local backup_file=$1
    
    if tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_backup "Backup integrity verified: $(basename $backup_file)"
        return 0
    else
        log_backup "ERROR: Backup integrity check failed: $(basename $backup_file)"
        return 1
    fi
}

# Main backup function
perform_backup() {
    local timestamp=$(date +%Y-%m-%d_%H-%M)
    local backup_name="galion-platform-$timestamp"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log_backup "========================================="
    log_backup "Starting backup: $backup_name"
    log_backup "========================================="
    
    # Create backup directory
    mkdir -p "$backup_path"
    
    # Perform backups
    backup_databases "$backup_path"
    backup_user_configs "$backup_path"
    backup_analytics "$backup_path"
    
    # Backup all platforms
    backup_platform "v2/backend" "$backup_path"
    backup_platform "galion-studio" "$backup_path"
    backup_platform "galion-app" "$backup_path"
    backup_platform "developer-platform" "$backup_path"
    
    # Compress backup
    log_backup "Compressing backup..."
    tar -czf "$BACKUP_DIR/$backup_name.tar.gz" -C "$BACKUP_DIR" "$backup_name" 2>/dev/null
    
    # Remove uncompressed directory
    rm -rf "$backup_path"
    
    # Verify backup
    if verify_backup "$BACKUP_DIR/$backup_name.tar.gz"; then
        # Get backup size
        local backup_size=$(du -h "$BACKUP_DIR/$backup_name.tar.gz" | cut -f1)
        log_backup "Backup created successfully: $backup_name.tar.gz ($backup_size)"
        
        # Update status file
        echo "$timestamp" > "$STATUS_FILE"
        
        # Rotate old backups
        rotate_backups
    else
        log_backup "ERROR: Backup verification failed, removing corrupted backup"
        rm -f "$BACKUP_DIR/$backup_name.tar.gz"
    fi
    
    log_backup "Backup cycle complete"
    log_backup "========================================="
}

# Signal handlers
cleanup() {
    log_backup "Backup daemon shutting down..."
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup EXIT INT TERM

# Main daemon loop
log_backup "Backup daemon started (PID: $$)"
log_backup "Backup interval: $BACKUP_INTERVAL seconds (15 minutes)"
log_backup "Backup location: $BACKUP_DIR"
log_backup "Max backups: $MAX_BACKUPS"

# Perform initial backup immediately
perform_backup

# Main loop
while true; do
    # Sleep for 15 minutes
    sleep $BACKUP_INTERVAL
    
    # Perform backup
    perform_backup
done

