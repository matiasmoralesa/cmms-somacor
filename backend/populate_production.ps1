# Script para poblar la base de datos de producción
# ADVERTENCIA: Este script cargará datos de ejemplo a la base de datos de producción

Write-Host "=========================================="  -ForegroundColor Yellow
Write-Host "ADVERTENCIA: Poblando base de datos de PRODUCCIÓN" -ForegroundColor Red
Write-Host "=========================================="  -ForegroundColor Yellow
Write-Host ""

# Solicitar confirmación
$confirmation = Read-Host "¿Estás seguro de que quieres cargar datos de ejemplo a PRODUCCIÓN? (escribe 'SI' para confirmar)"
if ($confirmation -ne "SI") {
    Write-Host "Operación cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Solicitando contraseña de la base de datos..." -ForegroundColor Cyan

# Solicitar la contraseña de la base de datos
$DB_PASSWORD = Read-Host "Ingresa la contraseña del usuario 'cmms_user' de Cloud SQL" -AsSecureString
$DB_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD))

Write-Host ""
Write-Host "Configurando variables de entorno..." -ForegroundColor Cyan

# Configurar variables de entorno para producción
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:DATABASE_URL = "postgresql://cmms_user:${DB_PASSWORD_PLAIN}@34.31.236.19:5432/cmms_prod"
$env:DB_NAME = "cmms_prod"
$env:DB_USER = "cmms_user"
$env:DB_PASSWORD = $DB_PASSWORD_PLAIN
$env:DB_HOST = "34.31.236.19"
$env:DB_PORT = "5432"

Write-Host ""
Write-Host "Ejecutando script de población..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar el script
python populate_data.py

# Limpiar variables sensibles
$env:DB_PASSWORD = ""
$DB_PASSWORD_PLAIN = ""

Write-Host ""
Write-Host "=========================================="  -ForegroundColor Green
Write-Host "Proceso completado" -ForegroundColor Green
Write-Host "=========================================="  -ForegroundColor Green
