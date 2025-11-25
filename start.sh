#!/bin/bash

echo "🚀 Iniciando CMMS System..."

# Check if .env files exist
if [ ! -f backend/.env ]; then
    echo "📝 Creando backend/.env desde .env.example..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creando frontend/.env desde .env.example..."
    cp frontend/.env.example frontend/.env
fi

# Start Docker Compose
echo "🐳 Iniciando servicios con Docker Compose..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 10

# Run migrations
echo "🔄 Ejecutando migraciones..."
docker-compose exec -T backend python manage.py migrate

echo "✅ Sistema iniciado correctamente!"
echo ""
echo "📍 URLs disponibles:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000/api/v1/"
echo "   Admin Django: http://localhost:8000/admin/"
echo "   API Docs: http://localhost:8000/api/docs/"
echo ""
echo "💡 Para crear un superusuario, ejecuta:"
echo "   docker-compose exec backend python manage.py createsuperuser"
