#!/usr/bin/env python
"""
Script para crear superusuario en Railway
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Datos del superusuario
email = 'admin@somacor.cl'
password = 'Admin123!'
first_name = 'Administrador'
last_name = 'Sistema'
rut = '11111111-1'

# Verificar si el usuario ya existe
if User.objects.filter(email=email).exists():
    print(f"⚠️  El usuario con email '{email}' ya existe.")
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✅ Contraseña actualizada para '{email}'")
else:
    # Crear el superusuario
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        rut=rut
    )
    print(f"✅ Superusuario creado exitosamente!")

print("\n📋 Credenciales:")
print(f"   Email: {email}")
print(f"   Contraseña: {password}")
print(f"\n🌐 Admin Panel: https://web-production-bcdff1c0.railway.app/admin/")
