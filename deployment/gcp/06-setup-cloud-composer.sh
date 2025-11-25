#!/bin/bash

# Script para configurar Cloud Composer (Airflow) - OPCIONAL
# Uso: ./06-setup-cloud-composer.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
COMPOSER_ENV_NAME=${COMPOSER_ENV_NAME:-"cmms-composer"}

echo -e "${GREEN}=== Configurando Cloud Composer (Airflow) ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Environment Name: $COMPOSER_ENV_NAME"
echo ""

echo -e "${YELLOW}NOTA: Cloud Composer es OPCIONAL y tiene un costo significativo (~$300/mes)${NC}"
echo -e "${YELLOW}Solo es necesario si requieres automatización avanzada con Airflow${NC}"
echo ""

read -p "¿Deseas continuar con la configuración de Cloud Composer? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Configuración de Cloud Composer omitida"
    exit 0
fi

# Verificar proyecto
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar APIs
echo -e "${YELLOW}Habilitando APIs necesarias...${NC}"
gcloud services enable composer.googleapis.com
gcloud services enable dataproc.googleapis.com

# Verificar si el environment ya existe
if gcloud composer environments describe $COMPOSER_ENV_NAME --location $REGION &> /dev/null; then
    echo -e "${YELLOW}El environment $COMPOSER_ENV_NAME ya existe${NC}"
else
    # Crear environment de Cloud Composer
    echo -e "${YELLOW}Creando environment de Cloud Composer...${NC}"
    echo -e "${YELLOW}Esto puede tomar 20-30 minutos...${NC}"
    
    gcloud composer environments create $COMPOSER_ENV_NAME \
        --location $REGION \
        --python-version 3 \
        --machine-type n1-standard-1 \
        --disk-size 30GB \
        --node-count 3 \
        --labels environment=production,application=cmms
    
    echo -e "${GREEN}✓ Environment creado${NC}"
fi

# Obtener información del environment
AIRFLOW_URI=$(gcloud composer environments describe $COMPOSER_ENV_NAME \
    --location $REGION \
    --format="value(config.airflowUri)")

DAGS_FOLDER=$(gcloud composer environments describe $COMPOSER_ENV_NAME \
    --location $REGION \
    --format="value(config.dagGcsPrefix)")

echo ""
echo -e "${GREEN}=== Cloud Composer Configurado ===${NC}"
echo ""
echo "Airflow UI: $AIRFLOW_URI"
echo "DAGs Folder: $DAGS_FOLDER"
echo ""

# Guardar configuración
cat >> .env.gcp << EOF

# Cloud Composer
COMPOSER_ENVIRONMENT=$COMPOSER_ENV_NAME
COMPOSER_LOCATION=$REGION
AIRFLOW_URI=$AIRFLOW_URI
DAGS_FOLDER=$DAGS_FOLDER
EOF

echo -e "${GREEN}✓ Configuración guardada${NC}"

# Instrucciones para subir DAGs
echo ""
echo -e "${YELLOW}Para subir DAGs a Cloud Composer:${NC}"
echo ""
echo "1. Los DAGs deben estar en: airflow/dags/"
echo ""
echo "2. Subir DAGs:"
echo "   gcloud composer environments storage dags import \\"
echo "     --environment $COMPOSER_ENV_NAME \\"
echo "     --location $REGION \\"
echo "     --source airflow/dags/my_dag.py"
echo ""
echo "3. O subir toda la carpeta:"
echo "   gsutil -m rsync -r airflow/dags/ $DAGS_FOLDER"
echo ""
echo -e "${YELLOW}Acceder a Airflow UI:${NC}"
echo "   $AIRFLOW_URI"
echo ""
echo -e "${YELLOW}Ver logs:${NC}"
echo "   gcloud composer environments run $COMPOSER_ENV_NAME \\"
echo "     --location $REGION \\"
echo "     logs -- -t"
echo ""
