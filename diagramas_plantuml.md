# 📊 Diagramas PlantUML - Sistema CMMS SOMACOR

**Fecha**: 18 de Noviembre de 2025

---

## 1. Diagrama de Casos de Uso

```plantuml
@startuml casos_uso_cmms
left to right direction
skinparam packageStyle rectangle

actor "Administrador" as admin
actor "Supervisor" as supervisor
actor "Operador" as operador
actor "Sistema Externo" as sistema

rectangle "Sistema CMMS SOMACOR" {
  
  package "Gestión de Usuarios" {
    usecase "Crear Usuario" as UC1
    usecase "Modificar Usuario" as UC2
    usecase "Eliminar Usuario" as UC3
    usecase "Asignar Roles" as UC4
  }
  
  package "Gestión de Activos" {
    usecase "Registrar Activo" as UC5
    usecase "Modificar Activo" as UC6
    usecase "Consultar Activo" as UC7
    usecase "Cargar Documentos" as UC8
  }
  
  package "Órdenes de Trabajo" {
    usecase "Crear Orden de Trabajo" as UC9
    usecase "Asignar Orden" as UC10
    usecase "Completar Orden" as UC11
    usecase "Consultar Órdenes" as UC12
  }
  
  package "Checklists" {
    usecase "Seleccionar Plantilla" as UC13
    usecase "Completar Checklist" as UC14
    usecase "Generar PDF" as UC15
    usecase "Firmar Digitalmente" as UC16
  }
  
  package "Inventario" {
    usecase "Registrar Repuesto" as UC17
    usecase "Ajustar Stock" as UC18
    usecase "Consultar Inventario" as UC19
    usecase "Alertas Stock Bajo" as UC20
  }
  
  package "Mantenimiento" {
    usecase "Crear Plan Mantenimiento" as UC21
    usecase "Programar Mantenimiento" as UC22
    usecase "Generar Órdenes Automáticas" as UC23
  }
  
  package "Reportes y Analytics" {
    usecase "Generar Reportes" as UC24
    usecase "Consultar KPIs" as UC25
    usecase "Exportar Datos" as UC26
  }
  
  package "Notificaciones" {
    usecase "Enviar Notificación" as UC27
    usecase "Configurar Preferencias" as UC28
  }
  
  package "Predicciones IA" {
    usecase "Predecir Fallas" as UC29
    usecase "Generar Alertas" as UC30
  }
}

' Relaciones Administrador
admin --> UC1
admin --> UC2
admin --> UC3
admin --> UC4
admin --> UC5
admin --> UC6
admin --> UC7
admin --> UC8
admin --> UC17
admin --> UC18
admin --> UC19
admin --> UC21
admin --> UC22
admin --> UC24
admin --> UC25
admin --> UC26
admin --> UC28

' Relaciones Supervisor
supervisor --> UC7
supervisor --> UC9
supervisor --> UC10
supervisor --> UC12
supervisor --> UC13
supervisor --> UC19
supervisor --> UC21
supervisor --> UC22
supervisor --> UC24
supervisor --> UC25

' Relaciones Operador
operador --> UC7
operador --> UC11
operador --> UC12
operador --> UC13
operador --> UC14
operador --> UC15
operador --> UC16
operador --> UC19

' Relaciones Sistema
sistema --> UC23
sistema --> UC27
sistema --> UC29
sistema --> UC30

' Relaciones include/extend
UC9 ..> UC27 : <<include>>
UC10 ..> UC27 : <<include>>
UC11 ..> UC27 : <<include>>
UC14 ..> UC15 : <<include>>
UC15 ..> UC16 : <<extend>>
UC18 ..> UC20 : <<include>>
UC22 ..> UC23 : <<include>>
UC29 ..> UC30 : <<include>>

@enduml
```

---

## 2. Diagrama de Componentes

