# User Profiles and Permissions - Sistema CMMS

Este documento define los tres perfiles de usuario del sistema y sus permisos específicos basados en el perfilamiento proporcionado.

## Perfiles de Usuario

El sistema tiene **3 perfiles** con diferentes niveles de acceso:

### 1. ADMIN (Administrador)
**Acceso completo al sistema**

### 2. SUPERVISOR
**Acceso de gestión y supervisión**

### 3. OPERADOR
**Acceso limitado a tareas asignadas**

---

## Matriz de Permisos por Módulo

### 📊 Dashboard

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver equipos por estado (gráfico) | ✅ | ✅ | ❌ |
| Ver estadísticas generales | ✅ | ✅ | ❌ |
| Ver KPIs del sistema | ✅ | ✅ | ❌ |
| Ver actividad reciente | ✅ | ✅ | ✅ (solo propia) |

### 🚗 Estado de la Máquina (Equipos/Assets)

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver TODOS los equipos | ✅ | ✅ | ❌ |
| Ver solo equipos asignados | ✅ | ✅ | ✅ |
| Consultar estado de equipos | ✅ | ✅ | ✅ (asignados) |
| Crear/Editar equipos | ✅ | ✅ | ❌ |
| Eliminar equipos | ✅ | ❌ | ❌ |
| Subir documentos de equipos | ✅ | ✅ | ❌ |
| Marcar equipo como inactivo | ✅ | ✅ | ❌ |

### 📋 Órdenes de Trabajo (OT)

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver TODAS las OT | ✅ | ✅ | ❌ |
| Ver solo OT asignadas | ✅ | ✅ | ✅ |
| Crear OT | ✅ | ✅ | ❌ |
| Asignar OT a operadores | ✅ | ✅ | ❌ |
| Cambiar estado de OT | ✅ | ✅ | ✅ (solo asignadas) |
| Completar OT | ✅ | ✅ | ✅ (solo asignadas) |
| Cancelar OT | ✅ | ✅ | ❌ |
| Ver historial completo | ✅ | ✅ | ✅ (solo propias) |

**Nota importante:** 
- Listado no muestra equipo, tipo y estado
- Botón "Reportar Falla" no muestra solicitudes
- Nota: Revisar el flujo de OT y facilidad/agilizar fotografías de respaldo

### ✅ Checklists Diarios

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver TODOS los checklists | ✅ | ✅ | ❌ |
| Ver checklists de equipos asignados | ✅ | ✅ | ✅ |
| Completar checklists | ✅ | ✅ | ✅ (asignados) |
| Ver checklists completados | ✅ | ✅ | ✅ (propios) |
| Descargar PDF de checklist | ✅ | ✅ | ✅ |
| Seleccionar equipos sin checklist | ✅ | ✅ | ❌ |

**Nota:** Se seleccionan equipos pero no hay checklist cargados

### 🔧 Reportar Falla

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Reportar falla | ✅ | ✅ | ✅ |
| Crear reporte de falla | ✅ | ✅ | ✅ |
| Agregar fotografía | ✅ | ✅ | ✅ |
| Ver reportes propios | ✅ | ✅ | ✅ |
| Ver TODOS los reportes | ✅ | ✅ | ❌ |

**Nota:** Facilidad agregar una fotografía para acompañar la falla

### 📅 Calendario

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver calendario | ✅ | ✅ | ❌ |
| Ver mantenimientos programados | ✅ | ✅ | ❌ |
| Crear mantenimiento planificado | ✅ | ✅ | ❌ |
| Editar mantenimiento | ✅ | ✅ | ❌ |
| Eliminar mantenimiento | ✅ | ❌ | ❌ |

**Nota:** No carga datos

### 🔧 Programas de Mantenimiento

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Ver programas | ✅ | ✅ | ❌ |
| Crear programa | ✅ | ✅ | ❌ |
| Editar programa | ✅ | ✅ | ❌ |
| Pausar/Reanudar programa | ✅ | ✅ | ❌ |
| Eliminar programa | ✅ | ❌ | ❌ |
| Acceder a detalles del plan | ✅ | ✅ | ❌ |

**Nota:** Se accede a acuerdos de detalles del plan de mantenimiento pero no muestra las tareas y no se puede generar agenda

### 👥 Administración (Solo ADMIN)

| Funcionalidad | ADMIN | SUPERVISOR | OPERADOR |
|--------------|-------|------------|----------|
| Gestión de usuarios | ✅ | ❌ | ❌ |
| Gestión de perfiles | ✅ | ❌ | ❌ |
| Gestión de equipos móviles | ✅ | ❌ | ❌ |
| Gestión de programas de mantenimiento | ✅ | ❌ | ❌ |
| Configuración del sistema | ✅ | ❌ | ❌ |
| Ver logs de auditoría | ✅ | ❌ | ❌ |

#### Gestión de Perfiles (ADMIN)

**Requisitos para registro de operadores:**
- Listado no imprimir nombre completo, rol, ni Estado de empleado
- Añadir tipo de licencia (Licencia municipal, licencia interna, otra)
- Nota: Revisar factibilidad de guardar fotografías de licencias
- Nota: Revisar factibilidad de acordar la fecha de kilometraje y acciones realizadas en un equipo

**Campos requeridos:**
1. Nombre completo
2. RUT
3. Estado de empleado
4. Tipo de licencia (opciones):
   - Licencia municipal
   - Licencia interna  
   - Otra
