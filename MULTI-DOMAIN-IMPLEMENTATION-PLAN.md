# 🚀 Multi-Domain Implementation Plan

**Complete setup for galion.studio and galion.app with RunPod + Cloudflare**

---

## 🎯 **Overview**

**Domains & Services:**
- **galion.studio** (main corporate domain)
- **galion.app** (app-focused domain)
- **RunPod IP:** `213.173.105.83`
- **Services:** Backend (8000), Studio (3030), App (3000), Dev (3003)

**Target URLs:**
- `https://api.galion.studio` → Backend API
- `https://studio.galion.studio` → Corporate Website
- `https://app.galion.studio` → Voice-First App
- `https://dev.galion.studio` → Developer Platform
- `https://galion.app` → Main Voice App
- `https://api.galion.app` → Backend API (alternative)
- `https://studio.galion.app` → Corporate Website (alternative)
- `https://dev.galion.app` → Developer Platform (alternative)

---

## 📋 **Implementation Steps**

### **Phase 1: RunPod Configuration**

#### **Step 1.1: Update Nginx Configuration**
```bash
# SSH into RunPod
ssh root@213.173.105.83

# Download and apply multi-domain nginx config
wget https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/nginx-both-domains.conf
sudo cp nginx-both-domains.conf /etc/nginx/sites-available/galion-platform
sudo ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **Step 1.2: Verify Services are Running**
```bash
# Check PM2 status
pm2 status

# Should show:
# backend          online
# galion-studio    online
# galion-app       online
# developer-platform online
```

#### **Step 1.3: Test Local Access**
```bash
# Test all services locally
curl http://localhost:8000/health
curl http://localhost:3030
curl http://localhost:3000
curl http://localhost:3003
```

---

### **Phase 2: Cloudflare DNS Configuration**

#### **Step 2.1: Add galion.studio to Cloudflare**
1. Go to https://dash.cloudflare.com
2. Click "Add Site"
3. Enter: `galion.studio`
4. Follow Cloudflare setup wizard
5. Update nameservers at your domain registrar

#### **Step 2.2: Configure DNS Records for galion.studio**
Navigate to: **DNS → Records**

Add these records:

```
# Main Domain (A Record)
Type: A
Name: @
IPv4 address: 213.173.105.83
Proxy status: Proxied

# WWW Subdomain
Type: CNAME
Name: www
Target: galion.studio
Proxy status: Proxied

# API Subdomain
Type: CNAME
Name: api
Target: galion.studio
Proxy status: Proxied

# Studio Subdomain
Type: CNAME
Name: studio
Target: galion.studio
Proxy status: Proxied

# App Subdomain
Type: CNAME
Name: app
Target: galion.studio
Proxy status: Proxied

# Dev Subdomain
Type: CNAME
Name: dev
Target: galion.studio
Proxy status: Proxied
```

#### **Step 2.3: Add galion.app to Cloudflare**
1. Click "Add Site" again
2. Enter: `galion.app`
3. Follow Cloudflare setup wizard
4. Update nameservers at your domain registrar

#### **Step 2.4: Configure DNS Records for galion.app**
Navigate to: **DNS → Records**

Add these records:

```
# Main Domain (A Record) - points to main app
Type: A
Name: @
IPv4 address: 213.173.105.83
Proxy status: Proxied

# WWW Subdomain
Type: CNAME
Name: www
Target: galion.app
Proxy status: Proxied

# API Subdomain
Type: CNAME
Name: api
Target: galion.app
Proxy status: Proxied

# Studio Subdomain
Type: CNAME
Name: studio
Target: galion.app
Proxy status: Proxied

# Dev Subdomain
Type: CNAME
Name: dev
Target: galion.app
Proxy status: Proxied
```

---

### **Phase 3: SSL/TLS Configuration**

#### **Step 3.1: Enable SSL for Both Domains**
For each domain in Cloudflare:

1. Go to **SSL/TLS → Overview**
2. Set **SSL/TLS encryption mode** to: `Full`
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**

#### **Step 3.2: Wait for SSL Certificates**
- SSL certificates are provisioned automatically
- May take 5-24 hours for full propagation
- Check SSL status in Cloudflare dashboard

---

### **Phase 4: Backend CORS Updates**

#### **Step 4.1: Update CORS Configuration**
Update `v2/backend/main_simple.py` to allow all new domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000", "http://localhost:3001",
        "http://localhost:3002", "http://localhost:3003", "http://localhost:3030",

        # Production galion.studio domains
        "https://api.galion.studio", "https://studio.galion.studio",
        "https://app.galion.studio", "https://dev.galion.studio",
        "https://galion.studio", "https://www.galion.studio",

        # Production galion.app domains
        "https://galion.app", "https://www.galion.app",
        "https://api.galion.app", "https://studio.galion.app",
        "https://dev.galion.app",

        # HTTP versions (for development)
        "http://api.galion.studio", "http://studio.galion.studio",
        "http://app.galion.studio", "http://dev.galion.studio",
        "http://galion.studio", "http://www.galion.studio",
        "http://galion.app", "http://www.galion.app",
        "http://api.galion.app", "http://studio.galion.app", "http://dev.galion.app",

        # RunPod direct access
        "http://213.173.105.83:3000", "http://213.173.105.83:3001",
        "http://213.173.105.83:3003", "http://213.173.105.83:3030",

        # Wildcard for development
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

#### **Step 4.2: Deploy Backend Changes**
```bash
# Commit and push changes
git add v2/backend/main_simple.py
git commit -m "Update CORS for multi-domain support"
git push origin clean-nexuslang

