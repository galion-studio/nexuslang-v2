# 🚀 V2 Deployment System

**Stable, HTTP-based deployment (no SSH needed!)**

---

## ✅ Why V2 is Better

- ❌ **V1:** SSH (complex, breaks in Docker)
- ✅ **V2:** HTTP webhooks (simple, always works)

---

## 📦 Setup (One Time)

### **On RunPod:**

1. **Upload the webhook script:**
   ```bash
   cd /nexuslang-v2
   mkdir -p v2-deployment
   # Copy deploy-webhook.py to this directory
   ```

2. **Install dependencies:**
   ```bash
   pip3 install flask
   ```

3. **Start the webhook:**
   ```bash
   cd /nexuslang-v2/v2-deployment
   chmod +x start-webhook.sh
   ./start-webhook.sh
   ```

4. **Expose port 7000** in RunPod dashboard:
   - Go to your pod settings
   - Add TCP port: 7000
   - Save

---

## 🚀 Daily Use

### **From Your Laptop:**

```powershell
# Deploy (pull code + restart services)
.\deploy-from-laptop.ps1 -Action deploy

# Check status
.\deploy-from-laptop.ps1 -Action status

# View logs
.\deploy-from-laptop.ps1 -Action logs

# Health check
.\deploy-from-laptop.ps1 -Action health
```

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `deploy` | Pull latest code and restart all services |
| `status` | Show PM2 service status |
| `logs` | View recent logs |
| `health` | Check if webhook is running |

---

## 🔧 Configuration

Edit `deploy-from-laptop.ps1` to change:
- `$RunPodIP` - Your RunPod IP address
- `$Port` - Webhook port (default: 7000)

---

## ✅ Advantages

1. **Simple** - Just HTTP requests
2. **Stable** - No SSH configuration issues
3. **Fast** - Direct connection
4. **Reliable** - Works in any environment
5. **Secure** - Only exposed through RunPod ports

---

## 🆘 Troubleshooting

### Webhook not responding?

**On RunPod:**
```bash
pm2 logs deploy-webhook
```

### Port not accessible?

1. Check RunPod dashboard → Your pod → TCP Port Mappings
2. Make sure port 7000 is exposed
3. Use the external port number shown

### Services not starting?

Check logs:
```bash
pm2 logs galion-backend
```

---

**Much simpler than SSH! 🎉**

