# Procedimientos de Despliegue - Sistema CMMS

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Despliegue Inicial](#despliegue-inicial)
3. [Actualizaciones](#actualizaciones)
4. [Rollback](#rollback)
5. [Ambientes](#ambientes)
6. [Checklist de Despliegue](#checklist-de-despliegue)

---

## Requisitos Previos

### Herramientas Necesarias

- Google Cloud SDK (`gcloud`)
- Docker
- Node.js 20+
- Python 3.11+
- Firebase CLI
- Git

### Permisos Requeridos

- Editor de proyecto GCP
- Acceso a Cloud Run
- Acceso a Cloud SQL
- Acceso a Cloud Storage
- Acceso a Firebase Hosting

### Configuración Inicial

1. **Instalar Google Cloud SDK:**
   ```bash
   # Windows
   (New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
   & $env:Temp\GoogleCloudSDKInstaller.exe
   
   # Linux/Mac
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Autenticar con GCP:**
   ```bash
   gcloud auth login
   gcloud config set project PROJECT_ID
   ```

3. **Instalar Firebase CLI:**
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

---

## Despliegue Inicial

### Paso 1: Configurar Infraestructura GCP

#### 1.1 Crear Cloud SQL Instance

```bash
# Crear instancia PostgreSQL
gcloud sql instances create cmms-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --backup \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --enable-bin-log

# Crear base de datos
gcloud sql databases create cmms_prod \
  --instance=cmms-db

# Crear usuario
gcloud sql users create cmms_user \
  --instance=cmms-db \
  --password=SECURE_PASSWORD
```

#### 1.2 Crear Cloud Storage Buckets

```bash
# Bucket para documentos
gsutil mb -l us-central1 -c STANDARD gs://PROJECT_ID-cmms-documents
gsutil versioning set on gs://PROJECT_ID-cmms-documents

# Bucket para modelos ML
gsutil mb -l us-central1 -c STANDARD gs://PROJECT_ID-cmms-ml-models

# Bucket para reportes
gsutil mb -l us-central1 -c STANDARD gs://PROJECT_ID-cmms-reports

# Configurar lifecycle para reportes (eliminar después de 90 días)
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://PROJECT_ID-cmms-reports
```

#### 1.3 Configurar Cloud Pub/Sub

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

#### 1.4 Configurar Secret Manager

```bash
# Crear secrets
echo -n "your-secret-key" | gcloud secrets create django-secret-key --data-file=-
echo -n "your-db-password" | gcloud secrets create db-password --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create jwt-secret --data-file=-
echo -n "your-telegram-token" | gcloud secrets create telegram-bot-token --data-file=-

# Dar permisos al service account
gcloud secrets add-iam-policy-binding django-secret-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Paso 2: Desplegar Backend

#### 2.1 Preparar Código

```bash
cd backend

# Crear archivo .env.production
cat > .env.production <<EOF
DEBUG=False
ALLOWED_HOSTS=.run.app
DATABASE_URL=postgresql://cmms_user:PASSWORD@/cmms_prod?host=/cloudsql/PROJECT_ID:us-central1:cmms-db
REDIS_URL=redis://REDIS_IP:6379/0
GCS_BUCKET_NAME=PROJECT_ID-cmms-documents
PUBSUB_PROJECT_ID=PROJECT_ID
EOF
```

#### 2.2 Build y Push Docker Image

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/cmms-backend

# O con Docker local
docker build -t gcr.io/PROJECT_ID/cmms-backend .
docker push gcr.io/PROJECT_ID/cmms-backend
```

#### 2.3 Desplegar a Cloud Run

```bash
gcloud run deploy cmms-backend \
  --image gcr.io/PROJECT_ID/cmms-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env.production | tr '\n' ',')" \
  --add-cloudsql-instances PROJECT_ID:us-central1:cmms-db \
  --min-instances 1 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80
```

#### 2.4 Ejecutar Migraciones

```bash
# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe cmms-backend --region us-central1 --format 'value(status.url)')

# Ejecutar migraciones (usando Cloud Run Jobs o manualmente)
gcloud run jobs create cmms-migrate \
  --image gcr.io/PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances PROJECT_ID:us-central1:cmms-db \
  --set-env-vars="$(cat .env.production | tr '\n' ',')" \
  --command python \
  --args manage.py,migrate

gcloud run jobs execute cmms-migrate --region us-central1
```

#### 2.5 Inicializar Datos

```bash
# Crear roles y permisos
gcloud run jobs create cmms-init-roles \
  --image gcr.io/PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances PROJECT_ID:us-central1:cmms-db \
  --set-env-vars="$(cat .env.production | tr '\n' ',')" \
  --command python \
  --args manage.py,init_roles_permissions

gcloud run jobs execute cmms-init-roles --region us-central1

# Cargar plantillas de checklist
gcloud run jobs create cmms-load-checklists \
  --image gcr.io/PROJECT_ID/cmms-backend \
  --region us-central1 \
  --set-cloudsql-instances PROJECT_ID:us-central1:cmms-db \
  --set-env-vars="$(cat .env.production | tr '\n' ',')" \
  --command python \
  --args manage.py,load_checklist_templates

gcloud run jobs execute cmms-load-checklists --region us-central1
```

### Paso 3: Desplegar Frontend

#### 3.1 Configurar Firebase

```bash
cd frontend

# Inicializar Firebase
firebase init hosting

# Configurar .env.production
cat > .env.production <<EOF
VITE_API_URL=https://cmms-backend-HASH-uc.a.run.app/api/v1
VITE_ENVIRONMENT=production
EOF
```

#### 3.2 Build y Deploy

```bash
# Build
npm run build

# Deploy
firebase deploy --only hosting

# O con target específico
firebase target:apply hosting production cmms-prod
firebase deploy --only hosting:production
```

### Paso 4: Desplegar Bot de Telegram

#### 4.1 Preparar Código

```bash
cd telegram-bot

# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/cmms-telegram-bot
```

#### 4.2 Desplegar a Cloud Run

```bash
gcloud run deploy cmms-telegram-bot \
  --image gcr.io/PROJECT_ID/cmms-telegram-bot \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars="TELEGRAM_TOKEN=YOUR_TOKEN,API_URL=https://cmms-backend-HASH-uc.a.run.app" \
  --min-instances 0 \
  --max-instances 5 \
  --memory 512Mi \
  --cpu 1
```

#### 4.3 Configurar Webhook

```bash
# Obtener URL del bot
BOT_URL=$(gcloud run services describe cmms-telegram-bot --region us-central1 --format 'value(status.url)')

# Configurar webhook en Telegram
curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" \
  -d "url=$BOT_URL/webhook"
```

### Paso 5: Configurar Cloud Composer

#### 5.1 Crear Ambiente

```bash
gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-2 \
  --disk-size 30GB \
  --node-count 3
```

#### 5.2 Subir DAGs

```bash
# Obtener bucket de DAGs
DAGS_BUCKET=$(gcloud composer environments describe cmms-composer \
  --location us-central1 \
  --format="value(config.dagGcsPrefix)")

# Subir DAGs
gsutil -m cp airflow/dags/*.py $DAGS_BUCKET/
```

#### 5.3 Configurar Variables y Connections

```bash
# Variables
gcloud composer environments run cmms-composer \
  --location us-central1 \
  variables set -- \
  api_url https://cmms-backend-HASH-uc.a.run.app

# Connections
gcloud composer environments run cmms-composer \
  --location us-central1 \
  connections add cmms_db \
  --conn-type postgres \
  --conn-host /cloudsql/PROJECT_ID:us-central1:cmms-db \
  --conn-login cmms_user \
  --conn-password PASSWORD \
  --conn-schema cmms_prod
```

### Paso 6: Configurar Monitoreo

#### 6.1 Crear Dashboard

```bash
# Importar dashboard predefinido
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

#### 6.2 Configurar Alertas

```bash
# Crear canal de notificación
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=admin@cmms.com

# Crear políticas de alerta
gcloud alpha monitoring policies create --config-from-file=monitoring/alerts.yaml
```

### Paso 7: Verificación Post-Despliegue

#### 7.1 Health Checks

```bash
# Backend
curl https://cmms-backend-HASH-uc.a.run.app/api/v1/core/health/

# Frontend
curl https://cmms-prod.web.app/

# Bot
curl https://cmms-telegram-bot-HASH-uc.a.run.app/health
```

#### 7.2 Smoke Tests

```bash
# Login
curl -X POST https://cmms-backend-HASH-uc.a.run.app/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cmms.com","password":"password"}'

# Listar activos
curl https://cmms-backend-HASH-uc.a.run.app/api/v1/assets/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Actualizaciones

### Actualización de Backend

#### 1. Preparar Nueva Versión

```bash
cd backend

# Actualizar código
git pull origin main

# Build nueva imagen con tag de versión
gcloud builds submit --tag gcr.io/PROJECT_ID/cmms-backend:v1.1.0
```

#### 2. Desplegar con Zero Downtime

```bash
# Desplegar nueva versión sin tráfico
gcloud run deploy cmms-backend \
  --image gcr.io/PROJECT_ID/cmms-backend:v1.1.0 \
  --no-traffic \
  --tag v1-1-0

# Verificar nueva versión
curl https://v1-1-0---cmms-backend-HASH-uc.a.run.app/api/v1/core/health/

# Migrar tráfico gradualmente
gcloud run services update-traffic cmms-backend \
  --to-revisions=v1-1-0=10

# Monitorear errores
# Si todo OK, migrar 100%
gcloud run services update-traffic cmms-backend \
  --to-revisions=v1-1-0=100
```

#### 3. Ejecutar Migraciones

```bash
# Si hay migraciones de BD
gcloud run jobs create cmms-migrate-v1-1-0 \
  --image gcr.io/PROJECT_ID/cmms-backend:v1.1.0 \
  --region us-central1 \
  --set-cloudsql-instances PROJECT_ID:us-central1:cmms-db \
  --command python \
  --args manage.py,migrate

gcloud run jobs execute cmms-migrate-v1-1-0 --region us-central1
```

### Actualización de Frontend

```bash
cd frontend

# Actualizar código
git pull origin main

# Build
npm run build

# Deploy
firebase deploy --only hosting

# Verificar
curl https://cmms-prod.web.app/
```

### Actualización de DAGs

```bash
# Subir DAGs actualizados
gsutil -m cp airflow/dags/*.py $DAGS_BUCKET/

# Los DAGs se actualizan automáticamente
```

---

## Rollback

### Rollback de Backend

#### Opción 1: Cambiar Tráfico a Versión Anterior

```bash
# Listar revisiones
gcloud run revisions list --service=cmms-backend --region=us-central1

# Cambiar tráfico a revisión anterior
gcloud run services update-traffic cmms-backend \
  --to-revisions=PREVIOUS_REVISION=100
```

#### Opción 2: Redesplegar Versión Anterior

```bash
gcloud run deploy cmms-backend \
  --image gcr.io/PROJECT_ID/cmms-backend:v1.0.0 \
  --region us-central1
```

### Rollback de Base de Datos

```bash
# Listar backups
gcloud sql backups list --instance=cmms-db

# Restaurar backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=cmms-db \
  --backup-project=PROJECT_ID
```

### Rollback de Frontend

```bash
# Firebase mantiene historial de deploys
firebase hosting:rollback
```

---

## Ambientes

### Desarrollo (Local)

```bash
# Backend
docker-compose up -d

# Frontend
cd frontend
npm run dev
```

### Staging

```bash
# Backend
gcloud run deploy cmms-backend-staging \
  --image gcr.io/PROJECT_ID/cmms-backend:staging \
  --region us-central1

# Frontend
firebase deploy --only hosting:staging
```

### Producción

Ver sección [Despliegue Inicial](#despliegue-inicial)

---

## Checklist de Despliegue

### Pre-Despliegue

- [ ] Código revisado y aprobado (Pull Request)
- [ ] Tests pasando (unit, integration, security)
- [ ] Changelog actualizado
- [ ] Documentación actualizada
- [ ] Backup de base de datos creado
- [ ] Ventana de mantenimiento comunicada (si aplica)
- [ ] Rollback plan preparado

### Durante Despliegue

- [ ] Build exitoso
- [ ] Migraciones ejecutadas sin errores
- [ ] Health checks pasando
- [ ] Smoke tests exitosos
- [ ] Logs sin errores críticos
- [ ] Métricas normales

### Post-Despliegue

- [ ] Verificación funcional completa
- [ ] Monitoreo activo por 1 hora
- [ ] Usuarios notificados de nueva versión
- [ ] Documentación de despliegue actualizada
- [ ] Incidentes documentados (si hubo)
- [ ] Retrospectiva programada (si hubo problemas)

---

## Contactos de Emergencia

- **DevOps Lead**: [Nombre] - [Email] - [Teléfono]
- **Technical Lead**: [Nombre] - [Email] - [Teléfono]
- **GCP Support**: [Plan de Soporte]

---

**Versión del Documento:** 1.0  
**Última Actualización:** 2024-11-13  
**Próxima Revisión:** Después de cada despliegue mayor
