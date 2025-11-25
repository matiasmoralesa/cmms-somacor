# API Endpoints de Checklists

## Base URL
```
https://cmms-backend-232652686658.us-central1.run.app/api/v1/checklists/
```

## Autenticación
Todos los endpoints requieren autenticación mediante JWT token en el header:
```
Authorization: Bearer <token>
```

## Endpoints Disponibles

### 1. Plantillas de Checklist

#### Listar todas las plantillas
```http
GET /templates/
```

**Respuesta:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "code": "F-PR-020-CH01",
      "name": "Check List Camionetas MDO",
      "vehicle_type": "CAMIONETA_MDO",
      "vehicle_type_display": "Camioneta MDO",
      "description": "Checklist diario para Camionetas MDO",
      "items": [...],
      "is_system_template": true,
      "passing_score": 80,
      "item_count": 23,
      "response_count": 0,
      "created_at": "2024-11-17T...",
      "updated_at": "2024-11-17T..."
    }
  ]
}
```

#### Obtener una plantilla específica
```http
GET /templates/{id}/
```

#### Filtrar plantillas por tipo de vehículo
```http
GET /templates/?vehicle_type=CAMIONETA_MDO
```

Tipos de vehículo disponibles:
- `CAMIONETA_MDO`
- `CAMION_SUPERSUCKER`
- `RETROEXCAVADORA`
- `CARGADOR_FRONTAL`
- `MINICARGADOR`

#### Buscar plantillas
```http
GET /templates/?search=camioneta
```

#### Plantillas por tipo de vehículo (endpoint personalizado)
```http
GET /templates/by_vehicle_type/?vehicle_type=CAMIONETA_MDO
```

---

### 2. Respuestas de Checklist (Checklists Completados)

#### Listar todos los checklists completados
```http
GET /responses/
```

**Respuesta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "template": "template-uuid",
      "template_code": "F-PR-020-CH01",
      "template_name": "Check List Camionetas MDO",
      "work_order": "wo-uuid",
      "work_order_number": "WO-2024-001",
      "asset": "asset-uuid",
      "asset_name": "Camioneta 01",
      "asset_code": "CAM-001",
      "responses": [...],
      "score": 95,
      "passed": true,
      "pdf_url": "gs://bucket/checklists/...",
      "signature_url": "gs://bucket/signatures/...",
      "completed_by": "user-uuid",
      "completed_by_name": "Juan Pérez",
      "completed_at": "2024-11-17T...",
      "operator_name": "Juan Pérez",
      "shift": "Mañana",
      "odometer_reading": 12500
    }
  ]
}
```

#### Crear un nuevo checklist completado
```http
POST /responses/
```

**Body:**
```json
{
  "template": "template-uuid",
  "asset": "asset-uuid",
  "work_order": "wo-uuid",  // opcional
  "operator_name": "Juan Pérez",
  "shift": "Mañana",
  "odometer_reading": 12500,
  "signature_url": "gs://bucket/signatures/...",  // opcional
  "responses": [
    {
      "item_order": 1,
      "response": "yes",
      "notes": "Todo en orden",
      "photo_url": "gs://bucket/photos/..."  // opcional
    },
    {
      "item_order": 2,
      "response": "no",
      "notes": "Requiere mantenimiento"
    }
  ]
}
```

**Validaciones:**
- El `vehicle_type` del asset debe coincidir con el de la plantilla
- El número de respuestas debe coincidir con el número de items en la plantilla
- Cada respuesta debe tener `item_order` y `response`
- Los valores válidos para `response` son: `"yes"`, `"no"`, `"na"`

#### Completar un checklist (endpoint alternativo)
```http
POST /responses/complete/
```
Mismo body que el endpoint anterior, con validaciones adicionales.

#### Obtener un checklist específico
```http
GET /responses/{id}/
```

#### Filtrar checklists
```http
GET /responses/?template={template-id}
GET /responses/?asset={asset-id}
GET /responses/?work_order={wo-id}
GET /responses/?passed=true
GET /responses/?completed_by={user-id}
```

#### Buscar por nombre de operador
```http
GET /responses/?search=Juan
```

