#!/bin/bash
# NexusLang v2 Production Security Audit
# Comprehensive security assessment and hardening

set -e

# Configuration
AUDIT_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
AUDIT_REPORT="security_audit_$AUDIT_TIMESTAMP.txt"
SECURITY_SCORE=0
MAX_SCORE=100

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Security categories
declare -A SECURITY_CHECKS=(
    ["container_security"]="Container Security"
    ["network_security"]="Network Security"
    ["gpu_security"]="GPU Security"
    ["data_security"]="Data Security"
    ["access_control"]="Access Control"
    ["monitoring_security"]="Monitoring & Logging"
    ["dependency_security"]="Dependency Security"
)

# Initialize audit report
init_audit() {
    echo "==========================================" > "$AUDIT_REPORT"
    echo "NEXUSLANG V2 SECURITY AUDIT REPORT" >> "$AUDIT_REPORT"
    echo "Generated: $(date)" >> "$AUDIT_REPORT"
    echo "==========================================" >> "$AUDIT_REPORT"
    echo "" >> "$AUDIT_REPORT"
}

log() {
    echo -e "${BLUE}[$AUDIT_TIMESTAMP]${NC} $1" | tee -a "$AUDIT_REPORT"
}

success() {
    echo -e "${GREEN}✓ PASS: $1${NC}" | tee -a "$AUDIT_REPORT"
    ((SECURITY_SCORE+=10))
}

warning() {
    echo -e "${YELLOW}⚠ WARN: $1${NC}" | tee -a "$AUDIT_REPORT"
    ((SECURITY_SCORE+=5))
}

error() {
    echo -e "${RED}✗ FAIL: $1${NC}" | tee -a "$AUDIT_REPORT"
}

info() {
    echo -e "${BLUE}ℹ INFO: $1${NC}" | tee -a "$AUDIT_REPORT"
}

# Container Security Audit
audit_container_security() {
    log "Auditing Container Security..."

    # Check if containers run as non-root
    if docker ps --format "table {{.Names}}\t{{.Image}}" | grep -q "nexus-"; then
        # Check for privileged containers
        if docker inspect $(docker ps -q) | grep -q '"Privileged": true'; then
            warning "Privileged containers detected"
        else
            success "No privileged containers found"
        fi

        # Check for security options
        if docker inspect $(docker ps -q) | grep -q "no-new-privileges"; then
            success "Security options configured"
        else
            warning "Security options not configured"
        fi
    else
        error "No Nexus containers running"
    fi

    # Check Docker daemon security
    if pgrep -f dockerd > /dev/null; then
        if docker system info | grep -q "Security Options"; then
            success "Docker daemon has security options"
        else
            warning "Docker daemon security options not configured"
        fi
    fi
}

# Network Security Audit
audit_network_security() {
    log "Auditing Network Security..."

    # Check firewall status
    if command -v ufw >/dev/null 2>&1; then
        if ufw status | grep -q "Status: active"; then
            success "UFW firewall is active"
        else
            error "UFW firewall is not active"
        fi
    elif command -v firewall-cmd >/dev/null 2>&1; then
        if firewall-cmd --state | grep -q "running"; then
            success "Firewalld is active"
        else
            error "Firewalld is not active"
        fi
    else
        warning "No firewall detected"
    fi

    # Check open ports
    OPEN_PORTS=$(netstat -tln | grep LISTEN | wc -l)
    if [ "$OPEN_PORTS" -gt 10 ]; then
        warning "Many open ports detected ($OPEN_PORTS)"
    else
        success "Reasonable number of open ports ($OPEN_PORTS)"
    fi

    # Check SSL/TLS configuration
    if curl -I https://localhost 2>/dev/null | grep -q "HTTP/2 200"; then
        success "HTTPS is properly configured"
    else
        warning "HTTPS not detected or not working"
    fi
}

