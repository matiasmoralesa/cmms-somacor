# Plan de Pruebas - Sistema CMMS SOMACOR

## 1. Información General

### 1.1 Objetivo
Validar el correcto funcionamiento de todos los módulos del Sistema de Gestión de Mantenimiento Computarizado (CMMS) SOMACOR, asegurando que cumple con los requisitos funcionales y no funcionales establecidos.

### 1.2 Alcance
- **Incluye**: Pruebas funcionales de API, validación de datos, autenticación y autorización
- **Excluye**: Pruebas de interfaz de usuario (UI), pruebas de carga, pruebas de seguridad avanzadas

### 1.3 Entorno de Pruebas
- **Backend**: https://cmms-backend-888881509782.us-central1.run.app
- **Frontend**: https://cmms-somacor-prod.web.app
- **Base de Datos**: Cloud SQL PostgreSQL (GCP)
- **Infraestructura**: Google Cloud Platform

---

## 2. Estrategia de Pruebas

### 2.1 Tipos de Pruebas

1. **Pruebas Funcionales**: Verificar que cada funcionalidad trabaja según lo esperado
2. **Pruebas de Integración**: Validar la comunicación entre módulos
3. **Pruebas de API**: Verificar endpoints REST
4. **Pruebas de Autenticación**: Validar seguridad y control de acceso

### 2.2 Criterios de Aceptación

- ✅ **PASS**: La funcionalidad trabaja correctamente según lo esperado
- ❌ **FAIL**: La funcionalidad no trabaja o produce errores
- ⚪ **SKIP**: La prueba no se pudo ejecutar por dependencias o datos faltantes

### 2.3 Criterios de Éxito

- Mínimo 80% de pruebas exitosas
- 0 errores críticos
- Todos los módulos core operativos

---

## 3. Casos de Prueba por Módulo

### 3.1 Módulo de Autenticación

#### TC-AUTH-001: Login con credenciales válidas (Admin)
- **Objetivo**: Verificar que un administrador puede iniciar sesión
- **Precondiciones**: Usuario admin existe en el sistema
- **Pasos**:
  1. Enviar POST a `/api/v1/auth/login/`
  2. Incluir email: `admin@cmms.com` y password: `admin123`
- **Resultado Esperado**: 
  - Status 200
  - Token JWT válido
  - Información del usuario con rol ADMIN

#### TC-AUTH-002: Login con credenciales válidas (Supervisor)
- **Objetivo**: Verificar que un supervisor puede iniciar sesión
- **Precondiciones**: Usuario supervisor existe en el sistema
- **Pasos**:
  1. Enviar POST a `/api/v1/auth/login/`
  2. Incluir email y password de supervisor
- **Resultado Esperado**: 
  - Status 200
  - Token JWT válido
  - Información del usuario con rol SUPERVISOR

#### TC-AUTH-003: Login con credenciales válidas (Operador)
- **Objetivo**: Verificar que un operador puede iniciar sesión
- **Precondiciones**: Usuario operador existe en el sistema
- **Pasos**:
  1. Enviar POST a `/api/v1/auth/login/`
  2. Incluir email y password de operador
- **Resultado Esperado**: 
  - Status 200
  - Token JWT válido
  - Información del usuario con rol OPERADOR

#### TC-AUTH-004: Rechazo de credenciales incorrectas
- **Objetivo**: Verificar que el sistema rechaza credenciales inválidas
- **Precondiciones**: Ninguna
- **Pasos**:
  1. Enviar POST a `/api/v1/auth/login/`
  2. Incluir credenciales incorrectas
- **Resultado Esperado**: 
  - Status 401
  - Mensaje de error apropiado
  - No se genera token

---

### 3.2 Módulo de Gestión de Usuarios

#### TC-USER-001: Listar todos los usuarios
- **Objetivo**: Verificar que se pueden listar todos los usuarios
- **Precondiciones**: Usuario autenticado con permisos
- **Pasos**:
  1. Enviar GET a `/api/v1/auth/users/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de usuarios con sus datos

#### TC-USER-002: Obtener roles disponibles
- **Objetivo**: Verificar que se pueden listar los roles del sistema
- **Precondiciones**: Usuario autenticado
- **Pasos**:
  1. Enviar GET a `/api/v1/auth/roles/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de roles (ADMIN, SUPERVISOR, OPERADOR, MECANICO)

#### TC-USER-003: Ver perfil propio
- **Objetivo**: Verificar que un usuario puede ver su propio perfil
- **Precondiciones**: Usuario autenticado
- **Pasos**:
  1. Enviar GET a `/api/v1/auth/profile/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Datos completos del usuario autenticado

---

### 3.3 Módulo de Gestión de Activos

#### TC-ASSET-001: Listar todos los activos
- **Objetivo**: Verificar que se pueden listar todos los activos
- **Precondiciones**: Usuario autenticado, activos existen en el sistema
- **Pasos**:
  1. Enviar GET a `/api/v1/assets/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de activos con sus datos

