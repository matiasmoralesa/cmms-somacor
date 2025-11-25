#!/usr/bin/env python
"""Script para activar el usuario admin"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.authentication.models import User

try:
    user = User.objects.get(email='admin@cmms.com')
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password('admin123')  # Resetear password
    user.save()
    print(f"✓ Usuario {user.email} activado exitosamente")
    print(f"  - is_active: {user.is_active}")
    print(f"  - is_staff: {user.is_staff}")
    print(f"  - is_superuser: {user.is_superuser}")
except User.DoesNotExist:
    print("✗ Usuario admin@cmms.com no existe")
except Exception as e:
    print(f"✗ Error: {e}")
