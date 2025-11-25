# Arquitectura del Sistema - Capa Gratuita

## 🏗️ Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIOS                                 │
│                    (Navegador Web)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FIREBASE HOSTING                               │
│                   (Frontend - React)                             │
│                   ✅ Free Tier: 10 GB/mes                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API (HTTPS)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CLOUD RUN                                    │
│                  (Backend - Django)                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Instancia: cmms-backend                                 │  │
│  │  CPU: 1 vCPU                                             │  │
│  │  RAM: 512 MB - 1 GB                                      │  │
│  │  Concurrencia: 80 requests                               │  │
│  │  ✅ Free Tier: 2M requests/mes                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cache Local (In-Memory)                                 │  │
│  │  Max Entries: 1000                                       │  │
│  │  Timeout: 5 minutos                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Unix Socket
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD SQL                                     │
│                  (PostgreSQL 14)                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Instancia: cmms-db-free                                 │  │
│  │  Tipo: db-f1-micro                                       │  │
│  │  CPU: 1 vCPU compartida                                  │  │
│  │  RAM: 0.6 GB                                             │  │
│  │  Almacenamiento: 30 GB HDD                               │  │
│  │  Conexiones: Máximo 25                                   │  │
│  │  ✅ Free Tier: 1 instancia                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Backups Automáticos                                     │  │
│  │  Frecuencia: Diaria (03:00 AM)                           │  │
│  │  Retención: 7 días                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ (Opcional)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CLOUD STORAGE                                   │
│              (Archivos y Documentos)                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Bucket: cmms-documents                                  │  │
│  │  Tipo: Standard Storage                                  │  │
│  │  Región: us-central1                                     │  │
│  │  ✅ Free Tier: 5 GB                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Datos

### 1. Solicitud del Usuario
```
Usuario → Firebase Hosting → Cloud Run → Cloud SQL
```

### 2. Respuesta del Servidor
```
Cloud SQL → Cloud Run → Firebase Hosting → Usuario
```

### 3. Carga de Archivos
```
Usuario → Cloud Run → Cloud Storage
```

### 4. Descarga de Archivos
```
Cloud Storage → Cloud Run → Usuario
```

## 📊 Comparación: Antes vs Después

### Arquitectura Anterior (Costosa)

```
┌─────────────────┐
│  Cloud Run      │  $10/mes
│  (2 GB RAM)     │
└────────┬────────┘
         │
         ├─────────┐
         │         │
    ┌────▼────┐  ┌▼──────────┐
    │Cloud SQL│  │Redis      │
    │Standard │  │Memorystore│
    │$50/mes  │  │$30/mes    │
    └─────────┘  └───────────┘

Total: ~$95/mes
```

### Arquitectura Actual (Gratuita)

```
┌─────────────────┐
│  Cloud Run      │  $0/mes ✅
│  (512 MB RAM)   │
└────────┬────────┘
         │
         ├─────────┐
         │         │
    ┌────▼────┐  ┌▼──────────┐
    │Cloud SQL│  │Cache Local│
    │Free Tier│  │In-Memory  │
    │$0/mes ✅│  │$0/mes ✅  │
    └─────────┘  └───────────┘

Total: ~$0/mes 🎉
```

## 🎯 Componentes Clave

### 1. Frontend (Firebase Hosting)
- **Framework**: React + TypeScript
- **Build**: Vite
- **Hosting**: Firebase Hosting
- **CDN**: Global
- **SSL**: Automático
- **Costo**: $0 (< 10 GB/mes)

### 2. Backend (Cloud Run)
- **Framework**: Django 4.2
- **API**: Django REST Framework
- **Autenticación**: JWT
- **Documentación**: drf-spectacular
- **Costo**: $0 (< 2M requests/mes)

### 3. Base de Datos (Cloud SQL)
- **Motor**: PostgreSQL 14
- **Tipo**: db-f1-micro
- **Almacenamiento**: 30 GB HDD
- **Backups**: Automáticos (7 días)
- **Costo**: $0 (Free Tier)

### 4. Cache (Local Memory)
- **Tipo**: Django LocMemCache
- **Capacidad**: 1000 entradas
- **Timeout**: 5 minutos
- **Costo**: $0 (incluido en Cloud Run)

### 5. Almacenamiento (Cloud Storage)
- **Tipo**: Standard Storage
- **Región**: us-central1
- **Uso**: Documentos y archivos
- **Costo**: $0 (< 5 GB)

## 🔐 Seguridad

### Capas de Seguridad

