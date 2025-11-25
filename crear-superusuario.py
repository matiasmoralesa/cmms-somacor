#!/usr/bin/env python
"""
Script para crear superusuario en Django
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ['DATABASE_URL'] = 'postgresql://cmms_user:Santi2005@localhost:5432/cmms_db'
os.environ['GCP_PROJECT_ID'] = 'argon-edge-478500-i8'
os.environ['GCP_STORAGE_BUCKET_NAME'] = 'cmms-storage-argon-edge'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Cambiar al directorio backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()

print("Creando superusuario...")
print("=" * 50)

email = "admin@example.com"
password = "admin123"
first_name = "Admin"
last_name = "User"

# Obtener el rol ADMIN
try:
    admin_role = Role.objects.get(name=Role.ADMIN)
    print(f"✓ Rol ADMIN encontrado")
except Role.DoesNotExist:
    print("❌ Error: El rol ADMIN no existe. Ejecuta primero: python backend/manage.py init_roles_permissions")
    sys.exit(1)

if User.objects.filter(email=email).exists():
    print(f"✓ El usuario {email} ya existe")
    user = User.objects.get(email=email)
    print(f"\nDetalles del usuario:")
    print(f"  Email: {user.email}")
    print(f"  Nombre: {user.first_name} {user.last_name}")
    print(f"  Rol: {user.role.name if user.role else 'Sin rol'}")
    print(f"  Es superusuario: {user.is_superuser}")
    print(f"  Es staff: {user.is_staff}")
else:
    # Crear usuario con rol
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        rut="11111111-1",  # RUT de ejemplo
        role=admin_role,
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    user.set_password(password)
    user.save()
    
    print(f"✓ Superusuario creado exitosamente")
    print(f"\nCredenciales:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Rol: {admin_role.name}")

print("\n" + "=" * 50)
print("✓ Configuración completada")
print("=" * 50)
print("\nPuedes iniciar sesión en:")
print("  https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/login/")
print("\nCon las credenciales:")
print(f"  Email: {email}")
print(f"  Password: {password}")
print("\n⚠️  IMPORTANTE: Cambia estas credenciales en producción")
