# Script PowerShell para redesplegar el backend en Cloud Run
# Este script actualiza el backend con la nueva configuración de CORS

Write-Host "🚀 Iniciando redespliegue del backend..." -ForegroundColor Green
Write-Host ""

# Configurar el proyecto
Write-Host "📋 Configurando proyecto GCP..." -ForegroundColor Yellow
gcloud config set project argon-edge-478500-i8

# Navegar al directorio del backend
Set-Location backend

# Construir la imagen
Write-Host "🔨 Construyendo imagen Docker..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/argon-edge-478500-i8/cmms-backend

# Desplegar en Cloud Run
Write-Host "🚢 Desplegando en Cloud Run..." -ForegroundColor Yellow
gcloud run deploy cmms-backend `
  --image gcr.io/argon-edge-478500-i8/cmms-backend `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars DJANGO_SETTINGS_MODULE=config.settings.production `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10

Write-Host ""
Write-Host "✅ Redespliegue completado!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs del sistema:" -ForegroundColor Cyan
Write-Host "   Frontend: https://cmms-somacor-prod.web.app" -ForegroundColor White
Write-Host "   Backend: https://cmms-backend-232652686658.us-central1.run.app" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Verifica que el frontend pueda comunicarse con el backend." -ForegroundColor Yellow
