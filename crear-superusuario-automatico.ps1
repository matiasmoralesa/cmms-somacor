# Script Automático para Crear Superusuario
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Creando Superusuario Automáticamente" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$backendUrl = "https://cmms-backend-4qfhh2wkzq-uc.a.run.app"

Write-Host "Método: Usando Django Management Command via Cloud Run" -ForegroundColor Yellow
Write-Host ""

# Crear script Python para crear superusuario
$createUserScript = @'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = 'admin@cmms.com'
password = 'Admin123!'

if User.objects.filter(email=email).exists():
    print(f'Usuario {email} ya existe')
else:
    User.objects.create_superuser(email, email, password)
    print(f'Superusuario {email} creado exitosamente!')
'@

Write-Host "Guardando script..." -ForegroundColor White
$createUserScript | Out-File -FilePath "create_superuser_temp.py" -Encoding UTF8

Write-Host "✓ Script creado" -ForegroundColor Green
Write-Host ""

Write-Host "Ejecutando creación de superusuario..." -ForegroundColor Yellow
Write-Host ""

# Crear job en Cloud Run para ejecutar el script
$jobName = "create-superuser-$(Get-Random -Maximum 9999)"

Write-Host "Creando Cloud Run Job..." -ForegroundColor White

gcloud run jobs create $jobName `
    --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend/cmms-backend `
    --region=us-central1 `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db" `
    --add-cloudsql-instances=argon-edge-478500-i8:us-central1:cmms-db `
    --command="python" `
    --args="manage.py,shell,-c,from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@cmms.com').exists() or User.objects.create_superuser('admin@cmms.com', 'admin@cmms.com', 'Admin123!')" `
    --project=argon-edge-478500-i8 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Job creado" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Ejecutando job..." -ForegroundColor White
    
    gcloud run jobs execute $jobName --region=us-central1 --project=argon-edge-478500-i8 --wait
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Superusuario creado exitosamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Credenciales:" -ForegroundColor Cyan
        Write-Host "  Email: admin@cmms.com" -ForegroundColor White
        Write-Host "  Password: Admin123!" -ForegroundColor White
        Write-Host ""
        
        # Limpiar job
        Write-Host "Limpiando job temporal..." -ForegroundColor Gray
        gcloud run jobs delete $jobName --region=us-central1 --project=argon-edge-478500-i8 --quiet 2>$null
        
    } else {
        Write-Host "✗ Error ejecutando job" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Error creando job" -ForegroundColor Red
}

# Limpiar archivo temporal
Remove-Item "create_superuser_temp.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "Verificando creación..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Probando login..." -ForegroundColor White

$loginBody = @{
    email = "admin@cmms.com"
    password = "Admin123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    
    Write-Host "✓ Login exitoso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usuario: $($loginResponse.user.email)" -ForegroundColor White
    Write-Host "Token generado: $($loginResponse.access.Substring(0,50))..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "     Superusuario Creado y Verificado" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora puedes ejecutar: .\probar-modelo-ia.ps1" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "⚠ No se pudo verificar el login" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Intenta crear el usuario manualmente en Cloud Shell" -ForegroundColor Yellow
}
