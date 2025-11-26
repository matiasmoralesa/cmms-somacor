# Pasos Finales para Ejecutar Migraciones

## Estado Actual

- ✅ Backend con endpoint de migraciones creado
- ⏳ Build de Docker en progreso (Build ID: e64be93b-968e-4694-857d-88f5b333551a)
- ⏳ Pendiente: Desplegar nueva versión del backend
- ⏳ Pendiente: Ejecutar migraciones via HTTP

## Pasos a Seguir

### 1. Verificar que el Build Terminó

```powershell
gcloud builds describe e64be93b-968e-4694-857d-88f5b333551a --project=cmms-somacorv2 --format="value(status)"
```

Espera hasta que el status sea `SUCCESS`.

### 2. Desplegar el Backend Actualizado

Una vez que el build termine exitosamente:

```powershell
cd backend
gcloud run deploy cmms-backend-service `
    --image gcr.io/cmms-somacorv2/cmms-backend-service `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=config.settings.production,ENVIRONMENT=production,DEBUG=False,GCP_PROJECT_ID=cmms-somacorv2,FRONTEND_URL=https://cmms-somacor-prod.web.app,CORS_ALLOWED_ORIGINS=https://cmms-somacor-prod.web.app,FIREBASE_DATABASE_URL=https://cmms-somacor-prod.firebaseio.com,FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com,FIREBASE_TOKEN_CACHE_TTL=300" `
    --set-secrets "FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest,SECRET_KEY=django-secret-key:latest,DATABASE_URL=database-url:latest" `
    --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --project=cmms-somacorv2
```

### 3. Ejecutar las Migraciones via HTTP

Una vez desplegado el backend:

```powershell
.\call_migrate_endpoint.ps1
```

O manualmente:

```powershell
curl -X POST https://cmms-backend-service-888881509782.us-central1.run.app/api/v1/core/migrate/
```

### 4. Verificar que las Migraciones Funcionaron

```powershell
# Verificar el health check
curl https://cmms-backend-service-888881509782.us-central1.run.app/api/v1/core/health/
```

### 5. Probar el Login

Una vez que las migraciones estén completas, intenta iniciar sesión en:

https://cmms-somacor-prod.web.app

Con cualquiera de estas credenciales:

- **admin@somacor.cl** / Admin123!
- **supervisor@somacor.cl** / Super123!
- **operador@somacor.cl** / Opera123!

## Archivos Creados

1. `backend/apps/core/views.py` - Endpoint para ejecutar migraciones
2. `backend/apps/core/urls.py` - URLs para core (migrate y health)
3. `backend/apps/core/management/commands/setup_database.py` - Comando de management
4. `call_migrate_endpoint.ps1` - Script para llamar al endpoint

## Endpoints Nuevos

- `POST /api/v1/core/migrate/` - Ejecuta las migraciones de la base de datos
- `GET /api/v1/core/health/` - Health check del servicio

## Notas Importantes

1. El endpoint de migraciones está sin autenticación por ahora para facilitar el setup inicial
2. Una vez que el sistema esté funcionando, considera agregar autenticación al endpoint de migraciones
3. El DATABASE_URL ya está configurado correctamente para usar Cloud SQL

## Troubleshooting

Si las migraciones fallan:

1. Verifica los logs del backend:
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cmms-backend-service" --limit=20 --project=cmms-somacorv2
```

2. Verifica que el DATABASE_URL sea correcto:
```
postgresql://postgres:Somacor2024@/cmms_db?host=/cloudsql/cmms-somacorv2:us-central1:cmms-db
```

3. Verifica que Cloud SQL esté conectado al servicio de Cloud Run

---

**Última Actualización**: 25 de Noviembre de 2025, 20:25
**Build ID**: e64be93b-968e-4694-857d-88f5b333551a
**Estado**: En progreso
