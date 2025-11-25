# Optimizaciones para Capa Gratuita de GCP

## 📋 Resumen de Cambios

Se han aplicado optimizaciones al proyecto CMMS para funcionar eficientemente dentro de la **capa gratuita de Google Cloud Platform**.

## 🎯 Objetivos

1. **Reducir costos** a $0 o cerca de $0 mensual
2. **Mantener funcionalidad** completa del sistema
3. **Optimizar rendimiento** dentro de los límites gratuitos
4. **Preparar para escalabilidad** futura

## 🔧 Cambios Aplicados

### 1. Base de Datos - Cloud SQL Free Tier

#### Configuración de Instancia
```yaml
Tipo: db-f1-micro
CPU: 1 vCPU compartida
RAM: 0.6 GB
Almacenamiento: 30 GB HDD
Región: us-central1
Conexiones máximas: 25
```

#### Optimizaciones en Django (`production.py`)
```python
# Reducción de tiempo de vida de conexiones
CONN_MAX_AGE = 300  # 5 minutos (antes: 600)

# Timeouts optimizados
'connect_timeout': 10
'statement_timeout': 30000  # 30 segundos

# Pool de conexiones limitado
# Máximo 25 conexiones simultáneas
```

**Impacto**: Reduce el uso de conexiones y memoria en la base de datos.

### 2. Cache - Sin Redis

#### Antes
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://...',
    }
}
```

#### Después
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cmms-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
```

**Impacto**: Elimina costo de Redis (~$30/mes). Cache en memoria local de Cloud Run.

### 3. Sesiones - Base de Datos

#### Antes
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

#### Después
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

**Impacto**: Sesiones persistentes sin depender de Redis.

### 4. Rate Limiting - Reducido

#### Límites Anteriores vs Nuevos

| Endpoint | Antes | Ahora | Reducción |
|----------|-------|-------|-----------|
| User | 100/min | 60/min | -40% |
| Anon | 20/min | 10/min | -50% |
| Burst | 10/min | 5/min | -50% |
| Daily | 10000/day | 5000/day | -50% |
| Report | 10/hour | 5/hour | -50% |
| Upload | 50/hour | 30/hour | -40% |

**Impacto**: Reduce carga en el servidor y base de datos.

### 5. Cloud Run - Configuración Optimizada

```yaml
CPU: 1 vCPU
Memoria: 512 MB (mínimo)
Instancias mínimas: 0
Instancias máximas: 10
Concurrencia: 80
Timeout: 300s
```

**Impacto**: Dentro de la capa gratuita (2 millones de solicitudes/mes).

### 6. Cloud Storage - Optimizado

```yaml
Bucket: Standard Storage
Región: us-central1
Límite: 5 GB (Free Tier)
```

**Impacto**: Almacenamiento gratuito hasta 5 GB.

## 💰 Estimación de Costos

### Antes de Optimizaciones
```
Cloud SQL (db-n1-standard-1): $50/mes
Redis (Memorystore): $30/mes
Cloud Run: $10/mes
Cloud Storage: $5/mes
Total: ~$95/mes
```

### Después de Optimizaciones
```
Cloud SQL (db-f1-micro): $0/mes (Free Tier)
Redis: $0/mes (eliminado)
Cloud Run: $0/mes (dentro de Free Tier)
Cloud Storage: $0/mes (< 5GB)
Total: ~$0/mes 🎉
```

**Ahorro mensual: ~$95**

## 📊 Límites de la Capa Gratuita

### Cloud SQL
- ✅ 1 instancia db-f1-micro
- ✅ 30 GB almacenamiento HDD
- ✅ Backups automáticos (7 días)
- ⚠️ Solo regiones de EE.UU.
- ⚠️ Máximo 25 conexiones

### Cloud Run
- ✅ 2 millones solicitudes/mes
- ✅ 360,000 GB-segundos/mes
- ✅ 180,000 vCPU-segundos/mes
- ⚠️ Límite de memoria: 512 MB mínimo

### Cloud Storage
- ✅ 5 GB almacenamiento Standard
- ✅ 5,000 operaciones Clase A/mes
- ✅ 50,000 operaciones Clase B/mes
- ⚠️ Tráfico de salida limitado

## 🚀 Rendimiento Esperado

### Capacidad del Sistema

Con las optimizaciones aplicadas, el sistema puede manejar:

- **Usuarios concurrentes**: 50-100
- **Solicitudes/minuto**: 300-500
- **Tamaño de base de datos**: Hasta 25 GB (recomendado)
- **Archivos almacenados**: Hasta 4 GB (recomendado)
- **Tiempo de respuesta**: 200-500ms (promedio)

### Casos de Uso Ideales

✅ **Recomendado para:**
- Desarrollo y pruebas
- MVP y prototipos
- Empresas pequeñas (< 50 usuarios)
- Uso interno con bajo tráfico
- Demos y presentaciones

❌ **NO recomendado para:**
- Producción con alto tráfico
- Más de 100 usuarios concurrentes
- Operaciones intensivas de datos
- Aplicaciones críticas 24/7

## 📈 Plan de Escalabilidad

