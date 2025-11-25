# Configuración de Monitoreo y Alertas

## Descripción General

Este documento describe cómo configurar el monitoreo y las alertas para el sistema CMMS en Google Cloud Platform.

## Componentes de Monitoreo

### 1. Health Checks

El sistema expone tres endpoints de health check:

- **Liveness Probe** (`/api/v1/core/health/live/`): Verifica que el servicio está vivo
- **Readiness Probe** (`/api/v1/core/health/ready/`): Verifica que el servicio está listo para recibir tráfico
- **Full Health Check** (`/api/v1/core/health/`): Verifica todos los componentes del sistema

### 2. Logging Estructurado

El sistema utiliza logging estructurado en formato JSON con los siguientes loggers:

- **audit**: Eventos de auditoría (creación, actualización, eliminación)
- **performance**: Métricas de rendimiento (tiempos de respuesta, queries lentas)
- **security**: Eventos de seguridad (intentos de autenticación, accesos no autorizados)
- **business**: Eventos de negocio (órdenes de trabajo, predicciones, alertas)

### 3. Métricas

El sistema recopila las siguientes métricas:

- Tasa de requests por segundo
- Tiempo de respuesta promedio
- Tasa de errores (4xx, 5xx)
- Conexiones de base de datos activas
- Uso de caché
- Entregas de webhooks exitosas/fallidas

## Configuración en Google Cloud

### Cloud Monitoring

#### 1. Crear Políticas de Alerta

```bash
# Alerta por alta tasa de errores
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'

# Alerta por tiempo de respuesta lento
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Slow Response Time" \
  --condition-display-name="Response time > 1s" \
  --condition-threshold-value=1000 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'

# Alerta por fallo de health check
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Health Check Failed" \
  --condition-display-name="Health check failing" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=60s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/health_check_failures"'
```

#### 2. Configurar Canales de Notificación

```bash
# Email
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=admin@cmms.com

# Telegram (via webhook)
gcloud alpha monitoring channels create \
  --display-name="Telegram Alerts" \
  --type=webhook_tokenauth \
  --channel-labels=url=https://api.telegram.org/bot<TOKEN>/sendMessage
```

### Cloud Logging

#### 1. Crear Log-based Metrics

```bash
# Métrica para errores de autenticación
gcloud logging metrics create authentication_failures \
  --description="Failed authentication attempts" \
  --log-filter='jsonPayload.level="WARNING" AND jsonPayload.logger="security" AND jsonPayload.success=false'

# Métrica para requests lentos
gcloud logging metrics create slow_requests \
  --description="Requests taking more than 1 second" \
  --log-filter='jsonPayload.logger="performance" AND jsonPayload.duration_ms>1000'

# Métrica para actividad sospechosa
gcloud logging metrics create suspicious_activity \
  --description="Suspicious security events" \
  --log-filter='jsonPayload.logger="security" AND jsonPayload.activity_type="suspicious"'
```

#### 2. Configurar Log Sinks

```bash
# Exportar logs a BigQuery para análisis
gcloud logging sinks create cmms-logs-bigquery \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/cmms_logs \
  --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="cmms-backend"'

# Exportar logs de seguridad a Cloud Storage
gcloud logging sinks create cmms-security-logs \
  storage.googleapis.com/cmms-security-logs \
  --log-filter='jsonPayload.logger="security"'
```

### Cloud Run Configuration

#### 1. Configurar Health Checks

En el archivo `service.yaml` de Cloud Run:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: cmms-backend
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/cmms-backend
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/core/health/live/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/v1/core/health/ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
```

#### 2. Configurar Variables de Entorno

```bash
gcloud run services update cmms-backend \
  --set-env-vars="LOG_LEVEL=INFO,ENABLE_MONITORING=true"
```

## Dashboards

### Dashboard de Monitoreo Principal

Crear un dashboard en Cloud Monitoring con los siguientes widgets:

1. **Request Rate**: Requests por segundo
2. **Error Rate**: Porcentaje de errores (4xx, 5xx)
3. **Response Time**: Percentiles p50, p95, p99
4. **Instance Count**: Número de instancias activas
5. **CPU Usage**: Uso de CPU por instancia
6. **Memory Usage**: Uso de memoria por instancia
7. **Database Connections**: Conexiones activas a Cloud SQL
8. **Health Check Status**: Estado de health checks

### Dashboard de Seguridad

1. **Authentication Failures**: Intentos fallidos de autenticación
2. **Authorization Failures**: Accesos denegados
3. **Suspicious Activity**: Actividad sospechosa detectada
4. **API Rate Limit Hits**: Requests bloqueados por rate limiting

### Dashboard de Negocio

1. **Work Orders Created**: Órdenes de trabajo creadas por día
2. **Work Orders Completed**: Órdenes completadas por día
3. **High-Risk Predictions**: Predicciones de alto riesgo
4. **Low Stock Alerts**: Alertas de stock bajo
5. **Webhook Deliveries**: Entregas de webhooks exitosas/fallidas

## Alertas Recomendadas

### Críticas (Notificación Inmediata)

1. **Service Down**: Health check fallando por más de 1 minuto
2. **High Error Rate**: Tasa de errores > 10% por 5 minutos
3. **Database Connection Failure**: No se puede conectar a la base de datos
4. **Critical Security Event**: Múltiples intentos de acceso no autorizado

### Advertencias (Notificación en 15 minutos)

1. **Slow Response Time**: Tiempo de respuesta > 1s por 5 minutos
2. **High CPU Usage**: CPU > 80% por 10 minutos
3. **High Memory Usage**: Memoria > 85% por 10 minutos
4. **Database Connection Pool**: > 80% de conexiones en uso

### Informativas (Notificación Diaria)

1. **Daily Summary**: Resumen de métricas del día
2. **Failed Webhook Deliveries**: Webhooks que fallaron en el día
3. **Slow Queries**: Queries que tomaron > 100ms

## Integración con Telegram

Para recibir alertas en Telegram:

1. Crear un bot de Telegram para alertas
2. Configurar webhook en Cloud Monitoring
3. El sistema enviará alertas críticas automáticamente

Ejemplo de mensaje de alerta:

```
🚨 CRITICAL: High Error Rate

Error rate is 12.5% (threshold: 10.0%)

Details:
- Window: Last 5 minutes
- Total requests: 1000
- Failed requests: 125

Time: 2024-11-13 15:30:00 UTC
```

## Monitoreo de Costos

Configurar alertas de presupuesto en GCP:

```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="CMMS Monthly Budget" \
  --budget-amount=1000USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Mejores Prácticas

1. **Revisar logs regularmente**: Revisar logs de seguridad y errores semanalmente
2. **Ajustar umbrales**: Ajustar umbrales de alertas según patrones reales
3. **Documentar incidentes**: Mantener registro de incidentes y resoluciones
4. **Pruebas de alertas**: Probar alertas mensualmente
5. **Actualizar dashboards**: Mantener dashboards actualizados con métricas relevantes

## Troubleshooting

### Alertas Falsas

Si recibes muchas alertas falsas:
- Aumentar el período de evaluación
- Ajustar umbrales
- Agregar filtros adicionales

### Logs No Aparecen

Verificar:
- Configuración de logging en settings.py
- Permisos de Cloud Logging
- Formato de logs (debe ser JSON)

### Health Checks Fallando

Verificar:
- Conectividad a base de datos
- Configuración de Cloud SQL
- Timeouts de health check

## Contacto

Para soporte con monitoreo:
- Email: ops@cmms.com
- Slack: #cmms-ops