5. Fecha de vencimiento de licencia
6. Fotografía de licencia (para control de operador con licencia en regla)

**Validaciones:**
- No operador tiene que tener licencias en regla (no vencidas) para operar equipos
- Sistema debe alertar cuando licencias estén próximas a vencer (1 mes antes)

#### Gestión de Equipos Móviles (ADMIN)

**Requisitos:**
- Listado no imprimir Fecha y Estado
- Añadir tipo de licencia necesaria para cada tipo de equipo

**Campos requeridos:**
1. Fecha y Estado
2. Tipo de licencia requerida para operar el equipo

**Nota:** Revisar factibilidad de acordar la fecha de kilometraje y acciones realizadas en un equipo

#### Gestión de Programas de Mantenimiento (ADMIN)

**Nota:** No se puede seleccionar la pestaña a ejecutar

---

## Reglas de Negocio por Perfil

### ADMIN
- Acceso total sin restricciones
- Único perfil que puede acceder al módulo de Administración
- Puede gestionar usuarios, perfiles y configuración del sistema
- Puede eliminar registros (equipos, OT, programas)
- Puede ver y gestionar TODOS los recursos del sistema

### SUPERVISOR
- Acceso de gestión operativa
- Puede ver TODOS los equipos, OT y checklists
- Puede crear y asignar OT
- Puede crear programas de mantenimiento
- Puede gestionar equipos (crear, editar, documentos)
- NO puede acceder a Administración
- NO puede eliminar registros críticos

### OPERADOR
- Acceso limitado a tareas asignadas
- Solo ve equipos que le han sido asignados
- Solo ve OT que le han sido asignadas
- Solo puede completar checklists de equipos asignados
- Puede reportar fallas
- NO puede crear OT ni programas de mantenimiento
- NO puede ver dashboard ni calendario
- NO puede acceder a Administración

---

## Flujo de Trabajo por Perfil

### Flujo ADMIN
1. Accede al dashboard con vista completa
2. Gestiona usuarios y perfiles en Administración
3. Configura equipos y programas de mantenimiento
4. Supervisa todas las operaciones
5. Genera reportes y analíticas

### Flujo SUPERVISOR
1. Accede al dashboard con vista completa
2. Revisa estado de todos los equipos
3. Crea y asigna OT a operadores
4. Programa mantenimientos en calendario
5. Supervisa checklists completados
6. Revisa reportes de fallas

### Flujo OPERADOR
1. Accede a "Mis Tareas" (OT asignadas)
2. Completa checklists diarios de equipos asignados
3. Ejecuta OT asignadas
4. Reporta fallas cuando las detecta
5. Actualiza estado de OT en progreso

---

## Validaciones de Licencias

### Control de Licencias de Operadores

**Regla crítica:** Un operador NO puede operar un equipo si:
1. No tiene licencia registrada
2. Su licencia está vencida
3. El tipo de licencia no corresponde al tipo de equipo

**Alertas del sistema:**
- 🔴 **Crítica**: Licencia vencida (bloquea operación)
- 🟡 **Advertencia**: Licencia próxima a vencer (30 días)
- 🟢 **OK**: Licencia vigente

**Proceso de validación:**
1. Al asignar OT a operador, sistema valida licencia
2. Al completar checklist, sistema valida licencia del operador
3. Dashboard de ADMIN muestra operadores con licencias por vencer
4. Notificaciones automáticas 30 días antes del vencimiento

---

## Notas de Implementación

### Prioridades de Corrección

1. **Alta Prioridad:**
   - Implementar validación de licencias
   - Corregir listados que no muestran información completa
   - Habilitar carga de fotografías en reportes de falla
   - Implementar checklists predefinidos por tipo de equipo

2. **Media Prioridad:**
   - Mejorar flujo de OT con fotografías de respaldo
   - Implementar calendario funcional
   - Habilitar gestión de programas de mantenimiento
   - Agregar filtros por tipo de licencia

3. **Baja Prioridad:**
   - Optimizar interfaz de usuario
   - Agregar más opciones de reportes
   - Implementar notificaciones push

### Campos Faltantes a Agregar

**En Perfiles de Usuario:**
- Tipo de licencia (dropdown)
- Fecha de vencimiento de licencia
- Campo para subir foto de licencia

**En Equipos Móviles:**
- Tipo de licencia requerida para operar
- Fecha de última operación
- Kilometraje/horómetro actual

**En Órdenes de Trabajo:**
- Mostrar equipo, tipo y estado en listado
- Facilitar adjuntar múltiples fotografías

**En Checklists:**
- Cargar checklists predefinidos por tipo de equipo
- Indicador de equipos sin checklist asignado

---

## Resumen de Cambios vs Sistema Actual

| Aspecto | Sistema Actual | Sistema Mejorado |
|---------|---------------|------------------|
| Perfiles | 5 roles (Admin, Supervisor, Técnico, Operador, Invitado) | 3 roles (ADMIN, SUPERVISOR, OPERADOR) |
| Licencias | No validadas | Validación obligatoria con foto |
| Checklists | No cargados | 5 predefinidos por tipo de vehículo |
| OT | Listado incompleto | Listado completo con fotos |
| Calendario | No funcional | Funcional con programación |
| Reportes de Falla | Sin fotos | Con fotos obligatorias |
| Administración | Limitada | Completa solo para ADMIN |

Este perfilamiento asegura que cada usuario tenga acceso solo a la información y funciones necesarias para su rol, mejorando la seguridad y usabilidad del sistema.