```plantuml
@startuml componentes_cmms
!define RECTANGLE class

skinparam component {
  BackgroundColor LightBlue
  BorderColor DarkBlue
  ArrowColor DarkBlue
}

package "Frontend - React" {
  component [Aplicación Web React] as WebApp
  component [Componentes UI] as UI
  component [Gestión de Estado] as State
  component [Servicios API] as APIClient
  component [Autenticación] as AuthClient
}

package "Backend - Django" {
  component [API REST] as API
  component [Autenticación JWT] as Auth
  component [Módulo Activos] as Assets
  component [Módulo Órdenes] as Orders
  component [Módulo Checklists] as Checklists
  component [Módulo Inventario] as Inventory
  component [Módulo Mantenimiento] as Maintenance
  component [Módulo Reportes] as Reports
  component [Módulo Notificaciones] as Notifications
  component [Módulo Predicciones] as Predictions
}

package "Servicios GCP" {
  database "Cloud SQL\nPostgreSQL" as DB
  storage "Cloud Storage" as Storage
  queue "Cloud Pub/Sub" as PubSub
  component "Cloud Composer\n(Airflow)" as Composer
  component "Vertex AI" as VertexAI
}

package "Servicios Externos" {
  component [SendGrid\nEmail] as Email
  component [Telegram Bot] as Telegram
}

' Relaciones Frontend
WebApp --> UI
WebApp --> State
WebApp --> APIClient
WebApp --> AuthClient

' Relaciones Frontend-Backend
APIClient --> API : HTTPS/REST
AuthClient --> Auth : JWT

' Relaciones Backend
API --> Auth
API --> Assets
API --> Orders
API --> Checklists
API --> Inventory
API --> Maintenance
API --> Reports
API --> Notifications
API --> Predictions

' Relaciones Backend-Base de Datos
Assets --> DB
Orders --> DB
Checklists --> DB
Inventory --> DB
Maintenance --> DB
Reports --> DB
Notifications --> DB
Predictions --> DB

' Relaciones Backend-Storage
Checklists --> Storage : PDFs
Assets --> Storage : Documentos
Reports --> Storage : Reportes

' Relaciones Backend-PubSub
Notifications --> PubSub : Eventos
Orders --> PubSub : Eventos

' Relaciones Backend-Composer
Maintenance --> Composer : Programación
Predictions --> Composer : Entrenamiento

' Relaciones Backend-VertexAI
Predictions --> VertexAI : Predicciones

' Relaciones Servicios Externos
Notifications --> Email
PubSub --> Telegram

@enduml
```

---

## 3. Diagrama Entidad-Relación (ER)

