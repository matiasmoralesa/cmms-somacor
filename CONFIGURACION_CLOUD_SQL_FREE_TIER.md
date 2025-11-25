# Configuración de Cloud SQL - Capa Gratuita (Free Tier)

## 📋 Resumen

Este documento explica cómo configurar Cloud SQL en la capa gratuita de GCP para el proyecto CMMS.

## 🆓 Especificaciones de la Capa Gratuita

Google Cloud ofrece una capa gratuita para Cloud SQL con las siguientes características:

### Límites de la Capa Gratuita
- **Tipo de instancia**: `db-f1-micro` (1 vCPU compartida, 0.6 GB RAM)
- **Almacenamiento**: 30 GB de HDD
- **Región**: Solo en regiones de EE.UU. (us-central1, us-east1, us-west1)
- **Conexiones simultáneas**: Máximo 25
- **Backups**: 7 días de retención
- **Base de datos**: PostgreSQL (recomendado) o MySQL

### Costos Adicionales (fuera de la capa gratuita)
- Tráfico de red saliente
- Almacenamiento adicional más allá de 30 GB
- Backups adicionales
- Instancias adicionales

## 🚀 Pasos para Crear la Instancia

### 1. Crear la Instancia de Cloud SQL

```powershell
# Variables de configuración
$PROJECT_ID = "argon-edge-478500-i8"
$INSTANCE_NAME = "cmms-db-free"
$REGION = "us-central1"  # Región gratuita
$DB_VERSION = "POSTGRES_14"

# Crear instancia en capa gratuita
gcloud sql instances create $INSTANCE_NAME `
  --database-version=$DB_VERSION `
  --tier=db-f1-micro `
  --region=$REGION `
  --storage-type=HDD `
  --storage-size=30GB `
  --storage-auto-increase `
  --storage-auto-increase-limit=30 `
  --backup-start-time=03:00 `
  --maintenance-window-day=SUN `
  --maintenance-window-hour=04 `
  --enable-bin-log=false `
  --no-assign-ip `
  --network=default `
  --project=$PROJECT_ID
```

### 2. Configurar la Base de Datos

```powershell
# Crear la base de datos
gcloud sql databases create cmms_db `
  --instance=$INSTANCE_NAME `
  --project=$PROJECT_ID

# Establecer contraseña para el usuario postgres
gcloud sql users set-password postgres `
  --instance=$INSTANCE_NAME `
  --password="TuContraseñaSegura123!" `
  --project=$PROJECT_ID
```

### 3. Configurar Variables de Entorno en Cloud Run

```powershell
# Actualizar el servicio de Cloud Run con las nuevas variables
gcloud run services update cmms-backend `
  --region=us-central1 `
  --add-cloudsql-instances="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}" `
  --set-env-vars="DB_HOST=/cloudsql/${PROJECT_ID}:${REGION}:${INSTANCE_NAME},DB_NAME=cmms_db,DB_USER=postgres,DB_PASSWORD=TuContraseñaSegura123!" `
  --project=$PROJECT_ID
```

## 🔧 Optimizaciones Aplicadas

### 1. Configuración de Django

Las siguientes optimizaciones se han aplicado para la capa gratuita:

#### `backend/config/settings/production.py`
- **Conexiones reducidas**: `CONN_MAX_AGE = 300` (5 minutos)
- **Timeout de conexión**: 10 segundos
- **Statement timeout**: 30 segundos
- **Pool de conexiones**: Optimizado para máximo 25 conexiones

#### `backend/config/settings/base.py`
- **Rate limiting reducido**: Límites más conservadores
- **Cache local**: Sin Redis para evitar costos adicionales
- **Sesiones en DB**: En lugar de cache

### 2. Límites de API (Throttling)

```python
'DEFAULT_THROTTLE_RATES': {
    'user': '60/minute',      # Reducido de 100
    'anon': '10/minute',      # Reducido de 20
    'burst': '5/min',         # Reducido de 10
    'sustained': '60/min',    # Reducido de 100
    'daily': '5000/day',      # Reducido de 10000
    'webhook': '20/hour',     # Reducido de 30
    'report': '5/hour',       # Reducido de 10
    'upload': '30/hour',      # Reducido de 50
    'anon_strict': '3/min',   # Reducido de 5
}
```

## 📊 Monitoreo de Uso

### Verificar Uso de la Instancia

```powershell
# Ver métricas de la instancia
gcloud sql operations list `
  --instance=$INSTANCE_NAME `
  --project=$PROJECT_ID

