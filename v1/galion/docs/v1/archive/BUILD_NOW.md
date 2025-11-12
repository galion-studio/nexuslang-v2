# 🚀 BUILD NOW - Launch GALION.APP in 5 Minutes

**Zero BS. Just commands. Let's go.**

---

## 🎯 WHAT YOU'RE BUILDING

A microservices platform with:
- User authentication (registration, login, JWT)
- User profiles
- Analytics tracking
- REST API

**Status:** Code complete, tested locally, ready to launch.

---

## ⚡ LAUNCH LOCALLY (2 Commands)

```powershell
# 1. Generate secrets
.\generate-secrets.ps1

# 2. Start everything
docker-compose up -d
```

**Done.** Wait 60 seconds for services to start.

### Verify It Works

```powershell
# Check all services are running
docker-compose ps

# Test the API
curl http://localhost:8080/health
```

**Expected:** All services show `healthy` status, API returns `{"status":"ok"}`.

---

## 🌐 LAUNCH TO INTERNET (Option 1: Cloudflare Tunnel)

**Time:** 15 minutes  
**Cost:** $0  
**Requirements:** None (uses your local machine)

### Step 1: Install Cloudflared

```powershell
winget install --id Cloudflare.cloudflared
```

Close PowerShell and open a new one.

### Step 2: Authenticate

```powershell
cloudflared tunnel login
```

Browser will open. Login to Cloudflare, authorize.

### Step 3: Create Tunnel

```powershell
cloudflared tunnel create nexus-core
```

