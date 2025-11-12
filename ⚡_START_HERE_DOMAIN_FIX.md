# ⚡ START HERE: Quick Domain Fix

**Problem:** SSL errors, missing config files, domain issues  
**Solution:** Run one script, answer a few questions, done!  
**Time:** 5 minutes

---

## 🚀 Quick Fix (Choose Your OS)

### Linux / Mac:
```bash
chmod +x fix-all-domain-errors.sh
./fix-all-domain-errors.sh
```

### Windows:
```powershell
.\fix-all-domain-errors.ps1
```

---

## 💬 What the Script Does

1. Asks where you're deploying (local, developer.galion.app, RunPod, etc.)
2. Creates `.env` files with correct URLs
3. Generates secure passwords
4. Updates Docker configurations
5. Shows you next steps

**That's it!** ✅

---

## 📝 Choose Your Deployment

When the script asks, pick:

| Option | Choose If... |
|--------|-------------|
| **1. Local development** | Testing on your computer |
| **2. developer.galion.app** | Production with this domain |
| **3. nexuslang.galion.app** | Production with this domain |
| **4. RunPod + custom domain** | RunPod with your own domain |
| **5. RunPod direct** | Quick RunPod test (no domain needed) |

---

## 🔥 After Running the Script

### For Local Development:
```bash
cd v2
docker-compose up -d
```
Visit: `http://localhost:3000`

### For Production:
1. Set up SSL certificates:
   ```bash
   ./install-cloudflare-certs.sh
   ```
   (See `QUICK_FIX_SSL_ERROR.md` for details)

2. Configure DNS in Cloudflare

3. Deploy:
   ```bash
   cd v2
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## 📚 More Help?

| Guide | When to Read |
|-------|-------------|
| `QUICK_FIX_SSL_ERROR.md` | SSL certificate errors |
| `SSL_ERROR_EXPLAINED.md` | Want to understand SSL |
| `DOMAIN_ERRORS_FIXED.md` | Complete documentation |
| `v2/env.template` | See all config options |

---

## ✅ Done!

After running the script:
- ✅ Environment files created
- ✅ Secure passwords generated
- ✅ URLs configured
- ✅ Ready to start services

**Total time:** ~5 minutes

🚀 **Let's go!**

