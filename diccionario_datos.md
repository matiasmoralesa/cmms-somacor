# 📚 Diccionario de Datos - Sistema CMMS SOMACOR

**Fecha**: 18 de Noviembre de 2025  
**Base de Datos**: PostgreSQL 15.4  
**Total de Tablas**: 15

---

## Tabla 1: users (Usuarios)

**Descripción**: Almacena información de los usuarios del sistema.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del usuario |
| email | VARCHAR | 255 | NO | UNIQUE | - | Correo electrónico (login) |
| password | VARCHAR | 255 | NO | - | - | Contraseña encriptada (bcrypt) |
| first_name | VARCHAR | 100 | NO | - | - | Nombre(s) del usuario |
| last_name | VARCHAR | 100 | NO | - | - | Apellido(s) del usuario |
| role_id | UUID | - | NO | FK | - | Referencia a tabla roles |
| telegram_id | VARCHAR | 50 | YES | UNIQUE | NULL | ID de Telegram para notificaciones |
| phone | VARCHAR | 20 | YES | - | NULL | Teléfono de contacto |
| rut | VARCHAR | 12 | NO | UNIQUE | - | RUT chileno (identificación) |
| license_type | VARCHAR | 50 | YES | - | NULL | Tipo de licencia (MUNICIPAL, INTERNAL, OTHER) |
| license_expiration | DATE | - | YES | - | NULL | Fecha de expiración de licencia |
| license_photo_url | VARCHAR | 500 | YES | - | NULL | URL de foto de licencia en Cloud Storage |
| is_active | BOOLEAN | - | NO | - | TRUE | Usuario activo/inactivo |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de última actualización |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)
- UNIQUE INDEX (rut)
- INDEX (role_id)
- INDEX (is_active)

**Restricciones**:
- CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
- CHECK (license_type IN ('MUNICIPAL', 'INTERNAL', 'OTHER', NULL))

---

## Tabla 2: roles (Roles)

**Descripción**: Define los roles de usuario en el sistema.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del rol |
| name | VARCHAR | 50 | NO | UNIQUE | - | Nombre del rol (ADMIN, SUPERVISOR, OPERADOR) |
| description | TEXT | - | YES | - | NULL | Descripción del rol |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (name)

**Restricciones**:
- CHECK (name IN ('ADMIN', 'SUPERVISOR', 'OPERADOR'))

**Datos Predefinidos**:
```sql
INSERT INTO roles (name, description) VALUES
('ADMIN', 'Administrador del sistema con acceso completo'),
('SUPERVISOR', 'Supervisor con acceso a gestión de órdenes y reportes'),
('OPERADOR', 'Operador con acceso limitado a sus tareas asignadas');
```

---

## Tabla 3: locations (Ubicaciones)

**Descripción**: Almacena las ubicaciones físicas donde se encuentran los activos.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de ubicación |
| name | VARCHAR | 200 | NO | - | - | Nombre de la ubicación |
| code | VARCHAR | 50 | NO | UNIQUE | - | Código único de ubicación |
| description | TEXT | - | YES | - | NULL | Descripción detallada |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (code)

---

## Tabla 4: assets (Activos/Vehículos)

**Descripción**: Almacena información de los activos y vehículos de la flota.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del activo |
| name | VARCHAR | 200 | NO | - | - | Nombre descriptivo del activo |
| asset_code | VARCHAR | 50 | NO | UNIQUE | - | Código único del activo |
| vehicle_type | VARCHAR | 50 | NO | - | - | Tipo de vehículo |
| location_id | UUID | - | NO | FK | - | Referencia a tabla locations |
| manufacturer | VARCHAR | 100 | YES | - | NULL | Fabricante del equipo |
| model | VARCHAR | 100 | YES | - | NULL | Modelo del equipo |
| serial_number | VARCHAR | 100 | NO | UNIQUE | - | Número de serie |
| license_plate | VARCHAR | 20 | YES | UNIQUE | NULL | Patente del vehículo |
| installation_date | DATE | - | YES | - | NULL | Fecha de instalación/compra |
| status | VARCHAR | 20 | NO | - | 'OPERATIONAL' | Estado actual del activo |
| criticality | VARCHAR | 20 | NO | - | 'MEDIUM' | Nivel de criticidad |
| specifications | JSONB | - | YES | - | '{}' | Especificaciones técnicas |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de última actualización |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (asset_code)
- UNIQUE INDEX (serial_number)
- INDEX (vehicle_type)
- INDEX (location_id)
- INDEX (status)

