#!/bin/bash

# Script de entrada para contenedor Docker
# Ejecuta migraciones y otros comandos de inicialización

set -e

echo "=== CMMS Backend Starting ==="
echo "Environment: ${ENVIRONMENT:-production}"
echo "Debug: ${DEBUG:-False}"

# Esperar a que la base de datos esté lista
echo "Waiting for database..."
python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse

max_retries = 30
retry_interval = 2

db_url = "$DATABASE_URL"
if not db_url:
    print("DATABASE_URL not set, skipping database check")
    sys.exit(0)

# Parse database URL
result = urlparse(db_url)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port or 5432

for i in range(max_retries):
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        conn.close()
        print("Database is ready!")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        if i < max_retries - 1:
            print(f"Database not ready yet, retrying in {retry_interval}s... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
        else:
            print(f"Could not connect to database after {max_retries} attempts")
            sys.exit(1)
END

# Ejecutar migraciones
echo "Running database migrations..."
python manage.py migrate --noinput

# Crear superusuario si no existe (solo en desarrollo)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
END
fi

# Recolectar archivos estáticos (por si acaso)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "=== Starting application ==="
echo ""

# Ejecutar comando pasado como argumentos
exec "$@"
