# ✅ NexusLang v2 - Production Deployment Guide

**Target**: developer.galion.app  
**Platform**: RunPod  
**Time to Deploy**: 30 minutes  
**Status**: All scripts ready, execute in order

---

## 🚀 Complete Deployment Sequence

### Prerequisites Checklist

```
✅ RunPod pod with code deployed (at /workspace/project-nexus)
✅ OpenAI API key (get from: https://platform.openai.com/api-keys)
✅ Cloudflare access to galion.app domain
✅ SSH access to RunPod pod
```

---

## 🔥 Rapid Deployment (Execute This)

### On Your Local Machine

**Step 1: Generate Environment (30 seconds)**
```bash
# From project root
chmod +x setup-production-env.sh
./setup-production-env.sh
```

When prompted, enter your OpenAI key (provided above).

This creates:
- `v2/.env` with secure secrets
- `v2/frontend/.env.local` with production URLs

**Step 2: Push to RunPod (if needed)**
```bash
# If you have your custom upload process, use that
# Otherwise, commit and push to GitHub, then pull on RunPod

git add v2/.env v2/frontend/.env.local
git commit -m "Add production environment configuration"
# Push to your private repo
```

### On RunPod Pod (SSH)

**Step 3: Navigate to Project**
```bash
# SSH into RunPod
# cd to your project directory
cd /workspace/project-nexus

# Pull latest changes (if using git)
git pull
```

**Step 4: Deploy Services (2 minutes)**
```bash
# Make deployment script executable
chmod +x deploy-to-runpod-production.sh

# Run deployment (does everything automatically)
./deploy-to-runpod-production.sh
```

This script will:
1. ✅ Validate environment configuration
2. ✅ Install Docker/Docker Compose if needed
3. ✅ Build all images
4. ✅ Start all services
5. ✅ Initialize database
6. ✅ Verify health checks
7. ✅ Report status

**Step 5: Verify Services (30 seconds)**
```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Test backend
curl http://localhost:8000/health

# Test frontend (may take 30s to start)
curl http://localhost:3000

# View logs if any issues
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 🌐 DNS & SSL Configuration

### Step 6: Configure DNS (5 minutes)

**In Cloudflare Dashboard:**

1. Go to: https://dash.cloudflare.com/
2. Select: **galion.app** domain
3. Navigate: **DNS** → **Records**
4. Add these records:

```
Type: A
Name: developer.galion.app
Content: YOUR_RUNPOD_POD_IP
Proxy: ON (🟠 Orange cloud)
TTL: Auto

Type: A  
Name: api.developer
Content: YOUR_RUNPOD_POD_IP
Proxy: ON (🟠 Orange cloud)
TTL: Auto
```

**Find your RunPod IP:**
```bash
# On RunPod pod:
curl ifconfig.me
# Or check RunPod dashboard → Pod → Connection Info
```

### Step 7: SSL Configuration (10 minutes)

**Option A: Cloudflare Tunnel (Recommended - Easiest)**

```bash
# On RunPod pod
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Login
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create nexuslang-production

# Configure tunnel
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Add this configuration:
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: developer.galion.app
    service: http://localhost:3000
  - hostname: api.developer.galion.app
    service: http://localhost:8000
  - service: http_status:404
```

```bash
# Test tunnel
cloudflared tunnel run nexuslang-production

# If works, install as service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**Option B: Nginx with Cloudflare Certificates**

See: `RUNPOD_SSL_SETUP_GUIDE.md` for detailed instructions.

### Step 8: Update Cloudflare SSL Settings

1. Go to: **SSL/TLS** → **Overview**
2. Set encryption mode: **Full (strict)**
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**
5. Set **Minimum TLS Version**: TLS 1.2

---

## ✅ Verification Checklist

### Services Running
```bash
# All containers should show "Up"
docker-compose -f docker-compose.prod.yml ps

Expected output:
  nexus-backend     Up (healthy)
  nexus-frontend    Up (healthy)
  nexus-postgres    Up (healthy)
  nexus-redis       Up (healthy)
```

### Health Checks
```bash
# Backend
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# Frontend  
curl http://localhost:3000
# Expected: HTML response

# Database
docker-compose -f docker-compose.prod.yml exec postgres pg_isready
# Expected: accepting connections
```

### External Access (after DNS propagation)
```bash
# From your local machine (not RunPod)
curl -I https://developer.galion.app
# Expected: HTTP/2 200

curl https://api.developer.galion.app/health
# Expected: {"status":"healthy",...}
```

### Security Verification
```bash
# Check security headers
curl -I https://api.developer.galion.app/health | grep X-

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
```

### Feature Testing

Open in browser: https://developer.galion.app

Test these features:
- [ ] Landing page loads (no errors)
- [ ] Register new account
- [ ] Login with account
- [ ] Open IDE (/ide)
- [ ] Write and execute code
- [ ] Open AI Chat widget (bottom-right)
- [ ] Send message to AI chat
- [ ] Open Grokopedia (/grokopedia)
- [ ] Search for something
- [ ] Check billing page (/billing)
- [ ] Open content manager (/content-manager)

All working? ✅ **DEPLOYMENT SUCCESSFUL!**

---

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Resource Usage
```bash
# CPU and memory
docker stats

# Disk usage
df -h

# Network
netstat -tlnp | grep -E '3000|8000'
```

### Database Status
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U nexus -d nexus_v2

# Check tables
\dt

# Check user count
SELECT COUNT(*) FROM users;
```

---

## 🔧 Common Issues & Fixes

### Issue: Port 8000 already in use
```bash
# Find what's using it
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Issue: Database won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs postgres

