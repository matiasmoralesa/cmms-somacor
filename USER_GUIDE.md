# Guía de Usuario - Sistema CMMS

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Módulos del Sistema](#módulos-del-sistema)
4. [Guías por Rol](#guías-por-rol)
5. [Preguntas Frecuentes](#preguntas-frecuentes)
6. [Soporte](#soporte)

---

## Introducción

El Sistema CMMS (Computerized Maintenance Management System) es una plataforma integral para la gestión de mantenimiento de vehículos y equipos. Permite planificar, ejecutar y dar seguimiento a todas las actividades de mantenimiento, con capacidades avanzadas de predicción de fallas mediante inteligencia artificial.

### Beneficios Clave

- ✅ Reducción de tiempos de inactividad no planificados
- ✅ Optimización de recursos y repuestos
- ✅ Predicción proactiva de fallas
- ✅ Trazabilidad completa de mantenimientos
- ✅ Acceso móvil mediante Telegram
- ✅ Reportes y KPIs en tiempo real

---

## Primeros Pasos

### 1. Acceso al Sistema

**Aplicación Web:**
- URL: `https://your-domain.com`
- Ingrese su email y contraseña
- El sistema le redirigirá al dashboard según su rol

**Bot de Telegram:**
- Busque el bot: `@CMSBot`
- Envíe el comando `/start`
- El bot le reconocerá automáticamente si su Telegram ID está registrado

### 2. Navegación Principal

El menú lateral contiene los siguientes módulos:

- **Dashboard**: Vista general del sistema
- **Activos**: Gestión de vehículos y equipos
- **Órdenes de Trabajo**: Creación y seguimiento de OT
- **Mantenimiento**: Planes preventivos y calendario
- **Inventario**: Control de repuestos
- **Checklists**: Inspecciones y verificaciones
- **Predicciones**: Alertas de fallas potenciales
- **Reportes**: KPIs y análisis
- **Configuración**: Ajustes del sistema (solo Admin)

### 3. Perfil de Usuario

Haga clic en su nombre en la esquina superior derecha para:
- Ver su perfil
- Cambiar contraseña
- Configurar notificaciones
- Cerrar sesión

---

## Módulos del Sistema

### 📦 Gestión de Activos

#### Ver Activos

1. Navegue a **Activos** en el menú
2. Verá la lista de todos los vehículos y equipos
3. Use los filtros para buscar:
   - Por nombre o código
   - Por tipo de vehículo
   - Por estado (Operacional, Mantenimiento, Fuera de Servicio)
   - Por ubicación

#### Crear Nuevo Activo

1. Click en **"Nuevo Activo"**
2. Complete el formulario:
   - **Nombre**: Ej. "Camión Supersucker 001"
   - **Código**: Identificador único (ej. CS-001)
   - **Tipo de Vehículo**: Seleccione uno de los 5 tipos
   - **Fabricante y Modelo**
   - **Número de Serie**
   - **Patente**
   - **Ubicación**
   - **Estado**: Operacional por defecto
   - **Criticidad**: Baja, Media, Alta, Crítica
3. Click en **"Guardar"**

#### Subir Documentos

1. Abra un activo
2. Vaya a la pestaña **"Documentos"**
3. Click en **"Subir Documento"**
4. Seleccione el tipo:
   - Manual de operación
   - Foto
   - Certificado
   - Plano técnico
5. Seleccione el archivo (máx. 10MB)
6. Click en **"Subir"**

### 🔧 Órdenes de Trabajo

#### Crear Orden de Trabajo

**Para Supervisores:**

1. Navegue a **Órdenes de Trabajo**
2. Click en **"Nueva Orden"**
3. Complete el formulario:
   - **Título**: Descripción breve
   - **Descripción**: Detalles del trabajo
   - **Activo**: Seleccione el vehículo/equipo
   - **Tipo**: Correctivo, Preventivo, Predictivo, Inspección
   - **Prioridad**: Baja, Media, Alta, Urgente
   - **Asignar a**: Seleccione el técnico
   - **Fecha programada**: Cuándo debe realizarse
4. Click en **"Guardar"**

La orden se creará con estado **"Pendiente"** y el técnico recibirá una notificación.

#### Ejecutar Orden de Trabajo

**Para Operadores:**

1. Navegue a **"Mis Asignaciones"**
2. Verá todas las órdenes asignadas a usted
3. Click en una orden para ver detalles
4. Click en **"Iniciar Trabajo"**
   - El estado cambia a "En Progreso"
   - Se registra la hora de inicio
5. Realice el trabajo
6. Click en **"Completar"**
7. Complete el formulario de cierre:
   - **Horas trabajadas**: Tiempo real invertido
   - **Notas de cierre**: Descripción del trabajo realizado
   - **Repuestos utilizados** (opcional)
8. Click en **"Guardar"**

La orden se marca como **"Completada"** y el supervisor recibe notificación.

#### Estados de Órdenes de Trabajo

- **Pendiente**: Creada pero no asignada o no iniciada
- **Asignada**: Asignada a un técnico
- **En Progreso**: El técnico está trabajando en ella
- **Completada**: Trabajo finalizado
- **Cancelada**: Orden cancelada

### 📅 Planes de Mantenimiento

#### Crear Plan de Mantenimiento

**Para Supervisores:**

1. Navegue a **Mantenimiento** > **Planes**
2. Click en **"Nuevo Plan"**
3. Complete el formulario:
   - **Nombre**: Ej. "Mantenimiento Preventivo Mensual"
   - **Activo**: Seleccione el vehículo
   - **Tipo**: Preventivo o Predictivo
   - **Recurrencia**: Diaria, Semanal, Mensual, Personalizada
   - **Intervalo**: Cada cuánto se repite
   - **Próxima fecha**: Cuándo debe ejecutarse
   - **Checklist**: Seleccione la plantilla correspondiente
   - **Duración estimada**: En minutos
4. Click en **"Guardar"**

El sistema generará automáticamente órdenes de trabajo según la programación.

#### Ver Calendario de Mantenimiento

1. Navegue a **Mantenimiento** > **Calendario**
2. Verá todos los mantenimientos programados
3. Use los filtros para ver:
   - Por mes/semana/día
   - Por activo
   - Por tipo de mantenimiento

#### Pausar/Reanudar Plan

1. Abra un plan de mantenimiento
2. Click en **"Pausar Plan"** si necesita detenerlo temporalmente
3. Click en **"Reanudar Plan"** para reactivarlo

### 📋 Checklists

#### Ejecutar Checklist

**Para Operadores:**

1. Navegue a **Checklists**
2. Click en **"Nueva Inspección"**
3. Seleccione:
   - **Plantilla**: Según el tipo de vehículo
   - **Activo**: El vehículo a inspeccionar
   - **Orden de Trabajo** (opcional): Si está vinculado a una OT
4. Complete cada ítem del checklist:
   - **Sí/No/N/A**: Para verificaciones binarias
   - **Numérico**: Para mediciones (ej. presión de neumáticos)
   - **Texto**: Para observaciones
5. **Subir fotos** cuando sea necesario
6. **Agregar notas** en ítems que lo requieran
7. Al finalizar, **firme digitalmente**
8. Click en **"Finalizar Inspección"**

El sistema:
- Calcula el puntaje automáticamente
- Genera un PDF con el formato original
- Almacena el PDF en la nube
- Vincula el checklist a la orden de trabajo

#### Plantillas de Checklist

El sistema incluye 5 plantillas predefinidas:

| Tipo de Vehículo | Código | Ítems |
|------------------|--------|-------|
| Camión Supersucker | SUPERSUCKER-CH01 | Motor, Sistema de vacío, Tanque, Mangueras |
| Camioneta MDO | F-PR-020-CH01 | Motor, Frenos, Neumáticos, Luces |
| Retroexcavadora MDO | F-PR-034-CH01 | Motor, Sistema hidráulico, Estructura, Seguridad |
| Cargador Frontal MDO | F-PR-037-CH01 | Motor, Hidráulico, Balde, Transmisión |
| Minicargador MDO | F-PR-040-CH01 | Motor, Hidráulico, Cadenas |

### 📦 Inventario de Repuestos

#### Ver Inventario

1. Navegue a **Inventario**
2. Verá todos los repuestos con:
   - Cantidad actual
   - Stock mínimo
   - Indicador de stock bajo (rojo)
   - Ubicación
   - Costo unitario

#### Ajustar Stock

**Para Operadores y Supervisores:**

1. Seleccione un repuesto
2. Click en **"Ajustar Stock"**
3. Seleccione el tipo de movimiento:
   - **Entrada**: Recepción de repuestos
   - **Salida**: Uso en mantenimiento
   - **Ajuste**: Corrección de inventario
4. Ingrese la cantidad
5. **Vincule a orden de trabajo** si es una salida
6. Agregue notas explicativas
7. Click en **"Guardar"**

El sistema:
- Actualiza el stock automáticamente
- Registra el movimiento en el historial
- Genera alerta si el stock queda bajo el mínimo

#### Alertas de Stock Bajo

Cuando un repuesto cae por debajo del stock mínimo:
- Se genera una alerta automática
- Los supervisores y admins reciben notificación
- El repuesto se marca en rojo en la lista

### 🤖 Predicciones de Fallas

#### Ver Dashboard de Predicciones

**Para Supervisores y Admins:**

1. Navegue a **Predicciones**
2. Verá el dashboard con:
   - **Scores de salud** de todos los activos
   - **Alertas activas** de alto riesgo
   - **Tendencias** de predicciones
   - **Recomendaciones** del sistema

#### Interpretar Scores de Salud

- **Verde (80-100)**: Activo en buen estado
- **Amarillo (60-79)**: Requiere atención
- **Naranja (40-59)**: Riesgo medio
- **Rojo (0-39)**: Riesgo alto, acción inmediata

#### Actuar sobre Alertas

1. Click en una alerta de alto riesgo
2. Revise los detalles:
   - Probabilidad de falla
   - Fecha estimada de falla
   - Componente afectado
   - Recomendaciones
3. Click en **"Crear Orden de Trabajo"**
4. El sistema pre-llena la OT con:
   - Tipo: Predictivo
   - Prioridad: Urgente
   - Descripción con detalles de la predicción
5. Asigne a un técnico y guarde

### 📊 Reportes y KPIs

#### Ver Dashboard de KPIs

1. Navegue a **Reportes**
2. Verá tarjetas con:
   - **Órdenes activas**: Cantidad de OT en progreso
   - **Mantenimientos pendientes**: Próximos mantenimientos
   - **Alertas críticas**: Alertas que requieren atención
   - **Disponibilidad de flota**: Porcentaje de activos operacionales

#### Generar Reporte Personalizado

1. Click en **"Generar Reporte"**
2. Seleccione:
   - **Tipo de reporte**:
     - Resumen de órdenes de trabajo
     - Downtime de activos
     - Consumo de repuestos
     - KPIs de mantenimiento
   - **Rango de fechas**
   - **Filtros** (activo, tipo, prioridad)
3. Click en **"Generar"**
4. Visualice el reporte en pantalla
5. **Exporte** en CSV o PDF

#### KPIs Disponibles

- **MTBF** (Mean Time Between Failures): Tiempo promedio entre fallas
- **MTTR** (Mean Time To Repair): Tiempo promedio de reparación
- **OEE** (Overall Equipment Effectiveness): Efectividad general del equipo
- **Tasa de cumplimiento**: Porcentaje de mantenimientos completados a tiempo
- **Costo de mantenimiento**: Por activo y por período

### 🔔 Notificaciones

#### Configurar Preferencias

1. Click en su perfil > **"Preferencias de Notificación"**
2. Configure para cada tipo de evento:
   - **En la aplicación**: Notificaciones en el sistema
   - **Email**: Notificaciones por correo
   - **Telegram**: Notificaciones en Telegram
3. Tipos de eventos:
   - Orden de trabajo asignada
   - Cambio de estado de OT
   - Alerta de predicción
   - Stock bajo
   - Mantenimiento próximo

#### Ver Notificaciones

1. Click en el ícono de campana (🔔) en la barra superior
2. Verá todas sus notificaciones recientes
3. Click en una notificación para ver detalles
4. Click en **"Marcar como leída"**
5. Click en **"Marcar todas como leídas"** para limpiar

---

## Guías por Rol

### 👨‍💼 Administrador

**Responsabilidades:**
- Gestión de usuarios y roles
- Configuración del sistema
- Supervisión general
- Acceso a todos los módulos

**Tareas Comunes:**

1. **Crear Usuario**
   - Navegue a **Configuración** > **Usuarios**
   - Click en **"Nuevo Usuario"**
   - Complete datos personales
   - Asigne rol (Admin, Supervisor, Operador)
   - Para operadores, registre información de licencia
   - Click en **"Guardar"**

2. **Configurar Datos Maestros**
   - Navegue a **Configuración** > **Datos Maestros**
   - Gestione:
     - Ubicaciones
     - Categorías de activos
     - Tipos de órdenes de trabajo
     - Niveles de prioridad

3. **Revisar Logs de Auditoría**
   - Navegue a **Configuración** > **Auditoría**
   - Filtre por:
     - Usuario
     - Acción (crear, modificar, eliminar)
     - Fecha
   - Exporte logs si es necesario

### 👨‍🔧 Supervisor

**Responsabilidades:**
- Planificación de mantenimiento
- Asignación de órdenes de trabajo
- Supervisión de equipo
- Análisis de reportes

**Flujo de Trabajo Típico:**

1. **Inicio del Día**
   - Revise el dashboard
   - Verifique alertas críticas
   - Revise órdenes pendientes

2. **Planificación**
   - Cree órdenes de trabajo para el día
   - Asigne técnicos según disponibilidad
   - Priorice según urgencia y predicciones

3. **Seguimiento**
   - Monitoree progreso de órdenes
   - Responda a consultas de técnicos
   - Revise checklists completados

4. **Cierre del Día**
   - Verifique órdenes completadas
   - Revise consumo de repuestos
   - Planifique para el día siguiente

### 👷 Operador/Técnico

**Responsabilidades:**
- Ejecutar órdenes de trabajo asignadas
- Completar checklists
- Reportar problemas
- Registrar uso de repuestos

**Flujo de Trabajo Típico:**

1. **Inicio del Turno**
   - Revise **"Mis Asignaciones"**
   - Priorice según urgencia
   - Verifique disponibilidad de repuestos

2. **Ejecución de Trabajo**
   - Inicie la orden de trabajo
   - Ejecute el checklist correspondiente
   - Tome fotos de evidencia
   - Registre observaciones

3. **Uso de Repuestos**
   - Registre salida de repuestos
   - Vincule a la orden de trabajo
   - Reporte stock bajo si es necesario

4. **Cierre de Trabajo**
   - Complete la orden de trabajo
   - Registre horas trabajadas
   - Agregue notas de cierre
   - Firme digitalmente el checklist

---

## Bot de Telegram

### Comandos Disponibles

#### Para Todos los Roles

- `/start` - Iniciar el bot
- `/status` - Estado del sistema
- `/equipos` - Lista de activos

#### Para Operadores

- `/ordenes` - Mis órdenes asignadas
- `/pendientes` - Cantidad de órdenes pendientes

#### Para Supervisores y Admins

- `/alertas` - Alertas recientes
- `/kpis` - Indicadores clave

### Notificaciones Automáticas

El bot enviará notificaciones automáticas para:
- Nuevas órdenes asignadas
- Cambios de estado en órdenes
- Alertas críticas de predicción
- Stock bajo de repuestos

---

## Preguntas Frecuentes

### General

**P: ¿Cómo recupero mi contraseña?**
R: En la pantalla de login, click en "¿Olvidaste tu contraseña?". Ingresa tu email y recibirás instrucciones.

**P: ¿Puedo usar el sistema en mi teléfono?**
R: Sí, la aplicación web es responsive. También puedes usar el bot de Telegram para acceso rápido.

**P: ¿Cómo cambio mi contraseña?**
R: Click en tu perfil > "Cambiar Contraseña". Ingresa tu contraseña actual y la nueva.

### Órdenes de Trabajo

**P: ¿Puedo reasignar una orden de trabajo?**
R: Sí, si eres supervisor o admin. Abre la orden y click en "Reasignar".

**P: ¿Qué hago si no puedo completar una orden?**
R: Agrega notas explicando el problema y contacta a tu supervisor. Puedes pausar la orden si es necesario.

**P: ¿Puedo ver el historial de una orden?**
R: Sí, en los detalles de la orden hay una pestaña "Historial" con todos los cambios.

### Checklists

**P: ¿Qué pasa si no puedo completar todos los ítems del checklist?**
R: Marca los ítems que no aplican como "N/A" y agrega notas explicativas. El sistema calculará el puntaje considerando solo los ítems aplicables.

**P: ¿Puedo editar un checklist después de enviarlo?**
R: No, los checklists son inmutables una vez enviados para mantener la integridad. Si hay un error, crea uno nuevo.

**P: ¿Dónde se guardan las fotos que subo?**
R: Las fotos se almacenan de forma segura en Google Cloud Storage y están vinculadas al checklist.

### Inventario

**P: ¿Cómo solicito más repuestos?**
R: Cuando el stock está bajo, se genera una alerta automática. También puedes contactar al encargado de compras directamente.

**P: ¿Puedo devolver repuestos al inventario?**
R: Sí, usa "Ajustar Stock" con tipo "Entrada" y agrega notas explicando la devolución.

### Predicciones

**P: ¿Qué tan precisas son las predicciones?**
R: El modelo de ML tiene una precisión del 85-90% basado en datos históricos. Las predicciones deben usarse como guía, no como certeza absoluta.

**P: ¿Por qué mi activo tiene un score bajo?**
R: El score considera múltiples factores: horas de operación, historial de fallas, tiempo desde último mantenimiento, etc. Revisa las recomendaciones del sistema.

---

## Soporte

### Contacto

- **Email**: soporte@cmms.com
- **Teléfono**: +56 2 XXXX XXXX
- **Horario**: Lunes a Viernes, 9:00 - 18:00

### Reportar Problemas

1. Navegue a **Ayuda** > **Reportar Problema**
2. Complete el formulario:
   - Descripción del problema
   - Pasos para reproducir
   - Capturas de pantalla (opcional)
3. Recibirá un número de ticket
4. El equipo de soporte le contactará

### Recursos Adicionales

- **Tutoriales en Video**: [Link a videos]
- **Base de Conocimiento**: [Link a KB]
- **Changelog**: [Link a cambios]

---

**Versión del Documento:** 1.0  
**Última Actualización:** 2024-11-13  
**Próxima Revisión:** Trimestral
