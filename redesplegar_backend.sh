#!/bin/bash

# Script para redesplegar el backend en Cloud Run
# Este script actualiza el backend con la nueva configuración de CORS

echo "🚀 Iniciando redespliegue del backend..."
echo ""

# Configurar el proyecto
echo "📋 Configurando proyecto GCP..."
gcloud config set project argon-edge-478500-i8

# Navegar al directorio del backend
cd backend

# Construir la imagen
echo "🔨 Construyendo imagen Docker..."
gcloud builds submit --tag gcr.io/argon-edge-478500-i8/cmms-backend

# Desplegar en Cloud Run
echo "🚢 Desplegando en Cloud Run..."
gcloud run deploy cmms-backend \
  --image gcr.io/argon-edge-478500-i8/cmms-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DJANGO_SETTINGS_MODULE=config.settings.production \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10

echo ""
echo "✅ Redespliegue completado!"
echo ""
echo "🌐 URLs del sistema:"
echo "   Frontend: https://cmms-somacor-prod.web.app"
echo "   Backend: https://cmms-backend-232652686658.us-central1.run.app"
echo ""
echo "🔍 Verifica que el frontend pueda comunicarse con el backend."
