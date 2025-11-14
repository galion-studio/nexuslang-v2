#!/bin/bash
# 🚀 GALION PLATFORM - SSL & Domain Configuration
# Automated SSL certificate setup with Let's Encrypt and domain routing

set -e

echo "🔐 GALION PLATFORM - SSL & DOMAIN SETUP"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Configuration
SSL_DIR="./ssl"
LETSENCRYPT_DIR="/etc/letsencrypt"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-admin@galion.app}"
DOMAINS="${DOMAINS:-galion.app www.galion.app developer.galion.app studio.galion.app}"
RUNPOD_IP="${RUNPOD_IP:-}"

# Check if we're in the right environment
check_environment() {
    log "Checking environment..."

    if [ ! -d "/workspace/project-nexus" ]; then
        error "Not in RunPod workspace. Please run from /workspace/project-nexus"
    fi

    cd /workspace/project-nexus
    success "In correct workspace directory"

    # Check if nginx is running
    if ! curl -f -s http://localhost/nginx-health >/dev/null 2>&1; then
        warning "Nginx not running. Starting services..."
        docker-compose up -d nginx
        sleep 5
    fi

    success "Environment check complete"
}

# Create SSL directory structure
create_ssl_directories() {
    log "Creating SSL directory structure..."

    mkdir -p "$SSL_DIR"
    mkdir -p "$SSL_DIR/certs"
    mkdir -p "$SSL_DIR/private"
    mkdir -p "$SSL_DIR/challenges"

    # Create self-signed certificates for development
    if [ ! -f "$SSL_DIR/certs/galion.app.crt" ]; then
        log "Creating self-signed certificates for development..."

        openssl req -x509 -newkey rsa:4096 -keyout "$SSL_DIR/private/galion.app.key" \
            -out "$SSL_DIR/certs/galion.app.crt" -days 365 -nodes \
            -subj "/C=US/ST=California/L=San Francisco/O=Galion/OU=Platform/CN=galion.app"

        # Create symlinks for other domains
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/www.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/www.galion.app.key"
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/developer.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/developer.galion.app.key"
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/studio.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/studio.galion.app.key"

        success "Self-signed certificates created"
    fi

    success "SSL directories created"
}

# Install Certbot for Let's Encrypt
install_certbot() {
    log "Installing Certbot for Let's Encrypt..."

    # Update package list
    sudo apt update

    # Install certbot
    sudo apt install -y certbot python3-certbot-nginx

    # Install certbot-dns-route53 if AWS is available
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        sudo apt install -y python3-certbot-dns-route53
        success "AWS Route53 DNS challenge support installed"
    fi

    success "Certbot installed successfully"
}

# Setup DNS records (manual instructions)
setup_dns_records() {
    log "Setting up DNS records..."

    if [ -z "$RUNPOD_IP" ]; then
        RUNPOD_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_RUNPOD_IP")
    fi

    echo ""
    echo "📋 DNS RECORDS TO CONFIGURE:"
    echo "============================"
    echo ""
    echo "Add these A records to your DNS provider:"
    echo ""
    echo "galion.app          A     $RUNPOD_IP"
    echo "www.galion.app      A     $RUNPOD_IP"
    echo "developer.galion.app A    $RUNPOD_IP"
    echo "studio.galion.app   A     $RUNPOD_IP"
    echo ""
    echo "Optional TXT records for SPF/DKIM:"
    echo "galion.app          TXT   \"v=spf1 include:_spf.google.com ~all\""
    echo "_dmarc.galion.app   TXT   \"v=DMARC1; p=quarantine; rua=mailto:admin@galion.app\""
    echo ""
    echo "⚠️  IMPORTANT: DNS propagation can take 5-30 minutes"
    echo "🔍 Check propagation: nslookup galion.app"
    echo ""

    read -p "Have you configured the DNS records? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "DNS configuration skipped. Run this step again after DNS setup."
        return 1
    fi

    success "DNS records configured"
}

