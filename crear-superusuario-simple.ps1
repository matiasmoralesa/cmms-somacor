# Script Simple para Crear Superusuario
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Creando Superusuario" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$backendUrl = "https://cmms-backend-4qfhh2wkzq-uc.a.run.app"

Write-Host "Creando Cloud Run Job para crear superusuario..." -ForegroundColor Yellow
Write-Host ""

# Crear job
$jobName = "create-superuser"

# Primero intentar eliminar si existe
gcloud run jobs delete $jobName --region=us-central1 --project=argon-edge-478500-i8 --quiet 2>$null

Write-Host "Creando job..." -ForegroundColor White

$command = "python"
$args = "manage.py,shell,-c,from django.contrib.auth import get_user_model; User = get_user_model(); print('Usuario ya existe') if User.objects.filter(email='admin@cmms.com').exists() else (User.objects.create_superuser('admin@cmms.com', 'admin@cmms.com', 'Admin123!'), print('Superusuario creado'))"

gcloud run jobs create $jobName --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend/cmms-backend --region=us-central1 --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db" --add-cloudsql-instances=argon-edge-478500-i8:us-central1:cmms-db --command=$command --args=$args --project=argon-edge-478500-i8

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Job creado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ejecutando job..." -ForegroundColor White
    
    gcloud run jobs execute $jobName --region=us-central1 --project=argon-edge-478500-i8 --wait
    
    Write-Host ""
    Write-Host "✓ Job ejecutado" -ForegroundColor Green
} else {
    Write-Host "⚠ El job puede que ya exista, intentando ejecutar..." -ForegroundColor Yellow
    gcloud run jobs execute $jobName --region=us-central1 --project=argon-edge-478500-i8 --wait
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Verificando login..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$loginBody = @{
    email = "admin@cmms.com"
    password = "Admin123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    
    Write-Host "✓ ¡LOGIN EXITOSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Credenciales verificadas:" -ForegroundColor Cyan
    Write-Host "  Email: admin@cmms.com" -ForegroundColor White
    Write-Host "  Password: Admin123!" -ForegroundColor White
    Write-Host ""
    Write-Host "Usuario: $($loginResponse.user.email)" -ForegroundColor White
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "     ¡Superusuario Creado Exitosamente!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora puedes:" -ForegroundColor Cyan
    Write-Host "  1. Ejecutar: .\probar-modelo-ia.ps1" -ForegroundColor White
    Write-Host "  2. Ir a: $backendUrl/api/docs/" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "✗ Login falló" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Puede que necesites crear el usuario manualmente en Cloud Shell" -ForegroundColor Yellow
    Write-Host "Comando: gcloud sql connect cmms-db --user=cmms_user --database=cmms_prod" -ForegroundColor Cyan
}
