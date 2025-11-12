# NEXUS ADMIN TERMINAL - QUICK START

**⚡ Get admin access in 30 seconds**

---

## Windows (PowerShell)

```powershell
# 1. Setup (first time only)
.\setup-admin-terminal.ps1

# 2. Launch
.\nexus-admin.ps1

# Or directly
python nexus-admin.py
```

---

## Linux/Mac

```bash
# 1. Make executable
chmod +x nexus-admin.py

# 2. Launch
./nexus-admin.py

# Or with Python
python3 nexus-admin.py
```

---

## Common Commands

Once inside the admin terminal:

```
nexus-admin> status          # View system status
nexus-admin> start           # Start all services
nexus-admin> logs api-gateway  # View logs
nexus-admin> users           # User management
nexus-admin> monitor         # Real-time monitoring
nexus-admin> help            # Full command list
```

---

## What You Get

✅ **Full System Control**
- Start/stop/restart services
- View logs in real-time
- Execute commands in containers

✅ **Admin Backdoor**
- Direct database access
- User management
- SQL query console

✅ **Monitoring Dashboard**
- Service health status
- Resource usage
- Auto-refresh mode

✅ **Zero Dependencies**
- Pure Python (stdlib only)
- No npm install
- No pip requirements
- Instant startup

---

## Troubleshooting

**"Python not found"**
→ Install Python from python.org

**"Docker error"**
→ Start Docker Desktop

**"Permission denied"** (Linux/Mac)
→ Run: `chmod +x nexus-admin.py`

**Colors not showing**
→ Use Windows Terminal or modern terminal emulator

---

## Built With

**Elon Musk's First Principles:**
1. ✅ Question requirements (Do we need a web UI? No.)
2. ✅ Delete unnecessary parts (Zero external dependencies)
3. ✅ Optimize (Direct Docker API, fast subprocess calls)
4. ✅ Accelerate (Single file, instant startup)
5. ✅ Automate (Auto-refresh, health checks, backups)

**Result:** 700 lines of pure Python. Zero bloat. Maximum power.

---

## See Full Documentation

→ `ADMIN_TERMINAL.md` - Complete guide with all features

---

**Ship it.** 🚀