```plantuml
@startuml modelo_datos_cmms
!define TABLE(x) class x << (T,#FFAAAA) >>
!define PK(x) <u>x</u>
!define FK(x) <i>x</i>

hide methods
hide stereotypes

entity "User" as user {
  PK(id) : UUID
  --
  email : VARCHAR(255)
  password : VARCHAR(255)
  first_name : VARCHAR(100)
  last_name : VARCHAR(100)
  FK(role_id) : UUID
  telegram_id : VARCHAR(50)
  phone : VARCHAR(20)
  rut : VARCHAR(12)
  license_type : VARCHAR(50)
  license_expiration : DATE
  license_photo_url : VARCHAR(500)
  is_active : BOOLEAN
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "Role" as role {
  PK(id) : UUID
  --
  name : VARCHAR(50)
  description : TEXT
  created_at : TIMESTAMP
}

entity "Asset" as asset {
  PK(id) : UUID
  --
  name : VARCHAR(200)
  asset_code : VARCHAR(50)
  vehicle_type : VARCHAR(50)
  FK(location_id) : UUID
  manufacturer : VARCHAR(100)
  model : VARCHAR(100)
  serial_number : VARCHAR(100)
  license_plate : VARCHAR(20)
  installation_date : DATE
  status : VARCHAR(20)
  criticality : VARCHAR(20)
  specifications : JSON
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "Location" as location {
  PK(id) : UUID
  --
  name : VARCHAR(200)
  code : VARCHAR(50)
  description : TEXT
  created_at : TIMESTAMP
}

entity "AssetDocument" as asset_doc {
  PK(id) : UUID
  --
  FK(asset_id) : UUID
  document_type : VARCHAR(50)
  file_url : VARCHAR(500)
  file_name : VARCHAR(255)
  file_size : INTEGER
  FK(uploaded_by) : UUID
  uploaded_at : TIMESTAMP
}

entity "WorkOrder" as work_order {
  PK(id) : UUID
  --
  work_order_number : VARCHAR(50)
  title : VARCHAR(200)
  description : TEXT
  FK(asset_id) : UUID
  work_order_type : VARCHAR(20)
  priority : VARCHAR(20)
  status : VARCHAR(20)
  FK(assigned_to) : UUID
  FK(created_by) : UUID
  scheduled_date : TIMESTAMP
  started_at : TIMESTAMP
  completed_at : TIMESTAMP
  estimated_hours : DECIMAL(5,2)
  actual_hours : DECIMAL(5,2)
  completion_notes : TEXT
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "MaintenancePlan" as maintenance_plan {
  PK(id) : UUID
  --
  name : VARCHAR(200)
  FK(asset_id) : UUID
  plan_type : VARCHAR(20)
  recurrence_type : VARCHAR(20)
  recurrence_interval : INTEGER
  next_due_date : DATE
  is_active : BOOLEAN
  FK(checklist_template_id) : UUID
  estimated_duration : INTEGER
  FK(created_by) : UUID
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "ChecklistTemplate" as checklist_template {
  PK(id) : UUID
  --
  code : VARCHAR(50)
  name : VARCHAR(200)
  vehicle_type : VARCHAR(50)
  description : TEXT
  items : JSON
  is_system_template : BOOLEAN
  passing_score : INTEGER
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "ChecklistResponse" as checklist_response {
  PK(id) : UUID
  --
  FK(template_id) : UUID
  FK(work_order_id) : UUID
  FK(asset_id) : UUID
  responses : JSON
  score : INTEGER
  passed : BOOLEAN
  pdf_url : VARCHAR(500)
  FK(completed_by) : UUID
  completed_at : TIMESTAMP
}

entity "SparePart" as spare_part {
  PK(id) : UUID
  --
  part_number : VARCHAR(100)
  name : VARCHAR(200)
  description : TEXT
  category : VARCHAR(100)
  quantity : INTEGER
  minimum_stock : INTEGER
  unit_cost : DECIMAL(10,2)
  location : VARCHAR(100)
  supplier : VARCHAR(200)
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "StockMovement" as stock_movement {
  PK(id) : UUID
  --
  FK(spare_part_id) : UUID
  movement_type : VARCHAR(20)
  quantity : INTEGER
  FK(work_order_id) : UUID
  FK(performed_by) : UUID
  notes : TEXT
  created_at : TIMESTAMP
}

entity "FailurePrediction" as failure_prediction {
  PK(id) : UUID
  --
  FK(asset_id) : UUID
  prediction_date : TIMESTAMP
  failure_probability : DECIMAL(5,2)
  predicted_failure_date : DATE
  confidence_score : DECIMAL(5,2)
  model_version : VARCHAR(50)
  input_features : JSON
  recommendations : TEXT
  risk_level : VARCHAR(20)
  created_at : TIMESTAMP
}

entity "Alert" as alert {
  PK(id) : UUID
  --
  alert_type : VARCHAR(50)
  severity : VARCHAR(20)
  title : VARCHAR(200)
  message : TEXT
  FK(asset_id) : UUID
  FK(work_order_id) : UUID
  FK(prediction_id) : UUID
  is_read : BOOLEAN
  is_resolved : BOOLEAN
  FK(resolved_by) : UUID
  resolved_at : TIMESTAMP
  created_at : TIMESTAMP
}

entity "Notification" as notification {
  PK(id) : UUID
  --
  FK(user_id) : UUID
  notification_type : VARCHAR(50)
  title : VARCHAR(200)
  message : TEXT
  data : JSON
  is_read : BOOLEAN
  sent_via_telegram : BOOLEAN
  sent_via_email : BOOLEAN
  created_at : TIMESTAMP
}

' Relaciones
user }o--|| role
asset }o--|| location
asset_doc }o--|| asset
asset_doc }o--|| user
work_order }o--|| asset
work_order }o--|| user : assigned_to
work_order }o--|| user : created_by
maintenance_plan }o--|| asset
maintenance_plan }o--|| checklist_template
maintenance_plan }o--|| user
checklist_response }o--|| checklist_template
checklist_response }o--|| work_order
checklist_response }o--|| asset
checklist_response }o--|| user
stock_movement }o--|| spare_part
stock_movement }o--|| work_order
stock_movement }o--|| user
failure_prediction }o--|| asset
alert }o--|| asset
alert }o--|| work_order
alert }o--|| failure_prediction
alert }o--|| user
notification }o--|| user

@enduml
```

