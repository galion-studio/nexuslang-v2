# 🚀 Cursor → RunPod SSH Pipeline

**Complete automation pipeline connecting Cursor IDE to RunPod server**

---

## 📚 Documentation

This directory contains a complete SSH pipeline for seamless development between your local Cursor IDE and RunPod server.

### **Start Here:**
👉 [`cursor-ssh-pipeline/SETUP_GUIDE.md`](cursor-ssh-pipeline/SETUP_GUIDE.md) - Complete setup instructions

### **Quick Access:**
- 📖 [`README.md`](cursor-ssh-pipeline/README.md) - Full documentation
- ⚡ [`QUICK_REFERENCE.md`](cursor-ssh-pipeline/QUICK_REFERENCE.md) - Command cheat sheet

---

## 🎯 What This Does

### Before:
❌ Manual file copying  
❌ Multiple SSH sessions  
❌ Manual service restarts  
❌ No real-time feedback  

### After:
✅ **One-click deployment from Cursor**  
✅ **Automatic builds & restarts**  
✅ **Live logs in IDE**  
✅ **Remote command execution**  
✅ **Local testing via SSH tunnel**  

---

## ⚡ Quick Start

### 1. Setup (One-Time)

**Windows:**
```powershell
cd cursor-ssh-pipeline
.\setup-local-ssh.ps1 -RunPodIP "YOUR_RUNPOD_IP"
```

**Mac/Linux:**
```bash
cd cursor-ssh-pipeline
./setup-local-ssh.sh YOUR_RUNPOD_IP
```

### 2. Add Public Key to RunPod

```bash
# On RunPod (copy public key from setup output)
mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

### 3. Test Connection

```bash
ssh runpod
```

### 4. Deploy!

**From Cursor:** Press `Ctrl+Shift+P` → "Tasks: Run Task" → "RunPod: Deploy All"

**From Terminal:**
```powershell
.\cursor-ssh-pipeline\deploy.ps1
```

---

## 🎮 Usage

### From Cursor IDE (Recommended)

Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac):

| Task | Description |
|------|-------------|
| **RunPod: Deploy All** | Full deployment with build |
| **RunPod: Quick Deploy** | Fast deploy (no build) |
| **RunPod: Check Status** | View PM2 services |
| **RunPod: View Logs** | Live log stream |
| **RunPod: Restart Services** | Restart all services |
| **RunPod: Health Check** | Test all endpoints |
| **RunPod: Open Shell** | Interactive RunPod terminal |
| **RunPod: Start Tunnel** | Access services locally |

### From Terminal

```powershell
# Windows
cd cursor-ssh-pipeline
.\deploy.ps1                    # Full deploy
.\deploy.ps1 -SkipBuild        # Quick deploy
.\quick-commands.ps1 status    # Check status
.\quick-commands.ps1 logs      # View logs
.\quick-commands.ps1 health    # Health check

# Mac/Linux
cd cursor-ssh-pipeline
./deploy.sh                     # Full deploy
./quick-commands.sh status      # Check status
./quick-commands.sh logs        # View logs
```

---

## 📦 What's Included

```
cursor-ssh-pipeline/
├── README.md                # Complete documentation
├── SETUP_GUIDE.md          # Step-by-step setup
├── QUICK_REFERENCE.md      # Command cheat sheet
│
├── setup-local-ssh.ps1     # Windows setup
├── setup-local-ssh.sh      # Mac/Linux setup
│
├── deploy.ps1              # Windows deployment
├── deploy.sh               # Mac/Linux deployment
│
├── quick-commands.ps1      # Windows quick commands
├── quick-commands.sh       # Mac/Linux quick commands
│
├── remote-exec.ps1         # Windows remote execution
│
└── .gitignore              # Protect sensitive files