#### Ordenar resultados
```http
GET /responses/?ordering=-completed_at  // más recientes primero
GET /responses/?ordering=score  // menor a mayor puntaje
GET /responses/?ordering=-score  // mayor a menor puntaje
```

#### Checklists por activo
```http
GET /responses/by_asset/?asset_id={asset-uuid}
```

#### Obtener PDF de un checklist
```http
GET /responses/{id}/pdf/
```

**Respuesta:**
```json
{
  "pdf_url": "https://storage.googleapis.com/..."
}
```

#### Regenerar PDF de un checklist
```http
POST /responses/{id}/regenerate_pdf/
```

Útil cuando la generación automática falló o LibreOffice no estaba disponible.

#### Estadísticas de checklists
```http
GET /responses/statistics/
```

**Respuesta:**
```json
{
  "total": 100,
  "passed": 85,
  "failed": 15,
  "average_score": 87.5,
  "by_template": {
    "F-PR-020-CH01": {
      "name": "Check List Camionetas MDO",
      "count": 30,
      "passed": 28,
      "failed": 2
    },
    "CH-SUPERSUCKER-01": {
      "name": "Check List Camión Supersucker",
      "count": 25,
      "passed": 22,
      "failed": 3
    }
  }
}
```

---

## Permisos

### Roles y Acceso

**ADMIN y SUPERVISOR:**
- Ver todas las plantillas
- Ver todos los checklists completados
- Crear nuevos checklists
- Ver estadísticas completas

**OPERADOR:**
- Ver todas las plantillas
- Ver solo sus propios checklists completados
- Crear nuevos checklists
- Ver estadísticas de sus propios checklists

---

## Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Error en los datos enviados
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

---

## Ejemplos de Uso

### Ejemplo 1: Obtener plantillas para un tipo de vehículo

```bash
curl -X GET \
  "https://cmms-backend-232652686658.us-central1.run.app/api/v1/checklists/templates/?vehicle_type=CAMIONETA_MDO" \
  -H "Authorization: Bearer <token>"
```

### Ejemplo 2: Completar un checklist

```bash
curl -X POST \
  "https://cmms-backend-232652686658.us-central1.run.app/api/v1/checklists/responses/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "template-uuid",
    "asset": "asset-uuid",
    "operator_name": "Juan Pérez",
    "shift": "Mañana",
    "odometer_reading": 12500,
    "responses": [
      {"item_order": 1, "response": "yes"},
      {"item_order": 2, "response": "yes"},
      {"item_order": 3, "response": "no", "notes": "Requiere revisión"}
    ]
  }'
```

### Ejemplo 3: Ver estadísticas

```bash
curl -X GET \
  "https://cmms-backend-232652686658.us-central1.run.app/api/v1/checklists/responses/statistics/" \
  -H "Authorization: Bearer <token>"
```

---

## Estructura de Items en Plantilla

Cada item en una plantilla tiene la siguiente estructura:

```json
{
  "section": "I - Auto Evaluación",
  "order": 1,
  "question": "Cumplo con descanso suficiente y condiciones para manejo seguro",
  "response_type": "yes_no_na",
  "required": true,
  "observations_allowed": true
}
```

## Estructura de Respuestas

Cada respuesta en un checklist completado tiene:

```json
{
  "item_order": 1,
  "response": "yes",  // "yes", "no", o "na"
  "notes": "Observaciones opcionales",
  "photo_url": "gs://bucket/photos/..."  // opcional
}
```

---

## Notas Importantes

1. **Generación de PDF**: Los PDFs se generan automáticamente al crear un checklist. Si falla, se puede regenerar manualmente.

2. **Validación de Vehículos**: El sistema valida que el tipo de vehículo del activo coincida con el de la plantilla.

3. **Cálculo de Puntaje**: El puntaje se calcula automáticamente basado en las respuestas "yes" vs total de items.

4. **Plantillas del Sistema**: Las plantillas marcadas como `is_system_template=true` están protegidas contra eliminación.

5. **Paginación**: Todos los endpoints de listado soportan paginación automática.
