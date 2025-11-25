import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.checklists.models import ChecklistTemplate, ChecklistTemplateItem

def create_camionetas_mdo():
    """F-PR-020-CH01 Check List Camionetas MDO"""
    template, created = ChecklistTemplate.objects.get_or_create(
        code="F-PR-020-CH01",
        defaults={
            "name": "Check List Camionetas MDO",
            "vehicle_type": "CAMIONETA_MDO",
            "description": "Checklist diario para Camionetas MDO",
            "is_system_template": True,
            "passing_score": 80
        }
    )
    
    if created:
        items = [
            # I - Auto Evaluación
            ("I - Auto Evaluación", 1, "Cumplo con descanso suficiente y condiciones para manejo seguro"),
            ("I - Auto Evaluación", 2, "Cumplo con condiciones físicas adecuadas sin dolencias"),
            ("I - Auto Evaluación", 3, "Consciente de responsabilidad al conducir"),
            
            # II - Documentación Operador
            ("II - Documentación Operador", 4, "Licencia Municipal"),
            ("II - Documentación Operador", 5, "Licencia interna de Faena"),
            
            # III - Requisitos
            ("III - Requisitos", 6, "Permiso de Circulación"),
            ("III - Requisitos", 7, "Revisión Técnica"),
            ("III - Requisitos", 8, "Seguro Obligatorio"),
            ("III - Requisitos", 9, "Cinturones de Seguridad en buen estado"),
            ("III - Requisitos", 10, "Espejos interior y exterior limpios"),
            ("III - Requisitos", 11, "Frenos (incluye freno de mano) operativos"),
            ("III - Requisitos", 12, "Neumáticos en buen estado (incluye repuestos)"),
            ("III - Requisitos", 13, "Luces (Altas, Bajas, Frenos, intermitentes)"),
            ("III - Requisitos", 14, "Vidrios y parabrisas limpios"),
            ("III - Requisitos", 15, "Gata y llave de rueda disponible"),
            
            # IV - Complementarios
            ("IV - Complementarios", 16, "Baliza y pértiga funcionando"),
            ("IV - Complementarios", 17, "Radio Base funciona en todos los canales"),
            ("IV - Complementarios", 18, "Limpiaparabrisas funciona"),
            ("IV - Complementarios", 19, "Bocina en buen estado"),
            ("IV - Complementarios", 20, "Orden y Aseo interior"),
            ("IV - Complementarios", 21, "Estado carrocería y parachoques"),
            ("IV - Complementarios", 22, "Cuñas de seguridad (2)"),
            ("IV - Complementarios", 23, "Aire acondicionado/calefacción"),
        ]
        
        for section, order, question in items:
            ChecklistTemplateItem.objects.create(
                template=template,
                section=section,
                order=order,
                question=question,
                response_type="yes_no_na",
                required=True,
                observations_allowed=True
            )
        print(f"✓ Creada plantilla: {template.name} con {len(items)} items")
    else:
        print(f"- Plantilla ya existe: {template.name}")

