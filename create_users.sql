-- Crear roles
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    (gen_random_uuid(), 'ADMIN', 'Administrador del sistema', NOW(), NOW()),
    (gen_random_uuid(), 'SUPERVISOR', 'Supervisor de mantenimiento', NOW(), NOW()),
    (gen_random_uuid(), 'OPERADOR', 'Operador de equipos', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Crear usuario admin
-- Password hash para 'admin123' usando Django's PBKDF2
INSERT INTO users (
    id, email, password, first_name, last_name, rut, 
    role_id, is_staff, is_superuser, is_active,
    employee_status, created_at, updated_at, date_joined
)
SELECT 
    gen_random_uuid(),
    'admin@cmms.com',
    'pbkdf2_sha256$600000$salt$hash',  -- Placeholder, necesita ser generado
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
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@cmms.com');
