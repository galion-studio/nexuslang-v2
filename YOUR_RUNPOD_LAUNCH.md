# 🚀 YOUR RUNPOD LAUNCH - NexusLang v2

**Your Pod ID:** `a51059ucg22sxt`

---

## 📤 STEP 1: UPLOAD (Choose Easiest Method)

### Method A: GitHub (Recommended)

**On your PC:**
```powershell
git init
git add .
git commit -m "NexusLang v2 AI"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

**On RunPod Jupyter Terminal:**
```bash
cd /workspace
git clone YOUR_GITHUB_URL nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

### Method B: Manual Zip Upload

1. Create zip of your project folder
2. Open Jupyter Lab: https://a51059ucg22sxt.proxy.runpod.net/lab
3. Click Upload button (⬆️)
4. Select your zip file
5. Wait for upload

**Then in Jupyter Terminal:**
```bash
cd /workspace
unzip yourfile.zip -d nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

---

## 🔧 STEP 2: CONFIGURE

```bash
nano .env
```

**Add this line:**
```bash
OPENROUTER_API_KEY=sk-or-your-key-here
```

Get key from: https://openrouter.ai/keys

**Save (Ctrl+O, Enter, Ctrl+X) and restart:**
```bash
docker-compose restart backend
```

---

## 🌐 STEP 3: EXPOSE PORTS

1. Go to: https://www.runpod.io/console/pods
2. Click on pod `a51059ucg22sxt`
3. Click **"Edit"**
4. Under **"TCP Port Mappings"**, add:
   - `8000` → Check "HTTP"
   - `3000` → Check "HTTP"
   - `3001` → Check "HTTP" (optional)
5. Click **"Save"**

---

## ✨ YOUR PLATFORM URLS

### Backend API:
```
https://a51059ucg22sxt-8000.proxy.runpod.net
```

### API Documentation:
```
https://a51059ucg22sxt-8000.proxy.runpod.net/docs
```

### Frontend:
```
https://a51059ucg22sxt-3000.proxy.runpod.net
```

### Grafana Monitoring:
```
https://a51059ucg22sxt-3001.proxy.runpod.net
```

---

## 🧪 TEST YOUR DEPLOYMENT

### 1. Check Health:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### 2. View Logs:
```bash
docker-compose logs -f backend
```

### 3. Check Containers:
```bash
docker-compose ps
```

All should show "Up"

---

## 🤖 TEST AI FEATURES

Visit: **https://a51059ucg22sxt-8000.proxy.runpod.net/docs**

**Try these:**

1. **GET** `/api/v2/ai/models`
   - Click "Try it out" → "Execute"
   - See all 30+ AI models available

2. **POST** `/api/v2/ai/quick`
   ```json
   {
     "prompt": "What is the capital of France?"
   }
   ```

3. **POST** `/api/v2/ide/ai/generate`
   ```json
   {
     "description": "Create a hello world function in Python",
     "language": "python"
   }
   ```

---

## 📊 YOUR AI MODELS

**Cheap & Fast:**
- `openai/gpt-3.5-turbo` - $0.50/1M tokens
- `anthropic/claude-3-haiku` - $0.25/1M tokens
- `meta-llama/llama-3-70b-instruct` - $0.90/1M tokens

**Best Quality (Your Defaults):**
- `anthropic/claude-3.5-sonnet` - $3/1M tokens (PRIMARY)
- `openai/gpt-4-turbo` - $10/1M tokens (FALLBACK)

**Specialized:**
- `meta-llama/codellama-70b-instruct` - Code generation
- `perplexity/pplx-70b-online` - Internet access

---

## 🔍 MONITORING

### Jupyter Lab:
```
https://a51059ucg22sxt.proxy.runpod.net/lab
Password: a704ts883wtjmaxrvayf
```

### View Logs:
```bash
cd /workspace/nexuslang-v2
docker-compose logs -f backend
```

### Restart Services:
```bash
docker-compose restart
```

### Stop Services:
```bash
docker-compose down
```

---

## 🆘 TROUBLESHOOTING

### Can't access URLs?
1. Make sure ports are exposed in RunPod Dashboard
2. Wait 1-2 minutes after exposing ports
3. Check services are running: `docker-compose ps`

### AI not working?
```bash
# Check API key is set
cat .env | grep OPENROUTER_API_KEY

# Should show: OPENROUTER_API_KEY=sk-or-...
# If empty, edit and add it:
nano .env

# Then restart:
docker-compose restart backend
```

### Services not starting?
```bash
# Check Docker
docker --version
docker-compose --version

# Rebuild
docker-compose down
docker-compose up -d --build

# Check logs for errors
docker-compose logs backend | tail -50
```

---

## 📋 QUICK COMMANDS

```bash
# Navigate to project
cd /workspace/nexuslang-v2

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop everything
docker-compose down

# Update from GitHub
git pull
docker-compose restart backend
```

---

## ✅ LAUNCH CHECKLIST

- [ ] Files uploaded to `/workspace/nexuslang-v2`
- [ ] Deployment script run successfully
- [ ] OPENROUTER_API_KEY added to `.env`
- [ ] Backend restarted after adding key
- [ ] Ports 8000, 3000, 3001 exposed in RunPod
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Can access: https://a51059ucg22sxt-8000.proxy.runpod.net/docs
- [ ] AI models endpoint works
- [ ] Generated test code successfully

---

## 🎉 YOU'RE LIVE!

Once all steps complete:

✅ **Your URLs:**
- API: https://a51059ucg22sxt-8000.proxy.runpod.net
- Docs: https://a51059ucg22sxt-8000.proxy.runpod.net/docs
- Frontend: https://a51059ucg22sxt-3000.proxy.runpod.net

✅ **AI Features:**
- 30+ models available
- Code generation ready
- IDE AI assistant active
- Search enhancement enabled

✅ **Services:**
- PostgreSQL database
- Redis cache
- Elasticsearch search
- Grafana monitoring

---

## 🚀 START NOW!

1. Choose upload method (GitHub recommended)
2. Run deployment script
3. Add OpenRouter API key
4. Expose ports
5. Access your platform!

**Total time: ~15 minutes** ⏱️

**Your AI-powered platform is ready! 🎉**

