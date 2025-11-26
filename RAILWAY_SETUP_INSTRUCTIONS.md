# 🚂 Configuración de Railway - Instrucciones Completas

## ✅ Cambios Aplicados al Proyecto

Se han realizado los siguientes cambios para optimizar el despliegue en Railway:

1. **nixpacks.toml** - Configuración de build para Railway
2. **railway.json** - Configuración de despliegue
3. **backend/start-railway.sh** - Script de inicio optimizado
4. **backend/config/settings/railway.py** - Settings específicos para Railway
5. **backend/requirements-railway.txt** - Dependencias mínimas (sin Google Cloud)

## 📋 Variables de Entorno Requeridas

Configura estas variables en Railway (servicio backend → Variables):

### 1. DJANGO_SETTINGS_MODULE
```
config.settings.railway
```

### 2. SECRET_KEY
Genera una clave secreta ejecutando:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. DJANGO_SECRET_KEY
Usa el mismo valor que SECRET_KEY

### 4. FIREBASE_CREDENTIALS
Copia el contenido completo del archivo `cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json` en UNA SOLA LÍNEA.

Para convertirlo a una línea en PowerShell:
```powershell
$json = Get-Content "cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress
Write-Output $json
```

### 5. RAILWAY_ENVIRONMENT
```
true
```

### 6. DATABASE_URL
Esta variable se crea automáticamente cuando agregas PostgreSQL al proyecto.

## 🗄️ Agregar PostgreSQL

1. En Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway vincula automáticamente la base de datos con tu backend

## 🚀 Proceso de Despliegue

Una vez configuradas las variables:

1. Railway redesplega automáticamente
2. El script `start-railway.sh` se ejecuta:
   - Verifica variables de entorno
   - Ejecuta `collectstatic`
   - Inicia Gunicorn

## ✅ Verificación Post-Despliegue

Después del despliegue exitoso, ejecuta:

```powershell
# Usa el script automatizado
.\verificar-railway-y-migrar.ps1
```

Este script:
- Verifica que el backend esté activo
- Ejecuta las migraciones de base de datos
- Crea el usuario administrador
- Verifica los endpoints de la API

## 🔍 Solución de Problemas

### Error: "DATABASES setting is not configured"
- Verifica que `DATABASE_URL` exista (debe ser automática de PostgreSQL)
- Verifica que `DJANGO_SETTINGS_MODULE=config.settings.railway`

### Error: "No module named 'storages'"
- Verifica que `RAILWAY_ENVIRONMENT=true` esté configurado
- Esto evita que el código intente importar Google Cloud Storage

### Error: "collectstatic failed"
- Verifica que todas las variables de entorno estén configuradas
- Especialmente `DJANGO_SETTINGS_MODULE` y `SECRET_KEY`

### El despliegue tarda mucho
- Es normal que el primer despliegue tarde 3-5 minutos
- Railway instala todas las dependencias desde cero

## 📞 Siguiente Paso

Una vez que el backend esté corriendo:

1. Obtén la URL del backend (Settings → Domains en Railway)
2. Ejecuta `.\verificar-railway-y-migrar.ps1` con esa URL
3. Actualiza el frontend para apuntar a la nueva URL de Railway

## 🎯 Checklist de Configuración

- [ ] PostgreSQL agregado al proyecto
- [ ] Variable `DJANGO_SETTINGS_MODULE` configurada
- [ ] Variable `SECRET_KEY` configurada
- [ ] Variable `DJANGO_SECRET_KEY` configurada
- [ ] Variable `FIREBASE_CREDENTIALS` configurada
- [ ] Variable `RAILWAY_ENVIRONMENT` configurada
- [ ] Variable `DATABASE_URL` existe (automática)
- [ ] Backend desplegado exitosamente
- [ ] Migraciones ejecutadas
- [ ] Usuario admin creado
