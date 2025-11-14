@echo off
echo ============================================
echo   GALION BACKEND - RUNPOD DEPLOYMENT
echo   Fixes Cloudflare Error 521 (Backend Only)
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
echo ✓ Directories created
echo.

echo Step 3: Cleaning up existing containers...
docker-compose down 2>nul
docker system prune -f 2>nul
echo ✓ Cleanup completed
echo.

echo Step 4: Building backend only...
echo.

echo Building backend...
docker-compose build backend
if %errorlevel% neq 0 (
    echo ✗ Backend build failed
    exit /b 1
)
echo ✓ Backend built
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
echo Starting monitoring services...
docker-compose up -d prometheus grafana nginx 2>nul

echo.
echo Step 5: Final verification...
echo.

echo Service Status:
docker-compose ps
echo.

echo ============================================
echo   GALION BACKEND DEPLOYED! 🚀
echo ============================================
echo.

echo 🌐 BACKEND ACCESS:
echo.
echo 🔗 Backend API:
echo   http://localhost:8010/docs
echo   http://localhost:8010/health/fast
echo   http://localhost:8010/api/v2/agents/list
echo.

echo 🔧 CLOUDFLARE SETUP (Fix Error 521):
echo 1. Go to Cloudflare Dashboard
echo 2. Update DNS records:
echo    CNAME api.galion.app → [your-runpod-ip]
echo 3. Enable 'Always Use HTTPS'
echo 4. Set SSL to 'Full (strict)'
echo.

echo 📊 MONITORING:
echo   Prometheus: http://localhost:9090
echo   Grafana: http://localhost:3001
echo.

echo "Backend deployed! Now frontend services can connect."
echo.

pause
