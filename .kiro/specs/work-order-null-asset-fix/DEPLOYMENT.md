# Deployment Guide - Work Order Null Asset Fix

## 📋 Resumen

Este documento describe los pasos necesarios para desplegar la solución al problema de assets nulos en órdenes de trabajo.

## 🔧 Cambios Implementados

### Backend
- ✅ Modelo `WorkOrder` actualizado para permitir assets nulos
- ✅ Serializer con métodos seguros para manejar assets nulos
- ✅ Viewset con filtrado por `has_asset` y endpoint `without_asset`
- ✅ Validación de assets requeridos para tipos PREVENTIVE y PREDICTIVE
- ✅ Logging de órdenes sin asset
- ✅ Middleware de monitoreo
- ✅ Migración de base de datos

### Frontend
- ✅ Tipos TypeScript actualizados con campos nullable
- ✅ Funciones helper para acceso seguro a datos
- ✅ Componentes de UI para mostrar assets nulos
- ✅ Hook para filtrado de órdenes
- ✅ Modal de asignación de assets
- ✅ Error boundary para manejo de errores

## 🚀 Pasos de Deployment

### 1. Backup de Base de Datos

```bash
# PostgreSQL
pg_dump -U usuario -d nombre_db > backup_antes_migracion.sql

# SQLite (desarrollo)
cp backend/db.sqlite3 backend/db.sqlite3.backup
```

### 2. Aplicar Migración de Base de Datos

```bash
cd backend
python manage.py migrate work_orders
```

**Nota**: Esta migración cambia el campo `asset` de `NOT NULL` a `NULL`, permitiendo órdenes sin asset.

### 3. Agregar Middleware (Opcional)

Si deseas monitoreo de órdenes sin asset, agrega el middleware en `backend/config/settings/base.py`:

```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'core.monitoring.WorkOrderMonitoringMiddleware',
    'core.monitoring.WorkOrderMetricsMiddleware',
]

# Configuración del threshold de alerta (opcional)
WORK_ORDER_NO_ASSET_THRESHOLD = 30  # Alerta si más del 30% no tienen asset
```

### 4. Reiniciar Servidor Backend

```bash
# Desarrollo
python manage.py runserver

# Producción (Cloud Run se reinicia automáticamente al hacer deploy)
gcloud run deploy cmms-backend --source .
```

### 5. Verificar Frontend

No se requieren cambios de configuración en el frontend. Los archivos TypeScript se compilarán automáticamente.

```bash
cd frontend
npm run build
```

### 6. Deploy Frontend (Firebase Hosting)

```bash
cd frontend
firebase deploy --only hosting
```

## ✅ Verificación Post-Deployment

### 1. Verificar Migración

```bash
python manage.py showmigrations work_orders
```

Deberías ver:
```
work_orders
 [X] 0001_initial
 [X] 0002_make_asset_nullable
```

### 2. Probar API

```bash
# Crear orden sin asset (debería funcionar)
curl -X POST http://localhost:8000/api/v1/work-orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Order",
    "description": "Testing null asset",
    "work_order_type": "CORRECTIVE",
    "priority": "MEDIUM"
  }'

# Filtrar órdenes sin asset
curl http://localhost:8000/api/v1/work-orders/?has_asset=false \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ver estadísticas
curl http://localhost:8000/api/v1/work-orders/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Verificar Logs

```bash
# Buscar logs de órdenes sin asset
tail -f backend/logs/django.log | grep "without asset"
```

### 4. Probar Frontend

1. Abrir la aplicación en el navegador
2. Navegar a la lista de órdenes de trabajo
3. Verificar que no hay errores en la consola
4. Crear una orden sin asset
5. Verificar que se muestra "Sin equipo asignado"
6. Probar el botón "Asignar" en órdenes sin asset

## 🔄 Rollback (Si es necesario)

### Backend

```bash
# Revertir migración
cd backend
python manage.py migrate work_orders 0001_initial

# Restaurar backup
psql -U usuario -d nombre_db < backup_antes_migracion.sql
```

### Frontend

```bash
# Revertir a versión anterior en Firebase
firebase hosting:rollback
```

## 📊 Monitoreo Post-Deployment

### Métricas a Monitorear

1. **Errores de null reference**: Deberían ser 0
2. **Órdenes sin asset**: Porcentaje y tendencia
3. **Tiempo de respuesta API**: No debería aumentar
4. **Logs de advertencia**: Revisar patrones

### Queries Útiles

```sql
-- Contar órdenes sin asset
SELECT COUNT(*) FROM work_orders WHERE asset_id IS NULL;

-- Porcentaje de órdenes sin asset
SELECT 
  COUNT(CASE WHEN asset_id IS NULL THEN 1 END) * 100.0 / COUNT(*) as percentage_without_asset
FROM work_orders;

-- Órdenes sin asset por tipo
SELECT work_order_type, COUNT(*) 
FROM work_orders 
WHERE asset_id IS NULL 
GROUP BY work_order_type;
```

## 🐛 Troubleshooting

### Error: "Cannot read properties of null"

**Causa**: Componente frontend no actualizado
**Solución**: Limpiar caché del navegador y recargar

### Error: "NOT NULL constraint failed"

**Causa**: Migración no aplicada
**Solución**: Ejecutar `python manage.py migrate work_orders`

### Órdenes PREVENTIVE sin asset

**Causa**: Validación no está funcionando
**Solución**: Verificar que el serializer `WorkOrderCreateSerializer` tiene el método `validate()`

## 📞 Soporte

Si encuentras problemas durante el deployment:

1. Revisar logs del backend: `backend/logs/django.log`
2. Revisar consola del navegador (F12)
3. Verificar que la migración se aplicó correctamente
4. Contactar al equipo de desarrollo

## 📝 Notas Adicionales

- **Compatibilidad**: Los cambios son backward compatible
- **Performance**: No hay impacto significativo en performance
- **Datos existentes**: Las órdenes existentes no se ven afectadas
- **Testing**: Se recomienda probar en ambiente de staging primero

## ✨ Mejoras Futuras

- [ ] Dashboard de métricas de assets sin asignar
- [ ] Alertas automáticas por Telegram/Email
- [ ] Reportes semanales de órdenes sin asset
- [ ] Sugerencias automáticas de assets basadas en tipo de orden
