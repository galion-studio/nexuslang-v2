# Admin Control Script for Content Management System
# Run from local machine (Windows PowerShell) to manage RunPod deployment

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "menu",
    
    [Parameter(Mandatory=$false)]
    [string]$RunPodHost = $env:RUNPOD_HOST,
    
    [Parameter(Mandatory=$false)]
    [string]$RunPodPort = $env:RUNPOD_PORT
)

# Configuration
$SSH_USER = "nexus-admin"
$PROJECT_PATH = "/home/nexus-admin/project-nexus/v2"

function Show-Menu {
    Write-Host "`n=== Content Manager Admin Control ===" -ForegroundColor Cyan
    Write-Host "1.  Deploy/Update System"
    Write-Host "2.  View Logs"
    Write-Host "3.  Restart Services"
    Write-Host "4.  Database Shell"
    Write-Host "5.  Run Migration"
    Write-Host "6.  Backup Database"
    Write-Host "7.  View Service Status"
    Write-Host "8.  Test API"
    Write-Host "9.  Open SSH Tunnel"
    Write-Host "10. Sync Analytics"
    Write-Host "11. Process Scheduled Jobs"
    Write-Host "12. View Upcoming Posts"
    Write-Host "Q.  Quit"
    Write-Host "======================================`n" -ForegroundColor Cyan
}

function Invoke-RemoteCommand {
    param([string]$Command)
    
    if (-not $RunPodHost -or -not $RunPodPort) {
        Write-Host "Error: RUNPOD_HOST and RUNPOD_PORT must be set" -ForegroundColor Red
        Write-Host "Set them as environment variables or pass as parameters" -ForegroundColor Yellow
        exit 1
    }
    
    ssh -p $RunPodPort "$SSH_USER@$RunPodHost" $Command
}

function Deploy-System {
    Write-Host "`nDeploying system..." -ForegroundColor Green
    
    $deployScript = @"
cd $PROJECT_PATH
git pull origin main
docker-compose -f docker-compose.nexuslang.yml pull
docker-compose -f docker-compose.nexuslang.yml up -d
docker-compose -f docker-compose.nexuslang.yml exec -T backend python -c 'print(\"Backend is healthy\")'
"@
    
    Invoke-RemoteCommand $deployScript
    Write-Host "Deployment complete!" -ForegroundColor Green
}

function View-Logs {
    Write-Host "`nFetching logs (Ctrl+C to stop)..." -ForegroundColor Green
    Invoke-RemoteCommand "cd $PROJECT_PATH && docker-compose logs -f --tail=100"
}

function Restart-Services {
    Write-Host "`nRestarting services..." -ForegroundColor Green
    Invoke-RemoteCommand "cd $PROJECT_PATH && docker-compose restart"
    Write-Host "Services restarted!" -ForegroundColor Green
}

function Open-DatabaseShell {
    Write-Host "`nOpening database shell..." -ForegroundColor Green
    Invoke-RemoteCommand "cd $PROJECT_PATH && docker-compose exec postgres psql -U nexuslang nexuslang_v2"
}

function Run-Migration {
    Write-Host "`nRunning content manager migration..." -ForegroundColor Green
    
    $migrationCommand = @"
cd $PROJECT_PATH
docker-compose exec -T postgres psql -U nexuslang nexuslang_v2 -f /app/database/migrations/003_content_manager.sql
"@
    
    Invoke-RemoteCommand $migrationCommand
    Write-Host "Migration complete!" -ForegroundColor Green
}

function Backup-Database {
    Write-Host "`nCreating database backup..." -ForegroundColor Green
    
    $date = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_$date.sql.gz"
    
    $backupCommand = @"
cd $PROJECT_PATH
docker-compose exec -T postgres pg_dump -U nexuslang nexuslang_v2 | gzip > ~/backups/$backupFile
echo 'Backup created: ~/backups/$backupFile'
"@
    
    Invoke-RemoteCommand $backupCommand
    
    # Optionally download backup
    $download = Read-Host "Download backup to local machine? (y/n)"
    if ($download -eq "y") {
        scp -P $RunPodPort "$SSH_USER@${RunPodHost}:~/backups/$backupFile" "./backups/"
        Write-Host "Backup downloaded to ./backups/$backupFile" -ForegroundColor Green
    }
}

function Show-ServiceStatus {
    Write-Host "`nService Status:" -ForegroundColor Green
    Invoke-RemoteCommand "cd $PROJECT_PATH && docker-compose ps"
}

function Test-API {
    Write-Host "`nTesting API endpoints..." -ForegroundColor Green
    
    # Get RunPod IP for API testing
    $apiUrl = Read-Host "Enter API URL (default: http://$RunPodHost:8100)"
    if (-not $apiUrl) {
        $apiUrl = "http://$RunPodHost:8100"
    }
    
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    curl "$apiUrl/health"
    
    Write-Host "`nTesting content manager..." -ForegroundColor Yellow
    Write-Host "Note: Requires authentication token" -ForegroundColor Gray
}

