# ⚡ Inicio Rápido - Despliegue en 30 Minutos

**Sistema**: CMMS  
**Plataforma**: Google Cloud Platform  
**Tiempo**: ~30 minutos  
**Costo**: Gratis (con crédito de $300)

---

## 🎯 Objetivo

Desplegar el sistema CMMS completo en Google Cloud Platform en menos de 30 minutos.

---

## ✅ Pre-requisitos (5 minutos)

### 1. Instalar Google Cloud SDK
```powershell
# Descargar e instalar desde:
Start-Process "https://cloud.google .com/sdk/docs/install#windows"

# Después de instalar, abrir nueva terminal PowerShell y verificar:
gcloud --version
```

### 2. Crear Proyecto GCP
```powershell
# Ir a: https://console.cloud.google.com
# 1. Crear nuevo proyecto
# 2. Habilitar facturación (usa los $300 gratis)
# 3. Anotar el Project ID
```

---

## 🚀 Despliegue Automatizado (25 minutos)

### Paso 1: Autenticarse (2 minutos)
```powershell
# Iniciar sesión en GCP
gcloud auth login

# Esto abrirá tu navegador para autenticarte
```

### Paso 2: Ejecutar Script de Despliegue (20 minutos)
```powershell
# Navegar al directorio de despliegue
cd deployment\gcp

# Ejecutar script automatizado
.\deploy-windows.ps1

# El script te pedirá:
# 1. Project ID (el que creaste)
# 2. Contraseña para la base de datos (elige una segura)
# 3. Confirmación para continuar

# Luego se ejecutará automáticamente:
# ✓ Habilitar APIs (2 min)
# ✓ Crear Cloud SQL (8 min)
# ✓ Crear Storage (1 min)
# ✓ Configurar Pub/Sub (1 min)
# ✓ Desplegar Backend (6 min)
# ✓ Desplegar Frontend (2 min)
```

### Paso 3: Crear Superusuario (3 minutos)
```powershell
# Opción A: Cloud Shell (más fácil)
# 1. Ir a: https://console.cloud.google.com
# 2. Abrir Cloud Shell (icono >_ arriba a la derecha)
# 3. Ejecutar:
gcloud run services proxy cmms-backend --region=us-central1

# En otra terminal de Cloud Shell:
python manage.py createsuperuser
# Email: admin@cmms.com
# Password: (tu contraseña)

# Opción B: Local con Cloud SQL Proxy
# Descargar proxy
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"

# Ejecutar proxy (en una terminal)
.\cloud_sql_proxy.exe -instances=TU-PROYECTO:us-central1:cmms-db=tcp:5432

# En otra terminal
cd ..\..\backend
.\venv\Scripts\Activate.ps1
$env:DB_HOST = "127.0.0.1"
$env:DB_NAME = "cmms_prod"
$env:DB_USER = "cmms_user"
$env:DB_PASSWORD = "TuContraseña"
python manage.py createsuperuser
```

---

## 🎉 ¡Listo!

### URLs de tu Aplicación
Al finalizar el script verás:
```
Backend:  https://cmms-backend-xxx-uc.a.run.app
API Docs: https://cmms-backend-xxx-uc.a.run.app/api/docs/
Frontend: https://tu-proyecto.web.app
```

### Probar el Sistema
1. Abrir la URL del backend en el navegador
2. Ir a `/api/docs/` para ver la documentación interactiva
3. Hacer login con el superusuario que creaste
4. Explorar los endpoints

---

## 📊 Verificación Rápida

### 1. Verificar Backend
```powershell
# Obtener URL del backend
$backendUrl = gcloud run services describe cmms-backend --region=us-central1 --format="value(status.url)"

# Probar health check
Invoke-RestMethod -Uri "$backendUrl/api/v1/core/health/live/"
# Debería retornar: {"status": "alive", "timestamp": ...}
```

### 2. Verificar Base de Datos
```powershell
# Ver instancia
gcloud sql instances describe cmms-db

# Debería mostrar: status: RUNNABLE
```

### 3. Verificar Storage
```powershell
# Listar buckets
gcloud storage buckets list

# Deberías ver 4 buckets: documents, ml-models, reports, backups
```

---

## 💰 Costos

### Configuración Actual (Desarrollo)
- Cloud SQL (db-f1-micro): ~$7/mes
- Cloud Run (auto-scaling): ~$5/mes
- Cloud Storage: ~$0.20/mes
- **Total: ~$12/mes**

### Con Crédito Gratis
- Tienes $300 de crédito
- Duración: ~25 meses gratis
- Después: ~$12/mes

---

## 🔄 Comandos Útiles

### Ver Logs
```powershell
gcloud run services logs tail cmms-backend --region=us-central1
```

### Actualizar Backend
```powershell
cd backend
gcloud run deploy cmms-backend --source . --region=us-central1
```

### Actualizar Frontend
```powershell
cd frontend
npm run build
firebase deploy --only hosting
```

### Ver Costos
```powershell
Start-Process "https://console.cloud.google.com/billing"
```

---

## 🆘 Problemas Comunes

### "gcloud not found"
**Solución**: Cerrar y abrir nueva terminal PowerShell después de instalar SDK

### "Permission denied"
**Solución**: Asegúrate de ser Owner o Editor del proyecto

### "Build failed"
**Solución**: Ver logs con `gcloud builds list` y `gcloud builds log BUILD_ID`

### "Frontend no carga"
**Solución**: 
```powershell
cd frontend
firebase login
firebase init hosting
firebase deploy --only hosting
```

---

## 📚 Documentación Completa

Si necesitas más detalles:
- **Guía Completa**: `GUIA_DESPLIEGUE_WINDOWS.md`
- **Resumen**: `RESUMEN_DESPLIEGUE.md`
- **Script**: `deployment/gcp/deploy-windows.ps1`

---

## ✅ Checklist

- [ ] Google Cloud SDK instalado
- [ ] Proyecto GCP creado
- [ ] Facturación habilitada
- [ ] Script ejecutado exitosamente
- [ ] Superusuario creado
- [ ] Backend accesible
- [ ] Frontend accesible (si configuraste Firebase)

---

## 🎯 Próximos Pasos

1. **Explorar la API**: Ir a `/api/docs/` y probar endpoints
2. **Cargar datos**: Crear activos, órdenes de trabajo, etc.
3. **Configurar dominio**: (Opcional) Usar tu propio dominio
4. **Configurar monitoreo**: Alertas y métricas
5. **Invitar usuarios**: Crear cuentas para tu equipo

---

## 🚀 ¡Comienza Ahora!

```powershell
# 1. Instalar SDK
Start-Process "https://cloud.google.com/sdk/docs/install#windows"

# 2. Después de instalar, abrir nueva terminal
gcloud auth login

# 3. Desplegar
cd deployment\gcp
.\deploy-windows.ps1
```

**Tiempo total: ~30 minutos**  
**Costo: Gratis (con crédito de $300)**  
**Dificultad: Fácil** ⭐⭐☆☆☆

---

¿Preguntas? Revisa `GUIA_DESPLIEGUE_WINDOWS.md` para más detalles.

🎉 **¡Buena suerte con tu despliegue!**