# Deploy to RunPod
wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/runpod-deploy-simple.sh | bash
```

---

### **Phase 5: Testing & Verification**

#### **Step 5.1: DNS Verification**
```bash
# Test DNS resolution (run on RunPod)
wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/quick-dns-check-runpod.sh | bash
```

#### **Step 5.2: External Access Testing**
```bash
# Test all galion.studio domains
curl -I https://api.galion.studio/health
curl -I https://studio.galion.studio
curl -I https://app.galion.studio
curl -I https://dev.galion.studio

# Test all galion.app domains
curl -I https://galion.app
curl -I https://api.galion.app/health
curl -I https://studio.galion.app
curl -I https://dev.galion.app
```

#### **Step 5.3: SSL Certificate Check**
```bash
# Check SSL certificates
echo | openssl s_client -connect api.galion.studio:443 -servername api.galion.studio 2>/dev/null | openssl x509 -noout -dates
echo | openssl s_client -connect galion.app:443 -servername galion.app 2>/dev/null | openssl x509 -noout -dates
```

#### **Step 5.4: Full System Test**
```bash
# Run comprehensive test
wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/test-external-access.sh | bash
```

---

### **Phase 6: Final Configuration**

#### **Step 6.1: Update Documentation**
Update README.md with new domain information:

```markdown
## ✨ Live Demo

**galion.studio domains:**
- [Backend API](https://api.galion.studio) - FastAPI documentation
- [Galion Studio](https://studio.galion.studio) - Corporate website
- [Galion App](https://app.galion.studio) - Voice-first interface
- [Developer Platform](https://dev.galion.studio) - Full IDE

**galion.app domains:**
- [Main App](https://galion.app) - Primary voice application
- [API Access](https://api.galion.app) - Alternative API access
- [Studio](https://studio.galion.app) - Corporate website
- [Developer](https://dev.galion.app) - IDE platform
```

#### **Step 6.2: Configure Monitoring**
Set up uptime monitoring for all domains:
- https://api.galion.studio/health
- https://galion.app
- https://studio.galion.studio

#### **Step 6.3: Update Deployment Scripts**
Ensure all deployment scripts work with multi-domain setup.

---

## 🔧 **Quick Implementation Commands**

### **RunPod Setup (One Command):**
```bash
ssh root@213.173.105.83 'wget https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/nginx-both-domains.conf && sudo cp nginx-both-domains.conf /etc/nginx/sites-available/galion-platform && sudo ln -sf /etc/nginx/sites-available/galion-platform /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx'
```

### **DNS Verification:**
```bash
# Test all domains resolve to Cloudflare
for domain in galion.studio api.galion.studio studio.galion.studio app.galion.studio dev.galion.studio galion.app api.galion.app studio.galion.app dev.galion.app; do echo -n "$domain: "; nslookup $domain 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}'; done
```

### **Full System Test:**
```bash
# Test all endpoints
for url in https://api.galion.studio/health https://studio.galion.studio https://app.galion.studio https://dev.galion.studio https://galion.app https://api.galion.app/health https://studio.galion.app https://dev.galion.app; do echo "Testing $url"; curl -I $url 2>/dev/null | head -1; done
```

---

## 📊 **Expected Results**

### **DNS Resolution (Should show Cloudflare IPs):**
```
galion.studio: 188.114.96.3
api.galion.studio: 188.114.97.3
studio.galion.studio: 188.114.96.3
app.galion.studio: 188.114.97.3
dev.galion.studio: 188.114.96.3
galion.app: 188.114.96.3
api.galion.app: 188.114.97.3
studio.galion.app: 188.114.96.3
dev.galion.app: 188.114.97.3
```

### **HTTP Responses (Should be 200):**
```
Testing https://api.galion.studio/health
HTTP/2 200
Testing https://studio.galion.studio
HTTP/2 200
Testing https://galion.app
HTTP/2 200
```

---

## 🆘 **Troubleshooting**

### **DNS Issues:**
- Wait 2-10 minutes for propagation
- Check Cloudflare proxy status (orange cloud)
- Verify domain nameservers updated

### **502 Errors:**
- Check nginx configuration: `sudo nginx -t`
- Verify services running: `pm2 status`
- Restart nginx: `sudo systemctl restart nginx`

### **SSL Issues:**
- Wait up to 24 hours for certificates
- Check SSL mode is set to "Full"
- Verify "Always Use HTTPS" is enabled

---

## ✅ **Final Checklist**

- [ ] RunPod nginx configured for both domains
- [ ] galion.studio added to Cloudflare with DNS records
- [ ] galion.app added to Cloudflare with DNS records
- [ ] SSL/TLS configured for both domains
- [ ] Backend CORS updated for new domains
- [ ] All services tested and working
- [ ] Documentation updated with new URLs
- [ ] Monitoring configured

---

## 🎉 **Success Criteria**

**All domains accessible with HTTP 200 responses:**
- ✅ https://api.galion.studio/health
- ✅ https://studio.galion.studio
- ✅ https://app.galion.studio
- ✅ https://dev.galion.studio
- ✅ https://galion.app
- ✅ https://api.galion.app/health
- ✅ https://studio.galion.app
- ✅ https://dev.galion.app

**All domains resolve to Cloudflare IPs (not direct RunPod IP)**

---

**Ready to implement? Start with Phase 1: RunPod Configuration!** 🚀

*(Estimated completion time: 30-60 minutes)*
