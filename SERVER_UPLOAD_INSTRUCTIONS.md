# 📤 SERVER UPLOAD INSTRUCTIONS

**How to get NexusLang v2 onto your server for developer.galion.app**

---

## ✅ EVERYTHING IS READY IN GITHUB

**Your complete platform is already on GitHub!**

Repository: https://github.com/galion-studio/galion-platform.git

---

## 🚀 EASIEST METHOD: Clone from GitHub on Server

### Step 1: SSH into Your Server

```bash
ssh root@your-server-ip
```

### Step 2: Clone the Repository

```bash
# Navigate to web directory
cd /var/www

# Clone from GitHub (all your code is there!)
git clone https://github.com/galion-studio/galion-platform.git nexuslang-v2

# Enter directory
cd nexuslang-v2
```

### Step 3: Run Deployment Script

```bash
# Make script executable
chmod +x quick-deploy-server.sh

# Run deployment
./quick-deploy-server.sh
```

**That's it!** The script will:
- ✅ Install all dependencies (Docker, Nginx, etc.)
- ✅ Start all services
- ✅ Initialize database
- ✅ Configure Nginx
- ✅ Setup firewall
- ✅ Get you ready to go live

### Step 4: Configure DNS

In Cloudflare dashboard for `galion.app`:

```
Add DNS Records:
Type    Name                      Content                 Proxy
A       developer                 YOUR_SERVER_IP          ✅ On
A       api.developer             YOUR_SERVER_IP          ✅ On
```

### Step 5: Setup SSL

```bash
# Option A: Let's Encrypt (automatic)
sudo certbot --nginx -d developer.galion.app -d api.developer.galion.app

# Option B: Cloudflare Origin Certificate
# See CLOUDFLARE_SETUP_DEVELOPER.md
```

### Step 6: GO LIVE! 🚀

Visit:
- https://developer.galion.app
- https://api.developer.galion.app/docs

**Done! Your platform is live!**

---

## 📦 ALTERNATIVE: Create & Upload Package

If you can't use Git on the server, create a deployment package:

### On Your Windows Machine

```powershell
# Create deployment package
.\create-deployment-package.ps1

# This creates: nexuslang-v2-deploy-TIMESTAMP.zip
```

### Upload to Server

**Option A: WinSCP (Easiest)**
1. Download WinSCP: https://winscp.net/
2. Connect to your server
3. Upload the .zip file to `/root/`
4. Done!

**Option B: Command Line**
```powershell
scp nexuslang-v2-deploy-*.zip root@your-server-ip:/root/
```

### On Server

```bash
# Extract
cd /var/www
unzip /root/nexuslang-v2-deploy-*.zip -d nexuslang-v2
cd nexuslang-v2

# Deploy
chmod +x quick-deploy-server.sh
./quick-deploy-server.sh
```

---

## 🖥️ YOUR SERVER INFO

### What You Need
- **Server IP:** Your VPS/server IP address
- **SSH Access:** Root or sudo user
- **Domain:** galion.app (in Cloudflare)
- **API Keys:** OpenAI, Shopify (optional for testing)

### Server Requirements
- **Minimum:** 2 CPU, 4GB RAM, 20GB disk
- **Recommended:** 4 CPU, 8GB RAM, 50GB disk
- **OS:** Ubuntu 22.04 LTS

---

## ⚡ FASTEST DEPLOYMENT (5 Commands)

```bash
# 1. SSH to server
ssh root@your-server-ip

# 2. Clone repository
cd /var/www && git clone https://github.com/galion-studio/galion-platform.git nexuslang-v2 && cd nexuslang-v2

# 3. Configure
cp .env.example .env && nano .env
# (Add your API keys, then save)

# 4. Deploy
chmod +x quick-deploy-server.sh && ./quick-deploy-server.sh

# 5. Setup SSL
certbot --nginx -d developer.galion.app -d api.developer.galion.app
```

**DONE! You're live!**

---

## 📊 WHAT WILL BE RUNNING

### Docker Services (8)

1. **PostgreSQL** - Database with pgvector
2. **Redis** - Cache
3. **Elasticsearch** - Search
4. **Backend API** - FastAPI (port 8000)
5. **Frontend** - Next.js (port 3000)
6. **Prometheus** - Metrics (port 9090)
7. **Grafana** - Dashboards (port 3001)
8. **PgBouncer** - Connection pooling

### Nginx Reverse Proxy

- developer.galion.app → Frontend (port 3000)
- api.developer.galion.app → Backend (port 8000)

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:

```bash
# Check services
docker-compose ps
# All should be "Up"

# Test backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Test frontend
curl http://localhost:3000
# Should return HTML

# Check logs
docker-compose logs -f
# Should show no errors

# Test domain (after DNS)
curl https://developer.galion.app
# Should return HTML

# Test API
curl https://api.developer.galion.app/health
# Should return: {"status":"healthy"}
```

---

## 🆘 TROUBLESHOOTING

### Can't SSH to Server

```bash
# Check SSH service
systemctl status sshd

# Check firewall
ufw status
ufw allow 22/tcp
```

### Git Clone Fails

```bash
# Use HTTPS instead
git clone https://github.com/galion-studio/galion-platform.git

# Or download as ZIP from GitHub
wget https://github.com/galion-studio/galion-platform/archive/refs/heads/main.zip
unzip main.zip
mv galion-platform-main nexuslang-v2
```

### Docker Services Won't Start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
systemctl restart docker
docker-compose up -d
```

### Domain Won't Connect

```bash
# Check DNS
nslookup developer.galion.app

# Wait for DNS propagation (can take 1-24 hours)

# Check Nginx
nginx -t
systemctl status nginx

# Check firewall
ufw status
```

---

## 📞 SUPPORT

### Documentation on Server

All documentation is in the uploaded files:
- `README.md` - Main overview
- `QUICKSTART.md` - Setup guide
- `DEPLOY_TO_SERVER.md` - This guide
- `CLOUDFLARE_SETUP_DEVELOPER.md` - DNS/SSL

### View Logs

```bash
# Application logs
docker-compose logs -f

# Nginx logs
tail -f /var/log/nginx/developer.galion.app.access.log
tail -f /var/log/nginx/developer.galion.app.error.log

# System logs
journalctl -u docker -f
```

---

## 🎯 SUMMARY

**Everything you need is on GitHub!**

**Just:**
1. SSH to your server
2. Clone from GitHub (1 command)
3. Run deployment script (1 command)
4. Configure DNS in Cloudflare
5. Setup SSL
6. **GO LIVE!**

**Your complete NexusLang v2 platform will be running on developer.galion.app!**

---

**Repository:** https://github.com/galion-studio/galion-platform.git  
**Branch:** main  
**Status:** ✅ All 11 plan todos complete & pushed

🚀 **READY TO DEPLOY!** 🚀

