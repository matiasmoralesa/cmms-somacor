#!/bin/bash

# Script para crear topics y subscriptions de Cloud Pub/Sub para CMMS
# Uso: ./03-create-pubsub-topics.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}

# Topics
TOPIC_NOTIFICATIONS="notifications"
TOPIC_EVENTS="events"
TOPIC_ALERTS="alerts"

echo -e "${GREEN}=== Configurando Cloud Pub/Sub ===${NC}"
echo "Project ID: $PROJECT_ID"
echo ""

# Verificar proyecto
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar API
echo -e "${YELLOW}Habilitando Cloud Pub/Sub API...${NC}"
gcloud services enable pubsub.googleapis.com

# Función para crear topic
create_topic() {
    local topic_name=$1
    local description=$2
    
    echo -e "${YELLOW}Creando topic: $topic_name${NC}"
    
    if gcloud pubsub topics describe $topic_name --project=$PROJECT_ID &> /dev/null; then
        echo -e "${YELLOW}El topic $topic_name ya existe. Saltando...${NC}"
    else
        gcloud pubsub topics create $topic_name \
            --message-retention-duration=7d \
            --labels=environment=production,application=cmms
        
        echo -e "${GREEN}✓ Topic creado: $topic_name${NC}"
    fi
}

# Función para crear subscription
create_subscription() {
    local subscription_name=$1
    local topic_name=$2
    local description=$3
    
    echo -e "${YELLOW}Creando subscription: $subscription_name${NC}"
    
    if gcloud pubsub subscriptions describe $subscription_name --project=$PROJECT_ID &> /dev/null; then
        echo -e "${YELLOW}La subscription $subscription_name ya existe. Saltando...${NC}"
    else
        gcloud pubsub subscriptions create $subscription_name \
            --topic=$topic_name \
            --ack-deadline=60 \
            --message-retention-duration=7d \
            --expiration-period=never \
            --labels=environment=production,application=cmms
        
        echo -e "${GREEN}✓ Subscription creada: $subscription_name${NC}"
    fi
}

# Crear topics
echo ""
echo -e "${GREEN}Creando topics...${NC}"

create_topic $TOPIC_NOTIFICATIONS "Notificaciones del sistema"
create_topic $TOPIC_EVENTS "Eventos de negocio"
create_topic $TOPIC_ALERTS "Alertas y predicciones"

# Crear subscriptions
echo ""
echo -e "${GREEN}Creando subscriptions...${NC}"

# Subscriptions para notificaciones
create_subscription "notifications-backend" $TOPIC_NOTIFICATIONS "Backend processor"
create_subscription "notifications-telegram" $TOPIC_NOTIFICATIONS "Telegram bot"

# Subscriptions para eventos
create_subscription "events-processor" $TOPIC_EVENTS "Event processor"
create_subscription "events-webhook" $TOPIC_EVENTS "Webhook delivery"

# Subscriptions para alertas
create_subscription "alerts-processor" $TOPIC_ALERTS "Alert processor"
create_subscription "alerts-telegram" $TOPIC_ALERTS "Telegram alerts"

# Configurar dead letter topics
echo ""
echo -e "${YELLOW}Configurando dead letter topics...${NC}"

# Crear dead letter topic
DLQ_TOPIC="dead-letter-queue"
create_topic $DLQ_TOPIC "Dead letter queue para mensajes fallidos"

# Actualizar subscriptions con DLQ
for sub in notifications-backend events-processor alerts-processor; do
    echo -e "${YELLOW}Configurando DLQ para $sub...${NC}"
    gcloud pubsub subscriptions update $sub \
        --dead-letter-topic=$DLQ_TOPIC \
        --max-delivery-attempts=5
done

# Configurar permisos
echo ""
echo -e "${GREEN}Configurando permisos...${NC}"

SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

# Dar permisos de publisher a los topics
for topic in $TOPIC_NOTIFICATIONS $TOPIC_EVENTS $TOPIC_ALERTS; do
    echo -e "${YELLOW}Configurando permisos para topic $topic...${NC}"
    gcloud pubsub topics add-iam-policy-binding $topic \
        --member=serviceAccount:$SERVICE_ACCOUNT \
        --role=roles/pubsub.publisher
done

# Dar permisos de subscriber a las subscriptions
for sub in notifications-backend notifications-telegram events-processor events-webhook alerts-processor alerts-telegram; do
    echo -e "${YELLOW}Configurando permisos para subscription $sub...${NC}"
    gcloud pubsub subscriptions add-iam-policy-binding $sub \
        --member=serviceAccount:$SERVICE_ACCOUNT \
        --role=roles/pubsub.subscriber
done

# Guardar configuración
echo ""
echo -e "${YELLOW}Guardando configuración...${NC}"
cat >> .env.gcp << EOF

# Cloud Pub/Sub Topics
GCP_PUBSUB_TOPIC_NOTIFICATIONS=$TOPIC_NOTIFICATIONS
GCP_PUBSUB_TOPIC_EVENTS=$TOPIC_EVENTS
GCP_PUBSUB_TOPIC_ALERTS=$TOPIC_ALERTS
GCP_PUBSUB_DLQ_TOPIC=$DLQ_TOPIC
EOF

echo -e "${GREEN}✓ Configuración guardada en .env.gcp${NC}"

# Mostrar resumen
echo ""
echo -e "${GREEN}=== Cloud Pub/Sub Configurado Exitosamente ===${NC}"
echo ""
echo "📢 Topics creados:"
echo "   - $TOPIC_NOTIFICATIONS"
echo "   - $TOPIC_EVENTS"
echo "   - $TOPIC_ALERTS"
echo "   - $DLQ_TOPIC (Dead Letter Queue)"
echo ""
echo "📥 Subscriptions creadas:"
echo "   Notifications:"
echo "     - notifications-backend"
echo "     - notifications-telegram"
echo "   Events:"
echo "     - events-processor"
echo "     - events-webhook"
echo "   Alerts:"
echo "     - alerts-processor"
echo "     - alerts-telegram"
echo ""
echo "⚙️  Configuración:"
echo "   - Retención de mensajes: 7 días"
echo "   - ACK deadline: 60 segundos"
echo "   - Dead letter queue configurado"
echo "   - Max delivery attempts: 5"
echo ""

# Probar publicación
echo -e "${YELLOW}Probando publicación de mensaje...${NC}"
gcloud pubsub topics publish $TOPIC_NOTIFICATIONS \
    --message='{"test": true, "message": "Test message from setup script"}' \
    --attribute=source=setup-script

echo -e "${GREEN}✓ Mensaje de prueba publicado${NC}"
echo ""

echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configura las variables de entorno en tu aplicación"
echo "2. Implementa los subscribers en tu código"
echo "3. Monitorea los mensajes en Cloud Console:"
echo "   https://console.cloud.google.com/cloudpubsub/topic/list?project=$PROJECT_ID"
echo ""
