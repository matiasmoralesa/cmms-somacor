# Airflow DAGs for CMMS System

Este directorio contiene los DAGs de Apache Airflow para automatización del sistema CMMS.

## 📁 Estructura

```
airflow/
├── dags/
│   ├── etl_ml_training_dag.py           # ETL y entrenamiento ML
│   ├── preventive_maintenance_dag.py    # Generación de mantenimiento preventivo
│   └── report_generation_dag.py         # Generación de reportes
├── scripts/
│   └── feature_engineering.py           # Script PySpark para ingeniería de características
├── airflow_variables.json               # Variables de configuración
└── README.md                            # Este archivo
```

## 🚀 Despliegue en Cloud Composer

### 1. Crear Environment

```bash
gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-4 \
  --disk-size 30 \
  --node-count 3
```

### 2. Subir DAGs

```bash
# Subir todos los DAGs
gcloud composer environments storage dags import \
  --environment cmms-composer \
  --location us-central1 \
  --source dags/

# O subir uno por uno
gcloud composer environments storage dags import \
  --environment cmms-composer \
  --location us-central1 \
  --source dags/etl_ml_training_dag.py
```

### 3. Subir Scripts

```bash
# Crear bucket si no existe
gsutil mb gs://cmms-ml-data

# Subir script de PySpark
gsutil cp scripts/feature_engineering.py gs://cmms-ml-data/scripts/
```

### 4. Configurar Variables

```bash
# Importar todas las variables desde JSON
gcloud composer environments storage data import \
  --environment cmms-composer \
  --location us-central1 \
  --source airflow_variables.json

# O configurar una por una
gcloud composer environments run cmms-composer \
  --location us-central1 \
  variables set -- gcp_project_id your-project-id

gcloud composer environments run cmms-composer \
  --location us-central1 \
  variables set -- backend_api_url https://your-backend.run.app
```

### 5. Configurar Conexiones

```bash
# Cloud SQL PostgreSQL
gcloud composer environments run cmms-composer \
  --location us-central1 \
  connections add cloudsql_postgres \
  --conn-type postgres \
  --conn-host /cloudsql/project:region:instance \
  --conn-schema cmms_db \
  --conn-login postgres \
  --conn-password <password>
```

## 📋 DAGs Disponibles

### 1. ETL and ML Training (`etl_ml_training`)

**Schedule:** Semanal (Domingos a las 2 AM)

**Descripción:** Extrae datos de Cloud SQL, procesa características con PySpark, y entrena el modelo ML.

**Tareas:**
1. Extracción de datos de activos
2. Extracción de datos de órdenes de trabajo
3. Creación de cluster Dataproc
4. Ingeniería de características (PySpark)
5. Entrenamiento del modelo
6. Despliegue a Vertex AI
7. Eliminación del cluster
8. Notificación de éxito

### 2. Preventive Maintenance (`preventive_maintenance_generator`)

**Schedule:** Diario (6 AM)

**Descripción:** Genera órdenes de trabajo para planes de mantenimiento vencidos.

**Tareas:**
1. Consulta de planes vencidos
2. Creación de órdenes de trabajo
3. Publicación de notificaciones
4. Envío de resumen por email

### 3. Report Generation (`weekly_kpi_report`)

**Schedule:** Semanal (Lunes a las 8 AM)

**Descripción:** Genera y envía reportes semanales de KPIs.

**Tareas:**
1. Extracción de datos de KPIs
2. Generación de gráficos
3. Generación de reporte PDF
4. Subida a Cloud Storage
5. Envío por email

## ⚙️ Configuración

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `gcp_project_id` | ID del proyecto GCP | `my-project-123` |
| `gcp_region` | Región de GCP | `us-central1` |
| `gcs_bucket_name` | Bucket para datos ML | `cmms-ml-data` |
| `backend_api_url` | URL del backend | `https://api.cmms.com` |
| `backend_api_token` | Token de autenticación | `Bearer token...` |
| `alert_email` | Emails para alertas | `admin@cmms.com` |
| `report_email` | Emails para reportes | `reports@cmms.com` |
| `sendgrid_api_key` | API key de SendGrid | `SG.xxx` |

