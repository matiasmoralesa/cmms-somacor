#!/bin/bash
set -e

echo "🚂 Starting Railway deployment..."

# Forzar el uso de railway settings si no está configurado
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "⚠️  DJANGO_SETTINGS_MODULE no configurado, usando config.settings.railway"
    export DJANGO_SETTINGS_MODULE=config.settings.railway
fi

# Verificar DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurado"
    exit 1
fi

echo "✅ Variables de entorno verificadas"
echo "📦 DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "📦 RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"

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
