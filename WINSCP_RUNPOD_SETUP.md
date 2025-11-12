# 📁 Connect to RunPod via WinSCP

## 🔧 WinSCP Connection Setup

### Step 1: Get RunPod SSH Details

1. Go to RunPod Dashboard: https://www.runpod.io/console/pods
2. Click your pod: **a51059ucg22sxt**
3. Click **"Connect"** → **"TCP Port Mappings"**
4. Find SSH port (usually 22)
5. Your SSH connection string should be shown

### Step 2: Configure WinSCP

**File Protocol:** `SFTP`  
**Host name:** `a51059ucg22sxt.proxy.runpod.net` (or SSH proxy URL from RunPod)  
**Port number:** `22` (or SSH port from RunPod)  
**User name:** `root`  
**Password:** Leave blank if using SSH key

**SSH Key (if needed):**
- If RunPod shows SSH key, save it to file
- In WinSCP: Advanced → SSH → Authentication
- Select your private key file

### Step 3: Connect

Click **"Login"**

### Step 4: Navigate

Go to: `/workspace/nexuslang-v2`

---

## 📤 Upload Files via WinSCP

### What to Upload:

1. **Drag & drop** from your PC to `/workspace/nexuslang-v2`
2. Or upload new files as needed

### Important Folders:
- `/workspace/nexuslang-v2/v2/backend` - Backend code
- `/workspace/nexuslang-v2/.env` - Configuration

---

## 🚀 FRESH RUNPOD CONSOLE - COMPLETE STEPS

### Copy these commands one by one:

```bash
# Step 1: Navigate to project
cd /workspace/nexuslang-v2

# Step 2: Pull latest from GitHub (if needed)
git pull

# Step 3: Go to backend
cd v2/backend

# Step 4: Install dependencies (takes 5-10 min)
pip install -r requirements.txt

# Step 5: Set environment
export $(cat ../../.env | grep -v '^#' | xargs)

# Step 6: Start backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Step 7: Wait for startup
sleep 5

# Step 8: Test health
curl http://localhost:8000/health

# Step 9: View logs
tail -f /tmp/*.log
```

---

## ✅ SUCCESS CHECKLIST

After running above commands:

- [ ] `pip install` completed without errors
- [ ] Backend started (you see uvicorn output)
- [ ] Health check returns: `{"status":"healthy"}`
- [ ] Port 8000 exposed in RunPod Dashboard
- [ ] Can access: https://a51059ucg22sxt-8000.proxy.runpod.net/docs

---

## 🌐 EXPOSE PORTS (Required!)

1. Go to RunPod Dashboard
2. Your pod → **Edit**
3. **TCP Port Mappings:**
   - Add: `8000` → Check "HTTP"
   - Add: `3000` → Check "HTTP" (for frontend later)
4. **Save**
5. Wait 1-2 minutes

---

## 🧪 TEST YOUR DEPLOYMENT

### 1. Check Backend Running:
```bash
ps aux | grep uvicorn
```

Should show process running

### 2. Test Locally:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}`

### 3. Test Externally:
Visit: **https://a51059ucg22sxt-8000.proxy.runpod.net/docs**

Should show API documentation

### 4. Test AI Endpoint:
In API docs, try:
- **GET** `/api/v2/ai/models`
- Should list all 30+ available models

---

## 🆘 TROUBLESHOOTING

### Pip install fails:
```bash
# Install build tools first
apt-get update
apt-get install -y build-essential python3-dev

# Try again
pip install -r requirements.txt
```

### Backend won't start:
```bash
# Check for errors
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Check what's wrong in the output
```

### Can't access URL:
1. Make sure port 8000 is exposed in RunPod
2. Wait 1-2 minutes after exposing
3. Try direct IP: http://localhost:8000/docs from RunPod

### Port already in use:
```bash
# Kill existing process
pkill -f uvicorn

# Start again
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

## 📋 QUICK REFERENCE

### Restart Backend:
```bash
pkill -f uvicorn
cd /workspace/nexuslang-v2/v2/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Update from GitHub:
```bash
cd /workspace/nexuslang-v2
git pull
pkill -f uvicorn
cd v2/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### View Logs:
```bash
# Backend logs
ps aux | grep uvicorn

# Or if logging to file
tail -f logs/*.log
```

---

## 🎯 YOUR URLS

**Once port 8000 is exposed:**
- API: https://a51059ucg22sxt-8000.proxy.runpod.net
- Docs: https://a51059ucg22sxt-8000.proxy.runpod.net/docs
- Health: https://a51059ucg22sxt-8000.proxy.runpod.net/health

---

**Ready to deploy! Wait for pip install to finish, then run the commands!** 🚀

