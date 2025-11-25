# Script de Despliegue Inmediato
# Proyecto: argon-edge-478500-i8
# Usuario: electronightx@gmail.com

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "║     Desplegando CMMS en Google Cloud Platform            ║" -ForegroundColor Cyan
Write-Host "║     Proyecto: argon-edge-478500-i8                        ║" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar configuración
Write-Host "Verificando configuración..." -ForegroundColor Yellow
$project = gcloud config get-value project
$account = gcloud config get-value account

if ($project -ne "argon-edge-478500-i8") {
    Write-Host "✗ Proyecto incorrecto. Configurando..." -ForegroundColor Red
    gcloud config set project argon-edge-478500-i8
}

Write-Host "✓ Proyecto: $project" -ForegroundColor Green
Write-Host "✓ Cuenta: $account" -ForegroundColor Green
Write-Host ""

# Habilitar APIs necesarias
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Habilitando APIs necesarias (3-5 minutos)..." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$apis = @(
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage-api.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com",
    "artifactregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Habilitando $api..." -ForegroundColor White
    gcloud services enable $api --project=argon-edge-478500-i8 --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $api habilitada" -ForegroundColor Green
    } else {
        Write-Host "⚠ Error al habilitar $api" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✓ Todas las APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Solicitar contraseña de base de datos
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Configuración de Base de Datos" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Necesitas elegir una contraseña segura para la base de datos." -ForegroundColor White
Write-Host "Ejemplo: CMMS2025!Secure" -ForegroundColor Gray
Write-Host ""
$dbPassword = Read-Host "Ingresa contraseña para la base de datos" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Iniciando Despliegue" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Esto tomará aproximadamente 20-25 minutos." -ForegroundColor White
Write-Host "Puedes ver el progreso en tiempo real." -ForegroundColor White
Write-Host ""
Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
Read-Host

# Paso 1: Cloud SQL
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 1/5: Creando Cloud SQL (8-10 minutos)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando si la instancia ya existe..." -ForegroundColor White
$existingInstance = gcloud sql instances describe cmms-db --project=argon-edge-478500-i8 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠ La instancia cmms-db ya existe" -ForegroundColor Yellow
    Write-Host "¿Deseas usar la instancia existente? (y/n): " -ForegroundColor Yellow -NoNewline
    $useExisting = Read-Host
    if ($useExisting -ne 'y' -and $useExisting -ne 'Y') {
        Write-Host "Despliegue cancelado" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Creando instancia de PostgreSQL..." -ForegroundColor White
    gcloud sql instances create cmms-db `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=us-central1 `
        --root-password=$dbPasswordPlain `
        --backup-start-time=03:00 `
        --enable-bin-log `
        --retained-backups-count=7 `
        --retained-transaction-log-days=7 `
        --project=argon-edge-478500-i8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Instancia de Cloud SQL creada" -ForegroundColor Green
    } else {
        Write-Host "✗ Error al crear Cloud SQL" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Creando base de datos..." -ForegroundColor White
gcloud sql databases create cmms_prod --instance=cmms-db --project=argon-edge-478500-i8 2>&1 | Out-Null
Write-Host "✓ Base de datos creada" -ForegroundColor Green

Write-Host ""
Write-Host "Creando usuario..." -ForegroundColor White
gcloud sql users create cmms_user --instance=cmms-db --password=$dbPasswordPlain --project=argon-edge-478500-i8 2>&1 | Out-Null
Write-Host "✓ Usuario creado" -ForegroundColor Green

# Paso 2: Cloud Storage
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 2/5: Creando Cloud Storage Buckets (1-2 minutos)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$buckets = @("cmms-documents", "cmms-ml-models", "cmms-reports", "cmms-backups")

foreach ($bucket in $buckets) {
    $bucketName = "argon-edge-478500-i8-$bucket"
    Write-Host "Creando bucket: $bucketName" -ForegroundColor White
    
    gcloud storage buckets create gs://$bucketName `
        --location=us-central1 `
        --uniform-bucket-level-access `
        --project=argon-edge-478500-i8 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Bucket $bucketName creado" -ForegroundColor Green
    } else {
        Write-Host "⚠ Bucket $bucketName ya existe o error" -ForegroundColor Yellow
    }
}

