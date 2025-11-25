# Design Document - Sistema CMMS Avanzado

## Overview

El Sistema CMMS es una aplicación distribuida de nivel empresarial que combina gestión de mantenimiento tradicional con capacidades avanzadas de inteligencia artificial y automatización. La arquitectura está diseñada para aprovechar servicios gestionados de Google Cloud Platform, maximizando escalabilidad, confiabilidad y reduciendo la carga operativa.

### Principios de Diseño

- **Cloud-Native First**: Uso de servicios gestionados de GCP para reducir complejidad operativa
- **Microservicios Ligeros**: Separación de responsabilidades entre backend API, ML service, y bot
- **Event-Driven Architecture**: Comunicación asíncrona mediante Cloud Pub/Sub para desacoplamiento
- **API-First**: Backend expone API REST completa documentada con OpenAPI
- **Stateless Services**: Servicios sin estado para facilitar escalado horizontal
- **Infrastructure as Code**: Configuración reproducible mediante scripts y contenedores

### Stack Tecnológico

**Backend:**
- Django 4.x con Django REST Framework
- Python 3.11+
- PostgreSQL (Cloud SQL)
- Redis (Memorystore) para caché y sesiones
- Gunicorn como WSGI server

**Frontend:**
- React 18+ con TypeScript
- Vite como build tool
- Tailwind CSS para estilos
- Recharts para visualizaciones
- Axios para HTTP client
- React Query para state management

**Infrastructure:**
- Cloud Run para backend y bot
- Firebase Hosting para frontend
- Cloud SQL (PostgreSQL) para base de datos
- Cloud Storage para archivos
- Cloud Pub/Sub para mensajería
- Cloud Composer (Airflow) para orquestación
- Dataproc para procesamiento ML
- Vertex AI para deployment de modelos

**ML Stack:**
- Scikit-learn para modelos predictivos
- Pandas/NumPy para procesamiento de datos
- Joblib para serialización de modelos

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users & Clients                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web App    │  │  Mobile Web  │  │   Telegram   │          │
│  │  (Browser)   │  │  (Browser)   │  │     Bot      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                    Firebase Hosting (CDN)                        │
│                      Static React App                            │
└─────────┬────────────────────────────────────────────────────────┘
          │
          │ HTTPS/REST
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                         Cloud Run                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Django Backend API                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │   Auth   │  │  Assets  │  │   Work   │  │  Reports │  │  │
│  │  │ Service  │  │ Service  │  │  Orders  │  │ Service  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └────────┬───────────────────────────────────────────────────┘  │
└───────────┼──────────────────────────────────────────────────────┘
            │
            │
    ┌───────┼───────────────────────────────────────┐
    │       │                                       │
    │       │                                       │
┌───▼───────▼──┐  ┌──────────────┐  ┌──────────────▼──────┐
│  Cloud SQL   │  │Cloud Storage │  │   Cloud Pub/Sub     │
│ (PostgreSQL) │  │   Buckets    │  │  ┌──────────────┐   │
│              │  │              │  │  │ notifications│   │
└──────┬───────┘  └──────────────┘  │  │   events     │   │
       │                             │  │   alerts     │   │
       │                             │  └──────┬───────┘   │
       │                             └─────────┼───────────┘
       │                                       │
       │                                       │
┌──────▼───────────────────────────────────────▼─────────────┐
│                   Cloud Composer (Airflow)                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ ETL/ML   │  │  Preventive  │  │  Reports Generation  │ │
│  │   DAG    │  │  Maint. DAG  │  │        DAG           │ │
│  └────┬─────┘  └──────────────┘  └──────────────────────┘ │
└───────┼────────────────────────────────────────────────────┘
        │
        │
┌───────▼──────────────────────────────────────────────────────┐
│                        Dataproc                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  ML Training Pipeline (Spark/Dask)                     │  │
│  │  - Feature Engineering                                 │  │
│  │  - Model Training                                      │  │
│  │  - Model Evaluation                                    │  │
│  └────────────────────────┬───────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ Deploy Model
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                      Vertex AI                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Failure Prediction Model Endpoint                     │  │
│  │  - Input: Asset telemetry & historical data           │  │
│  │  - Output: Failure probability & recommendations      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    Cloud Run (Bot Service)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Telegram Bot Handler                      │  │
│  │  - Webhook receiver                                    │  │
│  │  - Command processor                                   │  │
│  │  - Role-based access control                          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**1. User Creates Work Order:**
```
User (Web) → Frontend → Backend API → Cloud SQL (save)
                                   → Cloud Pub/Sub (publish event)
                                   → Telegram Bot (notify assigned user)
```

**2. ML Prediction Flow:**
```
Cloud Composer (scheduled) → Dataproc (train model)
                          → Vertex AI (deploy model)
Backend API → Vertex AI (predict) → Cloud SQL (save prediction)
                                  → Cloud Pub/Sub (alert if high risk)
```

**3. Automated Maintenance:**
```
Cloud Composer (daily 6 AM) → Backend API (create work orders)
                            → Cloud Pub/Sub (notify supervisors)
```


## Components and Interfaces

### Backend API (Django)

