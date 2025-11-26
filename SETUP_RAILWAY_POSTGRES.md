# Configurar PostgreSQL en Railway

## Paso 1: Agregar PostgreSQL a tu Proyecto

1. Ve a tu proyecto en Railway: https://railway.app/project/
2. Click en **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente la base de datos

## Paso 2: Obtener las Variables de Entorno

Railway automáticamente crea estas variables:
- `DATABASE_URL` - URL completa de conexión
- `PGHOST` - Host de la BD
- `PGPORT` - Puerto (5432)
- `PGUSER` - Usuario
- `PGPASSWORD` - Contraseña
- `PGDATABASE` - Nombre de la BD

## Paso 3: Configurar el Backend

Las variables ya están disponibles automáticamente en tu servicio web.
Solo necesitas asegurarte de que `config/settings/railway.py` use `DATABASE_URL`:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

## Paso 4: Redesplegar

Railway automáticamente redesplega cuando detecta la nueva BD.
Las migraciones se ejecutarán automáticamente.

## Costo

- **$5/mes** por la base de datos PostgreSQL
- Incluye:
  - 1GB de storage
  - Backups automáticos
  - Alta disponibilidad
  - Monitoreo

## Ventajas

✅ Configuración en 2 minutos
✅ Variables de entorno automáticas
✅ Backups incluidos
✅ Mismo proveedor que el backend
✅ Baja latencia (mismo datacenter)
✅ Escalable

---

## Alternativa GRATIS: Supabase

Si prefieres algo gratis:

1. Ve a https://supabase.com
2. Crea un proyecto nuevo
3. Copia la connection string
4. Agrégala como variable `DATABASE_URL` en Railway

**Límites del plan gratis:**
- 500MB de storage
- 2GB de transferencia/mes
- Suficiente para desarrollo y pruebas
