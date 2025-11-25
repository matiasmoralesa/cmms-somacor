#!/bin/bash
# Script to load inventory data in production

echo "Loading inventory demo data in production..."

gcloud run jobs create load-inventory-data \
  --image gcr.io/argon-edge-478500-i8/cmms-backend \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings,ENVIRONMENT=production" \
  --command python \
  --args manage.py,load_demo_data \
  --max-retries 0 \
  --task-timeout 600

echo "Executing job..."
gcloud run jobs execute load-inventory-data --region us-central1

echo "Done!"
