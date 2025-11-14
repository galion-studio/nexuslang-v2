#!/bin/bash
# 🚀 GALION PLATFORM - Comprehensive Health Check
# Tests all services and provides detailed status report

set -e

echo "🔍 GALION PLATFORM - COMPREHENSIVE HEALTH CHECK"
echo "==============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Results tracking
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[$((++TOTAL_CHECKS))]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
}

# Test function
test_service() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    local timeout="${4:-10}"

    log_info "Testing $name..."

    if curl -f -s --max-time "$timeout" -w "%{http_code}" "$url" | grep -q "^$expected_code$"; then
        log_success "$name is healthy ($expected_code)"
        return 0
    else
        log_error "$name failed or returned unexpected status"
        return 1
    fi
}

# Docker container check
check_container() {
    local service="$1"
    local expected_status="${2:-running}"

    log_info "Checking Docker container: $service"

    if docker-compose ps "$service" | grep -q "$expected_status"; then
        log_success "Container $service is $expected_status"
        return 0
    else
        log_error "Container $service is not $expected_status"
        return 1
    fi
}

# Database connectivity test
test_database() {
    log_info "Testing database connectivity..."

    # Test PostgreSQL connection
    if docker-compose exec -T postgres pg_isready -U nexus -d galion_platform >/dev/null 2>&1; then
        log_success "PostgreSQL connection successful"
        return 0
    else
        log_error "PostgreSQL connection failed"
        return 1
    fi
}

# Redis connectivity test
test_redis() {
    log_info "Testing Redis connectivity..."

    # Test Redis connection
    if docker-compose exec -T redis redis-cli --raw ping | grep -q "PONG"; then
        log_success "Redis connection successful"
        return 0
    else
        log_error "Redis connection failed"
        return 1
    fi
}

# Elasticsearch test
test_elasticsearch() {
    log_info "Testing Elasticsearch..."

    if curl -f -s --max-time 10 "http://localhost:9201/_cluster/health" | grep -q '"status":"green"\|"status":"yellow"'; then
        log_success "Elasticsearch is healthy"
        return 0
    else
        log_error "Elasticsearch health check failed"
        return 1
    fi
}

# Backend API comprehensive test
test_backend_api() {
    log_info "Testing Backend API comprehensive endpoints..."

    local failed=0

    # Health check
    if ! test_service "Backend Health" "http://localhost:8010/health/fast"; then
        ((failed++))
    fi

    # API docs
    if ! test_service "API Documentation" "http://localhost:8010/docs"; then
        ((failed++))
    fi

    # OpenAPI schema
    if ! test_service "OpenAPI Schema" "http://localhost:8010/openapi.json"; then
        ((failed++))
    fi

    # Test a basic API endpoint
    if curl -f -s --max-time 10 "http://localhost:8010/api/v1/health" >/dev/null 2>&1; then
        log_success "Backend API endpoints responding"
    else
        log_error "Backend API endpoints not responding"
        ((failed++))
    fi

    return $((failed > 0 ? 1 : 0))
}

# Frontend services test
test_frontend_services() {
    log_info "Testing Frontend Services..."

    local failed=0

    # Galion.app
    if ! test_service "Galion.app" "http://localhost:3000"; then
        ((failed++))
    fi

    # Developer Platform
    if ! test_service "Developer Platform" "http://localhost:3020"; then
        ((failed++))
    fi

    # Galion Studio
    if ! test_service "Galion Studio" "http://localhost:3030"; then
        ((failed++))
    fi

    return $((failed > 0 ? 1 : 0))
}

# Monitoring services test
test_monitoring_services() {
    log_info "Testing Monitoring Services..."

    local failed=0

    # Prometheus
    if ! test_service "Prometheus" "http://localhost:9090/-/healthy"; then
        ((failed++))
    fi

    # Grafana
    if ! test_service "Grafana" "http://localhost:3001/api/health"; then
        ((failed++))
    fi

    # Platform monitoring
    if ! test_service "Platform Monitoring" "http://localhost:8080/health"; then
        ((failed++))
    fi

    # AI Models service
    if ! test_service "AI Models" "http://localhost:8011/health"; then
        ((failed++))
    fi

    return $((failed > 0 ? 1 : 0))
}

# Nginx reverse proxy test
test_nginx() {
    log_info "Testing Nginx Reverse Proxy..."

    local failed=0

    # Nginx health check
    if ! test_service "Nginx Health" "http://localhost/nginx-health"; then
        ((failed++))
    fi

    # Platform health through nginx
    if ! test_service "Platform Health via Nginx" "http://localhost/health"; then
        ((failed++))
    fi

    # Test frontend routing
    if curl -f -s --max-time 10 "http://localhost/galion/" >/dev/null 2>&1; then
        log_success "Galion.app routing working"
    else
        log_error "Galion.app routing failed"
        ((failed++))
    fi

    if curl -f -s --max-time 10 "http://localhost/developer/" >/dev/null 2>&1; then
        log_success "Developer Platform routing working"
    else
        log_error "Developer Platform routing failed"
        ((failed++))
    fi

    return $((failed > 0 ? 1 : 0))
}

