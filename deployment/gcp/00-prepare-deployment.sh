#!/bin/bash

# Script de preparación para despliegue en GCP
# Este script verifica requisitos y prepara el entorno

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
echo "║         CMMS - Preparación para Despliegue GCP           ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Función para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 está instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO está instalado"
        return 1
    fi
}

# Función para generar secreto
generate_secret() {
    python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
}

# Verificar requisitos
echo -e "${BLUE}═══ Verificando Requisitos ═══${NC}"
echo ""

MISSING_TOOLS=0

check_command "gcloud" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_command "firebase" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_command "docker" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_command "python3" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_command "node" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_command "npm" || MISSING_TOOLS=$((MISSING_TOOLS + 1))

echo ""

if [ $MISSING_TOOLS -gt 0 ]; then
    echo -e "${RED}Faltan $MISSING_TOOLS herramientas requeridas${NC}"
    echo ""
    echo "Instala las herramientas faltantes:"
    echo "  - gcloud: https://cloud.google.com/sdk/docs/install"
    echo "  - firebase: npm install -g firebase-tools"
    echo "  - docker: https://docs.docker.com/get-docker/"
    echo "  - python3: https://www.python.org/downloads/"
    echo "  - node/npm: https://nodejs.org/"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Todas las herramientas están instaladas${NC}"
echo ""

# Solicitar información del proyecto
echo -e "${BLUE}═══ Configuración del Proyecto ═══${NC}"
echo ""

read -p "ID del Proyecto GCP (ej: mi-cmms-123): " GCP_PROJECT_ID
read -p "Región GCP [us-central1]: " GCP_REGION
GCP_REGION=${GCP_REGION:-us-central1}

read -p "Nombre de la base de datos [cmms_prod]: " DB_NAME
DB_NAME=${DB_NAME:-cmms_prod}

read -p "Usuario de la base de datos [cmms_user]: " DB_USER
DB_USER=${DB_USER:-cmms_user}

echo ""
echo -e "${YELLOW}Generando secretos...${NC}"

# Generar secretos
SECRET_KEY=$(generate_secret)
DB_PASSWORD=$(generate_secret | cut -c1-32)

echo -e "${GREEN}✓ Secretos generados${NC}"
echo ""

# Crear archivo de configuración
ENV_FILE=".env.gcp"

echo -e "${YELLOW}Creando archivo de configuración: $ENV_FILE${NC}"

cat > $ENV_FILE << EOF
# Configuración de GCP para CMMS
# Generado: $(date)

# Proyecto GCP
export GCP_PROJECT_ID="$GCP_PROJECT_ID"
export GCP_REGION="$GCP_REGION"

# Base de Datos
export DB_NAME="$DB_NAME"
export DB_USER="$DB_USER"
export DB_PASSWORD="$DB_PASSWORD"
export DB_TIER="db-g1-small"
export CLOUD_SQL_CONNECTION_NAME="\${GCP_PROJECT_ID}:\${GCP_REGION}:cmms-db"

# Django
export SECRET_KEY="$SECRET_KEY"
export DJANGO_SETTINGS_MODULE="config.settings.production"
export DEBUG="False"

# Cloud Run
export SERVICE_NAME="cmms-backend"
export CLOUD_RUN_MIN_INSTANCES="1"
export CLOUD_RUN_MAX_INSTANCES="5"
export CLOUD_RUN_MEMORY="1Gi"
export CLOUD_RUN_CPU="2"

# Storage
export BUCKET_DOCUMENTS="\${GCP_PROJECT_ID}-cmms-documents"
export BUCKET_ML_MODELS="\${GCP_PROJECT_ID}-cmms-ml-models"
export BUCKET_REPORTS="\${GCP_PROJECT_ID}-cmms-reports"
export BUCKET_BACKUPS="\${GCP_PROJECT_ID}-cmms-backups"

# Pub/Sub
export TOPIC_NOTIFICATIONS="notifications"
export TOPIC_EVENTS="events"
export TOPIC_ALERTS="alerts"

# URLs (se actualizarán después del despliegue)
export SERVICE_URL="https://\${SERVICE_NAME}-\${GCP_PROJECT_ID}.run.app"
export FRONTEND_URL="https://\${GCP_PROJECT_ID}.web.app"

# CORS
export CORS_ALLOWED_ORIGINS="\${FRONTEND_URL}"
export ALLOWED_HOSTS="\${SERVICE_NAME}-\${GCP_PROJECT_ID}.run.app"
EOF

echo -e "${GREEN}✓ Archivo de configuración creado${NC}"
echo ""

# Cargar configuración
source $ENV_FILE

# Verificar autenticación de gcloud
echo -e "${BLUE}═══ Verificando Autenticación ═══${NC}"
echo ""

if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    CURRENT_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    echo -e "${GREEN}✓ Autenticado como: $CURRENT_ACCOUNT${NC}"
else
    echo -e "${YELLOW}No estás autenticado en gcloud${NC}"
    read -p "¿Deseas autenticarte ahora? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud auth login
    else
        echo -e "${RED}Debes autenticarte para continuar${NC}"
        exit 1
    fi
fi

echo ""

# Verificar/Crear proyecto
echo -e "${BLUE}═══ Verificando Proyecto GCP ═══${NC}"
echo ""

if gcloud projects describe $GCP_PROJECT_ID &> /dev/null; then
    echo -e "${GREEN}✓ Proyecto $GCP_PROJECT_ID existe${NC}"