```
┌─────────────────────────────────────────┐
│  1. HTTPS/TLS (Firebase + Cloud Run)   │
├─────────────────────────────────────────┤
│  2. CORS (Orígenes permitidos)         │
├─────────────────────────────────────────┤
│  3. JWT Authentication                  │
├─────────────────────────────────────────┤
│  4. Rate Limiting (60 req/min)         │
├─────────────────────────────────────────┤
│  5. CSRF Protection                     │
├─────────────────────────────────────────┤
│  6. SQL Injection Protection (ORM)     │
├─────────────────────────────────────────┤
│  7. Input Sanitization                  │
├─────────────────────────────────────────┤
│  8. Cloud SQL Private IP               │
└─────────────────────────────────────────┘
```

### Conexión Segura a Base de Datos

```
Cloud Run ──[Unix Socket]──> Cloud SQL
           (Sin IP pública)
```

## 📈 Escalabilidad

### Límites Actuales (Free Tier)

| Recurso | Límite | Uso Recomendado |
|---------|--------|-----------------|
| Usuarios concurrentes | 100 | 50-80 |
| Requests/minuto | 500 | 300-400 |
| Almacenamiento DB | 30 GB | < 25 GB |
| Conexiones DB | 25 | < 20 |
| Archivos | 5 GB | < 4 GB |

### Plan de Escalamiento

#### Fase 1: Optimización (Actual)
```
Costo: $0/mes
Capacidad: 50-100 usuarios
```

#### Fase 2: Básico ($25-50/mes)
```
Cloud SQL: db-g1-small (1.7 GB RAM)
Cloud Run: 1 GB RAM
Capacidad: 100-500 usuarios
```

#### Fase 3: Estándar ($100-150/mes)
```
Cloud SQL: db-n1-standard-1 (3.75 GB RAM)
Cloud Run: 2 GB RAM, múltiples instancias
Redis: Memorystore Basic (1 GB)
Capacidad: 500-2000 usuarios
```

#### Fase 4: Profesional ($300-500/mes)
```
Cloud SQL: db-n1-standard-2 (7.5 GB RAM)
Cloud Run: 4 GB RAM, auto-scaling
Redis: Memorystore Standard (5 GB)
Load Balancer: Cloud Load Balancing
Capacidad: 2000-10000 usuarios
```

## 🔍 Monitoreo

### Métricas Clave

```
┌─────────────────────────────────────────┐
│  Cloud SQL                              │
│  • Conexiones activas                   │
│  • Uso de almacenamiento                │
│  • CPU y memoria                        │
│  • Latencia de queries                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Cloud Run                              │
│  • Requests/segundo                     │
│  • Latencia de respuesta                │
│  • Errores HTTP                         │
│  • Uso de memoria                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Cloud Storage                          │
│  • Espacio usado                        │
│  • Número de archivos                   │
│  • Operaciones/día                      │
└─────────────────────────────────────────┘
```

## 🎓 Mejores Prácticas

### 1. Optimización de Queries
```python
# ✅ Bueno: Usar select_related
Asset.objects.select_related('location', 'asset_type')

# ❌ Malo: N+1 queries
for asset in Asset.objects.all():
    print(asset.location.name)  # Query por cada asset
```

### 2. Cache Estratégico
```python
# Cache de datos que no cambian frecuentemente
@cache_page(60 * 5)  # 5 minutos
def get_asset_types(request):
    return AssetType.objects.all()
```

### 3. Paginación
```python
# Siempre paginar resultados grandes
class AssetViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    page_size = 20
```

### 4. Índices de Base de Datos
```python
class Asset(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['location', 'asset_type']),
        ]
```

## 📝 Checklist de Implementación

- [x] Arquitectura diseñada
- [x] Configuración optimizada
- [x] Documentación creada
- [ ] Instancia Cloud SQL creada
- [ ] Cloud Run actualizado
- [ ] Migraciones ejecutadas
- [ ] Pruebas de carga realizadas
- [ ] Monitoreo configurado
- [ ] Alertas configuradas
- [ ] Backups verificados

## 🎉 Resultado Final

Con esta arquitectura optimizada:

✅ **Costo**: $0/mes (100% gratuito)
✅ **Rendimiento**: Adecuado para 50-100 usuarios
✅ **Escalabilidad**: Preparado para crecer
✅ **Seguridad**: Múltiples capas de protección
✅ **Mantenibilidad**: Fácil de mantener y actualizar

## 📚 Referencias

- [GCP Free Tier](https://cloud.google.com/free)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [Django Performance](https://docs.djangoproject.com/en/4.2/topics/performance/)
