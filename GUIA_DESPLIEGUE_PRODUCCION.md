# Guía Paso a Paso: Despliegue a Producción en GCP

## 📋 Índice
1. [Requisitos Previos](#requisitos-previos)
2. [Fase 1: Preparación](#fase-1-preparación)
3. [Fase 2: Configuración de GCP](#fase-2-configuración-de-gcp)
4. [Fase 3: Despliegue del Backend](#fase-3-despliegue-del-backend)
5. [Fase 4: Despliegue del Frontend](#fase-4-despliegue-del-frontend)
6. [Fase 5: Configuración de Servicios](#fase-5-configuración-de-servicios)
7. [Fase 6: Verificación](#fase-6-verificación)
8. [Fase 7: Monitoreo](#fase-7-monitoreo)

---

## Requisitos Previos

### 1. Cuenta de Google Cloud Platform
```bash
# Crear cuenta en: https://console.cloud.google.com
# Activar facturación
# Crear un nuevo proyecto
```

### 2. Herramientas Instaladas
```bash
# Google Cloud SDK
gcloud --version

# Docker
docker --version

# Node.js y npm
node --version
npm --version

# Python
python --version

# Firebase CLI
firebase --version
```

### 3. Instalar Herramientas (si no las tienes)

**Windows:**
```powershell
# Google Cloud SDK
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# Firebase CLI
npm install -g firebase-tools

# Docker Desktop
# Descargar de: https://www.docker.com/products/docker-desktop
```

---

## Fase 1: Preparación

### Paso 1.1: Configurar Variables de Entorno

Crea un archivo `production.env` con tus configuraciones:

```bash
# production.env
PROJECT_ID=tu-proyecto-gcp
REGION=us-central1
DB_PASSWORD=TuPasswordSegura123!
DJANGO_SECRET_KEY=tu-secret-key-muy-larga-y-segura
JWT_SECRET=otro-secret-key-para-jwt
TELEGRAM_BOT_TOKEN=tu-token-de-telegram
SENDGRID_API_KEY=tu-api-key-de-sendgrid
```

### Paso 1.2: Autenticar con GCP

```bash
# Iniciar sesión
gcloud auth login

# Configurar proyecto
gcloud config set project TU_PROJECT_ID

# Verificar configuración
gcloud config list
```

### Paso 1.3: Habilitar APIs Necesarias

```bash
# Habilitar todas las APIs necesarias
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  pubsub.googleapis.com \
  composer.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com
```

---

## Fase 2: Configuración de GCP

### Paso 2.1: Crear Cloud SQL (Base de Datos)

```bash
# Crear instancia PostgreSQL
gcloud sql instances create cmms-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --backup \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04

# Esperar a que se cree (puede tomar 5-10 minutos)
gcloud sql instances describe cmms-db

# Crear base de datos
gcloud sql databases create cmms_prod --instance=cmms-db

# Crear usuario
gcloud sql users create cmms_user \
  --instance=cmms-db \
  --password=TU_PASSWORD_SEGURA
```

### Paso 2.2: Crear Cloud Storage Buckets

```bash
# Bucket para documentos
gsutil mb -l us-central1 gs://TU_PROJECT_ID-cmms-documents
gsutil versioning set on gs://TU_PROJECT_ID-cmms-documents

# Bucket para modelos ML
gsutil mb -l us-central1 gs://TU_PROJECT_ID-cmms-ml-models

# Bucket para reportes
gsutil mb -l us-central1 gs://TU_PROJECT_ID-cmms-reports

# Configurar CORS para documentos
cat > cors.json <<EOF
[
  {
    "origin": ["https://tu-dominio.com"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set cors.json gs://TU_PROJECT_ID-cmms-documents
```

### Paso 2.3: Configurar Cloud Pub/Sub

```bash
# Crear topics
gcloud pubsub topics create cmms-notifications
gcloud pubsub topics create cmms-events
gcloud pubsub topics create cmms-alerts

# Crear subscriptions
gcloud pubsub subscriptions create cmms-notifications-sub \
  --topic=cmms-notifications \
  --ack-deadline=60

gcloud pubsub subscriptions create cmms-telegram-sub \
  --topic=cmms-notifications \
  --ack-deadline=60
```

### Paso 2.4: Configurar Secret Manager

```bash
# Crear secrets
echo -n "tu-django-secret-key-muy-larga" | \
  gcloud secrets create django-secret-key --data-file=-

echo -n "TU_PASSWORD_SEGURA" | \
  gcloud secrets create db-password --data-file=-

echo -n "tu-jwt-secret-key" | \
  gcloud secrets create jwt-secret --data-file=-

echo -n "TU_TELEGRAM_BOT_TOKEN" | \
  gcloud secrets create telegram-bot-token --data-file=-

# Dar permisos al service account de Cloud Run
PROJECT_NUMBER=$(gcloud projects describe TU_PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding django-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Fase 3: Despliegue del Backend

### Paso 3.1: Preparar el Código

```bash
cd backend

# Crear archivo .env.production
cat > .env.production <<EOF
DEBUG=False
ALLOWED_HOSTS=.run.app,.tu-dominio.com
DATABASE_URL=postgresql://cmms_user:PASSWORD@/cmms_prod?host=/cloudsql/TU_PROJECT_ID:us-central1:cmms-db
REDIS_URL=redis://REDIS_IP:6379/0
GCS_BUCKET_NAME=TU_PROJECT_ID-cmms-documents
PUBSUB_PROJECT_ID=TU_PROJECT_ID
SECRET_KEY=projects/TU_PROJECT_ID/secrets/django-secret-key/versions/latest
JWT_SECRET=projects/TU_PROJECT_ID/secrets/jwt-secret/versions/latest
EOF
```

### Paso 3.2: Build y Push de la Imagen Docker

```bash
# Opción 1: Usar Cloud Build (recomendado)
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-backend

# Opción 2: Build local y push
docker build -t gcr.io/TU_PROJECT_ID/cmms-backend .
docker push gcr.io/TU_PROJECT_ID/cmms-backend
```

### Paso 3.3: Desplegar a Cloud Run

```bash
gcloud run deploy cmms-backend \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DEBUG=False,ALLOWED_HOSTS=.run.app" \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest,JWT_SECRET=jwt-secret:latest" \
  --add-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --min-instances 1 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80

# Obtener URL del servicio
gcloud run services describe cmms-backend \
  --region us-central1 \
  --format 'value(status.url)'
```

### Paso 3.4: Ejecutar Migraciones

```bash
# Crear Cloud Run Job para migraciones
gcloud run jobs create cmms-migrate \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,migrate

# Ejecutar migraciones
gcloud run jobs execute cmms-migrate --region us-central1 --wait

# Ver logs
gcloud run jobs executions logs read --job cmms-migrate --region us-central1
```

### Paso 3.5: Inicializar Datos del Sistema

```bash
# Crear roles y permisos
gcloud run jobs create cmms-init-roles \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,init_roles_permissions

gcloud run jobs execute cmms-init-roles --region us-central1 --wait

# Cargar plantillas de checklist
gcloud run jobs create cmms-load-checklists \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,load_checklist_templates

gcloud run jobs execute cmms-load-checklists --region us-central1 --wait

# Crear superusuario (interactivo)
gcloud run jobs create cmms-createsuperuser \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,createsuperuser

gcloud run jobs execute cmms-createsuperuser --region us-central1
```

### Paso 3.6: Generar Datos de Demostración (Opcional)

```bash
gcloud run jobs create cmms-demo-data \
  --image gcr.io/TU_PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,generate_demo_data

gcloud run jobs execute cmms-demo-data --region us-central1 --wait
```

---

## Fase 4: Despliegue del Frontend

### Paso 4.1: Configurar Firebase

```bash
cd frontend

# Inicializar Firebase (si no lo has hecho)
firebase login
firebase init hosting

# Seleccionar tu proyecto GCP
# Directorio público: dist
# Single-page app: Yes
# Reescribir todas las URLs a index.html: Yes
```

### Paso 4.2: Configurar Variables de Entorno

```bash
# Obtener URL del backend
BACKEND_URL=$(gcloud run services describe cmms-backend \
  --region us-central1 \
  --format 'value(status.url)')

# Crear .env.production
cat > .env.production <<EOF
VITE_API_URL=${BACKEND_URL}/api/v1
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
EOF
```

### Paso 4.3: Build y Deploy

```bash
# Instalar dependencias
npm install

# Build para producción
npm run build

# Deploy a Firebase Hosting
firebase deploy --only hosting

# Obtener URL del frontend
firebase hosting:channel:list
```

---

## Fase 5: Configuración de Servicios

### Paso 5.1: Configurar Bot de Telegram

```bash
cd telegram-bot

# Build imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-telegram-bot

# Deploy a Cloud Run
gcloud run deploy cmms-telegram-bot \
  --image gcr.io/TU_PROJECT_ID/cmms-telegram-bot \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-secrets="TELEGRAM_TOKEN=telegram-bot-token:latest" \
  --set-env-vars="API_URL=${BACKEND_URL}" \
  --min-instances 0 \
  --max-instances 5 \
  --memory 512Mi

# Obtener URL del bot
BOT_URL=$(gcloud run services describe cmms-telegram-bot \
  --region us-central1 \
  --format 'value(status.url)')

# Configurar webhook en Telegram
TELEGRAM_TOKEN=$(gcloud secrets versions access latest --secret=telegram-bot-token)
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
  -d "url=${BOT_URL}/webhook"
```

### Paso 5.2: Configurar Cloud Composer (Airflow)

```bash
# Crear ambiente de Composer
gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-2 \
  --disk-size 30GB \
  --node-count 3

# Esto puede tomar 20-30 minutos
# Verificar estado
gcloud composer environments describe cmms-composer --location us-central1

# Obtener bucket de DAGs
DAGS_BUCKET=$(gcloud composer environments describe cmms-composer \
  --location us-central1 \
  --format="value(config.dagGcsPrefix)")

# Subir DAGs
cd airflow/dags
gsutil -m cp *.py ${DAGS_BUCKET}/

# Configurar variables
gcloud composer environments run cmms-composer \
  --location us-central1 \
  variables set -- api_url ${BACKEND_URL}

# Configurar conexión a base de datos
gcloud composer environments run cmms-composer \
  --location us-central1 \
  connections add cmms_db \
  --conn-type postgres \
  --conn-host /cloudsql/TU_PROJECT_ID:us-central1:cmms-db \
  --conn-login cmms_user \
  --conn-password TU_PASSWORD \
  --conn-schema cmms_prod
```

### Paso 5.3: Configurar Vertex AI (ML)

```bash
# Subir modelo inicial (si tienes uno entrenado)
gsutil cp backend/ml_models/failure_prediction_model.joblib \
  gs://TU_PROJECT_ID-cmms-ml-models/v1.0/

# Crear endpoint de Vertex AI
gcloud ai endpoints create \
  --region=us-central1 \
  --display-name=cmms-failure-prediction

# Nota: El entrenamiento y despliegue del modelo se hará
# automáticamente mediante el DAG de Cloud Composer
```

---

## Fase 6: Verificación

### Paso 6.1: Health Checks

```bash
# Backend
curl https://TU_BACKEND_URL/api/v1/core/health/

# Debe retornar:
# {"status": "healthy", "database": "connected", "storage": "accessible"}

# Frontend
curl https://TU_FRONTEND_URL/

# Debe retornar el HTML de la aplicación
```

### Paso 6.2: Pruebas de API

```bash
# Login
curl -X POST https://TU_BACKEND_URL/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@somacor.com",
    "password": "Demo2024!"
  }'

# Guardar el token
TOKEN="tu_token_aqui"

# Listar activos
curl https://TU_BACKEND_URL/api/v1/assets/ \
  -H "Authorization: Bearer ${TOKEN}"

# Crear orden de trabajo
curl -X POST https://TU_BACKEND_URL/api/v1/work-orders/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prueba de producción",
    "description": "Verificando sistema",
    "work_order_type": "PREVENTIVE",
    "priority": "MEDIUM"
  }'
```

### Paso 6.3: Pruebas del Bot de Telegram

```bash
# Abrir Telegram y buscar tu bot
# Enviar: /start
# Enviar: /status
# Verificar que responde correctamente
```

### Paso 6.4: Ejecutar Suite de Pruebas

```bash
cd backend

# Ejecutar pruebas de integración
./run_integration_tests.sh

# Ejecutar pruebas de seguridad
./run_security_tests.sh

# Revisar resultados
```

---

## Fase 7: Monitoreo

### Paso 7.1: Configurar Dashboard de Monitoreo

```bash
# Importar dashboard predefinido
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard.json
```

### Paso 7.2: Configurar Alertas

```bash
# Crear canal de notificación por email
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=admin@tu-empresa.com

# Obtener ID del canal
CHANNEL_ID=$(gcloud alpha monitoring channels list \
  --filter="displayName='Admin Email'" \
  --format="value(name)")

# Crear alerta de alta tasa de errores
gcloud alpha monitoring policies create \
  --notification-channels=${CHANNEL_ID} \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'

# Crear alerta de servicio caído
gcloud alpha monitoring policies create \
  --notification-channels=${CHANNEL_ID} \
  --display-name="Service Down" \
  --condition-display-name="Health check failing" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=60s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/health_check_failures"'
```

### Paso 7.3: Configurar Logs

```bash
# Crear sink para exportar logs a BigQuery
gcloud logging sinks create cmms-logs-bigquery \
  bigquery.googleapis.com/projects/TU_PROJECT_ID/datasets/cmms_logs \
  --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="cmms-backend"'

# Crear dataset en BigQuery
bq mk --dataset TU_PROJECT_ID:cmms_logs
```

---

## 🎯 Checklist Final de Despliegue

### Pre-Despliegue
- [ ] Cuenta GCP creada y facturación activada
- [ ] Todas las herramientas instaladas
- [ ] Variables de entorno configuradas
- [ ] APIs de GCP habilitadas
- [ ] Código revisado y probado localmente

### Infraestructura
- [ ] Cloud SQL creado y configurado
- [ ] Cloud Storage buckets creados
- [ ] Cloud Pub/Sub topics creados
- [ ] Secret Manager configurado
- [ ] Permisos IAM configurados

### Backend
- [ ] Imagen Docker construida y subida
- [ ] Cloud Run desplegado
- [ ] Migraciones ejecutadas
- [ ] Datos iniciales cargados
- [ ] Superusuario creado
- [ ] Health checks pasando

### Frontend
- [ ] Firebase configurado
- [ ] Variables de entorno configuradas
- [ ] Build de producción exitoso
- [ ] Desplegado a Firebase Hosting
- [ ] Accesible desde navegador

### Servicios
- [ ] Bot de Telegram desplegado
- [ ] Webhook de Telegram configurado
- [ ] Cloud Composer creado
- [ ] DAGs subidos
- [ ] Vertex AI configurado

### Monitoreo
- [ ] Dashboard creado
- [ ] Alertas configuradas
- [ ] Logs configurados
- [ ] Canales de notificación configurados

### Verificación
- [ ] Health checks pasando
- [ ] API respondiendo correctamente
- [ ] Frontend cargando
- [ ] Bot de Telegram funcionando
- [ ] Pruebas de integración pasando
- [ ] Pruebas de seguridad pasando

---

## 🚨 Troubleshooting Común

### Error: "Cloud SQL connection failed"
```bash
# Verificar que la instancia está corriendo
gcloud sql instances describe cmms-db

# Verificar conexión desde Cloud Run
gcloud run services describe cmms-backend --region us-central1
```

### Error: "Permission denied" en Cloud Storage
```bash
# Dar permisos al service account
gsutil iam ch serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com:objectAdmin \
  gs://TU_PROJECT_ID-cmms-documents
```

### Error: "Secret not found"
```bash
# Verificar que los secrets existen
gcloud secrets list

# Verificar permisos
gcloud secrets get-iam-policy django-secret-key
```

### Frontend no se conecta al Backend
```bash
# Verificar CORS en el backend
# Agregar el dominio del frontend a ALLOWED_HOSTS y CORS_ALLOWED_ORIGINS
```

---

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. **Revisar logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```

2. **Consultar documentación:**
   - [Cloud Run](https://cloud.google.com/run/docs)
   - [Cloud SQL](https://cloud.google.com/sql/docs)
   - [Firebase Hosting](https://firebase.google.com/docs/hosting)

3. **Contactar soporte:**
   - Email: soporte@tu-empresa.com
   - Documentación interna: Ver ADMIN_GUIDE.md

---

## 🎉 ¡Felicitaciones!

Si completaste todos los pasos, tu sistema CMMS está ahora en producción en GCP.

**Próximos pasos:**
1. Monitorear el sistema por 24-48 horas
2. Capacitar a los usuarios
3. Recopilar feedback
4. Planificar mejoras continuas

**URLs importantes:**
- Frontend: https://tu-proyecto.web.app
- Backend API: https://cmms-backend-xxx-uc.a.run.app
- Documentación API: https://cmms-backend-xxx-uc.a.run.app/api/docs/
- Cloud Console: https://console.cloud.google.com

---

**Versión:** 1.0  
**Fecha:** 2024-11-13  
**Autor:** Equipo CMMS