# Reset if needed (WARNING: deletes data)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### Issue: Frontend shows API errors
```bash
# Check CORS settings in v2/.env
# Ensure CORS_ORIGINS includes your frontend domain

# Restart backend to apply changes
docker-compose -f docker-compose.prod.yml restart backend
```

### Issue: SSL certificate errors
```bash
# Verify Cloudflare SSL mode is "Full (strict)"
# Check tunnel is running: sudo systemctl status cloudflared
# Check DNS propagation: nslookup developer.galion.app
```

---

## 🔄 Updating Deployment

### Deploy Code Changes
```bash
# Pull latest code
git pull

# Rebuild and restart
cd v2
docker-compose -f ../docker-compose.prod.yml up -d --build

# Zero-downtime update (if using multiple instances)
docker-compose -f ../docker-compose.prod.yml up -d --no-deps --build backend
```

### Update Environment Variables
```bash
# Edit .env
nano v2/.env

# Restart affected services
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

### Database Migrations
```bash
# Run new migration
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U nexus -d nexus_v2 < v2/database/migrations/new_migration.sql
```

---

## 📈 Performance Optimization

### After Initial Deployment

1. **Enable Redis Caching**
   - Already configured in docker-compose.prod.yml
   - Verify: `docker-compose ps redis`

2. **Configure Connection Pooling**
   - Already in config (pool_size=20)
   - Monitor connections: Check Grafana

3. **Enable Cloudflare Caching**
   - In Cloudflare: Create page rule
   - Cache static assets aggressively
   - Bypass cache for API

4. **Optimize Images**
   - Use Cloudflare Image Optimization
   - Enable WebP/AVIF formats
   - Set appropriate cache headers

---

## 🎯 Production Checklist

### Pre-Launch
- [x] Security vulnerabilities fixed
- [x] Environment configured with secure secrets
- [x] SSL/TLS setup documented
- [x] Deployment scripts created
- [x] All features tested locally
- [ ] DNS configured
- [ ] SSL certificates installed
- [ ] Services deployed to RunPod
- [ ] All health checks passing

### Launch
- [ ] Verify all URLs working
- [ ] Test user registration/login
- [ ] Test all features end-to-end
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Set up alerts

### Post-Launch (First Hour)
- [ ] Monitor server resources
- [ ] Watch error rates
- [ ] Respond to user issues
- [ ] Fix critical bugs immediately
- [ ] Celebrate! 🎉

---

## 🆘 Emergency Procedures

### Service Down
```bash
# Quick restart
docker-compose -f docker-compose.prod.yml restart

# If that doesn't work, full restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Database Corruption
```bash
# Restore from backup (assuming backups are configured)
# 1. Stop services
docker-compose -f docker-compose.prod.yml stop

# 2. Restore database
# (restoration commands depend on your backup solution)

# 3. Restart
docker-compose -f docker-compose.prod.yml start
```

### Memory Issues
```bash
# Check memory
free -h

# Restart services one by one
docker-compose -f docker-compose.prod.yml restart postgres
docker-compose -f docker-compose.prod.yml restart redis
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

---

## 📞 Support Contacts

### Technical Issues
- Check logs first: `docker-compose logs -f`
- Review: `TROUBLESHOOTING.md`
- GitHub Issues: (create repo issues)

### RunPod Support
- Dashboard: https://runpod.io
- Discord: https://discord.gg/runpod
- Email: support@runpod.io

### Cloudflare Support
- Dashboard: https://dash.cloudflare.com/
- Community: https://community.cloudflare.com/
- Docs: https://developers.cloudflare.com/

---

## 🎉 Success Indicators

You'll know deployment succeeded when:

1. ✅ All Docker containers show "healthy"
2. ✅ https://developer.galion.app loads with no SSL error
3. ✅ https://api.developer.galion.app/health returns JSON
4. ✅ Can register and login
5. ✅ Can execute code in IDE
6. ✅ AI chat widget responds
7. ✅ No errors in console
8. ✅ All features functional

---

## 🚀 Post-Deployment Actions

### Immediate (First Hour)
1. Create admin account
2. Test all features personally
3. Monitor logs continuously
4. Set up status page
5. Prepare support channels

### First Day
1. Announce launch (Twitter, ProductHunt)
2. Monitor user signups
3. Respond to all feedback
4. Fix any critical issues
5. Document lessons learned

### First Week
1. Gather user feedback systematically
2. Prioritize and fix bugs
3. Optimize performance bottlenecks
4. Add requested features
5. Celebrate milestones

---

## 💡 Pro Tips

1. **Test Locally First**: Always verify changes work on localhost before deploying
2. **Deploy During Low Traffic**: Early morning or late night
3. **Have Rollback Plan**: Keep previous version ready
4. **Monitor Everything**: Set up alerts for errors
5. **Communicate**: Let users know about updates

---

## 📊 Deployment Timeline

```
T-0:00  Start deployment script
T+2:00  Images building
T+5:00  Services starting
T+8:00  Health checks passing
T+10:00 DNS configured
T+15:00 SSL active
T+20:00 Final verification
T+30:00 ✅ LIVE!
```

---

## 🎯 Next Actions

1. **Run**: `./setup-production-env.sh` (local)
2. **Deploy**: `./deploy-to-runpod-production.sh` (on RunPod)
3. **Configure**: DNS and SSL (Cloudflare)
4. **Verify**: All health checks
5. **Launch**: Announce to the world! 🚀

---

**Status**: Scripts ready, documentation complete  
**Confidence**: High - All systems tested  
**Risk**: Low - Can rollback if needed

🚀 **Ready to deploy! Let's go live!**

