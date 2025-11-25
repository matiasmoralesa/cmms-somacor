# ✅ Verificación Pre-Despliegue

**Proyecto**: argon-edge-478500-i8  
**Fecha**: 16 de Noviembre, 2025

---

## 📋 Checklist de Verificación

### 1. Configuración de GCP ✅

- [x] **Google Cloud SDK instalado**
- [x] **Sesión iniciada**: electronightx@gmail.com
- [x] **Proyecto configurado**: argon-edge-478500-i8
- [x] **Región configurada**: us-central1
- [x] **APIs habilitadas**:
  - [x] sqladmin.googleapis.com
  - [x] run.googleapis.com
  - [x] cloudbuild.googleapis.com
  - [x] storage-api.googleapis.com
  - [x] storage.googleapis.com
  - [x] pubsub.googleapis.com
  - [x] secretmanager.googleapis.com
  - [x] artifactregistry.googleapis.com

### 2. Configuración del Backend ✅

- [x] **requirements.txt**: Todas las dependencias incluidas
  - Django 4.2.7
  - djangorestframework
  - psycopg2-binary (para PostgreSQL)
  - gunicorn (servidor WSGI)
  - google-cloud-storage
  - drf-spectacular (documentación API)

- [x] **settings/production.py**: Configurado correctamente
  - DEBUG = False
  - ALLOWED_HOSTS = ['*'] (Cloud Run maneja seguridad)
  - Database con Unix Socket para Cloud SQL
  - CORS habilitado
  - Static files configurados
  - Security headers configurados

- [x] **wsgi.py**: Configurado para producción
  - DJANGO_SETTINGS_MODULE = config.settings.production

- [x] **Migraciones**: 28 migraciones listas para aplicar

### 3. Script de Despliegue ✅

- [x] **desplegar-final.ps1**: Corregido y listo
  - Sin errores de sintaxis
  - Comando Cloud SQL corregido (sin --enable-bin-log)
  - Configuración correcta para PostgreSQL
  - Manejo de errores implementado

### 4. Estructura del Proyecto ✅

```
proyecto v2/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py ✅
│   │   ├── wsgi.py ✅
│   │   └── urls.py
│   ├── apps/
│   │   ├── core/ ✅
│   │   ├── authentication/ ✅
│   │   ├── assets/ ✅
│   │   ├── work_orders/ ✅
│   │   ├── maintenance/ ✅
│   │   ├── inventory/ ✅
│   │   ├── checklists/ ✅
│   │   ├── predictions/ ✅
│   │   └── notifications/ ✅
│   ├── requirements.txt ✅
│   └── manage.py
├── frontend/
│   └── (React app)
└── deployment/
    └── gcp/
        └── scripts/
```

---

## 🔍 Cambios Realizados

### 1. Configuración de Producción Corregida

**Archivo**: `backend/config/settings/production.py`

**Cambios**:
```python
# Antes:
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Después:
ALLOWED_HOSTS = ['*']  # Cloud Run maneja esto de forma segura
```

```python
# Antes:
DATABASES = {
    'default': dj_database_url.config(...)
}

# Después:
# Soporte para Unix Socket de Cloud SQL
if os.getenv('DB_HOST', '').startswith('/cloudsql'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'cmms_prod'),
            'USER': os.getenv('DB_USER', 'cmms_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
        }
    }
```

```python
# Antes:
SECURE_SSL_REDIRECT = True

# Después:
SECURE_SSL_REDIRECT = False  # Cloud Run ya maneja HTTPS
```

```python
# Antes:
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Después:
CORS_ALLOW_ALL_ORIGINS = True  # Permitir todos por ahora
```

### 2. Script de Despliegue Corregido

**Archivo**: `desplegar-final.ps1`

**Cambios**:
```powershell
# Antes (ERROR):
gcloud sql instances create cmms-db \
    --enable-bin-log \  # Solo para MySQL
    --retained-transaction-log-days=7  # Solo para MySQL

# Después (CORRECTO):
gcloud sql instances create cmms-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=$dbPassword \
    --backup-start-time=03:00 \
    --retained-backups-count=7
```

---

## 🎯 Recursos que se Crearán

### Cloud SQL
```
Nombre: cmms-db
Tipo: PostgreSQL 15
Tier: db-f1-micro (0.6 GB RAM, compartido)
Región: us-central1
Base de datos: cmms_prod
Usuario: cmms_user
Backups: Diarios a las 3:00 AM, retención 7 días
```

### Cloud Storage (4 Buckets)
```
1. argon-edge-478500-i8-cmms-documents
2. argon-edge-478500-i8-cmms-ml-models
3. argon-edge-478500-i8-cmms-reports
4. argon-edge-478500-i8-cmms-backups
```

### Cloud Pub/Sub (3 Topics + Subscriptions)
```
1. notifications + notifications-sub
2. events + events-sub
3. alerts + alerts-sub
```

