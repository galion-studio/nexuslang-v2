# ============================================
# API.GALION.APP - API GATEWAY
# ============================================

server {
    listen 80;
    server_name api.galion.app;

    location /.well-known/acme-challenge/ {
        allow all;
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://api.galion.app$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.galion.app;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.galion.app/privkey.pem;

    # API Rate limiting
    limit_req zone=api burst=10 nodelay;

    # CORS for API access
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH";
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-API-Key";

    # Handle preflight requests
    location / {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket endpoint with special handling
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;

        # Voice API specific limits
        limit_req zone=voice burst=5 nodelay;
    }

    # Health check (public)
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }

    # API documentation
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