# Get Let's Encrypt certificates
get_letsencrypt_certificates() {
    log "Obtaining Let's Encrypt SSL certificates..."

    # Check if certificates already exist
    if [ -f "$LETSENCRYPT_DIR/live/galion.app/fullchain.pem" ]; then
        log "Certificates already exist. Renewing if needed..."
        sudo certbot renew
        success "Certificates renewed"
        return 0
    fi

    # Get certificates for all domains
    log "Requesting certificates for: $DOMAINS"

    # Use webroot challenge (requires nginx to serve .well-known/acme-challenge)
    sudo certbot certonly --webroot \
        -w /usr/share/nginx/html \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --non-interactive \
        --expand \
        -d galion.app \
        -d www.galion.app \
        -d developer.galion.app \
        -d studio.galion.app

    if [ $? -eq 0 ]; then
        success "Let's Encrypt certificates obtained successfully"

        # Copy certificates to our SSL directory
        sudo cp "$LETSENCRYPT_DIR/live/galion.app/fullchain.pem" "$SSL_DIR/certs/galion.app.crt"
        sudo cp "$LETSENCRYPT_DIR/live/galion.app/privkey.pem" "$SSL_DIR/private/galion.app.key"
        sudo chown $(whoami):$(whoami) "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/private/galion.app.key"

        # Create symlinks for other domains
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/www.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/www.galion.app.key"
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/developer.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/developer.galion.app.key"
        ln -sf "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/certs/studio.galion.app.crt"
        ln -sf "$SSL_DIR/private/galion.app.key" "$SSL_DIR/private/studio.galion.app.key"

        success "SSL certificates copied to project directory"
    else
        error "Failed to obtain Let's Encrypt certificates"
    fi
}

# Alternative: DNS challenge method (for AWS Route53)
get_certificates_dns() {
    log "Obtaining certificates via DNS challenge (AWS Route53)..."

    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        warning "AWS credentials not found. Skipping DNS challenge."
        return 1
    fi

    sudo certbot certonly --dns-route53 \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --non-interactive \
        --expand \
        -d galion.app \
        -d www.galion.app \
        -d developer.galion.app \
        -d studio.galion.app

    success "DNS challenge certificates obtained"
}

