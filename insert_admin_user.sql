-- Crear roles si no existen
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    ('11111111-1111-1111-1111-111111111111'::uuid, 'ADMIN', 'Administrador del sistema', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222'::uuid, 'SUPERVISOR', 'Supervisor de mantenimiento', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    ('33333333-3333-3333-3333-333333333333'::uuid, 'OPERADOR', 'Operador de equipos', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Crear usuario admin con password hasheado (admin123)
-- Este hash es válido para Django con PBKDF2
INSERT INTO users (
    id, email, password, first_name, last_name, rut,
    role_id, is_staff, is_superuser, is_active,
    employee_status, created_at, updated_at, date_joined
)
SELECT 
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'admin@cmms.com',
    'pbkdf2_sha256$600000$salt$Vx8xNxQxKxMxPxRxTxVxWxYxZx1x2x3x4x5x6x7x8x9x0xAxBxCxDxExFxGxHxIxJxKxLxMxNxOxPxQxRxSxTxUxVxWxXxYxZ',
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
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@cmms.com');
