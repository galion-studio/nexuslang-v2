# Setup Script for Shopify Integration - pay.galion.studio v2
# This script helps you configure Shopify app credentials

Write-Host "🛒 Shopify App Configuration Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path "../env.template") {
        Copy-Item "../env.template" $envFile
        Write-Host "✅ Created .env file from template" -ForegroundColor Green
    } else {
        Write-Host "❌ No env.template found. Creating basic .env file..." -ForegroundColor Red
        New-Item -Path $envFile -ItemType File -Force | Out-Null
    }
    Write-Host ""
}

Write-Host "📋 Shopify App Information" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Gray
Write-Host "App Name: pay.galion.studio" -ForegroundColor White
Write-Host "Store URL: pay-galion-studio.myshopify.com" -ForegroundColor White
Write-Host "Developer Dashboard: https://partners.shopify.com/" -ForegroundColor Cyan
Write-Host ""

# Function to update or add environment variable
function Set-EnvVariable {
    param (
        [string]$Name,
        [string]$Value,
        [string]$FilePath
    )
    
    $content = Get-Content $FilePath -Raw
    
    # Check if variable exists
    if ($content -match "(?m)^$Name=.*$") {
        # Update existing variable
        $content = $content -replace "(?m)^$Name=.*$", "$Name=$Value"
    } else {
        # Add new variable
        if (-not $content.EndsWith("`n")) {
            $content += "`n"
        }
        $content += "$Name=$Value`n"
    }
    
    Set-Content -Path $FilePath -Value $content -NoNewline
}

Write-Host "🔧 Configuration Steps" -ForegroundColor Cyan
Write-Host ""

# Step 1: Store URL
Write-Host "[1/6] Shopify Store URL" -ForegroundColor Green
Write-Host "Example: pay-galion-studio.myshopify.com" -ForegroundColor Gray
$storeUrl = Read-Host "Enter your Shopify store URL"
if ([string]::IsNullOrWhiteSpace($storeUrl)) {
    $storeUrl = "pay-galion-studio.myshopify.com"
    Write-Host "Using default: $storeUrl" -ForegroundColor Yellow
}
Set-EnvVariable -Name "SHOPIFY_STORE_URL" -Value $storeUrl -FilePath $envFile
Write-Host "✅ Store URL saved" -ForegroundColor Green
Write-Host ""

# Step 2: API Key
Write-Host "[2/6] Shopify API Key" -ForegroundColor Green
Write-Host "Found in: Shopify Partner Dashboard → Apps → pay.galion.studio → App credentials" -ForegroundColor Gray
$apiKey = Read-Host "Enter your Shopify API Key" -MaskInput
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "⚠️  Skipping API Key (you can add it later to .env file)" -ForegroundColor Yellow
    $apiKey = ""
} else {
    Write-Host "✅ API Key saved" -ForegroundColor Green
}
Set-EnvVariable -Name "SHOPIFY_API_KEY" -Value $apiKey -FilePath $envFile
Write-Host ""

# Step 3: API Secret
Write-Host "[3/6] Shopify API Secret" -ForegroundColor Green
Write-Host "Found in: Shopify Partner Dashboard → Apps → pay.galion.studio → App credentials" -ForegroundColor Gray
$apiSecret = Read-Host "Enter your Shopify API Secret" -MaskInput
if ([string]::IsNullOrWhiteSpace($apiSecret)) {
    Write-Host "⚠️  Skipping API Secret (you can add it later to .env file)" -ForegroundColor Yellow
    $apiSecret = ""
} else {
    Write-Host "✅ API Secret saved" -ForegroundColor Green
}
Set-EnvVariable -Name "SHOPIFY_API_SECRET" -Value $apiSecret -FilePath $envFile
Write-Host ""

