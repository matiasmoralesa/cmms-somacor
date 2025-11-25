# 🚀 Guía de Despliegue en GCP - Windows

**Fecha**: 16 de Noviembre, 2025  
**Sistema**: Windows  
**Estado del Proyecto**: ✅ Listo para desplegar

---

## 📋 Requisitos Previos

### 1. Cuenta de Google Cloud Platform
- ✅ Crear cuenta en https://cloud.google.com/
- ✅ Habilitar facturación (incluye $300 de crédito gratis)
- ✅ Crear un nuevo proyecto o usar uno existente

### 2. Instalar Google Cloud SDK en Windows

**Opción A: Instalador (Recomendado)**
1. Descargar desde: https://cloud.google.com/sdk/docs/install#windows
2. Ejecutar `GoogleCloudSDKInstaller.exe`
3. Seguir el asistente de instalación
4. Marcar "Run 'gcloud init'" al finalizar

**Opción B: PowerShell**
```powershell
# Descargar instalador
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

# Ejecutar instalador
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### 3. Verificar Instalación
```powershell
# Abrir nueva terminal PowerShell
gcloud --version
```

Deberías ver algo como:
```
Google Cloud SDK 456.0.0
bq 2.0.99
core 2023.11.10
gcloud-crc32c 1.0.0
gsutil 5.27
```

### 4. Instalar Firebase CLI
```powershell
npm install -g firebase-tools
firebase --version
```

### 5. Instalar Docker Desktop (Opcional para desarrollo local)
- Descargar desde: https://www.docker.com/products/docker-desktop/
- Instalar y reiniciar Windows si es necesario

---

## 🔧 Configuración Inicial

### 1. Autenticarse en GCP
```powershell
# Iniciar sesión
gcloud auth login

# Esto abrirá tu navegador para autenticarte
```

### 2. Configurar Proyecto
```powershell
# Listar proyectos disponibles
gcloud projects list

# Crear nuevo proyecto (opcional)
gcloud projects create cmms-prod-123 --name="CMMS Production"

# Configurar proyecto activo
gcloud config set project cmms-prod-123

# Configurar región
gcloud config set compute/region us-central1
```

### 3. Habilitar APIs Necesarias
```powershell
# Habilitar todas las APIs necesarias
gcloud services enable `
  sqladmin.googleapis.com `
  run.googleapis.com `
  cloudbuild.googleapis.com `
  storage-api.googleapis.com `
  pubsub.googleapis.com `
  secretmanager.googleapis.com `
  cloudscheduler.googleapis.com `
  composer.googleapis.com
```

Esto tomará unos minutos. Verás mensajes como:
```
Operation "operations/..." finished successfully.
```

### 4. Configurar Variables de Entorno
```powershell
# Crear archivo de configuración
cd deployment\gcp

# Editar y guardar estas variables
$env:GCP_PROJECT_ID = "cmms-prod-123"  # Tu proyecto
$env:GCP_REGION = "us-central1"
$env:DB_PASSWORD = "TuContraseñaSegura123!"  # Cambiar por una segura
$env:DB_TIER = "db-f1-micro"  # Para desarrollo (más barato)
# $env:DB_TIER = "db-n1-standard-1"  # Para producción

# Guardar en archivo para reutilizar
@"
`$env:GCP_PROJECT_ID = "$env:GCP_PROJECT_ID"
`$env:GCP_REGION = "$env:GCP_REGION"
`$env:DB_PASSWORD = "$env:DB_PASSWORD"
`$env:DB_TIER = "$env:DB_TIER"
"@ | Out-File -FilePath "config.ps1" -Encoding UTF8

Write-Host "✅ Variables configuradas y guardadas en config.ps1"
```

---

## 🚀 Despliegue Paso a Paso

### Paso 1: Crear Cloud SQL (Base de Datos)

```powershell
# Cargar configuración
. .\config.ps1

# Crear instancia de PostgreSQL
gcloud sql instances create cmms-db `
  --database-version=POSTGRES_15 `
  --tier=$env:DB_TIER `
  --region=$env:GCP_REGION `
  --root-password=$env:DB_PASSWORD `
  --backup-start-time=03:00 `
  --enable-bin-log `
  --retained-backups-count=7 `
  --retained-transaction-log-days=7

Write-Host "✅ Instancia de Cloud SQL creada"

# Crear base de datos
gcloud sql databases create cmms_prod --instance=cmms-db

Write-Host "✅ Base de datos creada"

# Crear usuario
gcloud sql users create cmms_user `
  --instance=cmms-db `
  --password=$env:DB_PASSWORD

