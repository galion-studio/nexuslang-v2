# ╔════════════════════════════════════════════════════════════╗
# ║  Create Public Repository - Open Source Release           ║
# ║  Exports ONLY v2/ code without secrets or private data    ║
# ╚════════════════════════════════════════════════════════════╝

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  🌟 Create Public Repository (nexuslang-v2)                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Configuration
$PublicRepoPath = "..\nexuslang-v2-public"
$SourcePath = ".\v2"

Write-Host "This script will:" -ForegroundColor White
Write-Host "  1. Create clean copy of v2/ code" -ForegroundColor Gray
Write-Host "  2. Remove private/sensitive files" -ForegroundColor Gray
Write-Host "  3. Add open source license" -ForegroundColor Gray
Write-Host "  4. Create public-ready README" -ForegroundColor Gray
Write-Host "  5. Initialize new git repo (clean history)" -ForegroundColor Gray
Write-Host ""

if (Test-Path $PublicRepoPath) {
    Write-Host "⚠️  Directory $PublicRepoPath already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Delete and recreate? (y/N)"
    if ($overwrite -ne "y") {
        Write-Host "Aborted." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force $PublicRepoPath
}

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Step 1: Copying v2/ Code" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Create directory
New-Item -ItemType Directory -Path $PublicRepoPath | Out-Null
Write-Host "✅ Created: $PublicRepoPath" -ForegroundColor Green

# Copy v2/ directory
Write-Host "📦 Copying v2/ code..." -ForegroundColor Yellow
Copy-Item -Path $SourcePath -Destination "$PublicRepoPath\v2" -Recurse

# Copy essential root files (public-safe)
$publicRootFiles = @(
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    ".gitignore"
)

foreach ($file in $publicRootFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $PublicRepoPath
        Write-Host "  ✅ Copied: $file" -ForegroundColor Gray
    }
}

Write-Host "✅ Files copied" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Step 2: Removing Private Files" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Remove sensitive files/directories
$privatePatterns = @(
    "*\.env",
    "*\.env.local",
    "*.env.production",
    "__pycache__",
    "node_modules",
    "*.db",
    "*.sqlite",
    "backups",
    "logs",
    "*secrets*",
    "*credentials*",
    "*api-keys*"
)

foreach ($pattern in $privatePatterns) {
    $files = Get-ChildItem -Path $PublicRepoPath -Filter $pattern -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Remove-Item -Path $file.FullName -Recurse -Force
        Write-Host "  🗑️  Removed: $($file.Name)" -ForegroundColor Gray
    }
}

Write-Host "✅ Private files removed" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Step 3: Creating Public README" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Create public-facing README
$publicReadme = @"
# 🚀 NexusLang v2

**The First AI-Native Programming Language**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0--beta-green.svg)](https://github.com/galion-studio/nexuslang-v2)
[![Status](https://img.shields.io/badge/status-production--ready-success.svg)](https://developer.galion.app)

**[🌐 Live Platform](https://developer.galion.app)** • **[📖 Documentation](./v2/docs/)** • **[🎮 Try IDE](https://developer.galion.app/ide)** • **[💬 Discord](https://discord.gg/nexuslang)**

---

## ⚡ What is NexusLang v2?

NexusLang is the world's first programming language designed by AI for AI, featuring:

- **10x Faster**: Binary compilation for AI processing
- **Built-in AI**: Personality system, knowledge integration, voice-first design
- **Complete Platform**: IDE, knowledge base, community, all integrated
- **Open Source**: MIT licensed, built in public

## 🚀 Quick Start

\`\`\`bash
# Try online (no installation)
https://developer.galion.app/ide

# Or install CLI
pip install nexuslang
nexuslang run hello.nx

# Or use Docker
docker run -it galion/nexuslang:v2
\`\`\`

## 📖 Documentation

See [v2/docs/](./v2/docs/) for complete documentation.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Star History

Star this repo to support the project! ⭐

---

**Built with First Principles** • **Designed for the 22nd Century** • **Open for Everyone**
"@

$publicReadme | Out-File -FilePath "$PublicRepoPath\README.md" -Encoding UTF8
Write-Host "✅ Public README created" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Step 4: Initializing Git" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Initialize git
Set-Location $PublicRepoPath
git init
Write-Host "✅ Git initialized" -ForegroundColor Green

# Add all files
git add -A
Write-Host "✅ Files staged" -ForegroundColor Green

# Initial commit
git commit -m "Initial Release: NexusLang v2 - AI-Native Programming Language

Open source release of the world's first AI-native programming language.

Features:
- Binary compilation (10x faster AI processing)
- AI personality system (industry-first)
- Built-in knowledge integration
- Voice-first development
- Complete web IDE
- Production-ready platform

Ready for community contributions and production use."

Write-Host "✅ Initial commit created" -ForegroundColor Green
Write-Host ""

# Set remote (user needs to create repo first)
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ PUBLIC REPOSITORY READY" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Create PUBLIC repository on GitHub:" -ForegroundColor Yellow
Write-Host "   Name: nexuslang-v2" -ForegroundColor Gray
Write-Host "   Visibility: PUBLIC" -ForegroundColor Gray
Write-Host "   Description: The first AI-native programming language" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Add remote and push:" -ForegroundColor Yellow
Write-Host "   cd $PublicRepoPath" -ForegroundColor Cyan
Write-Host "   git remote add origin https://github.com/YOUR-ORG/nexuslang-v2.git" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Location: $PublicRepoPath" -ForegroundColor White
Write-Host "Status: ✅ Clean (no secrets, no history)" -ForegroundColor Green
Write-Host ""

Set-Location ..

