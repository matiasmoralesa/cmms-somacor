# 🚀 Firebase Authentication - Despliegue a Producción

## Guía Completa de Despliegue

Esta guía te llevará paso a paso para desplegar Firebase Authentication a producción en Google Cloud Run y Firebase Hosting.

---

## 📋 Pre-requisitos

Antes de comenzar, asegúrate de tener:

- [x] Google Cloud SDK instalado y configurado
- [x] Firebase CLI instalado (`npm install -g firebase-tools`)
- [x] Acceso al proyecto GCP: `argon-edge-478500-i8`
- [x] Acceso al proyecto Firebase: `cmms-somacor-prod`
- [x] Credenciales de Firebase descargadas: `cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json`

---

## 🔧 Paso 1: Configurar Firebase Credentials en Secret Manager

Las credenciales de Firebase deben almacenarse de forma segura en Google Cloud Secret Manager:

```powershell
# Crear el secret con las credenciales de Firebase
gcloud secrets create firebase-credentials `
    --data-file=cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json `
    --project=argon-edge-478500-i8

# Dar permisos al servicio de Cloud Run para acceder al secret
gcloud secrets add-iam-policy-binding firebase-credentials `
    --member="serviceAccount:888881509782-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=argon-edge-478500-i8
```

---

## 🐳 Paso 2: Desplegar Backend a Cloud Run

### Opción A: Usando el Script Automatizado (Recomendado)

```powershell
.\deploy_firebase_auth_production.ps1
```

Este script:
- ✅ Configura Firebase credentials en Secret Manager
- ✅ Construye la imagen Docker del backend
- ✅ Despliega a Cloud Run con todas las variables de entorno
- ✅ Construye y despliega el frontend a Firebase Hosting

### Opción B: Despliegue Manual

#### 2.1 Construir la imagen Docker

```powershell
cd backend

gcloud builds submit `
    --tag gcr.io/argon-edge-478500-i8/cmms-backend-service `
    --project=argon-edge-478500-i8
```

#### 2.2 Desplegar a Cloud Run

```powershell
gcloud run deploy cmms-backend-service `
    --image gcr.io/argon-edge-478500-i8/cmms-backend-service `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=config.settings.production" `
    --set-env-vars "ENVIRONMENT=production" `
    --set-env-vars "DEBUG=False" `
    --set-env-vars "GCP_PROJECT_ID=cmms-somacorv2" `
    --set-env-vars "FRONTEND_URL=https://cmms-somacor-prod.web.app" `
    --set-env-vars "CORS_ALLOWED_ORIGINS=https://cmms-somacor-prod.web.app" `
    --set-env-vars "FIREBASE_DATABASE_URL=https://cmms-somacor-prod.firebaseio.com" `
    --set-env-vars "FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com" `
    --set-env-vars "FIREBASE_TOKEN_CACHE_TTL=300" `
    --set-secrets "FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest" `
    --set-secrets "SECRET_KEY=django-secret-key:latest" `
    --set-secrets "DATABASE_URL=database-url:latest" `
    --add-cloudsql-instances argon-edge-478500-i8:us-central1:cmms-db `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --project=argon-edge-478500-i8
```

---

## 🌐 Paso 3: Desplegar Frontend a Firebase Hosting

```powershell
cd frontend

# Construir el frontend con las variables de producción
npm run build

# Desplegar a Firebase Hosting
firebase deploy --only hosting --project cmms-somacor-prod
```

---

## 👥 Paso 4: Migrar Usuarios Existentes

### Opción A: Crear y Ejecutar Cloud Run Job

#### 4.1 Crear el Job

```powershell
cd backend

gcloud builds submit `
    --config cloudbuild-migrate-users.yaml `
    --project=argon-edge-478500-i8
```

#### 4.2 Ejecutar el Job

```powershell
gcloud run jobs execute migrate-users-firebase `
    --region us-central1 `
    --project=argon-edge-478500-i8
```

#### 4.3 Ver los logs

```powershell
gcloud run jobs executions list `
    --job migrate-users-firebase `
    --region us-central1 `
    --project=argon-edge-478500-i8

# Ver logs de una ejecución específica
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-users-firebase" `
    --limit 100 `
    --project=argon-edge-478500-i8
```

### Opción B: Ejecutar Localmente con Conexión a Producción

```powershell
cd backend

# Conectar al Cloud SQL Proxy
.\cloud_sql_proxy.exe -instances=argon-edge-478500-i8:us-central1:cmms-db=tcp:5432

# En otra terminal, ejecutar la migración
$env:FIREBASE_CREDENTIALS_PATH="../cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json"
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
$env:DATABASE_URL="postgresql://postgres:Somacor2024@localhost:5432/cmms_db"

python manage.py migrate_users_to_firebase
```

---

## 📧 Paso 5: Enviar Emails de Recuperación

Después de migrar los usuarios, envía los emails de recuperación de contraseña:

```powershell
# Si usas Cloud Run Job
gcloud run jobs execute send-migration-emails `
    --region us-central1 `
    --project=argon-edge-478500-i8

# Si ejecutas localmente
python manage.py send_migration_emails
```

---

## ⚙️ Paso 6: Configurar Firebase Console

### 6.1 Habilitar Email/Password Authentication

