# 🚀 Despliegue Railway desde Cero - Guía Completa

## 📋 Resumen del Proceso (10 minutos)

1. Crear proyecto en Railway (1 min)
2. Conectar GitHub (1 min)
3. Agregar MySQL (1 min)
4. Configurar variables de entorno (2 min)
5. Desplegar (5 min)
6. Verificar (1 min)

---

## PASO 1: Crear Proyecto en Railway (1 minuto)

1. Ve a: **https://railway.app**
2. Login con tu cuenta
3. Click en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Autoriza Railway a acceder a GitHub (si es necesario)
6. Selecciona tu repositorio: **matiasmoralesa/cmms-somacor**
7. Railway empezará a detectar el proyecto

---

## PASO 2: Configurar el Servicio (2 minutos)

Railway detectará automáticamente que es un proyecto Python/Django.

### 2.1 Configurar Root Directory

1. Click en el servicio que se creó
2. Ve a **Settings**
3. Busca **"Root Directory"**
4. Déjalo vacío o pon: `/`

### 2.2 Configurar Start Command

1. En Settings, busca **"Start Command"**
2. Déjalo vacío (usará el Procfile automáticamente)

O si quieres ser explícito:
```
cd backend && python manage.py migrate && python manage.py create_admin && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

---

## PASO 3: Agregar MySQL (1 minuto)

1. En tu proyecto, click en **"+ New"**
2. Selecciona **"Database"**
3. Click en **"Add MySQL"**
4. Espera 30 segundos

Railway creará automáticamente:
- La base de datos MySQL
- Las variables de entorno
- La conexión con tu backend

---

## PASO 4: Conectar MySQL al Backend (1 minuto)

### Opción A: Automático (Recomendado)

1. Click en el servicio **MySQL**
2. Ve a **"Connect"**
3. Selecciona tu servicio **web**
4. Railway agregará las variables automáticamente

### Opción B: Manual

Si no se conecta automáticamente, ve al servicio web → Variables y verifica que existan:
- `MYSQLHOST`
- `MYSQLPORT`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `MYSQLDATABASE`

---

## PASO 5: Configurar Variables de Entorno (2 minutos)

En tu servicio **web**, ve a **Variables** y agrega:

### Variables Requeridas:

```
DJANGO_SETTINGS_MODULE=config.settings.railway
PORT=8080
```

### Variables de Firebase (si las tienes):

```
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"..."}
```

*(Copia el contenido de tu archivo JSON de Firebase)*

---

## PASO 6: Desplegar (Automático)

Railway desplegará automáticamente cuando:
- Conectes el repositorio
- Agregues la base de datos
- Configures las variables

Verás el progreso en la pestaña **"Deployments"**

---

## PASO 7: Verificar que Funciona (1 minuto)

### 7.1 Ver los Logs

1. Click en tu servicio web
2. Ve a **"Deployments"**
3. Click en el deployment activo
4. Ve a **"View Logs"**

Busca:
```
✅ "Running migrations..."
✅ "Superusuario admin@somacor.cl creado"
✅ "Listening at: http://0.0.0.0:8080"
```

### 7.2 Obtener la URL

1. En tu servicio web, ve a **"Settings"**
2. Busca **"Domains"**
3. Click en **"Generate Domain"**
4. Railway te dará una URL como: `https://web-production-xxxx.railway.app`

### 7.3 Probar la API

Abre en tu navegador:
```
https://tu-url.railway.app/health/
```

Deberías ver: `{"status": "ok"}`

---

## 🎉 ¡Listo!

Tu aplicación está desplegada con:
- ✅ Backend Django en Railway
- ✅ Base de datos MySQL en Railway
- ✅ Variables configuradas
- ✅ URL pública

---

## 🔧 Configuración del Frontend

Ahora actualiza tu frontend para usar la nueva URL:

1. Ve a tu proyecto frontend
2. Actualiza la variable de entorno:
```
VITE_API_URL=https://tu-url.railway.app
```
3. Redesplega el frontend

---

## 💰 Costo

- **Backend:** Incluido en plan gratuito (500 horas/mes)
- **MySQL:** $5/mes
- **Total:** $5/mes

---

## 🆘 Solución de Problemas

### Error: "Application failed to respond"
- Verifica que el puerto sea 8080
- Verifica las variables de entorno
- Revisa los logs

### Error: "Can't connect to MySQL"
- Verifica que MySQL esté conectado al servicio web
- Verifica las variables MYSQL*

### Error: "Module not found"
- Verifica que requirements.txt esté en backend/
- Railway debe instalar desde backend/requirements-railway.txt

---

## 📝 Archivos Importantes

Tu proyecto ya tiene estos archivos configurados:
- ✅ `Procfile` - Comando de inicio
- ✅ `railway.toml` - Configuración Railway
- ✅ `backend/requirements-railway.txt` - Dependencias
- ✅ `backend/config/settings/railway.py` - Settings

---

¡Empecemos con el Paso 1!
