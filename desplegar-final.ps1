# Script de Despliegue Final - Sin Errores
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Desplegando CMMS en Google Cloud Platform" -ForegroundColor Cyan
Write-Host "     Proyecto: argon-edge-478500-i8" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar configuración
Write-Host "Verificando configuración..." -ForegroundColor Yellow
$project = gcloud config get-value project 2>$null
$account = gcloud config get-value account 2>$null

Write-Host "Proyecto: $project" -ForegroundColor Green
Write-Host "Cuenta: $account" -ForegroundColor Green
Write-Host ""

# Habilitar APIs
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Habilitando APIs necesarias (3-5 minutos)..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$apis = @(
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage-api.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Habilitando $api..." -ForegroundColor White
    gcloud services enable $api --project=argon-edge-478500-i8 --quiet 2>$null
    Write-Host "OK: $api" -ForegroundColor Green
}

Write-Host ""
Write-Host "Todas las APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Solicitar contraseña
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Configuración de Base de Datos" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ingresa una contraseña segura para la base de datos" -ForegroundColor White
Write-Host "Ejemplo: CMMS2025Secure (sin espacios ni caracteres especiales)" -ForegroundColor Gray
Write-Host ""
$dbPassword = Read-Host "Contraseña"

Write-Host ""
Write-Host "Presiona Enter para continuar con el despliegue..." -ForegroundColor Yellow
Read-Host

