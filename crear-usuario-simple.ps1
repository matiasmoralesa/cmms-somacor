# Script Simple para Crear Superusuario
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Creando Superusuario - Metodo Simple" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$connectionName = "argon-edge-478500-i8:us-central1:cmms-db"

Write-Host "Paso 1: Aplicando migraciones..." -ForegroundColor Yellow

# Ejecutar migraciones
gcloud run jobs execute cmms-migrate --region=us-central1 --project=argon-edge-478500-i8 --wait 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migraciones aplicadas" -ForegroundColor Green
} else {
    Write-Host "Creando job de migraciones..." -ForegroundColor Yellow
    
    gcloud run jobs create cmms-migrate `
        --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend/cmms-backend `
        --region=us-central1 `
        --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/$connectionName" `
        --add-cloudsql-instances=$connectionName `
        --command="python" `
        --args="manage.py,migrate" `
        --project=argon-edge-478500-i8
    
    Write-Host "Ejecutando migraciones..." -ForegroundColor White
    gcloud run jobs execute cmms-migrate --region=us-central1 --project=argon-edge-478500-i8 --wait
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 2: Crear Superusuario" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ingresa los datos del superusuario:" -ForegroundColor White
Write-Host ""

$email = Read-Host "Email (ejemplo: admin@cmms.com)"
$password = Read-Host "Password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Write-Host ""
Write-Host "Creando superusuario..." -ForegroundColor Yellow

# Crear script Python para crear superusuario
$createUserScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$email').exists():
    User.objects.create_superuser('$email', '$email', '$passwordPlain')
    print('Superusuario creado exitosamente')
else:
    print('El usuario ya existe')
"@

# Guardar script temporalmente
$createUserScript | Out-File -FilePath "create_superuser.py" -Encoding UTF8

Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "IMPORTANTE: Necesitas ejecutar esto en Cloud Shell" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Abre Cloud Shell: https://console.cloud.google.com/?cloudshell=true" -ForegroundColor White
Write-Host ""
Write-Host "2. Ejecuta estos comandos:" -ForegroundColor White
Write-Host ""
Write-Host "cat > create_superuser.py << 'EOF'" -ForegroundColor Cyan
Write-Host $createUserScript -ForegroundColor Gray
Write-Host "EOF" -ForegroundColor Cyan
Write-Host ""
Write-Host "gcloud run jobs create create-superuser --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend/cmms-backend --region=us-central1 --set-env-vars=DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/$connectionName --add-cloudsql-instances=$connectionName --command=python --args=create_superuser.py --project=argon-edge-478500-i8" -ForegroundColor Cyan
Write-Host ""
Write-Host "gcloud run jobs execute create-superuser --region=us-central1 --wait" -ForegroundColor Cyan
Write-Host ""

Write-Host "Presiona Enter para abrir Cloud Shell..." -ForegroundColor Yellow
Read-Host

Start-Process "https://console.cloud.google.com/?cloudshell=true&project=argon-edge-478500-i8"

Write-Host ""
Write-Host "Cloud Shell abierto. Copia y pega los comandos de arriba." -ForegroundColor Green
Write-Host ""
Write-Host "Credenciales guardadas:" -ForegroundColor Cyan
Write-Host "  Email: $email" -ForegroundColor White
Write-Host "  Password: ********" -ForegroundColor White
Write-Host ""