**Restricciones**:
- CHECK (vehicle_type IN ('CAMION_SUPERSUCKER', 'CAMIONETA_MDO', 'RETROEXCAVADORA_MDO', 'CARGADOR_FRONTAL_MDO', 'MINICARGADOR_MDO'))
- CHECK (status IN ('OPERATIONAL', 'DOWN', 'MAINTENANCE', 'RETIRED'))
- CHECK (criticality IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))

---

## Tabla 5: asset_documents (Documentos de Activos)

**Descripción**: Almacena documentos y fotos asociados a los activos.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del documento |
| asset_id | UUID | - | NO | FK | - | Referencia a tabla assets |
| document_type | VARCHAR | 50 | NO | - | - | Tipo de documento |
| file_url | VARCHAR | 500 | NO | - | - | URL del archivo en Cloud Storage |
| file_name | VARCHAR | 255 | NO | - | - | Nombre original del archivo |
| file_size | INTEGER | - | NO | - | - | Tamaño del archivo en bytes |
| uploaded_by | UUID | - | NO | FK | - | Usuario que subió el documento |
| uploaded_at | TIMESTAMP | - | NO | - | NOW() | Fecha de carga |

**Índices**:
- PRIMARY KEY (id)
- INDEX (asset_id)
- INDEX (uploaded_by)
- INDEX (document_type)

**Restricciones**:
- CHECK (document_type IN ('MANUAL', 'PHOTO', 'CERTIFICATE', 'DRAWING', 'OTHER'))
- CHECK (file_size > 0)

---

## Tabla 6: work_orders (Órdenes de Trabajo)

**Descripción**: Almacena las órdenes de trabajo de mantenimiento.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la orden |
| work_order_number | VARCHAR | 50 | NO | UNIQUE | - | Número de orden (auto-generado) |
| title | VARCHAR | 200 | NO | - | - | Título de la orden |
| description | TEXT | - | NO | - | - | Descripción detallada |
| asset_id | UUID | - | NO | FK | - | Referencia a tabla assets |
| work_order_type | VARCHAR | 20 | NO | - | - | Tipo de orden |
| priority | VARCHAR | 20 | NO | - | 'MEDIUM' | Prioridad de la orden |
| status | VARCHAR | 20 | NO | - | 'PENDING' | Estado actual |
| assigned_to | UUID | - | YES | FK | NULL | Usuario asignado |
| created_by | UUID | - | NO | FK | - | Usuario creador |
| scheduled_date | TIMESTAMP | - | YES | - | NULL | Fecha programada |
| started_at | TIMESTAMP | - | YES | - | NULL | Fecha de inicio real |
| completed_at | TIMESTAMP | - | YES | - | NULL | Fecha de completación |
| estimated_hours | DECIMAL | 5,2 | YES | - | NULL | Horas estimadas |
| actual_hours | DECIMAL | 5,2 | YES | - | NULL | Horas reales |
| completion_notes | TEXT | - | YES | - | NULL | Notas de completación |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de actualización |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (work_order_number)
- INDEX (asset_id)
- INDEX (assigned_to)
- INDEX (created_by)
- INDEX (status)
- INDEX (priority)
- INDEX (work_order_type)

**Restricciones**:
- CHECK (work_order_type IN ('CORRECTIVE', 'PREVENTIVE', 'PREDICTIVE', 'INSPECTION'))
- CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT'))
- CHECK (status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))

---

## Tabla 7: maintenance_plans (Planes de Mantenimiento)

