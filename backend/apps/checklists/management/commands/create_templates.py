from django.core.management.base import BaseCommand
from apps.checklists.models import ChecklistTemplate


class Command(BaseCommand):
    help = 'Crea todas las plantillas de checklist del sistema'

    def handle(self, *args, **options):
        self.stdout.write("Creando plantillas de checklist...\n")
        
        self.create_camionetas_mdo()
        self.create_supersucker()
        self.create_retroexcavadora()
        self.create_cargador_frontal()
        self.create_minicargador()
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Proceso completado"))
        self.stdout.write(f"Total plantillas en sistema: {ChecklistTemplate.objects.count()}")

    def _create_template(self, code, name, vehicle_type, description, items_data):
        """Helper para crear plantillas"""
        items = [
            {
                "section": section,
                "order": order,
                "question": question,
                "response_type": "yes_no_na",
                "required": True,
                "observations_allowed": True
            }
            for section, order, question in items_data
        ]
        
        template, created = ChecklistTemplate.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "vehicle_type": vehicle_type,
                "description": description,
                "is_system_template": True,
                "passing_score": 80,
                "items": items
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Creada plantilla: {template.name} con {len(items)} items"))
        else:
            self.stdout.write(f"- Plantilla ya existe: {template.name}")

    def create_camionetas_mdo(self):
        """F-PR-020-CH01 Check List Camionetas MDO"""
        items_data = [
            ("I - Auto Evaluación", 1, "Cumplo con descanso suficiente y condiciones para manejo seguro"),
            ("I - Auto Evaluación", 2, "Cumplo con condiciones físicas adecuadas sin dolencias"),
            ("I - Auto Evaluación", 3, "Consciente de responsabilidad al conducir"),
            ("II - Documentación Operador", 4, "Licencia Municipal"),
            ("II - Documentación Operador", 5, "Licencia interna de Faena"),
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
            ("IV - Complementarios", 16, "Baliza y pértiga funcionando"),
            ("IV - Complementarios", 17, "Radio Base funciona en todos los canales"),
            ("IV - Complementarios", 18, "Limpiaparabrisas funciona"),
            ("IV - Complementarios", 19, "Bocina en buen estado"),
            ("IV - Complementarios", 20, "Orden y Aseo interior"),
            ("IV - Complementarios", 21, "Estado carrocería y parachoques"),
            ("IV - Complementarios", 22, "Cuñas de seguridad (2)"),
            ("IV - Complementarios", 23, "Aire acondicionado/calefacción"),
        ]
        
        self._create_template(
            "F-PR-020-CH01",
            "Check List Camionetas MDO",
            "CAMIONETA_MDO",
            "Checklist diario para Camionetas MDO",
            items_data
        )

    def create_supersucker(self):
        """Check List Camión Supersucker"""
        items_data = [
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para manejo seguro"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas sin dolencias"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad al conducir"),
            ("Documentación", 4, "Licencia Municipal vigente"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Permiso de Circulación"),
            ("Documentación", 7, "Revisión Técnica vigente"),
            ("Documentación", 8, "Seguro Obligatorio"),
            ("Seguridad", 9, "Cinturones de seguridad operativos"),
            ("Seguridad", 10, "Espejos retrovisores limpios y ajustados"),
            ("Seguridad", 11, "Sistema de frenos operativo"),
            ("Seguridad", 12, "Freno de mano operativo"),
            ("Seguridad", 13, "Luces delanteras y traseras"),
            ("Seguridad", 14, "Luces de freno e intermitentes"),
            ("Seguridad", 15, "Bocina operativa"),
            ("Neumáticos", 16, "Presión de neumáticos adecuada"),
            ("Neumáticos", 17, "Estado de neumáticos (sin cortes ni desgaste excesivo)"),
            ("Neumáticos", 18, "Neumático de repuesto disponible"),
            ("Fluidos", 19, "Nivel de aceite motor"),
            ("Fluidos", 20, "Nivel de líquido refrigerante"),
            ("Fluidos", 21, "Nivel de líquido de frenos"),
            ("Fluidos", 22, "Nivel de combustible"),
            ("Equipo Supersucker", 23, "Mangueras de succión en buen estado"),
            ("Equipo Supersucker", 24, "Sistema de vacío operativo"),
            ("Equipo Supersucker", 25, "Tanque sin fugas"),
            ("Equipo Supersucker", 26, "Válvulas de descarga operativas"),
            ("Equipo Supersucker", 27, "Filtros limpios"),
            ("Complementarios", 28, "Baliza y señalización"),
            ("Complementarios", 29, "Radio de comunicación"),
            ("Complementarios", 30, "Extintor vigente"),
            ("Complementarios", 31, "Botiquín de primeros auxilios"),
            ("Complementarios", 32, "Cuñas de seguridad"),
            ("Complementarios", 33, "Orden y limpieza de cabina"),
        ]
        
        self._create_template(
            "CH-SUPERSUCKER-01",
            "Check List Camión Supersucker",
            "CAMION_SUPERSUCKER",
            "Checklist diario para Camión Supersucker",
            items_data
        )

    def create_retroexcavadora(self):
        """F-PR-034-CH01 Check Retroexcavadora MDO"""
        items_data = [
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para operación segura"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad al operar"),
            ("Documentación", 4, "Licencia Municipal clase D"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Certificación de operador"),
            ("Seguridad General", 7, "Cinturón de seguridad operativo"),
            ("Seguridad General", 8, "Espejos retrovisores"),
            ("Seguridad General", 9, "Bocina operativa"),
            ("Seguridad General", 10, "Alarma de retroceso"),
            ("Seguridad General", 11, "Luces de trabajo"),
            ("Seguridad General", 12, "Baliza operativa"),
            ("Sistema Hidráulico", 13, "Nivel de aceite hidráulico"),
            ("Sistema Hidráulico", 14, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 15, "Cilindros hidráulicos operativos"),
            ("Sistema Hidráulico", 16, "Controles de movimiento suaves"),
            ("Motor y Fluidos", 17, "Nivel de aceite motor"),
            ("Motor y Fluidos", 18, "Nivel de refrigerante"),
            ("Motor y Fluidos", 19, "Nivel de combustible"),
            ("Motor y Fluidos", 20, "Filtro de aire limpio"),
            ("Frenos y Neumáticos", 21, "Freno de servicio operativo"),
            ("Frenos y Neumáticos", 22, "Freno de estacionamiento"),
            ("Frenos y Neumáticos", 23, "Presión de neumáticos"),
            ("Frenos y Neumáticos", 24, "Estado de neumáticos"),
            ("Implementos", 25, "Balde delantero sin grietas"),
            ("Implementos", 26, "Dientes del balde en buen estado"),
            ("Implementos", 27, "Brazo retroexcavador operativo"),
            ("Implementos", 28, "Balde retroexcavador sin daños"),
            ("Implementos", 29, "Pasadores y seguros en su lugar"),
            ("Cabina", 30, "Vidrios limpios y sin daños"),
            ("Cabina", 31, "Limpiaparabrisas operativo"),
            ("Cabina", 32, "Asiento en buen estado"),
            ("Cabina", 33, "Controles e instrumentos operativos"),
            ("Cabina", 34, "Orden y limpieza"),
            ("Complementarios", 35, "Extintor vigente"),
            ("Complementarios", 36, "Cuñas de seguridad"),
            ("Complementarios", 37, "Radio de comunicación"),
        ]
        
        self._create_template(
            "F-PR-034-CH01",
            "Check List Retroexcavadora MDO",
            "RETROEXCAVADORA",
            "Checklist diario para Retroexcavadora MDO",
            items_data
        )

    def create_cargador_frontal(self):
        """F-PR-037-CH01 Check List Cargador Frontal MDO"""
        items_data = [
            ("Auto Evaluación", 1, "Descanso suficiente y condiciones para operación"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad"),
            ("Documentación", 4, "Licencia Municipal clase D"),
            ("Documentación", 5, "Licencia interna de Faena"),
            ("Documentación", 6, "Certificación de operador"),
            ("Seguridad", 7, "Cinturón de seguridad"),
            ("Seguridad", 8, "Espejos retrovisores"),
            ("Seguridad", 9, "Bocina operativa"),
            ("Seguridad", 10, "Alarma de retroceso"),
            ("Seguridad", 11, "Luces de trabajo"),
            ("Seguridad", 12, "Baliza"),
            ("Seguridad", 13, "Extintor vigente"),
            ("Sistema Hidráulico", 14, "Nivel aceite hidráulico"),
            ("Sistema Hidráulico", 15, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 16, "Cilindros de levante operativos"),
            ("Sistema Hidráulico", 17, "Cilindro de volteo operativo"),
            ("Sistema Hidráulico", 18, "Controles suaves"),
            ("Motor", 19, "Nivel aceite motor"),
            ("Motor", 20, "Nivel refrigerante"),
            ("Motor", 21, "Nivel combustible"),
            ("Motor", 22, "Filtro aire limpio"),
            ("Motor", 23, "Batería cargada"),
            ("Frenos y Transmisión", 24, "Freno de servicio"),
            ("Frenos y Transmisión", 25, "Freno de estacionamiento"),
            ("Frenos y Transmisión", 26, "Transmisión sin ruidos anormales"),
            ("Neumáticos", 27, "Presión adecuada"),
            ("Neumáticos", 28, "Estado general sin cortes"),
            ("Neumáticos", 29, "Tuercas apretadas"),
            ("Balde y Brazos", 30, "Balde sin grietas"),
            ("Balde y Brazos", 31, "Cuchilla de corte en buen estado"),
            ("Balde y Brazos", 32, "Brazos de levante sin daños"),
            ("Balde y Brazos", 33, "Pasadores y seguros"),
            ("Cabina", 34, "Vidrios limpios"),
            ("Cabina", 35, "Limpiaparabrisas"),
            ("Cabina", 36, "Asiento ajustable"),
            ("Cabina", 37, "Instrumentos operativos"),
            ("Cabina", 38, "Orden y limpieza"),
            ("Complementarios", 39, "Cuñas de seguridad"),
            ("Complementarios", 40, "Radio comunicación"),
        ]
        
        self._create_template(
            "F-PR-037-CH01",
            "Check List Cargador Frontal MDO",
            "CARGADOR_FRONTAL",
            "Checklist diario para Cargador Frontal MDO",
            items_data
        )

    def create_minicargador(self):
        """F-PR-040-CH01 Check List Minicargador MDO"""
        items_data = [
            ("Auto Evaluación", 1, "Descanso suficiente"),
            ("Auto Evaluación", 2, "Condiciones físicas adecuadas"),
            ("Auto Evaluación", 3, "Consciente de responsabilidad"),
            ("Documentación", 4, "Licencia Municipal"),
            ("Documentación", 5, "Licencia interna Faena"),
            ("Documentación", 6, "Certificación operador"),
            ("Seguridad", 7, "Cinturón seguridad"),
            ("Seguridad", 8, "Barra protección ROPS"),
            ("Seguridad", 9, "Bocina"),
            ("Seguridad", 10, "Alarma retroceso"),
            ("Seguridad", 11, "Luces trabajo"),
            ("Seguridad", 12, "Baliza"),
            ("Sistema Hidráulico", 13, "Nivel aceite hidráulico"),
            ("Sistema Hidráulico", 14, "Mangueras sin fugas"),
            ("Sistema Hidráulico", 15, "Cilindros operativos"),
            ("Sistema Hidráulico", 16, "Controles suaves"),
            ("Motor", 17, "Nivel aceite motor"),
            ("Motor", 18, "Nivel refrigerante"),
            ("Motor", 19, "Nivel combustible"),
            ("Motor", 20, "Filtro aire"),
            ("Frenos y Cadenas", 21, "Frenos operativos"),
            ("Frenos y Cadenas", 22, "Freno estacionamiento"),
            ("Frenos y Cadenas", 23, "Tensión cadenas/neumáticos"),
            ("Frenos y Cadenas", 24, "Estado cadenas/neumáticos"),
            ("Implementos", 25, "Balde sin daños"),
            ("Implementos", 26, "Cuchilla buen estado"),
            ("Implementos", 27, "Brazos levante operativos"),
            ("Implementos", 28, "Sistema acople rápido"),
            ("Implementos", 29, "Pasadores seguros"),
            ("Cabina/Controles", 30, "Vidrios limpios"),
            ("Cabina/Controles", 31, "Asiento buen estado"),
            ("Cabina/Controles", 32, "Controles operativos"),
            ("Cabina/Controles", 33, "Instrumentos funcionando"),
            ("Cabina/Controles", 34, "Orden limpieza"),
            ("Complementarios", 35, "Extintor vigente"),
            ("Complementarios", 36, "Cuñas seguridad"),
            ("Complementarios", 37, "Radio comunicación"),
        ]
        
        self._create_template(
            "F-PR-040-CH01",
            "Check List Minicargador MDO",
            "MINICARGADOR",
            "Checklist diario para Minicargador MDO",
            items_data
        )
