# PowerShell script for Windows
Write-Host "🚀 Iniciando CMMS System..." -ForegroundColor Green

# Check if .env files exist
if (-not (Test-Path "backend/.env")) {
    Write-Host "📝 Creando backend/.env desde .env.example..." -ForegroundColor Yellow
    Copy-Item "backend/.env.example" "backend/.env"
}

if (-not (Test-Path "frontend/.env")) {
    Write-Host "📝 Creando frontend/.env desde .env.example..." -ForegroundColor Yellow
    Copy-Item "frontend/.env.example" "frontend/.env"
}

# Start Docker Compose
Write-Host "🐳 Iniciando servicios con Docker Compose..." -ForegroundColor Cyan
docker-compose up -d

# Wait for database to be ready
Write-Host "⏳ Esperando a que la base de datos esté lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run migrations
Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Cyan
docker-compose exec -T backend python manage.py migrate

Write-Host "`n✅ Sistema iniciado correctamente!" -ForegroundColor Green
Write-Host "`n📍 URLs disponibles:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000/api/v1/" -ForegroundColor Cyan
Write-Host "   Admin Django: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/api/docs/" -ForegroundColor Cyan
Write-Host "`n💡 Para crear un superusuario, ejecuta:" -ForegroundColor Yellow
Write-Host "   docker-compose exec backend python manage.py createsuperuser" -ForegroundColor White
