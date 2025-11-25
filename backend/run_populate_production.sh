#!/bin/bash

# Script para ejecutar el script de población de datos en Cloud Run Job
# Este script construye una imagen Docker y la ejecuta como un Job de Cloud Run

set -e

PROJECT_ID="argon-edge-478500-i8"
REGION="us-central1"
JOB_NAME="cmms-populate-data"
IMAGE_NAME="gcr.io/${PROJECT_ID}/cmms-populate:latest"
DB_INSTANCE="cmms-db"

echo "=========================================="
echo "Poblando base de datos de producción"
echo "=========================================="

# 1. Construir la imagen Docker
echo "1. Construyendo imagen Docker..."
docker build -f Dockerfile.populate -t ${IMAGE_NAME} .

# 2. Subir la imagen a Container Registry
echo "2. Subiendo imagen a Container Registry..."
docker push ${IMAGE_NAME}

# 3. Crear o actualizar el Job de Cloud Run
echo "3. Creando/actualizando Cloud Run Job..."
gcloud run jobs create ${JOB_NAME} \
    --image=${IMAGE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production" \
    --set-cloudsql-instances="${PROJECT_ID}:${REGION}:${DB_INSTANCE}" \
    --set-secrets="DB_PASSWORD=cmms-db-password:latest" \
    --set-env-vars="DB_NAME=cmms_prod,DB_USER=cmms_user,DB_HOST=/cloudsql/${PROJECT_ID}:${REGION}:${DB_INSTANCE}" \
    --max-retries=0 \
    --task-timeout=10m \
    --memory=512Mi \
    --cpu=1 \
    || gcloud run jobs update ${JOB_NAME} \
        --image=${IMAGE_NAME} \
        --region=${REGION} \
        --project=${PROJECT_ID}

# 4. Ejecutar el Job
echo "4. Ejecutando Job..."
gcloud run jobs execute ${JOB_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --wait

echo "=========================================="
echo "✓ Datos poblados exitosamente"
echo "=========================================="
