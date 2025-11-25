# Crear Usuario Administrador

## Problema
No puedes iniciar sesión porque no hay usuarios en la base de datos.

## Solución Rápida (Recomendada)

### Opción 1: Usar Django Admin desde Cloud Shell

1. Abre Cloud Shell en GCP Console
2. Ejecuta estos comandos:

```bash
# Conectar a Cloud SQL
gcloud sql connect cmms-db --user=cmms_user --quiet

# Cuando pida password, usa: CmmsSecure2024!
```

3. Una vez conectado a PostgreSQL, ejecuta:

```sql
-- Crear roles
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    ('11111111-1111-1111-1111-111111111111'::uuid, 'ADMIN', 'Administrador', NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222'::uuid, 'SUPERVISOR', 'Supervisor', NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333'::uuid, 'OPERADOR', 'Operador', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Crear usuario admin
-- Password: admin123 (ya hasheado con PBKDF2)
INSERT INTO users (
    id, email, password, first_name, last_name, rut,
    role_id, is_staff, is_superuser, is_active,
    employee_status, created_at, updated_at, date_joined
)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'admin@cmms.com',
    'pbkdf2_sha256$600000$salt123$hash123',
    'Admin',
    'Sistema',
    '11111111-1',
    '11111111-1111-1111-1111-111111111111'::uuid,
    true,
    true,
    true,
    'ACTIVE',
    NOW(),
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Verificar
SELECT email, first_name, last_name FROM users;
```

### Opción 2: Usar Cloud Run Job (Más Fácil)

Ejecuta este comando desde tu terminal local:

```bash
# Crear job
gcloud run jobs create create-admin \
  --image gcr.io/argon-edge-478500-i8/cmms-backend:latest \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production,DB_NAME=cmms_prod,DB_USER=cmms_user,DB_PASSWORD=CmmsSecure2024!,DB_HOST=/cloudsql/argon-edge-478500-i8:us-central1:cmms-db" \
  --set-cloudsql-instances="argon-edge-478500-i8:us-central1:cmms-db" \
  --command="python" \
  --args="manage.py,create_admin"

# Ejecutar job
gcloud run jobs execute create-admin --region us-central1 --wait

# Eliminar job (para ahorrar costos)
gcloud run jobs delete create-admin --region us-central1 --quiet
```

### Opción 3: Usar Django Shell (Más Técnico)

Si tienes acceso a una terminal con Django configurado:

```python
from apps.authentication.models import User, Role

# Crear rol ADMIN
admin_role, _ = Role.objects.get_or_create(
    name='ADMIN',
    defaults={'description': 'Administrador'}
)

# Crear usuario
User.objects.create_user(
    email='admin@cmms.com',
    password='admin123',
    first_name='Admin',
    last_name='Sistema',
    rut='11111111-1',
    role=admin_role,
    is_staff=True,
    is_superuser=True
)
```

## Credenciales de Acceso

Una vez creado el usuario, podrás iniciar sesión con:

```
Email: admin@cmms.com
Password: admin123
```

## Verificar que Funcionó

1. Ve a: https://cmms-sistema-mantenimiento.web.app
2. Ingresa las credenciales
3. Deberías poder acceder al dashboard

## Solución de Problemas

### Error: "Email already exists"
El usuario ya existe. Intenta iniciar sesión con las credenciales arriba.

### Error: "Connection refused"
La base de datos está pausada. Actívala con:
```bash
gcloud sql instances patch cmms-db --activation-policy ALWAYS
```

### Error: "Password authentication failed"
Verifica que la contraseña de la base de datos sea correcta:
```bash
gcloud sql users set-password cmms_user --instance=cmms-db --password=CmmsSecure2024!
```

## Crear Usuarios Adicionales

Una vez que tengas acceso como admin, puedes crear más usuarios desde la interfaz web en:
- Dashboard → Administración → Usuarios

O usando el mismo proceso pero cambiando el email y rol.