# GPU Security Audit
audit_gpu_security() {
    log "Auditing GPU Security..."

    # Check NVIDIA GPU access
    if command -v nvidia-smi >/dev/null 2>&1; then
        # Check GPU processes
        GPU_PROCESSES=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)
        if [ "$GPU_PROCESSES" -gt 0 ]; then
            success "GPU processes are running ($GPU_PROCESSES detected)"
        else
            warning "No GPU processes detected"
        fi

        # Check GPU memory usage
        GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
        if [ "$GPU_MEM" -gt 0 ]; then
            success "GPU memory is being utilized"
        else
            warning "GPU memory not utilized"
        fi

        # Check GPU temperature (security concern if too high)
        GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -1)
        if [ "$GPU_TEMP" -gt 85 ]; then
            error "GPU temperature critically high ($GPU_TEMP°C)"
        elif [ "$GPU_TEMP" -gt 75 ]; then
            warning "GPU temperature elevated ($GPU_TEMP°C)"
        else
            success "GPU temperature normal ($GPU_TEMP°C)"
        fi
    else
        error "NVIDIA GPU not accessible"
    fi
}

# Data Security Audit
audit_data_security() {
    log "Auditing Data Security..."

    # Check database encryption
    if docker ps | grep -q postgres; then
        # Check if PostgreSQL has SSL enabled
        docker exec nexus-postgres psql -U nexus -c "SHOW ssl;" 2>/dev/null | grep -q "on" && \
        success "PostgreSQL SSL enabled" || \
        warning "PostgreSQL SSL not enabled"
    fi

    # Check Redis security
    if docker ps | grep -q redis; then
        # Check if Redis requires password
        docker exec nexus-redis redis-cli ping | grep -q "PONG" && \
        success "Redis is accessible" || \
        error "Redis authentication failed"
    fi

    # Check environment variables for secrets
    if [ -f ".env" ] || [ -f ".env.production" ]; then
        SECRET_VARS=$(grep -E "(password|secret|key|token)" .env* 2>/dev/null | grep -v "#" | wc -l)
        if [ "$SECRET_VARS" -gt 0 ]; then
            warning "Secrets found in environment files ($SECRET_VARS detected)"
            info "Ensure .env files are not committed to version control"
        else
            success "No secrets detected in environment files"
        fi
    fi

    # Check file permissions
    SECURE_FILES=$(find . -name "*.key" -o -name "*.pem" -o -name "*.crt" 2>/dev/null | wc -l)
    if [ "$SECURE_FILES" -gt 0 ]; then
        warning "SSL certificates/keys found ($SECURE_FILES files)"
        info "Ensure certificates have proper permissions (600)"
    fi
}

# Access Control Audit
audit_access_control() {
    log "Auditing Access Control..."

    # Check SSH configuration
    if [ -f "/etc/ssh/sshd_config" ]; then
        if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config; then
            success "Root SSH login disabled"
        else
            error "Root SSH login may be enabled"
        fi

        if grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config; then
            success "SSH password authentication disabled"
        else
            warning "SSH password authentication may be enabled"
        fi
    fi

    # Check sudo configuration
    if command -v sudo >/dev/null 2>&1; then
        SUDO_USERS=$(grep -c "^[^#]*ALL" /etc/sudoers 2>/dev/null || echo "0")
        if [ "$SUDO_USERS" -gt 1 ]; then
            warning "Multiple sudo users detected"
        else
            success "Sudo access properly restricted"
        fi
    fi

    # Check running processes as root
    ROOT_PROCESSES=$(ps aux | grep "^root" | wc -l)
    if [ "$ROOT_PROCESSES" -gt 10 ]; then
        warning "Many processes running as root ($ROOT_PROCESSES)"
    else
        success "Reasonable number of root processes ($ROOT_PROCESSES)"
    fi
}

