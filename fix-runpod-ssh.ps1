# Fix RunPod SSH Connection Issues

Write-Host "🔧 RunPod SSH Troubleshooting" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan
Write-Host ""

$runPodIP = "213.173.105.83"
$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"

Write-Host "🔍 Checking SSH setup..." -ForegroundColor Yellow
Write-Host ""

# Check if SSH key exists
if (Test-Path $sshKeyPath) {
    Write-Host "✅ SSH key found at: $sshKeyPath" -ForegroundColor Green
} else {
    Write-Host "❌ SSH key not found at: $sshKeyPath" -ForegroundColor Red
    Write-Host "You need to generate SSH keys first:" -ForegroundColor Yellow
    Write-Host "   ssh-keygen -t ed25519 -C 'your-email@example.com'" -ForegroundColor White
    exit 1
}

# Check if SSH key has been added to agent
Write-Host ""
Write-Host "🔑 Checking SSH agent..." -ForegroundColor Yellow
$sshAgent = Get-Process ssh-agent -ErrorAction SilentlyContinue
if ($sshAgent) {
    Write-Host "✅ SSH agent is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  SSH agent not running" -ForegroundColor Yellow
    Write-Host "Start SSH agent: ssh-agent" -ForegroundColor White
}

# Check SSH config
$sshConfigPath = "$env:USERPROFILE\.ssh\config"
if (Test-Path $sshConfigPath) {
    Write-Host ""
    Write-Host "📄 SSH config found:" -ForegroundColor Yellow
    Get-Content $sshConfigPath | ForEach-Object {
        Write-Host "   $_" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "📄 No SSH config found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 SSH Connection Commands:" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan

Write-Host ""
Write-Host "1️⃣ Try with explicit key:" -ForegroundColor Yellow
Write-Host "   ssh -i $sshKeyPath root@$runPodIP" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣ Add key to SSH agent first:" -ForegroundColor Yellow
Write-Host "   ssh-add $sshKeyPath" -ForegroundColor White
Write-Host "   ssh root@$runPodIP" -ForegroundColor White
Write-Host ""

Write-Host "3️⃣ If key doesn't work, check RunPod web terminal:" -ForegroundColor Yellow
Write-Host "   • Go to RunPod dashboard" -ForegroundColor White
Write-Host "   • Open web terminal for your pod" -ForegroundColor White
Write-Host "   • Run the setup script directly there" -ForegroundColor White
Write-Host ""

Write-Host "4️⃣ Alternative: Copy SSH key to RunPod manually:" -ForegroundColor Yellow
Write-Host "   • Open RunPod web terminal" -ForegroundColor White
Write-Host "   • Run: nano ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "   • Copy your public key: $(Get-Content $sshKeyPath.pub)" -ForegroundColor White
Write-Host "   • Paste and save (Ctrl+X, Y, Enter)" -ForegroundColor White
Write-Host ""

Write-Host "5️⃣ Check your public key:" -ForegroundColor Yellow
if (Test-Path "$sshKeyPath.pub") {
    Write-Host "Your public key:" -ForegroundColor White
    Write-Host "$(Get-Content $sshKeyPath.pub)" -ForegroundColor Gray
} else {
    Write-Host "❌ Public key file not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚨 Emergency Access:" -ForegroundColor Red
Write-Host "If all else fails, use RunPod web terminal in your browser!" -ForegroundColor Red
Write-Host "Go to: RunPod Dashboard → Your Pod → Terminal" -ForegroundColor Red

Write-Host ""
Write-Host "=" * 40 -ForegroundColor Cyan
