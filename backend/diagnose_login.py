#!/usr/bin/env python
"""
Script para diagnosticar problemas de login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User
from apps.authentication.serializers import CustomTokenObtainPairSerializer

print("=== Diagnóstico de Login ===\n")

# Verificar usuario
try:
    user = User.objects.get(email='admin@somacor.com')
    print(f"✅ Usuario encontrado: {user.email}")
    print(f"   Nombre: {user.get_full_name()}")
    print(f"   Activo: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"   Rol: {user.role.name if user.role else 'Sin rol'}")
    
    # Verificar permisos
    if user.role:
        perms = user.role.permissions.all()
        print(f"   Permisos: {perms.count()}")
        if perms.count() > 0:
            for perm in perms[:5]:
                print(f"      - {perm.code}: {perm.name}")
        else:
            print(f"      ⚠️  No tiene permisos asignados")
    else:
        print(f"   ⚠️  No tiene rol asignado")
    
    # Verificar contraseña
    if user.check_password('admin123'):
        print(f"✅ Contraseña correcta")
    else:
        print(f"❌ Contraseña incorrecta")
    
    # Intentar generar token
    print(f"\n=== Intentando generar token ===")
    
    # Simular request
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.post('/api/v1/auth/login/', {
        'email': 'admin@somacor.com',
        'password': 'admin123'
    })
    
    serializer = CustomTokenObtainPairSerializer(data={
        'email': 'admin@somacor.com',
        'password': 'admin123'
    }, context={'request': request})
    
    if serializer.is_valid():
        print(f"✅ Serializer válido")
        try:
            token_data = serializer.validated_data
            print(f"   Access token generado: {str(token_data['access'])[:50]}...")
            print(f"   Refresh token generado: {str(token_data['refresh'])[:50]}...")
            print(f"   Usuario en respuesta: {token_data['user']['email']}")
        except Exception as e:
            print(f"❌ Error al generar token: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Serializer inválido")
        print(f"   Errores: {serializer.errors}")
        
except User.DoesNotExist:
    print(f"❌ Usuario no encontrado")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n=== Diagnóstico completado ===")
