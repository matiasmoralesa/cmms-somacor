-- Crear usuario administrador
-- Contraseña: Admin2024! (hash bcrypt)

INSERT INTO authentication_user (
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined,
    role
) VALUES (
    'pbkdf2_sha256$600000$randomsalt$hashedpassword',
    NULL,
    true,
    'admin',
    'Administrador',
    'Sistema',
    'admin@cmms.com',
    true,
    true,
    NOW(),
    'ADMIN'
) ON CONFLICT (username) DO NOTHING;
