# Cloudflare Tunnels Setup for NexusLang v2

## Overview

This project now includes Cloudflare Tunnel support for exposing your local services to the internet securely through two domains:
- **galion.studio**
- **galion.app**

Both domains are configured to route traffic through Cloudflare's network, providing:
- ✅ Free SSL/TLS certificates
- ✅ DDoS protection
- ✅ CDN caching
- ✅ No need to open ports on your firewall
- ✅ Automatic HTTPS

## Files Created

### Configuration Files
- `cloudflare-tunnel-galion-studio.yml` - Tunnel config for galion.studio
- `cloudflare-tunnel-galion-app.yml` - Tunnel config for galion.app
- `docker-compose.cloudflare.yml` - Docker compose override with both tunnels

### Scripts
- `start-with-cloudflare.ps1` - PowerShell script for Windows
- `start-with-cloudflare.sh` - Bash script for Linux/Mac

## Quick Start

### Windows (PowerShell)
```powershell
.\start-with-cloudflare.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x start-with-cloudflare.sh
./start-with-cloudflare.sh
```

### Manual Start
```bash
# Start main services + Cloudflare tunnels
docker-compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d

# View logs
docker-compose logs -f cloudflared-studio cloudflared-app

# Stop everything
docker-compose down
```

## Exposed Services

### galion.studio
| Subdomain | Service | Local Port |
|-----------|---------|------------|
| galion.studio | Frontend | 3000 |
| www.galion.studio | Frontend | 3000 |
| api.galion.studio | Backend API | 8000 |
| grafana.galion.studio | Grafana | 3001 |
| prometheus.galion.studio | Prometheus | 9090 |

### galion.app
| Subdomain | Service | Local Port |
|-----------|---------|------------|
| galion.app | Frontend | 3000 |
| www.galion.app | Frontend | 3000 |
| api.galion.app | Backend API | 8000 |
| grafana.galion.app | Grafana | 3001 |
| prometheus.galion.app | Prometheus | 9090 |

## Environment Variables

Make sure you have a `.env` file with required variables:

```env
# Database
POSTGRES_USER=nexus
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=nexus_v2

# Cache
REDIS_PASSWORD=your_redis_password

# Application Secrets
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Optional: API Keys
OPENAI_API_KEY=your_openai_key
SHOPIFY_API_KEY=your_shopify_key
SHOPIFY_API_SECRET=your_shopify_secret

# Monitoring
GRAFANA_PASSWORD=admin
```

## How It Works

1. **Cloudflare Tunnel Containers**: Two `cloudflared` containers run as Docker services
2. **Token Authentication**: Each tunnel uses a pre-configured token (embedded in docker-compose)
3. **Service Routing**: Tunnels route incoming requests to internal Docker services
4. **No Port Forwarding**: No need to expose ports directly to the internet
5. **Automatic SSL**: Cloudflare handles SSL/TLS certificates automatically

## Monitoring Tunnels

### Check Tunnel Status
```bash
# View tunnel logs
docker-compose logs cloudflared-studio
docker-compose logs cloudflared-app

# Check if tunnels are running
docker-compose ps | grep cloudflared
```

### Restart Tunnels
```bash
# Restart both tunnels
docker-compose restart cloudflared-studio cloudflared-app

# Restart specific tunnel
docker-compose restart cloudflared-studio
```

## Troubleshooting

### Tunnel Not Connecting
1. Check logs: `docker-compose logs cloudflared-studio`
2. Verify token is correct in `docker-compose.cloudflare.yml`
3. Ensure Docker containers are on the same network
4. Check Cloudflare dashboard for tunnel status

### Services Not Accessible
1. Verify services are running: `docker-compose ps`
2. Check service health: `docker-compose logs backend frontend`
3. Test local access first: `http://localhost:3000`
4. Verify DNS records in Cloudflare dashboard

### 502 Bad Gateway
- Service might not be ready yet (wait 30-60 seconds)
- Check if backend is healthy: `curl http://localhost:8000/health`
- Restart the problematic service

## Security Notes

⚠️ **Important**: The tunnel tokens in this configuration provide direct access to your services
- Tokens are embedded in `docker-compose.cloudflare.yml`
- Keep this file secure
- Never commit tokens to public repositories
- Rotate tokens if compromised via Cloudflare dashboard

## DNS Configuration

Make sure these DNS records are set in Cloudflare:

### galion.studio
- `galion.studio` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `www.galion.studio` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `api.galion.studio` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `grafana.galion.studio` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `prometheus.galion.studio` → CNAME → `<tunnel-id>.cfargotunnel.com`

### galion.app
- `galion.app` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `www.galion.app` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `api.galion.app` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `grafana.galion.app` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `prometheus.galion.app` → CNAME → `<tunnel-id>.cfargotunnel.com`

*Note: DNS records are usually configured automatically when using tunnel tokens*

## Architecture

```
Internet
    ↓
Cloudflare Network
    ↓
[Cloudflare Tunnel (cloudflared containers)]
    ↓
Docker Network (nexus-network)
    ↓
[Frontend] [Backend] [Grafana] [Prometheus]
    ↓
[PostgreSQL] [Redis] [Elasticsearch]
```

## Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project Main README](./README.md)

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all services are healthy: `docker-compose ps`
3. Check Cloudflare dashboard for tunnel status
4. Test local access before testing public URLs

---

**Status**: ✅ Ready to use
**Last Updated**: November 11, 2025

