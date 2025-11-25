# Rutas API Completas - Sistema CMMS

## 📋 Resumen de Endpoints

**Total de Endpoints:** 60+  
**Versión API:** v1  
**Base URL:** `/api/v1/`

---

## 🔐 Autenticación (`/api/v1/auth/`)

### Autenticación
- `POST /api/v1/auth/login/` - Iniciar sesión
- `POST /api/v1/auth/logout/` - Cerrar sesión
- `POST /api/v1/auth/refresh/` - Refrescar token
- `POST /api/v1/auth/password-reset/` - Solicitar reset de contraseña
- `POST /api/v1/auth/password-reset-confirm/` - Confirmar reset de contraseña

### Perfil de Usuario
- `GET /api/v1/auth/profile/` - Ver perfil
- `PUT /api/v1/auth/profile/` - Actualizar perfil
- `POST /api/v1/auth/change-password/` - Cambiar contraseña

### Gestión de Usuarios (Admin)
- `GET /api/v1/auth/users/` - Listar usuarios
- `POST /api/v1/auth/users/` - Crear usuario
- `GET /api/v1/auth/users/{id}/` - Ver usuario
- `PUT /api/v1/auth/users/{id}/` - Actualizar usuario
- `DELETE /api/v1/auth/users/{id}/` - Eliminar usuario

### Roles
- `GET /api/v1/auth/roles/` - Listar roles

---

## 🚗 Activos (`/api/v1/assets/`)

### CRUD de Activos
- `GET /api/v1/assets/` - Listar activos
- `POST /api/v1/assets/` - Crear activo
- `GET /api/v1/assets/{id}/` - Ver activo
- `PUT /api/v1/assets/{id}/` - Actualizar activo
- `PATCH /api/v1/assets/{id}/` - Actualizar parcial
- `DELETE /api/v1/assets/{id}/` - Eliminar activo

### Documentos
- `GET /api/v1/assets/{id}/documents/` - Listar documentos del activo
- `POST /api/v1/assets/{id}/upload-document/` - Subir documento
- `GET /api/v1/assets/documents/{id}/` - Ver documento
- `DELETE /api/v1/assets/documents/{id}/` - Eliminar documento

### Categorías y Ubicaciones
- `GET /api/v1/assets/categories/` - Listar categorías
- `POST /api/v1/assets/categories/` - Crear categoría
- `GET /api/v1/assets/locations/` - Listar ubicaciones
- `POST /api/v1/assets/locations/` - Crear ubicación

---

## 🔧 Órdenes de Trabajo (`/api/v1/work-orders/`)

### CRUD de Órdenes
- `GET /api/v1/work-orders/` - Listar órdenes
- `POST /api/v1/work-orders/` - Crear orden
- `GET /api/v1/work-orders/{id}/` - Ver orden
- `PUT /api/v1/work-orders/{id}/` - Actualizar orden
- `PATCH /api/v1/work-orders/{id}/` - Actualizar parcial
- `DELETE /api/v1/work-orders/{id}/` - Eliminar orden

### Acciones Especiales
- `GET /api/v1/work-orders/my-assignments/` - Mis asignaciones
- `PATCH /api/v1/work-orders/{id}/status/` - Cambiar estado
- `POST /api/v1/work-orders/{id}/complete/` - Completar orden
- `POST /api/v1/work-orders/{id}/assign/` - Asignar orden

---

## 📅 Mantenimiento (`/api/v1/maintenance/`)

### Planes de Mantenimiento
- `GET /api/v1/maintenance/plans/` - Listar planes
- `POST /api/v1/maintenance/plans/` - Crear plan
- `GET /api/v1/maintenance/plans/{id}/` - Ver plan
- `PUT /api/v1/maintenance/plans/{id}/` - Actualizar plan
- `DELETE /api/v1/maintenance/plans/{id}/` - Eliminar plan

### Acciones de Planes
- `PATCH /api/v1/maintenance/plans/{id}/pause/` - Pausar plan
- `PATCH /api/v1/maintenance/plans/{id}/resume/` - Reanudar plan

### Calendario
- `GET /api/v1/maintenance/calendar/` - Ver calendario de mantenimiento

---

## 📦 Inventario (`/api/v1/inventory/`)