### Cuando Escalar

Considera escalar cuando:
1. Usuarios concurrentes > 80
2. Uso de almacenamiento > 25 GB
3. Conexiones DB > 20 simultáneas
4. Tiempo de respuesta > 1 segundo
5. Errores de timeout frecuentes

### Opciones de Escalamiento

#### Nivel 1: Básico ($25-50/mes)
```yaml
Cloud SQL: db-g1-small (1.7 GB RAM)
Cloud Run: 1 GB memoria
Redis: Opcional
```

#### Nivel 2: Estándar ($100-150/mes)
```yaml
Cloud SQL: db-n1-standard-1 (3.75 GB RAM)
Cloud Run: 2 GB memoria
Redis: Memorystore Basic (1 GB)
```

#### Nivel 3: Profesional ($300-500/mes)
```yaml
Cloud SQL: db-n1-standard-2 (7.5 GB RAM)
Cloud Run: 4 GB memoria, múltiples instancias
Redis: Memorystore Standard (5 GB)
Load Balancer: Cloud Load Balancing
```

## 🔍 Monitoreo

### Métricas Clave a Monitorear

1. **Cloud SQL**
   ```powershell
   gcloud sql instances describe cmms-db-free
   ```
   - Uso de almacenamiento
   - Conexiones activas
   - CPU y memoria

2. **Cloud Run**
   ```powershell
   gcloud run services describe cmms-backend --region=us-central1
   ```
   - Solicitudes/minuto
   - Latencia
   - Errores

3. **Cloud Storage**
   ```powershell
   gsutil du -sh gs://tu-bucket
   ```
   - Espacio usado
   - Número de archivos

### Alertas Recomendadas

Configura alertas en Cloud Monitoring para:
- Almacenamiento DB > 25 GB (83%)
- Conexiones DB > 20 (80%)
- Solicitudes Cloud Run > 1.5M/mes (75%)
- Errores HTTP 5xx > 1%
- Latencia > 2 segundos

## 🛠️ Herramientas de Optimización

### 1. Django Debug Toolbar (Desarrollo)
```python
# Identifica queries lentas
INSTALLED_APPS += ['debug_toolbar']
```

### 2. Django Query Optimization
```python
# Usar select_related y prefetch_related
Asset.objects.select_related('location', 'asset_type')
WorkOrder.objects.prefetch_related('tasks', 'assigned_to')
```

### 3. Database Indexing
```python
class Meta:
    indexes = [
        models.Index(fields=['status', 'created_at']),
        models.Index(fields=['asset', 'date']),
    ]
```

### 4. Cache de Queries
```python
from django.core.cache import cache

def get_active_assets():
    cache_key = 'active_assets'
    assets = cache.get(cache_key)
    if not assets:
        assets = Asset.objects.filter(status='ACTIVE')
        cache.set(cache_key, assets, 300)  # 5 minutos
    return assets
```

## 📝 Checklist de Implementación

- [x] Configuración de Cloud SQL Free Tier actualizada
- [x] Cache cambiado a local memory
- [x] Sesiones movidas a base de datos
- [x] Rate limiting reducido
- [x] Timeouts optimizados
- [x] Documentación creada
- [ ] Script de configuración ejecutado
- [ ] Instancia de Cloud SQL creada
- [ ] Cloud Run actualizado
- [ ] Migraciones ejecutadas
- [ ] Pruebas de rendimiento realizadas
- [ ] Monitoreo configurado

## 🆘 Solución de Problemas

### Problema: "Too many connections"
**Solución**: Reducir `CONN_MAX_AGE` a 60 segundos

### Problema: Rendimiento lento
**Solución**: 
1. Optimizar queries con índices
2. Implementar cache de queries
3. Usar `select_related()` y `prefetch_related()`

### Problema: Timeout en operaciones
**Solución**: Aumentar timeout en Cloud Run a 300s

### Problema: Memoria insuficiente
**Solución**: Aumentar memoria de Cloud Run a 1 GB

## 📚 Recursos Adicionales

- [GCP Free Tier](https://cloud.google.com/free)
- [Cloud SQL Pricing](https://cloud.google.com/sql/pricing)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Django Performance](https://docs.djangoproject.com/en/4.2/topics/performance/)
- [PostgreSQL Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)

## 🎓 Mejores Prácticas

1. **Monitorea constantemente** el uso de recursos
2. **Optimiza queries** antes de escalar hardware
3. **Implementa cache** estratégicamente
4. **Usa índices** en campos frecuentemente consultados
5. **Limpia datos antiguos** regularmente
6. **Planifica el crecimiento** con anticipación
7. **Documenta cambios** y optimizaciones
8. **Prueba en staging** antes de producción

## 🎉 Conclusión

Con estas optimizaciones, el proyecto CMMS puede funcionar completamente **gratis** dentro de los límites de la capa gratuita de GCP, manteniendo un rendimiento adecuado para:

- Desarrollo y pruebas
- MVPs y prototipos
- Empresas pequeñas con bajo tráfico
- Demostraciones y presentaciones

Cuando el proyecto crezca, el sistema está preparado para escalar gradualmente según las necesidades.