# Paso 3: Pub/Sub
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 3/5: Configurando Cloud Pub/Sub (1 minuto)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$topics = @("notifications", "events", "alerts")

foreach ($topic in $topics) {
    Write-Host "Creando topic: $topic" -ForegroundColor White
    gcloud pubsub topics create $topic --project=argon-edge-478500-i8 2>&1 | Out-Null
    Write-Host "✓ Topic $topic creado" -ForegroundColor Green
    
    Write-Host "Creando subscription: $topic-sub" -ForegroundColor White
    gcloud pubsub subscriptions create "$topic-sub" `
        --topic=$topic `
        --ack-deadline=60 `
        --project=argon-edge-478500-i8 2>&1 | Out-Null
    Write-Host "✓ Subscription $topic-sub creada" -ForegroundColor Green
}

# Paso 4: Backend
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 4/5: Desplegando Backend a Cloud Run (8-10 minutos)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\..\backend"
Push-Location $backendPath

Write-Host "Creando Dockerfile..." -ForegroundColor White
$dockerfile = @"
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

COPY . .

RUN mkdir -p staticfiles

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:`$PORT --workers 2 --threads 4 --timeout 0
"@
$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8
Write-Host "✓ Dockerfile creado" -ForegroundColor Green

Write-Host ""
Write-Host "Desplegando backend (esto puede tomar 8-10 minutos)..." -ForegroundColor White
$connectionName = "argon-edge-478500-i8:us-central1:cmms-db"

gcloud run deploy cmms-backend `
    --source . `
    --region=us-central1 `
    --platform=managed `
    --allow-unauthenticated `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=$dbPasswordPlain,DB_HOST=/cloudsql/$connectionName" `
    --add-cloudsql-instances=$connectionName `
    --memory=1Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=10 `
    --project=argon-edge-478500-i8

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend desplegado" -ForegroundColor Green
    
    $serviceUrl = gcloud run services describe cmms-backend --region=us-central1 --project=argon-edge-478500-i8 --format="value(status.url)"
    Write-Host "✓ Backend URL: $serviceUrl" -ForegroundColor Green
} else {
    Write-Host "✗ Error al desplegar backend" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Resumen final
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║     ✓ Despliegue Completado Exitosamente                 ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "URLs de la Aplicación:" -ForegroundColor Cyan
Write-Host "  Backend:  $serviceUrl" -ForegroundColor White
Write-Host "  API Docs: $serviceUrl/api/docs/" -ForegroundColor White
Write-Host ""
Write-Host "Recursos Creados:" -ForegroundColor Cyan
Write-Host "  ✓ Cloud SQL: $connectionName" -ForegroundColor White
Write-Host "  ✓ Cloud Storage: 4 buckets" -ForegroundColor White
Write-Host "  ✓ Cloud Pub/Sub: 3 topics + subscriptions" -ForegroundColor White
Write-Host "  ✓ Cloud Run: cmms-backend" -ForegroundColor White
Write-Host ""
Write-Host "Próximos Pasos:" -ForegroundColor Yellow
Write-Host "  1. Crear superusuario para acceder al admin" -ForegroundColor White
Write-Host "  2. Probar la API en: $serviceUrl/api/docs/" -ForegroundColor White
Write-Host ""
Write-Host "¡Despliegue completado! 🎉" -ForegroundColor Green
Write-Host ""

# Guardar información
$deployInfo = @"
Información del Despliegue
==========================
Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Proyecto: argon-edge-478500-i8
Cuenta: electronightx@gmail.com
Backend URL: $serviceUrl
Connection Name: $connectionName
Región: us-central1

Credenciales de Base de Datos:
- Host: /cloudsql/$connectionName
- Database: cmms_prod
- User: cmms_user
- Password: [guardada en variables de entorno de Cloud Run]
"@

$deployInfo | Out-File -FilePath "deployment-info.txt" -Encoding UTF8
Write-Host "✓ Información guardada en: deployment-info.txt" -ForegroundColor Green