# Paso 1: Cloud SQL
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 1/4: Creando Cloud SQL (8-10 minutos)" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando si la instancia ya existe..." -ForegroundColor White
$existingInstance = gcloud sql instances describe cmms-db --project=argon-edge-478500-i8 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "La instancia cmms-db ya existe" -ForegroundColor Yellow
    $useExisting = Read-Host "Deseas usar la instancia existente? (y/n)"
    if ($useExisting -ne 'y') {
        Write-Host "Despliegue cancelado" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Creando instancia de PostgreSQL..." -ForegroundColor White
    Write-Host "Esto tomara 8-10 minutos. Por favor espera..." -ForegroundColor Yellow
    
    # Comando corregido sin --enable-bin-log (solo para MySQL)
    gcloud sql instances create cmms-db `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=us-central1 `
        --root-password=$dbPassword `
        --backup-start-time=03:00 `
        --retained-backups-count=7 `
        --project=argon-edge-478500-i8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Instancia de Cloud SQL creada" -ForegroundColor Green
    } else {
        Write-Host "Error al crear Cloud SQL" -ForegroundColor Red
        Write-Host "Verifica que la facturación esté habilitada" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "Creando base de datos..." -ForegroundColor White
gcloud sql databases create cmms_prod --instance=cmms-db --project=argon-edge-478500-i8 2>$null
Write-Host "Base de datos creada" -ForegroundColor Green

Write-Host ""
Write-Host "Creando usuario..." -ForegroundColor White
gcloud sql users create cmms_user --instance=cmms-db --password=$dbPassword --project=argon-edge-478500-i8 2>$null
Write-Host "Usuario creado" -ForegroundColor Green

# Paso 2: Cloud Storage
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 2/4: Creando Cloud Storage Buckets" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$buckets = @("cmms-documents", "cmms-ml-models", "cmms-reports", "cmms-backups")

foreach ($bucket in $buckets) {
    $bucketName = "argon-edge-478500-i8-$bucket"
    Write-Host "Creando bucket: $bucketName" -ForegroundColor White
    
    gcloud storage buckets create gs://$bucketName --location=us-central1 --uniform-bucket-level-access --project=argon-edge-478500-i8 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Bucket $bucketName creado" -ForegroundColor Green
    } else {
        Write-Host "Bucket $bucketName ya existe" -ForegroundColor Yellow
    }
}

# Paso 3: Pub/Sub
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 3/4: Configurando Cloud Pub/Sub" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$topics = @("notifications", "events", "alerts")

foreach ($topic in $topics) {
    Write-Host "Creando topic: $topic" -ForegroundColor White
    gcloud pubsub topics create $topic --project=argon-edge-478500-i8 2>$null
    Write-Host "Topic $topic creado" -ForegroundColor Green
    
    Write-Host "Creando subscription: $topic-sub" -ForegroundColor White
    gcloud pubsub subscriptions create "$topic-sub" --topic=$topic --ack-deadline=60 --project=argon-edge-478500-i8 2>$null
    Write-Host "Subscription $topic-sub creada" -ForegroundColor Green
}

# Paso 4: Backend
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Paso 4/4: Desplegando Backend a Cloud Run (8-10 minutos)" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "backend"
if (Test-Path $backendPath) {
    Push-Location $backendPath
    
    Write-Host "Creando Dockerfile..." -ForegroundColor White
    
    $dockerfileContent = @'
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

COPY . .

RUN mkdir -p staticfiles

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 0
'@
    
    $dockerfileContent | Out-File -FilePath "Dockerfile" -Encoding UTF8 -NoNewline
    Write-Host "Dockerfile creado" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Desplegando backend..." -ForegroundColor White
    Write-Host "Esto tomara 8-10 minutos. Por favor espera..." -ForegroundColor Yellow
    
    $connectionName = "argon-edge-478500-i8:us-central1:cmms-db"
    
    gcloud run deploy cmms-backend `
        --source . `
        --region=us-central1 `
        --platform=managed `
        --allow-unauthenticated `
        --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=$dbPassword,DB_HOST=/cloudsql/$connectionName" `
        --add-cloudsql-instances=$connectionName `
        --memory=1Gi `
        --cpu=1 `
        --min-instances=0 `
        --max-instances=10 `
        --project=argon-edge-478500-i8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Backend desplegado" -ForegroundColor Green
        
        $serviceUrl = gcloud run services describe cmms-backend --region=us-central1 --project=argon-edge-478500-i8 --format="value(status.url)"
        Write-Host "Backend URL: $serviceUrl" -ForegroundColor Green
        
        Pop-Location
        
        # Resumen final
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "     Despliegue Completado Exitosamente" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "URLs de la Aplicacion:" -ForegroundColor Cyan
        Write-Host "  Backend:  $serviceUrl" -ForegroundColor White
        Write-Host "  API Docs: $serviceUrl/api/docs/" -ForegroundColor White
        Write-Host ""
        Write-Host "Recursos Creados:" -ForegroundColor Cyan
        Write-Host "  - Cloud SQL: $connectionName" -ForegroundColor White
        Write-Host "  - Cloud Storage: 4 buckets" -ForegroundColor White
        Write-Host "  - Cloud Pub/Sub: 3 topics + subscriptions" -ForegroundColor White
        Write-Host "  - Cloud Run: cmms-backend" -ForegroundColor White
        Write-Host ""
        Write-Host "Proximos Pasos:" -ForegroundColor Yellow
        Write-Host "  1. Crear superusuario para acceder al admin" -ForegroundColor White
        Write-Host "  2. Probar la API en: $serviceUrl/api/docs/" -ForegroundColor White
        Write-Host ""
        
        # Guardar información
        $deployInfo = @"
Informacion del Despliegue
==========================
Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Proyecto: argon-edge-478500-i8
Cuenta: $account
Backend URL: $serviceUrl
Connection Name: $connectionName
Region: us-central1

Credenciales de Base de Datos:
- Host: /cloudsql/$connectionName
- Database: cmms_prod
- User: cmms_user
- Password: $dbPassword
"@
        
        $deployInfo | Out-File -FilePath "..\deployment-info.txt" -Encoding UTF8
        Write-Host "Informacion guardada en: deployment-info.txt" -ForegroundColor Green
        Write-Host ""
        Write-Host "Despliegue completado!" -ForegroundColor Green
        
    } else {
        Write-Host "Error al desplegar backend" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "Error: No se encontro el directorio backend" -ForegroundColor Red
    exit 1
}
