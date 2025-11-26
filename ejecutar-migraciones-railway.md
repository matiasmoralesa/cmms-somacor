# 🚀 Ejecutar Migraciones en Railway

## Método Más Simple: Usar la Interfaz de Railway

### Paso 1: Ir a Settings del Servicio

1. Ve a Railway: https://railway.app/project/
2. Haz clic en el servicio **"web"**
3. Ve a la pestaña **"Settings"**

### Paso 2: Modificar el Start Command Temporalmente

1. Baja hasta la sección **"Deploy"**
2. Encuentra **"Custom Start Command"**
3. Cambia el comando actual por este:

```bash
cd backend && python manage.py migrate && python manage.py createsuperuser --noinput --username admin --email admin@somacor.cl && gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
```

4. Haz clic en **"Deploy"** (botón arriba a la derecha)

### Paso 3: Esperar el Redespliegue

Railway redesplega automáticamente (~2 minutos). Las migraciones se ejecutarán durante el inicio.

### Paso 4: Restaurar el Comando Original

Una vez que el despliegue termine exitosamente:

1. Vuelve a **Settings → Deploy → Custom Start Command**
2. Cambia el comando a:

```bash
cd backend && gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
```

3. Haz clic en **"Deploy"** nuevamente

---

## ⚠️ Nota sobre el Superusuario

El comando `createsuperuser --noinput` creará un usuario admin, pero necesitarás establecer la contraseña manualmente después.

### Para establecer la contraseña:

Usa Railway Shell:

```powershell
railway shell
```

Luego dentro del shell:

```bash
cd backend
python manage.py shell
```

Y ejecuta:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('Admin123!')
admin.save()
exit()
```

---

## ✅ Verificación

Una vez completado, verifica que todo funciona:

```powershell
$BACKEND_URL = "https://web-production-bcdff1c0.railway.app"
Invoke-WebRequest -Uri "$BACKEND_URL/admin/"
```

Deberías poder acceder al admin panel en:
https://web-production-bcdff1c0.railway.app/admin/

Con las credenciales:
- **Usuario:** admin
- **Contraseña:** Admin123!
