# Generate SSH Key for RunPod Access

Write-Host "🔑 Generate SSH Key for RunPod" -ForegroundColor Cyan
Write-Host "=" * 35 -ForegroundColor Cyan
Write-Host ""

$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
$sshPubKeyPath = "$env:USERPROFILE\.ssh\id_ed25519.pub"

# Check if key already exists
if (Test-Path $sshKeyPath) {
    Write-Host "✅ SSH key already exists at: $sshKeyPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your public key:" -ForegroundColor Yellow
    Get-Content $sshPubKeyPath
    Write-Host ""
} else {
    Write-Host "🔄 Generating new SSH key..." -ForegroundColor Yellow
    Write-Host ""

    # Generate SSH key
    ssh-keygen -t ed25519 -C "info@galion.studio" -f $sshKeyPath -N '""'

    if (Test-Path $sshPubKeyPath) {
        Write-Host "✅ SSH key generated successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your public key (copy this to RunPod):" -ForegroundColor Yellow
        Write-Host "=" * 50 -ForegroundColor Yellow
        Get-Content $sshPubKeyPath
        Write-Host "=" * 50 -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "❌ Failed to generate SSH key" -ForegroundColor Red
        exit 1
    }
}

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy the public key above" -ForegroundColor White
Write-Host "2. Go to RunPod web terminal" -ForegroundColor White
Write-Host "3. Run: nano ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "4. Paste the key and save (Ctrl+X, Y, Enter)" -ForegroundColor White
Write-Host "5. Try SSH: ssh -i $sshKeyPath root@213.173.105.83" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Alternative: Just use RunPod web terminal!" -ForegroundColor Green
Write-Host "RunPod Dashboard → Your Pod → Terminal → Run setup script" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 35 -ForegroundColor Cyan
