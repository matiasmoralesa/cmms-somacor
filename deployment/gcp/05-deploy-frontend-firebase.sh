#!/bin/bash

# Script para desplegar frontend a Firebase Hosting
# Uso: ./05-deploy-frontend-firebase.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
BACKEND_URL=${SERVICE_URL:-""}

echo -e "${GREEN}=== Desplegando Frontend a Firebase Hosting ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Backend URL: $BACKEND_URL"
echo ""

# Verificar proyecto
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}Error: Debes configurar GCP_PROJECT_ID${NC}"
    exit 1
fi

# Cargar configuración
if [ -f .env.gcp ]; then
    source .env.gcp
    BACKEND_URL=${SERVICE_URL:-$BACKEND_URL}
else
    echo -e "${YELLOW}Advertencia: Archivo .env.gcp no encontrado${NC}"
fi

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}Error: SERVICE_URL no está configurado${NC}"
    echo "Ejecuta primero: ./04-deploy-backend-cloud-run.sh"
    exit 1
fi

# Verificar que Firebase CLI esté instalado
if ! command -v firebase &> /dev/null; then
    echo -e "${YELLOW}Firebase CLI no está instalado. Instalando...${NC}"
    npm install -g firebase-tools
fi

# Ir al directorio del frontend
cd ../../frontend

# Verificar que node_modules exista
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Instalando dependencias...${NC}"
    npm install
fi

# Crear archivo de configuración de Firebase si no existe
if [ ! -f "firebase.json" ]; then
    echo -e "${YELLOW}Creando firebase.json...${NC}"
    cat > firebase.json << EOF
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "**/*.@(jpg|jpeg|gif|png|svg|webp|ico)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "index.html",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      }
    ]
  }
}
EOF
fi

# Crear .firebaserc si no existe
if [ ! -f ".firebaserc" ]; then
    echo -e "${YELLOW}Creando .firebaserc...${NC}"
    cat > .firebaserc << EOF
{
  "projects": {
    "default": "$PROJECT_ID"
  }
}
EOF
fi

# Crear archivo .env.production con la URL del backend
echo -e "${YELLOW}Configurando variables de entorno...${NC}"
cat > .env.production << EOF
VITE_API_URL=${BACKEND_URL}/api/v1
VITE_ENVIRONMENT=production
EOF

echo -e "${GREEN}✓ Variables de entorno configuradas${NC}"

# Construir aplicación
echo ""
echo -e "${YELLOW}Construyendo aplicación...${NC}"
npm run build

echo -e "${GREEN}✓ Build completado${NC}"

# Login a Firebase (si es necesario)
echo ""
echo -e "${YELLOW}Verificando autenticación de Firebase...${NC}"
if ! firebase projects:list &> /dev/null; then
    echo -e "${YELLOW}Necesitas autenticarte en Firebase${NC}"
    firebase login
fi

# Inicializar Firebase si es necesario
if [ ! -f ".firebaserc" ] || ! grep -q "$PROJECT_ID" .firebaserc; then
    echo -e "${YELLOW}Inicializando Firebase...${NC}"
    firebase use --add $PROJECT_ID
fi

# Desplegar a Firebase Hosting
echo ""
echo -e "${YELLOW}Desplegando a Firebase Hosting...${NC}"
firebase deploy --only hosting --project $PROJECT_ID

echo -e "${GREEN}✓ Frontend desplegado exitosamente${NC}"

# Obtener URL de Firebase Hosting
HOSTING_URL="https://${PROJECT_ID}.web.app"

echo ""
echo -e "${GREEN}=== Despliegue Completado ===${NC}"
echo ""
echo "🌐 URL del frontend: $HOSTING_URL"
echo "🔗 URL alternativa: https://${PROJECT_ID}.firebaseapp.com"
echo ""
echo "📋 Aplicación disponible en:"
echo "   $HOSTING_URL"
echo ""

# Guardar URL en configuración
echo "FRONTEND_URL=$HOSTING_URL" >> ../gcp/.env.gcp

# Probar que el sitio esté disponible
echo -e "${YELLOW}Probando disponibilidad del sitio...${NC}"
sleep 5
if curl -f "$HOSTING_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Sitio disponible${NC}"
else
    echo -e "${RED}✗ Sitio no disponible aún (puede tomar unos minutos)${NC}"
fi

echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configura un dominio personalizado en Firebase Console"
echo "2. Actualiza CORS en el backend para permitir el dominio del frontend"
echo "3. Prueba la aplicación en: $HOSTING_URL"
echo ""
echo -e "${YELLOW}Para actualizar el frontend:${NC}"
echo "   npm run build && firebase deploy --only hosting"
echo ""
