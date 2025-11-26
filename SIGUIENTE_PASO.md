# 🎯 Siguiente Paso: Subir a GitHub y Desplegar en Railway

## ✅ Lo que ya está listo

- ✅ Código preparado para Railway
- ✅ Configuración de Railway creada
- ✅ Git inicializado y commit realizado
- ✅ Documentación completa

## 📋 Ahora debes hacer esto:

### 1. Crear Repositorio en GitHub (2 minutos)

1. Ve a: **https://github.com/new**
2. Nombre del repositorio: `cmms-somacor`
3. Descripción: `Sistema CMMS para Somacor`
4. Visibilidad: **Private** (recomendado)
5. NO inicialices con README, .gitignore o licencia
6. Haz clic en **"Create repository"**

### 2. Conectar tu Código con GitHub (1 minuto)

Copia y pega estos comandos en tu terminal:

```powershell
git remote add origin https://github.com/TU_USUARIO/cmms-somacor.git
git branch -M main
git push -u origin main
```

**Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub**

### 3. Crear Proyecto en Railway (3 minutos)

1. Ve a: **https://railway.app**
2. Haz clic en **"Start a New Project"**
3. Inicia sesión con tu cuenta de GitHub
4. Selecciona **"Deploy from GitHub repo"**
5. Autoriza Railway a acceder a tu GitHub
6. Selecciona el repositorio **"cmms-somacor"**
7. Railway comenzará a construir automáticamente

### 4. Agregar PostgreSQL (1 minuto)

1. En tu proyecto de Railway, haz clic en **"+ New"**
2. Selecciona **"Database"**
3. Selecciona **"Add PostgreSQL"**
4. Railway creará la base de datos automáticamente
5. La variable `DATABASE_URL` se creará automáticamente

### 5. Configurar Variables de Entorno (5 minutos)

En Railway, ve a tu servicio backend → **Variables** y agrega:

#### Variables Básicas
```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ENVIRONMENT=production
RAILWAY_ENVIRONMENT=true
ALLOWED_HOSTS=*.railway.app
```

#### Secret Key (genera uno nuevo)
```
SECRET_KEY=django-insecure-GENERA-UNO-NUEVO-AQUI
```

Para generar un secret key seguro:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Firebase
```
FIREBASE_DATABASE_URL=https://cmms-somacor-prod.firebaseio.com
FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com
FIREBASE_TOKEN_CACHE_TTL=300
```

#### Firebase Credentials (importante)
Necesitas convertir el archivo JSON a una línea:

```powershell
# En PowerShell
$json = Get-Content cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json -Raw
$json = $json -replace '\s+', ' '
Write-Host $json
```

Copia el resultado y agrégalo como:
```
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"cmms-somacor-prod",...}
```

#### CORS
```
CORS_ALLOWED_ORIGINS=https://cmms-somacor-prod.web.app
```

### 6. Ejecutar Migraciones (2 minutos)

Una vez desplegado, instala Railway CLI:

```powershell
npm install -g @railway/cli
```

Luego ejecuta:

```powershell
railway login
railway link
railway run python manage.py migrate
```

### 7. Crear Superusuario (1 minuto)

```powershell
railway run python manage.py createsuperuser
```

Ingresa:
- Email: admin@somacor.cl
- Contraseña: Admin123! (o la que prefieras)

### 8. Actualizar Frontend (2 minutos)

Edita `frontend/.env.production`:

```env
VITE_API_URL=https://tu-app.railway.app
```

Reemplaza `tu-app.railway.app` con la URL que Railway te dio.

Luego redesplega el frontend:

```powershell
cd frontend
npm run build
firebase deploy --only hosting
```

### 9. Probar el Sistema (1 minuto)

1. Ve a: https://cmms-somacor-prod.web.app
2. Inicia sesión con: admin@somacor.cl / Admin123!
3. ¡Debería funcionar! 🎉

## 🆘 Si Algo Sale Mal

### Ver logs en Railway
```powershell
railway logs
```

### Verificar variables
```powershell
railway variables
```

### Reiniciar servicio
En Railway Dashboard → Settings → Restart

## 📚 Documentación Completa

- **GUIA_RAILWAY.md** - Guía detallada completa
- **RESUMEN_MIGRACION_RAILWAY.md** - Comparación GCP vs Railway

## 💰 Costos

- **Gratis**: $5 de crédito al mes
- **Uso estimado**: $2-3/mes
- **Sobra crédito**: Sí, te alcanza perfectamente

## ⏱️ Tiempo Total Estimado

- GitHub: 2 minutos
- Railway: 3 minutos
- PostgreSQL: 1 minuto
- Variables: 5 minutos
- Migraciones: 2 minutos
- Superusuario: 1 minuto
- Frontend: 2 minutos
- Prueba: 1 minuto

**Total: ~17 minutos** ⚡

---

**¿Listo?** Empieza por el paso 1: Crear el repositorio en GitHub 🚀
