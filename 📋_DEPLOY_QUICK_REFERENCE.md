# 📋 NexusLang v2 - Deploy Quick Reference

**Ultra-quick reference for server deployment**

---

## 🎯 ON YOUR SERVER (3 Commands = LIVE)

```bash
# Command 1: Clone from GitHub
cd /var/www && git clone https://github.com/galion-studio/galion-platform.git nexuslang-v2 && cd nexuslang-v2

# Command 2: Deploy everything
chmod +x quick-deploy-server.sh && ./quick-deploy-server.sh

# Command 3: Get SSL
certbot --nginx -d developer.galion.app -d api.developer.galion.app
```

**Configure DNS in Cloudflare** (see below)

**YOU'RE LIVE!** ✅

---

## 🌐 CLOUDFLARE DNS SETUP

**Dashboard:** https://dash.cloudflare.com  
**Domain:** galion.app

**Add these DNS records:**

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | developer | YOUR_SERVER_IP | ✅ On |
| A | api.developer | YOUR_SERVER_IP | ✅ On |

**Save and wait 1-5 minutes for propagation.**

---

## ✅ URLS AFTER DEPLOYMENT

**Main Platform:**  
https://developer.galion.app

**API Documentation:**  
https://api.developer.galion.app/docs

**Monitoring:**  
http://YOUR_SERVER_IP:9090 (Prometheus)  
http://YOUR_SERVER_IP:3001 (Grafana)

---

## 🔧 USEFUL COMMANDS ON SERVER

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all
docker-compose down

# Update from GitHub
git pull && docker-compose up -d --build

# Check database
docker-compose exec postgres psql -U nexus -d nexus_v2
```

---

## 🆘 QUICK TROUBLESHOOTING

**Services won't start:**
```bash
docker-compose logs
systemctl restart docker
```

**Domain won't load:**
```bash
# Check DNS
nslookup developer.galion.app
# Wait for DNS propagation (up to 24h)
```

**SSL fails:**
```bash
# Check Nginx
nginx -t
systemctl status nginx
# Try again
certbot renew --force-renewal
```

---

## 📊 WHAT'S INCLUDED

- ✅ NexusLang v2 language with binary compiler
- ✅ Web IDE with Monaco editor
- ✅ Grokopedia knowledge base
- ✅ Voice system (STT/TTS)
- ✅ Shopify billing
- ✅ Community platform
- ✅ Beautiful responsive UI
- ✅ Production infrastructure
- ✅ Monitoring & auto-scaling
- ✅ Complete documentation

**All 11 plan todos complete!** ✅

---

## 🎉 YOU'RE READY!

**Repository:** https://github.com/galion-studio/galion-platform.git  
**Deployment:** 3 commands  
**Time:** 10-15 minutes  
**Result:** Live platform! 🚀

**See 🚀_GO_LIVE_NOW.md for detailed guide**

---

📋 **QUICK REFERENCE - KEEP THIS HANDY!** 📋

