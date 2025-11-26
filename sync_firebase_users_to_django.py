#!/usr/bin/env python
"""
Script para sincronizar usuarios de Firebase con Django
"""
import os
import sys
import django
import firebase_admin
from firebase_admin import credentials, auth

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.authentication.models import User, Role

# Initialize Firebase
cred = credentials.Certificate('cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json')
firebase_admin.initialize_app(cred)

def sync_users():
    """Sincronizar usuarios de Firebase con Django"""
    print("=" * 60)
    print("Sincronizando usuarios de Firebase con Django")
    print("=" * 60)
    print()
    
    # Usuarios a sincronizar
    users_to_sync = [
        {
            'email': 'admin@somacor.cl',
            'password': 'Admin123!',
            'role': 'ADMIN',
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'firebase_uid': 'yD9roANaOITWAysyczjmBgMls5f1'
        },
        {
            'email': 'supervisor@somacor.cl',
            'password': 'Super123!',
            'role': 'SUPERVISOR',
            'first_name': 'Supervisor',
            'last_name': 'Sistema',
            'firebase_uid': 'WQisFpxLYGhpYzZS70H4qvDBUq32'
        },
        {
            'email': 'operador@somacor.cl',
            'password': 'Opera123!',
            'role': 'OPERADOR',
            'first_name': 'Operador',
            'last_name': 'Sistema',
            'firebase_uid': 'a0EA2lWbEwXEnItTOFDUvYwX9Tm2'
        }
    ]
    
    for user_data in users_to_sync:
        email = user_data['email']
        print(f"Procesando: {email}")
        print("-" * 60)
        
        try:
            # Verificar si el usuario existe en Firebase
            try:
                firebase_user = auth.get_user_by_email(email)
                print(f"  ✓ Usuario encontrado en Firebase: {firebase_user.uid}")
            except Exception as e:
                print(f"  ✗ Usuario no encontrado en Firebase: {e}")
                continue
            
            # Obtener o crear rol
            role, _ = Role.objects.get_or_create(
                name=user_data['role'],
                defaults={'description': f'Rol {user_data["role"]}'}
            )
            
            # Verificar si el usuario existe en Django
            django_user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': role,
                    'firebase_uid': user_data['firebase_uid'],
                    'is_active': True,
                    'employee_status': 'ACTIVO'
                }
            )
            
            if created:
                # Establecer contraseña
                django_user.set_password(user_data['password'])
                django_user.save()
                print(f"  ✓ Usuario creado en Django")
            else:
                # Actualizar usuario existente
                django_user.first_name = user_data['first_name']
                django_user.last_name = user_data['last_name']
                django_user.role = role
                django_user.firebase_uid = user_data['firebase_uid']
                django_user.is_active = True
                django_user.set_password(user_data['password'])
                django_user.save()
                print(f"  ✓ Usuario actualizado en Django")
            
            print(f"  ✓ ID Django: {django_user.id}")
            print(f"  ✓ Firebase UID: {django_user.firebase_uid}")
            print(f"  ✓ Rol: {django_user.role.name}")
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
            continue
    
    print("=" * 60)
    print("Sincronización completada")
    print("=" * 60)

if __name__ == '__main__':
    sync_users()
