# 🚂 Guía de Despliegue en Railway.app

## Paso 1: Crear Cuenta en Railway

1. Ve a https://railway.app
2. Haz clic en "Start a New Project"
3. Inicia sesión con GitHub (recomendado) o email
4. Obtendrás **$5 de crédito gratis al mes**

## Paso 2: Crear Repositorio en GitHub

Primero necesitamos subir el código a GitHub:

```bash
# Inicializar git si no está inicializado
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit - CMMS Somacor"

# Crear repositorio en GitHub y conectar
# Ve a https://github.com/new
# Crea un repositorio llamado "cmms-somacor"
# Luego ejecuta:
git remote add origin https://github.com/TU_USUARIO/cmms-somacor.git
git branch -M main
git push -u origin main
```

## Paso 3: Crear Proyecto en Railway

1. En Railway, haz clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Autoriza Railway a acceder a tu GitHub
4. Selecciona el repositorio "cmms-somacor"
5. Railway detectará automáticamente el Dockerfile

## Paso 4: Agregar PostgreSQL

1. En tu proyecto de Railway, haz clic en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la base de datos
4. Copia la variable `DATABASE_URL` que se genera automáticamente

## Paso 5: Configurar Variables de Entorno

En Railway, ve a tu servicio backend y agrega estas variables:

```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=tu-secret-key-aqui-genera-uno-nuevo
DEBUG=False
ALLOWED_HOSTS=*.railway.app
ENVIRONMENT=production

# Database (Railway lo genera automáticamente)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Firebase
FIREBASE_DATABASE_URL=https://cmms-somacor-prod.firebaseio.com
FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com
FIREBASE_TOKEN_CACHE_TTL=300

# CORS
CORS_ALLOWED_ORIGINS=https://cmms-somacor-prod.web.app

# GCP (opcional si usas Gemini)
GCP_PROJECT_ID=cmms-somacor-prod
```

## Paso 6: Agregar Firebase Credentials

Railway no soporta archivos JSON directamente, así que convertiremos las credenciales a string:

```bash
# En tu terminal local
cat cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json | tr -d '\n' | tr -d ' '
```

Copia el resultado y agrégalo como variable de entorno:
```env
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"cmms-somacor-prod",...}
```

## Paso 7: Actualizar Configuración de Django

Necesitamos actualizar `backend/config/settings/production.py` para Railway:

```python
# Agregar al final del archivo
import json

# Railway database
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Firebase credentials desde variable de entorno
if 'FIREBASE_CREDENTIALS' in os.environ:
    FIREBASE_CREDENTIALS = json.loads(os.environ['FIREBASE_CREDENTIALS'])
```

## Paso 8: Ejecutar Migraciones

Una vez desplegado, ejecuta las migraciones:

1. En Railway, ve a tu servicio
2. Haz clic en "Settings" → "Deploy"
3. Agrega un comando de inicio personalizado:

```bash
python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

O ejecuta manualmente desde la terminal de Railway:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Paso 9: Actualizar Frontend

Actualiza la URL del backend en `frontend/.env.production`:

```env
VITE_API_URL=https://tu-app.railway.app
```

Redesplega el frontend en Firebase:
```bash
cd frontend
npm run build
firebase deploy --only hosting
```

## Paso 10: Verificar Despliegue

1. Railway te dará una URL como: `https://cmms-somacor-production.up.railway.app`
2. Verifica el health check: `https://tu-app.railway.app/api/v1/core/health/`
3. Prueba el login desde el frontend

## 🎯 Ventajas de Railway

✅ **$5 gratis al mes** (suficiente para desarrollo)
✅ **PostgreSQL incluido** (500MB gratis)
✅ **Deploy automático** desde GitHub
✅ **SSL gratis** (HTTPS automático)
✅ **Logs en tiempo real**
✅ **Fácil de escalar**
✅ **No requiere tarjeta** inicialmente

## 💰 Costos Después del Crédito Gratis

- **Hobby Plan**: $5/mes (incluye $5 de crédito)
- **PostgreSQL**: Incluido en el plan
- **Bandwidth**: 100GB incluidos
- **Build time**: Ilimitado

## 🔧 Comandos Útiles

### Ver logs
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

### Ejecutar comandos
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## 🆘 Solución de Problemas

### Error de conexión a base de datos
- Verifica que `DATABASE_URL` esté configurado
- Asegúrate de que el formato sea: `postgresql://user:pass@host:port/db`

### Error de Firebase
- Verifica que `FIREBASE_CREDENTIALS` esté en formato JSON válido
- Usa comillas dobles, no simples

### Error 502 Bad Gateway
- Revisa los logs: `railway logs`
- Verifica que el puerto sea `$PORT` (Railway lo asigna automáticamente)

## 📚 Recursos

- Documentación: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

---

**¿Listo para desplegar?** Sigue estos pasos y tendrás tu CMMS funcionando en Railway en menos de 30 minutos! 🚀
