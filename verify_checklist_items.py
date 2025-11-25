import os
import sys
import django

# Setup Django
sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.checklists.models import ChecklistTemplate

# Verificar todos los templates
templates = ChecklistTemplate.objects.all().order_by('code')

print("=" * 80)
print("VERIFICACIÓN DE CHECKLISTS COMPLETOS")
print("=" * 80)

for template in templates:
    print(f"\n📋 {template.name}")
    print(f"   Código: {template.code}")
    print(f"   Tipo de vehículo: {template.vehicle_type}")
    print(f"   Total items: {len(template.items)}")
    print(f"   Sistema: {'Sí' if template.is_system_template else 'No'}")
    
    # Mostrar secciones
    sections = {}
    for item in template.items:
        section = item['section']
        if section not in sections:
            sections[section] = 0
        sections[section] += 1
    
    print(f"   Secciones:")
    for section, count in sections.items():
        print(f"      • {section}: {count} items")
    
    # Mostrar primeros 3 items
    print(f"   Primeros 3 items:")
    for item in template.items[:3]:
        print(f"      {item['order']}. [{item['section']}] {item['question']}")

print("\n" + "=" * 80)
print(f"✅ Total de templates: {templates.count()}")
print(f"✅ Total de items: {sum(len(t.items) for t in templates)}")
print("=" * 80)