# Performance metrics
test_performance() {
    log_info "Testing Performance Metrics..."

    # Backend response time
    local start_time=$(date +%s%3N)
    curl -f -s "http://localhost:8010/health/fast" >/dev/null 2>&1
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))

    if [ $response_time -lt 100 ]; then
        log_success "Backend response time: ${response_time}ms (excellent)"
    elif [ $response_time -lt 500 ]; then
        log_success "Backend response time: ${response_time}ms (good)"
    else
        log_warning "Backend response time: ${response_time}ms (slow)"
    fi

    # Memory usage check
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep nexus-backend | awk '{print $3}' | sed 's/%//')
    if [ -n "$memory_usage" ] && [ "${memory_usage%.*}" -lt 80 ]; then
        log_success "Memory usage acceptable: $memory_usage"
    else
        log_warning "High memory usage detected: $memory_usage"
    fi
}

# API functionality test
test_api_functionality() {
    log_info "Testing API Functionality..."

    # Test NexusLang endpoint if available
    if curl -f -s --max-time 15 "http://localhost:8010/api/nexuslang/health" >/dev/null 2>&1; then
        log_success "NexusLang API responding"
    else
        log_warning "NexusLang API not responding (may be initializing)"
    fi

    # Test voice API endpoint
    if curl -f -s --max-time 15 -X POST "http://localhost:8010/api/voice/status" -H "Content-Type: application/json" -d '{}' >/dev/null 2>&1; then
        log_success "Voice API responding"
    else
        log_warning "Voice API not responding (may be initializing)"
    fi
}

# Main health check function
main() {
    echo "Starting comprehensive health check..."
    echo "======================================"
    echo ""

    # Infrastructure checks
    echo "🏗️  INFRASTRUCTURE CHECKS"
    echo "-------------------------"
    check_container "postgres"
    check_container "redis"
    check_container "elasticsearch"
    test_database
    test_redis
    test_elasticsearch
    echo ""

    # Service checks
    echo "🔧 SERVICE CONTAINER CHECKS"
    echo "---------------------------"
    check_container "backend"
    check_container "frontend"
    check_container "galion-app"
    check_container "developer-platform"
    check_container "galion-studio"
    check_container "monitoring"
    check_container "prometheus"
    check_container "grafana"
    check_container "ai-models"
    check_container "nginx"
    echo ""

    # API and functionality checks
    echo "🌐 API & FUNCTIONALITY CHECKS"
    echo "-----------------------------"
    test_backend_api
    test_frontend_services
    test_monitoring_services
    test_nginx
    test_api_functionality
    echo ""

    # Performance checks
    echo "⚡ PERFORMANCE CHECKS"
    echo "--------------------"
    test_performance
    echo ""

    # Final summary
    echo "📊 HEALTH CHECK SUMMARY"
    echo "======================"
    echo "Total Checks: $TOTAL_CHECKS"
    echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
    echo ""

    local success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

    if [ $success_rate -ge 95 ]; then
        echo -e "${GREEN}🎉 PLATFORM HEALTH: EXCELLENT ($success_rate% success rate)${NC}"
        echo "All systems operational!"
    elif [ $success_rate -ge 80 ]; then
        echo -e "${YELLOW}⚠️  PLATFORM HEALTH: GOOD ($success_rate% success rate)${NC}"
        echo "Most systems operational, minor issues detected."
    else
        echo -e "${RED}❌ PLATFORM HEALTH: CRITICAL ($success_rate% success rate)${NC}"
        echo "Immediate attention required!"
        exit 1
    fi

    echo ""
    echo "🔗 QUICK ACCESS LINKS:"
    echo "----------------------"
    echo "Galion.app (Voice):     http://localhost:3000"
    echo "Developer Platform:     http://localhost:3020"
    echo "Galion Studio:          http://localhost:3030"
    echo "API Documentation:      http://localhost:8010/docs"
    echo "AI Models API:          http://localhost:8011/docs"
    echo "Grafana Dashboard:      http://localhost:3001"
    echo "Platform Monitoring:    http://localhost:8080"
    echo ""

    # Generate timestamp
    echo "✅ Health check completed at $(date)"
}

# Handle command line arguments
case "${1:-all}" in
    "infrastructure")
        echo "🏗️  INFRASTRUCTURE CHECKS ONLY"
        echo "-----------------------------"
        check_container "postgres"
        check_container "redis"
        check_container "elasticsearch"
        test_database
        test_redis
        test_elasticsearch
        ;;
    "services")
        echo "🔧 SERVICE CHECKS ONLY"
        echo "----------------------"
        check_container "backend"
        check_container "frontend"
        check_container "galion-app"
        check_container "developer-platform"
        check_container "galion-studio"
        check_container "monitoring"
        ;;
    "api")
        echo "🌐 API CHECKS ONLY"
        echo "------------------"
        test_backend_api
        test_frontend_services
        test_api_functionality
        ;;
    "performance")
        echo "⚡ PERFORMANCE CHECKS ONLY"
        echo "-------------------------"
        test_performance
        ;;
    "all"|*)
        main
        ;;
esac
