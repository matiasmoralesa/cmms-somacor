#!/usr/bin/env python
"""
Script para ejecutar migraciones de Django en Cloud SQL
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ['DATABASE_URL'] = 'postgresql://cmms_user:Santi2005@/cmms_db?host=/cloudsql/argon-edge-478500-i8:us-central1:cmms-postgres'
os.environ['GCP_PROJECT_ID'] = 'argon-edge-478500-i8'
os.environ['GCP_STORAGE_BUCKET_NAME'] = 'cmms-storage-argon-edge'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Cambiar al directorio backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

django.setup()

from django.core.management import call_command

print("Ejecutando migraciones...")
call_command('migrate', '--noinput')
print("Migraciones completadas!")

print("\nCreando superusuario...")
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print("Superusuario creado: admin@example.com / admin123")
else:
    print("El superusuario ya existe")