**Descripción**: Almacena los planes de mantenimiento preventivo y predictivo.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del plan |
| name | VARCHAR | 200 | NO | - | - | Nombre del plan |
| asset_id | UUID | - | NO | FK | - | Referencia a tabla assets |
| plan_type | VARCHAR | 20 | NO | - | - | Tipo de plan |
| recurrence_type | VARCHAR | 20 | NO | - | - | Tipo de recurrencia |
| recurrence_interval | INTEGER | - | NO | - | 1 | Intervalo de recurrencia |
| next_due_date | DATE | - | NO | - | - | Próxima fecha de ejecución |
| is_active | BOOLEAN | - | NO | - | TRUE | Plan activo/inactivo |
| checklist_template_id | UUID | - | YES | FK | NULL | Plantilla de checklist asociada |
| estimated_duration | INTEGER | - | NO | - | - | Duración estimada en minutos |
| created_by | UUID | - | NO | FK | - | Usuario creador |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de actualización |

**Índices**:
- PRIMARY KEY (id)
- INDEX (asset_id)
- INDEX (is_active)
- INDEX (next_due_date)

**Restricciones**:
- CHECK (plan_type IN ('PREVENTIVE', 'PREDICTIVE'))
- CHECK (recurrence_type IN ('DAILY', 'WEEKLY', 'MONTHLY', 'CUSTOM'))
- CHECK (recurrence_interval > 0)
- CHECK (estimated_duration > 0)

---

**Continúa en la siguiente parte...**



## Tabla 8: checklist_templates (Plantillas de Checklist)

**Descripción**: Almacena las plantillas predefinidas de checklists por tipo de vehículo.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la plantilla |
| code | VARCHAR | 50 | NO | UNIQUE | - | Código de la plantilla |
| name | VARCHAR | 200 | NO | - | - | Nombre de la plantilla |
| vehicle_type | VARCHAR | 50 | NO | - | - | Tipo de vehículo asociado |
| description | TEXT | - | YES | - | NULL | Descripción de la plantilla |
| items | JSONB | - | NO | - | '[]' | Items del checklist en formato JSON |
| is_system_template | BOOLEAN | - | NO | - | FALSE | Plantilla del sistema (no editable) |
| passing_score | INTEGER | - | NO | - | 80 | Puntaje mínimo para aprobar (%) |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de actualización |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (code)
- INDEX (vehicle_type)
- INDEX (is_system_template)

**Restricciones**:
- CHECK (vehicle_type IN ('CAMION_SUPERSUCKER', 'CAMIONETA_MDO', 'RETROEXCAVADORA_MDO', 'CARGADOR_FRONTAL_MDO', 'MINICARGADOR_MDO'))
- CHECK (passing_score BETWEEN 0 AND 100)

**Estructura JSON de items**:
```json
[
  {
    "section": "Motor",
    "order": 1,
    "question": "Nivel de aceite motor",
    "response_type": "yes_no_na",
    "required": true,
    "observations_allowed": true
  }
]
```

---

## Tabla 9: checklist_responses (Respuestas de Checklist)

**Descripción**: Almacena las respuestas completadas de los checklists.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la respuesta |
| template_id | UUID | - | NO | FK | - | Referencia a checklist_templates |
| work_order_id | UUID | - | YES | FK | NULL | Orden de trabajo asociada |
| asset_id | UUID | - | NO | FK | - | Activo inspeccionado |
| responses | JSONB | - | NO | - | '[]' | Respuestas en formato JSON |
| score | INTEGER | - | NO | - | 0 | Puntaje obtenido (%) |
| passed | BOOLEAN | - | NO | - | FALSE | Checklist aprobado/reprobado |
| pdf_url | VARCHAR | 500 | YES | - | NULL | URL del PDF generado |
| completed_by | UUID | - | NO | FK | - | Usuario que completó |
| completed_at | TIMESTAMP | - | NO | - | NOW() | Fecha de completación |

**Índices**:
- PRIMARY KEY (id)
- INDEX (template_id)
- INDEX (work_order_id)
- INDEX (asset_id)
- INDEX (completed_by)
- INDEX (completed_at)

**Restricciones**:
- CHECK (score BETWEEN 0 AND 100)

**Estructura JSON de responses**:
```json
[
  {
    "item_order": 1,
    "response": "yes",
    "notes": "Oil level normal",
    "photo_url": "gs://bucket/photo.jpg"
  }
]
```

---

## Tabla 10: spare_parts (Repuestos)

