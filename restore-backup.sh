#!/bin/bash
################################################################################
# GALION PLATFORM - BACKUP RESTORE SYSTEM
#
# Restores the platform from a previous backup snapshot.
#
# Features:
# - Lists all available backups
# - Interactive or command-line selection
# - Stops services before restoration
# - Restores all files
# - Restarts services
# - Verifies restoration
#
# Usage: ./restore-backup.sh [timestamp]
#        ./restore-backup.sh 2025-11-15_23-30
#        ./restore-backup.sh (interactive mode)
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
BACKUP_DIR="/var/backups/galion-platform"
PROJECT_DIR="/nexuslang-v2"
LOG_FILE="/var/log/galion-platform/restore-$(date +%Y%m%d-%H%M%S).log"

# Logging
log_restore() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case $level in
        "INFO")
            echo -e "${CYAN}ℹ${NC}  $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️${NC}  $message"
            ;;
        "ERROR")
            echo -e "${RED}❌${NC} $message"
            ;;
        "STEP")
            echo -e "${CYAN}▶${NC}  ${WHITE}$message${NC}"
            ;;
    esac
}

# Display banner
display_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     GALION PLATFORM - BACKUP RESTORE SYSTEM             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo ""
}

# List available backups
list_backups() {
    log_restore "STEP" "Available Backups"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR/*.tar.gz 2>/dev/null)" ]; then
        log_restore "ERROR" "No backups found in $BACKUP_DIR"
        return 1
    fi
    
    local count=1
    declare -g -A BACKUP_MAP
    
    echo -e "${WHITE}#  Timestamp           Size      Age${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for backup in $(ls -1t "$BACKUP_DIR"/*.tar.gz); do
        local filename=$(basename "$backup")
        local timestamp=$(echo "$filename" | sed 's/galion-platform-\(.*\)\.tar\.gz/\1/')
        local size=$(du -h "$backup" | cut -f1)
        local age=$(stat -c %Y "$backup")
        local now=$(date +%s)
        local diff=$((now - age))
        local hours=$((diff / 3600))
        local days=$((hours / 24))
        
        local age_str
        if [ $days -gt 0 ]; then
            age_str="${days}d ago"
        elif [ $hours -gt 0 ]; then
            age_str="${hours}h ago"
        else
            local minutes=$((diff / 60))
            age_str="${minutes}m ago"
        fi
        
        echo -e "${GREEN}$count${NC}  $timestamp  $size    $age_str"
        BACKUP_MAP[$count]="$backup"
        count=$((count + 1))
    done
    
    echo ""
    return 0
}

# Select backup
select_backup() {
    local timestamp=$1
    
    if [ -n "$timestamp" ]; then
        # Timestamp provided via command line
        local backup_file="$BACKUP_DIR/galion-platform-$timestamp.tar.gz"
        
        if [ -f "$backup_file" ]; then
            echo "$backup_file"
            return 0
        else
            log_restore "ERROR" "Backup not found: $backup_file"
            return 1
        fi
    else
        # Interactive selection
        list_backups || return 1
        
        echo -e "${CYAN}Select backup number to restore (or 'q' to quit):${NC} "
        read -r selection
        
        if [ "$selection" == "q" ] || [ "$selection" == "Q" ]; then
            log_restore "INFO" "Restore cancelled by user"
            exit 0
        fi
        
        if [ -n "${BACKUP_MAP[$selection]}" ]; then
            echo "${BACKUP_MAP[$selection]}"
            return 0
        else
            log_restore "ERROR" "Invalid selection: $selection"
            return 1
        fi
    fi
}

# Confirm restoration
confirm_restore() {
    local backup_file=$1
    local filename=$(basename "$backup_file")
    
    echo ""
    log_restore "WARN" "You are about to restore from: $filename"
    log_restore "WARN" "This will OVERWRITE current platform files!"
    echo ""
    echo -e "${YELLOW}Are you sure you want to continue? (yes/no):${NC} "
    read -r confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log_restore "INFO" "Restore cancelled by user"
        exit 0
    fi
    
    return 0
}

# Stop services
stop_services() {
    log_restore "STEP" "Stopping all services..."
    
    # Stop PM2 services
    pm2 delete all 2>/dev/null || true
    log_restore "SUCCESS" "PM2 services stopped"
    
    # Stop Nginx
    pkill -9 nginx 2>/dev/null || true
    log_restore "SUCCESS" "Nginx stopped"
    
    # Stop backup daemon
    if [ -f "/var/run/galion-backup.pid" ]; then
        local pid=$(cat /var/run/galion-backup.pid)
        kill -9 $pid 2>/dev/null || true
        rm -f /var/run/galion-backup.pid
        log_restore "SUCCESS" "Backup daemon stopped"
    fi
    
    sleep 3
    echo ""
}

# Extract and restore backup
restore_files() {
    local backup_file=$1
    
    log_restore "STEP" "Extracting backup..."
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    
    # Extract backup
    if tar -xzf "$backup_file" -C "$temp_dir" 2>/dev/null; then
        log_restore "SUCCESS" "Backup extracted to temporary directory"
    else
        log_restore "ERROR" "Failed to extract backup"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Find the extracted directory
    local extracted_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "galion-platform-*" | head -1)
    
    if [ -z "$extracted_dir" ]; then
        log_restore "ERROR" "Could not find extracted backup directory"
        rm -rf "$temp_dir"
        return 1
    fi
    
    log_restore "STEP" "Restoring files..."
    
    # Restore backend
    if [ -d "$extracted_dir/v2/backend" ]; then
        log_restore "INFO" "Restoring backend..."
        rsync -a --delete "$extracted_dir/v2/backend/" "$PROJECT_DIR/v2/backend/"
        log_restore "SUCCESS" "Backend restored"
    fi
    
    # Restore galion-studio
    if [ -d "$extracted_dir/galion-studio" ]; then
        log_restore "INFO" "Restoring galion-studio..."
        rsync -a --delete "$extracted_dir/galion-studio/" "$PROJECT_DIR/galion-studio/"
        log_restore "SUCCESS" "Galion Studio restored"
    fi
    
    # Restore galion-app
    if [ -d "$extracted_dir/galion-app" ]; then
        log_restore "INFO" "Restoring galion-app..."
        rsync -a --delete "$extracted_dir/galion-app/" "$PROJECT_DIR/galion-app/"
        log_restore "SUCCESS" "Galion App restored"
    fi
    
    # Restore developer-platform
    if [ -d "$extracted_dir/developer-platform" ]; then
        log_restore "INFO" "Restoring developer-platform..."
        rsync -a --delete "$extracted_dir/developer-platform/" "$PROJECT_DIR/developer-platform/"
        log_restore "SUCCESS" "Developer Platform restored"
    fi
    
    # Restore configurations
    if [ -d "$extracted_dir/configs" ]; then
        log_restore "INFO" "Restoring configurations..."
        
        # PM2 ecosystem
        if [ -f "$extracted_dir/configs/ecosystem-universal.config.js" ]; then
            cp "$extracted_dir/configs/ecosystem-universal.config.js" "$PROJECT_DIR/"
        fi
        
        # Nginx config
        if [ -f "$extracted_dir/configs/nginx-galion.conf" ]; then
            cp "$extracted_dir/configs/nginx-galion.conf" /etc/nginx/sites-available/galion
            ln -sf /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/galion 2>/dev/null || true
        fi
        
        log_restore "SUCCESS" "Configurations restored"
    fi
    
    # Restore databases (if any)
    if [ -d "$extracted_dir/databases" ]; then
        log_restore "INFO" "Restoring databases..."
        rsync -a "$extracted_dir/databases/" "$PROJECT_DIR/databases/"
        log_restore "SUCCESS" "Databases restored"
    fi
    
    # Restore analytics (if any)
    if [ -d "$extracted_dir/analytics" ]; then
        log_restore "INFO" "Restoring analytics..."
        rsync -a "$extracted_dir/analytics/" "$PROJECT_DIR/analytics/"
        log_restore "SUCCESS" "Analytics restored"
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    
    echo ""
    return 0
}

# Restart services
restart_services() {
    log_restore "STEP" "Restarting services..."
    
    # Start PM2 services
    if [ -f "$PROJECT_DIR/ecosystem-universal.config.js" ]; then
        cd "$PROJECT_DIR"
        pm2 start ecosystem-universal.config.js
        pm2 save
        log_restore "SUCCESS" "PM2 services started"
    else
        log_restore "WARN" "PM2 ecosystem file not found, services not started"
    fi
    
    # Start Nginx
    if nginx -t 2>&1 | grep -q "successful"; then
        nginx
        log_restore "SUCCESS" "Nginx started"
    else
        log_restore "WARN" "Nginx configuration invalid, not started"
    fi
    
    # Restart backup daemon
    if [ -f "$PROJECT_DIR/backup-daemon.sh" ]; then
        nohup bash "$PROJECT_DIR/backup-daemon.sh" > /var/log/galion-platform/backup-daemon.log 2>&1 &
        echo $! > /var/run/galion-backup.pid
        log_restore "SUCCESS" "Backup daemon restarted"
    fi
    
    sleep 5
    echo ""
}

# Verify restoration
verify_restoration() {
    log_restore "STEP" "Verifying restoration..."
    
    local issues=0
    
    # Check PM2 services
    for service in backend galion-studio galion-app developer-platform; do
        if pm2 list | grep "$service" | grep -q "online"; then
            log_restore "SUCCESS" "$service: ONLINE"
        else
            log_restore "ERROR" "$service: NOT RUNNING"
            issues=$((issues + 1))
        fi
    done
    
    # Check ports
    for port in 8000 3000 3003 3030; do
        if ss -tlnp 2>/dev/null | grep -q ":$port "; then
            log_restore "SUCCESS" "Port $port: LISTENING"
        else
            log_restore "WARN" "Port $port: NOT LISTENING"
        fi
    done
    
    # Check HTTP endpoints
    sleep 5
    
    if curl -sf --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
        log_restore "SUCCESS" "Backend API: RESPONDING"
    else
        log_restore "WARN" "Backend API: NOT RESPONDING"
    fi
    
    echo ""
    
    if [ $issues -eq 0 ]; then
        log_restore "SUCCESS" "Restoration completed successfully!"
        return 0
    else
        log_restore "WARN" "Restoration completed with $issues issue(s)"
        return 1
    fi
}

# Main function
main() {
    display_banner
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_restore "WARN" "Not running as root. Some operations may fail."
    fi
    
    # Select backup
    local backup_file=$(select_backup "$1")
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Confirm restoration
    confirm_restore "$backup_file"
    
    # Perform restoration
    stop_services
    restore_files "$backup_file" || exit 1
    restart_services
    verify_restoration
    
    echo ""
    log_restore "INFO" "Restoration process complete"
    log_restore "INFO" "Log file: $LOG_FILE"
    echo ""
}

# Run main function
main "$@"

exit 0

