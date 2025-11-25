# Script para cargar datos de demostración en el sistema CMMS
# Este script ejecuta el comando de management en Cloud Run

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Cargando Datos de Demostración" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Este proceso cargará:" -ForegroundColor Yellow
Write-Host "  • Roles y usuarios de ejemplo" -ForegroundColor White
Write-Host "  • Ubicaciones y activos" -ForegroundColor White
Write-Host "  • Repuestos e inventario" -ForegroundColor White
Write-Host "  • Planes de mantenimiento" -ForegroundColor White
Write-Host "  • Plantillas de checklists" -ForegroundColor White
Write-Host "  • 12 meses de datos históricos" -ForegroundColor White
Write-Host "  • Órdenes de trabajo completadas" -ForegroundColor White
Write-Host "  • Checklists históricos`n" -ForegroundColor White

$confirm = Read-Host "¿Deseas continuar? (S/N)"

if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "`nOperación cancelada." -ForegroundColor Yellow
    exit
}

Write-Host "`n🚀 Iniciando carga de datos..." -ForegroundColor Green

# Ejecutar el comando en Cloud Run
Write-Host "`n📡 Conectando con Cloud Run..." -ForegroundColor Cyan

$command = "python manage.py load_demo_data --historical-months=12"

Write-Host "`n⏳ Ejecutando comando (esto puede tomar varios minutos)...`n" -ForegroundColor Yellow

gcloud run jobs create load-demo-data `
    --image gcr.io/argon-edge-478500-i8/cmms-backend `
    --region us-central1 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=config.settings.production,DATABASE_URL=postgresql://cmms_user:Santi2005@/cmms_db?host=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db,GCP_PROJECT_ID=argon-edge-478500-i8,GCP_STORAGE_BUCKET_NAME=cmms-storage-argon-edge,SECRET_KEY=your-secret-key-here-change-in-production" `
    --add-cloudsql-instances argon-edge-478500-i8:us-central1:cmms-db `
    --command python `
    --args "manage.py,load_demo_data,--historical-months=12" `
    --max-retries 0 `
    --task-timeout 30m

Write-Host "`n🎯 Ejecutando job..." -ForegroundColor Cyan

gcloud run jobs execute load-demo-data --region us-central1 --wait

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✓ Proceso Completado" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📊 Datos cargados exitosamente!" -ForegroundColor White
Write-Host "`n🌐 Puedes verificar los datos en:" -ForegroundColor Cyan
Write-Host "   https://cmms-somacor-prod.web.app`n" -ForegroundColor Yellow

Write-Host "👥 Usuarios creados:" -ForegroundColor Cyan
Write-Host "   • supervisor@example.com / demo123" -ForegroundColor White
Write-Host "   • operator1@example.com / demo123" -ForegroundColor White
Write-Host "   • operator2@example.com / demo123`n" -ForegroundColor White
