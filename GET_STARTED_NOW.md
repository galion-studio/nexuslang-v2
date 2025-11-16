# 🚀 GET STARTED NOW - Ultimate Voice API

**Let's get your Ultimate Voice API running in the next 15 minutes!**

---

## ⚡ STEP 1: Set Up API Keys (2 minutes)

### Create your .env file:

```bash
cd v2/backend
cp .env.example .env
```

### Add your API keys to `.env`:

```bash
# Open .env in your editor and add:
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
ELEVENLABS_API_KEY=sk_YOUR-KEY-HERE
```

**✅ Your keys are safe - `.env` is in `.gitignore` and will NEVER be committed!**

---

## ⚡ STEP 2: Start Redis (1 minute)

Redis handles sessions and caching.

### Option A: Docker (Recommended)
```bash
docker run -d -p 6379:6379 redis
```

### Option B: Windows
Download and run Redis from https://redis.io/download

---

## ⚡ STEP 3: Install Backend (3 minutes)

```bash
cd v2/backend
pip install -r requirements.txt
```

---

## ⚡ STEP 4: Start Backend (1 minute)

```bash
python main.py
```

**✅ Backend running at:** `http://localhost:8000`

Test it:
```bash
curl http://localhost:8000/health
```

---

## ⚡ STEP 5: Install & Start Frontend (5 minutes)

```bash
cd galion-app
npm install
npm run dev
```

**✅ Frontend running at:** `http://localhost:3003`

---

## ✅ YOU'RE DONE!

Open `http://localhost:3003` in your browser and **start talking!**

The voice interface will:
1. Listen to your voice
2. Send it to the backend
3. AI processes your request
4. Responds back with voice

---

## 🎯 Quick Tests

### Test 1: Check Backend Health
```bash
curl http://localhost:8000/health
```

### Test 2: Test Voice WebSocket
```bash
# The frontend will automatically connect when you open it
```

### Test 3: Interactive Demo (Terminal Chat)
```bash
cd v2/backend
python demo_voice_api.py
```

---

## 🔧 Troubleshooting

### Redis Connection Error?
- Make sure Redis is running: `docker ps`
- Check port 6379 is free: `netstat -an | findstr 6379`

### API Key Errors?
- Check `.env` file exists in `v2/backend/`
- Verify keys are correct (no extra spaces)
- Restart backend after editing `.env`

### Port Already in Use?
- Backend (8000): Change `PORT` in `.env`
- Frontend (3003): Change port in `galion-app/package.json`

### ModuleNotFoundError?
- Make sure you're in the right directory
- Reinstall: `pip install -r requirements.txt`

---

## 📚 Next Steps

1. **Read the docs**: Check `v2/backend/QUICK_REFERENCE.md`
2. **Customize AI**: Edit conversation prompts in `conversation_manager.py`
3. **Deploy**: See `QUICK_DEPLOY.md` for deployment guide
4. **Contribute**: See `CONTRIBUTING.md` to help build Galion

---

## 🆘 Need Help?

- **Documentation**: See all `.md` files in `v2/backend/`
- **Issues**: Check GitHub issues
- **Questions**: Ask in the community chat

---

**Built with ❤️ for the 22nd century**

*The first No-UI voice platform*

