#!/usr/bin/env python
"""
Script para verificar usuarios en la base de datos
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User

print("=== Usuarios en la base de datos ===\n")

users = User.objects.all()

if not users.exists():
    print("❌ No hay usuarios en la base de datos")
else:
    print(f"✅ Total de usuarios: {users.count()}\n")
    
    for user in users:
        print(f"Email: {user.email}")
        print(f"Nombre: {user.get_full_name()}")
        print(f"Rol: {user.role.name if user.role else 'Sin rol'}")
        print(f"Activo: {'Sí' if user.is_active else 'No'}")
        print(f"Staff: {'Sí' if user.is_staff else 'No'}")
        print(f"Superuser: {'Sí' if user.is_superuser else 'No'}")
        print("-" * 50)