**Structure:**
```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   │   ├── models.py (User, Role, Permission)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── assets/
│   │   ├── models.py (Asset, AssetCategory, Location)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── work_orders/
│   │   ├── models.py (WorkOrder, WorkOrderStatus)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── maintenance/
│   │   ├── models.py (MaintenancePlan, Schedule)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── inventory/
│   │   ├── models.py (SparePart, StockMovement)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── checklists/
│   │   ├── models.py (ChecklistTemplate, ChecklistResponse)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py
│   │   └── pdf_generator.py
│   ├── predictions/
│   │   ├── models.py (FailurePrediction, Alert)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── ml_client.py (Vertex AI integration)
│   ├── notifications/
│   │   ├── models.py (Notification, NotificationPreference)
│   │   ├── services.py
│   │   └── pubsub_publisher.py
│   ├── reports/
│   │   ├── models.py (Report, ReportSchedule)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── generators.py
│   ├── locations/
│   │   ├── models.py (Location)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   ├── users/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py (user management, email notifications)
│   └── machine_status/
│       ├── models.py (AssetStatus, AssetStatusHistory)
│       ├── serializers.py
│       ├── views.py
│       └── services.py (status updates, alert generation)
├── core/
│   ├── middleware.py
│   ├── permissions.py
│   ├── pagination.py
│   └── exceptions.py
├── utils/
│   ├── gcp_storage.py
│   ├── gcp_pubsub.py
│   └── validators.py
├── requirements.txt
├── Dockerfile
└── manage.py
```

**Key API Endpoints:**

```
Authentication:
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
POST   /api/v1/auth/password-reset

Assets:
GET    /api/v1/assets/
POST   /api/v1/assets/
GET    /api/v1/assets/{id}/
PUT    /api/v1/assets/{id}/
DELETE /api/v1/assets/{id}/
POST   /api/v1/assets/{id}/upload-document/
GET    /api/v1/assets/{id}/documents/

Work Orders:
GET    /api/v1/work-orders/
POST   /api/v1/work-orders/
GET    /api/v1/work-orders/{id}/
PUT    /api/v1/work-orders/{id}/
PATCH  /api/v1/work-orders/{id}/status/
POST   /api/v1/work-orders/{id}/complete/
GET    /api/v1/work-orders/my-assignments/

Maintenance Plans:
GET    /api/v1/maintenance-plans/
POST   /api/v1/maintenance-plans/
GET    /api/v1/maintenance-plans/{id}/
PUT    /api/v1/maintenance-plans/{id}/
PATCH  /api/v1/maintenance-plans/{id}/pause/
PATCH  /api/v1/maintenance-plans/{id}/resume/

Inventory:
GET    /api/v1/spare-parts/
POST   /api/v1/spare-parts/
GET    /api/v1/spare-parts/{id}/
PUT    /api/v1/spare-parts/{id}/
POST   /api/v1/spare-parts/{id}/adjust-stock/
GET    /api/v1/spare-parts/low-stock/

Checklists:
GET    /api/v1/checklist-templates/
POST   /api/v1/checklist-templates/
GET    /api/v1/checklist-responses/
POST   /api/v1/checklist-responses/
GET    /api/v1/checklist-responses/{id}/pdf/

Predictions:
GET    /api/v1/predictions/
POST   /api/v1/predictions/predict/
GET    /api/v1/predictions/alerts/
GET    /api/v1/predictions/asset/{id}/health-score/

Reports:
GET    /api/v1/reports/kpis/
GET    /api/v1/reports/work-orders-summary/
GET    /api/v1/reports/asset-downtime/
POST   /api/v1/reports/generate/
GET    /api/v1/reports/{id}/download/

Locations (Admin Only):
GET    /api/v1/locations/
POST   /api/v1/locations/
GET    /api/v1/locations/{id}/
PUT    /api/v1/locations/{id}/
DELETE /api/v1/locations/{id}/
GET    /api/v1/locations/{id}/assets/

Users (Admin Only):
GET    /api/v1/users/
POST   /api/v1/users/
GET    /api/v1/users/{id}/
PUT    /api/v1/users/{id}/
PATCH  /api/v1/users/{id}/activate/
PATCH  /api/v1/users/{id}/deactivate/
POST   /api/v1/users/{id}/reset-password/

Machine Status (Operator Feature):
GET    /api/v1/asset-status/
POST   /api/v1/asset-status/
GET    /api/v1/asset-status/{id}/
GET    /api/v1/asset-status/my-assets/
GET    /api/v1/asset-status/asset/{asset_id}/history/
GET    /api/v1/asset-status/asset/{asset_id}/current/
```

### Frontend Application (React + TypeScript)

**Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   └── Loader.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── assets/
│   │   │   ├── AssetList.tsx
│   │   │   ├── AssetForm.tsx
│   │   │   └── AssetDetail.tsx
│   │   ├── work-orders/
│   │   │   ├── WorkOrderList.tsx
│   │   │   ├── WorkOrderForm.tsx
│   │   │   ├── WorkOrderDetail.tsx
│   │   │   └── WorkOrderKanban.tsx
│   │   ├── maintenance/
│   │   │   ├── MaintenancePlanList.tsx
│   │   │   ├── MaintenancePlanForm.tsx
│   │   │   └── MaintenanceCalendar.tsx
│   │   ├── inventory/
│   │   │   ├── SparePartList.tsx
│   │   │   ├── SparePartForm.tsx
│   │   │   └── StockAlerts.tsx
│   │   ├── checklists/
│   │   │   ├── ChecklistTemplateBuilder.tsx
│   │   │   ├── ChecklistExecutor.tsx
│   │   │   └── ChecklistViewer.tsx
│   │   ├── predictions/
│   │   │   ├── PredictionDashboard.tsx
│   │   │   ├── AlertList.tsx
│   │   │   └── HealthScoreCard.tsx
│   │   ├── reports/
│   │   │   ├── ReportDashboard.tsx
│   │   │   ├── KPICards.tsx
│   │   │   └── ChartComponents.tsx
│   │   ├── locations/
│   │   │   ├── LocationList.tsx
│   │   │   ├── LocationForm.tsx
│   │   │   └── LocationMap.tsx
│   │   ├── users/
│   │   │   ├── UserList.tsx
│   │   │   ├── UserForm.tsx
│   │   │   └── UserRoleSelector.tsx
│   │   └── machine-status/
│   │       ├── StatusUpdateForm.tsx
│   │       ├── StatusHistory.tsx
│   │       ├── MyAssignedAssets.tsx
│   │       └── StatusDashboard.tsx
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── AssetsPage.tsx
│   │   ├── WorkOrdersPage.tsx
│   │   ├── MaintenancePage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── ChecklistsPage.tsx
│   │   ├── PredictionsPage.tsx
│   │   ├── ReportsPage.tsx
│   │   ├── LocationsPage.tsx
│   │   ├── UsersPage.tsx
│   │   └── MachineStatusPage.tsx
│   ├── services/
│   │   ├── api.ts (Axios instance)
│   │   ├── authService.ts
│   │   ├── assetService.ts
│   │   ├── workOrderService.ts
│   │   ├── maintenanceService.ts
│   │   ├── inventoryService.ts
│   │   ├── checklistService.ts
│   │   ├── predictionService.ts
│   │   ├── reportService.ts
│   │   ├── locationService.ts
│   │   ├── userService.ts
│   │   └── machineStatusService.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useNotifications.ts
│   │   ├── useWebSocket.ts
│   │   └── usePermissions.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── notificationStore.ts
│   │   └── uiStore.ts
│   ├── types/
│   │   ├── asset.types.ts
│   │   ├── workOrder.types.ts
│   │   ├── maintenance.types.ts
│   │   ├── inventory.types.ts
│   │   ├── checklist.types.ts
│   │   ├── prediction.types.ts
│   │   ├── user.types.ts
│   │   ├── location.types.ts
│   │   └── machineStatus.types.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── firebase.json
└── .firebaserc
```


### Telegram Bot Service

**Structure:**
```
telegram-bot/
├── src/
│   ├── handlers/
│   │   ├── commands.py
│   │   ├── status.py
│   │   ├── equipos.py
│   │   ├── ordenes.py
│   │   ├── pendientes.py
│   │   ├── alertas.py
│   │   └── kpis.py
│   ├── middleware/
│   │   ├── auth.py
│   │   └── role_check.py
│   ├── services/
│   │   ├── api_client.py (calls Backend API)
│   │   └── pubsub_subscriber.py
│   ├── utils/
│   │   ├── formatters.py
│   │   └── keyboards.py
│   ├── config.py
│   ├── main.py
│   └── webhook_handler.py
├── requirements.txt
└── Dockerfile
```

**Bot Commands by Role:**

| Command | Admin | Supervisor | Técnico | Operador | Invitado |
|---------|-------|------------|---------|----------|----------|
| /status | ✓ | ✓ | ✓ | ✓ | ✓ |
| /equipos | ✓ | ✓ | ✓ | ✓ | ✓ (limited) |
| /ordenes | ✓ | ✓ | ✓ (own) | ✗ | ✗ |
| /pendientes | ✓ | ✓ | ✓ (own) | ✗ | ✗ |
| /alertas | ✓ | ✓ | ✓ | ✗ | ✗ |
| /kpis | ✓ | ✓ | ✗ | ✗ | ✗ |

### Cloud Composer DAGs

**DAG 1: ETL and ML Training**
```python
# dags/ml_training_pipeline.py
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator
)
from airflow.providers.google.cloud.operators.vertex_ai import (
    CreateCustomTrainingJobOperator,
    DeployModelOperator
)

# Schedule: Weekly on Sundays at 2 AM
# Tasks:
# 1. Extract data from Cloud SQL
# 2. Create Dataproc cluster
# 3. Run feature engineering (PySpark)
# 4. Train ML model (Scikit-learn)
# 5. Evaluate model performance
# 6. Deploy to Vertex AI if metrics improve
# 7. Delete Dataproc cluster
# 8. Send notification email
```

**DAG 2: Preventive Maintenance Generation**
```python
# dags/preventive_maintenance.py
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator

# Schedule: Daily at 6 AM
# Tasks:
# 1. Call Backend API to get active maintenance plans
# 2. Generate work orders for due maintenance
# 3. Assign to default supervisors
# 4. Send notifications via Pub/Sub
```

**DAG 3: Report Generation**
```python
# dags/report_generation.py
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.providers.sendgrid.operators.sendgrid import SendGridOperator

