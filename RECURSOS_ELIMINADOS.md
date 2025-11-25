# Recursos Eliminados de GCP

## Fecha: 18 de Noviembre, 2024

### ✅ Recursos Eliminados

#### Cloud Run Services
- ✅ `cmms-backend` (us-central1)
  - URL anterior: https://cmms-backend-232652686658.us-central1.run.app
  - Estado: ELIMINADO

#### Cloud Run Jobs
- ✅ `cmms-migrate` (us-central1)
- ✅ `load-demo-data` (us-central1)

#### Container Images
- ✅ Todas las imágenes de `cmms-backend` en Artifact Registry
  - Repositorio: us-central1-docker.pkg.dev/argon-edge-478500-i8/cloud-run-source-deploy
  - Aproximadamente 23 imágenes (~6 GB)
  - Estado: ELIMINADAS

### 📋 Recursos que AÚN EXISTEN (No eliminados)

#### Cloud SQL
- ⚠️ `cmms-db` (us-central1-c)
  - Tipo: PostgreSQL 15
  - Tier: db-f1-micro
  - IP: 34.31.236.19
  - Base de datos: cmms_db
  - Usuario: cmms_user
  - **Estado: ACTIVO** (no eliminado)

#### Firebase Hosting
- ⚠️ Frontend desplegado en Firebase
  - URL: https://cmms-somacor-prod.web.app
  - Proyecto: cmms-somacor-prod
  - **Estado: ACTIVO** (no eliminado)

#### Cloud Storage
- ⚠️ Bucket: argon-edge-478500-i8-cmms-documents
  - **Estado: ACTIVO** (no eliminado)

#### Artifact Registry Repositories
- ⚠️ `cloud-run-source-deploy` (us-central1)
  - Repositorio vacío pero aún existe
  - **Estado: ACTIVO** (no eliminado)

### 💰 Ahorro de Costos

Con la eliminación del backend de Cloud Run:
- ✅ Sin cargos por Cloud Run (servicio eliminado)
- ✅ Sin cargos por almacenamiento de imágenes (~6 GB liberados)
- ⚠️ Cloud SQL sigue generando costos (~$10-15/mes)
- ⚠️ Cloud Storage sigue generando costos (según uso)

### 🔄 Para Desplegar en Nueva Cuenta

Cuando estés listo para desplegar en la nueva cuenta, necesitarás:

1. **Configurar nuevo proyecto GCP**
   ```bash
   gcloud config set project NUEVO_PROYECTO_ID
   ```

2. **Crear Cloud SQL** (si es necesario)
   ```bash
   gcloud sql instances create cmms-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

3. **Desplegar backend**
   ```bash
   cd backend
   gcloud run deploy cmms-backend \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --add-cloudsql-instances PROYECTO:REGION:INSTANCIA
   ```

4. **Actualizar frontend** con la nueva URL del backend
   ```bash
   # Actualizar frontend/.env.production
   VITE_API_URL=https://NUEVA_URL_BACKEND/api/v1
   
   # Redesplegar
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

### 📝 Notas Importantes

1. **Base de Datos**: La instancia de Cloud SQL `cmms-db` NO fue eliminada. Si quieres eliminarla:
   ```bash
   gcloud sql instances delete cmms-db
   ```

2. **Datos**: Los datos en la base de datos siguen existiendo. Si necesitas exportarlos antes de eliminar:
   ```bash
   gcloud sql export sql cmms-db gs://BUCKET/backup.sql \
     --database=cmms_db
   ```

3. **Frontend**: El frontend en Firebase sigue activo pero no podrá conectarse al backend eliminado.

4. **Costos**: Revisa los recursos restantes para evitar cargos innecesarios.

### ⚠️ Recursos a Considerar Eliminar

Si no los necesitas en esta cuenta:

```bash
# Eliminar Cloud SQL
gcloud sql instances delete cmms-db

# Eliminar bucket de Storage
gsutil rm -r gs://argon-edge-478500-i8-cmms-documents

# Eliminar repositorio de Artifact Registry
gcloud artifacts repositories delete cloud-run-source-deploy \
  --location=us-central1
```

### ✅ Verificación

Para verificar que el backend fue eliminado:
```bash
# Listar servicios de Cloud Run
gcloud run services list --region us-central1

# Debería mostrar: Listed 0 items.
```

---

**Estado Final:**
- ✅ Backend de Cloud Run: ELIMINADO
- ✅ Jobs de Cloud Run: ELIMINADOS
- ✅ Imágenes de contenedor: ELIMINADAS
- ⚠️ Cloud SQL: ACTIVO (no eliminado)
- ⚠️ Frontend Firebase: ACTIVO (no eliminado)
- ⚠️ Cloud Storage: ACTIVO (no eliminado)
