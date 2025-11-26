#!/usr/bin/env python
"""
Script para crear usuarios solo en Firebase (sin Django)
"""
import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase
cred_path = 'cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json'
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

def create_firebase_user(email, password, display_name, role):
    """Create a user in Firebase"""
    try:
        # Create user
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=False
        )
        
        print(f"✓ Usuario creado: {email}")
        print(f"  UID: {user.uid}")
        
        # Set custom claims
        auth.set_custom_user_claims(user.uid, {
            'role': role,
            'is_admin': role == 'ADMIN',
            'is_supervisor': role == 'SUPERVISOR',
            'is_operador': role == 'OPERADOR',
        })
        
        print(f"  ✓ Custom claims configurados: {role}")
        
        return user
        
    except auth.EmailAlreadyExistsError:
        print(f"⚠ Usuario ya existe: {email}")
        # Get existing user
        user = auth.get_user_by_email(email)
        # Update custom claims
        auth.set_custom_user_claims(user.uid, {
            'role': role,
            'is_admin': role == 'ADMIN',
            'is_supervisor': role == 'SUPERVISOR',
            'is_operador': role == 'OPERADOR',
        })
        print(f"  ✓ Custom claims actualizados: {role}")
        return user
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def main():
    print("="*60)
    print("Creando usuarios de prueba en Firebase")
    print("="*60)
    print()
    
    users = [
        {
            'email': 'admin@somacor.cl',
            'password': 'Admin123!',
            'display_name': 'Administrador Sistema',
            'role': 'ADMIN'
        },
        {
            'email': 'supervisor@somacor.cl',
            'password': 'Super123!',
            'display_name': 'Supervisor Mantenimiento',
            'role': 'SUPERVISOR'
        },
        {
            'email': 'operador@somacor.cl',
            'password': 'Opera123!',
            'display_name': 'Operador Campo',
            'role': 'OPERADOR'
        }
    ]
    
    created = []
    
    for user_data in users:
        print(f"\nCreando: {user_data['email']}")
        print(f"Rol: {user_data['role']}")
        print("-" * 60)
        
        user = create_firebase_user(
            email=user_data['email'],
            password=user_data['password'],
            display_name=user_data['display_name'],
            role=user_data['role']
        )
        
        if user:
            created.append({
                **user_data,
                'uid': user.uid
            })
    
    # Summary
    print()
    print("="*60)
    print("RESUMEN - CREDENCIALES DE ACCESO")
    print("="*60)
    print()
    print(f"URL: https://cmms-somacor-prod.web.app")
    print()
    
    for user in created:
        print(f"Email: {user['email']}")
        print(f"Contraseña: {user['password']}")
        print(f"Rol: {user['role']}")
        print(f"Firebase UID: {user['uid']}")
        print("-" * 60)
    
    print()
    print("✓ Usuarios creados exitosamente en Firebase")
    print()
    print("NOTA: Los usuarios se sincronizarán automáticamente con Django")
    print("      cuando inicien sesión por primera vez en el frontend.")
    print()

if __name__ == '__main__':
    main()
