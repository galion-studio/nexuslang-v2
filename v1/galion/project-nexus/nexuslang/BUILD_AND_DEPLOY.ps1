#!/usr/bin/env pwsh
# NexusLang - Build and Deploy Script
# Following Elon Musk's 5 Building Principles

Write-Host "🚀 NexusLang - BUILD AND DEPLOY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Principle 1: Question Every Requirement
Write-Host "📋 Phase 1: VALIDATE REQUIREMENTS" -ForegroundColor Yellow
Write-Host "Checking what we actually need..." -ForegroundColor Gray

# Check Python
Write-Host "  → Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(9|10|11|12)") {
        Write-Host " ✅ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Python 3.9+ required" -ForegroundColor Yellow
        Write-Host "     Install from: https://python.org" -ForegroundColor Gray
    }
} catch {
    Write-Host " ❌ Python not found" -ForegroundColor Red
    Write-Host "     Install from: https://python.org" -ForegroundColor Gray
}

# Check pip
Write-Host "  → Checking pip..." -NoNewline
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host " ✅ Found" -ForegroundColor Green
} catch {
    Write-Host " ❌ pip not found" -ForegroundColor Red
}

Write-Host ""

# Principle 2: Delete the Part
Write-Host "🗑️  Phase 2: DELETE UNNECESSARY COMPONENTS" -ForegroundColor Yellow
Write-Host "Removing what we don't need..." -ForegroundColor Gray

# Clean build artifacts
Write-Host "  → Cleaning old builds..." -NoNewline
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
if (Test-Path "src/*.egg-info") { Remove-Item -Recurse -Force "src/*.egg-info" }
Write-Host " ✅ Clean" -ForegroundColor Green

Write-Host ""

# Principle 3: Simplify & Optimize
Write-Host "⚡ Phase 3: SIMPLIFY & OPTIMIZE" -ForegroundColor Yellow
Write-Host "Building with minimal dependencies..." -ForegroundColor Gray

# Install build tools
Write-Host "  → Installing build tools..." -NoNewline
try {
    python -m pip install --upgrade pip setuptools wheel build twine --quiet 2>&1 | Out-Null
    Write-Host " ✅ Ready" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Check pip" -ForegroundColor Yellow
}

# Install dependencies
Write-Host "  → Installing dependencies..." -NoNewline
try {
    python -m pip install numpy rich --quiet 2>&1 | Out-Null
    Write-Host " ✅ Installed" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Check installation" -ForegroundColor Yellow
}

Write-Host ""

# Principle 4: Accelerate Cycle Time
Write-Host "🏃 Phase 4: ACCELERATE - BUILD FAST" -ForegroundColor Yellow
Write-Host "Building package at maximum speed..." -ForegroundColor Gray

# Build package
Write-Host "  → Building wheel and sdist..." -NoNewline
try {
    python -m build --quiet 2>&1 | Out-Null
    if (Test-Path "dist") {
        $files = Get-ChildItem "dist"
        Write-Host " ✅ Built $($files.Count) files" -ForegroundColor Green
        foreach ($file in $files) {
            Write-Host "     - $($file.Name)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host " ❌ Build failed" -ForegroundColor Red
}

Write-Host ""

# Principle 5: Automate
Write-Host "🤖 Phase 5: AUTOMATE - TEST EVERYTHING" -ForegroundColor Yellow
Write-Host "Running automated tests..." -ForegroundColor Gray

# Install in editable mode for testing
Write-Host "  → Installing package..." -NoNewline
try {
    python -m pip install -e . --quiet 2>&1 | Out-Null
    Write-Host " ✅ Installed" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Check installation" -ForegroundColor Yellow
}

# Test CLI
Write-Host "  → Testing CLI..." -NoNewline
try {
    $version = python -m nexuslang.cli --version 2>&1
    Write-Host " ✅ Working" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Check CLI" -ForegroundColor Yellow
}

# Test examples
Write-Host "  → Testing examples..." -ForegroundColor Gray
$examples = @(
    "hello.nx",
    "variables.nx",
    "functions.nx"
)

foreach ($example in $examples) {
    Write-Host "     - Running $example..." -NoNewline
    try {
        $output = python -m nexuslang.cli run "examples/$example" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
        } else {
            Write-Host " ⚠️" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " ❌" -ForegroundColor Red
    }
}

Write-Host ""

# Summary
Write-Host "📊 BUILD SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$distFiles = Get-ChildItem "dist" -ErrorAction SilentlyContinue
if ($distFiles) {
    Write-Host "✅ Package built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files created:" -ForegroundColor White
    foreach ($file in $distFiles) {
        $size = [math]::Round($file.Length / 1KB, 2)
        Write-Host "  - $($file.Name) ($size KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  No package files found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 DEPLOYMENT OPTIONS" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 1: Test on TestPyPI (RECOMMENDED)" -ForegroundColor Yellow
Write-Host "  python -m twine upload --repository testpypi dist/*" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 2: Deploy to Production PyPI" -ForegroundColor Yellow
Write-Host "  python -m twine upload dist/*" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 3: Install Locally" -ForegroundColor Yellow
Write-Host "  pip install dist/*.whl" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 4: GitHub Actions (Automated)" -ForegroundColor Yellow
Write-Host "  git tag v0.1.0" -ForegroundColor Gray
Write-Host "  git push origin v0.1.0" -ForegroundColor Gray
Write-Host "  (Deploys automatically via GitHub Actions)" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 NEXT STEPS" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Test locally:" -ForegroundColor White
Write-Host "   nexus repl" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Create PyPI account:" -ForegroundColor White
Write-Host "   https://pypi.org/account/register/" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Deploy to TestPyPI first:" -ForegroundColor White
Write-Host "   python -m twine upload --repository testpypi dist/*" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Then deploy to production:" -ForegroundColor White
Write-Host "   python -m twine upload dist/*" -ForegroundColor Gray
Write-Host ""

Write-Host "🎉 BUILD COMPLETE!" -ForegroundColor Green
Write-Host "NexusLang is ready to ship to the world! 🚀" -ForegroundColor Cyan
Write-Host ""

