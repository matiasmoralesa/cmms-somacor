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

checklists = []

# ============================================================================
# 1. CAMIÓN SUPERSUCKER (51 items)
# ============================================================================
supersucker_items = [
    # Luces (10 items)
    create_item("Luces", 1, "Luz baja"),
    create_item("Luces", 2, "Luz Alta"),
    create_item("Luces", 3, "Luz Marcha Atrás"),
    create_item("Luces", 4, "Luz Interior"),
    create_item("Luces", 5, "Luz de Freno"),
    create_item("Luces", 6, "Tercera Luz de Freno"),
    create_item("Luces", 7, "Intermitentes"),
    create_item("Luces", 8, "Luz Patente"),
    create_item("Luces", 9, "Baliza y conexión eléctrica"),
    create_item("Luces", 10, "Pértiga y conexión eléctrica"),
    # Documentos (6 items)
    create_item("Documentos", 11, "Permiso de Circulación"),
    create_item("Documentos", 12, "Revisión Técnica"),
    create_item("Documentos", 13, "Tarjeta de mantención"),
    create_item("Documentos", 14, "Seguro Obligatorio"),
    create_item("Documentos", 15, "Tarjeta o llave combustible"),
    create_item("Documentos", 16, "G.P.S."),
    # Aspirado (4 items)
    create_item("Aspirado", 17, "Bomba aspiradora"),
    create_item("Aspirado", 18, "Inspección ducto de succión"),
    create_item("Aspirado", 19, "Inspección mangueras de succión"),
    create_item("Aspirado", 20, "Sistema control descarga hidráulico"),
    # Neumáticos (4 items)
    create_item("Neumáticos", 21, "Delanteros"),
    create_item("Neumáticos", 22, "Traseros"),
    create_item("Neumáticos", 23, "Repuestos"),
    create_item("Neumáticos", 24, "Revisión de Tuercas"),
    # Accesorios (20 items)
    create_item("Accesorios", 25, "Barra interna /certificado"),
    create_item("Accesorios", 26, "Extintor, Botiquín, Triángulos"),
    create_item("Accesorios", 27, "Espejos Retrovisores"),
    create_item("Accesorios", 28, "Cinturón de Seguridad"),
    create_item("Accesorios", 29, "Logotipo"),
    create_item("Accesorios", 30, "Chapas de Puertas"),
    create_item("Accesorios", 31, "Cuñas"),
    create_item("Accesorios", 32, "Bocina"),
    create_item("Accesorios", 33, "Gata y manivela"),
    create_item("Accesorios", 34, "Parabrisas"),
    create_item("Accesorios", 35, "Llave rueda"),
    create_item("Accesorios", 36, "Vidrios laterales"),
    create_item("Accesorios", 37, "Plumillas Limpia Vidrios"),
    create_item("Accesorios", 38, "Bolso Herramientas"),
    create_item("Accesorios", 39, "Manillas Alza vidrios"),
    create_item("Accesorios", 40, "Batería"),
    create_item("Accesorios", 41, "Nivel de Agua"),
    create_item("Accesorios", 42, "Nivel de Aceite"),
    create_item("Accesorios", 43, "Correas de accesorios"),
    create_item("Accesorios", 44, "Verificar gases de escape"),
    # Alta Montaña (7 items opcionales)
    create_item("Alta Montaña", 45, "Saco", False),
    create_item("Alta Montaña", 46, "Cadenas para nieve", False),
    create_item("Alta Montaña", 47, "Tensores de cadenas", False),
    create_item("Alta Montaña", 48, "Pala", False),
    create_item("Alta Montaña", 49, "Estrobos remolque", False),
    create_item("Alta Montaña", 50, "Linterna", False),
    create_item("Alta Montaña", 51, "Frazadas", False),
]

checklists.append({
    "code": "SUPERSUCKER-CH01",
    "name": "Check List Camión Supersucker",
    "vehicle_type": "CAMION_SUPERSUCKER",
    "description": "Checklist de inspección diaria para Camión Supersucker - Chequeo de Vehículos",
    "is_system_template": True,
    "passing_score": 80,
    "items": supersucker_items
})

print(f"✓ Camión Supersucker: {len(supersucker_items)} items")

