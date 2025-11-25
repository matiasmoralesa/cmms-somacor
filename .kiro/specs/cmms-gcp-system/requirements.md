# Requirements Document - Sistema CMMS Avanzado

## Introduction

Este documento define los requisitos para un Sistema de Gestión de Mantenimiento Computarizado (CMMS) moderno y distribuido, optimizado para Google Cloud Platform (GCP). El sistema se enfoca en la predicción de fallas mediante inteligencia artificial, automatización de procesos de mantenimiento, y gestión integral de activos industriales. La arquitectura aprovecha servicios gestionados de GCP para maximizar escalabilidad y reducir sobrecarga operativa.

## Glossary

- **CMMS_System**: El Sistema de Gestión de Mantenimiento Computarizado completo, incluyendo backend, frontend, servicios de ML y bot de Telegram
- **Backend_API**: Servicio Django REST Framework desplegado en Cloud Run que expone endpoints HTTP/REST
- **Frontend_App**: Aplicación React con TypeScript desplegada en Firebase Hosting
- **ML_Service**: Servicio de Machine Learning para predicción de fallas desplegado en Vertex AI
- **Telegram_Bot**: Bot de Telegram desplegado como Cloud Function o Cloud Run para interacción con usuarios
- **Cloud_Composer**: Servicio gestionado de Apache Airflow en GCP para orquestación de workflows
- **Work_Order**: Orden de Trabajo (OT) que representa una tarea de mantenimiento asignada
- **Asset**: Equipo o activo industrial registrado en el sistema
- **Vehicle_Type**: Tipo de vehículo (Camión Supersucker, Camioneta MDO, Retroexcavadora MDO, Cargador Frontal MDO, Minicargador MDO)
- **Maintenance_Plan**: Plan de mantenimiento preventivo o predictivo programado
- **Checklist**: Lista de verificación dinámica para inspecciones de mantenimiento basada en plantillas específicas por Vehicle_Type
- **Checklist_Template**: Plantilla predefinida de checklist según código (F-PR-020-CH01, F-PR-034-CH01, F-PR-037-CH01, F-PR-040-CH01)
- **Spare_Part**: Repuesto o pieza de inventario
- **User_Role**: Rol de usuario con tres niveles (ADMIN, SUPERVISOR, OPERADOR)
- **Failure_Prediction**: Predicción de falla generada por el modelo de ML
- **Cloud_Storage_Bucket**: Almacenamiento de objetos en GCP para archivos y documentos
- **Cloud_SQL_Database**: Base de datos PostgreSQL gestionada en GCP
- **Real_Time_Notification**: Notificación enviada mediante WebSockets o Cloud Pub/Sub

## Requirements

### Requirement 1: Gestión de Vehículos y Activos

**User Story:** Como administrador del sistema, quiero gestionar el inventario completo de vehículos (Camión Supersucker, Camionetas MDO, Retroexcavadora MDO, Cargador Frontal MDO, Minicargador MDO) con sus documentos asociados, para mantener un registro centralizado y accesible de todos los recursos de la flota.

#### Acceptance Criteria

1. THE Backend_API SHALL provide CRUD endpoints for Asset management including name, Vehicle_Type, model, serial number, license plate, location, installation date, and status fields
2. THE Backend_API SHALL restrict Vehicle_Type to exactly five predefined types (Camión Supersucker, Camioneta MDO, Retroexcavadora MDO, Cargador Frontal MDO, Minicargador MDO)
3. WHEN a user uploads a document or photo for an Asset, THE Backend_API SHALL store the file in Cloud_Storage_Bucket and save the reference URL in Cloud_SQL_Database
4. THE Frontend_App SHALL display a searchable and filterable list of all Assets with pagination support and filtering by Vehicle_Type
5. THE Backend_API SHALL validate that Asset serial numbers and license plates are unique within the system before creation
6. WHEN an Asset is deleted, THE Backend_API SHALL archive the Asset record instead of permanent deletion to maintain historical data

### Requirement 2: Órdenes de Trabajo