**Descripción**: Almacena el inventario de repuestos y piezas.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del repuesto |
| part_number | VARCHAR | 100 | NO | UNIQUE | - | Número de parte |
| name | VARCHAR | 200 | NO | - | - | Nombre del repuesto |
| description | TEXT | - | YES | - | NULL | Descripción detallada |
| category | VARCHAR | 100 | NO | - | - | Categoría del repuesto |
| quantity | INTEGER | - | NO | - | 0 | Cantidad en stock |
| minimum_stock | INTEGER | - | NO | - | 0 | Stock mínimo |
| unit_cost | DECIMAL | 10,2 | NO | - | 0.00 | Costo unitario |
| location | VARCHAR | 100 | NO | - | - | Ubicación en bodega |
| supplier | VARCHAR | 200 | YES | - | NULL | Proveedor |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |
| updated_at | TIMESTAMP | - | NO | - | NOW() | Fecha de actualización |

**Índices**:
- PRIMARY KEY (id)
- UNIQUE INDEX (part_number)
- INDEX (category)
- INDEX (quantity)

**Restricciones**:
- CHECK (quantity >= 0)
- CHECK (minimum_stock >= 0)
- CHECK (unit_cost >= 0)

---

## Tabla 11: stock_movements (Movimientos de Stock)

**Descripción**: Registra los movimientos de entrada y salida de repuestos.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del movimiento |
| spare_part_id | UUID | - | NO | FK | - | Referencia a spare_parts |
| movement_type | VARCHAR | 20 | NO | - | - | Tipo de movimiento |
| quantity | INTEGER | - | NO | - | - | Cantidad movida |
| work_order_id | UUID | - | YES | FK | NULL | Orden de trabajo asociada |
| performed_by | UUID | - | NO | FK | - | Usuario que realizó el movimiento |
| notes | TEXT | - | YES | - | NULL | Notas adicionales |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha del movimiento |

**Índices**:
- PRIMARY KEY (id)
- INDEX (spare_part_id)
- INDEX (work_order_id)
- INDEX (performed_by)
- INDEX (created_at)

**Restricciones**:
- CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT'))
- CHECK (quantity != 0)

---

## Tabla 12: failure_predictions (Predicciones de Fallas)

**Descripción**: Almacena las predicciones de fallas generadas por el modelo de IA.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la predicción |
| asset_id | UUID | - | NO | FK | - | Activo analizado |
| prediction_date | TIMESTAMP | - | NO | - | NOW() | Fecha de la predicción |
| failure_probability | DECIMAL | 5,2 | NO | - | - | Probabilidad de falla (0-100) |
| predicted_failure_date | DATE | - | YES | - | NULL | Fecha estimada de falla |
| confidence_score | DECIMAL | 5,2 | NO | - | - | Nivel de confianza (0-100) |
| model_version | VARCHAR | 50 | NO | - | - | Versión del modelo usado |
| input_features | JSONB | - | NO | - | '{}' | Features usados en la predicción |
| recommendations | TEXT | - | YES | - | NULL | Recomendaciones |
| risk_level | VARCHAR | 20 | NO | - | - | Nivel de riesgo |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |

**Índices**:
- PRIMARY KEY (id)
- INDEX (asset_id)
- INDEX (prediction_date)
- INDEX (risk_level)

**Restricciones**:
- CHECK (failure_probability BETWEEN 0 AND 100)
- CHECK (confidence_score BETWEEN 0 AND 100)
- CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))

---

## Tabla 13: alerts (Alertas)

**Descripción**: Almacena las alertas generadas por el sistema.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la alerta |
| alert_type | VARCHAR | 50 | NO | - | - | Tipo de alerta |
| severity | VARCHAR | 20 | NO | - | - | Severidad de la alerta |
| title | VARCHAR | 200 | NO | - | - | Título de la alerta |
| message | TEXT | - | NO | - | - | Mensaje detallado |
| asset_id | UUID | - | YES | FK | NULL | Activo relacionado |
| work_order_id | UUID | - | YES | FK | NULL | Orden relacionada |
| prediction_id | UUID | - | YES | FK | NULL | Predicción relacionada |
| is_read | BOOLEAN | - | NO | - | FALSE | Alerta leída |
| is_resolved | BOOLEAN | - | NO | - | FALSE | Alerta resuelta |
| resolved_by | UUID | - | YES | FK | NULL | Usuario que resolvió |
| resolved_at | TIMESTAMP | - | YES | - | NULL | Fecha de resolución |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |

