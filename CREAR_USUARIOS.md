# 🔐 Crear Usuarios en Producción

## Problema

No puedes iniciar sesión porque no hay usuarios creados en la base de datos de producción.

---

## ✅ Solución Rápida

### Opción 1: Usar el Admin de Django (Recomendado)

1. **Accede al admin de Django:**
   ```
   https://cmms-backend-232652686658.us-central1.run.app/admin/
   ```

2. **Crea un superusuario desde Cloud Shell:**

   ```bash
   # Conectarse al servicio de Cloud Run
   gcloud run services proxy cmms-backend --region us-central1 --project argon-edge-478500-i8
   
   # En otra terminal, ejecutar:
   gcloud run services exec cmms-backend --region us-central1 --project argon-edge-478500-i8 -- python manage.py createsuperuser
   ```

### Opción 2: Usar el Comando de Management (Más Fácil)

He creado un comando que crea usuarios de prueba automáticamente.

**Ejecuta este comando:**

```powershell
# Desplegar el backend con el nuevo comando
cd backend
gcloud run deploy cmms-backend --source . --region us-central1 --quiet

# Ejecutar el comando de management
gcloud run services exec cmms-backend --region us-central1 --project argon-edge-478500-i8 -- python manage.py create_test_users
```

---

## 👥 Usuarios que se Crearán

| Rol | Email | Contraseña |
|-----|-------|------------|
| **Admin** | admin@cmms.com | admin123 |
| **Manager** | manager@cmms.com | manager123 |
| **Technician** | tech@cmms.com | tech123 |
| **Operator** | operator@cmms.com | operator123 |

---

## 🚀 Pasos Detallados

### 1. Desplegar el Backend Actualizado

```powershell
cd backend
gcloud run deploy cmms-backend --source . --region us-central1 --quiet
```

### 2. Ejecutar el Comando de Creación de Usuarios

```powershell
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py create_test_users
```

### 3. Iniciar Sesión

Ve a:
```
https://cmms-somacor-prod.web.app
```

Usa cualquiera de estas credenciales:
- **Email:** admin@cmms.com
- **Contraseña:** admin123

---

## 🔧 Alternativa: Crear Usuario Manualmente

Si prefieres crear un usuario manualmente:

```powershell
# Conectarse al servicio
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py shell

# En el shell de Django:
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()

# Crear superusuario
user = User.objects.create_superuser(
    email='tuusuario@cmms.com',
    password='tucontraseña',
    first_name='Tu',
    last_name='Nombre',
    role=Role.ADMIN
)

print(f"Usuario creado: {user.email}")
```

---

## ⚠️ Nota de Seguridad

**IMPORTANTE:** Estas son credenciales de prueba. En producción real:

1. ✅ Cambia las contraseñas inmediatamente
2. ✅ Usa contraseñas seguras (mínimo 12 caracteres)
3. ✅ Habilita autenticación de dos factores
4. ✅ Elimina usuarios de prueba que no uses

---

## 🔍 Verificar que Funcionó

1. Ve a: https://cmms-somacor-prod.web.app
2. Ingresa: admin@cmms.com / admin123
3. Deberías ver el dashboard

---

## 📝 Comandos Útiles

### Ver usuarios existentes
```powershell
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('\n'.join([f'{u.email} - {u.role}' for u in User.objects.all()]))"
```

### Cambiar contraseña de un usuario
```powershell
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py changepassword admin@cmms.com
```

### Eliminar todos los usuarios de prueba
```powershell
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email__in=['admin@cmms.com', 'manager@cmms.com', 'tech@cmms.com', 'operator@cmms.com']).delete()"
```

---

## ✅ Resumen

1. Despliega el backend actualizado
2. Ejecuta el comando `create_test_users`
3. Inicia sesión con `admin@cmms.com` / `admin123`
4. ¡Listo! Ya puedes usar el sistema

**URL del Sistema:**
```
https://cmms-somacor-prod.web.app
```
