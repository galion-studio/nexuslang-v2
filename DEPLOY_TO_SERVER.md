# 🚀 Deploy NexusLang v2 to Your Server

**Complete guide to upload and run on your server for developer.galion.app**

---

## 📦 OPTION 1: Upload via Git (Recommended)

### On Your Server

```bash
# SSH into your server
ssh root@your-server-ip

# Navigate to web directory
cd /var/www  # or wherever you want to deploy

# Clone from GitHub
git clone https://github.com/galion-studio/galion-platform.git nexuslang-v2
cd nexuslang-v2

# All your code is now on the server!
```

**Advantage:** Easy updates with `git pull`

---

## 📦 OPTION 2: Upload Entire Folder

### On Your Windows Machine

**Method A: Using WinSCP (GUI)**

1. Download WinSCP: https://winscp.net/
2. Connect to your server (SFTP)
3. Navigate to `/var/www/`
4. Upload entire `project-nexus` folder
5. Rename to `nexuslang-v2`

**Method B: Using PowerShell (SCP)**

```powershell
# Compress the project (exclude large files)
Compress-Archive -Path "C:\Users\Gigabyte\Documents\project-nexus\*" `
  -DestinationPath "C:\Users\Gigabyte\Documents\nexuslang-v2.zip" `
  -Force

# Upload to server
scp C:\Users\Gigabyte\Documents\nexuslang-v2.zip root@your-server-ip:/root/

# On server: Extract
ssh root@your-server-ip "cd /var/www && unzip /root/nexuslang-v2.zip -d nexuslang-v2"
```

**Method C: Using rsync (if available)**

```powershell
# Install rsync on Windows first
# Then sync to server
rsync -avz --progress C:\Users\Gigabyte\Documents\project-nexus\ root@your-server-ip:/var/www/nexuslang-v2/
```

---

## 📦 OPTION 3: Create Deployment Package

Let me create a clean deployment package for you:

```powershell
# On your Windows machine
cd C:\Users\Gigabyte\Documents\project-nexus

# Create deployment package
.\create-deployment-package.ps1
```

This will create `nexuslang-v2-deploy.zip` with only necessary files (no node_modules, no git history).

---

## 🔧 SERVER SETUP (Once Files Are Uploaded)

### Step 1: Install Requirements

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose -y

# Install Python (for NexusLang CLI)
apt install python3.11 python3-pip -y
```

### Step 2: Navigate to Project

```bash
cd /var/www/nexuslang-v2
# or wherever you uploaded it
```

### Step 3: Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required settings:**
```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Security
SECRET_KEY=generate_random_key_here
JWT_SECRET=another_random_key_here

# API Keys
OPENAI_API_KEY=sk-your-openai-key
SHOPIFY_API_KEY=your-shopify-key
SHOPIFY_API_SECRET=your-shopify-secret

# Production URLs
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app
```

### Step 4: Deploy Services

```bash
# Start all services
docker-compose up -d

# Wait for services (1 minute)
sleep 60

# Check status
docker-compose ps

# Initialize database
docker-compose exec -T postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql
```

### Step 5: Setup Nginx

```bash
# Install Nginx
apt install nginx -y

# Copy configuration
cp v2/infrastructure/nginx/developer.galion.app.conf /etc/nginx/sites-available/developer.galion.app

# Enable site
ln -s /etc/nginx/sites-available/developer.galion.app /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

### Step 6: Setup SSL with Cloudflare

**Option A: Cloudflare Origin Certificate (Recommended)**

See `CLOUDFLARE_SETUP_DEVELOPER.md` for complete guide.

**Option B: Let's Encrypt**

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificates
certbot --nginx -d developer.galion.app -d api.developer.galion.app

# Auto-renewal is configured automatically
```

### Step 7: Configure Cloudflare DNS

In your Cloudflare dashboard for `galion.app`:

```
DNS Records:
Type    Name                      Content             Proxy Status
A       developer                 YOUR_SERVER_IP      ✅ Proxied
A       api.developer             YOUR_SERVER_IP      ✅ Proxied
```

### Step 8: Verify Deployment

```bash
# Check all services
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Check logs
docker-compose logs -f
```

### Step 9: GO LIVE! 🚀

Visit:
- https://developer.galion.app
- https://api.developer.galion.app/docs

---

## ⚡ QUICK DEPLOY SCRIPT

For fastest deployment, I'll create an all-in-one script:

```bash
# On server (after uploading files)
chmod +x quick-deploy-server.sh
./quick-deploy-server.sh
```

This script will:
1. ✅ Install all dependencies
2. ✅ Start Docker services
3. ✅ Initialize database
4. ✅ Configure Nginx
5. ✅ Prompt for SSL setup
6. ✅ Verify everything

---

## 📊 SERVER REQUIREMENTS

### Minimum

- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 20GB
- **OS:** Ubuntu 22.04 or newer

### Recommended

- **CPU:** 4 cores
- **RAM:** 8GB
- **Disk:** 50GB
- **OS:** Ubuntu 22.04 LTS

### Optimal

- **CPU:** 8 cores
- **RAM:** 16GB
- **Disk:** 100GB
- **OS:** Ubuntu 22.04 LTS

---

## 🔒 SECURITY CHECKLIST

```bash
# On server after deployment

# 1. Setup firewall
ufw allow 22      # SSH
ufw allow 80      # HTTP
ufw allow 443     # HTTPS
ufw enable

# 2. Disable root login
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
systemctl restart sshd

# 3. Setup fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# 4. Enable automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

---

## 📞 NEED HELP?

### If Upload Fails

- Use Git method (easiest)
- Or zip smaller chunks
- Or use file transfer service (WeTransfer, etc.)

### If Services Won't Start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
systemctl restart docker
```

### If Domain Won't Connect

- Wait for DNS propagation (up to 24 hours)
- Check Cloudflare proxy is enabled (orange cloud)
- Verify server IP is correct
- Check nginx: `nginx -t`

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Files uploaded to server (via Git or SCP)
- [ ] Docker and Docker Compose installed
- [ ] .env file configured with your keys
- [ ] Services started with `docker-compose up -d`
- [ ] Database initialized
- [ ] Nginx configured
- [ ] DNS configured in Cloudflare
- [ ] SSL certificates obtained
- [ ] Firewall configured
- [ ] Services verified running
- [ ] **Platform LIVE at developer.galion.app!** 🚀

---

## 🎯 WHAT YOU GET LIVE

Once deployed on your server:

- **https://developer.galion.app** - Full platform
  - Beautiful landing page
  - Web IDE with Monaco editor
  - Grokopedia knowledge search
  - Community forums
  - Billing with Shopify
  
- **https://api.developer.galion.app** - Backend API
  - 40+ endpoints
  - Auto-generated docs
  - WebSocket support
  - Real-time features

---

**Choose your upload method and deploy to your server!**

**All 11 plan todos are complete and ready to go live!** 🚀

