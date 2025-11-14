# NexusLang v2 - Nginx Reverse Proxy with SSL
FROM nginx:alpine

# Install openssl for certificate generation
RUN apk add --no-cache openssl

# Create SSL directory
RUN mkdir -p /etc/ssl/certs /etc/ssl/private

# Generate self-signed certificate for development
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nexus.key \
    -out /etc/ssl/certs/nexus.crt \
    -subj "/C=US/ST=State/L=City/O=NexusLang/CN=localhost"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directory
RUN mkdir -p /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/nginx-health || exit 1

EXPOSE 80 443
