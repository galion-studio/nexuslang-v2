# ============================================
# V2 Deployment System - Deploy from Laptop
# ============================================
# Simple HTTP-based deployment (no SSH needed!)

param(
    [Parameter(Mandatory=$false)]
    [string]$RunPodIP = "213.173.105.83",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 7000,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("deploy", "status", "logs", "health")]
    [string]$Action = "deploy"
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  V2 DEPLOYMENT SYSTEM" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://${RunPodIP}:${Port}"

switch ($Action) {
    "deploy" {
        Write-Host "🚀 Deploying to RunPod..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/deploy" -Method Post -TimeoutSec 120
            
            if ($response.status -eq "success") {
                Write-Host "✅ Deployment successful!" -ForegroundColor Green
                Write-Host ""
                Write-Host "PM2 Status:" -ForegroundColor Cyan
                Write-Host $response.pm2_status
            } else {
                Write-Host "❌ Deployment failed!" -ForegroundColor Red
                Write-Host $response.message -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Error connecting to RunPod" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            Write-Host ""
            Write-Host "💡 Make sure:" -ForegroundColor Yellow
            Write-Host "   1. Port 7000 is exposed in RunPod dashboard" -ForegroundColor White
            Write-Host "   2. Webhook is running: pm2 status" -ForegroundColor White
        }
    }
    
    "status" {
        Write-Host "📊 Checking service status..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/status" -Method Get
            Write-Host $response.services
        } catch {
            Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "logs" {
        Write-Host "📋 Fetching logs..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/logs?lines=50" -Method Get
            Write-Host $response.logs
        } catch {
            Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "health" {
        Write-Host "🏥 Checking health..." -ForegroundColor Yellow
        Write-Host ""
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
            Write-Host "Status: $($response.status)" -ForegroundColor Green
            Write-Host "Service: $($response.service)"
            Write-Host "Version: $($response.version)"
        } catch {
            Write-Host "❌ Webhook not responding" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