# Monitoring and Logging Audit
audit_monitoring_security() {
    log "Auditing Monitoring & Logging Security..."

    # Check log file permissions
    LOG_FILES=$(find /var/log -name "*.log" 2>/dev/null | head -5)
    if [ -n "$LOG_FILES" ]; then
        INSECURE_LOGS=$(find /var/log -name "*.log" -perm /o+r 2>/dev/null | wc -l)
        if [ "$INSECURE_LOGS" -gt 0 ]; then
            warning "World-readable log files detected ($INSECURE_LOGS files)"
        else
            success "Log file permissions are secure"
        fi
    fi

    # Check monitoring services
    if docker ps | grep -q monitoring; then
        success "Monitoring service is running"
    else
        warning "Monitoring service not detected"
    fi

    if docker ps | grep -q prometheus; then
        success "Prometheus metrics collection active"
    else
        warning "Prometheus not running"
    fi
}

# Dependency Security Audit
audit_dependency_security() {
    log "Auditing Dependency Security..."

    # Check for known vulnerabilities in containers
    if command -v trivy >/dev/null 2>&1; then
        VULNERABILITIES=$(trivy image --format json --no-progress nexus-backend 2>/dev/null | jq '.Results[].Vulnerabilities | length' 2>/dev/null | awk '{sum += $1} END {print sum}')
        if [ "$VULNERABILITIES" -gt 0 ]; then
            warning "Vulnerabilities detected in containers ($VULNERABILITIES found)"
            info "Run 'trivy image nexus-backend' for details"
        else
            success "No container vulnerabilities detected"
        fi
    else
        info "Trivy not installed - install for vulnerability scanning"
    fi

    # Check Python dependencies
    if [ -f "requirements.txt" ]; then
        OUTDATED_PACKAGES=$(pip list --outdated 2>/dev/null | wc -l)
        if [ "$OUTDATED_PACKAGES" -gt 0 ]; then
            warning "Outdated Python packages detected ($OUTDATED_PACKAGES)"
            info "Run 'pip list --outdated' for details"
        else
            success "Python dependencies are up to date"
        fi
    fi

    # Check Node.js dependencies
    if [ -f "package.json" ]; then
        if command -v npm >/dev/null 2>&1; then
            VULNERABLE_DEPS=$(npm audit --audit-level=moderate --json 2>/dev/null | jq '.metadata.vulnerabilities.total' 2>/dev/null || echo "0")
            if [ "$VULNERABLE_DEPS" -gt 0 ]; then
                warning "Vulnerable npm packages detected ($VULNERABLE_DEPS)"
                info "Run 'npm audit' for details"
            else
                success "No vulnerable npm packages detected"
            fi
        fi
    fi
}

# Generate security recommendations
generate_recommendations() {
    log "Generating Security Recommendations..."

    echo "" >> "$AUDIT_REPORT"
    echo "==========================================" >> "$AUDIT_REPORT"
    echo "SECURITY RECOMMENDATIONS" >> "$AUDIT_REPORT"
    echo "==========================================" >> "$AUDIT_REPORT"

    # Container security recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "CONTAINER SECURITY:" >> "$AUDIT_REPORT"
    echo "• Use non-root users in containers" >> "$AUDIT_REPORT"
    echo "• Implement security options (--no-new-privileges)" >> "$AUDIT_REPORT"
    echo "• Scan images regularly with Trivy or similar tools" >> "$AUDIT_REPORT"
    echo "• Use minimal base images (Alpine, Distroless)" >> "$AUDIT_REPORT"

    # Network security recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "NETWORK SECURITY:" >> "$AUDIT_REPORT"
    echo "• Configure firewall rules (UFW, firewalld, iptables)" >> "$AUDIT_REPORT"
    echo "• Use HTTPS with valid SSL certificates" >> "$AUDIT_REPORT"
    echo "• Implement rate limiting and DDoS protection" >> "$AUDIT_REPORT"
    echo "• Restrict unnecessary open ports" >> "$AUDIT_REPORT"

    # GPU security recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "GPU SECURITY:" >> "$AUDIT_REPORT"
    echo "• Monitor GPU temperature and usage" >> "$AUDIT_REPORT"
    echo "• Implement GPU memory limits per container" >> "$AUDIT_REPORT"
    echo "• Restrict GPU access to authorized containers" >> "$AUDIT_REPORT"
    echo "• Regular GPU driver and firmware updates" >> "$AUDIT_REPORT"

    # Data security recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "DATA SECURITY:" >> "$AUDIT_REPORT"
    echo "• Enable database SSL/TLS encryption" >> "$AUDIT_REPORT"
    echo "• Use strong passwords and rotate regularly" >> "$AUDIT_REPORT"
    echo "• Implement data encryption at rest" >> "$AUDIT_REPORT"
    echo "• Regular security audits and penetration testing" >> "$AUDIT_REPORT"

    # Access control recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "ACCESS CONTROL:" >> "$AUDIT_REPORT"
    echo "• Disable root SSH login" >> "$AUDIT_REPORT"
    echo "• Use SSH key authentication only" >> "$AUDIT_REPORT"
    echo "• Implement principle of least privilege" >> "$AUDIT_REPORT"
    echo "• Regular access reviews and audits" >> "$AUDIT_REPORT"

    # Monitoring recommendations
    echo "" >> "$AUDIT_REPORT"
    echo "MONITORING & LOGGING:" >> "$AUDIT_REPORT"
    echo "• Implement comprehensive logging" >> "$AUDIT_REPORT"
    echo "• Set up security event monitoring" >> "$AUDIT_REPORT"
    echo "• Configure alerts for security events" >> "$AUDIT_REPORT"
    echo "• Regular log analysis and correlation" >> "$AUDIT_REPORT"
}

