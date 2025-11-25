# Guía de Administración - Sistema CMMS

## Tabla de Contenidos

1. [Gestión de Usuarios](#gestión-de-usuarios)
2. [Configuración del Sistema](#configuración-del-sistema)
3. [Mantenimiento del Sistema](#mantenimiento-del-sistema)
4. [Monitoreo y Alertas](#monitoreo-y-alertas)
5. [Respaldo y Recuperación](#respaldo-y-recuperación)
6. [Troubleshooting](#troubleshooting)

---

## Gestión de Usuarios

### Crear Usuario

1. Navegue a **Configuración** > **Usuarios**
2. Click en **"Nuevo Usuario"**
3. Complete el formulario:

**Información Personal:**
- Email (será el username)
- Nombre y Apellido
- RUT (formato: 12345678-9)
- Teléfono
- Telegram ID (opcional, para notificaciones)

**Información de Rol:**
- Seleccione el rol: ADMIN, SUPERVISOR, OPERADOR
- Estado del empleado: Activo, Inactivo, Licencia

**Para Operadores (Información de Licencia):**
- Tipo de licencia: Municipal, Interna, Otra
- Fecha de vencimiento
- Foto de licencia (subir archivo)

4. Click en **"Guardar"**
5. El usuario recibirá un email con instrucciones para establecer su contraseña

### Modificar Usuario

1. Busque el usuario en la lista
2. Click en el nombre para abrir el perfil
3. Modifique los campos necesarios
4. Click en **"Guardar Cambios"**

**Nota:** Los cambios de rol toman efecto inmediatamente.

### Desactivar Usuario

1. Abra el perfil del usuario
2. Cambie "Estado del empleado" a **"Inactivo"**
3. Click en **"Guardar"**

El usuario no podrá iniciar sesión pero sus datos históricos se mantienen.

### Resetear Contraseña

1. Abra el perfil del usuario
2. Click en **"Resetear Contraseña"**
3. El usuario recibirá un email con link de recuperación

### Gestión de Licencias de Operadores

**Alertas de Vencimiento:**
- El sistema genera alertas automáticas 30 días antes del vencimiento
- Los operadores con licencias vencidas no pueden ser asignados a órdenes de trabajo

**Renovar Licencia:**
1. Abra el perfil del operador
2. Actualice la fecha de vencimiento
3. Suba la nueva foto de licencia
4. Click en **"Guardar"**

### Roles y Permisos

#### ADMIN
- Acceso completo al sistema
- Gestión de usuarios y roles
- Configuración del sistema
- Acceso a logs de auditoría
- Gestión de datos maestros

#### SUPERVISOR
- Gestión de órdenes de trabajo
- Creación de planes de mantenimiento
- Asignación de técnicos
- Acceso a reportes y KPIs
- Gestión de inventario
- Visualización de predicciones

#### OPERADOR
- Ver órdenes asignadas
- Completar órdenes de trabajo
- Ejecutar checklists
- Registrar uso de repuestos
- Ver inventario (solo lectura)

---

## Configuración del Sistema

### Datos Maestros

#### Ubicaciones

1. Navegue a **Configuración** > **Datos Maestros** > **Ubicaciones**
2. Click en **"Nueva Ubicación"**
3. Complete:
   - Nombre (ej. "Planta Principal")
   - Dirección
   - Coordenadas GPS (opcional)
4. Click en **"Guardar"**

#### Categorías de Activos

1. Navegue a **Configuración** > **Datos Maestros** > **Categorías**
2. Click en **"Nueva Categoría"**
3. Complete:
   - Nombre (ej. "Vehículos Pesados")
   - Descripción
   - Código (opcional)
4. Click en **"Guardar"**

#### Tipos de Órdenes de Trabajo

Los tipos predefinidos son:
- **Correctivo**: Reparación de fallas
- **Preventivo**: Mantenimiento programado
- **Predictivo**: Basado en predicciones ML
- **Inspección**: Verificaciones y checklists

Puede agregar tipos personalizados si es necesario.

#### Niveles de Prioridad

Los niveles predefinidos son:
- **Baja**: Puede esperar
- **Media**: Programar pronto
- **Alta**: Atención prioritaria
- **Urgente**: Atención inmediata

### Parámetros del Sistema

#### Configuración de Notificaciones

1. Navegue a **Configuración** > **Notificaciones**
2. Configure:
   - **Email SMTP**: Servidor de correo
   - **Telegram Bot Token**: Token del bot
   - **Plantillas de email**: Personalice mensajes
   - **Frecuencia de notificaciones**: Inmediata, Agrupada, Diaria

#### Configuración de Predicciones ML

1. Navegue a **Configuración** > **Predicciones**
2. Configure:
   - **Umbral de alerta**: Probabilidad mínima para generar alerta (default: 70%)
   - **Días de anticipación**: Cuántos días antes alertar
   - **Frecuencia de predicción**: Diaria, Semanal
   - **Modelo activo**: Versión del modelo ML a usar

#### Configuración de Inventario

1. Navegue a **Configuración** > **Inventario**
2. Configure:
   - **Alertas de stock bajo**: Activar/Desactivar
   - **Porcentaje de alerta**: % del stock mínimo para alertar
   - **Aprobación de ajustes**: Requerir aprobación para ajustes grandes

### Plantillas de Checklist

**Nota:** Las 5 plantillas predefinidas son del sistema y no pueden modificarse.

Para crear plantillas personalizadas:

1. Navegue a **Configuración** > **Checklists**
2. Click en **"Nueva Plantilla"**
3. Complete:
   - Código único
   - Nombre
   - Tipo de vehículo asociado
   - Descripción
4. Agregue ítems:
   - Sección (ej. "Motor", "Frenos")
   - Orden
   - Pregunta
   - Tipo de respuesta: Sí/No/N/A, Numérico, Texto
   - Requerido: Sí/No
   - Permitir observaciones: Sí/No
5. Configure puntaje de aprobación (default: 80%)
6. Click en **"Guardar"**

---

## Mantenimiento del Sistema

### Tareas Diarias

#### Revisar Dashboard de Administración

1. Navegue a **Admin Dashboard**
2. Verifique:
   - ✅ Estado del sistema (verde)
   - ✅ Errores recientes (0 o mínimos)
   - ✅ Uso de recursos (< 80%)
   - ✅ Conexiones de base de datos (normales)

#### Revisar Alertas Críticas

1. Navegue a **Predicciones** > **Alertas**
2. Filtre por severidad: **Crítica**
3. Verifique que todas tengan órdenes de trabajo asociadas
4. Resuelva alertas atendidas

#### Revisar Logs de Seguridad

1. Navegue a **Configuración** > **Logs** > **Seguridad**
2. Busque:
   - Intentos fallidos de login (> 5 del mismo IP)
   - Accesos no autorizados
   - Cambios de permisos
3. Investigue actividad sospechosa

### Tareas Semanales

#### Revisar Reportes de Uso

1. Navegue a **Reportes** > **Uso del Sistema**
2. Revise:
   - Usuarios activos
   - Órdenes de trabajo creadas/completadas
   - Checklists ejecutados
   - Predicciones generadas

#### Actualizar Datos Maestros

1. Revise si hay nuevas ubicaciones, categorías, etc.
2. Actualice según necesidad del negocio

#### Revisar Inventario

1. Navegue a **Inventario**
2. Verifique alertas de stock bajo
3. Coordine reposición con compras

### Tareas Mensuales

#### Revisar Usuarios Inactivos

1. Navegue a **Configuración** > **Usuarios**
2. Filtre por "Último acceso > 30 días"
3. Contacte usuarios inactivos
4. Desactive cuentas si es necesario

#### Revisar Licencias de Operadores

1. Navegue a **Configuración** > **Usuarios** > **Operadores**
2. Filtre por "Licencia vence en < 60 días"
3. Notifique a operadores para renovación

#### Generar Reporte Mensual

1. Navegue a **Reportes** > **Reporte Mensual**
2. Genere reporte con:
   - KPIs del mes
   - Órdenes completadas
   - Downtime de activos
   - Consumo de repuestos
   - Predicciones acertadas
3. Exporte en PDF
4. Envíe a stakeholders

#### Revisar Modelo ML

1. Navegue a **Configuración** > **Predicciones** > **Modelo**
2. Revise métricas:
   - Precisión
   - Recall
   - F1-Score
3. Si la precisión < 80%, considere reentrenamiento

### Tareas Trimestrales

#### Auditoría de Seguridad

1. Ejecute el script de auditoría:
   ```bash
   cd backend
   ./run_security_tests.sh
   ```
2. Revise el reporte generado
3. Corrija vulnerabilidades encontradas

#### Limpieza de Datos

1. Navegue a **Configuración** > **Mantenimiento** > **Limpieza**
2. Revise:
   - Notificaciones antiguas (> 90 días)
   - Logs antiguos (> 90 días)
   - Archivos temporales
3. Click en **"Limpiar Datos Antiguos"**

#### Actualización del Sistema

1. Revise changelog de nuevas versiones
2. Pruebe en ambiente de desarrollo
3. Programe ventana de mantenimiento
4. Ejecute actualización
5. Verifique funcionamiento post-actualización

---

## Monitoreo y Alertas

### Dashboard de Monitoreo

Acceda al dashboard de monitoreo en Google Cloud Console:

1. Navegue a **Cloud Monitoring** > **Dashboards** > **CMMS Dashboard**
2. Revise widgets:
   - Request Rate
   - Error Rate
   - Response Time
   - Instance Count
   - CPU/Memory Usage
   - Database Connections

### Alertas Configuradas

#### Alertas Críticas (Notificación Inmediata)

1. **Service Down**
   - Condición: Health check fallando > 1 minuto
   - Acción: Verificar logs, reiniciar servicio si es necesario

2. **High Error Rate**
   - Condición: Tasa de errores > 10% por 5 minutos
   - Acción: Revisar logs de errores, identificar causa raíz

3. **Database Connection Failure**
   - Condición: No se puede conectar a Cloud SQL
   - Acción: Verificar estado de Cloud SQL, revisar configuración

#### Alertas de Advertencia (Notificación en 15 min)

1. **Slow Response Time**
   - Condición: Tiempo de respuesta > 1s por 5 minutos
   - Acción: Revisar queries lentas, considerar optimización

2. **High CPU Usage**
   - Condición: CPU > 80% por 10 minutos
   - Acción: Revisar procesos, considerar escalar instancias

3. **High Memory Usage**
   - Condición: Memoria > 85% por 10 minutos
   - Acción: Revisar memory leaks, considerar aumentar memoria

### Responder a Alertas

#### Proceso General

1. **Recibir Alerta**
   - Por email, Telegram, o SMS
   - Contiene: Descripción, severidad, timestamp

2. **Evaluar Severidad**
   - Crítica: Atención inmediata
   - Advertencia: Atención en 15-30 minutos
   - Informativa: Revisar en próxima revisión

3. **Investigar**
   - Revisar logs en Cloud Logging
   - Verificar métricas en Cloud Monitoring
   - Identificar causa raíz

4. **Remediar**
   - Aplicar solución
   - Verificar que la alerta se resuelve
   - Documentar en log de incidentes

5. **Post-Mortem** (para incidentes críticos)
   - Documentar qué pasó
   - Por qué pasó
   - Cómo se resolvió
   - Cómo prevenir en el futuro

---

## Respaldo y Recuperación

### Respaldos Automáticos

#### Base de Datos (Cloud SQL)

- **Frecuencia**: Diaria a las 3:00 AM
- **Retención**: 30 días
- **Ubicación**: Multi-región para redundancia

**Verificar Respaldos:**
```bash
gcloud sql backups list --instance=cmms-db
```

#### Archivos (Cloud Storage)

- **Frecuencia**: Continua (versionado habilitado)
- **Retención**: 90 días para versiones antiguas
- **Ubicación**: Multi-región

**Verificar Versionado:**
```bash
gsutil versioning get gs://cmms-documents
```

### Respaldo Manual

#### Antes de Actualizaciones Mayores

1. Crear respaldo manual de base de datos:
   ```bash
   gcloud sql backups create --instance=cmms-db
   ```

2. Exportar configuración:
   ```bash
   python manage.py dumpdata > backup_$(date +%Y%m%d).json
   ```

3. Respaldar archivos críticos:
   ```bash
   gsutil -m cp -r gs://cmms-documents gs://cmms-backups/$(date +%Y%m%d)/
   ```

### Recuperación de Desastres

#### Escenario 1: Pérdida de Datos Recientes

**Restaurar desde respaldo automático:**

1. Listar respaldos disponibles:
   ```bash
   gcloud sql backups list --instance=cmms-db
   ```

2. Restaurar respaldo:
   ```bash
   gcloud sql backups restore BACKUP_ID --backup-instance=cmms-db
   ```

3. Verificar integridad de datos

#### Escenario 2: Corrupción de Base de Datos

1. Detener aplicación:
   ```bash
   gcloud run services update cmms-backend --no-traffic
   ```

2. Crear respaldo del estado actual (por si acaso)

3. Restaurar desde último respaldo bueno conocido

4. Verificar integridad

5. Reactivar aplicación:
   ```bash
   gcloud run services update cmms-backend --traffic=100
   ```

#### Escenario 3: Pérdida Completa de Región

1. Activar instancia de Cloud SQL en región secundaria

2. Actualizar DNS para apuntar a nueva región

3. Desplegar aplicación en nueva región

4. Restaurar datos desde respaldo multi-región

5. Verificar funcionamiento completo

### RTO y RPO

- **RTO** (Recovery Time Objective): 4 horas
- **RPO** (Recovery Point Objective): 24 horas (respaldo diario)

---

## Troubleshooting

### Problemas Comunes

#### Usuarios No Pueden Iniciar Sesión

**Síntomas:**
- Error "Credenciales inválidas"
- Página de login no carga

**Diagnóstico:**
1. Verificar que el usuario existe y está activo
2. Verificar que el servicio de autenticación está funcionando
3. Revisar logs de autenticación

**Solución:**
- Si usuario bloqueado: Desbloquear en admin panel
- Si servicio caído: Reiniciar servicio
- Si problema de red: Verificar conectividad

#### Órdenes de Trabajo No Se Crean

**Síntomas:**
- Error al guardar
- Formulario no responde

**Diagnóstico:**
1. Verificar logs del backend
2. Verificar conexión a base de datos
3. Verificar permisos del usuario

**Solución:**
- Si error de validación: Revisar datos ingresados
- Si error de BD: Verificar Cloud SQL
- Si error de permisos: Verificar rol del usuario

#### Checklists No Generan PDF

**Síntomas:**
- Checklist se guarda pero no hay PDF
- Error al descargar PDF

**Diagnóstico:**
1. Verificar logs del servicio de generación de PDF
2. Verificar acceso a Cloud Storage
3. Verificar plantilla de PDF

**Solución:**
- Si error de generación: Revisar datos del checklist
- Si error de storage: Verificar permisos de Cloud Storage
- Si plantilla corrupta: Restaurar plantilla

#### Predicciones No Se Generan

**Síntomas:**
- No hay predicciones nuevas
- Predicciones con errores

**Diagnóstico:**
1. Verificar que el DAG de ML está corriendo
2. Verificar logs de Vertex AI
3. Verificar datos de entrada

**Solución:**
- Si DAG no corre: Verificar Cloud Composer
- Si modelo no responde: Verificar Vertex AI endpoint
- Si datos insuficientes: Esperar más datos históricos

#### Notificaciones No Llegan

**Síntomas:**
- Usuarios no reciben notificaciones
- Notificaciones retrasadas

**Diagnóstico:**
1. Verificar configuración de Pub/Sub
2. Verificar suscripciones activas
3. Verificar preferencias del usuario

**Solución:**
- Si Pub/Sub caído: Verificar estado del servicio
- Si suscripción inactiva: Reactivar suscripción
- Si preferencias desactivadas: Usuario debe activar

### Logs y Diagnóstico

#### Ver Logs en Tiempo Real

```bash
# Logs del backend
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=cmms-backend"

# Logs de errores solamente
gcloud logging tail "resource.type=cloud_run_revision AND severity>=ERROR"

# Logs de un usuario específico
gcloud logging tail "jsonPayload.user_id=USER_ID"
```

#### Buscar Logs Históricos

```bash
# Últimas 24 horas
gcloud logging read "timestamp>\"$(date -u -d '24 hours ago' '+%Y-%m-%dT%H:%M:%SZ')\"" --limit=100

# Por nivel de severidad
gcloud logging read "severity=ERROR" --limit=50

# Por módulo específico
gcloud logging read "jsonPayload.module=work_orders" --limit=50
```

### Contacto de Soporte

#### Soporte Interno
- Email: soporte-interno@cmms.com
- Slack: #cmms-support

#### Soporte GCP
- Console: https://console.cloud.google.com/support
- Teléfono: Según plan de soporte

---

**Versión del Documento:** 1.0  
**Última Actualización:** 2024-11-13  
**Próxima Revisión:** Trimestral
