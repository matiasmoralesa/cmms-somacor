#!/bin/bash

echo "=========================================="
echo "CARGANDO DATOS EN PRODUCCION"
echo "=========================================="
echo ""

# Configurar variables
export DJANGO_SETTINGS_MODULE="config.settings.production"
export DATABASE_URL="postgresql://cmms_user:Somacor2024!@34.31.236.19:5432/cmms_prod"
export DB_NAME="cmms_prod"
export DB_USER="cmms_user"
export DB_HOST="34.31.236.19"
export DB_PORT="5432"

# Cargar datos base
echo "[1/2] Cargando datos base..."
echo ""
python3 populate_data.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Datos base cargados exitosamente"
    echo ""
    
    # Cargar estados de maquinas
    echo "[2/2] Cargando estados de maquinas..."
    echo ""
    python3 agregar_machine_status.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "Estados cargados exitosamente"
    fi
fi

echo ""
echo "=========================================="
echo "PROCESO COMPLETADO"
echo "=========================================="
echo ""
echo "Credenciales de acceso:"
echo "  Usuario: admin@cmms.com"
echo "  Password: admin123"
echo ""
echo "=========================================="