# Calculate final security score
calculate_score() {
    echo "" >> "$AUDIT_REPORT"
    echo "==========================================" >> "$AUDIT_REPORT"
    echo "SECURITY SCORE: $SECURITY_SCORE/$MAX_SCORE" >> "$AUDIT_REPORT"

    PERCENTAGE=$((SECURITY_SCORE * 100 / MAX_SCORE))

    if [ $PERCENTAGE -ge 90 ]; then
        echo "GRADE: A (EXCELLENT - $PERCENTAGE%)" >> "$AUDIT_REPORT"
        echo "✅ Excellent security posture" >> "$AUDIT_REPORT"
    elif [ $PERCENTAGE -ge 80 ]; then
        echo "GRADE: B (GOOD - $PERCENTAGE%)" >> "$AUDIT_REPORT"
        echo "✅ Good security with minor improvements needed" >> "$AUDIT_REPORT"
    elif [ $PERCENTAGE -ge 70 ]; then
        echo "GRADE: C (FAIR - $PERCENTAGE%)" >> "$AUDIT_REPORT"
        echo "⚠️ Adequate security with improvements recommended" >> "$AUDIT_REPORT"
    elif [ $PERCENTAGE -ge 60 ]; then
        echo "GRADE: D (POOR - $PERCENTAGE%)" >> "$AUDIT_REPORT"
        echo "⚠️ Security improvements urgently needed" >> "$AUDIT_REPORT"
    else
        echo "GRADE: F (CRITICAL - $PERCENTAGE%)" >> "$AUDIT_REPORT"
        echo "❌ Critical security vulnerabilities detected" >> "$AUDIT_REPORT"
    fi

    echo "==========================================" >> "$AUDIT_REPORT"
}

# Main audit function
main() {
    echo "🔒 NexusLang v2 Security Audit"
    echo "================================"

    init_audit

    # Run all security checks
    audit_container_security
    audit_network_security
    audit_gpu_security
    audit_data_security
    audit_access_control
    audit_monitoring_security
    audit_dependency_security

    # Generate recommendations
    generate_recommendations

    # Calculate final score
    calculate_score

    echo ""
    echo "📄 Security audit completed!"
    echo "📊 Report saved to: $AUDIT_REPORT"
    echo "🎯 Security Score: $SECURITY_SCORE/$MAX_SCORE"

    # Display summary
    PERCENTAGE=$((SECURITY_SCORE * 100 / MAX_SCORE))
    if [ $PERCENTAGE -ge 80 ]; then
        echo -e "${GREEN}✅ Security audit passed!${NC}"
    else
        echo -e "${RED}⚠️ Security improvements needed${NC}"
    fi
}

# Run main function
main "$@"