else
    echo -e "${YELLOW}Proyecto $GCP_PROJECT_ID no existe${NC}"
    read -p "¿Deseas crear el proyecto? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud projects create $GCP_PROJECT_ID --name="CMMS System"
        echo -e "${GREEN}✓ Proyecto creado${NC}"
    else
        echo -e "${RED}Debes crear el proyecto para continuar${NC}"
        exit 1
    fi
fi

# Configurar proyecto actual
gcloud config set project $GCP_PROJECT_ID

echo ""

# Verificar facturación
echo -e "${BLUE}═══ Verificando Facturación ═══${NC}"
echo ""

if gcloud beta billing projects describe $GCP_PROJECT_ID --format="value(billingEnabled)" 2>/dev/null | grep -q "True"; then
    echo -e "${GREEN}✓ Facturación habilitada${NC}"
else
    echo -e "${YELLOW}⚠ Facturación NO habilitada${NC}"
    echo ""
    echo "Debes habilitar la facturación en:"
    echo "https://console.cloud.google.com/billing/linkedaccount?project=$GCP_PROJECT_ID"
    echo ""
    read -p "Presiona Enter cuando hayas habilitado la facturación..."
fi

echo ""

# Habilitar APIs
echo -e "${BLUE}═══ Habilitando APIs de GCP ═══${NC}"
echo ""

APIS=(
    "run.googleapis.com"
    "sql-component.googleapis.com"
    "sqladmin.googleapis.com"
    "storage-api.googleapis.com"
    "storage-component.googleapis.com"
    "pubsub.googleapis.com"
    "cloudbuild.googleapis.com"
    "secretmanager.googleapis.com"
    "firebase.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -n "Habilitando $api... "
    if gcloud services enable $api --quiet 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}(ya habilitada)${NC}"
    fi
done

echo ""
echo -e "${GREEN}✓ APIs habilitadas${NC}"
echo ""

# Crear backend .env
echo -e "${BLUE}═══ Creando Archivos de Configuración ═══${NC}"
echo ""

BACKEND_ENV="../../backend/.env.production"

cat > $BACKEND_ENV << EOF
# Backend Production Environment
# Generado: $(date)

SECRET_KEY=$SECRET_KEY
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=$ALLOWED_HOSTS

DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CLOUD_SQL_CONNECTION_NAME

GCP_PROJECT_ID=$GCP_PROJECT_ID
GCP_STORAGE_BUCKET_NAME=$BUCKET_DOCUMENTS
CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME

GCP_PUBSUB_TOPIC_NOTIFICATIONS=$TOPIC_NOTIFICATIONS
GCP_PUBSUB_TOPIC_EVENTS=$TOPIC_EVENTS
GCP_PUBSUB_TOPIC_ALERTS=$TOPIC_ALERTS

CORS_ALLOWED_ORIGINS=$CORS_ALLOWED_ORIGINS
EOF

echo -e "${GREEN}✓ Backend .env.production creado${NC}"

# Crear frontend .env
FRONTEND_ENV="../../frontend/.env.production"

cat > $FRONTEND_ENV << EOF
# Frontend Production Environment
# Generado: $(date)

VITE_API_URL=$SERVICE_URL/api/v1
EOF

echo -e "${GREEN}✓ Frontend .env.production creado${NC}"
echo ""

# Resumen
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         ✓ Preparación Completada                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${GREEN}Configuración:${NC}"
echo "  Proyecto: $GCP_PROJECT_ID"
echo "  Región: $GCP_REGION"
echo "  Base de Datos: $DB_NAME"
echo ""

echo -e "${GREEN}Archivos Creados:${NC}"
echo "  ✓ $ENV_FILE"
echo "  ✓ $BACKEND_ENV"
echo "  ✓ $FRONTEND_ENV"
echo ""

echo -e "${YELLOW}Próximos Pasos:${NC}"
echo ""
echo "1. Revisar la configuración en: $ENV_FILE"
echo ""
echo "2. Ejecutar el despliegue completo:"
echo "   ${BLUE}./deploy-all.sh${NC}"
echo ""
echo "   O ejecutar paso a paso:"
echo "   ${BLUE}./01-create-cloud-sql.sh${NC}"
echo "   ${BLUE}./02-create-storage-buckets.sh${NC}"
echo "   ${BLUE}./03-create-pubsub-topics.sh${NC}"
echo "   ${BLUE}./04-deploy-backend-cloud-run.sh${NC}"
echo "   ${BLUE}./05-deploy-frontend-firebase.sh${NC}"
echo ""

echo -e "${GREEN}¡Preparación completada! 🎉${NC}"
echo ""

# Guardar resumen
cat > DEPLOYMENT_SUMMARY.txt << EOF
CMMS - Resumen de Configuración
================================

Fecha: $(date)
Proyecto: $GCP_PROJECT_ID
Región: $GCP_REGION

Base de Datos:
  Nombre: $DB_NAME
  Usuario: $DB_USER
  Contraseña: $DB_PASSWORD

Django Secret Key: $SECRET_KEY

URLs (después del despliegue):
  Backend: $SERVICE_URL
  Frontend: $FRONTEND_URL

IMPORTANTE: Guarda este archivo en un lugar seguro y NO lo commitees a Git.
EOF

echo -e "${YELLOW}⚠ IMPORTANTE: Se ha creado DEPLOYMENT_SUMMARY.txt con información sensible${NC}"
echo -e "${YELLOW}   Guárdalo en un lugar seguro y NO lo commitees a Git${NC}"
echo ""
