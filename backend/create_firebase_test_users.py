#!/usr/bin/env python
"""
Script para crear usuarios de prueba en Firebase y Django
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.authentication.firebase_user_service import FirebaseUserService
from apps.authentication.firebase_custom_claims import CustomClaimsService
from apps.authentication.models import User

def create_test_users():
    """Create test users in Firebase and Django"""
    
    firebase_service = FirebaseUserService()
    claims_service = CustomClaimsService()
    
    # Test users data
    test_users = [
        {
            'email': 'admin@somacor.cl',
            'password': 'Admin123!',
            'full_name': 'Administrador Sistema',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'rut': '11111111-1',
            'role': 'ADMIN',
            'phone': '+56912345678'
        },
        {
            'email': 'supervisor@somacor.cl',
            'password': 'Super123!',
            'full_name': 'Supervisor Mantenimiento',
            'first_name': 'Supervisor',
            'last_name': 'Mantenimiento',
            'rut': '22222222-2',
            'role': 'SUPERVISOR',
            'phone': '+56987654321'
        },
        {
            'email': 'operador@somacor.cl',
            'password': 'Opera123!',
            'full_name': 'Operador Campo',
            'first_name': 'Operador',
            'last_name': 'Campo',
            'rut': '33333333-3',
            'role': 'OPERADOR',
            'phone': '+56911111111'
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            print(f"\n{'='*60}")
            print(f"Creando usuario: {user_data['email']}")
            print(f"Rol: {user_data['role']}")
            print(f"{'='*60}")
            
            # Check if user already exists in Django
            django_user = User.objects.filter(email=user_data['email']).first()
            
            if django_user:
                print(f"✓ Usuario ya existe en Django: {django_user.email}")
                
                # Check if has firebase_uid
                if not django_user.firebase_uid:
                    print("  Creando usuario en Firebase...")
                    # Create in Firebase
                    firebase_user = firebase_service.create_user(
                        email=user_data['email'],
                        password=user_data['password'],
                        display_name=user_data['full_name']
                    )
                    
                    # Update Django user with firebase_uid
                    django_user.firebase_uid = firebase_user.uid
                    django_user.save()
                    print(f"  ✓ Firebase UID asignado: {firebase_user.uid}")
                else:
                    print(f"  ✓ Ya tiene Firebase UID: {django_user.firebase_uid}")
                    firebase_user = firebase_service.get_user_by_uid(django_user.firebase_uid)
                
            else:
                print("  Creando usuario en Firebase...")
                # Create in Firebase
                firebase_user = firebase_service.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    display_name=user_data['full_name']
                )
                print(f"  ✓ Usuario creado en Firebase: {firebase_user.uid}")
                
                # Create in Django
                print("  Creando usuario en Django...")
                django_user = User.objects.create(
                    email=user_data['email'],
                    firebase_uid=firebase_user.uid,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    rut=user_data['rut'],
                    phone=user_data.get('phone'),
                    role=user_data['role'],
                    employee_status='ACTIVE',
                    is_active=True
                )
                print(f"  ✓ Usuario creado en Django: {django_user.id}")
            
            # Set custom claims
            print("  Configurando custom claims...")
            claims_service.set_user_claims(
                firebase_uid=django_user.firebase_uid,
                role=django_user.role,
                permissions=django_user.get_permissions(),
                license_status='VALID'
            )
            print("  ✓ Custom claims configurados")
            
            created_users.append({
                'email': user_data['email'],
                'password': user_data['password'],
                'role': user_data['role'],
                'firebase_uid': django_user.firebase_uid,
                'django_id': django_user.id
            })
            
            print(f"\n✓ Usuario completado exitosamente")
            
        except Exception as e:
            print(f"\n✗ Error creando usuario {user_data['email']}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Print summary
    print(f"\n{'='*60}")
    print("RESUMEN DE USUARIOS CREADOS")
    print(f"{'='*60}\n")
    
    for user in created_users:
        print(f"Email: {user['email']}")
        print(f"Contraseña: {user['password']}")
        print(f"Rol: {user['role']}")
        print(f"Firebase UID: {user['firebase_uid']}")
        print(f"Django ID: {user['django_id']}")
        print("-" * 60)
    
    print(f"\n✓ Total usuarios procesados: {len(created_users)}")
    print(f"\nPuedes iniciar sesión en: https://cmms-somacor-prod.web.app")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    create_test_users()
