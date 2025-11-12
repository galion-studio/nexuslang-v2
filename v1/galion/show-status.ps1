# Show all running apps status
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALL APPS ARE NOW RUNNING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "BACKEND SERVICES (Docker):" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Gray
Write-Host "  PostgreSQL Database     - http://localhost:5432" -ForegroundColor Green
Write-Host "  Redis Cache             - http://localhost:5479" -ForegroundColor Green
Write-Host "  Zookeeper               - Running internally" -ForegroundColor Green
Write-Host "  Kafka Message Queue     - http://localhost:9200" -ForegroundColor Green
Write-Host "  Auth Service            - http://localhost:8100" -ForegroundColor Green
Write-Host "  User Service            - http://localhost:8101" -ForegroundColor Green
Write-Host "  Scraping Service        - http://localhost:8102" -ForegroundColor Green
Write-Host "  Voice Service           - http://localhost:8103" -ForegroundColor Green
Write-Host "  API Gateway (PUBLIC)    - http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Analytics Service       - http://localhost:9302" -ForegroundColor Green
Write-Host "  Kafka UI                - http://localhost:9303" -ForegroundColor Green
Write-Host "  Prometheus              - http://localhost:9301" -ForegroundColor Green
Write-Host "  Grafana Dashboard       - http://localhost:9300" -ForegroundColor Green
Write-Host ""

Write-Host "FRONTEND (Next.js):" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Gray
Write-Host "  Frontend App            - http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "MAIN ACCESS POINTS:" -ForegroundColor Magenta
Write-Host "----------------------------" -ForegroundColor Gray
Write-Host "  Frontend UI:      http://localhost:3000" -ForegroundColor White
Write-Host "  API Gateway:      http://localhost:8080" -ForegroundColor White
Write-Host "  Grafana:          http://localhost:9300" -ForegroundColor White
Write-Host "  Kafka UI:         http://localhost:9303" -ForegroundColor White
Write-Host ""

Write-Host "USEFUL COMMANDS:" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Gray
Write-Host "  View backend logs:   docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "  Check status:        docker-compose ps" -ForegroundColor Gray
Write-Host "  Stop all:            docker-compose down" -ForegroundColor Gray
Write-Host "  Stop frontend:       Press Ctrl+C in the frontend terminal" -ForegroundColor Gray
Write-Host ""

