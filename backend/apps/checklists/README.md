# Checklist API Endpoints

## Overview
Sistema de checklists con 5 plantillas predefinidas para diferentes tipos de vehículos.

## Endpoints

### Templates

#### List Templates
```
GET /api/v1/checklists/templates/
```
Lista todas las plantillas de checklist (solo lectura para plantillas del sistema).

**Query Parameters:**
- `vehicle_type`: Filtrar por tipo de vehículo
- `is_system_template`: Filtrar plantillas del sistema
- `search`: Buscar por código o nombre

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "code": "SUPERSUCKER-CH01",
      "name": "Check List Camión Supersucker",
      "vehicle_type": "CAMION_SUPERSUCKER",
      "vehicle_type_display": "Camión Supersucker",
      "description": "Checklist de inspección diaria...",
      "items": [...],
      "is_system_template": true,
      "passing_score": 80,
      "item_count": 5,
      "response_count": 10
    }
  ]
}
```

#### Get Template by ID
```
GET /api/v1/checklists/templates/{id}/
```

#### Get Templates by Vehicle Type
```
GET /api/v1/checklists/templates/by_vehicle_type/?vehicle_type=CAMION_SUPERSUCKER
```

### Responses

#### List Checklist Responses
```
GET /api/v1/checklists/responses/
```
Lista todos los checklists completados (filtrado por permisos de usuario).

**Query Parameters:**
- `template`: Filtrar por plantilla
- `asset`: Filtrar por activo
- `work_order`: Filtrar por orden de trabajo
- `passed`: Filtrar por estado (true/false)
- `completed_by`: Filtrar por usuario
- `search`: Buscar por nombre de operador
- `ordering`: Ordenar por campos (completed_at, score)

#### Create Checklist Response
```
POST /api/v1/checklists/responses/
```

**Request Body:**
```json
{
  "template": "uuid",
  "asset": "uuid",
  "work_order": "uuid",  // opcional
  "responses": [
    {
      "item_order": 1,
      "response": "yes",  // yes, no, na
      "notes": "Nivel normal",
      "photo_url": "gs://bucket/photo.jpg"  // opcional
    }
  ],
  "operator_name": "Juan Pérez",
  "shift": "Mañana",
  "odometer_reading": 12500,
  "signature_url": "gs://bucket/signature.jpg"  // opcional
}
```

**Response:**
```json
{
  "id": "uuid",
  "template": "uuid",
  "template_code": "SUPERSUCKER-CH01",
  "template_name": "Check List Camión Supersucker",
  "asset": "uuid",
  "asset_name": "Camión 001",
  "asset_code": "CS-001",
  "work_order": "uuid",
  "work_order_number": "WO-2025-001",
  "responses": [...],
  "score": 85,
  "passed": true,
  "pdf_url": "gs://bucket/checklist_xxx.pdf",
  "signature_url": "gs://bucket/signature.jpg",
  "completed_by": "uuid",
  "completed_by_name": "Juan Pérez",
  "completed_at": "2025-11-13T10:30:00Z",
  "operator_name": "Juan Pérez",
  "shift": "Mañana",
  "odometer_reading": 12500
}
```

#### Complete Checklist (Alternative Endpoint)
```
POST /api/v1/checklists/responses/complete/
```
Endpoint alternativo con validación adicional de vehicle_type.

#### Get Checklist PDF
```
GET /api/v1/checklists/responses/{id}/pdf/
```
Retorna una URL firmada para descargar el PDF del checklist.

**Response:**
```json
{
  "pdf_url": "https://storage.googleapis.com/bucket/checklist_xxx.pdf?signature=..."
}
```

#### Get Checklists by Asset
```
GET /api/v1/checklists/responses/by_asset/?asset_id=uuid
```

#### Get Checklist Statistics
```
GET /api/v1/checklists/responses/statistics/
```

**Response:**
```json
{
  "total": 50,
  "passed": 42,
  "failed": 8,
  "average_score": 87.5,
  "by_template": {
    "SUPERSUCKER-CH01": {
      "name": "Check List Camión Supersucker",
      "count": 10,
      "passed": 8,
      "failed": 2
    }
  }
}
```

## Features

### Vehicle Type Validation
El sistema valida automáticamente que el tipo de vehículo del activo coincida con el tipo de vehículo de la plantilla.

### Automatic Scoring
El puntaje se calcula automáticamente basado en las respuestas "yes" vs total de items.

### PDF Generation
Al completar un checklist, se genera automáticamente un PDF con formato profesional que incluye:
- Información del activo y operador
- Tabla de items agrupados por sección
- Puntaje y estado (aprobado/no aprobado)
- Firma digital

### Cloud Storage Integration
Los PDFs generados se suben automáticamente a Google Cloud Storage y se retornan URLs firmadas para acceso seguro.

### System Template Protection
Las plantillas del sistema (is_system_template=true) son de solo lectura y no pueden ser modificadas o eliminadas.

## Validation Rules

1. **Vehicle Type Match**: El vehicle_type del asset debe coincidir con el vehicle_type de la template
2. **Response Count**: El número de respuestas debe coincidir con el número de items en la plantilla
3. **Response Values**: Solo se aceptan valores: "yes", "no", "na"
4. **Required Fields**: item_order y response son obligatorios en cada respuesta
5. **Passing Score**: El checklist se marca como "passed" si score >= template.passing_score

## Permissions

- **ADMIN/SUPERVISOR**: Pueden ver todos los checklists
- **OPERADOR**: Solo pueden ver sus propios checklists completados
- **Templates**: Todos los usuarios autenticados pueden ver las plantillas (read-only)
