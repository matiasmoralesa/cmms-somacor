#!/bin/bash

# Script para ejecutar migraciones en Cloud Run

echo "Ejecutando migraciones..."

# Ejecutar migraciones
gcloud run jobs execute cmms-migrate \
  --region us-central1 \
  --wait

echo "Migraciones completadas"