# Ver uso de almacenamiento
gcloud sql instances describe $INSTANCE_NAME `
  --project=$PROJECT_ID `
  --format="value(settings.dataDiskSizeGb)"
```

### Alertas Recomendadas

Configura alertas para:
- Uso de almacenamiento > 25 GB (83%)
- Conexiones simultáneas > 20 (80%)
- CPU > 80%
- Memoria > 80%

## 🔄 Migración desde Instancia Anterior

Si ya tienes una instancia de Cloud SQL:

### 1. Exportar Datos

```powershell
# Exportar base de datos actual
gcloud sql export sql cmms-db-old `
  gs://tu-bucket/backup-$(Get-Date -Format "yyyyMMdd").sql `
  --database=cmms_db `
  --project=$PROJECT_ID
```

### 2. Importar a Nueva Instancia

```powershell
# Importar a la nueva instancia free tier
gcloud sql import sql $INSTANCE_NAME `
  gs://tu-bucket/backup-$(Get-Date -Format "yyyyMMdd").sql `
  --database=cmms_db `
  --project=$PROJECT_ID
```

## ⚠️ Limitaciones y Consideraciones

### Rendimiento
- **db-f1-micro** es adecuado para:
  - Desarrollo y pruebas
  - Aplicaciones con bajo tráfico (< 100 usuarios concurrentes)
  - Prototipos y MVPs

- **NO recomendado para**:
  - Producción con alto tráfico
  - Operaciones intensivas de base de datos
  - Más de 100 usuarios concurrentes

### Escalabilidad
Si necesitas más recursos:
1. **db-g1-small**: $25/mes (1.7 GB RAM)
2. **db-n1-standard-1**: $50/mes (3.75 GB RAM)
3. **db-n1-standard-2**: $100/mes (7.5 GB RAM)

## 🔐 Seguridad

### Mejores Prácticas
1. **No usar IP pública**: Conectar solo via Unix Socket desde Cloud Run
2. **Contraseñas fuertes**: Mínimo 16 caracteres
3. **Backups automáticos**: Configurados diariamente
4. **SSL/TLS**: Habilitado por defecto
5. **Auditoría**: Revisar logs regularmente

### Configuración de Seguridad

```powershell
# Habilitar logs de auditoría
gcloud sql instances patch $INSTANCE_NAME `
  --database-flags=log_connections=on,log_disconnections=on `
  --project=$PROJECT_ID
```

## 📝 Checklist de Configuración

- [ ] Instancia creada en región us-central1
- [ ] Tipo de instancia: db-f1-micro
- [ ] Almacenamiento: 30 GB HDD
- [ ] Base de datos creada: cmms_db
- [ ] Usuario configurado: postgres
- [ ] Contraseña establecida
- [ ] Cloud Run conectado a la instancia
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] Datos de prueba cargados
- [ ] Backups automáticos habilitados
- [ ] Monitoreo configurado

## 🆘 Solución de Problemas

### Error: "Too many connections"
```python
# Reducir CONN_MAX_AGE en settings
DATABASES['default']['CONN_MAX_AGE'] = 60  # 1 minuto
```

### Error: "Connection timeout"
```python
# Aumentar timeout
DATABASES['default']['OPTIONS']['connect_timeout'] = 30
```

### Rendimiento lento
1. Verificar índices en la base de datos
2. Optimizar queries con `select_related()` y `prefetch_related()`
3. Implementar cache de queries
4. Considerar upgrade a instancia más grande

## 📚 Referencias

- [Cloud SQL Free Tier](https://cloud.google.com/sql/pricing#free-tier)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [Django Database Optimization](https://docs.djangoproject.com/en/4.2/topics/db/optimization/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

## 💡 Consejos Adicionales

1. **Monitorea tu uso**: Revisa regularmente el uso de recursos
2. **Optimiza queries**: Usa Django Debug Toolbar en desarrollo
3. **Implementa cache**: Reduce carga en la base de datos
4. **Backups regulares**: Exporta backups a Cloud Storage
5. **Planifica el crecimiento**: Ten un plan para escalar cuando sea necesario
