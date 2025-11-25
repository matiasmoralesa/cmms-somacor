#!/bin/bash

# Script para crear instancia de Cloud SQL para CMMS
# Uso: ./01-create-cloud-sql.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
INSTANCE_NAME=${CLOUD_SQL_INSTANCE_NAME:-"cmms-db"}
DATABASE_NAME=${DATABASE_NAME:-"cmms_prod"}
DB_USER=${DB_USER:-"cmms_user"}
DB_PASSWORD=${DB_PASSWORD:-""}
TIER=${DB_TIER:-"db-f1-micro"}  # Para producción usar db-n1-standard-1 o superior

echo -e "${GREEN}=== Creando Instancia de Cloud SQL ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Instance Name: $INSTANCE_NAME"
echo "Database Name: $DATABASE_NAME"
echo "Tier: $TIER"
echo ""

# Verificar que el proyecto esté configurado
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    echo "Ejemplo: export GCP_PROJECT_ID=mi-proyecto-123"
    exit 1
fi

# Verificar que la contraseña esté configurada
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}Generando contraseña aleatoria...${NC}"
    DB_PASSWORD=$(openssl rand -base64 32)
    echo -e "${GREEN}Contraseña generada. Guárdala en un lugar seguro:${NC}"
    echo "$DB_PASSWORD"
    echo ""
fi

# Configurar proyecto
echo -e "${YELLOW}Configurando proyecto...${NC}"
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo -e "${YELLOW}Habilitando APIs necesarias...${NC}"
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com

# Verificar si la instancia ya existe
if gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID &> /dev/null; then
    echo -e "${YELLOW}La instancia $INSTANCE_NAME ya existe. Saltando creación...${NC}"
else
    # Crear instancia de Cloud SQL
    echo -e "${YELLOW}Creando instancia de Cloud SQL...${NC}"
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=$TIER \
        --region=$REGION \
        --network=default \
        --no-assign-ip \
        --database-flags=max_connections=100 \
        --backup \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --maintenance-release-channel=production \
        --deletion-protection

    echo -e "${GREEN}✓ Instancia creada exitosamente${NC}"
fi

# Esperar a que la instancia esté lista
echo -e "${YELLOW}Esperando a que la instancia esté lista...${NC}"
gcloud sql operations wait \
    $(gcloud sql operations list --instance=$INSTANCE_NAME --limit=1 --format="value(name)") \
    --project=$PROJECT_ID || true

# Crear base de datos
echo -e "${YELLOW}Creando base de datos...${NC}"
if gcloud sql databases describe $DATABASE_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID &> /dev/null; then
    echo -e "${YELLOW}La base de datos $DATABASE_NAME ya existe. Saltando creación...${NC}"
else
    gcloud sql databases create $DATABASE_NAME \
        --instance=$INSTANCE_NAME \
        --charset=UTF8 \
        --collation=en_US.UTF8

    echo -e "${GREEN}✓ Base de datos creada${NC}"
fi

# Crear usuario
echo -e "${YELLOW}Creando usuario de base de datos...${NC}"
if gcloud sql users list --instance=$INSTANCE_NAME --project=$PROJECT_ID | grep -q $DB_USER; then
    echo -e "${YELLOW}El usuario $DB_USER ya existe. Actualizando contraseña...${NC}"
    gcloud sql users set-password $DB_USER \
        --instance=$INSTANCE_NAME \
        --password=$DB_PASSWORD
else
    gcloud sql users create $DB_USER \
        --instance=$INSTANCE_NAME \
        --password=$DB_PASSWORD
    
    echo -e "${GREEN}✓ Usuario creado${NC}"
fi

# Obtener información de conexión
echo -e "${GREEN}=== Información de Conexión ===${NC}"
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
PRIVATE_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")

echo "Connection Name: $CONNECTION_NAME"
echo "Private IP: $PRIVATE_IP"
echo "Database: $DATABASE_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""

# Guardar configuración en archivo .env
echo -e "${YELLOW}Guardando configuración en .env.gcp...${NC}"
cat > .env.gcp << EOF
# Cloud SQL Configuration
CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME
CLOUD_SQL_PRIVATE_IP=$PRIVATE_IP
DATABASE_NAME=$DATABASE_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$PRIVATE_IP:5432/$DATABASE_NAME

# Para Cloud Run (usando Unix socket)
DATABASE_URL_CLOUD_RUN=postgresql://$DB_USER:$DB_PASSWORD@/$DATABASE_NAME?host=/cloudsql/$CONNECTION_NAME
EOF

echo -e "${GREEN}✓ Configuración guardada en .env.gcp${NC}"
echo ""

# Configurar backups automáticos
echo -e "${YELLOW}Configurando backups automáticos...${NC}"
gcloud sql instances patch $INSTANCE_NAME \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --retained-backups-count=7 \
    --retained-transaction-log-days=7

echo -e "${GREEN}✓ Backups configurados (retención: 7 días)${NC}"

# Mostrar información de backups
echo -e "${GREEN}=== Configuración de Backups ===${NC}"
echo "Hora de backup: 03:00 UTC"
echo "Retención: 7 días"
echo "Transaction logs: 7 días"
echo ""

# Instrucciones finales
echo -e "${GREEN}=== Instancia de Cloud SQL Creada Exitosamente ===${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Guarda la contraseña de forma segura"
echo "2. Configura las variables de entorno en tu aplicación"
echo "3. Ejecuta las migraciones de Django:"
echo "   python manage.py migrate"
echo ""
echo -e "${YELLOW}Para conectarte desde Cloud Run:${NC}"
echo "Usa la variable DATABASE_URL_CLOUD_RUN del archivo .env.gcp"
echo ""
echo -e "${YELLOW}Para conectarte localmente (requiere Cloud SQL Proxy):${NC}"
echo "cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:5432"
echo ""
