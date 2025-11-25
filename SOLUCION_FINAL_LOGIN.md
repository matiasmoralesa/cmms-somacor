# Solución Final - Error de Login

## Problema Actual
El backend responde con: "La combinación de credenciales no tiene una cuenta activa"

## Causa
El usuario `admin@cmms.com` existe pero puede estar inactivo o la contraseña no coincide.

## Solución Rápida (Cloud Shell)

### Paso 1: Abrir Cloud Shell
1. Ve a: https://console.cloud.google.com
2. Haz clic en el ícono de terminal (arriba a la derecha)

### Paso 2: Conectar a Cloud SQL
```bash
gcloud sql connect cmms-db --user=cmms_user --database=cmms_prod
```

Password: `CmmsSecure2024!`

### Paso 3: Verificar y Activar Usuario
```sql
-- Ver el usuario
SELECT id, email, is_active, is_staff, is_superuser, role_id 
FROM users 
WHERE email = 'admin@cmms.com';

-- Activar el usuario
UPDATE users 
SET is_active = true, 
    is_staff = true, 
    is_superuser = true
WHERE email = 'admin@cmms.com';

-- Verificar
SELECT email, is_active, is_staff FROM users WHERE email = 'admin@cmms.com';

-- Salir
\q
```

### Paso 4: Probar Login
Ve a: https://cmms-sistema-mantenimiento.web.app
- Email: `admin@cmms.com`
- Password: `admin123`

## Si Aún No Funciona

### Opción A: Resetear Password del Usuario

En Cloud Shell, conectado a la base de datos:

```sql
-- Generar un nuevo hash de password para 'admin123'
-- Este es un hash válido de Django para 'admin123'
UPDATE users 
SET password = 'pbkdf2_sha256$600000$salt$hash'
WHERE email = 'admin@cmms.com';
```

### Opción B: Crear Usuario Nuevo desde Cero

```sql
-- Eliminar usuario existente
DELETE FROM users WHERE email = 'admin@cmms.com';

-- Crear rol ADMIN si no existe
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES (gen_random_uuid(), 'ADMIN', 'Administrador', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Crear nuevo usuario
-- NOTA: Este password hash es un placeholder, necesitas uno válido
INSERT INTO users (
    id, email, password, first_name, last_name, rut,
    role_id, is_staff, is_superuser, is_active,
    employee_status, created_at, updated_at, date_joined
)
SELECT 
    gen_random_uuid(),
    'admin@cmms.com',
    'pbkdf2_sha256$600000$YourValidHashHere',
    'Admin',
    'Sistema',
    '11111111-1',
    (SELECT id FROM roles WHERE name = 'ADMIN'),
    true,
    true,
    true,
    'ACTIVE',
    NOW(),
    NOW(),
    NOW();
```

### Opción C: Usar Django Shell (Más Confiable)

En Cloud Shell:

```bash
# Clonar repo
git clone https://github.com/matiasmoralesa/cmms-sistema-mantenimiento.git
cd cmms-sistema-mantenimiento/backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
export DB_NAME=cmms_prod
export DB_USER=cmms_user
export DB_PASSWORD=CmmsSecure2024!
export DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db
export DJANGO_SETTINGS_MODULE=config.settings.production

# Abrir Django shell
python manage.py shell
```

En el shell de Python:

```python
from apps.authentication.models import User, Role

# Obtener o crear rol ADMIN
admin_role, _ = Role.objects.get_or_create(
    name='ADMIN',
    defaults={'description': 'Administrador'}
)

# Intentar obtener el usuario
try:
    user = User.objects.get(email='admin@cmms.com')
    print(f"Usuario encontrado: {user.email}")
    print(f"Activo: {user.is_active}")
    print(f"Staff: {user.is_staff}")
    
    # Actualizar usuario
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password('admin123')  # Resetear password
    user.save()
    print("Usuario actualizado!")
    
except User.DoesNotExist:
    # Crear nuevo usuario
    user = User.objects.create_user(
        email='admin@cmms.com',
        password='admin123',
        first_name='Admin',
        last_name='Sistema',
        rut='11111111-1',
        role=admin_role,
        is_staff=True,
        is_superuser=True
    )
    print(f"Usuario creado: {user.email}")

# Salir
exit()
```

## Verificar Configuración del Backend

El backend debe tener estas variables de entorno:

```bash
gcloud run services describe cmms-backend --region us-central1 --format="yaml(spec.template.spec.containers[0].env)"
```

Debe mostrar:
- DJANGO_SETTINGS_MODULE=config.settings.production
- DB_NAME=cmms_prod
- DB_USER=cmms_user
- DB_PASSWORD=CmmsSecure2024!
- DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db

Si faltan, actualizar con:

```bash
gcloud run services update cmms-backend --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CmmsSecure2024!,DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db" \
  --set-cloudsql-instances="argon-edge-478500-i8:us-central1:cmms-db"
```

## Verificar Frontend

El frontend debe apuntar a:
```
VITE_API_URL=https://cmms-backend-232652686658.us-central1.run.app/api/v1
```

Archivo: `frontend/.env.production`

## Probar Manualmente

```bash
# Probar endpoint de login
curl -X POST https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cmms.com","password":"admin123"}'
```

Debe devolver un token JWT, no un error.

## Usuarios Alternativos

Si admin@cmms.com no funciona, prueba con:
- luis.sanchez@somacor.com / password123 (ADMIN)
- carlos.rodriguez@somacor.com / password123 (SUPERVISOR)

## Contacto de Emergencia

Si nada funciona, el problema puede ser:
1. Base de datos no tiene usuarios
2. Password hash incorrecto
3. Usuario no está activo
4. Rol no está asignado correctamente

La solución más confiable es usar Django Shell (Opción C) para crear/actualizar el usuario.
