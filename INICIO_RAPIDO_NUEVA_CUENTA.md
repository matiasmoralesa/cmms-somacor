# 🚀 Inicio Rápido - Despliegue en Nueva Cuenta

## Información del Proyecto

- **Cuenta:** lucasgallardo497@gmail.com
- **Project ID:** cmms-somacorv2
- **Región:** us-central1

---

## ⚡ Despliegue Rápido (5 pasos)

### 1️⃣ Autenticarse con la Nueva Cuenta

```powershell
# Autenticar con Google Cloud
gcloud auth login
# Selecciona: lucasgallardo497@gmail.com

# Configurar proyecto
gcloud config set project cmms-somacorv2
```

### 2️⃣ Habilitar APIs

```powershell
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage.googleapis.com
```

### 3️⃣ Crear Cloud SQL

```powershell
# Crear instancia (toma ~5 minutos)
gcloud sql instances create cmms-db `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=TuContraseñaSegura123

# Crear base de datos
gcloud sql databases create cmms_db --instance=cmms-db

# Crear usuario
gcloud sql users create cmms_user `
  --instance=cmms-db `
  --password=TuContraseñaUsuario123
```

### 4️⃣ Desplegar Backend

```powershell
cd backend
.\deploy-nueva-cuenta.ps1
```

El script te pedirá:
- Contraseña del usuario `cmms_user`
- Confirmación para continuar

### 5️⃣ Ejecutar Migraciones y Cargar Datos

```powershell
# Obtener el número de proyecto
$PROJECT_NUMBER = gcloud projects describe cmms-somacorv2 --format="value(projectNumber)"

# Ejecutar migraciones
gcloud run jobs create cmms-migrate `
  --image gcr.io/$PROJECT_NUMBER/cmms-backend `
  --region us-central1 `
  --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production,DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,DB_NAME=cmms_db,DB_USER=cmms_user,DB_PASSWORD=TuContraseñaUsuario123" `
  --command python `
  --args manage.py,migrate `
  --max-retries 0

gcloud run jobs execute cmms-migrate --region us-central1

# Cargar datos de demo
gcloud run jobs create load-demo-data `
  --image gcr.io/$PROJECT_NUMBER/cmms-backend `
  --region us-central1 `
  --add-cloudsql-instances cmms-somacorv2:us-central1:cmms-db `
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production,DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,DB_NAME=cmms_db,DB_USER=cmms_user,DB_PASSWORD=TuContraseñaUsuario123" `
  --command python `
  --args manage.py,load_demo_data `
  --max-retries 0

gcloud run jobs execute load-demo-data --region us-central1
```

---

## 🌐 Desplegar Frontend

### 1. Obtener URL del Backend

```powershell
$BACKEND_URL = gcloud run services describe cmms-backend --region us-central1 --format="value(status.url)"
Write-Host "Backend URL: $BACKEND_URL"
```

### 2. Actualizar Configuración del Frontend

Edita `frontend/.env.production`:

```env
VITE_API_URL=https://TU_URL_BACKEND/api/v1
VITE_APP_NAME=CMMS
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

### 3. Configurar Firebase

```powershell
cd frontend

# Login a Firebase
firebase login

# Crear proyecto en Firebase Console primero:
# https://console.firebase.google.com
# Nombre: cmms-somacorv2

# Inicializar Firebase
firebase init hosting
# Selecciona:
# - Use an existing project: cmms-somacorv2
# - Public directory: dist
# - Single-page app: Yes
```

### 4. Construir y Desplegar

```powershell
# Construir
npm run build

# Desplegar
firebase deploy --only hosting
```

---

## ✅ Verificación

### Backend

```powershell
curl https://TU_URL_BACKEND/api/v1/inventory/spare-parts/health/
```

Deberías ver:
```json
{
  "status": "ok",
  "spare_parts_count": 27,
  "message": "Found 27 spare parts in database"
}
```

### Frontend

Abre: https://cmms-somacorv2.web.app

Credenciales de prueba:
- **Email:** admin@somacor.com
- **Password:** admin123

---

## 📋 Checklist de Despliegue

- [ ] Autenticado con lucasgallardo497@gmail.com
- [ ] Proyecto configurado: cmms-somacorv2
- [ ] APIs habilitadas
- [ ] Cloud SQL creado y configurado
- [ ] Backend desplegado en Cloud Run
- [ ] Migraciones ejecutadas
- [ ] Datos de demo cargados
- [ ] Frontend configurado con URL del backend
- [ ] Frontend desplegado en Firebase
- [ ] Verificación exitosa

---

## 🆘 Problemas Comunes

### "Permission denied"
```powershell
# Verificar cuenta activa
gcloud auth list

# Cambiar cuenta
gcloud config set account lucasgallardo497@gmail.com
```

### "API not enabled"
```powershell
# Habilitar API específica
gcloud services enable NOMBRE_API.googleapis.com
```

### Error de conexión a BD
```powershell
# Verificar instancia
gcloud sql instances describe cmms-db

# Verificar connection name
gcloud sql instances describe cmms-db --format="value(connectionName)"
```

---

## 📚 Documentación Completa

Para más detalles, consulta:
- `DESPLIEGUE_NUEVA_CUENTA.md` - Guía completa paso a paso
- `backend/deploy-nueva-cuenta.ps1` - Script automatizado de despliegue

---

## 💰 Costos Estimados

- Cloud Run: ~$0-5/mes
- Cloud SQL (db-f1-micro): ~$10-15/mes
- Cloud Storage: ~$0.02/GB/mes
- Firebase Hosting: Gratis

**Total:** ~$10-20/mes

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu aplicación CMMS estará funcionando en:

- **Backend:** https://cmms-backend-[PROJECT_NUMBER].us-central1.run.app
- **Frontend:** https://cmms-somacorv2.web.app

¡Disfruta tu aplicación! 🚀
