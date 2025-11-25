# Completar Despliegue del Sistema CMMS

## Estado Actual

✅ **Backend** desplegado en Cloud Run: `https://cmms-backend-232652686658.us-central1.run.app`
✅ **Frontend** desplegado en Firebase Hosting: `https://cmms-somacor-prod.web.app`
✅ Base de datos PostgreSQL en Cloud SQL
✅ Bucket de almacenamiento creado: `cmms-storage-argon-edge`
⚠️ **Backend requiere redespliegue** para actualizar configuración de CORS
❌ Migraciones pendientes (si no se ejecutaron)
❌ Superusuario pendiente (si no se creó)

## Pasos para Completar el Despliegue

### Opción 1: Usar Cloud Shell (Recomendado)

1. Abre Cloud Shell en la consola de GCP
2. Clona tu repositorio o sube los archivos del backend
3. Instala las dependencias:
```bash
cd backend
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
export DATABASE_URL="postgresql://cmms_user:Santi2005@/cmms_db?host=/cloudsql/argon-edge-478500-i8:us-central1:cmms-postgres"
export GCP_PROJECT_ID="argon-edge-478500-i8"
export GCP_STORAGE_BUCKET_NAME="cmms-storage-argon-edge"
export SECRET_KEY="your-secret-key-here-change-in-production"
```

5. Ejecuta las migraciones:
```bash
python manage.py migrate
```

6. Crea el superusuario:
```bash
python manage.py createsuperuser
```

### Opción 2: Usar Cloud SQL Proxy Localmente

1. Descarga Cloud SQL Proxy:
```powershell
# Windows
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"
```

2. Inicia el proxy:
```powershell
.\cloud_sql_proxy.exe argon-edge-478500-i8:us-central1:cmms-postgres
```

3. En otra terminal, configura las variables de entorno:
```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
$env:DATABASE_URL="postgresql://cmms_user:Santi2005@localhost:5432/cmms_db"
$env:GCP_PROJECT_ID="argon-edge-478500-i8"
$env:GCP_STORAGE_BUCKET_NAME="cmms-storage-argon-edge"
$env:SECRET_KEY="your-secret-key-here-change-in-production"
```

4. Ejecuta las migraciones:
```powershell
cd backend
python manage.py migrate
```

5. Crea el superusuario:
```powershell
python manage.py createsuperuser
```

### Opción 3: Ejecutar desde Cloud Run Job (Requiere ajustes)

El job `cmms-migrate` está creado pero necesita ajustes. Para depurar:

```bash
# Ver logs del último intento
gcloud run jobs executions describe cmms-migrate-lt75j --region us-central1

# Ver logs detallados
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=cmms-migrate" --limit 50 --format json
```

## Verificar el Despliegue

Una vez completadas las migraciones, prueba el endpoint de login:

```powershell
$loginBody = @{
    email = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/login/" -Method Post -Body $loginBody -ContentType "application/json"
```

Deberías recibir un token JWT en la respuesta.

## Próximos Pasos

1. ⚠️ **URGENTE**: Redesplegar backend con nueva configuración de CORS
2. ✅ Completar migraciones (si no se ejecutaron)
3. ✅ Crear superusuario (si no se creó)
4. ✅ Frontend desplegado
5. 🔄 Configurar dominio personalizado (opcional)
6. 🔄 Configurar monitoreo y alertas

### Redesplegar Backend (ACCIÓN REQUERIDA)

El backend necesita ser redesplegado para reconocer el nuevo dominio del frontend.

**Opción 1: Usar script PowerShell**
```powershell
.\redesplegar_backend.ps1
```

**Opción 2: Comandos manuales**
```bash
gcloud config set project argon-edge-478500-i8
cd backend
gcloud builds submit --tag gcr.io/argon-edge-478500-i8/cmms-backend
gcloud run deploy cmms-backend \
  --image gcr.io/argon-edge-478500-i8/cmms-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DJANGO_SETTINGS_MODULE=config.settings.production
```

## Información de Conexión

### Frontend
- **URL Principal**: https://cmms-somacor-prod.web.app
- **URL Alternativa**: https://cmms-somacor-prod.firebaseapp.com
- **Proyecto Firebase**: cmms-somacor-prod
- **Cuenta Google**: matilqsabe@gmail.com

### Backend
- **Backend URL**: https://cmms-backend-232652686658.us-central1.run.app
- **API Docs**: https://cmms-backend-232652686658.us-central1.run.app/api/schema/swagger-ui/
- **Base de Datos**: argon-edge-478500-i8:us-central1:cmms-postgres
- **Bucket**: cmms-storage-argon-edge
- **Región**: us-central1

## Credenciales Temporales

- **Email**: admin@example.com
- **Password**: admin123

⚠️ **IMPORTANTE**: Cambia estas credenciales en producción.