### Repuestos
- `GET /api/v1/inventory/spare-parts/` - Listar repuestos
- `POST /api/v1/inventory/spare-parts/` - Crear repuesto
- `GET /api/v1/inventory/spare-parts/{id}/` - Ver repuesto
- `PUT /api/v1/inventory/spare-parts/{id}/` - Actualizar repuesto
- `DELETE /api/v1/inventory/spare-parts/{id}/` - Eliminar repuesto

### Gestión de Stock
- `POST /api/v1/inventory/spare-parts/{id}/adjust-stock/` - Ajustar stock
- `GET /api/v1/inventory/spare-parts/low-stock/` - Alertas de stock bajo

### Movimientos
- `GET /api/v1/inventory/stock-movements/` - Listar movimientos
- `GET /api/v1/inventory/stock-movements/{id}/` - Ver movimiento

---

## ✅ Checklists (`/api/v1/checklists/`)

### Plantillas
- `GET /api/v1/checklists/templates/` - Listar plantillas
- `POST /api/v1/checklists/templates/` - Crear plantilla
- `GET /api/v1/checklists/templates/{id}/` - Ver plantilla
- `PUT /api/v1/checklists/templates/{id}/` - Actualizar plantilla
- `DELETE /api/v1/checklists/templates/{id}/` - Eliminar plantilla
- `GET /api/v1/checklists/templates/by-vehicle-type/{type}/` - Por tipo de vehículo

### Respuestas
- `GET /api/v1/checklists/responses/` - Listar respuestas
- `POST /api/v1/checklists/responses/` - Crear respuesta
- `GET /api/v1/checklists/responses/{id}/` - Ver respuesta
- `GET /api/v1/checklists/responses/{id}/pdf/` - Generar PDF

---

## 🤖 Predicciones (`/api/v1/predictions/`)

### Predicciones de Fallas
- `GET /api/v1/predictions/` - Listar predicciones
- `POST /api/v1/predictions/predict/` - Generar predicción
- `GET /api/v1/predictions/{id}/` - Ver predicción
- `GET /api/v1/predictions/asset/{asset_id}/health-score/` - Score de salud

### Alertas
- `GET /api/v1/predictions/alerts/` - Listar alertas
- `GET /api/v1/predictions/alerts/{id}/` - Ver alerta
- `PATCH /api/v1/predictions/alerts/{id}/resolve/` - Resolver alerta

---

## 🔔 Notificaciones (`/api/v1/notifications/`)

### Notificaciones
- `GET /api/v1/notifications/` - Listar notificaciones
- `GET /api/v1/notifications/{id}/` - Ver notificación
- `PATCH /api/v1/notifications/{id}/mark-read/` - Marcar como leída
- `POST /api/v1/notifications/mark-all-read/` - Marcar todas como leídas

### Preferencias
- `GET /api/v1/notifications/preferences/` - Listar preferencias
- `POST /api/v1/notifications/preferences/` - Crear preferencia
- `GET /api/v1/notifications/preferences/{id}/` - Ver preferencia
- `PUT /api/v1/notifications/preferences/{id}/` - Actualizar preferencia

---

## 📊 Reportes (`/api/v1/reports/`)

### KPIs
- `GET /api/v1/reports/kpis/` - KPIs generales (MTBF, MTTR, OEE)
- `GET /api/v1/reports/work-orders-summary/` - Resumen de órdenes
- `GET /api/v1/reports/asset-downtime/` - Downtime de activos
- `GET /api/v1/reports/spare-parts-consumption/` - Consumo de repuestos

### Reportes Personalizados
- `POST /api/v1/reports/generate/` - Generar reporte
- `GET /api/v1/reports/{id}/download/` - Descargar reporte

### Reportes Programados
- `GET /api/v1/reports/scheduled/` - Listar reportes programados
- `POST /api/v1/reports/scheduled/` - Crear reporte programado
- `GET /api/v1/reports/scheduled/{id}/` - Ver reporte programado
- `PUT /api/v1/reports/scheduled/{id}/` - Actualizar reporte programado

---

## ⚙️ Configuración (`/api/v1/config/`)

### Datos Maestros
- `GET /api/v1/config/priorities/` - Listar prioridades
- `POST /api/v1/config/priorities/` - Crear prioridad
- `GET /api/v1/config/work-order-types/` - Listar tipos de OT
- `POST /api/v1/config/work-order-types/` - Crear tipo de OT