### Conexiones Requeridas

| Conexión | Tipo | Descripción |
|----------|------|-------------|
| `cloudsql_postgres` | PostgreSQL | Conexión a Cloud SQL |

## 🔍 Monitoreo

### Acceder a Airflow UI

```bash
# Obtener URL del webserver
gcloud composer environments describe cmms-composer \
  --location us-central1 \
  --format="get(config.airflowUri)"
```

### Ver Logs

```bash
# Logs de un DAG específico
gcloud composer environments run cmms-composer \
  --location us-central1 \
  dags list-runs -- -d etl_ml_training

# Logs de Cloud Logging
gcloud logging read "resource.type=cloud_composer_environment" \
  --limit 50
```

## 🧪 Testing

### Test Local (Desarrollo)

```bash
# Instalar Airflow localmente
pip install apache-airflow

# Inicializar base de datos
airflow db init

# Crear usuario admin
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

# Iniciar webserver
airflow webserver --port 8080

# Iniciar scheduler (en otra terminal)
airflow scheduler
```

### Test de DAG

```bash
# Validar sintaxis del DAG
python dags/etl_ml_training_dag.py

# Test de una tarea específica
airflow tasks test etl_ml_training extract_assets_data 2024-01-01
```

### Trigger Manual

```bash
# Desde CLI
gcloud composer environments run cmms-composer \
  --location us-central1 \
  dags trigger -- etl_ml_training

# Desde UI
# 1. Ir a Airflow UI
# 2. Click en el DAG
# 3. Click en "Trigger DAG"
```

## 📦 Dependencias

### Python Packages

Los siguientes paquetes deben estar instalados en el environment de Composer:

```
apache-airflow-providers-google>=10.0.0
apache-airflow-providers-postgres>=5.0.0
pandas>=1.5.0
matplotlib>=3.5.0
seaborn>=0.12.0
requests>=2.28.0
```

### Instalar Dependencias

```bash
gcloud composer environments update cmms-composer \
  --location us-central1 \
  --update-pypi-packages-from-file requirements.txt
```

## 🔒 Seguridad

### Service Account

El environment de Composer debe tener los siguientes permisos:

- `cloudsql.client` - Para conectar a Cloud SQL
- `storage.objectAdmin` - Para leer/escribir en GCS
- `dataproc.admin` - Para crear/eliminar clusters
- `aiplatform.user` - Para desplegar modelos en Vertex AI

### Secrets

Usar Secret Manager para credenciales sensibles:

```bash
# Crear secret
gcloud secrets create backend-api-token \
  --data-file=token.txt

# Dar acceso al service account
gcloud secrets add-iam-policy-binding backend-api-token \
  --member="serviceAccount:composer-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 📊 Costos Estimados

### Cloud Composer

- Environment: ~$300/mes (n1-standard-4, 3 nodes)
- Storage: ~$5/mes

### Dataproc (por ejecución)

- Cluster (2 workers): ~$2/hora
- Ejecución semanal: ~$8/mes

### Total Estimado: ~$313/mes

## 🐛 Troubleshooting

### DAG no aparece en UI

1. Verificar sintaxis: `python dags/your_dag.py`
2. Revisar logs del scheduler
3. Verificar que el archivo esté en la carpeta correcta

### Error de conexión a Cloud SQL

1. Verificar que el proxy de Cloud SQL esté habilitado
2. Revisar permisos del service account
3. Verificar formato de host: `/cloudsql/project:region:instance`

### Error en Dataproc

1. Verificar quotas de GCP
2. Revisar configuración del cluster
3. Verificar que el script esté en GCS

### Error en Backend API

1. Verificar token de autenticación
2. Revisar URL del backend
3. Verificar que el backend esté accesible desde Composer

## 📚 Recursos

- [Cloud Composer Documentation](https://cloud.google.com/composer/docs)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Dataproc Documentation](https://cloud.google.com/dataproc/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

## 🤝 Contribuir

Para agregar nuevos DAGs:

1. Crear archivo en `dags/`
2. Seguir convenciones de naming
3. Agregar documentación
4. Probar localmente
5. Subir a Composer
6. Actualizar este README
