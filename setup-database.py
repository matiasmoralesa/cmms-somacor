#!/usr/bin/env python
"""
Script para configurar la base de datos PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Conectar como postgres (usuario root)
print("Conectando a PostgreSQL...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Santi2005",
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("✓ Conectado exitosamente")
    
    # Verificar si el usuario ya existe
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='cmms_user'")
    user_exists = cursor.fetchone()
    
    if not user_exists:
        print("\nCreando usuario cmms_user...")
        cursor.execute("CREATE USER cmms_user WITH PASSWORD 'Santi2005';")
        print("✓ Usuario creado")
    else:
        print("\n✓ Usuario cmms_user ya existe")
    
    # Verificar si la base de datos ya existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='cmms_db'")
    db_exists = cursor.fetchone()
    
    if not db_exists:
        print("\nCreando base de datos cmms_db...")
        cursor.execute("CREATE DATABASE cmms_db OWNER cmms_user;")
        print("✓ Base de datos creada")
    else:
        print("\n✓ Base de datos cmms_db ya existe")
    
    # Otorgar permisos
    print("\nOtorgando permisos...")
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE cmms_db TO cmms_user;")
    print("✓ Permisos otorgados")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✓ Base de datos configurada correctamente")
    print("="*50)
    print("\nCredenciales:")
    print("  Usuario: cmms_user")
    print("  Password: Santi2005")
    print("  Database: cmms_db")
    print("  Host: localhost")
    print("  Port: 5432")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nAsegúrate de que:")
    print("1. El Cloud SQL Proxy está corriendo")
    print("2. La contraseña de postgres es correcta")
    exit(1)
