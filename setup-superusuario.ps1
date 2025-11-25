# Script para configurar superusuario
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Configurando Superusuario en CMMS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$backendUrl = "https://cmms-backend-4qfhh2wkzq-uc.a.run.app"
$connectionName = "argon-edge-478500-i8:us-central1:cmms-db"

Write-Host "Paso 1: Aplicando migraciones a la base de datos..." -ForegroundColor Yellow
Write-Host ""

# Crear job para migraciones si no existe
Write-Host "Creando job de migraciones..." -ForegroundColor White

gcloud run jobs create cmms-migrate `
    --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend/cmms-backend `
    --region=us-central1 `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/$connectionName" `
    --add-cloudsql-instances=$connectionName `
    --command="python" `
    --args="manage.py,migrate" `
    --project=argon-edge-478500-i8 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "El job ya existe, continuando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Ejecutando migraciones..." -ForegroundColor White
gcloud run jobs execute cmms-migrate --region=us-central1 --project=argon-edge-478500-i8 --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migraciones aplicadas exitosamente" -ForegroundColor Green
} else {
    Write-Host "Advertencia: Puede que las migraciones ya esten aplicadas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 2: Crear Superusuario" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Para crear el superusuario, necesitas usar Cloud Shell." -ForegroundColor White
Write-Host "Sigue estos pasos:" -ForegroundColor White
Write-Host ""

Write-Host "1. Abre Cloud Shell:" -ForegroundColor Yellow
Write-Host "   https://console.cloud.google.com/?cloudshell=true" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. En Cloud Shell, ejecuta este comando:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   gcloud run services proxy cmms-backend --region=us-central1 --project=argon-edge-478500-i8" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Abre OTRA terminal de Cloud Shell (clic en el icono +)" -ForegroundColor Yellow
Write-Host ""

Write-Host "4. En la nueva terminal, ejecuta:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   cd /tmp" -ForegroundColor Cyan
Write-Host "   git clone https://github.com/tu-repo/cmms.git || echo 'Usando codigo del contenedor'" -ForegroundColor Cyan
Write-Host "   python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Ingresa los datos del superusuario:" -ForegroundColor Yellow
Write-Host "   Email: admin@cmms.com" -ForegroundColor Gray
Write-Host "   Password: (tu contraseña segura)" -ForegroundColor Gray
Write-Host "   Password (again): (repetir contraseña)" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Green
Write-Host "Alternativa: Crear superusuario via API" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Presiona Enter para abrir Cloud Shell en tu navegador..." -ForegroundColor Yellow
Read-Host

Start-Process "https://console.cloud.google.com/?cloudshell=true&project=argon-edge-478500-i8"

Write-Host ""
Write-Host "Cloud Shell abierto en tu navegador" -ForegroundColor Green
Write-Host ""
Write-Host "Copia y pega estos comandos en Cloud Shell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Terminal 1:" -ForegroundColor Cyan
Write-Host "gcloud run services proxy cmms-backend --region=us-central1" -ForegroundColor White
Write-Host ""
Write-Host "# Terminal 2 (nueva terminal con +):" -ForegroundColor Cyan
Write-Host "python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