# Schedule: Weekly on Mondays at 8 AM
# Tasks:
# 1. Call Backend API to generate KPI report
# 2. Generate PDF report
# 3. Upload to Cloud Storage
# 4. Send email with report link via SendGrid
```

## Data Models

### Core Entities

**User Model:**
```python
class User(AbstractUser):
    id = UUIDField(primary_key=True)
    email = EmailField(unique=True)
    role = ForeignKey('Role')
    telegram_id = CharField(max_length=50, null=True, unique=True)
    phone = CharField(max_length=20, null=True)
    rut = CharField(max_length=12, unique=True)  # Chilean RUT
    employee_status = CharField(max_length=20)  # ACTIVE, INACTIVE, ON_LEAVE
    
    # License information (required for OPERADOR role)
    license_type = CharField(max_length=50, null=True)
    # Choices: MUNICIPAL, INTERNAL, OTHER
    license_expiration_date = DateField(null=True)
    license_photo_url = URLField(null=True)  # Cloud Storage URL
    
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    def has_valid_license(self):
        """Check if user has a valid, non-expired license"""
        if not self.license_type or not self.license_expiration_date:
            return False
        return self.license_expiration_date >= date.today()
    
    def license_expires_soon(self, days=30):
        """Check if license expires within specified days"""
        if not self.license_expiration_date:
            return False
        return 0 <= (self.license_expiration_date - date.today()).days <= days