**User Story:** Como supervisor de mantenimiento, quiero crear, asignar y dar seguimiento a órdenes de trabajo, para coordinar eficientemente las actividades de mantenimiento del equipo técnico.

#### Acceptance Criteria

1. THE Backend_API SHALL provide endpoints to create Work_Order with fields for title, description, priority, assigned technician, Asset reference, scheduled date, and status
2. WHEN a Work_Order is created or updated, THE CMMS_System SHALL send Real_Time_Notification to assigned users via Cloud Pub/Sub
3. THE Frontend_App SHALL display Work_Order status transitions including pending, in-progress, completed, and cancelled states
4. THE Backend_API SHALL allow filtering Work_Order by status, priority, assigned user, and date range
5. WHEN a Work_Order is completed, THE Backend_API SHALL require completion notes and actual hours worked before status change

### Requirement 3: Planes de Mantenimiento

**User Story:** Como ingeniero de confiabilidad, quiero programar planes de mantenimiento preventivo y predictivo para los activos, para reducir fallas inesperadas y optimizar la disponibilidad de equipos.

#### Acceptance Criteria

1. THE Backend_API SHALL provide endpoints to create Maintenance_Plan with recurrence rules (daily, weekly, monthly, custom intervals)
2. THE Cloud_Composer SHALL execute a DAG that generates Work_Order automatically based on active Maintenance_Plan schedules
3. WHEN a Maintenance_Plan is linked to a Failure_Prediction, THE Backend_API SHALL adjust the schedule priority to high
4. THE Frontend_App SHALL display a calendar view showing scheduled and completed maintenance activities
5. THE Backend_API SHALL allow pausing and resuming Maintenance_Plan without deleting historical data

### Requirement 4: Inventario de Repuestos

**User Story:** Como técnico de mantenimiento, quiero consultar la disponibilidad de repuestos y recibir alertas de stock bajo, para asegurar que tengo las piezas necesarias antes de iniciar un trabajo.

#### Acceptance Criteria

1. THE Backend_API SHALL provide CRUD endpoints for Spare_Part management including part number, description, quantity, minimum stock level, and location
2. WHEN Spare_Part quantity falls below minimum stock level, THE Backend_API SHALL create an alert notification
3. THE Backend_API SHALL track Spare_Part usage history linked to Work_Order for consumption analysis
4. THE Frontend_App SHALL display Spare_Part inventory with visual indicators for low stock items
5. THE Backend_API SHALL validate that Spare_Part quantities cannot be negative values

### Requirement 5: Checklists Específicos por Tipo de Vehículo

**User Story:** Como supervisor, quiero utilizar checklists predefinidos específicos para cada tipo de vehículo (Camión Supersucker, Camionetas MDO, Retroexcavadora MDO, Cargador Frontal MDO, Minicargador MDO) y generar PDFs de inspecciones completadas, para estandarizar procedimientos y mantener registros de cumplimiento.

#### Acceptance Criteria

1. THE Backend_API SHALL provide five predefined Checklist_Template corresponding to the five Vehicle_Type with their specific inspection items and codes (F-PR-020-CH01, F-PR-034-CH01, F-PR-037-CH01, F-PR-040-CH01, and Camión Supersucker)
2. THE Backend_API SHALL prevent deletion or modification of the structure of predefined Checklist_Template to maintain standardization
3. WHEN a Checklist is completed, THE Backend_API SHALL generate a PDF report matching the original format and store it in Cloud_Storage_Bucket
4. THE Frontend_App SHALL allow technicians to complete Checklist items with response types including yes/no, text, numeric values, and photo uploads
5. THE Backend_API SHALL link completed Checklist to Work_Order and Asset for traceability
6. THE Backend_API SHALL calculate Checklist completion percentage and flag items marked as non-compliant or requiring attention

### Requirement 6: Predicción de Fallas con Machine Learning

**User Story:** Como gerente de mantenimiento, quiero recibir alertas predictivas de posibles fallas en equipos críticos, para tomar acciones preventivas antes de que ocurran paros no planificados.

#### Acceptance Criteria