function Open-SSHTunnel {
    Write-Host "`nOpening SSH tunnel..." -ForegroundColor Green
    Write-Host "Local ports will be forwarded:" -ForegroundColor Yellow
    Write-Host "  localhost:5432 -> PostgreSQL" -ForegroundColor Gray
    Write-Host "  localhost:6379 -> Redis" -ForegroundColor Gray
    Write-Host "  localhost:8100 -> Backend API" -ForegroundColor Gray
    Write-Host "  localhost:3100 -> Frontend" -ForegroundColor Gray
    Write-Host "`nPress Ctrl+C to close tunnel`n" -ForegroundColor Yellow
    
    ssh -L 5432:localhost:5432 `
        -L 6379:localhost:6379 `
        -L 8100:localhost:8100 `
        -L 3100:localhost:3100 `
        -p $RunPodPort "$SSH_USER@$RunPodHost"
}

function Sync-Analytics {
    Write-Host "`nSyncing analytics..." -ForegroundColor Green
    
    $syncCommand = @"
cd $PROJECT_PATH
docker-compose exec -T backend python -c '
import asyncio
from core.database import get_db
from services.social.analytics_service import AnalyticsService

async def sync():
    async for db in get_db():
        service = AnalyticsService(db)
        results = await service.sync_all_recent_posts(days=7)
        print(f\"Synced {results[\"successful\"]} posts successfully\")
        break

asyncio.run(sync())
'
"@
    
    Invoke-RemoteCommand $syncCommand
    Write-Host "Analytics sync complete!" -ForegroundColor Green
}

function Process-ScheduledJobs {
    Write-Host "`nProcessing scheduled jobs..." -ForegroundColor Green
    
    $jobsCommand = @"
cd $PROJECT_PATH
docker-compose exec -T backend python -c '
import asyncio
from core.database import get_db
from services.social.scheduling_service import SchedulingService

async def process():
    async for db in get_db():
        service = SchedulingService(db)
        results = await service.process_due_jobs()
        print(f\"Processed {results[\"total\"]} jobs: {results[\"successful\"]} successful, {results[\"failed\"]} failed\")
        break

asyncio.run(process())
'
"@
    
    Invoke-RemoteCommand $jobsCommand
    Write-Host "Job processing complete!" -ForegroundColor Green
}

function View-UpcomingPosts {
    Write-Host "`nFetching upcoming scheduled posts..." -ForegroundColor Green
    
    $postsCommand = @"
cd $PROJECT_PATH
docker-compose exec -T postgres psql -U nexuslang nexuslang_v2 -c \"
SELECT 
    cp.title,
    b.name as brand,
    cp.status,
    cp.scheduled_at,
    cp.platforms
FROM content_posts cp
JOIN brands b ON cp.brand_id = b.id
WHERE cp.status = 'scheduled'
ORDER BY cp.scheduled_at
LIMIT 10;
\"
"@
    
    Invoke-RemoteCommand $postsCommand
}

# Main execution
if ($Action -eq "menu") {
    do {
        Show-Menu
        $choice = Read-Host "Select option"
        
        switch ($choice) {
            "1" { Deploy-System }
            "2" { View-Logs }
            "3" { Restart-Services }
            "4" { Open-DatabaseShell }
            "5" { Run-Migration }
            "6" { Backup-Database }
            "7" { Show-ServiceStatus }
            "8" { Test-API }
            "9" { Open-SSHTunnel }
            "10" { Sync-Analytics }
            "11" { Process-ScheduledJobs }
            "12" { View-UpcomingPosts }
            "Q" { Write-Host "Goodbye!" -ForegroundColor Cyan; exit }
            default { Write-Host "Invalid option" -ForegroundColor Red }
        }
        
        if ($choice -ne "Q") {
            Read-Host "`nPress Enter to continue"
        }
    } while ($choice -ne "Q")
} else {
    # Direct command execution
    switch ($Action.ToLower()) {
        "deploy" { Deploy-System }
        "logs" { View-Logs }
        "restart" { Restart-Services }
        "db" { Open-DatabaseShell }
        "migrate" { Run-Migration }
        "backup" { Backup-Database }
        "status" { Show-ServiceStatus }
        "test" { Test-API }
        "tunnel" { Open-SSHTunnel }
        "sync" { Sync-Analytics }
        "jobs" { Process-ScheduledJobs }
        "upcoming" { View-UpcomingPosts }
        default { Write-Host "Unknown action: $Action" -ForegroundColor Red }
    }
}

