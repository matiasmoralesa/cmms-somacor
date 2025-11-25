# Documentación de la API CMMS

## Descripción General

La API CMMS (Sistema de Gestión de Mantenimiento Computarizado) proporciona endpoints REST completos para gestionar activos, órdenes de trabajo, mantenimiento preventivo y predictivo, inventario, y más.

## Versión

**Versión actual:** 1.0.0

## URL Base

- **Desarrollo:** `http://localhost:8000/api/v1`
- **Producción:** `https://your-domain.com/api/v1`

## Documentación Interactiva

La API cuenta con documentación interactiva disponible en:

- **Swagger UI:** `/api/docs/` - Interfaz interactiva para probar endpoints
- **ReDoc:** `/api/redoc/` - Documentación detallada y legible
- **Schema OpenAPI:** `/api/schema/` - Esquema OpenAPI 3.0 en formato JSON

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para acceder a endpoints protegidos:

### 1. Obtener Tokens

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@cmms.com",
  "password": "tu_contraseña"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "usuario@cmms.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "ADMIN",
    "role_name": "Administrador"
  }
}
```

### 2. Usar el Token de Acceso

Incluye el token de acceso en el header `Authorization` de todas las peticiones:

```http
GET /api/v1/assets/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. Refrescar el Token

Los tokens de acceso expiran en 15 minutos. Usa el refresh token para obtener uno nuevo:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Roles y Permisos

El sistema cuenta con 3 roles principales:

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **ADMIN** | Administrador del sistema | Acceso completo a todos los módulos y configuración |
| **SUPERVISOR** | Supervisor de mantenimiento | Gestión de OT, activos, planes de mantenimiento, reportes |
| **OPERADOR** | Técnico/Operador | Ver y completar OT asignadas, ejecutar checklists |

## Módulos Principales

### 1. Autenticación (`/auth/`)
- Login, logout, refresh token
- Gestión de perfil de usuario
- Cambio de contraseña
- Recuperación de contraseña

### 2. Activos (`/assets/`)
- CRUD de activos y vehículos
- Gestión de documentos asociados
- Filtrado por tipo de vehículo
- Historial de mantenimiento

### 3. Órdenes de Trabajo (`/work-orders/`)
- Creación y asignación de OT
- Seguimiento de estado
- Completar OT con notas y horas
- Filtrado por estado, prioridad, usuario

### 4. Mantenimiento (`/maintenance/`)
- Planes de mantenimiento preventivo
- Programación recurrente
- Vinculación con predicciones ML
- Calendario de mantenimiento

### 5. Inventario (`/inventory/`)
- Gestión de repuestos
- Control de stock
- Alertas de stock bajo
- Historial de movimientos

### 6. Checklists (`/checklists/`)
- Plantillas predefinidas por tipo de vehículo
- Ejecución de checklists
- Generación de PDFs
- Carga de fotos

### 7. Predicciones (`/predictions/`)
- Predicciones de fallas con ML
- Alertas de alto riesgo
- Scores de salud de activos
- Recomendaciones

### 8. Notificaciones (`/notifications/`)
- Notificaciones en tiempo real
- Preferencias de notificación
- Integración con Telegram
- Cola offline

### 9. Reportes (`/reports/`)
- KPIs (MTBF, MTTR, OEE)
- Reportes de OT
- Downtime de activos
- Consumo de repuestos
- Exportación CSV

### 10. Configuración (`/config/`)
- Datos maestros (categorías, ubicaciones, prioridades)
- Tipos de OT
- Parámetros del sistema
- Registro de auditoría

## Paginación

Los endpoints que retornan listas utilizan paginación:

```json
{
  "count": 100,
  "next": "http://api.example.com/api/v1/assets/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parámetros de paginación:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20, max: 100)

## Filtrado y Búsqueda

La mayoría de endpoints soportan filtrado y búsqueda:

```http
GET /api/v1/assets/?search=camion&vehicle_type=CAMION_SUPERSUCKER&is_active=true
```

**Parámetros comunes:**
- `search`: Búsqueda de texto
- `ordering`: Ordenamiento (ej: `-created_at` para descendente)
- Filtros específicos por modelo

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Eliminación exitosa |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (ej: duplicado) |
| 429 | Too Many Requests - Límite de tasa excedido |
| 500 | Internal Server Error - Error del servidor |

## Rate Limiting

La API implementa límites de tasa para prevenir abuso:

- **Usuarios autenticados:** 100 peticiones/minuto
- **Usuarios anónimos:** 20 peticiones/minuto

Los headers de respuesta incluyen información sobre el límite:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876543
```

## Versionado

La API utiliza versionado en la URL (`/api/v1/`). Las versiones futuras mantendrán compatibilidad hacia atrás cuando sea posible.

## Tipos de Vehículos

El sistema soporta 5 tipos de vehículos predefinidos:

1. `CAMION_SUPERSUCKER` - Camión Supersucker
2. `CAMIONETA_MDO` - Camioneta MDO
3. `RETROEXCAVADORA_MDO` - Retroexcavadora MDO
4. `CARGADOR_FRONTAL_MDO` - Cargador Frontal MDO
5. `MINICARGADOR_MDO` - Minicargador MDO

Cada tipo tiene su plantilla de checklist específica.

## Códigos de Checklist

| Tipo de Vehículo | Código de Checklist |
|------------------|---------------------|
| Camión Supersucker | SUPERSUCKER-CH01 |
| Camioneta MDO | F-PR-020-CH01 |
| Retroexcavadora MDO | F-PR-034-CH01 |
| Cargador Frontal MDO | F-PR-037-CH01 |
| Minicargador MDO | F-PR-040-CH01 |

## Ejemplos de Uso

### Crear una Orden de Trabajo

```http
POST /api/v1/work-orders/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Mantenimiento preventivo mensual",
  "description": "Revisión general del vehículo",
  "asset": "asset-uuid",
  "work_order_type": "PREVENTIVE",
  "priority": "MEDIUM",
  "assigned_to": "user-uuid",
  "scheduled_date": "2024-11-20T09:00:00Z"
}
```

### Completar un Checklist

```http
POST /api/v1/checklists/responses/
Authorization: Bearer {token}
Content-Type: application/json

{
  "template": "template-uuid",
  "asset": "asset-uuid",
  "work_order": "wo-uuid",
  "responses": [
    {
      "item_order": 1,
      "response": "yes",
      "notes": "Nivel de aceite correcto",
      "photo_url": "gs://bucket/photo.jpg"
    }
  ]
}
```

### Obtener KPIs

```http
GET /api/v1/reports/kpis/?start_date=2024-01-01&end_date=2024-11-13
Authorization: Bearer {token}
```

## Webhooks

El sistema puede enviar notificaciones a URLs externas cuando ocurren eventos importantes:

```http
POST /api/v1/webhooks/
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["work_order.created", "work_order.completed", "alert.created"],
  "is_active": true
}
```

## Soporte

Para soporte técnico o preguntas sobre la API:

- **Email:** soporte@cmms.com
- **Documentación:** `/api/docs/`
- **Issues:** GitHub Issues (si aplica)

## Changelog

### v1.0.0 (2024-11-13)
- Lanzamiento inicial
- Módulos completos de autenticación, activos, OT, mantenimiento
- Integración con ML para predicciones
- Sistema de notificaciones en tiempo real
- Bot de Telegram
- Reportes y KPIs
