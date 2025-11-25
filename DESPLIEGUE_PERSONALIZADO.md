# 🚀 Despliegue Personalizado - CMMS

**Project ID**: `argon-edge-478500-i8`  
**Fecha**: 16 de Noviembre, 2025  
**Estado**: Listo para desplegar

---

## 📋 Paso 1: Instalar Google Cloud SDK (5 minutos)

### Opción A: Instalador Automático (Recomendado)
```powershell
# Descargar instalador
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

Write-Host "Descargando Google Cloud SDK..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "Ejecutando instalador..."
Start-Process -FilePath $installerPath -Wait

Write-Host "✅ Instalación completada"
Write-Host "⚠️ IMPORTANTE: Cierra esta terminal y abre una NUEVA terminal PowerShell"
```

### Opción B: Descarga Manual
1. Ir a: https://cloud.google.com/sdk/docs/install#windows
2. Descargar `GoogleCloudSDKInstaller.exe`
3. Ejecutar el instalador
4. Marcar "Run 'gcloud init'" al finalizar
5. **Cerrar y abrir nueva terminal PowerShell**

---

## 📋 Paso 2: Configurar GCP (3 minutos)

**⚠️ IMPORTANTE: Abre una NUEVA terminal PowerShell después de instalar el SDK**

```powershell
# Verificar instalación
gcloud --version

# Deberías ver algo como:
# Google Cloud SDK 456.0.0
# bq 2.0.99
# core 2023.11.10
```

### Autenticarse
```powershell
# Iniciar sesión (abrirá tu navegador)
gcloud auth login

# Configurar tu proyecto
gcloud config set project argon-edge-478500-i8

# Configurar región
gcloud config set compute/region us-central1

# Verificar configuración
gcloud config list
```

---

## 📋 Paso 3: Habilitar APIs (5 minutos)

```powershell
# Habilitar todas las APIs necesarias
Write-Host "Habilitando APIs de GCP..."

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
    Write-Host "Habilitando $api..."
    gcloud services enable $api --project=argon-edge-478500-i8
}

Write-Host "✅ Todas las APIs habilitadas"
```

**Esto tomará unos 3-5 minutos. Verás mensajes como:**
```
Operation "operations/..." finished successfully.
```

---

## 📋 Paso 4: Ejecutar Despliegue Automatizado (20 minutos)

```powershell
# Navegar al directorio de despliegue
cd deployment\gcp

# Ejecutar script con tu proyecto
.\deploy-windows.ps1 -ProjectId "argon-edge-478500-i8" -Region "us-central1"

# El script te pedirá:
# 1. Contraseña para la base de datos (elige una segura, ej: "CMMS2025!Secure")
# 2. Confirmación para continuar

# Luego se ejecutará automáticamente:
# ✓ Crear Cloud SQL (8 min)
# ✓ Crear Storage (1 min)
# ✓ Configurar Pub/Sub (1 min)
# ✓ Desplegar Backend (8 min)
# ✓ Configurar Frontend (2 min)
```

---

## 📋 Paso 5: Crear Superusuario (3 minutos)

### Opción A: Cloud Shell (Más Fácil)

1. Ir a: https://console.cloud.google.com
2. Hacer clic en el icono `>_` (Cloud Shell) arriba a la derecha
3. Esperar a que se active Cloud Shell
4. Ejecutar:

```bash
# Conectar al servicio
gcloud run services proxy cmms-backend --region=us-central1 --project=argon-edge-478500-i8
```

5. Abrir otra terminal de Cloud Shell (clic en `+`)
6. Ejecutar:

```bash
# Crear superusuario
python manage.py createsuperuser

# Ingresar:
# Email: admin@cmms.com
# Password: (tu contraseña segura)
# Password (again): (repetir contraseña)
```

### Opción B: Local con Cloud SQL Proxy

```powershell
# Descargar Cloud SQL Proxy
$proxyUrl = "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe"
Invoke-WebRequest -Uri $proxyUrl -OutFile "cloud_sql_proxy.exe"

# Ejecutar proxy (dejar corriendo en esta terminal)
.\cloud_sql_proxy.exe -instances=argon-edge-478500-i8:us-central1:cmms-db=tcp:5432

# En OTRA terminal PowerShell:
cd backend
.\venv\Scripts\Activate.ps1

# Configurar variables
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "5432"
$env:DB_NAME = "cmms_prod"
$env:DB_USER = "cmms_user"
$env:DB_PASSWORD = "TuContraseñaDeBaseDeDatos"

# Crear superusuario
python manage.py createsuperuser
```

---

## 🎉 ¡Listo!

### URLs de tu Aplicación

Al finalizar el despliegue verás:

```
Backend:  https://cmms-backend-xxx-uc.a.run.app
API Docs: https://cmms-backend-xxx-uc.a.run.app/api/docs/
```

### Probar el Sistema

