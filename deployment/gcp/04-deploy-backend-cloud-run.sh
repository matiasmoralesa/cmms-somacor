#!/bin/bash

# Script para desplegar backend a Cloud Run
# Uso: ./04-deploy-backend-cloud-run.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"cmms-backend"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}=== Desplegando Backend a Cloud Run ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "Image: $IMAGE_NAME"
echo ""

# Verificar proyecto
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    exit 1
fi

# Cargar configuración
if [ -f .env.gcp ]; then
    source .env.gcp
else
    echo -e "${RED}Error: Archivo .env.gcp no encontrado${NC}"
    echo "Ejecuta primero los scripts de configuración de infraestructura"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo -e "${YELLOW}Habilitando APIs necesarias...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Construir imagen con Cloud Build
echo ""
echo -e "${YELLOW}Construyendo imagen con Cloud Build...${NC}"
cd ../../backend

gcloud builds submit --tag $IMAGE_NAME \
    --timeout=20m \
    --machine-type=n1-highcpu-8

echo -e "${GREEN}✓ Imagen construida exitosamente${NC}"

# Desplegar a Cloud Run
echo ""
echo -e "${YELLOW}Desplegando a Cloud Run...${NC}"

# Preparar variables de entorno
ENV_VARS="ENVIRONMENT=production"
ENV_VARS="${ENV_VARS},DEBUG=False"
ENV_VARS="${ENV_VARS},SECRET_KEY=${SECRET_KEY:-$(openssl rand -base64 32)}"
ENV_VARS="${ENV_VARS},DATABASE_URL=${DATABASE_URL_CLOUD_RUN}"
ENV_VARS="${ENV_VARS},GCP_PROJECT_ID=${PROJECT_ID}"
ENV_VARS="${ENV_VARS},GCP_STORAGE_BUCKET_NAME=${GCP_STORAGE_BUCKET_DOCUMENTS}"
ENV_VARS="${ENV_VARS},GCP_PUBSUB_TOPIC_NOTIFICATIONS=${GCP_PUBSUB_TOPIC_NOTIFICATIONS}"
ENV_VARS="${ENV_VARS},GCP_PUBSUB_TOPIC_EVENTS=${GCP_PUBSUB_TOPIC_EVENTS}"
ENV_VARS="${ENV_VARS},GCP_PUBSUB_TOPIC_ALERTS=${GCP_PUBSUB_TOPIC_ALERTS}"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="$ENV_VARS" \
    --add-cloudsql-instances $CLOUD_SQL_CONNECTION_NAME \
    --min-instances 1 \
    --max-instances 10 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --port 8000 \
    --service-account ${PROJECT_ID}@appspot.gserviceaccount.com

echo -e "${GREEN}✓ Servicio desplegado exitosamente${NC}"

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo ""
echo -e "${GREEN}=== Despliegue Completado ===${NC}"
echo ""
echo "🌐 URL del servicio: $SERVICE_URL"
echo ""
echo "📋 Endpoints disponibles:"
echo "   - API Docs: ${SERVICE_URL}/api/docs/"
echo "   - Health Check: ${SERVICE_URL}/api/v1/core/health/"
echo "   - Admin: ${SERVICE_URL}/admin/"
echo ""

# Guardar URL en configuración
echo "SERVICE_URL=$SERVICE_URL" >> ../gcp/.env.gcp

# Probar health check
echo -e "${YELLOW}Probando health check...${NC}"
sleep 5
if curl -f "${SERVICE_URL}/api/v1/core/health/live/" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health check exitoso${NC}"
else
    echo -e "${RED}✗ Health check falló${NC}"
    echo "Revisa los logs:"
    echo "gcloud run services logs read $SERVICE_NAME --region $REGION"
fi

echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configura el dominio personalizado (opcional)"
echo "2. Configura CORS en settings para el frontend"
echo "3. Crea el superusuario:"
echo "   gcloud run services update $SERVICE_NAME --set-env-vars CREATE_SUPERUSER=true"
echo "4. Revisa los logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""
