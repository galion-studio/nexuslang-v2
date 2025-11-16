# ============================================
# DEVELOPER.GALION.APP - IDE PLATFORM
# ============================================

server {
    listen 80;
    server_name developer.galion.app;

    location /.well-known/acme-challenge/ {
        allow all;
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://developer.galion.app$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name developer.galion.app;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/developer.galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/developer.galion.app/privkey.pem;

    # Higher rate limits for developers
    limit_req zone=frontend burst=100 nodelay;

    # IDE root directory
    root /var/www/developer-galion;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;

        # API proxy for NexusLang execution
        location /api/ {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Higher limits for development
            limit_req zone=api burst=50 nodelay;
        }

        # WebSocket for real-time collaboration
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
        }
    }

    # Static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1M;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Development endpoints (protected)
    location /dev/ {
        # Basic auth for development access
        auth_basic "Developer Access";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

