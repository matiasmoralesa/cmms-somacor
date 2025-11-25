# Script para crear superusuario via SQL
# Proyecto: argon-edge-478500-i8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Creando Superusuario via PostgreSQL" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ingresa los datos del superusuario:" -ForegroundColor Yellow
Write-Host ""

$email = Read-Host "Email (ejemplo: admin@cmms.com)"
$password = Read-Host "Password"

Write-Host ""
Write-Host "Generando hash de contraseña Django..." -ForegroundColor Yellow

# Generar hash de contraseña usando Python
$pythonScript = @"
from django.contrib.auth.hashers import make_password
print(make_password('$password'))
"@

# Crear archivo temporal
$pythonScript | Out-File -FilePath "temp_hash.py" -Encoding UTF8

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Ejecuta estos comandos en Cloud Shell:" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Abre Cloud Shell: https://console.cloud.google.com/?cloudshell=true" -ForegroundColor White
Write-Host ""

Write-Host "2. Genera el hash de la contraseña:" -ForegroundColor White
Write-Host ""
Write-Host "python3 << 'EOF'" -ForegroundColor Cyan
Write-Host "from hashlib import pbkdf2_hmac" -ForegroundColor Gray
Write-Host "import base64" -ForegroundColor Gray
Write-Host "import os" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "password = '$password'" -ForegroundColor Gray
Write-Host "salt = base64.b64encode(os.urandom(12)).decode('utf-8')" -ForegroundColor Gray
Write-Host "hash = pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 600000)" -ForegroundColor Gray
Write-Host "hash_b64 = base64.b64encode(hash).decode('utf-8')" -ForegroundColor Gray
Write-Host "print(f'pbkdf2_sha256`$600000`${salt}`${hash_b64}')" -ForegroundColor Gray
Write-Host "EOF" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Copia el hash generado (empieza con pbkdf2_sha256...)" -ForegroundColor White
Write-Host ""

Write-Host "4. Conecta a la base de datos:" -ForegroundColor White
Write-Host ""
Write-Host "gcloud sql connect cmms-db --user=cmms_user --database=cmms_prod --project=argon-edge-478500-i8" -ForegroundColor Cyan
Write-Host ""
Write-Host "Password: CMMS2025Secure" -ForegroundColor Gray
Write-Host ""

Write-Host "5. En PostgreSQL, ejecuta (reemplaza HASH_AQUI con el hash copiado):" -ForegroundColor White
Write-Host ""
Write-Host "INSERT INTO authentication_user (" -ForegroundColor Cyan
Write-Host "    id, password, is_superuser, email, first_name, last_name," -ForegroundColor Cyan
Write-Host "    is_active, is_staff, date_joined" -ForegroundColor Cyan
Write-Host ") VALUES (" -ForegroundColor Cyan
Write-Host "    gen_random_uuid()," -ForegroundColor Cyan
Write-Host "    'HASH_AQUI'," -ForegroundColor Cyan
Write-Host "    true," -ForegroundColor Cyan
Write-Host "    '$email'," -ForegroundColor Cyan
Write-Host "    'Admin'," -ForegroundColor Cyan
Write-Host "    'User'," -ForegroundColor Cyan
Write-Host "    true," -ForegroundColor Cyan
Write-Host "    true," -ForegroundColor Cyan
Write-Host "    NOW()" -ForegroundColor Cyan
Write-Host ");" -ForegroundColor Cyan
Write-Host ""

Write-Host "6. Verificar:" -ForegroundColor White
Write-Host ""
Write-Host "SELECT email, is_superuser FROM authentication_user WHERE email = '$email';" -ForegroundColor Cyan
Write-Host ""

Write-Host "7. Salir:" -ForegroundColor White
Write-Host ""
Write-Host "\q" -ForegroundColor Cyan
Write-Host ""

Write-Host "Presiona Enter para abrir Cloud Shell..." -ForegroundColor Yellow
Read-Host

Start-Process "https://console.cloud.google.com/?cloudshell=true&project=argon-edge-478500-i8"

Write-Host ""
Write-Host "Cloud Shell abierto. Sigue los pasos de arriba." -ForegroundColor Green
Write-Host ""
