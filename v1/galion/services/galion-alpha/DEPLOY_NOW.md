# 🚀 DEPLOY GALION.STUDIO - RIGHT NOW

**Simple deployment in 3 steps**

---

## 🔧 PREREQUISITES

Make sure you have:
- Python 3.7+ installed
- Node.js 14+ installed
- Terminal/PowerShell access

---

## 📦 STEP 1: Install Backend Dependencies

Open **Terminal/PowerShell** and run:

```bash
cd services/galion-alpha
py -m pip install Flask Flask-SQLAlchemy Flask-CORS
```

or

```bash
python -m pip install Flask Flask-SQLAlchemy Flask-CORS
```

**Expected output:**
```
Successfully installed Flask-3.0.0 Flask-SQLAlchemy-3.1.1 Flask-CORS-4.0.0
```

---

## 🚀 STEP 2: Start Backend

In the same terminal:

```bash
py app.py
```

or

```bash
python app.py
```

**You should see:**
```
✅ Database tables created successfully!
📊 GALION.STUDIO Alpha is ready!
🌐 API running on http://localhost:5000
 * Running on http://0.0.0.0:5000
```

**Leave this terminal running!**

---

## 🌱 STEP 3: Seed Test Data

Open **NEW Terminal/PowerShell** and run:

```bash
curl -X POST http://localhost:5000/api/seed
```

or using PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/seed" -Method Post
```

**Expected output:**
```json
{
  "message": "Database seeded successfully!",
  "users": 3,
  "workspaces": 1,
  "tasks": 3,
  "time_logs": 2
}
```

---

## 🎨 STEP 4: Start Frontend

In a **NEW Terminal/PowerShell**:

```bash
cd services/galion-alpha/frontend
npm install
npm start
```

**First time:** This will take 2-3 minutes to install packages.

**You should see:**
```
Compiled successfully!

You can now view galion-alpha-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Browser will automatically open at http://localhost:3000**

---

## ✅ VERIFY IT'S WORKING

### 1. Check Backend
Open http://localhost:5000/health in browser

Should show:
```json
{
  "status": "healthy",
  "service": "galion-alpha",
  "timestamp": "2025-11-10T..."
}
```

### 2. Check Frontend
Open http://localhost:3000

You should see:
- GALION.STUDIO header
- Three tabs: Tasks, Time Tracking, Compensation
- Kanban board with 3 columns
- Pre-loaded test tasks

### 3. Test Features

**Drag & Drop:**
- Drag a task from "Backlog" to "In Progress"
- Watch it move instantly

**Create Task:**
- Click "+ New Task"
- Fill in: "Test deployment" / 5 hours / $100/hour
- See total cost: $500
- Click "Create Task"

**Time Tracking:**
- Click "Time Tracking" tab
- See existing time logs
- Click "+ Log Time"

**Compensation:**
- Click "Compensation" tab
- See transparent pay for all team members
- Everyone's rates and earnings visible

---

## 🐛 TROUBLESHOOTING

### Backend Issues

**Problem:** `py` or `python` not found

**Solution:**
- Download Python from https://python.org
- During install, check "Add Python to PATH"
- Restart terminal
- Try again

---

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
py -m pip install --upgrade pip
py -m pip install Flask Flask-SQLAlchemy Flask-CORS
```

---

**Problem:** Port 5000 already in use

**Solution:**
- Kill the process using port 5000
- Or edit `app.py`, change line: `app.run(debug=True, host='0.0.0.0', port=5001)`

---

### Frontend Issues

**Problem:** `npm` not found

**Solution:**
- Download Node.js from https://nodejs.org
- Install LTS version
- Restart terminal
- Try again

---

**Problem:** Port 3000 already in use

**Solution:**
```bash
# Linux/Mac
PORT=3001 npm start

# Windows PowerShell
$env:PORT=3001; npm start
```

---

**Problem:** "Failed to load data" in frontend

**Solution:**
1. Make sure backend is running (check http://localhost:5000/health)
2. Re-seed data: `curl -X POST http://localhost:5000/api/seed`
3. Refresh browser (F5)

---

## 🎯 QUICK DEPLOYMENT CHECKLIST

```
□ Python installed
□ Node.js installed
□ Backend dependencies installed (Flask, etc.)
□ Backend running on port 5000
□ Database seeded with test data
□ Frontend dependencies installed (npm install)
□ Frontend running on port 3000
□ Browser shows GALION.STUDIO
□ Can create tasks
□ Can log time
□ Can see compensation
```

---

## 🚀 AUTOMATED DEPLOYMENT (EASIER)

### Windows PowerShell:
```powershell
cd services/galion-alpha
.\start.ps1
```

This will:
- Start backend in new window
- Seed database
- Start frontend in new window
- Open browser automatically

### Mac/Linux:
```bash
cd services/galion-alpha
chmod +x start.sh
./start.sh
```

---

## 📊 WHAT'S RUNNING

After successful deployment:

**Terminal 1 (Backend):**
```
 * Running on http://0.0.0.0:5000
 * Serving Flask app 'app'
```

**Terminal 2 (Frontend):**
```
webpack compiled successfully
```

**Browser:**
```
http://localhost:3000
GALION.STUDIO Alpha dashboard
```

---

## 🎉 SUCCESS!

If you can see the GALION.STUDIO interface with:
- Tasks page (Kanban board)
- Time Tracking page
- Compensation page

**YOU'RE DEPLOYED! 🚀**

Now:
1. Invite teammates
2. Create real tasks
3. Log real time
4. Get feedback
5. Iterate!

---

## 🔥 PRODUCTION DEPLOYMENT (Later)

For real users (not localhost):

**Option 1: Cheap VPS ($5/month)**
- DigitalOcean, Linode, or Vultr
- Install Python + Node.js
- Clone repo
- Run same commands
- Point domain to server

**Option 2: Heroku (Free tier)**
- Create Heroku account
- Deploy backend as Python app
- Deploy frontend to Netlify/Vercel
- Connect them

**Option 3: AWS/Docker (Overkill for Alpha)**
- Don't do this yet
- Wait until you have 100+ users
- Current setup handles 50 users easily

---

**Built with ⚡ Elon Musk's First Principles ⚡**

Ship → Test → Iterate → Win

**NOW GO! 🚀**

