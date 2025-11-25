#!/bin/bash

# Script maestro para desplegar toda la infraestructura de CMMS en GCP
# Uso: ./deploy-all.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         CMMS - Despliegue Completo en GCP                ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar variables de entorno
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID no está configurado${NC}"
    echo ""
    echo "Configura las variables de entorno:"
    echo "  export GCP_PROJECT_ID=tu-proyecto-123"
    echo "  export GCP_REGION=us-central1"
    echo "  export DB_PASSWORD=tu-contraseña-segura"
    echo ""
    exit 1
fi

echo -e "${GREEN}Configuración:${NC}"
echo "  Project ID: $GCP_PROJECT_ID"
echo "  Region: ${GCP_REGION:-us-central1}"
echo ""

# Confirmar antes de continuar
read -p "¿Deseas continuar con el despliegue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Despliegue cancelado"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 1/6: Creando instancia de Cloud SQL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
./01-create-cloud-sql.sh

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 2/6: Creando buckets de Cloud Storage${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
./02-create-storage-buckets.sh

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 3/6: Configurando Cloud Pub/Sub${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
./03-create-pubsub-topics.sh

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 4/6: Desplegando Backend a Cloud Run${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
./04-deploy-backend-cloud-run.sh

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 5/6: Desplegando Frontend a Firebase Hosting${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
./05-deploy-frontend-firebase.sh

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Paso 6/6: Configuración final${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Cargar configuración
source .env.gcp

# Configurar CORS en el backend
echo -e "${YELLOW}Configurando CORS...${NC}"
gcloud run services update cmms-backend \
    --set-env-vars="FRONTEND_URL=${FRONTEND_URL}" \
    --region ${GCP_REGION:-us-central1}

echo -e "${GREEN}✓ CORS configurado${NC}"

# Resumen final
echo ""
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         ✓ Despliegue Completado Exitosamente             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${GREEN}URLs de la Aplicación:${NC}"
echo "  Frontend: ${FRONTEND_URL}"
echo "  Backend:  ${SERVICE_URL}"
echo "  API Docs: ${SERVICE_URL}/api/docs/"
echo ""
echo -e "${GREEN}Recursos Creados:${NC}"
echo "  ✓ Cloud SQL: ${CLOUD_SQL_CONNECTION_NAME}"
echo "  ✓ Cloud Storage: 4 buckets"
echo "  ✓ Cloud Pub/Sub: 3 topics + subscriptions"
echo "  ✓ Cloud Run: cmms-backend"
echo "  ✓ Firebase Hosting: frontend"
echo ""
echo -e "${YELLOW}Próximos Pasos:${NC}"
echo "  1. Crea un superusuario para acceder al admin"
echo "  2. Configura el bot de Telegram (opcional)"
echo "  3. Configura Cloud Composer para automatización (opcional)"
echo "  4. Configura monitoreo y alertas"
echo "  5. Configura dominio personalizado"
echo ""
echo -e "${YELLOW}Comandos Útiles:${NC}"
echo "  Ver logs del backend:"
echo "    gcloud run services logs read cmms-backend --region ${GCP_REGION:-us-central1}"
echo ""
echo "  Conectar a Cloud SQL:"
echo "    ./cloud-sql-proxy-setup.sh"
echo ""
echo "  Actualizar backend:"
echo "    ./04-deploy-backend-cloud-run.sh"
echo ""
echo "  Actualizar frontend:"
echo "    ./05-deploy-frontend-firebase.sh"
echo ""
echo -e "${GREEN}¡Despliegue completado! 🎉${NC}"
echo ""
