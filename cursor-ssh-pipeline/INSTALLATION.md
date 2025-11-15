# 📦 Installation Instructions

**Quick installation guide for the Cursor → RunPod SSH Pipeline**

---

## ⚡ Express Installation (5 Minutes)

### Prerequisites
- RunPod instance running
- Cursor IDE installed
- Git installed locally

### Step 1: Get RunPod IP (30 seconds)

In your RunPod terminal:
```bash
curl ifconfig.me
```
**Save this IP!** Example: `123.45.67.89`

### Step 2: Run Setup Script (2 minutes)

**On Windows:**
```powershell
cd C:\Users\YourUsername\Documents\project-nexus\cursor-ssh-pipeline
.\setup-local-ssh.ps1 -RunPodIP "YOUR_IP_HERE"
```

**On Mac/Linux:**
```bash
cd ~/Documents/project-nexus/cursor-ssh-pipeline
chmod +x *.sh
./setup-local-ssh.sh YOUR_IP_HERE
```

### Step 3: Copy Public Key (1 minute)

The setup script will show your public key. Copy it.

### Step 4: Add Key to RunPod (1 minute)

In RunPod terminal, paste (replace `YOUR_PUBLIC_KEY`):
```bash
mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

### Step 5: Test Connection (30 seconds)

On your local machine:
```bash
ssh runpod
```

If it connects **without asking for password**, you're done! ✅

Type `exit` to return to local machine.

### Step 6: First Deployment (1 minute)

**From Cursor:**
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "RunPod: Deploy All"

**From Terminal:**
```powershell
# Windows
.\deploy.ps1

# Mac/Linux
./deploy.sh
```

---

## 🎉 Installation Complete!

You can now:
- Deploy with one click from Cursor
- Execute remote commands instantly
- View live logs in your IDE
- Access RunPod services locally

**Next:** Read [README.md](README.md) for complete usage guide

---

## 🔧 What Was Installed?

### On Your Local Machine:
- ✅ SSH key pair (~/.ssh/id_ed25519)
- ✅ SSH config (~/.ssh/config)
- ✅ RunPod connection shortcuts
- ✅ Deployment scripts
- ✅ Cursor/VSCode tasks

### On RunPod:
- ✅ Your public SSH key (authorized_keys)

### No Changes:
- ❌ No global system changes
- ❌ No admin/sudo required
- ❌ No firewall modifications
- ❌ Easy to uninstall

---

## 🗑️ Uninstallation

If you ever want to remove the pipeline:

### Local Machine:

```powershell
# Remove SSH config entries
# Edit ~/.ssh/config and delete "Host runpod" sections

# Remove SSH key (optional)
rm ~/.ssh/id_ed25519*

# Remove pipeline directory
rm -rf cursor-ssh-pipeline
```

### RunPod:

```bash
# Remove public key
rm ~/.ssh/authorized_keys
```

---

## ✅ Verification

After installation, run these tests:

```bash
# 1. SSH connection
ssh runpod echo "✓ SSH works!"

# 2. Check services
.\quick-commands.ps1 status

# 3. Health check
.\quick-commands.ps1 health

# 4. Test deployment
.\deploy.ps1 -SkipBuild
```

All commands should work without errors.

---

## 🆘 Installation Troubleshooting

### Issue: "ssh: connect to host ... port 22: Connection refused"

**Solution:**
- Check RunPod pod is running
- Verify IP address is correct
- Check SSH service on RunPod: `systemctl status ssh`

---

### Issue: "Permission denied (publickey)"

**Solution:**
- Verify public key was added correctly to RunPod
- Check: `ssh runpod "cat ~/.ssh/authorized_keys"`
- Re-run Step 4 if needed

---

### Issue: Scripts won't run on Windows

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue: Scripts won't run on Mac/Linux

**Solution:**
```bash
chmod +x cursor-ssh-pipeline/*.sh
```

---

## 📚 Next Steps

1. ✅ Installation complete
2. 📖 Read [README.md](README.md) for full documentation
3. ⚡ Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
4. 🚀 Start deploying!

---

**Installation help?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

