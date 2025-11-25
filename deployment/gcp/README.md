# Guía de Despliegue en Google Cloud Platform

Esta guía describe cómo desplegar el sistema CMMS completo en Google Cloud Platform.

## Requisitos Previos

### 1. Cuenta de GCP
- Cuenta de Google Cloud Platform activa
- Proyecto de GCP creado
- Facturación habilitada

### 2. Herramientas Instaladas
```bash
# Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Firebase CLI
npm install -g firebase-tools

# Docker (para desarrollo local)
# Instalar desde: https://docs.docker.com/get-docker/

# Cloud SQL Proxy (para desarrollo local)
# Se instalará automáticamente con el script
```

### 3. Permisos Necesarios
Tu cuenta debe tener los siguientes roles en el proyecto:
- `roles/owner` o
- `roles/editor` + `roles/iam.serviceAccountAdmin`

## Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd cmms-system
```

### 2. Configurar Variables de Entorno
```bash
# Configurar proyecto de GCP
export GCP_PROJECT_ID="tu-proyecto-123"
export GCP_REGION="us-central1"

# Configurar contraseña de base de datos (o se generará automáticamente)
export DB_PASSWORD="tu-contraseña-segura-aquí"

# Opcional: Configurar tier de Cloud SQL
export DB_TIER="db-f1-micro"  # Para desarrollo
# export DB_TIER="db-n1-standard-1"  # Para producción
```

### 3. Autenticarse en GCP
```bash
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
```

## Despliegue Completo (Opción Rápida)

Para desplegar toda la infraestructura de una vez:

```bash
cd deployment/gcp
chmod +x *.sh
./deploy-all.sh
```

Este script ejecutará todos los pasos necesarios automáticamente.

## Despliegue Paso a Paso (Opción Manual)

Si prefieres ejecutar cada paso manualmente:

### Paso 1: Cloud SQL
```bash
cd deployment/gcp
./01-create-cloud-sql.sh
```

Esto creará:
- Instancia de PostgreSQL 15
- Base de datos `cmms_prod`
- Usuario de base de datos
- Configuración de backups automáticos

### Paso 2: Cloud Storage
```bash
./02-create-storage-buckets.sh
```

Esto creará 4 buckets:
- `{project}-cmms-documents`: Documentos y fotos
- `{project}-cmms-ml-models`: Modelos de ML
- `{project}-cmms-reports`: Reportes generados
- `{project}-cmms-backups`: Backups del sistema

### Paso 3: Cloud Pub/Sub
```bash
./03-create-pubsub-topics.sh
```

Esto creará:
- 3 topics (notifications, events, alerts)
- 6 subscriptions
- Dead letter queue
- Configuración de permisos

### Paso 4: Backend (Cloud Run)
```bash
./04-deploy-backend-cloud-run.sh
```

Esto:
- Construirá la imagen Docker
- Desplegará a Cloud Run
- Configurará variables de entorno
- Conectará con Cloud SQL

### Paso 5: Frontend (Firebase Hosting)
```bash
./05-deploy-frontend-firebase.sh
```

Esto:
- Construirá la aplicación React
- Desplegará a Firebase Hosting
- Configurará caché y headers

## Configuración Post-Despliegue

### 1. Crear Superusuario

Opción A: Usando Cloud Run
```bash
gcloud run services update cmms-backend \
  --set-env-vars="CREATE_SUPERUSER=true,DJANGO_SUPERUSER_EMAIL=admin@cmms.com,DJANGO_SUPERUSER_PASSWORD=admin123" \
  --region us-central1

# Esperar a que se reinicie el servicio
sleep 30

# Remover las variables (por seguridad)
gcloud run services update cmms-backend \
  --remove-env-vars="CREATE_SUPERUSER,DJANGO_SUPERUSER_EMAIL,DJANGO_SUPERUSER_PASSWORD" \
  --region us-central1
```

Opción B: Usando Cloud SQL Proxy
```bash
# En una terminal, iniciar proxy
./cloud-sql-proxy-setup.sh

# En otra terminal
cd ../../backend
source .env.gcp
python manage.py createsuperuser
```

### 2. Cargar Datos Iniciales

```bash
# Conectar con Cloud SQL Proxy
./cloud-sql-proxy-setup.sh

# En otra terminal
cd ../../backend
python manage.py loaddata initial_data.json
```

### 3. Configurar Dominio Personalizado

#### Backend (Cloud Run)
```bash
# Mapear dominio
gcloud run domain-mappings create \
  --service cmms-backend \
  --domain api.tudominio.com \
  --region us-central1