Write-Host "✅ Usuario de base de datos creado"
```

**Tiempo estimado**: 5-10 minutos

### Paso 2: Crear Cloud Storage Buckets

```powershell
# Crear buckets para almacenamiento
$buckets = @(
    "cmms-documents",
    "cmms-ml-models",
    "cmms-reports",
    "cmms-backups"
)

foreach ($bucket in $buckets) {
    $bucketName = "$env:GCP_PROJECT_ID-$bucket"
    
    gcloud storage buckets create gs://$bucketName `
      --location=$env:GCP_REGION `
      --uniform-bucket-level-access
    
    Write-Host "✅ Bucket $bucketName creado"
}

# Configurar CORS para el bucket de documentos
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

$corsConfig | Out-File -FilePath "cors.json" -Encoding UTF8
gcloud storage buckets update gs://$env:GCP_PROJECT_ID-cmms-documents --cors-file=cors.json
Remove-Item cors.json

Write-Host "✅ Todos los buckets creados"
```

**Tiempo estimado**: 1-2 minutos

### Paso 3: Crear Cloud Pub/Sub Topics

```powershell
# Crear topics
$topics = @("notifications", "events", "alerts")

foreach ($topic in $topics) {
    gcloud pubsub topics create $topic
    Write-Host "✅ Topic $topic creado"
    
    # Crear subscription para cada topic
    gcloud pubsub subscriptions create "$topic-sub" `
      --topic=$topic `
      --ack-deadline=60
    
    Write-Host "✅ Subscription $topic-sub creada"
}

Write-Host "✅ Pub/Sub configurado"
```

**Tiempo estimado**: 1 minuto

### Paso 4: Desplegar Backend a Cloud Run

```powershell
# Navegar al directorio del backend
cd ..\..\backend

# Crear Dockerfile si no existe
$dockerfile = @"
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copiar código
COPY . .

# Crear directorio para archivos estáticos
RUN mkdir -p staticfiles

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Puerto
ENV PORT=8080
EXPOSE 8080

# Comando de inicio
CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:`$PORT --workers 2 --threads 4 --timeout 0
"@

$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8

Write-Host "✅ Dockerfile creado"

# Construir y desplegar
gcloud run deploy cmms-backend `
  --source . `
  --region=$env:GCP_REGION `
  --platform=managed `
  --allow-unauthenticated `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=$env:DB_PASSWORD" `
  --add-cloudsql-instances="$env:GCP_PROJECT_ID:$env:GCP_REGION:cmms-db" `
  --memory=1Gi `
  --cpu=1 `
  --min-instances=1 `
  --max-instances=10

Write-Host "✅ Backend desplegado en Cloud Run"

# Obtener URL del servicio
$SERVICE_URL = gcloud run services describe cmms-backend --region=$env:GCP_REGION --format="value(status.url)"
Write-Host "Backend URL: $SERVICE_URL"
```

**Tiempo estimado**: 5-10 minutos (primera vez)

### Paso 5: Desplegar Frontend a Firebase Hosting

```powershell
# Navegar al directorio del frontend
cd ..\frontend

# Inicializar Firebase (solo primera vez)
firebase login
firebase init hosting

# Cuando pregunte:
# - Project: Selecciona tu proyecto GCP
# - Public directory: dist
# - Single-page app: Yes
# - GitHub deploys: No

# Crear archivo de configuración de producción
$envProd = @"
VITE_API_URL=$SERVICE_URL/api/v1
VITE_APP_NAME=CMMS
VITE_APP_VERSION=1.0.0
"@

$envProd | Out-File -FilePath ".env.production" -Encoding UTF8

# Construir aplicación
npm run build

# Desplegar a Firebase
firebase deploy --only hosting

Write-Host "✅ Frontend desplegado en Firebase Hosting"

# Obtener URL del frontend
$FRONTEND_URL = firebase hosting:channel:list --json | ConvertFrom-Json | Select-Object -First 1 -ExpandProperty url
Write-Host "Frontend URL: $FRONTEND_URL"
```

**Tiempo estimado**: 3-5 minutos

### Paso 6: Configuración Final

```powershell
# Actualizar CORS en el backend
gcloud run services update cmms-backend `
  --update-env-vars="FRONTEND_URL=$FRONTEND_URL" `
  --region=$env:GCP_REGION

Write-Host "✅ CORS configurado"

# Ejecutar migraciones
gcloud run jobs create cmms-migrate `
  --image=gcr.io/$env:GCP_PROJECT_ID/cmms-backend `
  --region=$env:GCP_REGION `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production" `
  --add-cloudsql-instances="$env:GCP_PROJECT_ID:$env:GCP_REGION:cmms-db" `
  --command="python,manage.py,migrate"

gcloud run jobs execute cmms-migrate --region=$env:GCP_REGION --wait

Write-Host "✅ Migraciones ejecutadas"
```

---

## 🎉 Despliegue Completado

### URLs de tu Aplicación
```
Frontend: https://tu-proyecto.web.app
Backend:  https://cmms-backend-xxx-uc.a.run.app
API Docs: https://cmms-backend-xxx-uc.a.run.app/api/docs/
```

### Crear Superusuario

**Opción 1: Usando Cloud Shell**
```powershell
# Abrir Cloud Shell en https://console.cloud.google.com
# Ejecutar:
gcloud run services proxy cmms-backend --region=us-central1
# En otra terminal:
python manage.py createsuperuser
```

**Opción 2: Usando Cloud SQL Proxy (Local)**
```powershell
# Descargar Cloud SQL Proxy
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"

# Ejecutar proxy
.\cloud_sql_proxy.exe -instances=$env:GCP_PROJECT_ID:$env:GCP_REGION:cmms-db=tcp:5432

# En otra terminal PowerShell
cd backend
.\venv\Scripts\Activate.ps1
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "5432"
$env:DB_NAME = "cmms_prod"
$env:DB_USER = "cmms_user"
$env:DB_PASSWORD = "TuContraseña"
python manage.py createsuperuser
```

---

## 📊 Monitoreo

### Ver Logs
```powershell
# Logs del backend en tiempo real
gcloud run services logs tail cmms-backend --region=$env:GCP_REGION

# Últimos 100 logs
gcloud run services logs read cmms-backend --region=$env:GCP_REGION --limit=100

# Solo errores
gcloud run services logs read cmms-backend --region=$env:GCP_REGION --log-filter="severity>=ERROR"
```

### Ver Métricas
```powershell
# Abrir Cloud Console
Start-Process "https://console.cloud.google.com/run/detail/$env:GCP_REGION/cmms-backend/metrics?project=$env:GCP_PROJECT_ID"
```

---

## 🔄 Actualizar la Aplicación

### Actualizar Backend
```powershell
cd backend
gcloud run deploy cmms-backend --source . --region=$env:GCP_REGION
```

### Actualizar Frontend
```powershell
cd frontend
npm run build
firebase deploy --only hosting
```

---

## 💰 Costos Estimados

### Configuración Mínima (Desarrollo)
- Cloud SQL (db-f1-micro): ~$7/mes
- Cloud Run (1 instancia): ~$5/mes
- Cloud Storage (10 GB): ~$0.20/mes
- Firebase Hosting: Gratis
- **Total: ~$12-15/mes**

### Configuración Producción
- Cloud SQL (db-n1-standard-1): ~$50/mes
- Cloud Run (auto-scaling): ~$20-50/mes
- Cloud Storage (100 GB): ~$2/mes
- **Total: ~$75-100/mes**

---

## 🛠️ Troubleshooting

### Error: "gcloud not found"
```powershell
# Cerrar y abrir nueva terminal PowerShell
# O agregar manualmente al PATH:
$env:Path += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
```

### Error: "Permission denied"
```powershell
# Verificar autenticación
gcloud auth list

# Re-autenticar si es necesario
gcloud auth login
```

### Error: "Cloud SQL connection failed"
```powershell
# Verificar que la instancia esté corriendo
gcloud sql instances describe cmms-db

# Reiniciar si es necesario
gcloud sql instances restart cmms-db
```

### Frontend no carga
```powershell
# Verificar build
cd frontend
npm run build

# Verificar despliegue
firebase hosting:channel:list

# Redesplegar
firebase deploy --only hosting --force
```

---

## 📞 Soporte

**Documentación Completa**: Ver `deployment/gcp/README.md`

**Comandos Útiles**:
```powershell
# Ver estado de servicios
gcloud run services list

# Ver bases de datos
gcloud sql instances list

# Ver buckets
gcloud storage buckets list

# Ver costos
Start-Process "https://console.cloud.google.com/billing"
```

---

## ✅ Checklist de Despliegue

- [ ] Google Cloud SDK instalado
- [ ] Firebase CLI instalado
- [ ] Proyecto GCP creado
- [ ] APIs habilitadas
- [ ] Variables de entorno configuradas
- [ ] Cloud SQL creado
- [ ] Cloud Storage configurado
- [ ] Pub/Sub configurado
- [ ] Backend desplegado
- [ ] Frontend desplegado
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] CORS configurado
- [ ] Monitoreo configurado

---

**¡Listo para producción! 🚀**