# Step 4: Access Token
Write-Host "[4/6] Shopify Access Token" -ForegroundColor Green
Write-Host "Generated after installing the app on your store" -ForegroundColor Gray
Write-Host "Starts with: shpat_..." -ForegroundColor Gray
$accessToken = Read-Host "Enter your Shopify Access Token (or skip if not yet installed)" -MaskInput
if ([string]::IsNullOrWhiteSpace($accessToken)) {
    Write-Host "⚠️  Skipping Access Token (add it after installing the app)" -ForegroundColor Yellow
    $accessToken = ""
} else {
    Write-Host "✅ Access Token saved" -ForegroundColor Green
}
Set-EnvVariable -Name "SHOPIFY_ACCESS_TOKEN" -Value $accessToken -FilePath $envFile
Write-Host ""

# Step 5: Webhook Secret
Write-Host "[5/6] Shopify Webhook Secret" -ForegroundColor Green
Write-Host "Found in: Shopify Partner Dashboard → Apps → pay.galion.studio → Webhooks" -ForegroundColor Gray
$webhookSecret = Read-Host "Enter your Webhook Secret (or skip)" -MaskInput
if ([string]::IsNullOrWhiteSpace($webhookSecret)) {
    Write-Host "⚠️  Skipping Webhook Secret (you can add it later)" -ForegroundColor Yellow
    $webhookSecret = ""
} else {
    Write-Host "✅ Webhook Secret saved" -ForegroundColor Green
}
Set-EnvVariable -Name "SHOPIFY_WEBHOOK_SECRET" -Value $webhookSecret -FilePath $envFile
Write-Host ""

# Step 6: App URLs
Write-Host "[6/6] App URLs Configuration" -ForegroundColor Green
Write-Host "These should be set in your Shopify App Dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "App URL:" -ForegroundColor White
Write-Host "  https://pay.galion.studio" -ForegroundColor Cyan
Write-Host ""
Write-Host "Redirect URLs:" -ForegroundColor White
Write-Host "  - https://pay.galion.studio/auth/callback" -ForegroundColor Cyan
Write-Host "  - https://api.galion.studio/shopify/callback" -ForegroundColor Cyan
Write-Host "  - https://pay.galion.studio/billing/confirm" -ForegroundColor Cyan
Write-Host ""
Write-Host "Webhook Endpoint:" -ForegroundColor White
Write-Host "  https://api.galion.studio/webhooks/shopify" -ForegroundColor Cyan
Write-Host ""
Write-Host "Preferences URL (optional):" -ForegroundColor White
Write-Host "  https://docs.galion.studio/pay/shopify-payment-processor" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✅ Configuration Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "📁 Credentials saved to: $envFile" -ForegroundColor Cyan
Write-Host ""

# Check what's missing
$missingItems = @()
if ([string]::IsNullOrWhiteSpace($apiKey)) { $missingItems += "API Key" }
if ([string]::IsNullOrWhiteSpace($apiSecret)) { $missingItems += "API Secret" }
if ([string]::IsNullOrWhiteSpace($accessToken)) { $missingItems += "Access Token" }
if ([string]::IsNullOrWhiteSpace($webhookSecret)) { $missingItems += "Webhook Secret" }

if ($missingItems.Count -gt 0) {
    Write-Host "⚠️  Missing Configuration:" -ForegroundColor Yellow
    foreach ($item in $missingItems) {
        Write-Host "   - $item" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "You can add these later by editing the .env file manually." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure URLs in Shopify Partner Dashboard" -ForegroundColor White
Write-Host "   https://partners.shopify.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Select API scopes (see SHOPIFY_APP_SETUP_V2.md)" -ForegroundColor White
Write-Host ""
Write-Host "3. Configure webhooks:" -ForegroundColor White
Write-Host "   - subscription/created" -ForegroundColor Gray
Write-Host "   - subscription/updated" -ForegroundColor Gray
Write-Host "   - subscription/cancelled" -ForegroundColor Gray
Write-Host "   - orders/paid" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Install app on your test store" -ForegroundColor White
Write-Host ""
Write-Host "5. Restart backend to load new configuration:" -ForegroundColor White
Write-Host "   docker-compose restart backend" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Test the integration!" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed setup instructions, read:" -ForegroundColor Cyan
Write-Host "   SHOPIFY_APP_SETUP_V2.md" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Happy building!" -ForegroundColor Green
Write-Host ""