1. THE ML_Service SHALL expose a prediction endpoint that accepts Asset telemetry data and returns failure probability score
2. THE Cloud_Composer SHALL execute a DAG that extracts historical data from Cloud_SQL_Database, trains the ML model in Dataproc, and deploys the updated model to Vertex AI
3. WHEN ML_Service predicts failure probability above 70 percent, THE Backend_API SHALL create a high-priority alert and notify relevant users
4. THE Backend_API SHALL log all Failure_Prediction with timestamp, Asset reference, probability score, and recommended actions
5. THE Frontend_App SHALL display a dashboard with Failure_Prediction trends and Asset health scores

### Requirement 7: Automatización con Cloud Composer

**User Story:** Como administrador del sistema, quiero automatizar tareas recurrentes como generación de reportes y mantenimiento preventivo, para reducir trabajo manual y asegurar consistencia operativa.

#### Acceptance Criteria

1. THE Cloud_Composer SHALL execute a DAG for ETL and ML retraining on a weekly schedule
2. THE Cloud_Composer SHALL execute a DAG that generates preventive Work_Order based on Maintenance_Plan schedules daily at 6 AM
3. THE Cloud_Composer SHALL execute a DAG that generates weekly performance reports and sends them via email using SendGrid integration
4. WHEN a Cloud_Composer DAG fails, THE CMMS_System SHALL send error notifications to administrators via email and Telegram_Bot
5. THE Backend_API SHALL provide endpoints to manually trigger Cloud_Composer DAGs for testing and emergency execution

### Requirement 8: Comunicación en Tiempo Real

**User Story:** Como técnico, quiero recibir notificaciones instantáneas cuando se me asigna una orden de trabajo o hay cambios importantes, para responder rápidamente a las necesidades operativas.

#### Acceptance Criteria

1. THE Backend_API SHALL publish notification events to Cloud Pub/Sub topics for Work_Order assignments, status changes, and alerts
2. THE Frontend_App SHALL subscribe to Real_Time_Notification via WebSocket connection or polling mechanism
3. WHEN a user is offline, THE Backend_API SHALL queue Real_Time_Notification for delivery when the user reconnects
4. THE Backend_API SHALL allow users to configure notification preferences for different event types
5. THE Telegram_Bot SHALL receive Real_Time_Notification from Cloud Pub/Sub and forward them to subscribed users

### Requirement 9: Bot de Telegram con Sistema de Roles

**User Story:** Como usuario móvil, quiero interactuar con el sistema CMMS mediante un bot de Telegram con comandos específicos según mi rol (ADMIN, SUPERVISOR, OPERADOR), para acceder a información crítica sin necesidad de abrir la aplicación web.

#### Acceptance Criteria

1. THE Telegram_Bot SHALL authenticate users and assign User_Role (ADMIN, SUPERVISOR, or OPERADOR) based on their Telegram ID registered in Cloud_SQL_Database
2. THE Telegram_Bot SHALL respond to command /status with system health metrics and active alerts count for all roles
3. THE Telegram_Bot SHALL respond to command /equipos with complete Asset list for ADMIN and SUPERVISOR, and only assigned Assets for OPERADOR
4. THE Telegram_Bot SHALL respond to command /ordenes with all Work_Order for ADMIN and SUPERVISOR, and only assigned Work_Order for OPERADOR
5. THE Telegram_Bot SHALL respond to command /pendientes with count of pending Work_Order by priority level filtered by user permissions
6. THE Telegram_Bot SHALL respond to command /alertas with recent Failure_Prediction and system alerts accessible to ADMIN and SUPERVISOR only
7. THE Telegram_Bot SHALL respond to command /kpis with key performance indicators including MTBF, MTTR, and equipment availability accessible to ADMIN and SUPERVISOR only
8. WHEN an OPERADOR attempts restricted commands (/alertas, /kpis, /admin), THE Telegram_Bot SHALL respond with permission denied message
9. THE Telegram_Bot SHALL be deployed as Cloud Function or lightweight Cloud Run service to handle Telegram webhooks

### Requirement 10: Autenticación y Autorización con Perfiles Específicos