```

**Role Model:**
```python
class Role(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    # Choices: ADMIN, SUPERVISOR, OPERADOR (exactly 3 roles)
    permissions = ManyToManyField('Permission')
    created_at = DateTimeField(auto_now_add=True)
```

**Asset Model:**
```python
class Asset(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=200)
    asset_code = CharField(max_length=50, unique=True)
    vehicle_type = CharField(max_length=50)
    # Choices: CAMION_SUPERSUCKER, CAMIONETA_MDO, RETROEXCAVADORA_MDO, 
    #          CARGADOR_FRONTAL_MDO, MINICARGADOR_MDO
    location = ForeignKey('Location')
    manufacturer = CharField(max_length=100, null=True)
    model = CharField(max_length=100, null=True)
    serial_number = CharField(max_length=100, unique=True)
    license_plate = CharField(max_length=20, unique=True, null=True)
    installation_date = DateField(null=True)
    status = CharField(max_length=20)
    # Choices: OPERATIONAL, DOWN, MAINTENANCE, RETIRED
    criticality = CharField(max_length=20)
    # Choices: LOW, MEDIUM, HIGH, CRITICAL
    specifications = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**AssetDocument Model:**
```python
class AssetDocument(Model):
    id = UUIDField(primary_key=True)
    asset = ForeignKey('Asset', related_name='documents')
    document_type = CharField(max_length=50)
    # Choices: MANUAL, PHOTO, CERTIFICATE, DRAWING
    file_url = URLField()  # Cloud Storage URL
    file_name = CharField(max_length=255)
    file_size = IntegerField()  # bytes
    uploaded_by = ForeignKey('User')
    uploaded_at = DateTimeField(auto_now_add=True)
```

**WorkOrder Model:**
```python
class WorkOrder(Model):
    id = UUIDField(primary_key=True)
    work_order_number = CharField(max_length=50, unique=True)
    title = CharField(max_length=200)
    description = TextField()
    asset = ForeignKey('Asset', related_name='work_orders')
    work_order_type = CharField(max_length=20)
    # Choices: CORRECTIVE, PREVENTIVE, PREDICTIVE, INSPECTION
    priority = CharField(max_length=20)
    # Choices: LOW, MEDIUM, HIGH, URGENT
    status = CharField(max_length=20)
    # Choices: PENDING, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED
    assigned_to = ForeignKey('User', null=True, related_name='assigned_work_orders')
    created_by = ForeignKey('User', related_name='created_work_orders')
    scheduled_date = DateTimeField(null=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    estimated_hours = DecimalField(max_digits=5, decimal_places=2, null=True)
    actual_hours = DecimalField(max_digits=5, decimal_places=2, null=True)
    completion_notes = TextField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**MaintenancePlan Model:**
```python
class MaintenancePlan(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=200)
    asset = ForeignKey('Asset', related_name='maintenance_plans')
    plan_type = CharField(max_length=20)
    # Choices: PREVENTIVE, PREDICTIVE
    recurrence_type = CharField(max_length=20)
    # Choices: DAILY, WEEKLY, MONTHLY, CUSTOM
    recurrence_interval = IntegerField(default=1)
    next_due_date = DateField()
    is_active = BooleanField(default=True)
    checklist_template = ForeignKey('ChecklistTemplate', null=True)
    estimated_duration = IntegerField()  # minutes
    created_by = ForeignKey('User')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**SparePart Model:**
```python
class SparePart(Model):
    id = UUIDField(primary_key=True)
    part_number = CharField(max_length=100, unique=True)
    name = CharField(max_length=200)
    description = TextField(null=True)
    category = CharField(max_length=100)
    quantity = IntegerField(default=0)
    minimum_stock = IntegerField(default=0)
    unit_cost = DecimalField(max_digits=10, decimal_places=2)
    location = CharField(max_length=100)
    supplier = CharField(max_length=200, null=True)
    compatible_assets = ManyToManyField('Asset')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**StockMovement Model:**
```python
class StockMovement(Model):
    id = UUIDField(primary_key=True)
    spare_part = ForeignKey('SparePart', related_name='movements')
    movement_type = CharField(max_length=20)
    # Choices: IN, OUT, ADJUSTMENT
    quantity = IntegerField()
    work_order = ForeignKey('WorkOrder', null=True)
    performed_by = ForeignKey('User')
    notes = TextField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```


**ChecklistTemplate Model:**
```python
class ChecklistTemplate(Model):
    id = UUIDField(primary_key=True)
    code = CharField(max_length=50, unique=True)
    # Codes: F-PR-020-CH01, F-PR-034-CH01, F-PR-037-CH01, F-PR-040-CH01, SUPERSUCKER-CH01
    name = CharField(max_length=200)
    vehicle_type = CharField(max_length=50)
    # Matches Asset vehicle_type choices
    description = TextField(null=True)
    items = JSONField()  # Array of checklist items from PDF templates
    # Example: [
    #   {
    #     "section": "Motor",
    #     "order": 1,
    #     "question": "Nivel de aceite motor",
    #     "response_type": "yes_no_na",
    #     "required": true,
    #     "observations_allowed": true
    #   }
    # ]
    is_system_template = BooleanField(default=False)  # Prevents deletion/modification
    passing_score = IntegerField(default=80)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**ChecklistResponse Model:**
```python
class ChecklistResponse(Model):
    id = UUIDField(primary_key=True)
    template = ForeignKey('ChecklistTemplate')
    work_order = ForeignKey('WorkOrder', null=True)
    asset = ForeignKey('Asset')
    responses = JSONField()  # Array of responses matching template items
    # Example: [
    #   {
    #     "item_order": 1,
    #     "response": "yes",
    #     "notes": "Oil level normal",
    #     "photo_url": "gs://bucket/photo.jpg"
    #   }
    # ]
    score = IntegerField()
    passed = BooleanField()
    pdf_url = URLField(null=True)  # Generated PDF in Cloud Storage
    completed_by = ForeignKey('User')
    completed_at = DateTimeField(auto_now_add=True)
```

**FailurePrediction Model:**
```python
class FailurePrediction(Model):
    id = UUIDField(primary_key=True)
    asset = ForeignKey('Asset', related_name='predictions')
    prediction_date = DateTimeField(auto_now_add=True)
    failure_probability = DecimalField(max_digits=5, decimal_places=2)
    # 0.00 to 100.00
    predicted_failure_date = DateField(null=True)
    confidence_score = DecimalField(max_digits=5, decimal_places=2)
    model_version = CharField(max_length=50)
    input_features = JSONField()  # Features used for prediction
    recommendations = TextField()
    risk_level = CharField(max_length=20)
    # Choices: LOW, MEDIUM, HIGH, CRITICAL
    created_at = DateTimeField(auto_now_add=True)
```

**Alert Model:**
```python
class Alert(Model):
    id = UUIDField(primary_key=True)
    alert_type = CharField(max_length=50)
    # Choices: PREDICTION, LOW_STOCK, OVERDUE_MAINTENANCE, SYSTEM
    severity = CharField(max_length=20)
    # Choices: INFO, WARNING, ERROR, CRITICAL
    title = CharField(max_length=200)
    message = TextField()
    asset = ForeignKey('Asset', null=True)
    work_order = ForeignKey('WorkOrder', null=True)
    prediction = ForeignKey('FailurePrediction', null=True)
    is_read = BooleanField(default=False)
    is_resolved = BooleanField(default=False)
    resolved_by = ForeignKey('User', null=True)
    resolved_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**Notification Model:**
```python
class Notification(Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey('User', related_name='notifications')
    notification_type = CharField(max_length=50)
    title = CharField(max_length=200)
    message = TextField()
    data = JSONField(default=dict)  # Additional context data
    is_read = BooleanField(default=False)
    sent_via_telegram = BooleanField(default=False)
    sent_via_email = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

### Database Relationships

```
User ──┬─── created WorkOrders (1:N)
       ├─── assigned WorkOrders (1:N)
       ├─── Role (N:1)
       ├─── Notifications (1:N)
       └─── ChecklistResponses (1:N)

Asset ──┬─── AssetCategory (N:1)
        ├─── Location (N:1)
        ├─── WorkOrders (1:N)
        ├─── MaintenancePlans (1:N)
        ├─── AssetDocuments (1:N)
        ├─── FailurePredictions (1:N)
        └─── SpareParts (N:M)

WorkOrder ──┬─── Asset (N:1)
            ├─── assigned User (N:1)
            ├─── created User (N:1)
            ├─── ChecklistResponse (1:1)
            └─── StockMovements (1:N)

MaintenancePlan ──┬─── Asset (N:1)
                  ├─── ChecklistTemplate (N:1)
                  └─── created User (N:1)

SparePart ──┬─── StockMovements (1:N)
            └─── compatible Assets (N:M)

ChecklistTemplate ──┬─── AssetCategory (N:1)
                    ├─── MaintenancePlans (1:N)
                    └─── ChecklistResponses (1:N)

FailurePrediction ──┬─── Asset (N:1)
                    └─── Alerts (1:N)
```

### New Models for Location, User Management, and Machine Status

**Location Model:**
```python
class Location(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=200, unique=True)
    address = TextField(null=True)
    city = CharField(max_length=100, null=True)
    region = CharField(max_length=100, null=True)
    coordinates = JSONField(null=True)  # {"lat": -33.4489, "lng": -70.6693}
    description = TextField(null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**AssetStatus Model (for Operator Updates):**
```python
class AssetStatus(Model):
    id = UUIDField(primary_key=True)
    asset = ForeignKey('Asset', related_name='status_updates')
    status_type = CharField(max_length=50)
    # Choices: OPERANDO, DETENIDA, EN_MANTENIMIENTO, FUERA_DE_SERVICIO
    odometer_reading = DecimalField(max_digits=10, decimal_places=2, null=True)
    # For vehicles: kilometers or hours
    fuel_level = IntegerField(null=True)  # Percentage 0-100
    condition_notes = TextField(null=True)
    reported_by = ForeignKey('User', related_name='status_reports')
    reported_at = DateTimeField(auto_now_add=True)
    location = ForeignKey('Location', null=True)
    
    class Meta:
        ordering = ['-reported_at']
        indexes = [
            Index(fields=['asset', '-reported_at']),
            Index(fields=['status_type']),
        ]
```

**AssetStatusHistory Model:**
```python
class AssetStatusHistory(Model):
    """Audit trail for all status changes"""
    id = UUIDField(primary_key=True)
    asset = ForeignKey('Asset', related_name='status_history')
    previous_status = CharField(max_length=50, null=True)
    new_status = CharField(max_length=50)
    previous_odometer = DecimalField(max_digits=10, decimal_places=2, null=True)
    new_odometer = DecimalField(max_digits=10, decimal_places=2, null=True)
    changed_by = ForeignKey('User')
    changed_at = DateTimeField(auto_now_add=True)
    change_reason = TextField(null=True)
    
    class Meta:
        ordering = ['-changed_at']
```

### Updated Relationships

```
Location ──┬─── Assets (1:N)
           └─── AssetStatus (1:N)

User ──┬─── AssetStatus reports (1:N)
       └─── AssetStatusHistory changes (1:N)

Asset ──┬─── AssetStatus updates (1:N)
        └─── AssetStatusHistory (1:N)
```

## Error Handling

### Backend Error Handling Strategy

**1. API Error Responses:**
```python
# Standard error response format
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "serial_number",
            "issue": "Serial number already exists"
        },
        "timestamp": "2025-11-13T10:30:00Z",
        "request_id": "uuid"
    }
}
```

**2. Error Categories:**
- **Validation Errors (400)**: Invalid input data, missing required fields
- **Authentication Errors (401)**: Invalid credentials, expired tokens
- **Authorization Errors (403)**: Insufficient permissions
- **Not Found Errors (404)**: Resource doesn't exist
- **Conflict Errors (409)**: Duplicate resources, state conflicts
- **Server Errors (500)**: Unexpected server failures
- **Service Unavailable (503)**: External service failures (Cloud SQL, Vertex AI)

**3. External Service Error Handling:**

```python
# Cloud SQL connection errors
try:
    result = db.query(...)
