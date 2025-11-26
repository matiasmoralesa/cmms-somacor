#!/usr/bin/env python
"""
Script para probar la conexión MySQL antes de desplegar
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.core.management import call_command

def test_connection():
    """Probar conexión a MySQL"""
    print("\n" + "="*60)
    print("PROBANDO CONEXION MYSQL")
    print("="*60 + "\n")
    
    # Obtener configuración
    db_config = connection.settings_dict
    print(f"[INFO] Configuración de base de datos:")
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")
    print(f"  Database: {db_config['NAME']}")
    print(f"  User: {db_config['USER']}")
    print()
    
    # Probar conexión
    try:
        print("[1/4] Probando conexión...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"  ✅ Conectado a MySQL {version}")
    except Exception as e:
        print(f"  ❌ Error de conexión: {e}")
        return False
    
    # Verificar base de datos
    try:
        print("\n[2/4] Verificando base de datos...")
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", [db_config['NAME']])
            result = cursor.fetchone()
            if result:
                print(f"  ✅ Base de datos '{db_config['NAME']}' existe")
            else:
                print(f"  ❌ Base de datos '{db_config['NAME']}' no existe")
                return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Verificar permisos
    try:
        print("\n[3/4] Verificando permisos...")
        with connection.cursor() as cursor:
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            print(f"  ✅ Usuario tiene {len(grants)} permisos")
    except Exception as e:
        print(f"  ⚠️  No se pudieron verificar permisos: {e}")
    
    # Probar migraciones
    try:
        print("\n[4/4] Probando migraciones...")
        call_command('migrate', '--check', verbosity=0)
        print("  ✅ Migraciones OK")
    except Exception as e:
        print(f"  ⚠️  Hay migraciones pendientes (normal en primera ejecución)")
    
    print("\n" + "="*60)
    print("✅ CONEXION EXITOSA - Listo para desplegar")
    print("="*60 + "\n")
    return True

if __name__ == '__main__':
    # Verificar variables de entorno
    required_vars = ['MYSQLHOST', 'MYSQLUSER', 'MYSQLPASSWORD', 'MYSQLDATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars and not os.getenv('DATABASE_URL'):
        print("\n❌ ERROR: Faltan variables de entorno:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nConfigura las variables o usa DATABASE_URL")
        print("\nEjemplo:")
        print("  set MYSQLHOST=localhost")
        print("  set MYSQLPORT=3306")
        print("  set MYSQLUSER=cmms_user")
        print("  set MYSQLPASSWORD=cmms_password_2024")
        print("  set MYSQLDATABASE=cmms_db")
        sys.exit(1)
    
    success = test_connection()
    sys.exit(0 if success else 1)
