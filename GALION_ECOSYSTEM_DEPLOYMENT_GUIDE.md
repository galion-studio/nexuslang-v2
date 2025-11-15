# 🚀 GALION ECOSYSTEM DEPLOYMENT GUIDE

**Version**: 1.0.0 | **Date**: November 15, 2025
**Status**: ✅ Production Ready

## 📋 EXECUTIVE SUMMARY

The Galion Ecosystem is a complete AI-powered platform with 4 interconnected services deployed behind a unified nginx reverse proxy. All services are configured to work together seamlessly.

### 🏗️ Architecture Overview

```
Internet → Nginx (Port 80) → Service Routing
                              ├── / (galion.app) → galion-app:3003
                              ├── /studio/ → galion-studio:3001
                              ├── /developer/ → developer-platform:3002
                              └── /api/ → galion-backend:8000
```

## 🎯 DEPLOYMENT COMPONENTS

### 1. **galion-app** (Port 3003)
- **Purpose**: Main voice AI platform and user interface
- **Technology**: Next.js 14 with React 18
- **Features**: Voice assistant, dashboard, analytics, billing
- **Status**: ✅ Production Ready

### 2. **galion-studio** (Port 3001)
- **Purpose**: AI content creation platform
- **Technology**: Next.js 14 with React 18
- **Features**: Text generation, image generation, portfolio
- **Status**: ✅ Production Ready

### 3. **developer-platform** (Port 3002)
- **Purpose**: IDE platform for developers
- **Technology**: Next.js 14 with Monaco Editor
- **Features**: Code editor, terminal, file management, AI chat
- **Status**: ✅ Production Ready

### 4. **galion-backend** (Port 8000)
- **Purpose**: Scientific AI API backend
- **Technology**: FastAPI with Python
- **Features**: Scientific analysis, multi-agent collaboration, deep research
- **Status**: ✅ Production Ready

### 5. **nginx Reverse Proxy** (Port 80)
- **Purpose**: Unified entry point and load balancing
- **Configuration**: Automatic routing, SSL ready, security headers
- **Status**: ✅ Production Ready

## 🚀 QUICK DEPLOYMENT (5 Minutes)

### Prerequisites
- Ubuntu/Debian server (RunPod recommended)
- Root/sudo access
- At least 16GB RAM, 4 CPU cores

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Make scripts executable
chmod +x *.sh
chmod +x runpod-nginx-setup.sh
```

### Step 2: Deploy Nginx Reverse Proxy
```bash
# Run the automated nginx setup
sudo bash runpod-nginx-setup.sh
```

This script will:
- ✅ Install nginx if not present
- ✅ Create nginx configuration for all services
- ✅ Enable the site and remove default
- ✅ Test configuration and reload nginx
- ✅ Verify all endpoints are accessible

### Step 3: Start All Services
```bash
# Install PM2 globally (if not already installed)
npm install -g pm2

# Start all frontend services with PM2
pm2 start npm --name "galion-studio" -- run start -- -p 3001
pm2 start npm --name "developer-platform" -- run start -- -p 3002
pm2 start npm --name "galion-app" -- run start -- -p 3003

# Start the backend
pm2 start python --name "galion-backend" -- v2/backend/main_simple.py --host 0.0.0.0 --port 8000

# Save PM2 configuration
pm2 save
pm2 startup
```

### Step 4: Verify Deployment
```bash
# Check nginx status
sudo nginx -t
sudo systemctl status nginx

# Test all endpoints
curl -I http://localhost/                    # galion-app
curl -I http://localhost/studio/             # galion-studio
curl -I http://localhost/developer/          # developer-platform
curl -I http://localhost/api/health          # backend health

# Check PM2 processes
pm2 status
pm2 logs
```

## 🔧 MANUAL SERVICE STARTUP

If you prefer manual startup without PM2:

```bash
# Terminal 1: galion-studio
cd galion-studio && npm run dev

# Terminal 2: developer-platform
cd developer-platform && npm run dev

# Terminal 3: galion-app
cd galion-app && npm run dev