1. Ve a [Firebase Console](https://console.firebase.google.com/project/cmms-somacor-prod/authentication/providers)
2. Habilita "Email/Password"
3. Guarda los cambios

### 6.2 Configurar Dominios Autorizados

1. Ve a [Authentication Settings](https://console.firebase.google.com/project/cmms-somacor-prod/authentication/settings)
2. En "Authorized domains", agrega:
   - `cmms-somacor-prod.web.app`
   - `cmms-somacor-prod.firebaseapp.com`
   - Tu dominio personalizado (si tienes)

### 6.3 Personalizar Email Templates

1. Ve a [Email Templates](https://console.firebase.google.com/project/cmms-somacor-prod/authentication/emails)
2. Personaliza:
   - **Password reset**: Email de recuperación de contraseña
   - **Email verification**: Verificación de email
   - **Email change**: Cambio de email

Ejemplo de plantilla:

```
Asunto: Restablece tu contraseña de CMMS Somacor

Hola,

Recibimos una solicitud para restablecer tu contraseña en CMMS Somacor.

Haz clic en el siguiente enlace para crear una nueva contraseña:
%LINK%

Este enlace expira en 1 hora.

Si no solicitaste este cambio, ignora este correo.

Saludos,
Equipo CMMS Somacor
```

---

## ✅ Paso 7: Verificación Post-Despliegue

### 7.1 Verificar Backend

```powershell
# Obtener URL del backend
$BACKEND_URL = gcloud run services describe cmms-backend-service `
    --region us-central1 `
    --project=argon-edge-478500-i8 `
    --format="value(status.url)"

# Probar endpoint de salud
curl "$BACKEND_URL/api/v1/health/"

# Probar endpoint de autenticación
curl "$BACKEND_URL/api/v1/auth/profile/" `
    -H "Authorization: Bearer <firebase-token>"
```

### 7.2 Verificar Frontend

1. Ve a https://cmms-somacor-prod.web.app
2. Abre las herramientas de desarrollador (F12)
3. Verifica que no haya errores de Firebase
4. Intenta iniciar sesión con un usuario migrado

### 7.3 Verificar Firebase Console

1. Ve a [Firebase Users](https://console.firebase.google.com/project/cmms-somacor-prod/authentication/users)
2. Verifica que los usuarios migrados aparezcan
3. Verifica que los emails sean correctos

---

## 🔍 Monitoreo y Logs

### Ver Logs del Backend

```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cmms-backend-service" `
    --limit 100 `
    --project=argon-edge-478500-i8
```

### Ver Logs de Firebase

1. Ve a [Firebase Console > Authentication > Usage](https://console.firebase.google.com/project/cmms-somacor-prod/authentication/usage)
2. Monitorea:
   - Sign-in attempts
   - Sign-in success rate
   - Active users

### Métricas de Cloud Run

```powershell
# Ver métricas del servicio
gcloud run services describe cmms-backend-service `
    --region us-central1 `
    --project=argon-edge-478500-i8
```

---

## 🆘 Solución de Problemas

### Error: "Firebase credentials not found"

**Solución:**
```powershell
# Verificar que el secret existe
gcloud secrets describe firebase-credentials --project=argon-edge-478500-i8

# Verificar permisos
gcloud secrets get-iam-policy firebase-credentials --project=argon-edge-478500-i8
```

### Error: "Permission denied" en Firebase

**Solución:**
1. Verifica que Email/Password esté habilitado en Firebase Console
2. Verifica que el dominio esté en la lista de dominios autorizados
3. Verifica que el usuario tenga `firebase_uid` en la base de datos

### Error: "CORS policy" en el frontend

**Solución:**
```powershell
# Actualizar CORS en Cloud Run
gcloud run services update cmms-backend-service `
    --set-env-vars "CORS_ALLOWED_ORIGINS=https://cmms-somacor-prod.web.app" `
    --region us-central1 `
    --project=argon-edge-478500-i8
```

### Error: "Database connection failed"

**Solución:**
```powershell
# Verificar que Cloud SQL está conectado
gcloud run services describe cmms-backend-service `
    --region us-central1 `
    --project=argon-edge-478500-i8 `
    --format="value(spec.template.spec.containers[0].env)"
```

---

## 📊 Checklist de Despliegue

- [ ] Firebase credentials configuradas en Secret Manager
- [ ] Backend desplegado a Cloud Run
- [ ] Frontend desplegado a Firebase Hosting
- [ ] Usuarios migrados a Firebase
- [ ] Emails de recuperación enviados
- [ ] Email/Password habilitado en Firebase Console
- [ ] Dominios autorizados configurados
- [ ] Email templates personalizados
- [ ] Backend responde correctamente
- [ ] Frontend carga sin errores
- [ ] Login funciona correctamente
- [ ] Tokens de Firebase se envían en las peticiones
- [ ] Custom claims configurados correctamente
- [ ] Logs monitoreados

---

## 🎯 URLs de Producción

- **Backend API:** https://cmms-backend-service-888881509782.us-central1.run.app/api/v1
- **Frontend:** https://cmms-somacor-prod.web.app
- **Firebase Console:** https://console.firebase.google.com/project/cmms-somacor-prod
- **GCP Console:** https://console.cloud.google.com/run?project=argon-edge-478500-i8

---

## 📚 Documentación Adicional

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Secret Manager Docs](https://cloud.google.com/secret-manager/docs)

---

**¡Despliegue completado!** 🚀

El sistema CMMS ahora usa Firebase Authentication en producción, proporcionando autenticación segura y escalable.
