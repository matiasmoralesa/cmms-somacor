#!/bin/bash

# Script simple para crear un usuario admin

echo "Creando usuario admin..."

gcloud run services exec cmms-backend \
  --region us-central1 \
  --project argon-edge-478500-i8 \
  -- python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()

# Crear admin si no existe
if not User.objects.filter(email='admin@cmms.com').exists():
    user = User.objects.create_superuser(
        email='admin@cmms.com',
        password='admin123',
        first_name='Admin',
        last_name='Sistema',
        role=Role.ADMIN
    )
    print(f"✓ Usuario creado: {user.email}")
else:
    print("⚠ Usuario ya existe")
EOF

echo ""
echo "=== Credenciales ==="
echo "Email: admin@cmms.com"
echo "Password: admin123"
echo ""
echo "Accede en: https://cmms-somacor-prod.web.app"
