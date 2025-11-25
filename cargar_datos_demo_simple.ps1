# Script simple para cargar datos de demostracion
Write-Host "`nCargando datos de demostracion en el sistema CMMS...`n" -ForegroundColor Cyan

# Crear y ejecutar un job de Cloud Run
Write-Host "Creando job de Cloud Run..." -ForegroundColor Yellow

gcloud run jobs create load-demo-data `
    --image gcr.io/argon-edge-478500-i8/cmms-backend `
    --region us-central1 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=config.settings.production,DATABASE_URL=postgresql://cmms_user:Santi2005@/cmms_db?host=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db,GCP_PROJECT_ID=argon-edge-478500-i8,GCP_STORAGE_BUCKET_NAME=cmms-storage-argon-edge,SECRET_KEY=your-secret-key-here-change-in-production" `
    --set-cloudsql-instances argon-edge-478500-i8:us-central1:cmms-db `
    --command python `
    --args "manage.py,load_demo_data,--historical-months=12" `
    --max-retries 0 `
    --task-timeout 30m `
    --project argon-edge-478500-i8

Write-Host "`nEjecutando job (esto puede tomar 5-10 minutos)...`n" -ForegroundColor Yellow

gcloud run jobs execute load-demo-data --region us-central1 --project argon-edge-478500-i8 --wait

Write-Host "`nDatos cargados exitosamente!`n" -ForegroundColor Green
Write-Host "Puedes verificar los datos en: https://cmms-somacor-prod.web.app`n" -ForegroundColor Cyan