except OperationalError as e:
    logger.error(f"Database connection failed: {e}")
    # Retry with exponential backoff (max 3 attempts)
    # If all retries fail, return 503 Service Unavailable

# Vertex AI prediction errors
try:
    prediction = vertex_ai_client.predict(...)
except Exception as e:
    logger.error(f"ML prediction failed: {e}")
    # Fall back to rule-based prediction or return cached result
    # Log incident for investigation

# Cloud Storage upload errors
try:
    blob.upload_from_file(file)
except Exception as e:
    logger.error(f"File upload failed: {e}")
    # Retry upload once
    # If fails, save file reference as pending and schedule background retry
```

**4. Transaction Management:**
```python
from django.db import transaction

@transaction.atomic
def create_work_order_with_notifications(data):
    # All operations succeed or all rollback
    work_order = WorkOrder.objects.create(**data)
    notification = Notification.objects.create(...)
    publish_to_pubsub(work_order)
    return work_order
```

**5. Logging Strategy:**
```python
import logging
import json

logger = logging.getLogger(__name__)

# Structured logging for Cloud Logging
logger.info(json.dumps({
    "severity": "INFO",
    "message": "Work order created",
    "work_order_id": str(work_order.id),
    "user_id": str(user.id),
    "timestamp": datetime.now().isoformat()
}))
```

### Frontend Error Handling

**1. API Error Interceptor:**
```typescript
// services/api.ts
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login
      authStore.logout();
      router.push('/login');
    } else if (error.response?.status === 403) {
      // Show permission denied message
      toast.error('No tienes permisos para esta acción');
    } else if (error.response?.status >= 500) {
      // Show generic server error
      toast.error('Error del servidor. Intenta nuevamente.');
    }
    return Promise.reject(error);
  }
);
```

**2. Error Boundaries:**
```typescript
// components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log to monitoring service
    console.error('React error:', error, errorInfo);
    // Show fallback UI
  }
}
```

**3. Network Error Handling:**
```typescript
// Handle offline scenarios
if (!navigator.onLine) {
  toast.warning('Sin conexión. Los cambios se sincronizarán cuando vuelvas a estar en línea.');
  // Queue operations for later sync
}
```

### Telegram Bot Error Handling

```python
# telegram-bot/src/handlers/commands.py
async def handle_command(update, context):
    try:
        # Process command
        result = await api_client.get_data()
        await update.message.reply_text(result)
    except APIConnectionError:
        await update.message.reply_text(
            "⚠️ No puedo conectarme al servidor. Intenta más tarde."
        )
    except PermissionError:
        await update.message.reply_text(
            "🚫 No tienes permisos para este comando."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. El equipo técnico ha sido notificado."
        )
