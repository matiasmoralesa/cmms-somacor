#!/bin/bash

# Script para configurar y ejecutar Cloud SQL Proxy para desarrollo local
# Uso: ./cloud-sql-proxy-setup.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Cargar configuración
if [ -f .env.gcp ]; then
    source .env.gcp
else
    echo "Error: Archivo .env.gcp no encontrado"
    echo "Ejecuta primero: ./01-create-cloud-sql.sh"
    exit 1
fi

echo -e "${GREEN}=== Configurando Cloud SQL Proxy ===${NC}"
echo ""

# Verificar si cloud_sql_proxy está instalado
if ! command -v cloud_sql_proxy &> /dev/null; then
    echo -e "${YELLOW}Cloud SQL Proxy no está instalado. Instalando...${NC}"
    
    # Detectar sistema operativo
    OS=$(uname -s)
    if [ "$OS" == "Linux" ]; then
        wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    elif [ "$OS" == "Darwin" ]; then
        curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
    else
        echo "Sistema operativo no soportado: $OS"
        exit 1
    fi
    
    chmod +x cloud_sql_proxy
    sudo mv cloud_sql_proxy /usr/local/bin/
    
    echo -e "${GREEN}✓ Cloud SQL Proxy instalado${NC}"
fi

# Crear directorio para socket Unix
mkdir -p /tmp/cloudsql

echo -e "${GREEN}Iniciando Cloud SQL Proxy...${NC}"
echo "Connection Name: $CLOUD_SQL_CONNECTION_NAME"
echo "Puerto local: 5432"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Ejecutar proxy
cloud_sql_proxy -instances=$CLOUD_SQL_CONNECTION_NAME=tcp:5432
