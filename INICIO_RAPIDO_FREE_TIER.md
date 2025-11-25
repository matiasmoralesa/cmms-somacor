# 🚀 Inicio Rápido - Migración a Capa Gratuita

## ⚡ Configuración en 5 Minutos

### Paso 1: Ejecutar Script de Configuración

```powershell
# Ejecutar desde la raíz del proyecto
.\configurar-cloud-sql-free-tier.ps1
```

El script te pedirá:
1. Contraseña para la base de datos (guárdala en un lugar seguro)
2. Confirmación para continuar

### Paso 2: Esperar (5-10 minutos)

El script automáticamente:
- ✅ Crea instancia Cloud SQL (db-f1-micro)
- ✅ Configura base de datos
- ✅ Actualiza Cloud Run
- ✅ Ejecuta migraciones

### Paso 3: Verificar

```powershell
# Ver estado de la instancia
gcloud sql instances describe cmms-db-free

# Ver servicio Cloud Run
gcloud run services describe cmms-backend --region=us-central1
```

### Paso 4: Probar

Accede a tu aplicación:
```
https://cmms-backend-[ID].run.app
```

## 📋 Checklist Rápido

- [ ] Script ejecutado sin errores
- [ ] Instancia Cloud SQL creada
- [ ] Base de datos configurada
- [ ] Cloud Run actualizado
- [ ] Migraciones ejecutadas
- [ ] Aplicación accesible
- [ ] Login funciona
- [ ] Datos se guardan correctamente

## 🎯 Configuración Aplicada

### Base de Datos
```
Tipo: db-f1-micro (Free Tier)
RAM: 0.6 GB
Almacenamiento: 30 GB
Conexiones: Máximo 25
Costo: $0/mes
```

### Cache
```
Tipo: Local Memory
Redis: Eliminado
Costo: $0/mes
```

### Rate Limiting
```
Usuarios: 60 req/min
Anónimos: 10 req/min
Costo: $0/mes
```

## 💰 Ahorro Total

```
Antes: ~$95/mes
Ahora: ~$0/mes
Ahorro: 100% 🎉
```

## 🆘 Problemas Comunes

### Error: "Instance already exists"
**Solución**: El script detectará la instancia existente y continuará con la configuración.

### Error: "Permission denied"
**Solución**: Verifica que tengas permisos de administrador en el proyecto GCP.

### Error: "Service not found"
**Solución**: Asegúrate de que el servicio `cmms-backend` esté desplegado en Cloud Run.

## 📞 Siguiente Paso

Si todo funciona correctamente:

1. **Cargar datos de prueba** (opcional):
   ```powershell
   # Crear job para cargar datos
   gcloud run jobs create cmms-load-data `
     --image=gcr.io/argon-edge-478500-i8/cmms-backend:latest `
     --region=us-central1 `
     --add-cloudsql-instances=argon-edge-478500-i8:us-central1:cmms-db-free `
     --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production" `
     --command=python `
     --args="manage.py,load_demo_data"
   
   # Ejecutar job
   gcloud run jobs execute cmms-load-data --region=us-central1 --wait
   ```

2. **Crear usuario administrador**:
   ```powershell
   # Conectar a Cloud SQL
   gcloud sql connect cmms-db-free --user=postgres --database=cmms_db
   
   # En el prompt de PostgreSQL:
   # Crear superusuario (reemplaza con tus datos)
   ```

3. **Monitorear uso**:
   - Cloud Console > SQL > cmms-db-free
   - Revisar métricas de uso
   - Configurar alertas

## 📚 Documentación Completa

Para más detalles, consulta:
- `CONFIGURACION_CLOUD_SQL_FREE_TIER.md` - Guía completa
- `OPTIMIZACIONES_FREE_TIER.md` - Detalles técnicos
- `RESUMEN_CAMBIOS_FREE_TIER.md` - Resumen de cambios

## ✨ ¡Listo!

Tu aplicación ahora funciona completamente **gratis** en GCP. 🎉