#### TC-ASSET-002: Listar ubicaciones
- **Objetivo**: Verificar que se pueden listar todas las ubicaciones
- **Precondiciones**: Usuario autenticado, ubicaciones existen
- **Pasos**:
  1. Enviar GET a `/api/v1/assets/locations/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de ubicaciones

#### TC-ASSET-003: Filtrar activos por tipo de vehículo
- **Objetivo**: Verificar que se pueden filtrar activos por tipo
- **Precondiciones**: Usuario autenticado, activos de diferentes tipos existen
- **Pasos**:
  1. Enviar GET a `/api/v1/assets/?vehicle_type=CAMIONETA_MDO`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo activos del tipo especificado

---

### 3.4 Módulo de Gestión de Inventario

#### TC-INV-001: Listar repuestos
- **Objetivo**: Verificar que se pueden listar todos los repuestos
- **Precondiciones**: Usuario autenticado, repuestos existen
- **Pasos**:
  1. Enviar GET a `/api/v1/inventory/spare-parts/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de repuestos con stock actual

#### TC-INV-002: Filtrar repuestos por categoría
- **Objetivo**: Verificar que se pueden filtrar repuestos por categoría
- **Precondiciones**: Usuario autenticado, repuestos de diferentes categorías existen
- **Pasos**:
  1. Enviar GET a `/api/v1/inventory/spare-parts/?category=FILTERS`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo repuestos de la categoría especificada

#### TC-INV-003: Alertas de stock bajo
- **Objetivo**: Verificar que se pueden obtener alertas de stock bajo
- **Precondiciones**: Usuario autenticado, repuestos con stock bajo existen
- **Pasos**:
  1. Enviar GET a `/api/v1/inventory/spare-parts/low-stock/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de repuestos con stock por debajo del mínimo

---

### 3.5 Módulo de Órdenes de Trabajo

#### TC-WO-001: Listar órdenes de trabajo
- **Objetivo**: Verificar que se pueden listar todas las órdenes
- **Precondiciones**: Usuario autenticado, órdenes existen
- **Pasos**:
  1. Enviar GET a `/api/v1/work-orders/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de órdenes de trabajo

#### TC-WO-002: Filtrar órdenes por prioridad
- **Objetivo**: Verificar que se pueden filtrar órdenes por prioridad
- **Precondiciones**: Usuario autenticado, órdenes de diferentes prioridades existen
- **Pasos**:
  1. Enviar GET a `/api/v1/work-orders/?priority=HIGH`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo órdenes de alta prioridad

#### TC-WO-003: Filtrar órdenes por tipo
- **Objetivo**: Verificar que se pueden filtrar órdenes por tipo
- **Precondiciones**: Usuario autenticado, órdenes de diferentes tipos existen
- **Pasos**:
  1. Enviar GET a `/api/v1/work-orders/?work_order_type=PREVENTIVE`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo órdenes preventivas

---

### 3.6 Módulo de Planes de Mantenimiento

#### TC-MAINT-001: Listar planes de mantenimiento
- **Objetivo**: Verificar que se pueden listar todos los planes
- **Precondiciones**: Usuario autenticado, planes existen
- **Pasos**:
  1. Enviar GET a `/api/v1/maintenance/plans/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de planes de mantenimiento

#### TC-MAINT-002: Filtrar planes activos
- **Objetivo**: Verificar que se pueden filtrar planes activos
- **Precondiciones**: Usuario autenticado, planes activos e inactivos existen
- **Pasos**:
  1. Enviar GET a `/api/v1/maintenance/plans/?is_active=true`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo planes activos

---

### 3.7 Módulo de Checklists

#### TC-CHECK-001: Listar plantillas de checklist
- **Objetivo**: Verificar que se pueden listar todas las plantillas
- **Precondiciones**: Usuario autenticado, plantillas existen
- **Pasos**:
  1. Enviar GET a `/api/v1/checklists/templates/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de plantillas (5 plantillas predefinidas)

#### TC-CHECK-002: Filtrar plantillas por tipo de vehículo
- **Objetivo**: Verificar que se pueden filtrar plantillas por vehículo
- **Precondiciones**: Usuario autenticado, plantillas para diferentes vehículos existen
- **Pasos**:
  1. Enviar GET a `/api/v1/checklists/templates/?vehicle_type=CAMIONETA_MDO`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Solo plantillas para camionetas

#### TC-CHECK-003: Listar respuestas de checklist
- **Objetivo**: Verificar que se pueden listar respuestas completadas
- **Precondiciones**: Usuario autenticado, respuestas existen
- **Pasos**:
  1. Enviar GET a `/api/v1/checklists/responses/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de checklists completados

---

### 3.8 Módulo de Notificaciones

#### TC-NOTIF-001: Listar notificaciones
- **Objetivo**: Verificar que se pueden listar notificaciones del usuario
- **Precondiciones**: Usuario autenticado
- **Pasos**:
  1. Enviar GET a `/api/v1/notifications/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Lista de notificaciones del usuario

