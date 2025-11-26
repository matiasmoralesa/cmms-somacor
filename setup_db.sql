-- Script para crear base de datos y usuario
CREATE DATABASE IF NOT EXISTS cmms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'cmms_user'@'%' IDENTIFIED BY 'cmms_password_2024';
GRANT ALL PRIVILEGES ON cmms_db.* TO 'cmms_user'@'%';
FLUSH PRIVILEGES;

-- Verificar
SHOW DATABASES LIKE 'cmms_db';
SELECT User, Host FROM mysql.user WHERE User = 'cmms_user';
