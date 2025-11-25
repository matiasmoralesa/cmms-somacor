# Cloud Composer Automation - Implementación Completa

## 📋 Resumen

Se ha implementado un sistema completo de automatización usando Cloud Composer (Apache Airflow) con 3 DAGs principales para ETL/ML, mantenimiento preventivo y generación de reportes.

## 🎯 DAGs Implementados

### 1. ETL and ML Training DAG (`etl_ml_training`)

**Propósito:** Extrae datos de Cloud SQL, procesa características con PySpark en Dataproc, y entrena el modelo ML.

**Schedule:** Semanal (Domingos a las 2 AM)

**Tareas:**
1. **extract_assets_data** - Extrae datos de activos de Cloud SQL a GCS
2. **extract_work_orders_data** - Extrae datos de órdenes de trabajo a GCS
3. **create_dataproc_cluster** - Crea cluster de Dataproc
4. **feature_engineering** - Ejecuta PySpark job para ingeniería de características
5. **train_model** - Entrena modelo ML vía Backend API
6. **deploy_model** - Despliega modelo a Vertex AI
7. **delete_dataproc_cluster** - Elimina cluster (siempre se ejecuta)
8. **notify_success** - Envía email de éxito

**Características:**
- ✅ Extracción paralela de datos
- ✅ Procesamiento distribuido con PySpark
- ✅ Integración con Backend API
- ✅ Despliegue automático a Vertex AI
- ✅ Limpieza automática de recursos
- ✅ Notificaciones por email

**Configuración:**
```python
PROJECT_ID = Variable.get("gcp_project_id")
REGION = Variable.get("gcp_region")
BUCKET_NAME = Variable.get("gcs_bucket_name")
```

### 2. Preventive Maintenance DAG (`preventive_maintenance_generator`)

**Propósito:** Genera órdenes de trabajo para planes de mantenimiento vencidos.

**Schedule:** Diario (6 AM)

**Tareas:**
1. **query_due_maintenance_plans** - Consulta planes vencidos en la BD
2. **create_work_orders** - Crea órdenes de trabajo vía Backend API
3. **publish_notifications** - Publica notificaciones para técnicos
4. **send_summary_email** - Envía resumen por email

**Características:**
- ✅ Consulta directa a Cloud SQL
- ✅ Creación automática de órdenes de trabajo
- ✅ Notificaciones a técnicos
- ✅ Resumen diario por email
- ✅ Manejo de errores robusto

**Lógica de Negocio:**
```sql
SELECT * FROM maintenance_maintenanceplan
WHERE is_active = true
AND next_due_date <= CURRENT_DATE
AND asset.status = 'ACTIVE'
```

### 3. Report Generation DAG (`weekly_kpi_report`)

**Propósito:** Genera y envía reportes semanales de KPIs.

**Schedule:** Semanal (Lunes a las 8 AM)

**Tareas:**
1. **extract_kpi_data** - Extrae datos de KPIs de la BD
2. **generate_charts** - Genera gráficos con matplotlib
3. **generate_pdf_report** - Genera reporte HTML/PDF
4. **upload_report_to_gcs** - Sube reporte a Cloud Storage
5. **send_report_email** - Envía reporte por email con SendGrid

**KPIs Incluidos:**
- 📊 Órdenes de trabajo (total, completadas, en progreso, pendientes)
- ⏱️ MTTR (Mean Time To Repair)
- 🔧 MTBF (Mean Time Between Failures) por tipo de vehículo
- 📦 Inventario (total, stock bajo, valor)
- 🔮 Predicciones ML (alto riesgo, crítico, probabilidad promedio)

**Gráficos:**
- Distribución de órdenes de trabajo por estado
- MTBF por tipo de vehículo

## 🔧 Scripts de Soporte

### Feature Engineering Script (`feature_engineering.py`)

**Propósito:** Procesa datos crudos y crea características para ML.

**Características Generadas:**
- `asset_age_days` - Edad del activo en días
- `days_since_last_maintenance` - Días desde último mantenimiento
- `total_work_orders` - Total de órdenes de trabajo
- `completed_work_orders` - Órdenes completadas
- `high_priority_work_orders` - Órdenes de alta prioridad
- `critical_work_orders` - Órdenes críticas
- `avg_repair_hours` - Horas promedio de reparación
- `work_order_completion_rate` - Tasa de completitud
- `high_priority_ratio` - Ratio de prioridad alta

**Tecnología:** PySpark en Dataproc

## 🔌 Backend Integration

### Composer Client (`composer_client.py`)

Cliente Python para interactuar con Airflow API:

```python
class ComposerClient:
    def trigger_dag(dag_id, conf)
    def get_dag_status(dag_id)
    def get_dag_runs(dag_id, limit)
    def list_dags()
```

**Configuración:**
```python
AIRFLOW_WEBSERVER_URL = os.getenv('AIRFLOW_WEBSERVER_URL')
AIRFLOW_USERNAME = os.getenv('AIRFLOW_USERNAME')
AIRFLOW_PASSWORD = os.getenv('AIRFLOW_PASSWORD')
```

### API Endpoints

**Base URL:** `/api/v1/core/composer/`

**Endpoints:**
```
GET  /list_dags/                      - Lista todos los DAGs
POST /trigger_etl_ml_training/        - Inicia ETL y ML training
POST /trigger_preventive_maintenance/ - Inicia generación de mantenimiento
POST /trigger_report_generation/      - Inicia generación de reportes
GET  /dag_status/?dag_id=<id>         - Estado de un DAG
GET  /dag_runs/?dag_id=<id>&limit=10  - Ejecuciones recientes
```

**Autenticación:** Bearer Token (Admin only)