# ============================================================================
# 2. CAMIONETAS MDO (21 items)
# ============================================================================
camioneta_items = [
    # Requisitos (12 items)
    create_item("Requisitos", 1, "Espejos interior y exterior en condiciones y limpios"),
    create_item("Requisitos", 2, "Frenos (incluye freno de mano) en condiciones operativas"),
    create_item("Requisitos", 3, "Neumáticos en buen estado (incluye dos repuestos)"),
    create_item("Requisitos", 4, "Luces (Altas, Bajas, Frenos, intermitentes, retroceso)"),
    create_item("Requisitos", 5, "Sello caja de operación invierno en buenas condiciones"),
    create_item("Requisitos", 6, "Gata y llave de rueda disponible"),
    create_item("Requisitos", 7, "Vidrios y parabrisas limpios"),
    create_item("Requisitos", 8, "Baliza y pértiga (funcionando y en condiciones)"),
    create_item("Requisitos", 9, "Radio Base funciona en todos los canales"),
    create_item("Requisitos", 10, "Limpiaparabrisas funciona correctamente"),
    create_item("Requisitos", 11, "Bocina en buen estado"),
    create_item("Requisitos", 12, "Aire acondicionado/ calefacción"),
    # Requisitos Complementarios (4 items)
    create_item("Requisitos Complementarios", 13, "Orden y Aseo (interior vehículo y pick up)"),
    create_item("Requisitos Complementarios", 14, "Estado de carrocería, parachoques, portalón"),
    create_item("Requisitos Complementarios", 15, "Cinturones de Seguridad en buen estado"),
    create_item("Requisitos Complementarios", 16, "Cuñas de seguridad disponibles (2)"),
    # Documentación (5 items)
    create_item("Documentación", 17, "Licencia Municipal"),
    create_item("Documentación", 18, "Licencia interna de Faena"),
    create_item("Documentación", 19, "Permiso de Circulación"),
    create_item("Documentación", 20, "Revisión Técnica"),
    create_item("Documentación", 21, "Seguro Obligatorio"),
]

checklists.append({
    "code": "F-PR-020-CH01",
    "name": "Check List Camionetas MDO",
    "vehicle_type": "CAMIONETA_MDO",
    "description": "Checklist de inspección diaria para Camionetas MDO",
    "is_system_template": True,
    "passing_score": 80,
    "items": camioneta_items
})

print(f"✓ Camionetas MDO: {len(camioneta_items)} items")

# ============================================================================
# 3. RETROEXCAVADORA MDO (63 items)
# ============================================================================
retro_items = [
    # Motor (10 items)
    create_item("Motor", 1, "Nivel de Agua"),
    create_item("Motor", 2, "Nivel de Aceite"),
    create_item("Motor", 3, "Nivel de Hidráulico"),
    create_item("Motor", 4, "Batería"),
    create_item("Motor", 5, "Correas"),
    create_item("Motor", 6, "Filtraciones (Aceite / Combustible)"),
    create_item("Motor", 7, "Alternador"),
    create_item("Motor", 8, "Partida en Frío"),
    create_item("Motor", 9, "Radiador / Anticongelante"),
    create_item("Motor", 10, "Motor Arranque"),
    # Luces (11 items)
    create_item("Luces", 11, "Focos faeneros"),
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
    create_item("Documentos", 22, "Permiso de Circulación (si aplicase)"),
    create_item("Documentos", 23, "Revisión Técnica (si aplicase)"),
    create_item("Documentos", 24, "Seguro Obligatorio (si aplicase)"),
    # Accesorios (22 items)
    create_item("Accesorios", 25, "Extintor (8-10 kilos) (A-B-C)/Sistema AFEX"),
    create_item("Accesorios", 26, "Llave de Rueda"),
    create_item("Accesorios", 27, "Conos"),
    create_item("Accesorios", 28, "Cinturón de Seguridad"),
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
    # Frenos (2 items)
    create_item("Frenos", 45, "Freno de Servicio"),
    create_item("Frenos", 46, "Freno Parqueo"),
    # Elementos Retroexcavadora (13 items)
    create_item("Elementos Retroexcavadora", 47, "Juego Pasador Balde"),
    create_item("Elementos Retroexcavadora", 48, "Juego Bujes"),
    create_item("Elementos Retroexcavadora", 49, "Desgaste Cuchillos"),
    create_item("Elementos Retroexcavadora", 50, "Desgaste Dientes"),
    create_item("Elementos Retroexcavadora", 51, "Degaste Cadena"),
    create_item("Elementos Retroexcavadora", 52, "Sistema Hidráulico"),
    create_item("Elementos Retroexcavadora", 53, "Mangueras Hidráulicas"),
    create_item("Elementos Retroexcavadora", 54, "Conexiones Hidráulicas"),
    create_item("Elementos Retroexcavadora", 55, "Sistema corta corriente"),
    create_item("Elementos Retroexcavadora", 56, "Estado de Aguilón"),
    create_item("Elementos Retroexcavadora", 57, "Martillo Hidráulico"),
    create_item("Elementos Retroexcavadora", 58, "Mandos Operacionales"),
]

checklists.append({
    "code": "F-PR-034-CH01",
    "name": "Check Retroexcavadora MDO",
    "vehicle_type": "RETROEXCAVADORA_MDO",
    "description": "Checklist de inspección diaria para Retroexcavadora MDO",
    "is_system_template": True,
    "passing_score": 80,
    "items": retro_items
})

print(f"✓ Retroexcavadora MDO: {len(retro_items)} items")

# Guardar JSON
with open('backend/apps/checklists/fixtures/checklist_templates.json', 'w', encoding='utf-8') as f:
    json.dump(checklists, f, ensure_ascii=False, indent=2)

print(f"\n✓ Archivo generado con {len(checklists)} checklists")
print("✓ Total de items:", sum(len(c['items']) for c in checklists))