1. **Abrir API Docs**: Ir a la URL del backend + `/api/docs/`
2. **Hacer Login**: 
   - Clic en `POST /api/v1/auth/login/`
   - Clic en "Try it out"
   - Ingresar:
     ```json
     {
       "email": "admin@cmms.com",
       "password": "tu-contraseña"
     }
     ```
   - Clic en "Execute"
3. **Copiar Token**: Copiar el `access` token de la respuesta
4. **Autorizar**: 
   - Clic en el botón "Authorize" arriba
   - Pegar: `Bearer tu-token-aqui`
   - Clic en "Authorize"
5. **Probar Endpoints**: Ahora puedes probar todos los endpoints

---

## 💰 Costos

### Tu Configuración Actual
- Cloud SQL (db-f1-micro): ~$7/mes
- Cloud Run (auto-scaling): ~$5/mes
- Cloud Storage: ~$0.20/mes
- **Total: ~$12/mes**

### Con tu Crédito Gratis
- Tienes $281.63 disponibles
- Duración: ~23 meses gratis
- Después: ~$12/mes

---

## 🔄 Comandos Útiles

### Ver Logs del Backend
```powershell
gcloud run services logs tail cmms-backend --region=us-central1 --project=argon-edge-478500-i8
```

### Ver Estado de Recursos
```powershell
# Cloud SQL
gcloud sql instances describe cmms-db --project=argon-edge-478500-i8

# Cloud Run
gcloud run services describe cmms-backend --region=us-central1 --project=argon-edge-478500-i8

# Storage Buckets
gcloud storage buckets list --project=argon-edge-478500-i8
```

### Actualizar Backend
```powershell
cd backend
gcloud run deploy cmms-backend --source . --region=us-central1 --project=argon-edge-478500-i8
```

### Ver Costos
```powershell
# Abrir página de facturación
Start-Process "https://console.cloud.google.com/billing?project=argon-edge-478500-i8"
```

---

## 🆘 Troubleshooting

### Error: "gcloud not found" después de instalar
**Solución**: Cerrar TODAS las terminales PowerShell y abrir una nueva

### Error: "Permission denied"
**Solución**: 
```powershell
# Verificar que estás autenticado
gcloud auth list

# Re-autenticar si es necesario
gcloud auth login
```

### Error: "API not enabled"
**Solución**: Ejecutar nuevamente el Paso 3 para habilitar APIs

### Error: "Cloud SQL connection failed"
**Solución**:
```powershell
# Verificar que la instancia esté corriendo
gcloud sql instances describe cmms-db --project=argon-edge-478500-i8

# Si está detenida, iniciarla
gcloud sql instances patch cmms-db --activation-policy=ALWAYS --project=argon-edge-478500-i8
```

---

## 📞 Recursos

### Consolas de GCP
- **Cloud Console**: https://console.cloud.google.com/home/dashboard?project=argon-edge-478500-i8
- **Cloud Run**: https://console.cloud.google.com/run?project=argon-edge-478500-i8
- **Cloud SQL**: https://console.cloud.google.com/sql/instances?project=argon-edge-478500-i8
- **Storage**: https://console.cloud.google.com/storage/browser?project=argon-edge-478500-i8
- **Facturación**: https://console.cloud.google.com/billing?project=argon-edge-478500-i8

### Documentación
- **Guía Completa**: `GUIA_DESPLIEGUE_WINDOWS.md`
- **Script**: `deployment/gcp/deploy-windows.ps1`
- **Reporte de Calidad**: `FINAL_QUALITY_REPORT_2025-11-16.md`

---

## ✅ Checklist de Despliegue

- [ ] Google Cloud SDK instalado
- [ ] Nueva terminal PowerShell abierta
- [ ] Autenticado en GCP (`gcloud auth login`)
- [ ] Proyecto configurado (`argon-edge-478500-i8`)
- [ ] APIs habilitadas
- [ ] Script de despliegue ejecutado
- [ ] Backend desplegado
- [ ] Superusuario creado
- [ ] Sistema probado

---

## 🎯 Resumen de Comandos

```powershell
# 1. Instalar SDK (ejecutar una vez)
# Descargar desde: https://cloud.google.com/sdk/docs/install#windows
# Luego cerrar y abrir NUEVA terminal

# 2. Configurar (en nueva terminal)
gcloud auth login
gcloud config set project argon-edge-478500-i8
gcloud config set compute/region us-central1

# 3. Habilitar APIs
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com storage-api.googleapis.com pubsub.googleapis.com --project=argon-edge-478500-i8

# 4. Desplegar
cd deployment\gcp
.\deploy-windows.ps1 -ProjectId "argon-edge-478500-i8"

# 5. Crear superusuario (en Cloud Shell)
gcloud run services proxy cmms-backend --region=us-central1 --project=argon-edge-478500-i8
# En otra terminal: python manage.py createsuperuser
```

---

**¡Listo para comenzar! Sigue los pasos en orden y tendrás tu sistema desplegado en ~30 minutos.**

🚀 **¡Éxito con tu despliegue!**
