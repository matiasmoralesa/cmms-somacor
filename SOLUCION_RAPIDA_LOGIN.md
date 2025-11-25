# 🚀 Solución Rápida - Crear Usuario para Iniciar Sesión

## Problema
No puedes iniciar sesión porque no hay usuarios en la base de datos.

---

## ✅ Solución Más Simple

### Usar el Admin de Django Directamente

1. **Ve al admin de Django:**
   ```
   https://cmms-backend-232652686658.us-central1.run.app/admin/
   ```

2. **Problema:** No tienes credenciales para el admin

---

## 🔧 Crear Superusuario desde Local

La forma más confiable es crear el superusuario desde tu máquina local conectándote a la base de datos de producción:

### Paso 1: Instalar Cloud SQL Proxy

```powershell
# Descargar Cloud SQL Proxy
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"
```

### Paso 2: Conectarse a la Base de Datos

```powershell
# Iniciar el proxy
.\cloud_sql_proxy.exe argon-edge-478500-i8:us-central1:cmms-db
```

### Paso 3: Configurar Variables de Entorno

En otra terminal PowerShell:

```powershell
$env:DATABASE_URL="postgresql://cmms_user:CMMS2025Secure@127.0.0.1:5432/cmms_prod"
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
```

### Paso 4: Crear Superusuario

```powershell
cd backend
python manage.py createsuperuser
```

Ingresa:
- Email: admin@cmms.com
- Password: admin123 (o la que prefieras)
- First name: Admin
- Last name: Sistema

---

## 🎯 Alternativa Más Rápida - Usar Django Shell

Si ya tienes el proxy corriendo:

```powershell
cd backend
python manage.py shell
```

Luego ejecuta:

```python
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()

# Crear admin
admin = User.objects.create_superuser(
    email='admin@cmms.com',
    password='admin123',
    first_name='Admin',
    last_name='Sistema',
    role=Role.ADMIN
)

print(f"Usuario creado: {admin.email}")
exit()
```

---

## 🌐 Alternativa - Usar Migración de Datos

Voy a crear una migración de datos que cree el usuario automáticamente:

### Archivo: `backend/apps/authentication/migrations/0002_create_initial_admin.py`

```python
from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_initial_admin(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    
    if not User.objects.filter(email='admin@cmms.com').exists():
        User.objects.create(
            email='admin@cmms.com',
            password=make_password('admin123'),
            first_name='Admin',
            last_name='Sistema',
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_admin),
    ]
```

Luego ejecuta:
```powershell
cd backend
python manage.py migrate
```

---

## ✅ Después de Crear el Usuario

1. Ve a: https://cmms-somacor-prod.web.app
2. Ingresa:
   - Email: admin@cmms.com
   - Password: admin123
3. ¡Listo! Deberías ver el dashboard

---

## 📝 Credenciales por Defecto

| Campo | Valor |
|-------|-------|
| Email | admin@cmms.com |
| Password | admin123 |
| Rol | ADMIN |

⚠️ **Importante:** Cambia la contraseña después del primer inicio de sesión

---

## 🆘 Si Aún No Funciona

Contacta con:
- Email: matilqsabe@gmail.com
- Incluye captura de pantalla del error
- Incluye logs de la consola del navegador (F12)

---

**Última actualización:** 18 de Noviembre, 2024
