# Script para crear usuario admin en producción

Write-Host "=== Creando Usuario Admin en Producción ===" -ForegroundColor Cyan
Write-Host ""

$pythonCode = @"
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()

if not User.objects.filter(email='admin@cmms.com').exists():
    user = User.objects.create_superuser(
        email='admin@cmms.com',
        password='admin123',
        first_name='Admin',
        last_name='Sistema',
        role=Role.ADMIN
    )
    print(f'Usuario creado: {user.email}')
else:
    print('Usuario ya existe')
"@

# Guardar el código Python en un archivo temporal
$pythonCode | Out-File -FilePath "temp_create_admin.py" -Encoding UTF8

# Ejecutar en Cloud Run
Write-Host "Ejecutando en Cloud Run..." -ForegroundColor Yellow
gcloud run services exec cmms-backend `
  --region us-central1 `
  --project argon-edge-478500-i8 `
  -- python manage.py shell < temp_create_admin.py

# Limpiar archivo temporal
Remove-Item "temp_create_admin.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Credenciales ===" -ForegroundColor Green
Write-Host "Email:    admin@cmms.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Accede en: https://cmms-somacor-prod.web.app" -ForegroundColor Cyan
Write-Host ""
