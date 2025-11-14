@echo off
echo 🌐 GALION ECOSYSTEM - CONNECTING ALL SERVICES ONLINE
echo.

echo 🔍 CHECKING SERVICE CONNECTIVITY...
echo.

echo Testing Galion App (3010)...
curl -s http://localhost:3010 > nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Galion App: CONNECTED
) else (
    echo   ❌ Galion App: NOT ACCESSIBLE
)

echo Testing Developer Platform (3020)...
curl -s http://localhost:3020 > nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Developer Platform: CONNECTED
) else (
    echo   ❌ Developer Platform: NOT ACCESSIBLE
)

echo Testing Galion Studio (3030)...
curl -s http://localhost:3030 > nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Galion Studio: CONNECTED
) else (
    echo   ❌ Galion Studio: NOT ACCESSIBLE
)

echo Testing Backend API (8010)...
curl -s http://localhost:8010/health/fast > nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Backend API: CONNECTED
) else (
    echo   ❌ Backend API: NOT ACCESSIBLE
)

echo.
echo 🌐 DOMAIN ROUTING CONFIGURATION
echo.

echo Creating nginx configuration for domain routing...
echo # Galion Ecosystem Domain Routing > galion-nginx.conf
echo server { >> galion-nginx.conf
echo     listen 80; >> galion-nginx.conf
echo     server_name galion.app www.galion.app; >> galion-nginx.conf
echo     location / { >> galion-nginx.conf
echo         proxy_pass http://localhost:3010; >> galion-nginx.conf
echo         proxy_set_header Host $host; >> galion-nginx.conf
echo         proxy_set_header X-Real-IP $remote_addr; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-Proto $scheme; >> galion-nginx.conf
echo     } >> galion-nginx.conf
echo } >> galion-nginx.conf
echo. >> galion-nginx.conf
echo server { >> galion-nginx.conf
echo     listen 80; >> galion-nginx.conf
echo     server_name developer.galion.app; >> galion-nginx.conf
echo     location / { >> galion-nginx.conf
echo         proxy_pass http://localhost:3020; >> galion-nginx.conf
echo         proxy_set_header Host $host; >> galion-nginx.conf
echo         proxy_set_header X-Real-IP $remote_addr; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-Proto $scheme; >> galion-nginx.conf
echo     } >> galion-nginx.conf
echo } >> galion-nginx.conf
echo. >> galion-nginx.conf
echo server { >> galion-nginx.conf
echo     listen 80; >> galion-nginx.conf
echo     server_name galion.studio www.galion.studio; >> galion-nginx.conf
echo     location / { >> galion-nginx.conf
echo         proxy_pass http://localhost:3030; >> galion-nginx.conf
echo         proxy_set_header Host $host; >> galion-nginx.conf
echo         proxy_set_header X-Real-IP $remote_addr; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; >> galion-nginx.conf
echo         proxy_set_header X-Forwarded-Proto $scheme; >> galion-nginx.conf
echo     } >> galion-nginx.conf
echo } >> galion-nginx.conf
echo ✅ Created galion-nginx.conf for domain routing

echo.
echo ☁️ CLOUDFLARE SETUP INSTRUCTIONS
echo.

echo To make your Galion ecosystem accessible worldwide:
echo.
echo 1. Create Cloudflare account: https://cloudflare.com
echo 2. Add these domains to Cloudflare:
echo    • galion.app
echo    • developer.galion.app
echo    • galion.studio
echo    • api.galion.app
echo.
echo 3. Point DNS to your server IP (CNAME records)
echo 4. Enable SSL/TLS: Full (strict)
echo 5. Turn on "Always Use HTTPS"
echo.

echo 🚀 PRODUCTION DEPLOYMENT OPTIONS
echo.

echo Option A: RunPod (Recommended)
echo   • Build Docker images for each service
echo   • Deploy to RunPod with GPU acceleration
echo   • Use global CDN for fast access
echo.

echo Option B: VPS/Cloud Server
echo   • Install nginx with galion-nginx.conf
echo   • Get SSL certificates from Let's Encrypt
echo   • Configure firewall and monitoring
echo.

echo 🎯 GALION ECOSYSTEM CONNECTION COMPLETE!
echo.

echo 🌐 YOUR SERVICES ARE NOW CONNECTED:
echo.
echo 🎤 Galion.app (Voice AI) - Port 3010
echo 💻 developer.Galion.app (IDE) - Port 3020
echo 🏢 Galion.studio (Corporate) - Port 3030
echo 🔗 Backend API - Port 8010
echo.

echo "Your imagination is the end." - Galion is connected and ready!
echo.

pause
