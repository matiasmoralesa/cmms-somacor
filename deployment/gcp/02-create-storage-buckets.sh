#!/bin/bash

# Script para crear buckets de Cloud Storage para CMMS
# Uso: ./02-create-storage-buckets.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
STORAGE_CLASS=${STORAGE_CLASS:-"STANDARD"}

# Nombres de buckets
DOCUMENTS_BUCKET="${PROJECT_ID}-cmms-documents"
ML_MODELS_BUCKET="${PROJECT_ID}-cmms-ml-models"
REPORTS_BUCKET="${PROJECT_ID}-cmms-reports"
BACKUPS_BUCKET="${PROJECT_ID}-cmms-backups"

echo -e "${GREEN}=== Creando Buckets de Cloud Storage ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Storage Class: $STORAGE_CLASS"
echo ""

# Verificar proyecto
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar API
echo -e "${YELLOW}Habilitando Cloud Storage API...${NC}"
gcloud services enable storage-api.googleapis.com
gcloud services enable storage-component.googleapis.com

# Función para crear bucket
create_bucket() {
    local bucket_name=$1
    local description=$2
    
    echo -e "${YELLOW}Creando bucket: $bucket_name${NC}"
    
    if gsutil ls -b gs://$bucket_name &> /dev/null; then
        echo -e "${YELLOW}El bucket $bucket_name ya existe. Saltando...${NC}"
    else
        gsutil mb -p $PROJECT_ID -c $STORAGE_CLASS -l $REGION gs://$bucket_name
        echo -e "${GREEN}✓ Bucket creado: $bucket_name${NC}"
    fi
    
    # Configurar labels
    gsutil label ch -l environment:production gs://$bucket_name
    gsutil label ch -l application:cmms gs://$bucket_name
}

# Crear buckets
echo ""
echo -e "${GREEN}Creando buckets...${NC}"

# 1. Bucket de documentos
create_bucket $DOCUMENTS_BUCKET "Documentos de activos y órdenes de trabajo"

# Configurar CORS para documentos
echo -e "${YELLOW}Configurando CORS para documentos...${NC}"
cat > /tmp/cors-config.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set /tmp/cors-config.json gs://$DOCUMENTS_BUCKET
rm /tmp/cors-config.json

# 2. Bucket de modelos ML
create_bucket $ML_MODELS_BUCKET "Modelos de Machine Learning"

# 3. Bucket de reportes
create_bucket $REPORTS_BUCKET "Reportes generados"

# Configurar lifecycle para reportes (eliminar después de 90 días)
echo -e "${YELLOW}Configurando lifecycle para reportes...${NC}"
cat > /tmp/lifecycle-config.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/lifecycle-config.json gs://$REPORTS_BUCKET
rm /tmp/lifecycle-config.json

# 4. Bucket de backups
create_bucket $BACKUPS_BUCKET "Backups del sistema"

# Configurar lifecycle para backups (mover a Nearline después de 30 días, eliminar después de 365)
echo -e "${YELLOW}Configurando lifecycle para backups...${NC}"
cat > /tmp/backup-lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/backup-lifecycle.json gs://$BACKUPS_BUCKET
rm /tmp/backup-lifecycle.json

# Configurar permisos
echo ""
echo -e "${GREEN}Configurando permisos...${NC}"

# Obtener service account de Cloud Run (si existe)
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

# Dar permisos a los buckets
for bucket in $DOCUMENTS_BUCKET $ML_MODELS_BUCKET $REPORTS_BUCKET $BACKUPS_BUCKET; do
    echo -e "${YELLOW}Configurando permisos para $bucket...${NC}"
    gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectAdmin gs://$bucket
done

# Configurar versionado para documentos importantes
echo ""
echo -e "${YELLOW}Habilitando versionado para documentos...${NC}"
gsutil versioning set on gs://$DOCUMENTS_BUCKET
gsutil versioning set on gs://$ML_MODELS_BUCKET

# Guardar configuración
echo ""
echo -e "${YELLOW}Guardando configuración...${NC}"
cat >> .env.gcp << EOF

# Cloud Storage Buckets
GCP_STORAGE_BUCKET_DOCUMENTS=$DOCUMENTS_BUCKET
GCP_STORAGE_BUCKET_ML_MODELS=$ML_MODELS_BUCKET
GCP_STORAGE_BUCKET_REPORTS=$REPORTS_BUCKET
GCP_STORAGE_BUCKET_BACKUPS=$BACKUPS_BUCKET
EOF

echo -e "${GREEN}✓ Configuración guardada en .env.gcp${NC}"

# Mostrar resumen
echo ""
echo -e "${GREEN}=== Buckets Creados Exitosamente ===${NC}"
echo ""
echo "📁 Documentos: gs://$DOCUMENTS_BUCKET"
echo "   - CORS habilitado"
echo "   - Versionado habilitado"
echo ""
echo "🤖 Modelos ML: gs://$ML_MODELS_BUCKET"
echo "   - Versionado habilitado"
echo ""
echo "📊 Reportes: gs://$REPORTS_BUCKET"
echo "   - Lifecycle: Eliminar después de 90 días"
echo ""
echo "💾 Backups: gs://$BACKUPS_BUCKET"
echo "   - Lifecycle: Nearline después de 30 días"
echo "   - Lifecycle: Eliminar después de 365 días"
echo ""

# Mostrar uso de storage
echo -e "${GREEN}=== Uso de Storage ===${NC}"
gsutil du -sh gs://$DOCUMENTS_BUCKET 2>/dev/null || echo "Documentos: 0 B"
gsutil du -sh gs://$ML_MODELS_BUCKET 2>/dev/null || echo "Modelos ML: 0 B"
gsutil du -sh gs://$REPORTS_BUCKET 2>/dev/null || echo "Reportes: 0 B"
gsutil du -sh gs://$BACKUPS_BUCKET 2>/dev/null || echo "Backups: 0 B"
echo ""

echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configura las variables de entorno en tu aplicación"
echo "2. Prueba subir un archivo:"
echo "   gsutil cp test.txt gs://$DOCUMENTS_BUCKET/"
echo ""
