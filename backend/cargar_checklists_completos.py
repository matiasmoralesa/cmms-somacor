"""
Script para cargar plantillas completas de checklist desde los PDFs
a la base de datos de producción
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.checklists.models import ChecklistTemplate

def cargar_plantillas_completas():
    """Carga todas las plantillas de checklist desde los PDFs"""
    
    # Definir todas las plantillas basadas en los PDFs
    plantillas = [
        {
            "code": "F-PR-020-CH01",
            "name": "Check List Camionetas MDO",
            "vehicle_type": "CAMIONETA_MDO",
            "description": "Checklist diario para Camionetas MDO según formato F-PR-020-CH01",
            "passing_score": 80,
            "items": [
                {"section": "I - Auto Evaluación del Operador", "order": 1, "question": "Cumplo con descanso suficiente y condiciones para manejo seguro", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "I - Auto Evaluación del Operador", "order": 2, "question": "Cumplo con condiciones físicas adecuadas y no tengo dolencias o enfermedades que me impidan conducir", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "I - Auto Evaluación del Operador", "order": 3, "question": "Estoy consciente de mi responsabilidad al conducir, sin poner en riesgo mi integridad ni la de mis compañeros o patrimonio", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "II - Documentación del Operador", "order": 4, "question": "Licencia Municipal", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "II - Documentación del Operador", "order": 5, "question": "Licencia interna de Faena", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 6, "question": "Permiso de Circulación", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 7, "question": "Revisión Técnica", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 8, "question": "Seguro Obligatorio", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 9, "question": "Cinturones de Seguridad en buen estado", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 10, "question": "Espejos interior y exterior en condiciones y limpios", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 11, "question": "Frenos (incluye freno de mano) en condiciones operativas", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 12, "question": "Neumáticos en buen estado (incluye dos repuestos)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 13, "question": "Luces (Altas, Bajas, Frenos, intermitentes, retroceso)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 14, "question": "Vidrios y parabrisas limpios", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "III - Requisitos", "order": 15, "question": "Gata y llave de rueda disponible", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 16, "question": "Baliza y pértiga (funcionando y en condiciones)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 17, "question": "Radio Base funciona en todos los canales", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 18, "question": "Limpiaparabrisas funciona correctamente", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 19, "question": "Bocina en buen estado", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 20, "question": "Orden y Aseo (interior vehículo y pick up)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 21, "question": "Estado de carrocería, parachoques, portalón", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 22, "question": "Sello caja de operación invierno en buenas condiciones", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 23, "question": "Cuñas de seguridad disponibles (2)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "IV - Condiciones Complementarias", "order": 24, "question": "Aire acondicionado/calefacción", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ]
        },
        {
            "code": "F-PR-034-CH01",
            "name": "Check List Retroexcavadora MDO",
            "vehicle_type": "RETROEXCAVADORA",
            "description": "Inspección diaria para Retroexcavadora según formato F-PR-034-CH01",
            "passing_score": 85,
            "items": [
                # Motor
                {"section": "1. MOTOR", "order": 1, "question": "Nivel de Agua", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 2, "question": "Nivel de Aceite", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 3, "question": "Nivel de Hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 4, "question": "Batería", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 5, "question": "Correas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 6, "question": "Filtraciones (Aceite / Combustible)", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "1. MOTOR", "order": 7, "question": "Alternador", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 8, "question": "Partida en Frío", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 9, "question": "Radiador / Anticongelante", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 10, "question": "Motor Arranque", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Luces
                {"section": "2. LUCES", "order": 11, "question": "Focos faeneros", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "2. LUCES", "order": 12, "question": "Luces Bajas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 13, "question": "Luces Intermitentes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 14, "question": "Luz Marcha Atrás", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 15, "question": "Luz Interior", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 16, "question": "Luz Patente", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 17, "question": "Luz Tablero", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 18, "question": "Luz Baliza", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 19, "question": "Luz Pértiga", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 20, "question": "Luces de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 21, "question": "Estado de Micas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Documentos
                {"section": "3. DOCUMENTOS VIGENTES", "order": 22, "question": "Permiso de Circulación (si aplicase)", "response_type": "yes_no", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS VIGENTES", "order": 23, "question": "Revisión Técnica (si aplicase)", "response_type": "yes_no", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS VIGENTES", "order": 24, "question": "Seguro Obligatorio (si aplicase)", "response_type": "yes_no", "required": True, "observations_allowed": True},
                # Accesorios
                {"section": "4. ACCESORIOS", "order": 25, "question": "Extintor (8-10 kilos) (A-B-C)/Sistema AFEX", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 26, "question": "Llave de Rueda", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 27, "question": "Conos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 28, "question": "Cinturón de Seguridad", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 29, "question": "Chapas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 30, "question": "Calefacción", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 31, "question": "Limpia parabrisas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 32, "question": "Vidrios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 33, "question": "Manillas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 34, "question": "Asiento", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 35, "question": "Espejo Retrovisor", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 36, "question": "Espejos Laterales", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 37, "question": "Estado de Carrocería en General", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 38, "question": "Bocina / Alarma de Retroceso", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 39, "question": "Aire Acondicionado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 40, "question": "Cuñas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 41, "question": "Estado de neumáticos", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 42, "question": "Seguros en tuercas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 43, "question": "Dirección (Mecánica o Hidráulica)", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 44, "question": "Tubo de Escape", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Frenos
                {"section": "5. FRENOS", "order": 45, "question": "Freno de Servicio", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "5. FRENOS", "order": 46, "question": "Freno Parqueo", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                # Elementos Retroexcavadora
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 47, "question": "Juego Pasador Balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 48, "question": "Juego Bujes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 49, "question": "Desgaste Cuchillos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 50, "question": "Desgaste Dientes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 51, "question": "Desgaste Cadena", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 52, "question": "Sistema Hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 53, "question": "Mangueras Hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 54, "question": "Conexiones Hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 55, "question": "Sistema corta corriente", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 56, "question": "Estado de Aguilón", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 57, "question": "Martillo Hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. ELEMENTOS RETROEXCAVADORA", "order": 58, "question": "Mandos Operacionales", "response_type": "good_bad", "required": True, "observations_allowed": True}
            ]
        },
        {
            "code": "F-PR-037-CH01",
            "name": "Check List Cargador Frontal MDO",
            "vehicle_type": "CARGADOR_FRONTAL",
            "description": "Inspección diaria para Cargador Frontal según formato F-PR-037-CH01",
            "passing_score": 85,
            "items": [
                # Motor
                {"section": "1. MOTOR", "order": 1, "question": "Nivel de Agua", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 2, "question": "Nivel de Aceite", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 3, "question": "Nivel de Líquido de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 4, "question": "Batería", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 5, "question": "Correas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 6, "question": "Filtraciones", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 7, "question": "Alternador", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 8, "question": "Partida en Frío", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 9, "question": "Radiador / Anticongelante", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 10, "question": "Motor Arranque", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Luces
                {"section": "2. LUCES", "order": 11, "question": "Luces Altas", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "2. LUCES", "order": 12, "question": "Luces Bajas", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "2. LUCES", "order": 13, "question": "Luces Intermitentes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 14, "question": "Luz Marcha Atrás", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 15, "question": "Luz Interior", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 16, "question": "Luz Patente", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 17, "question": "Luz Tablero", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 18, "question": "Luz Baliza", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 19, "question": "Luz Pértiga", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 20, "question": "Luces de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 21, "question": "Estado de Micas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Documentos
                {"section": "3. DOCUMENTOS", "order": 22, "question": "Permiso de Circulación", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS", "order": 23, "question": "Revisión Técnica", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS", "order": 24, "question": "Seguro Obligatorio", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Accesorios
                {"section": "4. ACCESORIOS", "order": 25, "question": "Cinturón de Seguridad", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 26, "question": "Extintor (8-10 kilos) (A-B-C)/ Sistema AFEX", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 27, "question": "Marcadores", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 28, "question": "Triángulos / Conos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 29, "question": "Chapas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 30, "question": "Calefacción", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 31, "question": "Limpia parabrisas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 32, "question": "Vidrios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 33, "question": "Manillas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 34, "question": "Asiento", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 35, "question": "Espejo Retrovisor", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 36, "question": "Espejos Laterales", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 37, "question": "Estado de Carrocería en General", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 38, "question": "Bocina / Alarma de Retroceso", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 39, "question": "Aire Acondicionado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 40, "question": "Cuñas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 41, "question": "Estado de neumáticos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 42, "question": "Seguros en tuercas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 43, "question": "Dirección (Mecánica o Hidráulica)", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 44, "question": "Tubo de Escape", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 45, "question": "Estado pasamanos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 46, "question": "Escaleras de acceso", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 47, "question": "Se ha sobrecargado el sistema eléctrico original del equipo?", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Frenos
                {"section": "5. FRENOS", "order": 48, "question": "Freno de Servicio", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "5. FRENOS", "order": 49, "question": "Freno de Parqueo", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                # Cargador Frontal
                {"section": "6. CARGADOR FRONTAL", "order": 50, "question": "Grietas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 51, "question": "Indicador de Angulo", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 52, "question": "Calzas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 53, "question": "Seguros", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 54, "question": "Balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 55, "question": "Sistema hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 56, "question": "Mangueras hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 57, "question": "Conexiones hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 58, "question": "Sistema Corta Corriente", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "6. CARGADOR FRONTAL", "order": 59, "question": "Desgaste dientes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 60, "question": "Mandos Operacional", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "6. CARGADOR FRONTAL", "order": 61, "question": "Sistema de Levante", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "6. CARGADOR FRONTAL", "order": 62, "question": "Sistema Engrase", "response_type": "good_bad", "required": True, "observations_allowed": True}
            ]
        },
        {
            "code": "F-PR-040-CH01",
            "name": "Check List Minicargador MDO",
            "vehicle_type": "MINICARGADOR",
            "description": "Inspección diaria para Minicargador según formato F-PR-040-CH01",
            "passing_score": 85,
            "items": [
                # Motor
                {"section": "1. MOTOR", "order": 1, "question": "Nivel de Agua", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 2, "question": "Nivel de Aceite", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "1. MOTOR", "order": 3, "question": "Nivel de Líquido de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "1. MOTOR", "order": 4, "question": "Combustible", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 5, "question": "Batería", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 6, "question": "Correas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 7, "question": "Filtraciones", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 8, "question": "Alternador", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 9, "question": "Partida en Frío", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 10, "question": "Radiador / Anticongelante", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "1. MOTOR", "order": 11, "question": "Motor Arranque", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Luces
                {"section": "2. LUCES", "order": 12, "question": "Luces Altas", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "2. LUCES", "order": 13, "question": "Luces Bajas", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "2. LUCES", "order": 14, "question": "Luces Intermitentes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 15, "question": "Luz Marcha Atrás", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 16, "question": "Focos Faeneros", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 17, "question": "Luz Patente", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 18, "question": "Luz Tablero", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 19, "question": "Luz Baliza", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 20, "question": "Luz Pértiga", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 21, "question": "Luces de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "2. LUCES", "order": 22, "question": "Estado de Micas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Documentos
                {"section": "3. DOCUMENTOS", "order": 23, "question": "Permiso de Circulación", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS", "order": 24, "question": "Revisión Técnica", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "3. DOCUMENTOS", "order": 25, "question": "Seguro Obligatorio", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Accesorios
                {"section": "4. ACCESORIOS", "order": 26, "question": "Botiquín", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 27, "question": "Extintor (8-10 kilos) (A-B-C) /Sistema AFEX", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 28, "question": "Llave de Rueda", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 29, "question": "Triángulos / Conos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 30, "question": "Cinturón de Seguridad", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 31, "question": "Marcadores", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 32, "question": "Señaléticas en Español", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 33, "question": "Manual de operación en Español", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 34, "question": "Instrumentos en buen estado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 35, "question": "Sistema Corta corriente", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 36, "question": "Revisión de tres puntos de apoyo", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 37, "question": "Puerta en buen estado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 38, "question": "Chapas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 39, "question": "Manillas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 40, "question": "Limpia parabrisas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 41, "question": "Cinta reflectante", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 42, "question": "Vidrios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 43, "question": "Protección contra volcamiento", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 44, "question": "Asiento con regulador y certificado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 45, "question": "Espejo Retrovisor", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 46, "question": "Espejos Laterales", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 47, "question": "Estado de Carrocería en General", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 48, "question": "Bocina / Alarma de Retroceso", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 49, "question": "Aire Acondicionado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 50, "question": "Cuñas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 51, "question": "Estado de neumáticos", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 52, "question": "Seguros en tuercas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 53, "question": "Dirección (Mecánica o Hidráulica)", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "4. ACCESORIOS", "order": 54, "question": "Tubo de Escape", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 55, "question": "Parada de Emergencia Exterior Equipo", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "4. ACCESORIOS", "order": 56, "question": "Se ha sobrecargado el sistema eléctrico original del equipo?", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                # Estado Mecánico
                {"section": "5. ESTADO MECÁNICO", "order": 57, "question": "Avanzar", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "5. ESTADO MECÁNICO", "order": 58, "question": "Retroceder", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                # Frenos
                {"section": "6. FRENOS", "order": 59, "question": "Freno de Servicio", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                {"section": "6. FRENOS", "order": 60, "question": "Freno de Parqueo", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True},
                # Cargador
                {"section": "7. CARGADOR", "order": 61, "question": "Balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 62, "question": "Cuchillo de balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 63, "question": "Porte cuchilla balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 64, "question": "Seguros manuales de balde", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 65, "question": "Conexión inferior", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 66, "question": "Sistema hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 67, "question": "Mangueras hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 68, "question": "Conexiones hidráulicas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 69, "question": "Sistema Corta Corriente", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 70, "question": "Desgaste dientes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "7. CARGADOR", "order": 71, "question": "Estado de los mandos del balde", "response_type": "good_bad", "required": True, "observations_allowed": True, "is_critical": True}
            ]
        },
        {
            "code": "CL-SUPERSUCKER",
            "name": "Check List Camión Supersucker",
            "vehicle_type": "CAMION_SUPERSUCKER",
            "description": "Checklist diario para Camión Supersucker",
            "passing_score": 80,
            "items": [
                # Luces
                {"section": "LUCES", "order": 1, "question": "Luz baja", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 2, "question": "Luz Alta", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 3, "question": "Luz Marcha Atrás", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 4, "question": "Luz Interior", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 5, "question": "Luz de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 6, "question": "Tercera Luz de Freno", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 7, "question": "Intermitentes", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 8, "question": "Luz Patente", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 9, "question": "Baliza y conexión eléctrica", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "LUCES", "order": 10, "question": "Pértiga y conexión eléctrica", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Documentos
                {"section": "DOCUMENTOS", "order": 11, "question": "Permiso de Circulación", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "DOCUMENTOS", "order": 12, "question": "Revisión Técnica", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "DOCUMENTOS", "order": 13, "question": "Tarjeta de mantención", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "DOCUMENTOS", "order": 14, "question": "Seguro Obligatorio", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "DOCUMENTOS", "order": 15, "question": "Tarjeta o llave combustible", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "DOCUMENTOS", "order": 16, "question": "G.P.S.", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Aspirado
                {"section": "ASPIRADO", "order": 17, "question": "Bomba aspiradora", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ASPIRADO", "order": 18, "question": "Inspección ducto de succión", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ASPIRADO", "order": 19, "question": "Inspección mangueras de succión", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ASPIRADO", "order": 20, "question": "Sistema control descarga hidráulico", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Neumáticos
                {"section": "NEUMÁTICOS", "order": 21, "question": "Delanteros", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "NEUMÁTICOS", "order": 22, "question": "Traseros", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "NEUMÁTICOS", "order": 23, "question": "Repuestos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "NEUMÁTICOS", "order": 24, "question": "Revisión de Tuercas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "NEUMÁTICOS", "order": 25, "question": "Barra interna /certificado", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Accesorios
                {"section": "ACCESORIOS", "order": 26, "question": "Extintor, Botiquín, Triángulos", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 27, "question": "Espejos Retrovisores", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 28, "question": "Cinturón de Seguridad", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 29, "question": "Logotipo", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 30, "question": "Chapas de Puertas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 31, "question": "Cuñas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 32, "question": "Bocina", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 33, "question": "Gata y manivela", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 34, "question": "Parabrisas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 35, "question": "Llave rueda", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 36, "question": "Vidrios laterales", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 37, "question": "Plumillas Limpia Vidrios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 38, "question": "Bolso Herramientas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 39, "question": "Manillas Alza vidrios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 40, "question": "Batería", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 41, "question": "Nivel de Agua", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 42, "question": "Nivel de Aceite", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 43, "question": "Correas de accesorios", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ACCESORIOS", "order": 44, "question": "Verificar gases de escape", "response_type": "good_bad", "required": True, "observations_allowed": True},
                # Alta Montaña
                {"section": "ALTA MONTAÑA", "order": 45, "question": "Saco", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 46, "question": "Cadenas para nieve", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 47, "question": "Tensores de cadenas", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 48, "question": "Pala", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 49, "question": "Estrobos remolque", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 50, "question": "Linterna", "response_type": "good_bad", "required": True, "observations_allowed": True},
                {"section": "ALTA MONTAÑA", "order": 51, "question": "Frazadas", "response_type": "good_bad", "required": True, "observations_allowed": True}
            ]
        }
    ]
    
    print("Iniciando carga de plantillas completas de checklist...")
    print(f"Total de plantillas a cargar: {len(plantillas)}\n")
    
    # Eliminar plantillas antiguas (simplificadas) que no están basadas en PDFs
    print("Eliminando plantillas antiguas simplificadas...")
    plantillas_antiguas = ChecklistTemplate.objects.exclude(
        code__in=['F-PR-020-CH01', 'F-PR-034-CH01', 'F-PR-037-CH01', 'F-PR-040-CH01', 'CL-SUPERSUCKER']
    )
    count_eliminadas = plantillas_antiguas.count()
    if count_eliminadas > 0:
        plantillas_antiguas.delete()
        print(f"   {count_eliminadas} plantillas antiguas eliminadas\n")
    else:
        print("   No hay plantillas antiguas para eliminar\n")
    
    for plantilla_data in plantillas:
        code = plantilla_data["code"]
        print(f"Procesando: {plantilla_data['name']} ({code})")
        
        # Eliminar plantilla existente si existe
        ChecklistTemplate.objects.filter(code=code).delete()
        print(f"   Plantilla anterior eliminada (si existia)")
        
        # Los items ya están en el formato correcto como lista
        # No necesitamos extraerlos, solo crear la plantilla
        
        # Crear plantilla con items incluidos
        template = ChecklistTemplate.objects.create(
            code=plantilla_data["code"],
            name=plantilla_data["name"],
            vehicle_type=plantilla_data["vehicle_type"],
            description=plantilla_data["description"],
            passing_score=plantilla_data["passing_score"],
            items=plantilla_data["items"],
            is_system_template=True  # Marcar como plantilla del sistema
        )
        print(f"   Plantilla creada: {template.name}")
        print(f"   {len(plantilla_data['items'])} items incluidos")
        print(f"   Plantilla {code} completada\n")
    
    print("Todas las plantillas han sido cargadas exitosamente!")
    print(f"\nResumen:")
    print(f"   - Total plantillas: {ChecklistTemplate.objects.count()}")
    total_items = sum(len(t.items) for t in ChecklistTemplate.objects.all())
    print(f"   - Total items: {total_items}")

if __name__ == "__main__":
    cargar_plantillas_completas()