**User Story:** Como administrador de seguridad, quiero controlar el acceso al sistema mediante autenticación robusta y tres perfiles específicos (ADMIN, SUPERVISOR, OPERADOR), para proteger información sensible y limitar acciones según responsabilidades.

#### Acceptance Criteria

1. THE Backend_API SHALL implement JWT-based authentication for all protected endpoints
2. THE Backend_API SHALL support exactly three User_Role types (ADMIN, SUPERVISOR, OPERADOR) with specific permissions
3. THE Backend_API SHALL allow ADMIN and SUPERVISOR roles to view all Work_Order, Assets, and Checklists
4. THE Backend_API SHALL restrict OPERADOR role to view only assigned Work_Order and Checklists for their assigned Assets
5. THE Backend_API SHALL allow only ADMIN role to access administration module for user management, master data, and system configuration
6. THE Backend_API SHALL allow ADMIN and SUPERVISOR roles to create maintenance plans and view calendar
7. WHEN a user attempts an unauthorized action, THE Backend_API SHALL return HTTP 403 Forbidden status with descriptive error message
8. THE Backend_API SHALL require license registration with complete operator information including license type, expiration date, and license photo before allowing Asset operation
9. THE Backend_API SHALL log all authentication attempts and authorization failures for security audit

### Requirement 11: Despliegue en Google Cloud Platform

**User Story:** Como ingeniero DevOps, quiero desplegar el sistema completo en GCP usando Infrastructure as Code, para asegurar reproducibilidad, escalabilidad y facilitar actualizaciones.

#### Acceptance Criteria

1. THE Backend_API SHALL be containerized using Dockerfile and deployed to Cloud Run with auto-scaling configuration
2. THE Frontend_App SHALL be built with Vite and deployed to Firebase Hosting with CDN distribution
3. THE CMMS_System SHALL use Cloud_SQL_Database (PostgreSQL) with automated backups enabled daily
4. THE CMMS_System SHALL store all files (documents, photos, PDFs, ML models) in Cloud_Storage_Bucket with lifecycle policies
5. THE CMMS_System SHALL include docker-compose.yml for local development environment setup
6. THE CMMS_System SHALL provide gcloud deployment scripts for automated provisioning of Cloud Run, Cloud SQL, and Cloud Storage resources
7. WHEN Cloud Run instances scale to zero, THE Backend_API SHALL reconnect to Cloud_SQL_Database on next request within 5 seconds

### Requirement 12: Monitoreo y Observabilidad

**User Story:** Como ingeniero de operaciones, quiero monitorear el rendimiento del sistema y recibir alertas de problemas, para mantener alta disponibilidad y resolver incidentes rápidamente.

#### Acceptance Criteria

1. THE Backend_API SHALL send logs to Cloud Logging with structured JSON format including severity levels
2. THE Backend_API SHALL expose health check endpoints for Cloud Run readiness and liveness probes
3. THE CMMS_System SHALL configure Cloud Monitoring alerts for API error rates above 5 percent, database connection failures, and Cloud Run instance crashes
4. THE Backend_API SHALL track API response times and send metrics to Cloud Monitoring
5. WHEN critical errors occur, THE CMMS_System SHALL send notifications to administrators via email and Telegram_Bot

### Requirement 13: Reportes y Analíticas

**User Story:** Como gerente de operaciones, quiero generar reportes personalizados sobre indicadores de mantenimiento, para tomar decisiones basadas en datos y presentar resultados a la dirección.

#### Acceptance Criteria

1. THE Backend_API SHALL provide endpoints to generate reports for Work_Order completion rates, Asset downtime, and Spare_Part consumption
2. THE Frontend_App SHALL display interactive charts using Recharts library for KPIs including MTBF, MTTR, OEE, and maintenance costs
3. THE Cloud_Composer SHALL generate automated weekly reports in PDF format and send them via email
4. THE Backend_API SHALL allow exporting report data in CSV and JSON formats
5. THE Frontend_App SHALL provide date range filters and Asset grouping options for custom report generation

### Requirement 14: Gestión de Configuración y Datos Maestros