.vscode/
└── tasks.json              # Cursor/VSCode integration
```

---

## 🔧 Features

### ✅ Automated Deployment
- Pull latest code from GitHub
- Install dependencies automatically
- Build frontends (optional)
- Restart services with PM2
- Verify deployment success

### ✅ Quick Commands
- Check service status
- View live logs
- Restart/stop/start services
- Health checks
- Get RunPod IP

### ✅ Remote Execution
- Run any command on RunPod from local machine
- Interactive shell access
- Execute scripts remotely

### ✅ SSH Tunneling
- Access RunPod services locally
- Test APIs on localhost
- Debug with local tools

### ✅ Cursor Integration
- One-click tasks in IDE
- Integrated terminal output
- Keyboard shortcuts support

---

## 🎓 Common Workflows

### Daily Development

```bash
# Morning: Start tunnel
.\quick-commands.ps1 tunnel

# Code locally in Cursor
# ...

# Deploy changes
.\deploy.ps1 -SkipBuild

# Check health
.\quick-commands.ps1 health
```

### Debugging Issues

```bash
# Check status
.\quick-commands.ps1 status

# View logs
.\quick-commands.ps1 logs

# Open shell for investigation
.\quick-commands.ps1 shell
```

### Testing Changes

```bash
# Deploy
.\deploy.ps1

# Start tunnel
.\quick-commands.ps1 tunnel

# Test locally
# Open browser to http://localhost:8000
```

---

## 🔍 Troubleshooting

### Connection Issues

```bash
# Test SSH
ssh runpod echo "Connected!"

# Check SSH config
cat ~/.ssh/config

# Verify key
cat ~/.ssh/id_ed25519.pub
```

### Service Issues

```bash
# Check logs
.\quick-commands.ps1 logs

# Restart services
.\quick-commands.ps1 restart

# Health check
.\quick-commands.ps1 health
```

### Deployment Issues

```bash
# Check git status
ssh runpod "cd /nexuslang-v2 && git status"

# Force pull
ssh runpod "cd /nexuslang-v2 && git fetch --all && git reset --hard origin/clean-nexuslang"

# Re-deploy
.\deploy.ps1
```

---

## 📖 Documentation Links

### Essential Reading:
1. **[SETUP_GUIDE.md](cursor-ssh-pipeline/SETUP_GUIDE.md)** - First-time setup
2. **[README.md](cursor-ssh-pipeline/README.md)** - Complete documentation
3. **[QUICK_REFERENCE.md](cursor-ssh-pipeline/QUICK_REFERENCE.md)** - Daily use commands

### Related Documentation:
- [SSH_TUNNEL_GUIDE.md](SSH_TUNNEL_GUIDE.md) - SSH tunneling details
- [RUNPOD_SSH_INSTRUCTIONS.md](RUNPOD_SSH_INSTRUCTIONS.md) - RunPod SSH setup

---

## 🚀 Benefits

### Developer Experience
- ⚡ Deploy in <30 seconds
- 🔄 Automatic service management
- 📊 Real-time status feedback
- 🔍 Integrated logging
- 🛠️ One-click operations

### Productivity
- 💻 Code locally, deploy remotely
- 🎯 Focus on development, not ops
- ⚙️ Automated workflows
- 🔄 Continuous deployment ready
- 📈 Faster iteration cycles

### Reliability
- ✅ Consistent deployments
- 🔒 Secure SSH authentication
- 🎯 Error detection & reporting
- 📋 Comprehensive logging
- 🔄 Easy rollback capability

---

## 🆘 Support

### Quick Help

```bash
# Health check
.\quick-commands.ps1 health

# View logs
.\quick-commands.ps1 logs

# Check status
.\quick-commands.ps1 status
```

### Documentation
- Read the [troubleshooting section](cursor-ssh-pipeline/README.md#troubleshooting)
- Check [SETUP_GUIDE.md](cursor-ssh-pipeline/SETUP_GUIDE.md#common-issues--solutions)
- Review [QUICK_REFERENCE.md](cursor-ssh-pipeline/QUICK_REFERENCE.md#-troubleshooting-commands)

---

## 🎉 Get Started!

1. **Setup:** Follow [`SETUP_GUIDE.md`](cursor-ssh-pipeline/SETUP_GUIDE.md)
2. **Deploy:** Run `.\deploy.ps1` or use Cursor task
3. **Enjoy:** One-click deployments from Cursor! 🚀

---

**Questions?** Check the [README](cursor-ssh-pipeline/README.md) or [Quick Reference](cursor-ssh-pipeline/QUICK_REFERENCE.md)

**Happy coding! 🚀**

