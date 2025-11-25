# Script de Despliegue Automatizado para Windows
# CMMS - Google Cloud Platform
# Uso: .\deploy-windows.ps1

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$DbPassword = "",
    [string]$DbTier = "db-f1-micro",
    [switch]$SkipConfirmation
)

# Colores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Info { Write-ColorOutput Cyan $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }

# Banner
Write-Info ""
Write-Info "╔═══════════════════════════════════════════════════════════╗"
Write-Info "║                                                           ║"
Write-Info "║         CMMS - Despliegue Completo en GCP                ║"
Write-Info "║                    Windows Edition                        ║"
Write-Info "║                                                           ║"
Write-Info "╚═══════════════════════════════════════════════════════════╝"
Write-Info ""

# Verificar gcloud
Write-Info "Verificando Google Cloud SDK..."
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Success "✓ Google Cloud SDK instalado: $gcloudVersion"
} catch {
    Write-Error "✗ Google Cloud SDK no está instalado"
    Write-Info ""
    Write-Info "Instala Google Cloud SDK desde:"
    Write-Info "https://cloud.google.com/sdk/docs/install#windows"
    Write-Info ""
    exit 1
}

# Verificar autenticación
Write-Info "Verificando autenticación..."
$authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($authAccount)) {
    Write-Warning "No estás autenticado en GCP"
    Write-Info "Iniciando proceso de autenticación..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "✗ Error en la autenticación"
        exit 1
    }
}
Write-Success "✓ Autenticado como: $authAccount"

# Solicitar Project ID si no se proporcionó
if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Info ""
    Write-Info "Proyectos disponibles:"
    gcloud projects list --format="table(projectId,name,projectNumber)"
    Write-Info ""
    $ProjectId = Read-Host "Ingresa el Project ID"
}

# Configurar proyecto
Write-Info "Configurando proyecto: $ProjectId"
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Error "✗ Error al configurar el proyecto"
    exit 1
}
Write-Success "✓ Proyecto configurado"

# Configurar región
gcloud config set compute/region $Region
Write-Success "✓ Región configurada: $Region"

# Solicitar contraseña de BD si no se proporcionó
if ([string]::IsNullOrEmpty($DbPassword)) {
    Write-Info ""
    $DbPassword = Read-Host "Ingresa una contraseña segura para la base de datos" -AsSecureString
    $DbPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DbPassword))
}

# Mostrar configuración
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Configuración del Despliegue:"
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "  Project ID:    $ProjectId"
Write-Info "  Region:        $Region"
Write-Info "  DB Tier:       $DbTier"
Write-Info "  Account:       $authAccount"
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info ""

# Confirmar
if (-not $SkipConfirmation) {
    $confirmation = Read-Host "¿Deseas continuar con el despliegue? (y/n)"
    if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
        Write-Warning "Despliegue cancelado"
        exit 0
    }
}

# Habilitar APIs
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Habilitando APIs necesarias..."
Write-Info "═══════════════════════════════════════════════════════════"

$apis = @(
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage-api.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "Habilitando $api..."
    gcloud services enable $api --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ $api habilitada"
    } else {
        Write-Warning "⚠ Error al habilitar $api (puede que ya esté habilitada)"
    }
}

# Paso 1: Cloud SQL
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Paso 1/5: Creando Cloud SQL"
Write-Info "═══════════════════════════════════════════════════════════"

Write-Info "Verificando si la instancia ya existe..."
$existingInstance = gcloud sql instances describe cmms-db 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Warning "⚠ La instancia cmms-db ya existe, saltando creación..."
} else {
    Write-Info "Creando instancia de PostgreSQL (esto puede tomar 5-10 minutos)..."
    gcloud sql instances create cmms-db `
        --database-version=POSTGRES_15 `
        --tier=$DbTier `
        --region=$Region `
        --root-password=$DbPassword `
        --backup-start-time=03:00 `
        --enable-bin-log `
        --retained-backups-count=7 `
        --retained-transaction-log-days=7 `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Instancia de Cloud SQL creada"
    } else {
        Write-Error "✗ Error al crear Cloud SQL"
        exit 1
    }
}

Write-Info "Creando base de datos..."
gcloud sql databases create cmms_prod --instance=cmms-db --quiet 2>&1 | Out-Null
Write-Success "✓ Base de datos creada"

Write-Info "Creando usuario..."
gcloud sql users create cmms_user --instance=cmms-db --password=$DbPassword --quiet 2>&1 | Out-Null
Write-Success "✓ Usuario creado"

# Paso 2: Cloud Storage
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Paso 2/5: Creando Cloud Storage Buckets"
Write-Info "═══════════════════════════════════════════════════════════"

$buckets = @("cmms-documents", "cmms-ml-models", "cmms-reports", "cmms-backups")

foreach ($bucket in $buckets) {
    $bucketName = "$ProjectId-$bucket"
    Write-Info "Creando bucket: $bucketName"
    
    gcloud storage buckets create gs://$bucketName `
        --location=$Region `
        --uniform-bucket-level-access `
        --quiet 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Bucket $bucketName creado"
    } else {
        Write-Warning "⚠ Bucket $bucketName ya existe o error al crear"
    }
}

# Configurar CORS
Write-Info "Configurando CORS..."
$corsConfig = @"
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
"@
$corsConfig | Out-File -FilePath "cors-temp.json" -Encoding UTF8
gcloud storage buckets update gs://$ProjectId-cmms-documents --cors-file=cors-temp.json --quiet 2>&1 | Out-Null
Remove-Item cors-temp.json -ErrorAction SilentlyContinue
Write-Success "✓ CORS configurado"

