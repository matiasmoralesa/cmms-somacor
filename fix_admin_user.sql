-- Verificar si el usuario existe
SELECT id, email, is_active, is_staff, is_superuser FROM users WHERE email = 'admin@cmms.com';

-- Activar el usuario si existe
UPDATE users 
SET is_active = true, 
    is_staff = true, 
    is_superuser = true
WHERE email = 'admin@cmms.com';

-- Verificar el resultado
SELECT id, email, is_active, is_staff, is_superuser FROM users WHERE email = 'admin@cmms.com';
