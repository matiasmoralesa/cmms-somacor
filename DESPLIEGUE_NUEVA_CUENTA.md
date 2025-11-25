# Guía de Despliegue en Nueva Cuenta GCP

## Información del Nuevo Proyecto

- **Cuenta GCP:** lucasgallardo497@gmail.com
- **Project ID:** cmms-somacorv2
- **Región recomendada:** us-central1

---

## Paso 1: Autenticación con la Nueva Cuenta

### 1.1 Cerrar sesión actual y autenticar con nueva cuenta

```powershell
# Listar cuentas actuales
gcloud auth list

# Autenticar con la nueva cuenta
gcloud auth login

# Esto abrirá el navegador para que inicies sesión con: lucasgallardo497@gmail.com
```

### 1.2 Configurar el proyecto

```powershell
# Establecer el proyecto
gcloud config set project cmms-somacorv2

# Verificar la configuración
gcloud config list
```

---

## Paso 2: Habilitar APIs Necesarias

```powershell
# Habilitar todas las APIs necesarias
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

---

## Paso 3: Crear Cloud SQL (Base de Datos)

### 3.1 Crear instancia de PostgreSQL

```powershell
gcloud sql instances create cmms-db `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=TU_CONTRASEÑA_SEGURA
```

### 3.2 Crear base de datos

```powershell
gcloud sql databases create cmms_db --instance=cmms-db
```

### 3.3 Crear usuario de aplicación

```powershell
gcloud sql users create cmms_user `
  --instance=cmms-db `
  --password=TU_CONTRASEÑA_USUARIO
```

### 3.4 Obtener el connection name

```powershell
gcloud sql instances describe cmms-db --format="value(connectionName)"
# Guarda este valor, lo necesitarás más adelante
# Formato: cmms-somacorv2:us-central1:cmms-db
```

---

## Paso 4: Crear Bucket de Cloud Storage

```powershell
# Obtener el número de proyecto
$PROJECT_NUMBER = gcloud projects describe cmms-somacorv2 --format="value(projectNumber)"

# Crear bucket para documentos
gsutil mb -p cmms-somacorv2 -l us-central1 gs://cmms-somacorv2-documents
```

---

## Paso 5: Desplegar Backend en Cloud Run

### 5.1 Navegar a la carpeta del backend

```powershell
cd backend
```

### 5.2 Desplegar con todas las configuraciones

```powershell
# Reemplaza los valores según tu configuración
gcloud run deploy cmms-backend `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production,DEBUG=False,SECRET_KEY=django-prod-$(Get-Random)-secret-key,DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,DB_NAME=cmms_db,DB_USER=cmms_user,DB_PASSWORD=TU_CONTRASEÑA_USUARIO,GCP_PROJECT_ID=cmms-somacorv2,GS_BUCKET_NAME=cmms-somacorv2-documents,FRONTEND_URL=https://cmms-somacorv2.web.app"
```

### 5.3 Obtener la URL del backend

```powershell
gcloud run services describe cmms-backend --region us-central1 --format="value(status.url)"
# Guarda esta URL, la necesitarás para el frontend
```

---

## Paso 6: Ejecutar Migraciones de Base de Datos

### 6.1 Crear job para migraciones

```powershell
gcloud run jobs create cmms-migrate `
  --image gcr.io/cmms-somacorv2/cmms-backend `
  --region us-central1 `
  --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production,DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,DB_NAME=cmms_db,DB_USER=cmms_user,DB_PASSWORD=TU_CONTRASEÑA_USUARIO" `
  --command python `
  --args manage.py,migrate `
  --max-retries 0 `
  --task-timeout 600
```

### 6.2 Ejecutar migraciones

```powershell
gcloud run jobs execute cmms-migrate --region us-central1
```

---

## Paso 7: Cargar Datos de Demostración

### 7.1 Crear job para cargar datos

```powershell
gcloud run jobs create load-demo-data `
  --image gcr.io/cmms-somacorv2/cmms-backend `
  --region us-central1 `
  --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production,DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,DB_NAME=cmms_db,DB_USER=cmms_user,DB_PASSWORD=TU_CONTRASEÑA_USUARIO" `
  --command python `
  --args manage.py,load_demo_data `
  --max-retries 0 `
  --task-timeout 600
```

