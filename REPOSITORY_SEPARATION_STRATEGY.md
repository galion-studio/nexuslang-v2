# 🔒 Repository Separation Strategy

**Problem**: Git history contains accidentally committed secrets  
**Solution**: Separate private and public repos with clean histories

---

## 📦 Two-Repository Approach

### Repository 1: project-nexus (PRIVATE)

**Purpose**: Your complete workspace  
**Visibility**: Private  
**Contains**:
- Full codebase (v1 + v2)
- Internal documentation
- Business planning
- Private configurations
- Development notes
- All experiments

**Security**:
- Contains secrets (properly gitignored)
- Private business docs
- Internal tools
- Not shared publicly

**Action**: Push with clean history (no secrets in commits)

---

### Repository 2: nexuslang-v2 (PUBLIC - Open Source)

**Purpose**: Open source product  
**Visibility**: Public  
**Contains**:
- v2/ code ONLY
- Public documentation
- Examples
- Contributing guide
- MIT License

**Excludes**:
- v1/ legacy code
- Private business docs
- API keys (even in history)
- Internal notes
- Deployment configs with IPs

**Action**: Fresh repo with clean history

---

## 🚀 Execution Plan

### Step 1: Clean Private Repo (project-nexus)

```powershell
# Run this script
.\push-clean-to-github.ps1

# This will:
# - Create new branch with clean history
# - Replace main branch
# - Force push (removes secret from history)
# - Result: Private repo safe
```

