import json

def create_item(section, order, question, required=True):
    return {
        "section": section,
        "order": order,
        "question": question,
        "response_type": "yes_no_na",
        "required": required,
        "observations_allowed": True
    }

# Leer checklists existentes
with open('backend/apps/checklists/fixtures/checklist_templates.json', 'r', encoding='utf-8') as f:
    checklists = json.load(f)

# ============================================================================
# 4. CARGADOR FRONTAL MDO (68 items)
# ============================================================================
cargador_items = [
    # Motor (10 items)
    create_item("Motor", 1, "Nivel de Agua"),
    create_item("Motor", 2, "Nivel de Aceite"),
    create_item("Motor", 3, "Nivel de Líquido de Freno"),
    create_item("Motor", 4, "Batería"),
    create_item("Motor", 5, "Correas"),
    create_item("Motor", 6, "Filtraciones"),
    create_item("Motor", 7, "Alternador"),
    create_item("Motor", 8, "Partida en Frío"),
    create_item("Motor", 9, "Radiador / Anticongelante"),
    create_item("Motor", 10, "Motor Arranque"),
    # Luces (11 items)
    create_item("Luces", 11, "Luces Altas"),
    create_item("Luces", 12, "Luces Bajas"),
    create_item("Luces", 13, "Luces Intermitentes"),
    create_item("Luces", 14, "Luz Marcha Atrás"),
    create_item("Luces", 15, "Luz Interior"),
    create_item("Luces", 16, "Luz Patente"),
    create_item("Luces", 17, "Luz Tablero"),
    create_item("Luces", 18, "Luz Baliza"),
    create_item("Luces", 19, "Luz Pértiga"),
    create_item("Luces", 20, "Luces de Freno"),
    create_item("Luces", 21, "Estado de Micas"),
    # Documentos (3 items)
    create_item("Documentos", 22, "Permiso de Circulación"),
    create_item("Documentos", 23, "Revisión Técnica"),
    create_item("Documentos", 24, "Seguro Obligatorio"),
    # Accesorios (23 items)
    create_item("Accesorios", 25, "Cinturón de Seguridad"),
    create_item("Accesorios", 26, "Extintor (8-10 kilos) (A-B-C)/ Sistema AFEX"),
    create_item("Accesorios", 27, "Marcadores"),
    create_item("Accesorios", 28, "Triángulos / Conos"),
    create_item("Accesorios", 29, "Chapas de Puertas"),
    create_item("Accesorios", 30, "Calefacción"),
    create_item("Accesorios", 31, "Limpia parabrisas"),
    create_item("Accesorios", 32, "Vidrios"),
    create_item("Accesorios", 33, "Manillas de Puertas"),
    create_item("Accesorios", 34, "Asiento"),
    create_item("Accesorios", 35, "Espejo Retrovisor"),
    create_item("Accesorios", 36, "Espejos Laterales"),
    create_item("Accesorios", 37, "Estado de Carrocería en General"),
    create_item("Accesorios", 38, "Bocina / Alarma de Retroceso"),
    create_item("Accesorios", 39, "Aire Acondicionado"),
    create_item("Accesorios", 40, "Cuñas"),
    create_item("Accesorios", 41, "Estado de neumáticos"),
    create_item("Accesorios", 42, "Seguros en tuercas"),
    create_item("Accesorios", 43, "Dirección (Mecánica o Hidráulica)"),
    create_item("Accesorios", 44, "Tubo de Escape"),
    create_item("Accesorios", 45, "Estado pasamanos"),
    create_item("Accesorios", 46, "Escaleras de acceso"),
    create_item("Accesorios", 47, "Se ha sobrecargado el sistema eléctrico original del equipo?"),
    # Frenos (2 items)
    create_item("Frenos", 48, "Freno de Servicio"),
    create_item("Frenos", 49, "Freno de Parqueo"),
    # Cargador Frontal (13 items)
    create_item("Cargador Frontal", 50, "Grietas"),
    create_item("Cargador Frontal", 51, "Indicador de Angulo"),
    create_item("Cargador Frontal", 52, "Calzas"),
    create_item("Cargador Frontal", 53, "Seguros"),
    create_item("Cargador Frontal", 54, "Balde"),
    create_item("Cargador Frontal", 55, "Sistema hidráulico"),
    create_item("Cargador Frontal", 56, "Mangueras hidráulicas"),
    create_item("Cargador Frontal", 57, "Conexiones hidráulicas"),
    create_item("Cargador Frontal", 58, "Sistema Corta Corriente"),
    create_item("Cargador Frontal", 59, "Desgaste dientes"),
    create_item("Cargador Frontal", 60, "Mandos Operacional"),
    create_item("Cargador Frontal", 61, "Sistema de Levante"),
    create_item("Cargador Frontal", 62, "Sistema Engrase"),
]

checklists.append({
    "code": "F-PR-037-CH01",
    "name": "Check List Cargador Frontal MDO",
    "vehicle_type": "CARGADOR_FRONTAL_MDO",
    "description": "Checklist de inspección diaria para Cargador Frontal MDO",
    "is_system_template": True,
    "passing_score": 80,
    "items": cargador_items
})

print(f"✓ Cargador Frontal MDO: {len(cargador_items)} items")

# Guardar JSON actualizado
with open('backend/apps/checklists/fixtures/checklist_templates.json', 'w', encoding='utf-8') as f:
    json.dump(checklists, f, ensure_ascii=False, indent=2)

print(f"\n✓ Archivo actualizado con {len(checklists)} checklists")
print("✓ Total de items:", sum(len(c['items']) for c in checklists))