---

## 4. Diagrama de Arquitectura de Software

```plantuml
@startuml arquitectura_software_cmms
!include <C4/C4_Container>

LAYOUT_WITH_LEGEND()

title Arquitectura de Software - Sistema CMMS SOMACOR

Person(usuario, "Usuario", "Admin, Supervisor, Operador")
Person(tecnico, "Técnico", "Usuario móvil")

System_Boundary(cmms, "Sistema CMMS SOMACOR") {
    Container(web, "Aplicación Web", "React 18, TypeScript", "Interfaz de usuario responsive")
    Container(api, "API REST", "Django 4.x, DRF", "Lógica de negocio y endpoints")
    Container(worker, "Workers", "Celery", "Tareas asíncronas")
    ContainerDb(db, "Base de Datos", "PostgreSQL 15", "Almacenamiento de datos")
    Container(cache, "Caché", "Redis", "Caché de sesiones y datos")
    Container(storage, "Almacenamiento", "Cloud Storage", "Archivos y documentos")
}

System_Ext(pubsub, "Cloud Pub/Sub", "Sistema de mensajería")
System_Ext(composer, "Cloud Composer", "Orquestación de workflows")
System_Ext(vertexai, "Vertex AI", "Predicciones ML")
System_Ext(email, "SendGrid", "Envío de emails")
System_Ext(telegram, "Telegram Bot", "Notificaciones móviles")

Rel(usuario, web, "Usa", "HTTPS")
Rel(tecnico, web, "Usa", "HTTPS")
Rel(web, api, "Consume", "REST/JSON")
Rel(api, db, "Lee/Escribe", "SQL")
Rel(api, cache, "Lee/Escribe", "Redis Protocol")
Rel(api, storage, "Almacena", "HTTPS")
Rel(api, pubsub, "Publica eventos", "HTTPS")
Rel(api, worker, "Encola tareas", "Redis")
Rel(worker, db, "Lee/Escribe", "SQL")
Rel(worker, storage, "Almacena", "HTTPS")
Rel(pubsub, telegram, "Notifica", "Webhook")
Rel(composer, api, "Ejecuta", "HTTPS")
Rel(api, vertexai, "Predice", "HTTPS")
Rel(worker, email, "Envía", "HTTPS")

@enduml
```

---

## 5. Diagrama de Topología de Red

