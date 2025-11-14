@echo off
echo ============================================
echo   GALION ECOSYSTEM - RUNPOD DEPLOYMENT
echo   Fixes Cloudflare Error 521
echo ============================================
echo.

echo Step 1: Setting up environment...
if not exist ".env" (
    if exist "production.env" (
        copy production.env .env
        echo ✓ Copied production.env to .env
    )
)
echo.

echo Step 2: Creating directories...
mkdir logs 2>nul
mkdir shared 2>nul
mkdir monitoring\prometheus 2>nul
mkdir monitoring\grafana\provisioning 2>nul
echo ✓ Directories created
echo.

echo Step 3: Cleaning up existing containers...
docker-compose down 2>nul
docker system prune -f 2>nul
echo ✓ Cleanup completed
echo.

echo Step 4: Building and deploying services...
echo.

echo Building backend...
docker-compose build backend
if %errorlevel% neq 0 (
    echo ✗ Backend build failed
    exit /b 1
)
echo ✓ Backend built
echo.

echo Building frontend services...
docker-compose build galion-app developer-platform galion-studio
if %errorlevel% neq 0 (
    echo ✗ Frontend build failed
    exit /b 1
)
echo ✓ Frontend services built
echo.

echo Starting infrastructure...
docker-compose up -d postgres redis
timeout /t 10 /nobreak >nul

echo Waiting for PostgreSQL...
for /L %%i in (1,1,30) do (
    docker-compose exec -T postgres pg_isready -U galion -d galion_db >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ PostgreSQL ready
        goto postgres_ready
    )
    echo Waiting for PostgreSQL... (%%i/30)
    timeout /t 2 /nobreak >nul
)
echo ✗ PostgreSQL failed to start
exit /b 1

:postgres_ready
echo Starting backend...
docker-compose up -d backend
timeout /t 5 /nobreak >nul

echo Waiting for backend...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8010/health/fast >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Backend healthy
        goto backend_ready
    )
    echo Waiting for backend... (%%i/30)
    timeout /t 2 /nobreak >nul
)
echo ✗ Backend failed to start
echo Check logs: docker-compose logs backend
exit /b 1

:backend_ready
echo Starting frontend services...
docker-compose up -d galion-app developer-platform galion-studio
timeout /t 5 /nobreak >nul

echo Starting monitoring services...
docker-compose up -d prometheus grafana nginx 2>nul

echo.
echo Step 5: Final verification...
echo.

echo Service Status:
docker-compose ps
echo.

echo ============================================
echo   GALION ECOSYSTEM DEPLOYED! 🚀
echo ============================================
echo.

echo 🌐 ACCESS YOUR GALION ECOSYSTEM:
echo.
echo 🎤 Galion.app (Voice AI):
echo   http://localhost:3010/voice
echo   http://localhost:3010/onboarding
echo.
echo 💻 developer.Galion.app (IDE):
echo   http://localhost:3020/ide
echo.
echo 🏢 Galion.studio (Corporate):
echo   http://localhost:3030
echo.
echo 🔗 Backend API:
echo   http://localhost:8010/docs
echo.

echo 🔧 CLOUDFLARE SETUP (Fix Error 521):
echo 1. Go to Cloudflare Dashboard
echo 2. Update DNS records:
echo    CNAME galion.app → [your-runpod-ip]
echo    CNAME developer.galion.app → [your-runpod-ip]
echo    CNAME galion.studio → [your-runpod-ip]
echo 3. Enable 'Always Use HTTPS'
echo 4. Set SSL to 'Full (strict)'
echo.

echo "Your imagination is the end."
echo.
echo Deployment completed! 🎉
pause
