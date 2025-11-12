# PowerShell Script to Install Cloudflare Origin Certificates
# Fixes: ERR_SSL_VERSION_OR_CIPHER_MISMATCH error
# Usage: Run as Administrator

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: Please run this script as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Cloudflare Origin Certificate Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you install Cloudflare Origin Certificates" -ForegroundColor White
Write-Host "to fix the SSL error on api.developer.galion.app" -ForegroundColor White
Write-Host ""

# Determine if this is for local testing or server deployment
Write-Host "Where are you installing?" -ForegroundColor Yellow
Write-Host "1. Local Windows (for testing)" -ForegroundColor White
Write-Host "2. Remote Linux Server (via SSH)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice (1 or 2)"

if ($choice -eq "1") {
    # Local Windows installation
    Write-Host ""
    Write-Host "Step 1: Creating certificate directory..." -ForegroundColor Green
    $certDir = "C:\nginx\certs"
    if (-not (Test-Path $certDir)) {
        New-Item -Path $certDir -ItemType Directory -Force | Out-Null
    }
    Write-Host "✅ Directory created: $certDir" -ForegroundColor Green
    Write-Host ""

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Step 2: Get Your Cloudflare Origin Certificate" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Open: https://dash.cloudflare.com/" -ForegroundColor White
    Write-Host "2. Select your 'galion.app' domain" -ForegroundColor White
    Write-Host "3. Go to: SSL/TLS → Origin Server" -ForegroundColor White
    Write-Host "4. Click: 'Create Certificate'" -ForegroundColor White
    Write-Host "5. Add hostnames:" -ForegroundColor White
    Write-Host "   - developer.galion.app" -ForegroundColor Gray
    Write-Host "   - api.developer.galion.app" -ForegroundColor Gray
    Write-Host "   - *.developer.galion.app" -ForegroundColor Gray
    Write-Host "6. Set validity: 15 years" -ForegroundColor White
    Write-Host "7. Click 'Create'" -ForegroundColor White
    Write-Host ""
    Write-Host "Press ENTER when you have the certificate and key ready..." -ForegroundColor Yellow
    Read-Host

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Step 3: Install Certificate" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    $certFile = "$certDir\developer.galion.app.pem"
    Write-Host "Opening Notepad for CERTIFICATE..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
    Write-Host "1. Copy the CERTIFICATE from Cloudflare" -ForegroundColor White
    Write-Host "   (starts with -----BEGIN CERTIFICATE-----)" -ForegroundColor Gray
    Write-Host "2. Paste it into Notepad" -ForegroundColor White
    Write-Host "3. Save and close Notepad" -ForegroundColor White
    Write-Host ""
    Write-Host "Press ENTER to open Notepad..." -ForegroundColor Yellow
    Read-Host
    
    notepad $certFile
    
    if (-not (Test-Path $certFile)) {
        Write-Host "❌ ERROR: Certificate file not saved!" -ForegroundColor Red
        pause
        exit
    }
    
    Write-Host "✅ Certificate saved!" -ForegroundColor Green
    Write-Host ""

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Step 4: Install Private Key" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    $keyFile = "$certDir\developer.galion.app.key"
    Write-Host "Opening Notepad for PRIVATE KEY..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
    Write-Host "1. Copy the PRIVATE KEY from Cloudflare" -ForegroundColor White
    Write-Host "   (starts with -----BEGIN PRIVATE KEY-----)" -ForegroundColor Gray
    Write-Host "2. Paste it into Notepad" -ForegroundColor White
    Write-Host "3. Save and close Notepad" -ForegroundColor White
    Write-Host ""
    Write-Host "Press ENTER to open Notepad..." -ForegroundColor Yellow
    Read-Host
    
    notepad $keyFile
    
    if (-not (Test-Path $keyFile)) {
        Write-Host "❌ ERROR: Private key file not saved!" -ForegroundColor Red
        pause
        exit
    }
    
    Write-Host "✅ Private key saved!" -ForegroundColor Green
    Write-Host ""

    Write-Host "Step 5: Verifying certificate files..." -ForegroundColor Green
    
    if ((Get-Item $certFile).Length -eq 0) {
        Write-Host "❌ ERROR: Certificate file is empty!" -ForegroundColor Red
        pause
        exit
    }
    
    if ((Get-Item $keyFile).Length -eq 0) {
        Write-Host "❌ ERROR: Private key file is empty!" -ForegroundColor Red
        pause
        exit
    }
    
    Write-Host "✅ Certificate files verified" -ForegroundColor Green
    Write-Host ""

    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "✅ INSTALLATION COMPLETE (Local)" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Certificate files saved to:" -ForegroundColor White
    Write-Host "  Certificate: $certFile" -ForegroundColor Gray
    Write-Host "  Private Key: $keyFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Update your nginx configuration to use these certificates" -ForegroundColor White
    Write-Host "2. Configure nginx with these paths:" -ForegroundColor White
    Write-Host "   ssl_certificate C:/nginx/certs/developer.galion.app.pem;" -ForegroundColor Gray
    Write-Host "   ssl_certificate_key C:/nginx/certs/developer.galion.app.key;" -ForegroundColor Gray
    Write-Host ""

} elseif ($choice -eq "2") {
    # Remote Linux Server installation
    Write-Host ""
    Write-Host "Remote Server Installation" -ForegroundColor Cyan
    Write-Host ""
    
    $serverIP = Read-Host "Enter your server IP address"
    $serverUser = Read-Host "Enter your server username (e.g., root)"
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Step 1: Get Your Cloudflare Origin Certificate" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Open: https://dash.cloudflare.com/" -ForegroundColor White
    Write-Host "2. Select your 'galion.app' domain" -ForegroundColor White
    Write-Host "3. Go to: SSL/TLS → Origin Server" -ForegroundColor White
    Write-Host "4. Click: 'Create Certificate'" -ForegroundColor White
    Write-Host "5. Add hostnames:" -ForegroundColor White
    Write-Host "   - developer.galion.app" -ForegroundColor Gray
    Write-Host "   - api.developer.galion.app" -ForegroundColor Gray
    Write-Host "   - *.developer.galion.app" -ForegroundColor Gray
    Write-Host "6. Set validity: 15 years" -ForegroundColor White
    Write-Host "7. Click 'Create'" -ForegroundColor White
    Write-Host ""
    Write-Host "Press ENTER when you have the certificate and key ready..." -ForegroundColor Yellow
    Read-Host

    Write-Host ""
    Write-Host "Step 2: Saving certificates temporarily..." -ForegroundColor Green
    
    # Save to temp directory
    $tempDir = "$env:TEMP\cloudflare-certs"
    if (-not (Test-Path $tempDir)) {
        New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
    }
    
    $tempCert = "$tempDir\developer.galion.app.pem"
    $tempKey = "$tempDir\developer.galion.app.key"
    
    Write-Host "Opening Notepad for CERTIFICATE..." -ForegroundColor Yellow
    Write-Host "Paste the certificate and save" -ForegroundColor White
    Read-Host "Press ENTER to open Notepad"
    notepad $tempCert
    
    Write-Host "Opening Notepad for PRIVATE KEY..." -ForegroundColor Yellow
    Write-Host "Paste the private key and save" -ForegroundColor White
    Read-Host "Press ENTER to open Notepad"
    notepad $tempKey
    
    Write-Host ""
    Write-Host "Step 3: Uploading to server..." -ForegroundColor Green
    Write-Host ""
    Write-Host "Copy these commands and run them on your server:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "# SSH into your server" -ForegroundColor Gray
    Write-Host "ssh $serverUser@$serverIP" -ForegroundColor White
    Write-Host ""
    Write-Host "# Download and run the installation script" -ForegroundColor Gray
    Write-Host "sudo bash install-cloudflare-certs.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "OR manually:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "# Create directory" -ForegroundColor Gray
    Write-Host "sudo mkdir -p /etc/cloudflare/certs" -ForegroundColor White
    Write-Host ""
    Write-Host "# Create certificate file" -ForegroundColor Gray
    Write-Host "sudo nano /etc/cloudflare/certs/developer.galion.app.pem" -ForegroundColor White
    Write-Host "# Paste certificate, Ctrl+X, Y, Enter" -ForegroundColor Gray
    Write-Host ""
    Write-Host "# Create private key file" -ForegroundColor Gray
    Write-Host "sudo nano /etc/cloudflare/certs/developer.galion.app.key" -ForegroundColor White
    Write-Host "# Paste private key, Ctrl+X, Y, Enter" -ForegroundColor Gray
    Write-Host ""
    Write-Host "# Set permissions" -ForegroundColor Gray
    Write-Host "sudo chmod 600 /etc/cloudflare/certs/developer.galion.app.key" -ForegroundColor White
    Write-Host "sudo chmod 644 /etc/cloudflare/certs/developer.galion.app.pem" -ForegroundColor White
    Write-Host ""
    Write-Host "# Test and restart nginx" -ForegroundColor Gray
    Write-Host "sudo nginx -t" -ForegroundColor White
    Write-Host "sudo systemctl restart nginx" -ForegroundColor White
    Write-Host ""
    Write-Host "Certificate files are saved in: $tempDir" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "❌ Invalid choice!" -ForegroundColor Red
    pause
    exit
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Important: Cloudflare Settings" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure these settings are configured in Cloudflare:" -ForegroundColor White
Write-Host ""
Write-Host "SSL/TLS Settings:" -ForegroundColor Yellow
Write-Host "  1. SSL/TLS encryption mode: Full (strict)" -ForegroundColor White
Write-Host "  2. Always Use HTTPS: ON" -ForegroundColor White
Write-Host "  3. Minimum TLS Version: TLS 1.2" -ForegroundColor White
Write-Host "  4. Automatic HTTPS Rewrites: ON" -ForegroundColor White
Write-Host ""
Write-Host "DNS Settings:" -ForegroundColor Yellow
Write-Host "  - developer.galion.app → Proxied (🟠 orange cloud)" -ForegroundColor White
Write-Host "  - api.developer.galion.app → Proxied (🟠 orange cloud)" -ForegroundColor White
Write-Host ""
Write-Host "For detailed troubleshooting, see: FIX_SSL_ERROR.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
Write-Host ""
pause