#### TC-NOTIF-002: Contador de notificaciones no leídas
- **Objetivo**: Verificar que se puede obtener el contador de no leídas
- **Precondiciones**: Usuario autenticado
- **Pasos**:
  1. Enviar GET a `/api/v1/notifications/unread_count/`
  2. Incluir token de autenticación
- **Resultado Esperado**: 
  - Status 200
  - Número de notificaciones no leídas

---

## 4. Datos de Prueba

### 4.1 Usuarios de Prueba

```
Admin:
  Email: admin@cmms.com
  Password: admin123
  Rol: ADMIN

Supervisor:
  Email: supervisor@somacor.com
  Password: Supervisor123!
  Rol: SUPERVISOR

Operador 1:
  Email: operador1@somacor.com
  Password: Operador123!
  Rol: OPERADOR

Operador 2:
  Email: operador2@somacor.com
  Password: Operador123!
  Rol: OPERADOR
```

### 4.2 Activos de Prueba

1. **Camioneta Toyota Hilux** (CAM-001)
   - Tipo: CAMIONETA_MDO
   - Ubicación: Planta Principal

2. **Camión Supersucker** (CSS-001)
   - Tipo: CAMION_SUPERSUCKER
   - Ubicación: Planta Principal

3. **Retroexcavadora CAT 420F** (RET-001)
   - Tipo: RETROEXCAVADORA_MDO
   - Ubicación: Planta Principal

4. **Cargador Frontal CAT 950** (CAR-001)
   - Tipo: CARGADOR_FRONTAL_MDO
   - Ubicación: Planta Principal

5. **Minicargador Bobcat S570** (MIN-001)
   - Tipo: MINICARGADOR_MDO
   - Ubicación: Planta Principal

### 4.3 Repuestos de Prueba

1. Filtro de Aceite (FIL-001) - Categoría: FILTERS
2. Filtro de Aire (FIL-002) - Categoría: FILTERS
3. Aceite Motor 15W40 (ACE-001) - Categoría: LUBRICANTS
4. Neumático 275/70R18 (NEU-001) - Categoría: TIRES
5. Batería 12V 100Ah (BAT-001) - Categoría: ELECTRICAL

---

## 5. Ejecución de Pruebas

### 5.1 Herramientas

- **Script Automatizado**: `plan_pruebas_cmms.py`
- **Cliente HTTP**: Python requests
- **Formato de Reporte**: JSON y Markdown

### 5.2 Comandos

```bash
# Ejecutar plan de pruebas completo
python plan_pruebas_cmms.py

# Ver reporte generado
cat reporte_pruebas_cmms.json
cat REPORTE_PRUEBAS_CMMS.md
```

### 5.3 Frecuencia

- **Pruebas de Regresión**: Después de cada despliegue
- **Pruebas Completas**: Semanalmente
- **Pruebas de Humo**: Diariamente

---

## 6. Criterios de Salida

### 6.1 Criterios de Éxito

- ✅ Mínimo 80% de pruebas exitosas
- ✅ 0 errores críticos (severidad alta)
- ✅ Todos los módulos core operativos
- ✅ Autenticación y autorización funcionando
- ✅ APIs respondiendo en < 500ms

### 6.2 Criterios de Fallo

- ❌ Más del 20% de pruebas fallidas
- ❌ Errores críticos en módulos core
- ❌ Problemas de seguridad identificados
- ❌ APIs no disponibles o con errores 500

---

## 7. Gestión de Defectos

### 7.1 Severidades

- **Crítica**: Sistema no funciona, pérdida de datos, seguridad comprometida
- **Alta**: Funcionalidad principal no trabaja, workaround difícil
- **Media**: Funcionalidad secundaria no trabaja, workaround disponible
- **Baja**: Problema cosmético, no afecta funcionalidad

### 7.2 Proceso

1. Identificar y documentar el defecto
2. Asignar severidad y prioridad
3. Reportar en sistema de tracking
4. Asignar a desarrollador
5. Verificar corrección
6. Cerrar defecto

---

## 8. Entregables

1. ✅ Plan de Pruebas (este documento)
2. ✅ Script de Pruebas Automatizado (`plan_pruebas_cmms.py`)
3. ✅ Reporte de Ejecución (`REPORTE_PRUEBAS_CMMS.md`)
4. ✅ Datos de Prueba en JSON (`reporte_pruebas_cmms.json`)
5. ⏳ Matriz de Trazabilidad (pendiente)
6. ⏳ Reporte de Defectos (según necesidad)

---

## 9. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Datos de prueba incompletos | Media | Alto | Crear script de carga de datos |
| APIs no disponibles | Baja | Crítico | Monitoreo continuo, alertas |
| Cambios en requisitos | Media | Medio | Actualizar plan de pruebas |
| Falta de tiempo | Alta | Medio | Priorizar pruebas críticas |

---

## 10. Aprobaciones

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| QA Lead | - | - | - |
| Project Manager | - | - | - |
| Tech Lead | - | - | - |

---

**Documento creado**: 18 de Noviembre de 2025
**Versión**: 1.0
**Próxima revisión**: 25 de Noviembre de 2025
