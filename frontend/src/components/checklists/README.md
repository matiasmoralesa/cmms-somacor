# Checklist Components

## Overview
Componentes React para el sistema de checklists con interfaz optimizada para móvil.

## Components

### ChecklistTemplateViewer
Visualiza plantillas de checklist predefinidas.

**Props:**
- `templateId?: string` - ID de plantilla específica a mostrar
- `vehicleType?: string` - Filtrar plantillas por tipo de vehículo
- `onSelectTemplate?: (template: ChecklistTemplate) => void` - Callback al seleccionar plantilla

**Features:**
- Lista de plantillas del sistema
- Selector de plantillas
- Vista detallada de items agrupados por sección
- Información de puntaje mínimo y estadísticas

**Usage:**
```tsx
<ChecklistTemplateViewer
  vehicleType="CAMION_SUPERSUCKER"
  onSelectTemplate={(template) => console.log(template)}
/>
```

### ChecklistExecutor
Interfaz optimizada para móvil para completar checklists.

**Props:**
- `template: ChecklistTemplate` - Plantilla a ejecutar (requerido)
- `assetId: string` - ID del activo (requerido)
- `assetName: string` - Nombre del activo (requerido)
- `workOrderId?: string` - ID de orden de trabajo (opcional)
- `onComplete?: (responseId: string) => void` - Callback al completar
- `onCancel?: () => void` - Callback al cancelar

**Features:**
- Navegación paso a paso por items
- Barra de progreso visual
- Botones grandes para respuestas (Sí/No/N/A)
- Campo de observaciones por item
- Captura de información del operador
- Vista de resumen con puntaje estimado
- Interfaz responsive y touch-friendly

**Usage:**
```tsx
<ChecklistExecutor
  template={template}
  assetId="asset-123"
  assetName="Camión 001"
  workOrderId="wo-456"
  onComplete={(id) => console.log('Completed:', id)}
  onCancel={() => console.log('Cancelled')}
/>
```

### ChecklistViewer
Visualiza checklists completados con opción de descarga de PDF.

**Props:**
- `checklistId: string` - ID del checklist a mostrar (requerido)
- `onClose?: () => void` - Callback al cerrar

**Features:**
- Vista completa de checklist completado
- Información del activo y operador
- Puntaje y estado (aprobado/no aprobado)
- Lista de respuestas con iconos visuales
- Botón de descarga de PDF
- Diseño responsive

**Usage:**
```tsx
<ChecklistViewer
  checklistId="checklist-789"
  onClose={() => console.log('Closed')}
/>
```

## Page

### Checklists
Página principal que integra todos los componentes.

**Features:**
- Lista de checklists completados
- Filtros por estado y búsqueda
- Botón para crear nuevo checklist
- Navegación entre vistas (lista/plantillas/ejecutar/ver)
- Cards con información resumida
- Descarga directa de PDFs

**View Modes:**
- `list` - Lista de checklists completados
- `templates` - Selector de plantillas
- `execute` - Ejecutar checklist
- `view` - Ver checklist completado

## Services

### checklistService
Servicio para interactuar con la API de checklists.

**Methods:**
- `getTemplates(params?)` - Obtener plantillas
- `getTemplate(id)` - Obtener plantilla por ID
- `getTemplatesByVehicleType(vehicleType)` - Filtrar por tipo de vehículo
- `getResponses(params?)` - Obtener checklists completados
- `getResponse(id)` - Obtener checklist por ID
- `createResponse(data)` - Crear checklist
- `completeChecklist(data)` - Completar checklist con validación
- `getResponsePdf(id)` - Obtener URL del PDF
- `getResponsesByAsset(assetId)` - Filtrar por activo
- `getStatistics(params?)` - Obtener estadísticas
- `downloadPdf(pdfUrl)` - Descargar PDF

## Types

### ChecklistTemplate
```typescript
{
  id: string;
  code: string;
  name: string;
  vehicle_type: string;
  vehicle_type_display: string;
  description: string;
  items: ChecklistItem[];
  is_system_template: boolean;
  passing_score: number;
  item_count: number;
  response_count: number;
  created_at: string;
  updated_at: string;
}
```

### ChecklistResponse
```typescript
{
  id: string;
  template: string;
  template_code: string;
  template_name: string;
  asset: string;
  asset_name: string;
  asset_code: string;
  work_order?: string;
  work_order_number?: string;
  responses: ChecklistResponseItem[];
  score: number;
  passed: boolean;
  pdf_url?: string;
  signature_url?: string;
  completed_by: string;
  completed_by_name: string;
  completed_at: string;
  operator_name: string;
  shift?: string;
  odometer_reading?: number;
}
```

### ChecklistResponseItem
```typescript
{
  item_order: number;
  response: 'yes' | 'no' | 'na';
  notes?: string;
  photo_url?: string;
}
```

## Mobile Optimization

Los componentes están optimizados para uso móvil:

- **Touch-friendly**: Botones grandes y espaciados
- **Responsive**: Adaptación automática a diferentes tamaños de pantalla
- **Progressive**: Navegación paso a paso para mejor UX en móvil
- **Visual feedback**: Animaciones y estados visuales claros
- **Offline-ready**: Preparado para funcionalidad offline (futuro)

## Styling

Los componentes usan Tailwind CSS para estilos:
- Paleta de colores consistente
- Espaciado uniforme
- Sombras y bordes sutiles
- Estados hover y focus
- Animaciones suaves

## Future Enhancements

- [ ] Captura de fotos para items
- [ ] Firma digital con canvas
- [ ] Modo offline con sincronización
- [ ] Geolocalización automática
- [ ] Notificaciones push
- [ ] Escaneo de códigos QR para activos