```


## Testing Strategy

### Backend Testing

**1. Unit Tests:**
```python
# tests/unit/test_work_order_service.py
import pytest
from apps.work_orders.services import WorkOrderService

class TestWorkOrderService:
    def test_create_work_order_success(self):
        # Test successful work order creation
        data = {
            'title': 'Test WO',
            'asset_id': asset.id,
            'priority': 'HIGH'
        }
        wo = WorkOrderService.create(data, user)
        assert wo.work_order_number is not None
        assert wo.status == 'PENDING'
    
    def test_create_work_order_invalid_asset(self):
        # Test validation for non-existent asset
        with pytest.raises(ValidationError):
            WorkOrderService.create({'asset_id': 'invalid'}, user)
```

**2. Integration Tests:**
```python
# tests/integration/test_work_order_api.py
from rest_framework.test import APITestCase

class WorkOrderAPITest(APITestCase):
    def test_create_work_order_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/work-orders/', data)
        assert response.status_code == 201
        assert 'work_order_number' in response.data
```

**3. ML Model Tests:**
```python
# tests/ml/test_prediction_model.py
def test_model_prediction_accuracy():
    # Test model predictions on test dataset
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    assert accuracy > 0.75  # Minimum acceptable accuracy
```

**Testing Tools:**
- pytest for unit and integration tests
- pytest-django for Django-specific testing
- factory_boy for test data generation
- pytest-cov for coverage reporting
- Target: 80% code coverage minimum

### Frontend Testing

**1. Component Tests:**
```typescript
// components/__tests__/AssetList.test.tsx
import { render, screen } from '@testing-library/react';
import AssetList from '../AssetList';

describe('AssetList', () => {
  it('renders asset list correctly', () => {
    render(<AssetList assets={mockAssets} />);
    expect(screen.getByText('Asset 1')).toBeInTheDocument();
  });
  
  it('handles empty state', () => {
    render(<AssetList assets={[]} />);
    expect(screen.getByText('No hay activos')).toBeInTheDocument();
  });
});
```

**2. Integration Tests:**
```typescript
// pages/__tests__/WorkOrdersPage.test.tsx
import { render, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('WorkOrdersPage', () => {
  it('creates new work order', async () => {
    render(<WorkOrdersPage />);
    await userEvent.click(screen.getByText('Nueva Orden'));
    await userEvent.type(screen.getByLabelText('Título'), 'Test WO');
    await userEvent.click(screen.getByText('Guardar'));
    
    await waitFor(() => {
      expect(screen.getByText('Orden creada exitosamente')).toBeInTheDocument();
    });
  });
});
```

**Testing Tools:**
- Vitest as test runner
- React Testing Library for component testing
- MSW (Mock Service Worker) for API mocking
- Playwright for E2E tests (optional)
- Target: 70% coverage for critical paths

### Cloud Composer DAG Testing

```python
# tests/dags/test_ml_training_dag.py
from airflow.models import DagBag

def test_dag_loaded():
    dagbag = DagBag()
    assert 'ml_training_pipeline' in dagbag.dags
    assert len(dagbag.import_errors) == 0

def test_dag_structure():
    dag = dagbag.get_dag('ml_training_pipeline')
    assert len(dag.tasks) == 7
    assert 'extract_data' in dag.task_ids
```

### Performance Testing

**1. Load Testing:**
```python
# Use Locust for load testing
from locust import HttpUser, task, between

class CMSUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_assets(self):
        self.client.get("/api/v1/assets/")
    
    @task(1)
    def create_work_order(self):
        self.client.post("/api/v1/work-orders/", json=data)
```

**Performance Targets:**
- API response time: < 200ms (p95)
- Page load time: < 2s
- Time to interactive: < 3s
- Concurrent users: 100+ without degradation

## Security Considerations

### Authentication & Authorization

**1. JWT Token Strategy:**
```python
# Access token: 15 minutes expiry
# Refresh token: 7 days expiry
# Tokens stored in httpOnly cookies (frontend)
# Token rotation on refresh
```

**2. Role-Based Access Control (RBAC):**
```python
# permissions.py
class IsAdminOrSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name in ['ADMIN', 'SUPERVISOR']

class IsOwnerOrSupervisor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.assigned_to == request.user or
            request.user.role.name in ['ADMIN', 'SUPERVISOR']
        )
```

**3. API Rate Limiting:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/minute',
        'anon': '20/minute',
    }
}
```

### Data Security

**1. Encryption:**
- Data in transit: TLS 1.3 (enforced by Cloud Run/Firebase)
- Data at rest: Cloud SQL automatic encryption
- Sensitive fields: Django field-level encryption for passwords

