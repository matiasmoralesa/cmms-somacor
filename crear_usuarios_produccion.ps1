# Script para crear usuarios de prueba en producción
# Ejecuta el comando de management en Cloud Run

Write-Host "=== Creando Usuarios de Prueba en Producción ===" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "argon-edge-478500-i8"
$SERVICE_NAME = "cmms-backend"
$REGION = "us-central1"

Write-Host "Proyecto: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Servicio: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "Región: $REGION" -ForegroundColor Yellow
Write-Host ""

# Ejecutar comando en Cloud Run
Write-Host "Ejecutando comando create_test_users..." -ForegroundColor Cyan

gcloud run jobs create create-users `
    --image=gcr.io/$PROJECT_ID/$SERVICE_NAME `
    --region=$REGION `
    --command="python" `
    --args="manage.py,create_test_users" `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production" `
    --execute-now

Write-Host ""
Write-Host "=== Usuarios Creados ===" -ForegroundColor Green
Write-Host ""
Write-Host "Admin:      admin@cmms.com / admin123" -ForegroundColor White
Write-Host "Manager:    manager@cmms.com / manager123" -ForegroundColor White
Write-Host "Technician: tech@cmms.com / tech123" -ForegroundColor White
Write-Host "Operator:   operator@cmms.com / operator123" -ForegroundColor White
Write-Host ""
Write-Host "Puedes usar cualquiera de estas credenciales para iniciar sesión en:" -ForegroundColor Cyan
Write-Host "https://cmms-somacor-prod.web.app" -ForegroundColor Yellow
Write-Host ""