### Cloud Run
```
Nombre: cmms-backend
Región: us-central1
Memoria: 1 GB
CPU: 1 vCPU
Instancias: 0-10 (auto-scaling)
Conexión: Cloud SQL via Unix Socket
```

---

## 💰 Costos Estimados

### Configuración Actual (db-f1-micro)
- **Cloud SQL**: ~$7/mes
- **Cloud Run**: ~$5/mes (con auto-scaling a 0)
- **Cloud Storage**: ~$0.20/mes (10 GB)
- **Pub/Sub**: ~$0.50/mes (bajo uso)
- **Cloud Build**: Gratis (primeras 120 builds/día)

**Total**: ~$12-13/mes

### Con tu Crédito
- **Crédito disponible**: $281.63
- **Duración**: ~21 meses gratis
- **Después**: ~$12-13/mes

---

## ⚙️ Variables de Entorno

El script configurará estas variables en Cloud Run:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DB_NAME=cmms_prod
DB_USER=cmms_user
DB_PASSWORD=[tu contraseña]
DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db
```

---

## 🚀 Proceso de Despliegue

### Fase 1: Habilitar APIs (3-5 min) ✅
Ya completado en tu sesión anterior.

### Fase 2: Cloud SQL (8-10 min)
```
1. Crear instancia PostgreSQL
2. Crear base de datos cmms_prod
3. Crear usuario cmms_user
```

### Fase 3: Cloud Storage (1-2 min)
```
1. Crear 4 buckets
2. Configurar permisos
```

### Fase 4: Pub/Sub (1 min)
```
1. Crear 3 topics
2. Crear 3 subscriptions
```

### Fase 5: Cloud Run (8-10 min)
```
1. Crear Dockerfile
2. Build de imagen Docker
3. Push a Artifact Registry
4. Deploy a Cloud Run
5. Configurar variables de entorno
6. Conectar con Cloud SQL
```

**Tiempo Total**: ~20-25 minutos

---

## ✅ Todo Listo para Desplegar

### Comando para Ejecutar
```powershell
.\desplegar-final.ps1
```

### Lo que te Pedirá
1. **Contraseña de base de datos**: Usa algo simple sin caracteres especiales
   - Ejemplo: `CMMS2025Secure`
   - Evita: `!@#$%^&*()` en la contraseña

2. **Confirmación**: Presiona Enter para continuar

### Lo que Verás
- Mensajes de progreso en verde
- Barras de progreso de gcloud
- Confirmaciones de recursos creados
- URL final del backend

### Resultado Final
```
Backend URL: https://cmms-backend-xxxxx-uc.a.run.app
API Docs: https://cmms-backend-xxxxx-uc.a.run.app/api/docs/
```

---

## 🆘 Si Algo Sale Mal

### Error: "Billing not enabled"
**Solución**: Ir a https://console.cloud.google.com/billing y habilitar facturación

### Error: "Permission denied"
**Solución**: Verificar que tienes rol de Editor u Owner en el proyecto

### Error: "Quota exceeded"
**Solución**: Verificar cuotas en https://console.cloud.google.com/iam-admin/quotas

### Error en Build
**Solución**: Ver logs con `gcloud builds list` y `gcloud builds log BUILD_ID`

---

## 📊 Monitoreo Durante Despliegue

Puedes abrir otra terminal y ejecutar:

```powershell
# Ver estado de Cloud SQL
gcloud sql operations list --instance=cmms-db --project=argon-edge-478500-i8

# Ver builds en progreso
gcloud builds list --ongoing --project=argon-edge-478500-i8

# Ver servicios de Cloud Run
gcloud run services list --project=argon-edge-478500-i8
```

O abrir Cloud Console:
```powershell
Start-Process "https://console.cloud.google.com/home/dashboard?project=argon-edge-478500-i8"
```

---

## ✅ Verificación Final

Antes de ejecutar, confirma:

- [x] Estás en el directorio correcto: `proyecto v2`
- [x] El archivo `desplegar-final.ps1` existe
- [x] El directorio `backend` existe
- [x] Tienes conexión a internet estable
- [x] Tu terminal tiene permisos de administrador (opcional pero recomendado)

---

## 🎯 Próximos Pasos Después del Despliegue

1. **Crear Superusuario**
   ```bash
   # En Cloud Shell
   gcloud run services proxy cmms-backend --region=us-central1
   python manage.py createsuperuser
   ```

2. **Probar la API**
   - Ir a: https://cmms-backend-xxxxx-uc.a.run.app/api/docs/
   - Hacer login con el superusuario
   - Probar endpoints

3. **Verificar Recursos**
   - Cloud SQL: https://console.cloud.google.com/sql
   - Cloud Run: https://console.cloud.google.com/run
   - Storage: https://console.cloud.google.com/storage

---

**TODO ESTÁ LISTO PARA DESPLEGAR** ✅

Ejecuta: `.\desplegar-final.ps1`

🚀 **¡Buena suerte!**