# Create production nginx configuration with SSL
create_production_nginx() {
    log "Creating production nginx configuration with SSL..."

    # Backup current config
    if [ -f "nginx.production.conf" ]; then
        cp nginx.production.conf nginx.production.conf.backup
    fi

    # Enable SSL server blocks in the configuration
    # This would uncomment the SSL sections we prepared earlier

    cat > nginx.production.ssl.conf << 'EOF'
# 🚀 GALION PLATFORM - Production SSL Configuration
# Full HTTPS setup with Let's Encrypt certificates

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/x-font-ttf
        application/vnd.ms-fontobject
        font/opentype
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=ai:10m rate=20r/s;

    # Upstream servers - Galion Platform Services
    upstream backend_api {
        least_conn;
        server backend:8000 weight=10 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream galion_app {
        server galion-app:3000 max_fails=3 fail_timeout=30s;
    }

    upstream developer_platform {
        server developer-platform:3020 max_fails=3 fail_timeout=30s;
    }

    upstream galion_studio {
        server galion-studio:3030 max_fails=3 fail_timeout=30s;
    }

    upstream monitoring {
        server monitoring:8080;
    }

    upstream prometheus {
        server prometheus:9090;
    }

    upstream grafana {
        server grafana:3000;
    }

    upstream ai-models {
        server ai-models:8001 max_fails=3 fail_timeout=30s;
    }

    # SSL Configuration (Production)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # ============================================
    # HTTPS PRODUCTION SERVERS
    # ============================================

    # Main Galion.app HTTPS server
    server {
        listen 443 ssl http2;
        server_name galion.app www.galion.app;

        # SSL Certificates
        ssl_certificate /workspace/project-nexus/ssl/certs/galion.app.crt;
        ssl_certificate_key /workspace/project-nexus/ssl/private/galion.app.key;

        # Galion.app - Voice-First Platform
        location / {
            proxy_pass http://galion_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support for voice
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Security headers
            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
            add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        }

        # API for voice features
        location /api/voice/ {
            proxy_pass http://backend_api/api/voice/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            limit_req zone=ai burst=50 nodelay;
        }
    }

    # Developer Platform HTTPS server
    server {
        listen 443 ssl http2;
        server_name developer.galion.app;

        ssl_certificate /workspace/project-nexus/ssl/certs/developer.galion.app.crt;
        ssl_certificate_key /workspace/project-nexus/ssl/private/developer.galion.app.key;

        # Developer Platform - IDE
        location / {
            proxy_pass http://developer_platform;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
        }

        # IDE API
        location /api/ide/ {
            proxy_pass http://backend_api/api/ide/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            limit_req zone=api burst=100 nodelay;
        }
    }

    # Galion Studio HTTPS server
    server {
        listen 443 ssl http2;
        server_name studio.galion.app;

        ssl_certificate /workspace/project-nexus/ssl/certs/studio.galion.app.crt;
        ssl_certificate_key /workspace/project-nexus/ssl/private/studio.galion.app.key;

        # Galion Studio - Corporate Website
        location / {
            proxy_pass http://galion_studio;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
        }
    }

    # ============================================
    # HTTP TO HTTPS REDIRECTS
    # ============================================

    # Redirect all HTTP to HTTPS
    server {
        listen 80;
        server_name galion.app www.galion.app developer.galion.app studio.galion.app;
        return 301 https://$server_name$request_uri;
    }

    # Default HTTP server (development)
    server {
        listen 80 default_server;
        server_name localhost _;

        # Health check endpoint
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Platform health check
        location /health {
            access_log off;
            return 200 "Galion Platform Active (HTTP)\n";
            add_header Content-Type text/plain;
        }

        # Development access (HTTP only)
        location /galion/ {
            proxy_pass http://galion_app/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /developer/ {
            proxy_pass http://developer_platform/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /studio/ {
            proxy_pass http://galion_studio/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            proxy_pass http://backend_api/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            limit_req zone=api burst=100 nodelay;

            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;

            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        location /api/models/ {
            proxy_pass http://ai-models/api/models/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            limit_req zone=ai burst=20 nodelay;

            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, X-Model-Type' always;

            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # WebSocket connections
        location /ws/ {
            proxy_pass http://backend_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }

        # Monitoring routes
        location /monitoring/ {
            proxy_pass http://monitoring/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /metrics {
            proxy_pass http://prometheus/metrics;
            access_log off;
        }

        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            rewrite ^/grafana/(.*)$ /$1 break;
        }

        # Static files
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            try_files /galion-app$uri /developer-platform$uri /galion-studio$uri @backend_static;

            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        location @backend_static {
            proxy_pass http://backend_api;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Error pages
        error_page 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }

        error_page 500 501 502 503 504 = @api_error;
        location @api_error {
            return 503 '{"error": "Service temporarily unavailable", "retry_after": 30}';
            add_header Content-Type application/json;
            add_header Retry-After 30;
        }
    }
}
EOF

    success "Production SSL nginx configuration created"
}

# Update docker-compose to use SSL configuration
update_docker_compose() {
    log "Updating docker-compose for SSL support..."

    # Update nginx service to use SSL config
    sed -i 's|nginx.production.conf:/etc/nginx/nginx.conf:ro|nginx.production.ssl.conf:/etc/nginx/nginx.conf:ro|' docker-compose.yml

    # Ensure SSL volumes are mounted
    if ! grep -q "ssl:/etc/ssl/certs:ro" docker-compose.yml; then
        sed -i '/volumes:/a\      - ./ssl:/etc/ssl/certs:ro' docker-compose.yml
    fi

    success "Docker compose updated for SSL"
}

# Setup certificate renewal
setup_certbot_renewal() {
    log "Setting up automatic certificate renewal..."

    # Create renewal hook
    sudo mkdir -p /etc/letsencrypt/renewal-hooks/post

    cat > cert-renewal-hook.sh << 'EOF'
#!/bin/bash
# Post-renewal hook to copy certificates to project directory

PROJECT_DIR="/workspace/project-nexus"
SSL_DIR="$PROJECT_DIR/ssl"

# Copy certificates
cp /etc/letsencrypt/live/galion.app/fullchain.pem "$SSL_DIR/certs/galion.app.crt"
cp /etc/letsencrypt/live/galion.app/privkey.pem "$SSL_DIR/private/galion.app.key"

# Set permissions
chown $(whoami):$(whoami) "$SSL_DIR/certs/galion.app.crt" "$SSL_DIR/private/galion.app.key"

# Reload nginx
docker-compose restart nginx

echo "SSL certificates renewed and nginx reloaded"
EOF

    chmod +x cert-renewal-hook.sh
    sudo mv cert-renewal-hook.sh /etc/letsencrypt/renewal-hooks/post/

    # Add to crontab for renewal checks
    (crontab -l ; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

    success "Certificate renewal automation configured"
}

# Test SSL configuration
test_ssl_setup() {
    log "Testing SSL configuration..."

    # Restart nginx with new configuration
    docker-compose restart nginx
    sleep 5

    # Test HTTP to HTTPS redirect
    if curl -f -s -I "http://localhost" | grep -q "301 Moved Permanently"; then
        success "HTTP to HTTPS redirect working"
    else
        warning "HTTP redirect not working (expected in development)"
    fi

    # Test SSL certificate (if available)
    if [ -f "$SSL_DIR/certs/galion.app.crt" ]; then
        success "SSL certificates are present"

        # Test certificate validity
        if openssl x509 -checkend 86400 -noout -in "$SSL_DIR/certs/galion.app.crt" >/dev/null 2>&1; then
            success "SSL certificate is valid (expires in more than 24 hours)"
        else
            warning "SSL certificate expires soon or is invalid"
        fi
    else
        warning "SSL certificates not found"
    fi

    success "SSL setup testing completed"
}

# Display SSL status and access URLs
show_ssl_status() {
    echo ""
    echo "🔐 SSL & DOMAIN CONFIGURATION COMPLETE"
    echo "====================================="
    echo ""

    if [ -f "$SSL_DIR/certs/galion.app.crt" ]; then
        echo -e "${GREEN}✅ SSL Certificates: INSTALLED${NC}"

        # Show certificate info
        echo "Certificate details:"
        openssl x509 -in "$SSL_DIR/certs/galion.app.crt" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)" | head -4

        echo ""
        echo "🔒 HTTPS URLs (Production):"
        echo "https://galion.app"
        echo "https://www.galion.app"
        echo "https://developer.galion.app"
        echo "https://studio.galion.app"
    else
        echo -e "${YELLOW}⚠️  SSL Certificates: SELF-SIGNED (Development)${NC}"
        echo "Run with --letsencrypt flag for production SSL"
    fi

    echo ""
    echo "🌐 HTTP URLs (Development):"
    echo "http://localhost/galion/"
    echo "http://localhost/developer/"
    echo "http://localhost/studio/"
    echo ""

    echo "🔧 Management Commands:"
    echo "sudo certbot renew                    # Renew certificates"
    echo "sudo certbot certificates             # List certificates"
    echo "docker-compose restart nginx          # Reload nginx"
    echo ""

    if [ -n "$RUNPOD_IP" ]; then
        echo "🚀 RunPod External URLs:"
        echo "HTTP:  http://$RUNPOD_IP/galion/"
        echo "HTTPS: https://galion.app (after DNS setup)"
        echo ""
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "setup")
            check_environment
            create_ssl_directories
            setup_dns_records && get_letsencrypt_certificates
            create_production_nginx
            update_docker_compose
            setup_certbot_renewal
            test_ssl_setup
            show_ssl_status
            ;;
        "self-signed")
            check_environment
            create_ssl_directories
            create_production_nginx
            update_docker_compose
            test_ssl_setup
            show_ssl_status
            ;;
        "letsencrypt")
            check_environment
            install_certbot
            setup_dns_records && get_letsencrypt_certificates
            create_production_nginx
            update_docker_compose
            setup_certbot_renewal
            test_ssl_setup
            show_ssl_status
            ;;
        "renew")
            sudo certbot renew
            docker-compose restart nginx
            success "Certificates renewed and nginx reloaded"
            ;;
        "status")
            show_ssl_status
            ;;
        "help"|*)
            echo "Galion Platform SSL & Domain Setup"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  setup       - Complete SSL setup (self-signed + Let's Encrypt ready)"
            echo "  self-signed - Setup self-signed certificates for development"
            echo "  letsencrypt - Get Let's Encrypt certificates (requires DNS setup)"
            echo "  renew       - Renew existing Let's Encrypt certificates"
            echo "  status      - Show SSL certificate status"
            echo "  help        - Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  CERTBOT_EMAIL    - Email for Let's Encrypt (default: admin@galion.app)"
            echo "  DOMAINS          - Domains to secure (default: galion.app subdomains)"
            echo "  RUNPOD_IP        - RunPod instance IP for DNS instructions"
            echo "  AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY - For Route53 DNS challenges"
            echo ""
            echo "Examples:"
            echo "  $0 self-signed"
            echo "  CERTBOT_EMAIL=admin@galion.app RUNPOD_IP=123.456.789.0 $0 letsencrypt"
            ;;
    esac
}

# Run main function
main "$@"