def create_supersucker():
    """Check List Camión Supersucker"""
    template, created = ChecklistTemplate.objects.get_or_create(
        code="CH-SUPERSUCKER-01",
        defaults={
            "name": "Check List Camión Supersucker",
            "vehicle_type": "CAMION_SUPERSUCKER",
            "description": "Checklist diario para Camión Supersucker",
            "is_system_template": True,
            "passing_score": 80
        }
    )
    
    if created:
        items = [
            # Auto Evaluación
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para manejo seguro"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas sin dolencias"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad al conducir"),
            
            # Documentación
            ("Documentación", 4, "Licencia Municipal vigente"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Permiso de Circulación"),
            ("Documentación", 7, "Revisión Técnica vigente"),
            ("Documentación", 8, "Seguro Obligatorio"),
            
            # Seguridad
            ("Seguridad", 9, "Cinturones de seguridad operativos"),
            ("Seguridad", 10, "Espejos retrovisores limpios y ajustados"),
            ("Seguridad", 11, "Sistema de frenos operativo"),
            ("Seguridad", 12, "Freno de mano operativo"),
            ("Seguridad", 13, "Luces delanteras y traseras"),
            ("Seguridad", 14, "Luces de freno e intermitentes"),
            ("Seguridad", 15, "Bocina operativa"),
            
            # Neumáticos
            ("Neumáticos", 16, "Presión de neumáticos adecuada"),
            ("Neumáticos", 17, "Estado de neumáticos (sin cortes ni desgaste excesivo)"),
            ("Neumáticos", 18, "Neumático de repuesto disponible"),
            
            # Fluidos
            ("Fluidos", 19, "Nivel de aceite motor"),
            ("Fluidos", 20, "Nivel de líquido refrigerante"),
            ("Fluidos", 21, "Nivel de líquido de frenos"),
            ("Fluidos", 22, "Nivel de combustible"),
            
            # Equipo Supersucker
            ("Equipo Supersucker", 23, "Mangueras de succión en buen estado"),
            ("Equipo Supersucker", 24, "Sistema de vacío operativo"),
            ("Equipo Supersucker", 25, "Tanque sin fugas"),
            ("Equipo Supersucker", 26, "Válvulas de descarga operativas"),
            ("Equipo Supersucker", 27, "Filtros limpios"),
            
            # Complementarios
            ("Complementarios", 28, "Baliza y señalización"),
            ("Complementarios", 29, "Radio de comunicación"),
            ("Complementarios", 30, "Extintor vigente"),
            ("Complementarios", 31, "Botiquín de primeros auxilios"),
            ("Complementarios", 32, "Cuñas de seguridad"),
            ("Complementarios", 33, "Orden y limpieza de cabina"),
        ]
        
        for section, order, question in items:
            ChecklistTemplateItem.objects.create(
                template=template,
                section=section,
                order=order,
                question=question,
                response_type="yes_no_na",
                required=True,
                observations_allowed=True
            )
        print(f"✓ Creada plantilla: {template.name} con {len(items)} items")
    else:
        print(f"- Plantilla ya existe: {template.name}")

def create_retroexcavadora():
    """F-PR-034-CH01 Check Retroexcavadora MDO"""
    template, created = ChecklistTemplate.objects.get_or_create(
        code="F-PR-034-CH01",
        defaults={
            "name": "Check List Retroexcavadora MDO",
            "vehicle_type": "RETROEXCAVADORA",
            "description": "Checklist diario para Retroexcavadora MDO",
            "is_system_template": True,
            "passing_score": 80
        }
    )
    
    if created:
        items = [
            # Auto Evaluación
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para operación segura"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad al operar"),
            
            # Documentación
            ("Documentación", 4, "Licencia Municipal clase D"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Certificación de operador"),
            
            # Seguridad General
            ("Seguridad General", 7, "Cinturón de seguridad operativo"),
            ("Seguridad General", 8, "Espejos retrovisores"),
            ("Seguridad General", 9, "Bocina operativa"),
            ("Seguridad General", 10, "Alarma de retroceso"),
            ("Seguridad General", 11, "Luces de trabajo"),
            ("Seguridad General", 12, "Baliza operativa"),
            
            # Sistema Hidráulico
            ("Sistema Hidráulico", 13, "Nivel de aceite hidráulico"),
            ("Sistema Hidráulico", 14, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 15, "Cilindros hidráulicos operativos"),
            ("Sistema Hidráulico", 16, "Controles de movimiento suaves"),
            
            # Motor y Fluidos
            ("Motor y Fluidos", 17, "Nivel de aceite motor"),
            ("Motor y Fluidos", 18, "Nivel de refrigerante"),
            ("Motor y Fluidos", 19, "Nivel de combustible"),
            ("Motor y Fluidos", 20, "Filtro de aire limpio"),
            
            # Frenos y Neumáticos
            ("Frenos y Neumáticos", 21, "Freno de servicio operativo"),
            ("Frenos y Neumáticos", 22, "Freno de estacionamiento"),
            ("Frenos y Neumáticos", 23, "Presión de neumáticos"),
            ("Frenos y Neumáticos", 24, "Estado de neumáticos"),
            
            # Implementos
            ("Implementos", 25, "Balde delantero sin grietas"),
            ("Implementos", 26, "Dientes del balde en buen estado"),
            ("Implementos", 27, "Brazo retroexcavador operativo"),
            ("Implementos", 28, "Balde retroexcavador sin daños"),
            ("Implementos", 29, "Pasadores y seguros en su lugar"),
            
            # Cabina
            ("Cabina", 30, "Vidrios limpios y sin daños"),
            ("Cabina", 31, "Limpiaparabrisas operativo"),
            ("Cabina", 32, "Asiento en buen estado"),
            ("Cabina", 33, "Controles e instrumentos operativos"),
            ("Cabina", 34, "Orden y limpieza"),
            
            # Complementarios
            ("Complementarios", 35, "Extintor vigente"),
            ("Complementarios", 36, "Cuñas de seguridad"),
            ("Complementarios", 37, "Radio de comunicación"),
        ]
        
        for section, order, question in items:
            ChecklistTemplateItem.objects.create(
                template=template,
                section=section,
                order=order,
                question=question,
                response_type="yes_no_na",
                required=True,
                observations_allowed=True
            )
        print(f"✓ Creada plantilla: {template.name} con {len(items)} items")
    else:
        print(f"- Plantilla ya existe: {template.name}")

def create_cargador_frontal():
    """F-PR-037-CH01 Check List Cargador Frontal MDO"""
    template, created = ChecklistTemplate.objects.get_or_create(
        code="F-PR-037-CH01",
        defaults={
            "name": "Check List Cargador Frontal MDO",
            "vehicle_type": "CARGADOR_FRONTAL",
            "description": "Checklist diario para Cargador Frontal MDO",
            "is_system_template": True,
            "passing_score": 80
        }
    )
    
    if created:
        items = [
            # Auto Evaluación
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para operación"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad"),
            
            # Documentación
            ("Documentación", 4, "Licencia Municipal clase D"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Certificación de operador"),
            
            # Seguridad
            ("Seguridad", 7, "Cinturón de seguridad"),
            ("Seguridad", 8, "Espejos retrovisores"),
            ("Seguridad", 9, "Bocina operativa"),
            ("Seguridad", 10, "Alarma de retroceso"),
            ("Seguridad", 11, "Luces de trabajo"),
            ("Seguridad", 12, "Baliza"),
            ("Seguridad", 13, "Extintor vigente"),
            
            # Sistema Hidráulico
            ("Sistema Hidráulico", 14, "Nivel aceite hidráulico"),
            ("Sistema Hidráulico", 15, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 16, "Cilindros de levante operativos"),
            ("Sistema Hidráulico", 17, "Cilindro de volteo operativo"),
            ("Sistema Hidráulico", 18, "Controles suaves"),
            
            # Motor
            ("Motor", 19, "Nivel aceite motor"),
            ("Motor", 20, "Nivel refrigerante"),
            ("Motor", 21, "Nivel combustible"),
            ("Motor", 22, "Filtro aire limpio"),
            ("Motor", 23, "Batería cargada"),
            
            # Frenos y Transmisión
            ("Frenos y Transmisión", 24, "Freno de servicio"),
            ("Frenos y Transmisión", 25, "Freno de estacionamiento"),
            ("Frenos y Transmisión", 26, "Transmisión sin ruidos anormales"),
            
            # Neumáticos
            ("Neumáticos", 27, "Presión adecuada"),
            ("Neumáticos", 28, "Estado general sin cortes"),
            ("Neumáticos", 29, "Tuercas apretadas"),
            
            # Balde y Brazos
            ("Balde y Brazos", 30, "Balde sin grietas"),
            ("Balde y Brazos", 31, "Cuchilla de corte en buen estado"),
            ("Balde y Brazos", 32, "Brazos de levante sin daños"),
            ("Balde y Brazos", 33, "Pasadores y seguros"),
            
            # Cabina
            ("Cabina", 34, "Vidrios limpios"),
            ("Cabina", 35, "Limpiaparabrisas"),
            ("Cabina", 36, "Asiento ajustable"),
            ("Cabina", 37, "Instrumentos operativos"),
            ("Cabina", 38, "Orden y limpieza"),
            
            # Complementarios
            ("Complementarios", 39, "Cuñas de seguridad"),
            ("Complementarios", 40, "Radio comunicación"),
        ]
        
        for section, order, question in items:
            ChecklistTemplateItem.objects.create(
                template=template,
                section=section,
                order=order,
                question=question,
                response_type="yes_no_na",
                required=True,
                observations_allowed=True
            )
        print(f"✓ Creada plantilla: {template.name} con {len(items)} items")
    else:
        print(f"- Plantilla ya existe: {template.name}")

def create_minicargador():
    """F-PR-040-CH01 Check List Minicargador MDO"""
    template, created = ChecklistTemplate.objects.get_or_create(
        code="F-PR-040-CH01",
        defaults={
            "name": "Check List Minicargador MDO",
            "vehicle_type": "MINICARGADOR",
            "description": "Checklist diario para Minicargador MDO",
            "is_system_template": True,
            "passing_score": 80
        }
    )
    
    if created:
        items = [
            # Auto Evaluación
            ("Auto Evaluación", 1, "Descanso suficiente"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad"),
            
            # Documentación
            ("Documentación", 4, "Licencia Municipal"),
            ("Documentación", 5, "Licencia interna Faena"),
            ("Documentación", 6, "Certificación operador"),
            
            # Seguridad
            ("Seguridad", 7, "Cinturón seguridad"),
            ("Seguridad", 8, "Barra protección ROPS"),
            ("Seguridad", 9, "Bocina"),
            ("Seguridad", 10, "Alarma retroceso"),
            ("Seguridad", 11, "Luces trabajo"),
            ("Seguridad", 12, "Baliza"),
            
            # Sistema Hidráulico
            ("Sistema Hidráulico", 13, "Nivel aceite hidráulico"),
            ("Sistema Hidráulico", 14, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 15, "Cilindros operativos"),
            ("Sistema Hidráulico", 16, "Controles suaves"),
            
            # Motor
            ("Motor", 17, "Nivel aceite motor"),
            ("Motor", 18, "Nivel refrigerante"),
            ("Motor", 19, "Nivel combustible"),
            ("Motor", 20, "Filtro aire"),
            
            # Frenos y Cadenas
            ("Frenos y Cadenas", 21, "Frenos operativos"),
            ("Frenos y Cadenas", 22, "Freno estacionamiento"),
            ("Frenos y Cadenas", 23, "Tensión cadenas/neumáticos"),
            ("Frenos y Cadenas", 24, "Estado cadenas/neumáticos"),
            
            # Implementos
            ("Implementos", 25, "Balde sin daños"),
            ("Implementos", 26, "Cuchilla buen estado"),
            ("Implementos", 27, "Brazos levante operativos"),
            ("Implementos", 28, "Sistema acople rápido"),
            ("Implementos", 29, "Pasadores seguros"),
            
            # Cabina/Controles
            ("Cabina/Controles", 30, "Vidrios limpios"),
            ("Cabina/Controles", 31, "Asiento buen estado"),
            ("Cabina/Controles", 32, "Controles operativos"),
            ("Cabina/Controles", 33, "Instrumentos funcionando"),
            ("Cabina/Controles", 34, "Orden limpieza"),
            
            # Complementarios
            ("Complementarios", 35, "Extintor vigente"),
            ("Complementarios", 36, "Cuñas seguridad"),
            ("Complementarios", 37, "Radio comunicación"),
        ]
        
        for section, order, question in items:
            ChecklistTemplateItem.objects.create(
                template=template,
                section=section,
                order=order,
                question=question,
                response_type="yes_no_na",
                required=True,
                observations_allowed=True
            )
        print(f"✓ Creada plantilla: {template.name} con {len(items)} items")
    else:
        print(f"- Plantilla ya existe: {template.name}")

if __name__ == "__main__":
    print("Creando plantillas de checklist...\n")
    
    create_camionetas_mdo()
    create_supersucker()
    create_retroexcavadora()
    create_cargador_frontal()
    create_minicargador()
    
    print("\n✓ Proceso completado")
    print(f"Total plantillas en sistema: {ChecklistTemplate.objects.count()}")