### Parámetros del Sistema
- `GET /api/v1/config/system-parameters/` - Listar parámetros
- `PUT /api/v1/config/system-parameters/{id}/` - Actualizar parámetro

### Auditoría
- `GET /api/v1/config/audit-logs/` - Ver logs de auditoría

---

## 🏥 Core (`/api/v1/core/`)

### Health Checks
- `GET /api/v1/core/health/` - Health check completo
- `GET /api/v1/core/health/live/` - Liveness probe
- `GET /api/v1/core/health/ready/` - Readiness probe

### Webhooks
- `GET /api/v1/core/webhooks/` - Listar webhooks
- `POST /api/v1/core/webhooks/` - Crear webhook
- `GET /api/v1/core/webhooks/{id}/` - Ver webhook
- `PUT /api/v1/core/webhooks/{id}/` - Actualizar webhook
- `DELETE /api/v1/core/webhooks/{id}/` - Eliminar webhook

---

## 📖 Documentación

### OpenAPI/Swagger
- `GET /api/schema/` - Schema OpenAPI (JSON)
- `GET /api/docs/` - Swagger UI (Interfaz interactiva)
- `GET /api/redoc/` - ReDoc (Documentación legible)

---

## 🔒 Autenticación y Permisos

### Headers Requeridos
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Roles y Permisos

#### ADMIN
- ✅ Acceso completo a todos los endpoints
- ✅ Gestión de usuarios
- ✅ Configuración del sistema
- ✅ Logs de auditoría

#### SUPERVISOR
- ✅ Gestión de órdenes de trabajo
- ✅ Gestión de planes de mantenimiento
- ✅ Gestión de inventario
- ✅ Ver predicciones y alertas
- ✅ Generar reportes
- ❌ Gestión de usuarios
- ❌ Configuración del sistema

#### OPERADOR
- ✅ Ver órdenes asignadas
- ✅ Completar órdenes asignadas
- ✅ Ejecutar checklists
- ✅ Ver inventario (solo lectura)
- ❌ Crear órdenes de trabajo
- ❌ Asignar órdenes
- ❌ Ver predicciones
- ❌ Generar reportes

---

## 📝 Parámetros Comunes

### Paginación
```
?page=1
?page_size=20
```

### Filtrado
```
?search=texto
?status=PENDING
?priority=HIGH
?vehicle_type=CAMION_SUPERSUCKER
?assigned_to={user_id}
?created_at__gte=2024-01-01
?created_at__lte=2024-12-31
```

### Ordenamiento
```
?ordering=created_at
?ordering=-created_at  (descendente)
?ordering=priority,-created_at  (múltiple)
```

---

## 🔄 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado |
| 204 | No Content - Eliminación exitosa |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (duplicado) |
| 429 | Too Many Requests - Rate limit |
| 500 | Internal Server Error - Error del servidor |

---

## 📊 Ejemplos de Uso

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@somacor.com",
    "password": "Demo2024!"
  }'
```

### Listar Activos
```bash
curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer {token}"
```

### Crear Orden de Trabajo
```bash
curl -X POST http://localhost:8000/api/v1/work-orders/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mantenimiento preventivo",
    "description": "Revisión general",
    "asset": "{asset_id}",
    "work_order_type": "PREVENTIVE",
    "priority": "MEDIUM",
    "assigned_to": "{user_id}"
  }'
```

### Completar Checklist
```bash
curl -X POST http://localhost:8000/api/v1/checklists/responses/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "{template_id}",
    "asset": "{asset_id}",
    "work_order": "{work_order_id}",
    "responses": [
      {
        "item_order": 1,
        "response": "yes",
        "notes": "OK"
      }
    ]
  }'
```

---

## 🔍 Rate Limiting

- **Usuarios autenticados:** 100 requests/minuto
- **Usuarios anónimos:** 20 requests/minuto

Headers de respuesta:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876543
```

---

## 📚 Documentación Adicional

- **API Documentation:** `/api/docs/`
- **ReDoc:** `/api/redoc/`
- **OpenAPI Schema:** `/api/schema/`
- **Guía de Usuario:** `USER_GUIDE.md`
- **Guía de Admin:** `ADMIN_GUIDE.md`

---

**Versión:** 1.0.0  
**Última Actualización:** 2024-11-13  
**Total de Endpoints:** 60+
