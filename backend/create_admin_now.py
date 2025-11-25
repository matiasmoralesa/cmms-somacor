#!/usr/bin/env python
"""
Script para crear usuario administrador
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User, Role

print("=== Creando usuario administrador ===\n")

# Verificar si existe el rol ADMIN
try:
    admin_role = Role.objects.get(name='ADMIN')
    print(f"✅ Rol ADMIN encontrado: {admin_role.get_name_display()}")
except Role.DoesNotExist:
    print("❌ Rol ADMIN no existe. Creando...")
    admin_role = Role.objects.create(
        name='ADMIN',
        description='Administrador del sistema con acceso completo'
    )
    print(f"✅ Rol ADMIN creado")

# Verificar si ya existe un usuario admin
admin_email = 'admin@somacor.com'
if User.objects.filter(email=admin_email).exists():
    print(f"\n⚠️  Usuario {admin_email} ya existe")
    user = User.objects.get(email=admin_email)
    print(f"   Nombre: {user.get_full_name()}")
    print(f"   Rol: {user.role.name if user.role else 'Sin rol'}")
    
    # Actualizar contraseña y asegurar que esté activo
    user.set_password('admin123')
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.role = admin_role
    user.save(update_fields=['password', 'is_active', 'is_staff', 'is_superuser', 'role'])
    print(f"✅ Usuario actualizado:")
    print(f"   - Contraseña: admin123")
    print(f"   - Activo: Sí")
    print(f"   - Staff: Sí")
    print(f"   - Superuser: Sí")
    print(f"   - Rol: {user.role.name}")
else:
    # Buscar si existe un usuario con RUT 11111111-1
    existing_user = User.objects.filter(rut='11111111-1').first()
    if existing_user:
        print(f"\n⚠️  Usuario con RUT 11111111-1 ya existe: {existing_user.email}")
        print(f"   Actualizando email a {admin_email}...")
        existing_user.email = admin_email
        existing_user.set_password('admin123')
        existing_user.first_name = 'Admin'
        existing_user.last_name = 'Sistema'
        existing_user.role = admin_role
        existing_user.is_staff = True
        existing_user.is_superuser = True
        existing_user.is_active = True
        existing_user.employee_status = 'ACTIVE'
        existing_user.save()
        user = existing_user
        print(f"✅ Usuario actualizado exitosamente")
    else:
        # Crear usuario admin
        user = User.objects.create_user(
            email=admin_email,
            password='admin123',
            first_name='Admin',
            last_name='Sistema',
            rut='11111111-1',
            role=admin_role,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            employee_status='ACTIVE'
        )
        print(f"\n✅ Usuario administrador creado exitosamente")
    
    print(f"   Email: {user.email}")
    print(f"   Contraseña: admin123")
    print(f"   Nombre: {user.get_full_name()}")
    print(f"   Rol: {user.role.name}")

print("\n=== Proceso completado ===")
print(f"\nPuedes iniciar sesión con:")
print(f"   Email: {admin_email}")
print(f"   Contraseña: admin123")
