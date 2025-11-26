#!/bin/bash
set -e

echo "🚂 Starting Railway deployment..."

# Verificar variables de entorno críticas
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "❌ ERROR: DJANGO_SETTINGS_MODULE no está configurado"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurado"
    exit 1
fi

echo "✅ Variables de entorno verificadas"
echo "📦 DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Ejecutar collectstatic
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Archivos estáticos recolectados"

# Iniciar Gunicorn
echo "🚀 Iniciando Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
