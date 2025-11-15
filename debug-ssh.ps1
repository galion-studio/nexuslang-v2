# Debug SSH Connection Issues

Write-Host "🔍 SSH Connection Debug" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan
Write-Host ""

$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
$runPodIP = "213.173.105.83"

Write-Host "📋 Checking local SSH setup..." -ForegroundColor Yellow

# Check SSH key exists
if (Test-Path $sshKeyPath) {
    Write-Host "✅ SSH private key exists" -ForegroundColor Green
} else {
    Write-Host "❌ SSH private key missing" -ForegroundColor Red
    exit 1
}

# Check SSH public key
if (Test-Path "$sshKeyPath.pub") {
    Write-Host "✅ SSH public key exists" -ForegroundColor Green
    Write-Host "Your public key:" -ForegroundColor Gray
    Get-Content "$sshKeyPath.pub"
} else {
    Write-Host "❌ SSH public key missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔧 Commands to run in RunPod web terminal:" -ForegroundColor Cyan
Write-Host "=" * 45 -ForegroundColor Cyan

Write-Host ""
Write-Host "1️⃣ Check SSH key permissions:" -ForegroundColor Yellow
Write-Host "   ls -la ~/.ssh/" -ForegroundColor White
Write-Host "   # Should show: -rw------- authorized_keys" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣ Fix permissions if needed:" -ForegroundColor Yellow
Write-Host "   chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "   chmod 700 ~/.ssh" -ForegroundColor White
Write-Host ""

Write-Host "3️⃣ Check SSH service:" -ForegroundColor Yellow
Write-Host "   sudo systemctl status ssh" -ForegroundColor White
Write-Host "   sudo systemctl restart ssh" -ForegroundColor White
Write-Host ""

Write-Host "4️⃣ Verify key format:" -ForegroundColor Yellow
Write-Host "   cat ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "   # Should start with: ssh-ed25519 AAAAC3..." -ForegroundColor Gray
Write-Host ""

Write-Host "🔄 Alternative: Use verbose SSH" -ForegroundColor Cyan
Write-Host "ssh -v -i $sshKeyPath root@$runPodIP" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Quick Domain Setup (skip SSH):" -ForegroundColor Green
Write-Host "Just run in RunPod web terminal:" -ForegroundColor Green
Write-Host "wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/runpod-domain-setup.sh | bash" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 30 -ForegroundColor Cyan