**User Story:** Como administrador del sistema, quiero configurar parámetros globales y gestionar datos maestros como ubicaciones y categorías, para personalizar el sistema según las necesidades de la organización.

#### Acceptance Criteria

1. THE Backend_API SHALL provide endpoints to manage master data including Asset categories, locations, priority levels, and Work_Order types
2. THE Backend_API SHALL allow configuration of system parameters including notification settings, ML model thresholds, and report schedules
3. THE Backend_API SHALL validate that master data deletions are prevented when referenced by existing records
4. THE Frontend_App SHALL provide administration interface for User_Role management and permission assignment
5. THE Backend_API SHALL maintain audit trail of all configuration changes with user and timestamp information

### Requirement 16: Gestión de Ubicaciones

**User Story:** Como administrador, quiero crear y gestionar ubicaciones físicas donde se encuentran los activos, para organizar geográficamente el inventario de equipos y facilitar la planificación logística.

#### Acceptance Criteria

1. THE Backend_API SHALL provide CRUD endpoints for Location management including name, address, coordinates, and description fields
2. THE Backend_API SHALL validate that Location names are unique within the system
3. THE Backend_API SHALL prevent deletion of Location records that are referenced by existing Assets
4. THE Frontend_App SHALL display a list of all locations with search and filter capabilities accessible only to ADMIN role
5. THE Frontend_App SHALL provide a form interface for creating and editing locations accessible only to ADMIN role

### Requirement 17: Gestión de Usuarios

**User Story:** Como administrador, quiero crear y gestionar cuentas de usuario con sus roles y permisos, para controlar el acceso al sistema y asignar responsabilidades apropiadas.

#### Acceptance Criteria

1. THE Backend_API SHALL provide CRUD endpoints for User management including username, email, full name, User_Role, and active status fields
2. THE Backend_API SHALL validate that usernames and email addresses are unique within the system
3. THE Backend_API SHALL allow only ADMIN role to create, modify, and deactivate user accounts
4. THE Frontend_App SHALL display a user management interface with list, create, edit, and deactivate functions accessible only to ADMIN role
5. THE Backend_API SHALL send email notification to new users with temporary password and login instructions
6. THE Backend_API SHALL require password change on first login for new user accounts

### Requirement 18: Actualización de Estado de Máquina por Operadores

**User Story:** Como operador, quiero actualizar el estado operativo de las máquinas asignadas a mí, para mantener información en tiempo real sobre la disponibilidad y condición de los equipos.

#### Acceptance Criteria

1. THE Backend_API SHALL provide an endpoint to update Asset operational status including status type (Operando, Detenida, En Mantenimiento, Fuera de Servicio), odometer/hour meter reading, fuel level percentage, and general condition notes
2. THE Backend_API SHALL allow OPERADOR role to update status only for Assets assigned to them through active Work_Order
3. THE Backend_API SHALL allow ADMIN and SUPERVISOR roles to update status for any Asset
4. THE Backend_API SHALL create a status history record with timestamp, user, and previous values for each status update
5. THE Frontend_App SHALL provide a mobile-optimized status update form accessible to OPERADOR role showing only their assigned Assets
6. THE Frontend_App SHALL display current status and status history for each Asset accessible to all roles
7. WHEN an Asset status is updated to "Fuera de Servicio", THE Backend_API SHALL create an alert notification to ADMIN and SUPERVISOR roles

### Requirement 19: Integración y Extensibilidad

**User Story:** Como arquitecto de sistemas, quiero que el CMMS pueda integrarse con otros sistemas empresariales y sea extensible para futuras funcionalidades, para maximizar el valor de la inversión tecnológica.

#### Acceptance Criteria

1. THE Backend_API SHALL expose OpenAPI (Swagger) documentation for all REST endpoints
2. THE Backend_API SHALL provide webhook endpoints for external systems to receive event notifications
3. THE Backend_API SHALL support API versioning to maintain backward compatibility during updates
4. THE CMMS_System SHALL use environment variables for all configuration parameters to support multiple deployment environments
5. THE Backend_API SHALL implement rate limiting of 100 requests per minute per user to prevent abuse