# Configurar DNS según las instrucciones mostradas
```

#### Frontend (Firebase Hosting)
```bash
# En Firebase Console:
# 1. Ir a Hosting
# 2. Agregar dominio personalizado
# 3. Seguir instrucciones de verificación DNS
```

### 4. Configurar CORS

Actualizar `backend/config/settings/production.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://tudominio.com',
    'https://www.tudominio.com',
]
```

Redesplegar backend:
```bash
./04-deploy-backend-cloud-run.sh
```

## Desarrollo Local

### 1. Configurar Cloud SQL Proxy
```bash
./cloud-sql-proxy-setup.sh
```

### 2. Backend Local
```bash
cd ../../backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copiar configuración
cp ../deployment/gcp/.env.gcp .env

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### 3. Frontend Local
```bash
cd ../../frontend
npm install

# Crear .env.local
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local

# Iniciar servidor de desarrollo
npm run dev
```

## Monitoreo y Logs

### Ver Logs del Backend
```bash
# Logs en tiempo real
gcloud run services logs tail cmms-backend --region us-central1

# Últimos 100 logs
gcloud run services logs read cmms-backend --region us-central1 --limit 100

# Filtrar por nivel
gcloud run services logs read cmms-backend --region us-central1 --log-filter="severity>=ERROR"
```

### Ver Métricas
```bash
# Abrir Cloud Console
gcloud run services describe cmms-backend --region us-central1 --format="value(status.url)"

# Ver en Cloud Console
# https://console.cloud.google.com/run/detail/us-central1/cmms-backend/metrics
```

### Configurar Alertas
Ver `MONITORING_SETUP.md` para configuración detallada de alertas.

## Actualización de la Aplicación

### Actualizar Backend
```bash
cd deployment/gcp
./04-deploy-backend-cloud-run.sh
```

### Actualizar Frontend
```bash
cd deployment/gcp
./05-deploy-frontend-firebase.sh
```

### Rollback
```bash
# Backend (Cloud Run)
gcloud run services update-traffic cmms-backend \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region us-central1

# Frontend (Firebase)
firebase hosting:rollback --project $GCP_PROJECT_ID
```

## Backup y Recuperación

### Backup Manual de Base de Datos
```bash
gcloud sql backups create \
  --instance=cmms-db \
  --description="Manual backup $(date +%Y-%m-%d)"
```

### Restaurar desde Backup
```bash
# Listar backups
gcloud sql backups list --instance=cmms-db

# Restaurar
gcloud sql backups restore BACKUP_ID \
  --backup-instance=cmms-db \
  --backup-instance=cmms-db
```

### Exportar Base de Datos
```bash
gcloud sql export sql cmms-db \
  gs://${GCP_PROJECT_ID}-cmms-backups/backup-$(date +%Y%m%d).sql \
  --database=cmms_prod
```

## Costos Estimados

### Configuración Mínima (Desarrollo)
- Cloud SQL (db-f1-micro): ~$7/mes
- Cloud Run (1 instancia mínima): ~$5/mes
- Cloud Storage (10 GB): ~$0.20/mes
- Firebase Hosting: Gratis (hasta 10 GB)
- **Total: ~$12-15/mes**

### Configuración Producción
- Cloud SQL (db-n1-standard-1): ~$50/mes
- Cloud Run (auto-scaling): ~$20-50/mes
- Cloud Storage (100 GB): ~$2/mes
- Cloud Pub/Sub: ~$1/mes
- **Total: ~$75-100/mes**

## Troubleshooting

### Error: "Permission denied"
```bash
# Verificar permisos
gcloud projects get-iam-policy $GCP_PROJECT_ID

# Agregar rol necesario
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=user:tu-email@gmail.com \
  --role=roles/editor
```

### Error: "Cloud SQL connection failed"
```bash
# Verificar que la instancia esté corriendo
gcloud sql instances describe cmms-db

# Verificar conexión
gcloud sql connect cmms-db --user=cmms_user
```

### Error: "Build failed"
```bash
# Ver logs de Cloud Build
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Frontend no carga
```bash
# Verificar despliegue
firebase hosting:channel:list

# Ver logs
firebase hosting:channel:open
```

## Seguridad

### Mejores Prácticas
1. **Rotar contraseñas regularmente**
2. **Habilitar 2FA en GCP**
3. **Usar Secret Manager para secretos**
4. **Configurar VPC Service Controls**
5. **Habilitar Cloud Armor para DDoS**
6. **Revisar logs de auditoría regularmente**

### Configurar Secret Manager
```bash
# Crear secret
echo -n "mi-secreto" | gcloud secrets create db-password --data-file=-

# Dar acceso a Cloud Run
gcloud secrets add-iam-policy-binding db-password \
  --member=serviceAccount:${GCP_PROJECT_ID}@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

## Soporte

Para problemas o preguntas:
- Email: soporte@cmms.com
- Documentación: `/docs`
- Issues: GitHub Issues

## Licencia

Propietario - Todos los derechos reservados
