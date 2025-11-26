# 🚂 Configuración de Base de Datos en Railway

## ❌ Problema Actual
El error `DATABASES setting is not configured` indica que Railway no tiene configurada la base de datos.

## ✅ Solución: Agregar PostgreSQL a Railway

### Paso 1: Agregar PostgreSQL al Proyecto

1. Ve a tu proyecto en Railway: https://railway.app/project/despliebe-encargamiento
2. Haz clic en **"+ New"** (botón superior derecho)
3. Selecciona **"Database"**
4. Elige **"Add PostgreSQL"**
5. Railway creará automáticamente la base de datos

### Paso 2: Conectar el Backend con PostgreSQL

Railway automáticamente creará una variable `DATABASE_URL` que el backend detectará.

**NO necesitas configurar nada manualmente** - Railway vincula automáticamente los servicios.

### Paso 3: Verificar Variables de Entorno

En el servicio `backend`, verifica que existan estas variables:

#### Variables Automáticas (Railway las crea):
- ✅ `DATABASE_URL` - Creada automáticamente al agregar PostgreSQL

#### Variables que DEBES agregar manualmente:

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=tu-secret-key-super-segura-aqui-cambiar
DJANGO_SECRET_KEY=tu-secret-key-super-segura-aqui-cambiar

# Firebase (del archivo JSON que tienes)
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"cmms-somacor-prod",...}
```

### Paso 4: Obtener FIREBASE_CREDENTIALS

Ejecuta este comando para obtener el JSON en una sola línea:

```powershell
# En PowerShell
$json = Get-Content "cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress
Write-Output $json
```

Copia el resultado completo y pégalo como valor de `FIREBASE_CREDENTIALS` en Railway.

### Paso 5: Generar SECRET_KEY

```powershell
# Genera una clave secreta segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Paso 6: Redesplegar

Después de agregar PostgreSQL y las variables:

1. Railway automáticamente redesplega el backend
2. O puedes forzar un redespliegue desde la interfaz

### Paso 7: Ejecutar Migraciones

Una vez que el backend esté corriendo, ejecuta las migraciones:

```powershell
# Obtén la URL de tu backend en Railway (ejemplo)
$BACKEND_URL = "https://tu-backend.railway.app"

# Ejecuta las migraciones
Invoke-WebRequest -Uri "$BACKEND_URL/api/migrate/" -Method POST
```

### Paso 8: Crear Usuario Admin

```powershell
# Crea el usuario administrador
$body = @{
    username = "admin"
    email = "admin@somacor.cl"
    password = "Admin123!"
    first_name = "Administrador"
    last_name = "Sistema"
} | ConvertTo-Json

Invoke-WebRequest -Uri "$BACKEND_URL/api/create-admin/" -Method POST -Body $body -ContentType "application/json"
```

## 📋 Checklist de Configuración

- [ ] PostgreSQL agregado al proyecto Railway
- [ ] Variable `DATABASE_URL` existe (automática)
- [ ] Variable `DJANGO_SETTINGS_MODULE=config.settings.railway`
- [ ] Variable `SECRET_KEY` configurada
- [ ] Variable `DJANGO_SECRET_KEY` configurada
- [ ] Variable `FIREBASE_CREDENTIALS` configurada (JSON completo)
- [ ] Backend redespliegado exitosamente
- [ ] Migraciones ejecutadas
- [ ] Usuario admin creado

## 🔍 Verificar que Todo Funciona

```powershell
# Verifica que el backend responde
Invoke-WebRequest -Uri "https://tu-backend.railway.app/health/"

# Verifica la base de datos
Invoke-WebRequest -Uri "https://tu-backend.railway.app/api/users/"
```

## ⚠️ Notas Importantes

1. **PostgreSQL en Railway es GRATIS** hasta 500MB de almacenamiento
2. Railway vincula automáticamente los servicios - no necesitas copiar URLs manualmente
3. Cada vez que cambies variables de entorno, Railway redesplega automáticamente
4. Las migraciones deben ejecutarse DESPUÉS de que el backend esté corriendo

## 🆘 Si Sigues Teniendo Problemas

Comparte:
1. Screenshot de las variables de entorno en Railway
2. Los últimos logs del despliegue
3. El mensaje de error específico