# Paso 3: Pub/Sub
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Paso 3/5: Configurando Cloud Pub/Sub"
Write-Info "═══════════════════════════════════════════════════════════"

$topics = @("notifications", "events", "alerts")

foreach ($topic in $topics) {
    Write-Info "Creando topic: $topic"
    gcloud pubsub topics create $topic --quiet 2>&1 | Out-Null
    Write-Success "✓ Topic $topic creado"
    
    Write-Info "Creando subscription: $topic-sub"
    gcloud pubsub subscriptions create "$topic-sub" `
        --topic=$topic `
        --ack-deadline=60 `
        --quiet 2>&1 | Out-Null
    Write-Success "✓ Subscription $topic-sub creada"
}

# Paso 4: Backend
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Paso 4/5: Desplegando Backend a Cloud Run"
Write-Info "═══════════════════════════════════════════════════════════"

# Navegar al directorio del backend
$backendPath = Join-Path $PSScriptRoot "..\..\backend"
Push-Location $backendPath

Write-Info "Creando Dockerfile..."
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
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:`$PORT --workers 2 --threads 4 --timeout 0
"@
$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8
Write-Success "✓ Dockerfile creado"

Write-Info "Desplegando backend (esto puede tomar 5-10 minutos)..."
$connectionName = "$ProjectId:$Region:cmms-db"

gcloud run deploy cmms-backend `
    --source . `
    --region=$Region `
    --platform=managed `
    --allow-unauthenticated `
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=$DbPassword,DB_HOST=/cloudsql/$connectionName" `
    --add-cloudsql-instances=$connectionName `
    --memory=1Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=10 `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Success "✓ Backend desplegado"
    
    # Obtener URL
    $serviceUrl = gcloud run services describe cmms-backend --region=$Region --format="value(status.url)"
    Write-Success "Backend URL: $serviceUrl"
} else {
    Write-Error "✗ Error al desplegar backend"
    Pop-Location
    exit 1
}

Pop-Location

# Paso 5: Frontend
Write-Info ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Info "Paso 5/5: Desplegando Frontend"
Write-Info "═══════════════════════════════════════════════════════════"

$frontendPath = Join-Path $PSScriptRoot "..\..\frontend"
Push-Location $frontendPath

# Verificar si Firebase está inicializado
if (-not (Test-Path "firebase.json")) {
    Write-Warning "⚠ Firebase no está inicializado"
    Write-Info "Ejecuta manualmente:"
    Write-Info "  cd frontend"
    Write-Info "  firebase login"
    Write-Info "  firebase init hosting"
    Write-Info "  firebase deploy"
} else {
    Write-Info "Creando configuración de producción..."
    $envProd = @"
VITE_API_URL=$serviceUrl/api/v1
VITE_APP_NAME=CMMS
VITE_APP_VERSION=1.0.0
"@
    $envProd | Out-File -FilePath ".env.production" -Encoding UTF8
    Write-Success "✓ Configuración creada"
    
    Write-Info "Construyendo frontend..."
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Frontend construido"
        
        Write-Info "Desplegando a Firebase..."
        firebase deploy --only hosting --project $ProjectId
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Frontend desplegado"
        } else {
            Write-Warning "⚠ Error al desplegar frontend"
        }
    } else {
        Write-Warning "⚠ Error al construir frontend"
    }
}

Pop-Location

# Resumen final
Write-Info ""
Write-Info "╔═══════════════════════════════════════════════════════════╗"
Write-Info "║                                                           ║"
Write-Info "║         ✓ Despliegue Completado Exitosamente             ║"
Write-Info "║                                                           ║"
Write-Info "╚═══════════════════════════════════════════════════════════╝"
Write-Info ""
Write-Success "URLs de la Aplicación:"
Write-Info "  Backend:  $serviceUrl"
Write-Info "  API Docs: $serviceUrl/api/docs/"
Write-Info ""
Write-Success "Recursos Creados:"
Write-Info "  ✓ Cloud SQL: $connectionName"
Write-Info "  ✓ Cloud Storage: 4 buckets"
Write-Info "  ✓ Cloud Pub/Sub: 3 topics + subscriptions"
Write-Info "  ✓ Cloud Run: cmms-backend"
Write-Info ""
Write-Warning "Próximos Pasos:"
Write-Info "  1. Crear superusuario para acceder al admin"
Write-Info "  2. Configurar dominio personalizado (opcional)"
Write-Info "  3. Configurar monitoreo y alertas"
Write-Info ""
Write-Info "Comandos Útiles:"
Write-Info "  Ver logs:"
Write-Info "    gcloud run services logs read cmms-backend --region $Region"
Write-Info ""
Write-Info "  Actualizar backend:"
Write-Info "    cd backend"
Write-Info "    gcloud run deploy cmms-backend --source . --region $Region"
Write-Info ""
Write-Success "¡Despliegue completado! 🎉"
Write-Info ""

# Guardar configuración
$configFile = Join-Path $PSScriptRoot "deployment-config.txt"
@"
Configuración del Despliegue
=============================
Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Project ID: $ProjectId
Region: $Region
Backend URL: $serviceUrl
Connection Name: $connectionName
"@ | Out-File -FilePath $configFile -Encoding UTF8

Write-Info "Configuración guardada en: $configFile"