**2. Input Validation:**
```python
# serializers.py
class AssetSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(
        max_length=100,
        validators=[validate_alphanumeric]
    )
    
    def validate_serial_number(self, value):
        # Additional custom validation
        if Asset.objects.filter(serial_number=value).exists():
            raise ValidationError("Serial number already exists")
        return value
```

**3. SQL Injection Prevention:**
- Django ORM parameterized queries (default protection)
- No raw SQL queries without parameterization

**4. XSS Prevention:**
- React automatic escaping
- Content Security Policy headers
- Sanitize user input on backend

**5. CSRF Protection:**
- Django CSRF tokens for state-changing operations
- SameSite cookie attribute

### GCP Security Best Practices

**1. IAM Permissions:**
```yaml
# Principle of least privilege
# Backend service account permissions:
- roles/cloudsql.client
- roles/storage.objectAdmin (specific bucket)
- roles/pubsub.publisher
- roles/aiplatform.user (Vertex AI)

# Cloud Composer service account:
- roles/dataproc.editor
- roles/cloudsql.client
- roles/aiplatform.admin
```

**2. Network Security:**
- Cloud Run: Ingress control (allow all, but with authentication)
- Cloud SQL: Private IP only, no public access
- VPC Service Controls for sensitive data

**3. Secrets Management:**
```python
# Use Secret Manager for sensitive config
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Store: DB passwords, API keys, JWT secrets
```

**4. Audit Logging:**
- Enable Cloud Audit Logs for all services
- Log all authentication attempts
- Log all data modifications with user context

## Deployment Architecture

### Local Development Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cmms_dev
      POSTGRES_USER: cmms_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cmms_user:dev_password@db:5432/cmms_dev
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=True
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1

volumes:
  postgres_data:
```

### GCP Production Deployment

**1. Cloud Run (Backend):**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations on startup (via Cloud Run startup script)
CMD exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

```bash
# deploy-backend.sh
#!/bin/bash

# Build and push container
gcloud builds submit --tag gcr.io/$PROJECT_ID/cmms-backend

# Deploy to Cloud Run
gcloud run deploy cmms-backend \
  --image gcr.io/$PROJECT_ID/cmms-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL \
  --set-env-vars REDIS_URL=$REDIS_URL \
  --add-cloudsql-instances $CLOUD_SQL_INSTANCE \
  --min-instances 1 \
  --max-instances 10 \
  --memory 1Gi \
  --cpu 1
```

**2. Firebase Hosting (Frontend):**
```json
// firebase.json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

```bash
# deploy-frontend.sh
#!/bin/bash

cd frontend

# Build production bundle
npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

**3. Cloud SQL Setup:**
```bash
# create-database.sh
#!/bin/bash

# Create Cloud SQL instance
gcloud sql instances create cmms-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --backup \
  --backup-start-time=03:00

# Create database
gcloud sql databases create cmms_prod \
  --instance=cmms-db

# Create user
gcloud sql users create cmms_user \
  --instance=cmms-db \
  --password=$DB_PASSWORD
```

**4. Cloud Storage Buckets:**
```bash
# create-storage.sh
#!/bin/bash

# Create buckets
gsutil mb -l us-central1 gs://$PROJECT_ID-cmms-documents
gsutil mb -l us-central1 gs://$PROJECT_ID-cmms-ml-models
gsutil mb -l us-central1 gs://$PROJECT_ID-cmms-reports

# Set lifecycle policies
gsutil lifecycle set lifecycle-config.json gs://$PROJECT_ID-cmms-reports
```

**5. Cloud Composer Setup:**
```bash
# create-composer.sh
#!/bin/bash

gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-1 \
  --disk-size 30GB
```

## Monitoring and Observability

### Metrics to Track

**Application Metrics:**
- API request rate and latency (p50, p95, p99)
- Error rate by endpoint
- Database query performance
- ML prediction latency
- Work order creation rate
- Active users count

**Business Metrics:**
- Work orders completed per day
- Average time to complete work orders (MTTR)
- Asset uptime percentage
- Prediction accuracy rate
- Maintenance plan compliance rate

**Infrastructure Metrics:**
- Cloud Run instance count
- Cloud SQL connections
- Cloud Storage bandwidth
- Pub/Sub message throughput

### Alerting Rules

```yaml
# Example Cloud Monitoring alert policy
displayName: "High API Error Rate"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
      comparison: COMPARISON_GT
      thresholdValue: 0.05
      duration: 300s
notificationChannels:
  - projects/$PROJECT_ID/notificationChannels/email-admins
  - projects/$PROJECT_ID/notificationChannels/telegram-bot
```

### Logging Strategy

**Structured Logging Format:**
```json
{
  "timestamp": "2025-11-13T10:30:00Z",
  "severity": "INFO",
  "service": "cmms-backend",
  "trace": "projects/PROJECT_ID/traces/TRACE_ID",
  "message": "Work order created",
  "context": {
    "user_id": "uuid",
    "work_order_id": "uuid",
    "asset_id": "uuid",
    "action": "create_work_order"
  }
}
```

**Log Retention:**
- Application logs: 30 days
- Audit logs: 1 year
- Error logs: 90 days

This design provides a comprehensive blueprint for building the CMMS system with modern cloud-native architecture, robust error handling, comprehensive testing, and production-ready deployment strategies.
