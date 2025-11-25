# Vehicle Types and Checklist Templates

Este documento especifica los tipos de vehículos soportados por el sistema CMMS y sus plantillas de checklist asociadas.

## Vehicle Types

El sistema soporta exactamente **5 tipos de vehículos**:

### 1. Camión Supersucker
- **Código**: `CAMION_SUPERSUCKER`
- **Checklist Template**: Camión Supersucker Check List
- **Código de Checklist**: `SUPERSUCKER-CH01`
- **Archivo de Referencia**: `Check_List_camión supersucker.pdf`

### 2. Camioneta MDO
- **Código**: `CAMIONETA_MDO`
- **Checklist Template**: Check List Camionetas MDO
- **Código de Checklist**: `F-PR-020-CH01`
- **Archivo de Referencia**: `F-PR-020-CH01 Check List Camionetas MDO.pdf`

### 3. Retroexcavadora MDO
- **Código**: `RETROEXCAVADORA_MDO`
- **Checklist Template**: Check Retroexcavadora MDO
- **Código de Checklist**: `F-PR-034-CH01`
- **Archivo de Referencia**: `F-PR-034-CH01_Check Retroexcavadora MDO.pdf`

### 4. Cargador Frontal MDO
- **Código**: `CARGADOR_FRONTAL_MDO`
- **Checklist Template**: Check List Cargador Frontal MDO
- **Código de Checklist**: `F-PR-037-CH01`
- **Archivo de Referencia**: `F-PR-037-CH01 Check List Cargador Frontal MDO.pdf`

### 5. Minicargador MDO
- **Código**: `MINICARGADOR_MDO`
- **Checklist Template**: Check List Minicargador MDO
- **Código de Checklist**: `F-PR-040-CH01`
- **Archivo de Referencia**: `F-PR-040-CH01 Check List Minicargador MDO.pdf`

## Checklist Template Structure

Cada plantilla de checklist debe seguir esta estructura basada en los PDFs proporcionados:

### Common Fields
- **Código de Template**: Identificador único (ej. F-PR-020-CH01)
- **Nombre del Vehículo**: Tipo de vehículo
- **Fecha**: Fecha de inspección
- **Operador**: Usuario que realiza la inspección
- **Kilometraje/Horómetro**: Lectura actual
- **Turno**: Turno de trabajo

### Checklist Items Structure

Cada item del checklist debe incluir:

```json
{
  "section": "Motor / Transmisión / Hidráulico / etc.",
  "order": 1,
  "item": "Descripción del item a verificar",
  "response_type": "yes_no_na",
  "options": ["Sí", "No", "N/A"],
  "observations_field": true,
  "photo_allowed": true,
  "required": true
}
```

### Response Types

- **yes_no_na**: Respuesta Sí/No/N/A (No Aplica)
- **text**: Campo de texto libre para observaciones
- **numeric**: Valor numérico (ej. nivel de combustible, presión)
- **photo**: Captura de foto para evidencia

### Sections Típicas

Basado en los PDFs, las secciones comunes incluyen:

1. **Motor**
   - Nivel de aceite
   - Fugas
   - Ruidos anormales
   - Temperatura

2. **Transmisión**
   - Nivel de aceite
   - Funcionamiento de cambios
   - Fugas

3. **Sistema Hidráulico**
   - Nivel de aceite hidráulico
   - Fugas en mangueras
   - Funcionamiento de cilindros

4. **Frenos**
   - Funcionamiento de freno de servicio
   - Freno de estacionamiento
   - Nivel de líquido

5. **Neumáticos**
   - Presión
   - Estado de banda de rodadura
   - Daños visibles

6. **Sistema Eléctrico**
   - Luces
   - Indicadores
   - Batería

7. **Cabina/Operador**
   - Cinturón de seguridad
   - Espejos
   - Limpieza
   - Instrumentos

8. **Estructura**
   - Daños en carrocería
   - Fugas de fluidos
   - Soldaduras

9. **Equipamiento Específico** (según tipo de vehículo)
   - Para Supersucker: Sistema de vacío, tanque
   - Para Retroexcavadora: Brazo, cucharón, estabilizadores
   - Para Cargador: Cucharón, sistema de elevación
   - Para Minicargador: Accesorios, sistema de enganche rápido

## Implementation Requirements

### Database Seeding

Al inicializar el sistema, se deben crear automáticamente las 5 plantillas de checklist con:
- Todos los items específicos de cada PDF
- Campo `is_system_template = True` para prevenir eliminación
- Relación con el tipo de vehículo correspondiente

### PDF Generation

Cuando se completa un checklist, el PDF generado debe:
- Mantener el formato visual del PDF original
- Incluir logo y encabezados corporativos
- Mostrar todas las respuestas
- Incluir fotos adjuntas (si las hay)
- Mostrar observaciones
- Incluir firma digital del operador
- Mostrar fecha y hora de completado

### Validation Rules

1. Un Asset solo puede usar el Checklist_Template que corresponde a su Vehicle_Type
2. Los Checklist_Template con `is_system_template = True` no pueden ser eliminados
3. Los items marcados como `required = True` deben ser completados
4. Si un item se marca como "No", debe incluir observaciones obligatorias
5. El sistema debe calcular el porcentaje de cumplimiento

### Mobile Considerations

Los checklists deben ser completables desde dispositivos móviles:
- Interfaz táctil optimizada
- Captura de fotos desde cámara
- Soporte offline con sincronización posterior
- Firma digital con touch/stylus

## Data Migration

Para la implementación inicial, se debe:

1. Extraer manualmente los items de cada PDF
2. Crear archivos JSON con la estructura de cada checklist
3. Crear un comando Django `load_checklist_templates` que:
   - Lee los archivos JSON
   - Crea los 5 ChecklistTemplate en la base de datos
   - Marca como `is_system_template = True`
   - Valida que no existan duplicados

## Future Enhancements

Posibles mejoras futuras (no en MVP):
- Permitir crear checklists personalizados adicionales
- Versionado de templates
- Comparación de resultados entre inspecciones
- Análisis de tendencias por item
- Alertas automáticas por items críticos marcados como "No"

## Reference Files

Los PDFs originales están ubicados en:
- `Check_List_camión supersucker.pdf`
- `F-PR-020-CH01 Check List Camionetas MDO.pdf`
- `F-PR-034-CH01_Check Retroexcavadora MDO.pdf`
- `F-PR-037-CH01 Check List Cargador Frontal MDO.pdf`
- `F-PR-040-CH01 Check List Minicargador MDO.pdf`

Estos archivos deben ser analizados en detalle durante la implementación de la tarea de checklists para extraer todos los items específicos.
