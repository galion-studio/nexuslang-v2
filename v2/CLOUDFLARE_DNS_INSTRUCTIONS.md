# 🌐 Cloudflare DNS Setup - Quick Instructions

**Add NexusLang v2 subdomains to galion.app**

---

## Step 1: Get RunPod URLs (1 minute)

**In RunPod Dashboard:**

1. Click on your pod
2. Scroll to "TCP Port Mappings"
3. Find your URLs for ports 3100 and 8100

**Example:**
```
Port 3100: https://w2hijk3qponmlk-3100.proxy.runpod.net
Port 8100: https://w2hijk3qponmlk-8100.proxy.runpod.net
```

**Copy these!** ✍️

---

## Step 2: Add DNS in Cloudflare (2 minutes)

**Go to:** https://dash.cloudflare.com  
**Select:** galion.app domain  
**Click:** DNS (left sidebar)

### Record 1: Frontend

Click **"Add record"**

Fill in:
```
Type:    CNAME
Name:    nexuslang
Target:  w2hijk3qponmlk-3100.proxy.runpod.net  ← YOUR port 3100 URL
Proxy:   🟠 ON (orange cloud)
TTL:     Auto
```

Click **"Save"**

### Record 2: Backend API

Click **"Add record"** again

Fill in:
```
Type:    CNAME
Name:    api.nexuslang
Target:  w2hijk3qponmlk-8100.proxy.runpod.net  ← YOUR port 8100 URL
Proxy:   🟠 ON (orange cloud)
TTL:     Auto
```

Click **"Save"**

---

## Step 3: Wait & Test (3 minutes)

**Wait:** 1-5 minutes for DNS propagation

**Test in browser:**
```
https://nexuslang.galion.app
```

**Should see:** NexusLang v2 landing page! 🎉

**Test API:**
```
https://api.nexuslang.galion.app/health
```

**Should see:** `{"status":"healthy",...}`

---

## ✅ Done!

Your users can now access:
- **IDE:** https://nexuslang.galion.app/ide
- **API:** https://api.nexuslang.galion.app
- **Docs:** https://api.nexuslang.galion.app/docs

Meanwhile, Galion still works on:
- **galion.app** (port 3000)
- **api.galion.app** (port 8000)

**Perfect coexistence!** 🎊

---

## 📋 Final Checklist

- [ ] Got RunPod URLs for ports 3100 & 8100
- [ ] Added CNAME for nexuslang → port 3100 URL
- [ ] Added CNAME for api.nexuslang → port 8100 URL
- [ ] Enabled proxy (orange cloud) on both
- [ ] Waited for DNS propagation
- [ ] Tested https://nexuslang.galion.app
- [ ] Tested https://api.nexuslang.galion.app/health
- [ ] Both work! ✅

---

**🎉 Ready to share with users!**

Send them: `https://nexuslang.galion.app/ide`