**Time**: 2 minutes  
**Risk**: Low (it's your private repo)  
**Benefit**: Clean history, no secrets

---

### Step 2: Create Public Repo (nexuslang-v2)

```powershell
# Run this script
.\create-public-repo.ps1

# This will:
# - Copy only v2/ code
# - Remove all private files
# - Create public README
# - Initialize fresh git repo
# - Ready to push
```

**Then manually:**
1. Create GitHub repo: `nexuslang-v2` (PUBLIC)
2. Add remote: `git remote add origin https://github.com/YOUR-ORG/nexuslang-v2.git`
3. Push: `git push -u origin main`

**Time**: 5 minutes  
**Risk**: None (new repo, clean history)  
**Benefit**: Open source presence

---

## 📁 What Goes Where?

### Private Repo (project-nexus):
```
✅ All v2/ code
✅ All v1/ code (legacy)
✅ Business docs (budget, marketing)
✅ Internal deployment scripts
✅ Private notes and plans
✅ Configuration files
✅ Backup scripts
✅ Development history
```

### Public Repo (nexuslang-v2):
```
✅ v2/backend/ (application code)
✅ v2/frontend/ (UI code)
✅ v2/nexuslang/ (language core)
✅ v2/docs/ (public documentation)
✅ v2/database/schemas/ (database structure)
✅ Examples and tutorials
✅ README.md (public-facing)
✅ LICENSE (MIT)
✅ CONTRIBUTING.md

❌ v1/ (old code)
❌ Business docs (budget, marketing)
❌ Deployment scripts with IPs/domains
❌ .env files (even templates with real data)
❌ Private configurations
❌ Internal planning docs
```

---

## 🔒 Security Best Practices

### For Private Repo:

**DO:**
- ✅ Use strong .gitignore
- ✅ Clean git history before sharing
- ✅ Store real secrets in environment variables only
- ✅ Document where secrets should go (templates)

**DON'T:**
- ❌ Commit .env files
- ❌ Hardcode API keys in code
- ❌ Include real passwords in examples
- ❌ Share repository access broadly

### For Public Repo:

**DO:**
- ✅ Use placeholder values everywhere
- ✅ Document HOW to get API keys (not actual keys)
- ✅ Include comprehensive setup instructions
- ✅ Keep examples generic and safe

**DON'T:**
- ❌ Include ANY real credentials
- ❌ Include private business information
- ❌ Include customer data
- ❌ Include internal IPs/domains

---

## 🎯 Implementation Steps

### Immediate (Do Now):

```powershell
# Step 1: Clean private repo history
.\push-clean-to-github.ps1

# Step 2: Create public repo export
.\create-public-repo.ps1

# Step 3: Verify no secrets
.\final-security-check.sh  # (in WSL/Git Bash)
```

### After GitHub Push:

```powershell
# Deploy to RunPod (private repo has deployment scripts)
# SSH to RunPod
# cd /workspace/project-nexus
# git pull origin main
# ./deploy-to-runpod-production.sh
```

---

## 📊 File Organization Matrix

| File Type | Private Repo | Public Repo | Notes |
|-----------|--------------|-------------|-------|
| Application Code | ✅ | ✅ | Same code both places |
| Documentation | ✅ | ✅ (filtered) | Public gets user-facing docs only |
| Business Plans | ✅ | ❌ | Budget, marketing stay private |
| Deployment Scripts | ✅ | ❌ | With IPs stay private |
| Generic Scripts | ✅ | ✅ | Setup scripts OK publicly |
| .env templates | ✅ | ✅ (sanitized) | With placeholders only |
| Test Suites | ✅ | ✅ | Tests are good for open source |
| Examples | ✅ | ✅ | Share widely |

---

## 🎯 Workflow Going Forward

### Making Changes:

```
1. Work in private repo (project-nexus)
2. Develop features, test thoroughly
3. Commit to private repo
4. When ready for public release:
   - Run create-public-repo.ps1
   - Review changes
   - Push to public repo
```

### Keeping Repos in Sync:

```powershell
# Script to sync public repo (create this if needed)
# Copies v2/ → public repo
# Runs security scan
# Sanitizes any secrets
# Commits to public
```

---

## 🚨 Emergency: If Secret Was Pushed

### Option 1: If Just Pushed (Last Few Minutes)

```bash
# Undo the push (if no one pulled yet)
git reset --hard HEAD~1
git push --force origin main
```

### Option 2: If Secret in Multiple Commits

```bash
# Use BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Remove secret from all commits
java -jar bfg.jar --replace-text secrets.txt

# secrets.txt contains:
# sk-proj-old-key-here==>REDACTED

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force origin main
```

### Option 3: Nuclear Option (Public Repo Only)

```bash
# Delete and recreate public repo
# This is safe for public repos without users yet

# 1. Delete repo on GitHub
# 2. Run create-public-repo.ps1 again
# 3. Create new GitHub repo
# 4. Push fresh history
```

**IMPORTANT**: Always rotate compromised secrets immediately!

---

## ✅ Verification Checklist

After separating repos:

**Private Repo:**
- [ ] No secrets visible in recent commits
- [ ] .gitignore protecting sensitive files
- [ ] Can deploy to RunPod
- [ ] All internal docs present

**Public Repo:**
- [ ] No secrets anywhere (check git history)
- [ ] Only v2/ code present
- [ ] Documentation is user-facing only
- [ ] README is public-friendly
- [ ] License file included
- [ ] Contributing guide present

**Both Repos:**
- [ ] No API keys in code
- [ ] No passwords in files
- [ ] No IPs in configs
- [ ] Secrets only in environment variables

---

## 🎯 Current Status

**Private Repo (project-nexus)**:
- Status: Needs clean push
- Action: Run `push-clean-to-github.ps1`
- Result: Clean history, ready for team

**Public Repo (nexuslang-v2)**:
- Status: Ready to create
- Action: Run `create-public-repo.ps1`
- Result: Open source release ready

---

## 📞 Next Actions

```powershell
# 1. Clean private repo
.\push-clean-to-github.ps1

# 2. Create public repo
.\create-public-repo.ps1

# 3. Push both
# (follow prompts from scripts)

# 4. Deploy to RunPod
# (from private repo, which has deployment scripts)
```

**Time**: 10 minutes total  
**Result**: Secure, separated, production-ready

---

**Security first. Transparency second. Ship fast.** 🚀

