# Start GALION.STUDIO Alpha (Windows PowerShell)

Write-Host "🚀 Starting GALION.STUDIO Alpha..." -ForegroundColor Cyan
Write-Host ""

# Start backend in new window
Write-Host "📊 Starting backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"

# Wait for backend
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Seed data
Write-Host "🌱 Seeding test data..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/seed" -Method Post
    Write-Host "✅ Data seeded successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not seed data. Backend might not be ready yet." -ForegroundColor Yellow
}

# Start frontend in new window
Write-Host "🎨 Starting frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host ""
Write-Host "✅ GALION.STUDIO is starting!" -ForegroundColor Green
Write-Host "   Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

