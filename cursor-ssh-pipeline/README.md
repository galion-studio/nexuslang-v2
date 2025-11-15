# 🚀 Cursor → RunPod SSH Pipeline

**Seamless development pipeline connecting Cursor IDE to RunPod server**

This pipeline enables you to code locally in Cursor and deploy/manage your RunPod server with one-click commands - just like running local terminal commands!

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [What This Pipeline Does](#what-this-pipeline-does)
3. [Setup Instructions](#setup-instructions)
4. [Using the Pipeline](#using-the-pipeline)
5. [Cursor Integration](#cursor-integration)
6. [Available Commands](#available-commands)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Step 1: Get Your RunPod IP

In your RunPod terminal:
```bash
curl ifconfig.me
```
Copy the IP address (e.g., `123.45.67.89`)

### Step 2: Setup SSH Connection (One-Time)

**On Windows:**
```powershell
cd cursor-ssh-pipeline
.\setup-local-ssh.ps1 -RunPodIP "YOUR_RUNPOD_IP"
```

**On Mac/Linux:**
```bash
cd cursor-ssh-pipeline
chmod +x *.sh
./setup-local-ssh.sh YOUR_RUNPOD_IP
```

### Step 3: Add Public Key to RunPod

The script will show your public key. Copy it and run on RunPod:
```bash
mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

### Step 4: Test Connection

```bash
ssh runpod
```

If you see the RunPod terminal, **you're connected!** 🎉

### Step 5: Deploy!

**From Cursor:**
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "Tasks: Run Task"
- Select "RunPod: Deploy All"

**Or from terminal:**
```powershell
# Windows
.\deploy.ps1

# Mac/Linux
./deploy.sh
```

---

## 💡 What This Pipeline Does

### Before This Pipeline:
❌ Copy code manually to RunPod  
❌ SSH into RunPod terminal  
❌ Run commands one by one  
❌ Wait and watch for errors  
❌ Repeat for every change  

### With This Pipeline:
✅ Code in Cursor (local)  
✅ One click to deploy  
✅ Automatic build & restart  
✅ Instant status feedback  
✅ Live logs in Cursor  

---

## 🔧 Setup Instructions

### Prerequisites

**Local Machine:**
- Windows 10+ with PowerShell 5.1+, OR Mac/Linux with Bash
- SSH client installed (included in Windows 10+, Mac, Linux)
- Git installed
- Cursor IDE

**RunPod Server:**
- Running pod with SSH access
- Git installed
- Node.js & npm installed
- Python 3.8+ with pip
- PM2 installed globally

### Detailed Setup

#### 1. Clone This Repository (If Not Already)

```bash
# On your local machine
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2/cursor-ssh-pipeline
```

#### 2. Run Setup Script

**Windows:**
```powershell
.\setup-local-ssh.ps1 -RunPodIP "123.45.67.89"
```

**Mac/Linux:**
```bash
chmod +x setup-local-ssh.sh
./setup-local-ssh.sh 123.45.67.89
```

The script will:
- ✅ Create/check SSH directory
- ✅ Generate SSH key (if needed)
- ✅ Configure SSH config file
- ✅ Display public key

#### 3. Add Public Key to RunPod

Copy the public key shown by the script, then on RunPod:

```bash
mkdir -p ~/.ssh
echo 'YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### 4. Verify Setup

```bash
ssh runpod
```

You should connect without password. Type `exit` to return.

---

## 🎮 Using the Pipeline

### From Cursor IDE (Recommended)

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) → "Tasks: Run Task" → Select:

- **RunPod: Deploy All** - Full deployment with build
- **RunPod: Quick Deploy** - Fast deploy without frontend build
- **RunPod: Check Status** - View service status
- **RunPod: View Logs** - Watch live logs
- **RunPod: Restart Services** - Restart all services
- **RunPod: Health Check** - Check all endpoints
- **RunPod: Open Shell** - Interactive RunPod terminal
- **RunPod: Start SSH Tunnel** - Access services locally
- **RunPod: Pull Latest Code** - Update code from GitHub

### From Terminal

**Quick Commands:**

```bash
# Check status
./quick-commands.ps1 status      # Windows
./quick-commands.sh status       # Mac/Linux

# View logs
./quick-commands.ps1 logs

# Restart services
./quick-commands.ps1 restart

# Health check
./quick-commands.ps1 health

# Open shell
./quick-commands.ps1 shell

# Start tunnel
./quick-commands.ps1 tunnel

# Get RunPod IP
./quick-commands.ps1 ip
```

**Full Deployment:**

```bash
# Windows
.\deploy.ps1                    # Full deploy
.\deploy.ps1 -SkipBuild        # Quick deploy
.\deploy.ps1 -Target backend   # Deploy backend only

# Mac/Linux
./deploy.sh                     # Full deploy
./deploy.sh all true            # Quick deploy
```

**Remote Execution:**

```bash
# Windows
.\remote-exec.ps1 "pm2 status"
.\remote-exec.ps1 "git status"
.\remote-exec.ps1 "curl http://localhost:8000/health"

# Mac/Linux
./remote-exec.sh "pm2 status"
```

---

## 🔌 Cursor Integration

### Using Cursor Tasks

The pipeline is integrated into Cursor via `.vscode/tasks.json`.

**To run a task:**

1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select your task

**Keyboard Shortcuts (Optional):**

Add to your `.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+d",
    "command": "workbench.action.tasks.runTask",
    "args": "RunPod: Deploy All"
  },
  {
    "key": "ctrl+shift+l",
    "command": "workbench.action.tasks.runTask",
    "args": "RunPod: View Logs"
  },
  {
    "key": "ctrl+shift+h",
    "command": "workbench.action.tasks.runTask",
    "args": "RunPod: Health Check"
  }
]
```

### Using Cursor Terminal

Open terminal in Cursor (`Ctrl+`` or `View → Terminal`) and run:

```powershell
# Windows
cd cursor-ssh-pipeline
.\deploy.ps1

# Mac/Linux
cd cursor-ssh-pipeline
./deploy.sh
```

---

## 📚 Available Commands

### Deployment Commands

| Command | Description | Example |
|---------|-------------|---------|
| `deploy.ps1` / `deploy.sh` | Full deployment | `.\deploy.ps1` |
| `deploy.ps1 -SkipBuild` | Quick deploy without build | `.\deploy.ps1 -SkipBuild` |
| `deploy.ps1 -Target backend` | Deploy backend only | `.\deploy.ps1 -Target backend` |

### Quick Commands

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Show PM2 service status | `.\quick-commands.ps1 status` |
| `logs` | View live logs | `.\quick-commands.ps1 logs` |
| `logs <service>` | View specific service logs | `.\quick-commands.ps1 logs galion-backend` |
| `restart` | Restart all services | `.\quick-commands.ps1 restart` |
| `restart <service>` | Restart specific service | `.\quick-commands.ps1 restart galion-backend` |
| `stop` | Stop all services | `.\quick-commands.ps1 stop` |
| `start` | Start all services | `.\quick-commands.ps1 start` |
| `health` | Check all health endpoints | `.\quick-commands.ps1 health` |
| `shell` | Open interactive shell | `.\quick-commands.ps1 shell` |
| `pull` | Pull latest code | `.\quick-commands.ps1 pull` |
| `tunnel` | Start SSH tunnel | `.\quick-commands.ps1 tunnel` |
| `ip` | Get RunPod IP | `.\quick-commands.ps1 ip` |

### Remote Execution

Execute any command on RunPod:

```powershell
# Windows
.\remote-exec.ps1 "your command here"
.\remote-exec.ps1 "pm2 status"
.\remote-exec.ps1 "git log -1"

# Mac/Linux
./remote-exec.sh "your command here"
```

### SSH Tunneling

Access RunPod services on your local machine:

```bash
# Start tunnel
ssh runpod-tunnel -N

# Or use quick command
.\quick-commands.ps1 tunnel
```

**Then access locally:**
- Backend: http://localhost:8000
- Galion Studio: http://localhost:3001
- Developer Platform: http://localhost:3002
- Galion App: http://localhost:3003

---

## 🔍 Troubleshooting

### SSH Connection Issues

**Problem:** "Permission denied (publickey)"

**Solution:**
```bash
# Check SSH config
cat ~/.ssh/config

# Test connection with verbose output
ssh -v runpod

# Verify public key on RunPod
ssh runpod "cat ~/.ssh/authorized_keys"
```

---

**Problem:** "Connection refused"

**Solution:**
```bash
# Check if RunPod is running
# Go to RunPod dashboard and verify pod status

# Test with IP directly
ssh root@YOUR_RUNPOD_IP

# Check if SSH is running on RunPod
ssh runpod "systemctl status ssh"
```

---

### Deployment Issues

**Problem:** Services fail to start

**Solution:**
```bash
# Check logs
.\quick-commands.ps1 logs

# Restart services manually
ssh runpod "cd /nexuslang-v2 && pm2 restart all"

# Check PM2 status
ssh runpod "pm2 status"
```

---

**Problem:** Frontend build fails

**Solution:**
```bash
# Deploy without building (use dev mode)
.\deploy.ps1 -SkipBuild

# Or manually build on RunPod
ssh runpod "cd /nexuslang-v2/galion-studio && npm install && npm run build"
```

---

**Problem:** Backend not found

**Solution:**
```bash
# Check if on correct branch
ssh runpod "cd /nexuslang-v2 && git branch && git checkout clean-nexuslang"

# Verify backend file exists
ssh runpod "ls -la /nexuslang-v2/v2/backend/main_simple.py"
```

---

### Tunnel Issues

**Problem:** Tunnel disconnects

**Solution:**
```bash
# Use persistent tunnel with autossh (install on local machine)
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" runpod-tunnel -N
```

---

**Problem:** Port already in use

**Solution:**
```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# On Mac/Linux
lsof -ti:8000 | xargs kill -9
```

---

## 🎓 Best Practices

### Daily Workflow

1. **Morning:** Start tunnel for local development
   ```bash
   .\quick-commands.ps1 tunnel
   ```

2. **Code:** Work in Cursor locally

3. **Deploy:** Use Cursor task or quick deploy
   ```bash
   .\deploy.ps1 -SkipBuild
   ```

4. **Monitor:** Check logs and health
   ```bash
   .\quick-commands.ps1 logs
   .\quick-commands.ps1 health
   ```

5. **Evening:** Check status before leaving
   ```bash
   .\quick-commands.ps1 status
   ```

### Git Workflow

```bash
# 1. Make changes locally
# 2. Commit and push to GitHub
git add .
git commit -m "Your changes"
git push origin clean-nexuslang

# 3. Deploy to RunPod (pulls from GitHub)
.\deploy.ps1
```

### Quick Testing

```bash
# Test backend locally through tunnel
.\quick-commands.ps1 tunnel &

# In another terminal
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test on RunPod directly
ssh runpod "curl http://localhost:8000/health"
```

---

## 📦 File Structure

```
cursor-ssh-pipeline/
├── README.md                    # This file
├── setup-local-ssh.ps1          # Windows setup
├── setup-local-ssh.sh           # Mac/Linux setup
├── deploy.ps1                   # Windows deployment
├── deploy.sh                    # Mac/Linux deployment
├── remote-exec.ps1              # Windows remote execution
├── quick-commands.ps1           # Windows quick commands
├── quick-commands.sh            # Mac/Linux quick commands
├── connection-info.json         # Generated: connection details
└── .gitignore                   # Ignore sensitive files

../.vscode/
└── tasks.json                   # Cursor/VSCode task definitions
```

---

## 🚀 Advanced Usage

### Custom Deployment Targets

```powershell
# Deploy only backend
.\deploy.ps1 -Target backend

# Deploy only frontend
.\deploy.ps1 -Target frontend

# Deploy specific service
.\remote-exec.ps1 "cd /nexuslang-v2/galion-studio && pm2 restart galion-studio"
```

### Parallel Deployments

```bash
# Start multiple deploys (not recommended unless needed)
Start-Job { .\deploy.ps1 -Target backend }
Start-Job { .\deploy.ps1 -Target frontend }
```

### Custom Scripts

Create your own scripts using the pipeline:

```powershell
# my-custom-deploy.ps1
param([string]$Branch = "clean-nexuslang")

.\remote-exec.ps1 "cd /nexuslang-v2 && git checkout $Branch && git pull"
.\deploy.ps1 -SkipBuild
.\quick-commands.ps1 health
```

---

## 🎉 Success!

You now have a complete SSH pipeline connecting Cursor to RunPod!

**What you can do:**
- ✅ Deploy with one click from Cursor
- ✅ View live logs in Cursor terminal
- ✅ Execute remote commands instantly
- ✅ Test services locally through tunnel
- ✅ Monitor health and status in real-time

**Next steps:**
- Set up keyboard shortcuts for frequent tasks
- Customize deployment scripts for your workflow
- Add monitoring and alerting
- Automate with CI/CD

---

**Questions or issues?** Check the troubleshooting section or run:
```bash
.\quick-commands.ps1 health
```

**Happy coding! 🚀**

