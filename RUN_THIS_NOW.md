# 🚀 RUN THIS NOW - SSH Pipeline Setup

**Your RunPod IP:** `213.173.105.83`

---

## ⚡ STEP 1: On Your Windows Laptop

Open PowerShell in the project directory and run:

```powershell
git pull origin clean-nexuslang
.\SETUP_SSH_NOW.ps1
```

**OR double-click:** `SETUP_SSH_NOW.bat`

---

## 📋 STEP 2: Copy the Public Key

The setup script will show you a public key that looks like:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... galion-pipeline-DESKTOP
```

**Copy this entire line!**

---

## 🔧 STEP 3: On Your RunPod Terminal

Run this command (replace `YOUR_PUBLIC_KEY` with the key you copied):

```bash
mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

**Example:**
```bash
mkdir -p ~/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... galion-pipeline-DESKTOP' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

---

## ✅ STEP 4: Test Connection (On Your Laptop)

```powershell
ssh runpod
```

**If it connects without asking for a password, you're done!** 🎉

Type `exit` to return to your laptop.

---

## 🚀 STEP 5: Deploy! (On Your Laptop)

### From PowerShell:
```powershell
cd cursor-ssh-pipeline
.\deploy.ps1
```

### From Cursor IDE:
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "RunPod: Deploy All"

---

## 🎯 Quick Commands (After Setup)

All from your laptop's PowerShell:

```powershell
cd cursor-ssh-pipeline

# Check status
.\quick-commands.ps1 status

# View logs
.\quick-commands.ps1 logs

# Health check
.\quick-commands.ps1 health

# Restart services
.\quick-commands.ps1 restart

# Open RunPod shell
.\quick-commands.ps1 shell

# Start tunnel (access locally)
.\quick-commands.ps1 tunnel
```

---

## 📚 Documentation

- **Quick Start:** `cursor-ssh-pipeline/INSTALLATION.md`
- **Complete Guide:** `cursor-ssh-pipeline/README.md`
- **Command Reference:** `cursor-ssh-pipeline/QUICK_REFERENCE.md`

---

## 🆘 Troubleshooting

### "Permission denied (publickey)"
→ Re-run STEP 3 on RunPod to add your public key

### "Connection refused"
→ Check your RunPod pod is running

### Scripts won't run
→ Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

**Ready? Run `.\SETUP_SSH_NOW.ps1` on your Windows laptop now!** 🚀