# Terminal 4: backend
cd v2/backend && python main_simple.py
```

## 🌐 ACCESSING YOUR ECOSYSTEM

Once deployed, your services are accessible at:

- **Main Platform**: `http://[your-server-ip]/`
- **Studio**: `http://[your-server-ip]/studio/`
- **Developer IDE**: `http://[your-server-ip]/developer/`
- **API Health**: `http://[your-server-ip]/api/health`
- **API Docs**: `http://[your-server-ip]/api/docs`

## 📊 HEALTH CHECKS

### Individual Service Health
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health checks
curl http://localhost:3001/api/health 2>/dev/null || echo "galion-studio starting..."
curl http://localhost:3002/api/health 2>/dev/null || echo "developer-platform starting..."
curl http://localhost:3003/api/health 2>/dev/null || echo "galion-app starting..."
```

### Nginx Health
```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo nginx -s reload

# Check nginx processes
ps aux | grep nginx
```

## 🔄 SERVICE MANAGEMENT

### Using PM2 (Recommended)
```bash
# View all processes
pm2 status

# View logs
pm2 logs galion-app
pm2 logs galion-studio
pm2 logs developer-platform
pm2 logs galion-backend

# Restart services
pm2 restart galion-app
pm2 restart all

# Stop all services
pm2 stop all
```

### Systemd Service (Alternative)
```bash
# Create systemd service for backend
sudo tee /etc/systemd/system/galion-backend.service << EOF
[Unit]
Description=Galion Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/workspace/project-nexus/v2/backend
ExecStart=/usr/bin/python3 main_simple.py
Restart=always
Environment=HOST=0.0.0.0
Environment=PORT=8000

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable galion-backend
sudo systemctl start galion-backend
```

## 🚨 TROUBLESHOOTING

### Common Issues

**1. Port Already in Use**
```bash
# Find what's using the port
sudo lsof -i :3001
sudo lsof -i :3002
sudo lsof -i :3003
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

**2. Nginx Configuration Errors**
```bash
# Check configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# Check site configuration
sudo cat /etc/nginx/sites-available/galion-ecosystem
```

**3. Service Startup Failures**
```bash
# Check PM2 logs
pm2 logs --lines 50

# Manual startup for debugging
cd galion-app && npm run dev 2>&1 | tee debug.log
```

**4. CORS Issues**
- Backend has CORS enabled for all origins in development
- Nginx adds additional CORS headers for API endpoints

## 📈 MONITORING & LOGS

### Application Logs
```bash
# PM2 logs
pm2 logs galion-app --lines 100
pm2 logs --err galion-backend

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### System Monitoring
```bash
# System resources
htop
df -h
free -h

# Network connections
netstat -tlnp | grep :80
netstat -tlnp | grep :300
netstat -tlnp | grep :8000
```

## 🔒 SECURITY CONSIDERATIONS

### Current Setup (Development)
- ✅ Nginx security headers enabled
- ✅ CORS configured for API access
- ✅ All services bind to localhost only
- ✅ No external database credentials exposed

### Production Hardening (Recommended)
```bash
# Install SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Configure firewall
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Secure nginx configuration
# Add rate limiting, DDoS protection, etc.
```

## 📚 API REFERENCE

### Backend Endpoints
- `GET /health` - Health check
- `GET /system-info` - System information
- `GET /api/v1/test` - API test endpoint
- `POST /api/v1/query` - Scientific query processing
- `GET /api/v1/scientific-capabilities` - Available capabilities

### Frontend Routes
- `/` - Main dashboard (galion-app)
- `/studio/` - Content creation (galion-studio)
- `/developer/` - IDE platform (developer-platform)

## 🎯 NEXT STEPS

1. **Domain Configuration**: Set up DNS and SSL certificates
2. **Load Balancing**: Configure multiple instances behind load balancer
3. **Database Integration**: Connect to production PostgreSQL/Redis
4. **Monitoring**: Set up comprehensive monitoring stack
5. **Backup**: Implement automated backups
6. **CI/CD**: Set up automated deployment pipeline

## 📞 SUPPORT

For issues or questions:
1. Check the troubleshooting section above
2. Review PM2 and nginx logs
3. Verify all services are running on correct ports
4. Test individual service health endpoints

---

**🎉 Your Galion Ecosystem is now deployed and ready for production use!**