**Índices**:
- PRIMARY KEY (id)
- INDEX (alert_type)
- INDEX (severity)
- INDEX (asset_id)
- INDEX (is_read)
- INDEX (is_resolved)

**Restricciones**:
- CHECK (alert_type IN ('PREDICTION', 'LOW_STOCK', 'OVERDUE_MAINTENANCE', 'SYSTEM'))
- CHECK (severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL'))

---

## Tabla 14: notifications (Notificaciones)

**Descripción**: Almacena las notificaciones enviadas a los usuarios.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único de la notificación |
| user_id | UUID | - | NO | FK | - | Usuario destinatario |
| notification_type | VARCHAR | 50 | NO | - | - | Tipo de notificación |
| title | VARCHAR | 200 | NO | - | - | Título de la notificación |
| message | TEXT | - | NO | - | - | Mensaje de la notificación |
| data | JSONB | - | YES | - | '{}' | Datos adicionales |
| is_read | BOOLEAN | - | NO | - | FALSE | Notificación leída |
| sent_via_telegram | BOOLEAN | - | NO | - | FALSE | Enviada por Telegram |
| sent_via_email | BOOLEAN | - | NO | - | FALSE | Enviada por email |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de creación |

**Índices**:
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (notification_type)
- INDEX (is_read)
- INDEX (created_at)

**Restricciones**:
- CHECK (notification_type IN ('WORK_ORDER_ASSIGNED', 'WORK_ORDER_COMPLETED', 'ALERT', 'REMINDER', 'SYSTEM'))

---

## Tabla 15: audit_logs (Logs de Auditoría)

**Descripción**: Registra todas las acciones importantes del sistema para auditoría.

| Campo | Tipo | Longitud | Nulo | Clave | Default | Descripción |
|-------|------|----------|------|-------|---------|-------------|
| id | UUID | - | NO | PK | uuid_generate_v4() | Identificador único del log |
| user_id | UUID | - | YES | FK | NULL | Usuario que realizó la acción |
| action | VARCHAR | 100 | NO | - | - | Acción realizada |
| entity_type | VARCHAR | 50 | NO | - | - | Tipo de entidad afectada |
| entity_id | UUID | - | YES | - | NULL | ID de la entidad afectada |
| old_values | JSONB | - | YES | - | NULL | Valores anteriores |
| new_values | JSONB | - | YES | - | NULL | Valores nuevos |
| ip_address | VARCHAR | 45 | YES | - | NULL | Dirección IP del usuario |
| user_agent | VARCHAR | 500 | YES | - | NULL | User agent del navegador |
| created_at | TIMESTAMP | - | NO | - | NOW() | Fecha de la acción |

**Índices**:
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (action)
- INDEX (entity_type)
- INDEX (entity_id)
- INDEX (created_at)

**Restricciones**:
- CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT'))
- CHECK (entity_type IN ('USER', 'ASSET', 'WORK_ORDER', 'CHECKLIST', 'SPARE_PART', 'MAINTENANCE_PLAN'))

---

## Relaciones entre Tablas

### Diagrama de Relaciones

```
users (1) ──< (N) work_orders (created_by)
users (1) ──< (N) work_orders (assigned_to)
users (1) ──< (N) asset_documents (uploaded_by)
users (1) ──< (N) checklist_responses (completed_by)
users (1) ──< (N) stock_movements (performed_by)
users (1) ──< (N) notifications
users (N) ──> (1) roles

assets (1) ──< (N) work_orders
assets (1) ──< (N) asset_documents
assets (1) ──< (N) maintenance_plans
assets (1) ──< (N) checklist_responses
assets (1) ──< (N) failure_predictions
assets (1) ──< (N) alerts
assets (N) ──> (1) locations

work_orders (1) ──< (N) checklist_responses
work_orders (1) ──< (N) stock_movements
work_orders (1) ──< (N) alerts

maintenance_plans (N) ──> (1) checklist_templates

spare_parts (1) ──< (N) stock_movements

failure_predictions (1) ──< (N) alerts
```

---

## Triggers y Funciones

### Trigger: update_updated_at

**Descripción**: Actualiza automáticamente el campo `updated_at` en cada UPDATE.

**Tablas afectadas**:
- users
- assets
- work_orders
- maintenance_plans
- checklist_templates
- spare_parts

**Función**:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Trigger: generate_work_order_number

**Descripción**: Genera automáticamente el número de orden de trabajo.

**Formato**: WO-YYYYMMDD-NNNN

**Función**:
```sql
CREATE OR REPLACE FUNCTION generate_work_order_number()
RETURNS TRIGGER AS $$
DECLARE
    date_part TEXT;
    sequence_num INTEGER;
BEGIN
    date_part := TO_CHAR(NOW(), 'YYYYMMDD');
    SELECT COUNT(*) + 1 INTO sequence_num
    FROM work_orders
    WHERE work_order_number LIKE 'WO-' || date_part || '%';
    
    NEW.work_order_number := 'WO-' || date_part || '-' || LPAD(sequence_num::TEXT, 4, '0');
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Trigger: check_stock_level

**Descripción**: Genera alerta cuando el stock cae por debajo del mínimo.

**Función**:
```sql
CREATE OR REPLACE FUNCTION check_stock_level()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity < NEW.minimum_stock THEN
        INSERT INTO alerts (alert_type, severity, title, message)
        VALUES (
            'LOW_STOCK',
            'WARNING',
            'Stock Bajo: ' || NEW.name,
            'El repuesto ' || NEW.name || ' tiene stock bajo (' || NEW.quantity || ' unidades)'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## Vistas

### Vista: active_work_orders

**Descripción**: Muestra órdenes de trabajo activas con información relacionada.

```sql
CREATE VIEW active_work_orders AS
SELECT 
    wo.id,
    wo.work_order_number,
    wo.title,
    wo.status,
    wo.priority,
    a.name AS asset_name,
    a.vehicle_type,
    u_assigned.first_name || ' ' || u_assigned.last_name AS assigned_to_name,
    u_created.first_name || ' ' || u_created.last_name AS created_by_name,
    wo.scheduled_date,
    wo.created_at
FROM work_orders wo
JOIN assets a ON wo.asset_id = a.id
LEFT JOIN users u_assigned ON wo.assigned_to = u_assigned.id
JOIN users u_created ON wo.created_by = u_created.id
WHERE wo.status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS');
```

### Vista: asset_availability

**Descripción**: Calcula la disponibilidad de cada activo.

```sql
CREATE VIEW asset_availability AS
SELECT 
    a.id,
    a.name,
    a.vehicle_type,
    a.status,
    COUNT(wo.id) AS total_work_orders,
    SUM(CASE WHEN wo.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_work_orders,
    AVG(CASE WHEN wo.status = 'COMPLETED' THEN wo.actual_hours ELSE NULL END) AS avg_repair_time
FROM assets a
LEFT JOIN work_orders wo ON a.id = wo.asset_id
GROUP BY a.id, a.name, a.vehicle_type, a.status;
```

---

## Índices de Rendimiento

### Índices Compuestos

```sql
-- Para búsquedas de órdenes por activo y estado
CREATE INDEX idx_work_orders_asset_status ON work_orders(asset_id, status);

-- Para búsquedas de notificaciones no leídas por usuario
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- Para búsquedas de alertas no resueltas
CREATE INDEX idx_alerts_unresolved ON alerts(is_resolved, severity) WHERE is_resolved = FALSE;

-- Para búsquedas de checklists por activo y fecha
CREATE INDEX idx_checklist_responses_asset_date ON checklist_responses(asset_id, completed_at);
```

---

## Políticas de Retención

| Tabla | Política | Período |
|-------|----------|---------|
| audit_logs | Archivar | 1 año |
| notifications | Eliminar leídas | 90 días |
| alerts | Archivar resueltas | 6 meses |
| work_orders | Mantener | Indefinido |
| checklist_responses | Mantener | Indefinido |
| failure_predictions | Mantener | Indefinido |

---

**Diccionario de Datos Completo**  
**Versión**: 1.0  
**Fecha**: 18 de Noviembre de 2025  
**Total de Tablas**: 15  
**Total de Campos**: 180+