```plantuml
@startuml topologia_red_cmms
!include <C4/C4_Deployment>

LAYOUT_WITH_LEGEND()

title Topología de Red - Sistema CMMS SOMACOR

Deployment_Node(internet, "Internet", "Red Pública") {
    Deployment_Node(users, "Usuarios", "Navegadores Web") {
        Container(browser, "Navegador", "Chrome, Firefox, Safari", "Cliente web")
    }
}

Deployment_Node(gcp, "Google Cloud Platform", "us-central1") {
    
    Deployment_Node(cdn, "Firebase Hosting", "CDN Global") {
        Container(frontend, "Frontend", "React App", "Aplicación estática")
    }
    
    Deployment_Node(cloudrun, "Cloud Run", "Serverless") {
        Container(backend, "Backend API", "Django", "1-10 instancias")
    }
    
    Deployment_Node(cloudsql, "Cloud SQL", "Managed Database") {
        ContainerDb(database, "PostgreSQL", "15.4", "Base de datos principal")
    }
    
    Deployment_Node(memorystore, "Memorystore", "Managed Redis") {
        ContainerDb(redis, "Redis", "7.x", "Caché y sesiones")
    }
    
    Deployment_Node(gcs, "Cloud Storage", "Object Storage") {
        Container(storage, "Buckets", "Standard", "Archivos y documentos")
    }
    
    Deployment_Node(pubsub_node, "Cloud Pub/Sub", "Messaging") {
        Container(pubsub, "Topics/Subs", "Pub/Sub", "Mensajería asíncrona")
    }
    
    Deployment_Node(composer_node, "Cloud Composer", "Airflow") {
        Container(airflow, "DAGs", "Airflow 2.x", "Orquestación")
    }
    
    Deployment_Node(vertex_node, "Vertex AI", "ML Platform") {
        Container(ml, "Modelos ML", "Scikit-learn", "Predicciones")
    }
}

Rel(browser, frontend, "HTTPS:443", "TLS 1.3")
Rel(browser, backend, "HTTPS:443", "REST API")
Rel(backend, database, "TCP:5432", "PostgreSQL")
Rel(backend, redis, "TCP:6379", "Redis Protocol")
Rel(backend, storage, "HTTPS:443", "Cloud Storage API")
Rel(backend, pubsub, "HTTPS:443", "Pub/Sub API")
Rel(backend, ml, "HTTPS:443", "Vertex AI API")
Rel(airflow, backend, "HTTPS:443", "REST API")

@enduml
```

---

## 6. Diagrama de Infraestructura GCP

```plantuml
@startuml infraestructura_gcp_cmms
!include <gcp/GCPCommon>
!include <gcp/Compute/Cloud_Run>
!include <gcp/Databases/Cloud_SQL>
!include <gcp/Storage/Cloud_Storage>
!include <gcp/Networking/Cloud_Load_Balancing>
!include <gcp/Management/Cloud_Monitoring>
!include <gcp/Management/Cloud_Logging>
!include <gcp/Data_Analytics/Cloud_Composer>
!include <gcp/AI_and_Machine_Learning/Vertex_AI>

title Infraestructura GCP - Sistema CMMS SOMACOR

package "Región: us-central1" {
    
    package "Frontend" {
        node "Firebase Hosting" as firebase {
            component "React App" as react
            component "CDN Global" as cdn
        }
    }
    
    package "Backend" {
        Cloud_Run(cloudrun, "Cloud Run", "Backend API")
        component "Auto-scaling\n1-10 instancias" as scaling
    }
    
    package "Datos" {
        Cloud_SQL(cloudsql, "Cloud SQL", "PostgreSQL 15")
        component "Backups\nAutomáticos" as backups
        component "Réplica\nLectura" as replica
    }
    
    package "Almacenamiento" {
        Cloud_Storage(storage, "Cloud Storage", "Buckets")
        component "cmms-documents" as docs
        component "cmms-reports" as reports
        component "cmms-ml-models" as models
    }
    
    package "Mensajería" {
        component "Cloud Pub/Sub" as pubsub
        component "Topics" as topics
        component "Subscriptions" as subs
    }
    
    package "Orquestación" {
        Cloud_Composer(composer, "Cloud Composer", "Airflow 2.x")
        component "DAGs" as dags
    }
    
    package "Machine Learning" {
        Vertex_AI(vertexai, "Vertex AI", "Predicciones")
        component "Modelos\nEntrenados" as mlmodels
    }
    
    package "Monitoreo" {
        Cloud_Monitoring(monitoring, "Cloud Monitoring", "Métricas")
        Cloud_Logging(logging, "Cloud Logging", "Logs")
    }
}

react --> cloudrun : HTTPS
cloudrun --> cloudsql : Private IP
cloudrun --> storage : API
cloudrun --> pubsub : API
cloudrun --> vertexai : API
composer --> cloudrun : HTTPS
cloudrun --> monitoring : Métricas
cloudrun --> logging : Logs

@enduml
```

---

## 7. Diagrama de Secuencia - Crear Orden de Trabajo

