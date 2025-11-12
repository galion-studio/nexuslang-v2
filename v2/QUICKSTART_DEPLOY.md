# ⚡ Quick Deploy - Get Running in 10 Minutes

## Prerequisites

- RunPod account with active instance
- SSH access configured
- Git installed locally

---

## 🚀 Option 1: One-Command Deploy (Recommended)

### Linux/Mac:
```bash
# Set your RunPod details
export RUNPOD_HOST="your-runpod-ip"
export RUNPOD_PORT="your-ssh-port"

# Deploy!
chmod +x v2/deploy-to-runpod.sh
./v2/deploy-to-runpod.sh
```

### Windows (PowerShell):
```powershell
# Set your RunPod details
$env:RUNPOD_HOST = "your-runpod-ip"
$env:RUNPOD_PORT = "your-ssh-port"

# Deploy!
.\v2\deploy-to-runpod.ps1
```

**That's it!** The script will:
- ✅ Check SSH connection
- ✅ Clone/update repository
- ✅ Install dependencies
- ✅ Configure environment
- ✅ Start Docker services
- ✅ Run database migrations
- ✅ Verify deployment

---

## 🚀 Option 2: Manual Deploy

### Step 1: SSH into RunPod
```bash
ssh root@your-runpod-ip -p your-port
```

### Step 2: Clone Repository
```bash
cd ~
git clone https://github.com/yourusername/project-nexus.git
cd project-nexus/v2
```

### Step 3: Install Dependencies
```bash
apt-get update
apt-get install -y docker.io docker-compose postgresql-client
systemctl start docker
```

### Step 4: Configure Environment
```bash
# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://nexuslang:your_password@postgres:5432/nexuslang_v2
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=["http://localhost:3100","https://developer.galion.app"]
BACKEND_PORT=8100
FRONTEND_PORT=3100
STORAGE_TYPE=local
ENVIRONMENT=production
EOF

# Generate secure password
sed -i "s/your_password/$(openssl rand -base64 32)/g" .env
```

### Step 5: Start Services
```bash
docker-compose -f docker-compose.nexuslang.yml up -d
```

### Step 6: Run Migrations
```bash
# Wait for services to start
sleep 30

# Initialize database
docker-compose -f docker-compose.nexuslang.yml exec -T backend python -c "
from core.database import init_db
import asyncio
asyncio.run(init_db())
"

# Run content manager migration
docker-compose -f docker-compose.nexuslang.yml exec -T postgres \
  psql -U nexuslang nexuslang_v2 < database/migrations/003_content_manager.sql
```

### Step 7: Verify
```bash
# Check services
docker-compose ps

# Test API
curl http://localhost:8100/health
```

---

## 🌐 Access Your System

### Local Access (from RunPod):
- **Backend**: http://localhost:8100
- **Frontend**: http://localhost:3100
- **API Docs**: http://localhost:8100/docs

### External Access:
- **Backend**: http://your-runpod-ip:8100
- **Frontend**: http://your-runpod-ip:3100

### Secure HTTPS (Cloudflare Tunnel):
See `DEPLOY_RUNPOD_SECURE.md` for Cloudflare setup.

---

## 🔧 Post-Deployment Setup

### 1. Create First User
```bash
# From RunPod
curl -X POST http://localhost:8100/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@galion.studio",
    "password": "your-secure-password"
  }'
```

### 2. Verify Brands
```bash
# Check that 4 brands exist
docker-compose exec -T postgres psql -U nexuslang nexuslang_v2 \
  -c "SELECT id, name, slug FROM brands;"

# Should show:
# - Galion Studio
# - Galion App
# - Slavic Nomad
# - Marilyn Element
```

### 3. Connect Social Accounts
Navigate to: http://your-runpod-ip:3100/content-manager/settings

For each platform:
1. Create developer app on platform
2. Get OAuth credentials
3. Connect via UI

---

## 🛠️ Admin Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Update Code
```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
docker-compose exec -T postgres pg_dump -U nexuslang nexuslang_v2 | \
  gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

---

## 🔐 Security Checklist

After deployment, secure your system:

- [ ] Change default passwords
- [ ] Setup firewall (UFW)
- [ ] Configure SSH keys only
- [ ] Setup Cloudflare Tunnel
- [ ] Enable HTTPS
- [ ] Backup database
- [ ] Monitor logs

See `DEPLOY_RUNPOD_SECURE.md` for detailed security setup.

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Error
```bash
# Check database is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### API Returns 500 Error
```bash
# Check backend logs
docker-compose logs backend

# Check environment
docker-compose exec backend env | grep DATABASE_URL
```

### Can't Access from Browser
```bash
# Check firewall
ufw status

# Allow ports
ufw allow 8100/tcp
ufw allow 3100/tcp
```

---

## 📞 Get Help

- **Documentation**: See `v2/START_HERE_CONTENT_MANAGER.md`
- **Admin Guide**: See `v2/README_ADMIN.md`
- **Full Deploy**: See `v2/DEPLOY_RUNPOD_SECURE.md`

---

## ✅ Deployment Checklist

After running the deploy script:

- [ ] Services are running (`docker-compose ps`)
- [ ] API is healthy (`curl http://localhost:8100/health`)
- [ ] Database has 4 brands
- [ ] Frontend is accessible
- [ ] Created first admin user
- [ ] Reviewed security settings

---

## 🎉 You're Live!

Your content management system is now running!

**Next Steps:**
1. Connect social media accounts
2. Create your first post
3. Schedule content
4. Monitor analytics

**Manage from local machine:**
```powershell
# Use admin control script
.\admin-control.ps1
```

---

**Deploy Time**: ~10 minutes  
**Status**: Production Ready  
**Support**: See documentation in `v2/` directory

