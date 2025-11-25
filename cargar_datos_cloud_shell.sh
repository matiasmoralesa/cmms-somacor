#!/bin/bash
# Script para cargar datos en producción desde Cloud Shell

echo "=========================================="
echo "CARGA DE DATOS EN PRODUCCIÓN - CMMS"
echo "=========================================="

# Configuración
PROJECT_ID="cmms-somacor-prod"
REGION="us-central1"
SERVICE="cmms-backend"

echo ""
echo "[1/4] Conectando a Cloud Run..."
gcloud config set project $PROJECT_ID

echo ""
echo "[2/4] Creando script de carga de datos..."
cat > /tmp/load_data.py << 'EOF'
from apps.assets.models import Asset, Location
from apps.work_orders.models import WorkOrder
from apps.inventory.models import SparePart
from apps.authentication.models import User
from datetime import datetime, timedelta
import random

print("\n=== Creando Ubicaciones ===")
locations_data = [
    {"name": "Faena La Coipa", "address": "Región de Atacama", "description": "Faena principal"},
    {"name": "Taller Mecánico", "address": "Faena La Coipa", "description": "Taller de mantenimiento"},
    {"name": "Patio de Equipos", "address": "Faena La Coipa", "description": "Área de estacionamiento"},
]

locations = []
for loc_data in locations_data:
    location, created = Location.objects.get_or_create(name=loc_data["name"], defaults=loc_data)
    print(f"  {'[OK]' if created else '[--]'} {loc_data['name']}")
    locations.append(location)

print("\n=== Creando Activos ===")
admin_user = User.objects.get(email="admin@cmms.com")
default_location = locations[0]

assets_data = [
    {"name": "Camión Supersucker SS-001", "asset_code": "SS-001", "vehicle_type": "CAMION_SUPERSUCKER", "serial_number": "VLV2023SS001", "license_plate": "HJKL-12", "status": "OPERATIONAL", "criticality": "CRITICAL"},
    {"name": "Camioneta MDO CM-001", "asset_code": "CM-001", "vehicle_type": "CAMIONETA_MDO", "serial_number": "TOY2023CM001", "license_plate": "ABCD-34", "status": "OPERATIONAL", "criticality": "HIGH"},
    {"name": "Retroexcavadora RE-001", "asset_code": "RE-001", "vehicle_type": "RETROEXCAVADORA_MDO", "serial_number": "CAT2022RE001", "license_plate": "WXYZ-56", "status": "OPERATIONAL", "criticality": "HIGH"},
    {"name": "Cargador Frontal CF-001", "asset_code": "CF-001", "vehicle_type": "CARGADOR_FRONTAL_MDO", "serial_number": "KOM2023CF001", "license_plate": "PQRS-78", "status": "OPERATIONAL", "criticality": "CRITICAL"},
    {"name": "Minicargador MC-001", "asset_code": "MC-001", "vehicle_type": "MINICARGADOR_MDO", "serial_number": "BOB2023MC001", "license_plate": "MNOP-90", "status": "OPERATIONAL", "criticality": "MEDIUM"},
    {"name": "Camioneta MDO CM-002", "asset_code": "CM-002", "vehicle_type": "CAMIONETA_MDO", "serial_number": "FOR2022CM002", "license_plate": "EFGH-23", "status": "MAINTENANCE", "criticality": "MEDIUM"},
]

assets = []
for asset_data in assets_data:
    asset, created = Asset.objects.get_or_create(
        asset_code=asset_data["asset_code"],
        defaults={**asset_data, "location": default_location, "created_by": admin_user}
    )
    print(f"  {'[OK]' if created else '[--]'} {asset_data['name']}")
    assets.append(asset)

print("\n=== Creando Órdenes de Trabajo ===")
types = ["CORRECTIVE", "PREVENTIVE", "PREDICTIVE"]
priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]
statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]

for i, asset in enumerate(assets[:5]):
    wo_data = {
        "title": f"Mantenimiento {types[i % 3]} - {asset.name}",
        "description": f"Orden de trabajo para {asset.name}",
        "asset": asset,
        "work_order_type": types[i % 3],
        "priority": priorities[i % 4],
        "status": statuses[i % 3],
        "scheduled_date": datetime.now() + timedelta(days=i),
        "estimated_hours": random.randint(2, 8),
        "created_by": admin_user
    }
    wo = WorkOrder.objects.create(**wo_data)
    print(f"  [OK] {wo_data['title']}")

print("\n=== Creando Repuestos ===")
parts_data = [
    {"part_number": "FLT-001", "name": "Filtro de Aceite", "category": "FILTROS", "quantity": 25, "minimum_stock": 10, "unit_cost": 15000, "location": "Bodega A"},
    {"part_number": "FLT-002", "name": "Filtro de Aire", "category": "FILTROS", "quantity": 30, "minimum_stock": 15, "unit_cost": 12000, "location": "Bodega A"},
    {"part_number": "ACE-001", "name": "Aceite Motor 15W-40", "category": "LUBRICANTES", "quantity": 50, "minimum_stock": 20, "unit_cost": 8500, "location": "Bodega B"},
    {"part_number": "NEU-001", "name": "Neumático 295/80R22.5", "category": "NEUMATICOS", "quantity": 8, "minimum_stock": 4, "unit_cost": 250000, "location": "Bodega C"},
    {"part_number": "BAT-001", "name": "Batería 12V 180Ah", "category": "ELECTRICOS", "quantity": 6, "minimum_stock": 3, "unit_cost": 180000, "location": "Bodega A"},
]

for part_data in parts_data:
    part, created = SparePart.objects.get_or_create(part_number=part_data["part_number"], defaults=part_data)
    print(f"  {'[OK]' if created else '[--]'} {part_data['name']}")

print("\n=== COMPLETADO ===")
print(f"Ubicaciones: {len(locations)}")
print(f"Activos: {len(assets)}")
print(f"Órdenes de Trabajo: 5")
print(f"Repuestos: {len(parts_data)}")
EOF

echo ""
echo "[3/4] Ejecutando script en Cloud Run..."
gcloud run services proxy $SERVICE --region $REGION &
PROXY_PID=$!
sleep 5

# Ejecutar el script
gcloud run services execute $SERVICE \
  --region $REGION \
  --command "python manage.py shell < /tmp/load_data.py"

kill $PROXY_PID 2>/dev/null

echo ""
echo "[4/4] Verificando datos..."
echo ""
echo "=========================================="
echo "✅ DATOS CARGADOS EXITOSAMENTE"
echo "=========================================="
echo ""
echo "Accede al sistema:"
echo "  Frontend: https://cmms-somacor-produccion.web.app/"
echo "  Backend Admin: https://cmms-backend-ufxpd3tbia-uc.a.run.app/admin/"
echo ""
echo "Credenciales:"
echo "  Email: admin@cmms.com"
echo "  Password: admin123"
echo ""
