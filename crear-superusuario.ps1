# Script para crear superusuario en Cloud Run
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Creando Superusuario en CMMS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Opcion 1: Usar Cloud Shell (Recomendado)" -ForegroundColor Yellow
Write-Host "1. Ir a: https://console.cloud.google.com" -ForegroundColor White
Write-Host "2. Hacer clic en el icono >_ (Cloud Shell)" -ForegroundColor White
Write-Host "3. Ejecutar:" -ForegroundColor White
Write-Host "   gcloud run services proxy cmms-backend --region=us-central1" -ForegroundColor Cyan
Write-Host "4. En otra terminal de Cloud Shell:" -ForegroundColor White
Write-Host "   python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""

Write-Host "Opcion 2: Ejecutar migraciones primero" -ForegroundColor Yellow
Write-Host "Presiona Enter para ejecutar migraciones..." -ForegroundColor White
Read-Host

Write-Host ""
Write-Host "Ejecutando migraciones..." -ForegroundColor Yellow

# Ejecutar comando en Cloud Run para aplicar migraciones
gcloud run jobs create cmms-migrate `
    --image=us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy/cmms-backend `
    --region=us-central1 `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CMMS2025Secure,DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db" `
    --add-cloudsql-instances=argon-edge-478500-i8:us-central1:cmms-db `
    --command="python" `
    --args="manage.py,migrate" `
    --project=argon-edge-478500-i8 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Job de migraciones creado" -ForegroundColor Green
    
    Write-Host "Ejecutando migraciones..." -ForegroundColor White
    gcloud run jobs execute cmms-migrate --region=us-central1 --project=argon-edge-478500-i8 --wait
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Migraciones aplicadas exitosamente" -ForegroundColor Green
    } else {
        Write-Host "Error al ejecutar migraciones" -ForegroundColor Red
    }
} else {
    Write-Host "El job ya existe, ejecutando..." -ForegroundColor Yellow
    gcloud run jobs execute cmms-migrate --region=us-central1 --project=argon-edge-478500-i8 --wait
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Para crear el superusuario, usa Cloud Shell:" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ir a: https://console.cloud.google.com" -ForegroundColor White
Write-Host "2. Abrir Cloud Shell (icono >_)" -ForegroundColor White
Write-Host "3. Ejecutar:" -ForegroundColor White
Write-Host ""
Write-Host "   gcloud run services proxy cmms-backend --region=us-central1" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. En otra terminal:" -ForegroundColor White
Write-Host ""
Write-Host "   python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Email: admin@cmms.com" -ForegroundColor Gray
Write-Host "   Password: (tu contraseña segura)" -ForegroundColor Gray
Write-Host ""
