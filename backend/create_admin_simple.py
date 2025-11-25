#!/usr/bin/env python
"""Script simple para crear usuario administrador"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Crear o actualizar usuario admin
username = 'admin'
email = 'admin@cmms.com'
password = 'Admin2024!'

try:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Usuario '{username}' creado exitosamente!")
    else:
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'ADMIN'
        user.save()
        print(f"✅ Usuario '{username}' actualizado exitosamente!")
    
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Rol: {user.role}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