**Save the Tunnel ID** that appears (looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

### Step 4: Configure DNS

```powershell
cloudflared tunnel route dns nexus-core galion.app
cloudflared tunnel route dns nexus-core api.galion.app
cloudflared tunnel route dns nexus-core app.galion.app
cloudflared tunnel route dns nexus-core www.galion.app
```

### Step 5: Update Config File

Edit `cloudflare-tunnel.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID_HERE  # Replace with ID from Step 3
credentials-file: C:\Users\YOUR_USERNAME\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: galion.app
    service: http://api-gateway:8080
  - hostname: api.galion.app
    service: http://api-gateway:8080
  - hostname: app.galion.app
    service: http://api-gateway:8080
  - hostname: www.galion.app
    service: http://api-gateway:8080
  - service: http_status:404
```

### Step 6: Launch

```powershell
# Generate secrets (if not done already)
.\generate-secrets.ps1

# Start with tunnel
docker-compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d
```

### Step 7: Test

Wait 2 minutes for DNS propagation, then:

```powershell
curl https://galion.app/health
curl https://api.galion.app/health
```

**Expected:** Both return `{"status":"ok"}`.

**DONE.** Your app is live on the internet at galion.app! 🎉

---

## 🖥️ LAUNCH TO INTERNET (Option 2: Production Server)

**Time:** 30 minutes  
**Cost:** $5-20/month  
**Requirements:** Server with public IP

### Step 1: Get a Server

**Recommended:** DigitalOcean Droplet

1. Go to: https://www.digitalocean.com
2. Create droplet:
   - **Image:** Ubuntu 22.04
   - **Plan:** Basic ($5/mo - 1GB RAM)
   - **Datacenter:** Closest to your users
3. Create
4. **Copy the public IP address**

### Step 2: Configure DNS

```powershell
# Run automated DNS setup (replace YOUR_SERVER_IP)
.\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP 203.0.113.45
```

Or manually in Cloudflare dashboard:
1. Go to: https://dash.cloudflare.com
2. Click: galion.app
3. Go to: DNS → Records
4. Add these A records:

```
Name: @     Content: YOUR_SERVER_IP    Proxy: ON
Name: api   Content: YOUR_SERVER_IP    Proxy: ON
Name: app   Content: YOUR_SERVER_IP    Proxy: ON
Name: www   Content: YOUR_SERVER_IP    Proxy: ON
```

### Step 3: Setup Server

SSH to your server:

```bash
ssh root@YOUR_SERVER_IP
```

Install Docker:

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Start Docker
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt install docker-compose-plugin -y
```

### Step 4: Deploy Code

```bash
# Install git
apt install git -y

# Clone repo (replace with your repo URL)
git clone https://github.com/yourusername/project-nexus.git
cd project-nexus

# Generate secrets
chmod +x generate-secrets.sh
./generate-secrets.sh

# Update .env for production
nano .env
# Change: ENVIRONMENT=production
# Change: DEBUG=false
# Change: ALLOWED_ORIGINS=https://galion.app,https://api.galion.app

# Build and start
docker-compose build
docker-compose up -d
```

### Step 5: Configure Firewall

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH
ufw enable
```

### Step 6: Test

From your local machine:

```powershell
curl https://galion.app/health
curl https://api.galion.app/health
```

**Expected:** Both return `{"status":"ok"}`.

**DONE.** Your app is live! 🚀

---

## 🔍 TROUBLESHOOTING

### Services Won't Start

```powershell
# Check what's wrong
docker-compose logs

# Common fix: regenerate secrets
.\generate-secrets.ps1
docker-compose down -v
docker-compose up -d
```

### Can't Access galion.app

```powershell
# Check DNS propagation
nslookup galion.app

# Wait 5 minutes, DNS takes time

# Check if server is reachable
ping YOUR_SERVER_IP

# Check if services are running
docker-compose ps
```

### Error 1016 from Cloudflare

**Cause:** DNS not configured or server not reachable

**Fix:**
1. Verify DNS records exist in Cloudflare dashboard
2. Verify server is running: `docker-compose ps`
3. Verify firewall allows port 80/443
4. Wait 5 minutes for DNS propagation

### Authentication Not Working

```powershell
# Verify JWT secret is consistent
docker exec nexus-auth-service env | grep JWT_SECRET
docker exec nexus-api-gateway env | grep JWT_SECRET

# Should match. If not, regenerate secrets:
.\generate-secrets.ps1
docker-compose restart
```

### Database Connection Errors

```powershell
# Wait for PostgreSQL to be ready (takes 30-60 seconds)
docker exec nexus-postgres pg_isready -U nexuscore

# Check database logs
docker logs nexus-postgres
```

---

## 📊 VERIFY EVERYTHING WORKS

### Test API Endpoints

```powershell
# 1. Health check
curl http://localhost:8080/health

# 2. Register a user
curl -X POST http://localhost:8080/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# 3. Login
curl -X POST http://localhost:8080/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"Test123!"}'

# Copy the token from response

# 4. Get profile (replace YOUR_TOKEN)
curl http://localhost:8080/api/v1/auth/me `
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Access Dashboards

- **Grafana:** http://localhost:3000 (username: admin, password: from generate-secrets.ps1)
- **API Docs:** http://localhost:8000/docs
- **Kafka UI:** http://localhost:8090

---

## 🎯 WHAT'S RUNNING

After `docker-compose up -d`, you have 11 services:

### Application Services (4)
- **API Gateway** (Go) - Port 8080 - Routes all requests
- **Auth Service** (Python) - Port 8000 - Registration/Login
- **User Service** (Python) - Port 8001 - Profiles
- **Analytics Service** (Go) - Port 9090 - Event processing

### Data Stores (4)
- **PostgreSQL** - Port 5432 - Primary database
- **Redis** - Port 6379 - Cache & sessions
- **Kafka** - Port 9092 - Event streaming
- **Zookeeper** - Port 2181 - Kafka coordination

### Monitoring (3)
- **Prometheus** - Port 9091 - Metrics collection
- **Grafana** - Port 3000 - Dashboards
- **Kafka-UI** - Port 8090 - Kafka management

---

## 🔐 SECURITY CHECKLIST

### For Local Development: ✅
- [x] Secrets in .env file
- [x] .env in .gitignore
- [x] Strong passwords generated

### For Production Deployment: ⚠️

```powershell
# Before going live, update .env:
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://galion.app,https://api.galion.app,https://app.galion.app

# Change default passwords
POSTGRES_PASSWORD=<new-strong-password>
REDIS_PASSWORD=<new-strong-password>
JWT_SECRET_KEY=<new-64-char-hex>

# Restart with new config
docker-compose down
docker-compose up -d
```

---

## ⚡ PERFORMANCE TUNING

### Resource Allocation

Edit `docker-compose.yml` for more resources:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Increase from 1.0
      memory: 1024M    # Increase from 512M
    reservations:
      cpus: '1.0'
      memory: 512M
```

### Scaling Services

```powershell
# Scale user service to 3 instances
docker-compose up -d --scale user-service=3

# Note: Need load balancer for this to work properly
```

---

## 📈 MONITORING

### View Metrics

1. Open Grafana: http://localhost:3000
2. Login: admin / <password from generate-secrets.ps1>
3. Go to: Dashboards → Analytics Overview

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service

# Last 50 lines
docker-compose logs --tail 50 api-gateway
```

### Check Resource Usage

```powershell
docker stats
```

---

## 🔄 UPDATES & MAINTENANCE

### Reload All Services (Clear Cache + Restart)

**FASTEST WAY - Use the reload script:**

```powershell
# Windows
.\reload-nexus.ps1

# Linux/Mac  
./reload-nexus.sh
```

This will:
- Clear Redis cache
- Stop all services
- Remove containers
- Start fresh
- Verify health

**Perfect for:**
- After code changes
- When services act weird
- Cache issues
- Need clean slate

### Update Code

```powershell
# Pull latest code
git pull

# Rebuild specific service
docker-compose build auth-service

# Restart
docker-compose up -d auth-service
```

### Backup Database

```powershell
# Create backup
docker exec nexus-postgres pg_dump -U nexuscore nexuscore > backup.sql

# Restore backup
docker exec -i nexus-postgres psql -U nexuscore nexuscore < backup.sql
```

### Clean Up

```powershell
# Stop all services
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v

# Remove old images
docker system prune -a
```

---

## 🎯 NEXT STEPS

### After Launch:

1. **Test Everything**
   - Register users
   - Login
   - Check analytics in Grafana

2. **Monitor Performance**
   - Watch Grafana dashboards
   - Check logs for errors

3. **Secure for Production**
   - Change all default passwords
   - Set up SSL certificates (Cloudflare does this automatically)
   - Configure backups
   - Set up alerts

4. **Build Frontend**
   - React/Next.js app
   - Deploy to app.galion.app
   - Connect to API

5. **Add Features**
   - More services (chat, CMS, etc.)
   - More analytics
   - More integrations

---

## 📚 MORE INFO

- **Status:** See TRANSPARENT_STATUS.md
- **Architecture:** See ARCHITECTURE.md  
- **Production Deployment:** See LAUNCH.md
- **API Documentation:** See API.md

---

## ✅ SUCCESS CRITERIA

**You're successful when:**
1. ✅ `docker-compose ps` shows all services healthy
2. ✅ `curl http://localhost:8080/health` returns 200
3. ✅ You can register and login via API
4. ✅ Grafana dashboards show data
5. ✅ (If deployed) galion.app is accessible from internet

---

**NOW GO BUILD!** 🚀

**Questions?** Everything should be clear. If not, the docs suck and need fixing.

**Problems?** Check logs: `docker-compose logs`

**Ready to launch to production?** See LAUNCH.md

