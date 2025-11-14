# 🚀 RunPod SSH Tunnel Setup Guide

## ⚠️ CRITICAL: Where to Run Commands

**DO NOT run SSH commands inside RunPod terminal!**

Run them from your **LOCAL COMPUTER** (Windows/Mac/Linux).

---

## 📋 Step-by-Step Instructions

### Step 1: Open Local Terminal
- **Windows:** Press `Win + R`, type `cmd`, press Enter
- **Mac:** Press `Cmd + Space`, type "Terminal", press Enter
- **Linux:** Open your terminal application

### Step 2: Check Your SSH Key
```bash
# Check if SSH key exists
ls -la ~/.ssh/id_ed25519*

# If not found, find your key
find ~ -name "*ed25519*" 2>/dev/null
```

### Step 3: Create SSH Tunnel
```bash
# Replace with your actual SSH key path if different
ssh -L 8080:localhost:36277 a51059ucg22sxt-644113f2@ssh.runpod.io -i ~/.ssh/id_ed25519 -N
```

### Step 4: Test API Access
With tunnel running, open browser to:
- http://localhost:8080
- http://localhost:8080/health
- http://localhost:8080/docs

---

## 🔧 Troubleshooting

### If "Permission denied (publickey)"
```bash
# Try with different key path
ssh -L 8080:localhost:36277 a51059ucg22sxt-644113f2@ssh.runpod.io -i /path/to/your/key -N

# Or use password (temporary)
ssh -L 8080:localhost:36277 a51059ucg22sxt-644113f2@ssh.runpod.io
```

### If "Connection refused"
- Check your internet connection
- Verify pod is running in RunPod dashboard

### If tunnel starts but API doesn't work
- Check that server is running on RunPod: `ps aux | grep uvicorn`
- Verify port 36277 is correct

---

## ✅ Success Indicators

- [ ] SSH connects without password prompt
- [ ] Command stays running (tunnel active)
- [ ] http://localhost:8080 loads your API
- [ ] http://localhost:8080/health returns JSON

---

## 🎯 Summary

**Local Machine** → SSH Tunnel → **RunPod Server** → **Your API**

**Command to run locally:**
```bash
ssh -L 8080:localhost:36277 a51059ucg22sxt-644113f2@ssh.runpod.io -i ~/.ssh/id_ed25519 -N
```

**Result:** API accessible at http://localhost:8080