### 7.2 Ejecutar carga de datos

```powershell
gcloud run jobs execute load-demo-data --region us-central1
```

---

## Paso 8: Configurar Firebase para Frontend

### 8.1 Crear proyecto en Firebase

1. Ve a https://console.firebase.google.com
2. Crea un nuevo proyecto llamado `cmms-somacorv2`
3. Habilita Firebase Hosting

### 8.2 Inicializar Firebase en el proyecto

```powershell
cd frontend

# Login a Firebase
firebase login

# Inicializar (si no está inicializado)
firebase init hosting

# Selecciona:
# - Use an existing project: cmms-somacorv2
# - Public directory: dist
# - Configure as single-page app: Yes
# - Set up automatic builds: No
```

### 8.3 Actualizar configuración del frontend

Edita `frontend/.env.production`:

```env
VITE_API_URL=https://TU_URL_BACKEND/api/v1
VITE_APP_NAME=CMMS
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

Reemplaza `TU_URL_BACKEND` con la URL que obtuviste en el Paso 5.3

### 8.4 Construir y desplegar frontend

```powershell
# Construir
npm run build

# Desplegar
firebase deploy --only hosting
```

---

## Paso 9: Verificación

### 9.1 Verificar backend

```powershell
# Verificar health endpoint
curl https://TU_URL_BACKEND/api/v1/inventory/spare-parts/health/
```

Deberías ver:
```json
{
  "status": "ok",
  "spare_parts_count": 27,
  "message": "Found 27 spare parts in database"
}
```

### 9.2 Verificar frontend

1. Abre https://cmms-somacorv2.web.app
2. Inicia sesión con las credenciales de demo
3. Verifica que todas las páginas funcionen

---

## Paso 10: Configurar CORS en Backend

Si tienes problemas de CORS, actualiza el backend:

```powershell
cd backend

# Edita config/settings/production.py y agrega:
# CORS_ALLOWED_ORIGINS = [
#     'https://cmms-somacorv2.web.app',
#     'https://cmms-somacorv2.firebaseapp.com',
# ]

# Redesplegar
gcloud run deploy cmms-backend --source . --region us-central1
```

---

## Credenciales de Demo

Después de cargar los datos de demostración, puedes usar:

- **Admin:**
  - Email: admin@somacor.com
  - Password: admin123

- **Supervisor:**
  - Email: supervisor@somacor.com
  - Password: supervisor123

- **Técnico:**
  - Email: tecnico@somacor.com
  - Password: tecnico123

---

## Costos Estimados

- **Cloud Run:** ~$0-5/mes (según uso)
- **Cloud SQL (db-f1-micro):** ~$10-15/mes
- **Cloud Storage:** ~$0.02/GB/mes
- **Firebase Hosting:** Gratis (plan Spark)

**Total estimado:** ~$10-20/mes

---

## Troubleshooting

### Error: "permission denied"
```powershell
# Verificar que estás autenticado con la cuenta correcta
gcloud auth list

# Cambiar de cuenta si es necesario
gcloud config set account lucasgallardo497@gmail.com
```

### Error: "API not enabled"
```powershell
# Habilitar la API específica
gcloud services enable NOMBRE_API.googleapis.com
```

### Error de conexión a base de datos
```powershell
# Verificar que el connection name sea correcto
gcloud sql instances describe cmms-db --format="value(connectionName)"

# Verificar que el usuario tenga permisos
gcloud sql users list --instance=cmms-db
```

---

## Scripts de Despliegue Automatizado

He creado scripts para facilitar el despliegue. Revisa:

- `backend/deploy-production.ps1` - Despliegue del backend
- `frontend/deploy-production.ps1` - Despliegue del frontend

---

## Soporte

Si encuentras problemas durante el despliegue:

1. Verifica los logs de Cloud Run:
   ```powershell
   gcloud run services logs read cmms-backend --region us-central1 --limit 50
   ```

2. Verifica el estado de Cloud SQL:
   ```powershell
   gcloud sql instances describe cmms-db
   ```

3. Verifica las APIs habilitadas:
   ```powershell
   gcloud services list --enabled
   ```

---

**¡Listo para desplegar!** 🚀

Sigue estos pasos en orden y tendrás tu aplicación funcionando en la nueva cuenta.
