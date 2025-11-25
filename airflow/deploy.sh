#!/bin/bash

# Deployment script for Airflow DAGs to Cloud Composer
# Usage: ./deploy.sh <environment-name> <location>

set -e

ENVIRONMENT_NAME=${1:-cmms-composer}
LOCATION=${2:-us-central1}
PROJECT_ID=$(gcloud config get-value project)

echo "🚀 Deploying Airflow DAGs to Cloud Composer"
echo "Environment: $ENVIRONMENT_NAME"
echo "Location: $LOCATION"
echo "Project: $PROJECT_ID"
echo ""

# Check if environment exists
echo "📋 Checking if environment exists..."
if ! gcloud composer environments describe $ENVIRONMENT_NAME --location $LOCATION &> /dev/null; then
    echo "❌ Environment $ENVIRONMENT_NAME does not exist in $LOCATION"
    echo "Create it first with:"
    echo "  gcloud composer environments create $ENVIRONMENT_NAME --location $LOCATION"
    exit 1
fi

echo "✅ Environment exists"
echo ""

# Upload DAGs
echo "📤 Uploading DAGs..."
gcloud composer environments storage dags import \
    --environment $ENVIRONMENT_NAME \
    --location $LOCATION \
    --source dags/etl_ml_training_dag.py

gcloud composer environments storage dags import \
    --environment $ENVIRONMENT_NAME \
    --location $LOCATION \
    --source dags/preventive_maintenance_dag.py

gcloud composer environments storage dags import \
    --environment $ENVIRONMENT_NAME \
    --location $LOCATION \
    --source dags/report_generation_dag.py

echo "✅ DAGs uploaded"
echo ""

# Upload scripts
echo "📤 Uploading PySpark scripts..."
BUCKET_NAME=$(gcloud composer environments describe $ENVIRONMENT_NAME \
    --location $LOCATION \
    --format="get(config.dagGcsPrefix)" | sed 's|gs://||' | cut -d'/' -f1)

gsutil cp scripts/feature_engineering.py gs://$BUCKET_NAME/scripts/

echo "✅ Scripts uploaded"
echo ""

# Update Python packages
echo "📦 Updating Python packages..."
gcloud composer environments update $ENVIRONMENT_NAME \
    --location $LOCATION \
    --update-pypi-packages-from-file requirements.txt

echo "✅ Packages updated"
echo ""

# Get Airflow UI URL
AIRFLOW_URL=$(gcloud composer environments describe $ENVIRONMENT_NAME \
    --location $LOCATION \
    --format="get(config.airflowUri)")

echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Airflow UI: $AIRFLOW_URL"
echo ""
echo "Next steps:"
echo "1. Configure Airflow variables (see airflow_variables.json)"
echo "2. Configure connections (cloudsql_postgres)"
echo "3. Unpause DAGs in Airflow UI"
echo "4. Test DAGs with manual trigger"
