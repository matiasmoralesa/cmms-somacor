import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.checklists.models import ChecklistTemplate

# Get Camioneta template
template = ChecklistTemplate.objects.get(code='F-PR-020-CH01')

print("=" * 80)
print(f"Template: {template.name}")
print(f"Code: {template.code}")
print(f"Vehicle Type: {template.vehicle_type}")
print(f"Total Items: {len(template.items)}")
print("=" * 80)

print("\nVerificando estructura de items:")
for i, item in enumerate(template.items[:5]):
    print(f"\nItem {i+1}:")
    print(f"  Order: {item.get('order')}")
    print(f"  Section: {item.get('section')}")
    print(f"  Question: {item.get('question')}")
    print(f"  Response Type: {item.get('response_type')}")
    print(f"  Required: {item.get('required')}")
    print(f"  Observations Allowed: {item.get('observations_allowed')}")

print("\n" + "=" * 80)
print("Verificando que todos los items tengan los campos requeridos:")
missing_fields = []
for i, item in enumerate(template.items):
    required_fields = ['order', 'section', 'question', 'response_type', 'required', 'observations_allowed']
    for field in required_fields:
        if field not in item:
            missing_fields.append(f"Item {i+1} missing field: {field}")

if missing_fields:
    print("❌ Campos faltantes encontrados:")
    for msg in missing_fields:
        print(f"  - {msg}")
else:
    print("✅ Todos los items tienen los campos requeridos")

print("\n" + "=" * 80)
print("JSON del template (primeros 2 items):")
print(json.dumps(template.items[:2], indent=2, ensure_ascii=False))
