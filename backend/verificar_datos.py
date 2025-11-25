import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.assets.models import Location, Asset
from apps.checklists.models import ChecklistTemplate
from apps.predictions.models import FailurePrediction
from apps.inventory.models import SparePart
from apps.work_orders.models import WorkOrder

print("=== VERIFICACION DE DATOS ===")
print(f"Ubicaciones: {Location.objects.count()}")
print(f"Activos: {Asset.objects.count()}")
print(f"Plantillas checklist: {ChecklistTemplate.objects.count()}")
print(f"Predicciones: {FailurePrediction.objects.count()}")
print(f"Repuestos: {SparePart.objects.count()}")
print(f"Ordenes: {WorkOrder.objects.count()}")

if Location.objects.exists():
    print("\nPrimeras 3 ubicaciones:")
    for loc in Location.objects.all()[:3]:
        print(f"  - {loc.name}")

if ChecklistTemplate.objects.exists():
    print("\nPlantillas de checklist:")
    for template in ChecklistTemplate.objects.all():
        print(f"  - {template.code}: {template.name} ({template.vehicle_type})")
