# Setup SSH Access to TITANAXE VPS
## Get Access to Deploy GALION

**Issue:** Cannot SSH with password - TITANAXE requires SSH keys

---

## 🔑 **SOLUTION: Generate and Add SSH Key**

### **Step 1: Generate SSH Key** (On your Windows machine)

In PowerShell:

```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "polskitygrys111@gmail.com"

# Press Enter for default location (~/.ssh/id_ed25519)
# Press Enter twice to skip passphrase (or create one)
```

### **Step 2: Get Your Public Key**

```powershell
# Display your public key
Get-Content ~\.ssh\id_ed25519.pub
```

**Copy the entire output** (starts with `ssh-ed25519 AAAA...`)

---

### **Step 3: Add SSH Key to TITANAXE Panel**

1. **Go to TITANAXE panel** (where you showed firewall)
2. **Look for:** "SSH Keys" or "Klucze SSH" section
3. **Click:** "Add SSH Key" or "+ Dodaj"
4. **Paste:** Your public key from Step 2
5. **Save**

---

### **Step 4: Try SSH Again**

```powershell
ssh root@54.37.161.67
```

**Should connect automatically now!**

---

## 🆘 **IF SSH KEYS SECTION NOT FOUND:**

### **Alternative: Contact Support with This Exact Message**

**Send to:** support@titanaxe.com

```
Subject: Add SSH Key to VPS 54.37.161.67

Hello,

I need to add my SSH public key to enable access to my VPS.

VPS: 54.37.161.67 (VPS Max 3XL 16384 MB)
Account: polskitygrys111@gmail.com

My SSH public key:
[PASTE YOUR PUBLIC KEY HERE from Get-Content ~\.ssh\id_ed25519.pub]

Please add this key to the root user's authorized_keys.

Thank you!
```

---

## 🚀 **AFTER YOU GET ACCESS:**

Once SSH works, run this ONE command:

```bash
curl -fsSL https://raw.githubusercontent.com/galion-studio/galion-platform/main/FULL_AUTO_DEPLOY.sh | bash
```

**Everything deploys automatically. 30-45 minutes. Done.**

---

## 📞 **WHAT TO DO NOW:**

1. ✅ Generate SSH key (Step 1-2 above)
2. ✅ Add to TITANAXE panel OR email support (Step 3)
3. ✅ Wait 5-30 minutes for key to be added
4. ✅ Try SSH again
5. ✅ Run deployment command

**This is the ONLY way forward without manual console access.**