```plantuml
@startuml secuencia_crear_orden
actor Supervisor
participant "Frontend\nReact" as Frontend
participant "API Gateway\nCloud Run" as API
participant "Auth Service" as Auth
participant "Work Order\nService" as WO
participant "Database\nPostgreSQL" as DB
participant "Pub/Sub" as PubSub
participant "Notification\nService" as Notif

Supervisor -> Frontend: Crear nueva orden
activate Frontend

Frontend -> API: POST /api/v1/work-orders/\n{title, description, asset_id, ...}
activate API

API -> Auth: Validar JWT token
activate Auth
Auth --> API: Token válido, user_id
deactivate Auth

API -> WO: create_work_order(data, user_id)
activate WO

WO -> DB: INSERT INTO work_orders
activate DB
DB --> WO: work_order_id
deactivate DB

WO -> DB: SELECT asset, user info
activate DB
DB --> WO: asset_data, user_data
deactivate DB

WO -> PubSub: Publicar evento\n"work_order.created"
activate PubSub
PubSub --> WO: Evento publicado
deactivate PubSub

WO --> API: work_order_created
deactivate WO

API --> Frontend: 201 Created\n{work_order_data}
deactivate API

Frontend --> Supervisor: Orden creada exitosamente
deactivate Frontend

PubSub -> Notif: Evento "work_order.created"
activate Notif

Notif -> DB: Crear notificación
activate DB
DB --> Notif: notification_id
deactivate DB

Notif -> Notif: Enviar email/telegram
Notif --> PubSub: Procesado
deactivate Notif

@enduml
```

---

## 8. Diagrama de Secuencia - Completar Checklist

```plantuml
@startuml secuencia_completar_checklist
actor Operador
participant "Frontend\nReact" as Frontend
participant "API Gateway" as API
participant "Checklist\nService" as Check
participant "Database" as DB
participant "Storage\nCloud Storage" as Storage
participant "PDF Generator" as PDF

Operador -> Frontend: Seleccionar plantilla checklist
activate Frontend

Frontend -> API: GET /api/v1/checklist-templates/\n?vehicle_type=CAMIONETA_MDO
activate API

API -> DB: SELECT templates
activate DB
DB --> API: template_data
deactivate DB

API --> Frontend: 200 OK {templates}
deactivate API

Frontend --> Operador: Mostrar plantilla

Operador -> Frontend: Completar items\n(respuestas, fotos, notas)

Operador -> Frontend: Enviar checklist

Frontend -> API: POST /api/v1/checklist-responses/\n{template_id, responses, ...}
activate API

API -> Check: create_response(data)
activate Check

Check -> DB: INSERT INTO checklist_responses
activate DB
DB --> Check: response_id
deactivate DB

Check -> PDF: generate_pdf(response_data)
activate PDF

PDF -> PDF: Crear PDF con formato\noriginal del checklist

PDF -> Storage: Subir PDF
activate Storage
Storage --> PDF: pdf_url
deactivate Storage

PDF --> Check: pdf_generated
deactivate PDF

Check -> DB: UPDATE response\nSET pdf_url = ?
activate DB
DB --> Check: updated
deactivate DB

Check --> API: response_created
deactivate Check

API --> Frontend: 201 Created\n{response_data, pdf_url}
deactivate API

Frontend --> Operador: Checklist completado\nPDF disponible
deactivate Frontend

@enduml
```

---

## Notas de Uso

### Cómo Generar los Diagramas

1. **Online**: Usar https://www.plantuml.com/plantuml/uml/
2. **VS Code**: Instalar extensión "PlantUML"
3. **CLI**: Instalar PlantUML y ejecutar:
   ```bash
   plantuml diagrama.puml
   ```

### Exportar a Imágenes

```bash
# PNG
plantuml -tpng diagrama.puml

# SVG (mejor calidad)
plantuml -tsvg diagrama.puml

# PDF
plantuml -tpdf diagrama.puml
```

### Incluir en Documento Word

1. Generar imágenes PNG o SVG
2. Insertar en Word: Insertar > Imágenes
3. Ajustar tamaño según necesidad
4. Agregar pie de figura con descripción

---

**Diagramas creados**: 18 de Noviembre de 2025  
**Formato**: PlantUML  
**Total de diagramas**: 8