**Ejemplo de Uso:**
```bash
curl -X POST \
  http://localhost:8000/api/v1/core/composer/trigger_etl_ml_training/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"conf": {}}'
```

## 🎨 Frontend - Admin UI

### Admin Page (`Admin.tsx`)

**Ruta:** `/admin`

**Características:**
- 🎛️ Botones para iniciar cada DAG manualmente
- 📋 Lista de DAGs disponibles con estado
- ✅ Feedback visual de éxito/error
- 🔄 Estados de carga

**Componentes:**
- Tarjetas para cada DAG con descripción
- Botones de trigger con estados de carga
- Mensajes de éxito/error
- Tabla de DAGs disponibles

## 📁 Estructura de Archivos

```
proyecto/
├── airflow/
│   ├── dags/
│   │   ├── etl_ml_training_dag.py
│   │   ├── preventive_maintenance_dag.py
│   │   └── report_generation_dag.py
│   └── scripts/
│       └── feature_engineering.py
├── backend/
│   └── apps/
│       └── core/
│           ├── composer_client.py
│           ├── views.py
│           └── urls.py
└── frontend/
    └── src/
        └── pages/
            └── Admin.tsx
```

## ⚙️ Configuración

### Variables de Airflow

```python
# GCP Configuration
gcp_project_id = "your-project-id"
gcp_region = "us-central1"
gcs_bucket_name = "cmms-ml-data"

# Backend API
backend_api_url = "http://backend-service-url"
backend_api_token = "your-api-token"

# Email Configuration
alert_email = "admin@cmms.com,team@cmms.com"
report_email = "reports@cmms.com"
sendgrid_api_key = "your-sendgrid-key"
```

### Conexiones de Airflow

```python
# Cloud SQL PostgreSQL
cloudsql_postgres:
  conn_type: postgres
  host: /cloudsql/project:region:instance
  schema: cmms_db
  login: postgres
  password: <password>
```

### Variables de Entorno (Backend)

```bash
# Airflow Configuration
AIRFLOW_WEBSERVER_URL=https://your-composer-url
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=<password>
```

## 🚀 Despliegue

### 1. Crear Composer Environment

```bash
gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-4
```

### 2. Subir DAGs

```bash
gcloud composer environments storage dags import \
  --environment cmms-composer \
  --location us-central1 \
  --source airflow/dags/
```

### 3. Subir Scripts

```bash
gsutil cp airflow/scripts/feature_engineering.py \
  gs://cmms-ml-data/scripts/
```

### 4. Configurar Variables

```bash
gcloud composer environments run cmms-composer \
  --location us-central1 \
  variables set -- \
  gcp_project_id your-project-id
```

### 5. Configurar Conexiones

```bash
gcloud composer environments run cmms-composer \
  --location us-central1 \
  connections add cloudsql_postgres \
  --conn-type postgres \
  --conn-host /cloudsql/project:region:instance \
  --conn-schema cmms_db \
  --conn-login postgres \
  --conn-password <password>
```

## 📊 Monitoreo

### Airflow UI

Acceder a: `https://your-composer-url/home`

**Vistas Disponibles:**
- DAGs - Lista de todos los DAGs
- Graph View - Visualización de tareas
- Tree View - Historial de ejecuciones
- Logs - Logs detallados de cada tarea

### Cloud Logging

```bash
# Ver logs de DAG runs
gcloud logging read "resource.type=cloud_composer_environment" \
  --limit 50 \
  --format json
```

### Métricas

- Duración de ejecución de DAGs
- Tasa de éxito/fallo
- Uso de recursos de Dataproc
- Costos de ejecución

## 🔍 Troubleshooting

### DAG no se ejecuta

1. Verificar que el DAG no esté pausado
2. Revisar schedule_interval
3. Verificar start_date y catchup

### Error en extracción de datos

1. Verificar conexión a Cloud SQL
2. Revisar permisos de la cuenta de servicio
3. Verificar queries SQL

### Error en Dataproc

1. Verificar quotas de GCP
2. Revisar configuración del cluster
3. Verificar script de PySpark en GCS

### Error en Backend API

1. Verificar token de autenticación
2. Revisar URL del backend
3. Verificar logs del backend

## ✅ Testing

### Test Manual de DAGs

```python
# En Airflow UI
1. Ir a DAGs
2. Click en el DAG
3. Click en "Trigger DAG"
4. Monitorear ejecución en Graph View
```

### Test de Endpoints

```bash
# Listar DAGs
curl -X GET \
  http://localhost:8000/api/v1/core/composer/list_dags/ \
  -H "Authorization: Bearer <token>"

# Trigger DAG
curl -X POST \
  http://localhost:8000/api/v1/core/composer/trigger_etl_ml_training/ \
  -H "Authorization: Bearer <token>"
```

## 📈 Mejoras Futuras

1. **Alertas Avanzadas:**
   - Integración con PagerDuty
   - Alertas a Slack/Teams
   - Umbrales personalizables

2. **Optimizaciones:**
   - Cache de datos intermedios
   - Paralelización de tareas
   - Uso de Dataflow en lugar de Dataproc

3. **Reportes:**
   - Dashboards interactivos
   - Reportes personalizables
   - Exportación a múltiples formatos

4. **ML Pipeline:**
   - A/B testing de modelos
   - Monitoreo de drift
   - Reentrenamiento automático

## 🎉 Conclusión

La implementación de Cloud Composer está completa con:
- ✅ 3 DAGs principales funcionando
- ✅ Script de PySpark para feature engineering
- ✅ Cliente de Composer en Backend
- ✅ API endpoints para triggers manuales
- ✅ UI de administración en Frontend
- ✅ Notificaciones por email
- ✅ Integración completa con Backend
- ✅ Documentación completa

El sistema de automatización está listo para producción y puede ser desplegado en GCP Cloud Composer.
