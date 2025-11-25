#!/usr/bin/env python
"""Test database connection"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    import django
    django.setup()
    
    from django.db import connection
    
    print("Intentando conectar a la base de datos...")
    print(f"Host: {connection.settings_dict['HOST']}")
    print(f"Port: {connection.settings_dict['PORT']}")
    print(f"Database: {connection.settings_dict['NAME']}")
    print(f"User: {connection.settings_dict['USER']}")
    print("")
    
    # Intentar conexión
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("✓ Conexión exitosa!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        users = cursor.fetchone()[0]
        print(f"Usuarios en la base de datos: {users}")
        
except Exception as e:
    print(f"✗ Error de conexión: {str(e)}")
    print("")
    print("Posibles soluciones:")
    print("1. Verifica que tu IP esté autorizada en Cloud SQL")
    print("2. Usa Cloud SQL Proxy")
    print("3. Ejecuta desde Cloud Shell")
    sys.exit(1)
