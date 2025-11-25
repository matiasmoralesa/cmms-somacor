"""
Django management command to populate the database
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from faker import Faker

from apps.authentication.models import Role
from apps.assets.models import Asset, Location
from apps.work_orders.models import WorkOrder
from apps.inventory.models import SparePart, StockMovement
from apps.maintenance.models import MaintenancePlan
from apps.checklists.models import ChecklistTemplate

User = get_user_model()
fake = Faker('es_ES')


class Command(BaseCommand):
    help = 'Populate database with sample data including checklist templates'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('INICIANDO POBLACIÓN DE BASE DE DATOS CMMS')
        self.stdout.write('=' * 60)
        
        try:
            # Create checklist templates
            self.create_checklist_templates()
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('RESUMEN DE DATOS CREADOS')
            self.stdout.write('=' * 60)
            self.stdout.write('✓ Plantillas de checklist creadas exitosamente')
            self.stdout.write('=' * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error al poblar la base de datos: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise

    def create_checklist_templates(self):
        """Crear plantillas de checklists para los 5 tipos de vehículos basadas en los PDFs reales"""
        self.stdout.write('Creando plantillas de checklists...')
        
        templates_data = [
            {
                'code': 'F-PR-020-CH01',
                'name': 'Check List Camionetas MDO',
                'vehicle_type': 'CAMIONETA_MDO',
                'items': [
                    # I - AUTO EVALUACION DEL OPERADOR
                    {'section': 'I - Auto Evaluación del Operador', 'order': 1, 'question': 'Cumplo con descanso suficiente y condiciones para manejo seguro', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'I - Auto Evaluación del Operador', 'order': 2, 'question': 'Cumplo con condiciones físicas adecuadas y no tengo dolencias o enfermedades que me impidan conducir', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'I - Auto Evaluación del Operador', 'order': 3, 'question': 'Estoy consciente de mi responsabilidad al conducir, sin poner en riesgo mi integridad ni la de mis compañeros o patrimonio', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    # II - DOCUMENTACION DEL OPERADOR
                    {'section': 'II - Documentación del Operador', 'order': 4, 'question': 'Licencia Municipal', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'II - Documentación del Operador', 'order': 5, 'question': 'Licencia interna de Faena', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    # III - REQUISITOS
                    {'section': 'III - Requisitos', 'order': 6, 'question': 'Permiso de Circulación', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 7, 'question': 'Revisión Técnica', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 8, 'question': 'Seguro Obligatorio', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 9, 'question': 'Cinturones de Seguridad en buen estado', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 10, 'question': 'Espejos interior y exterior en condiciones y limpios', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 11, 'question': 'Frenos (incluye freno de mano) en condiciones operativas', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 12, 'question': 'Neumáticos en buen estado (incluye dos repuestos)', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 13, 'question': 'Luces (Altas, Bajas, Frenos, intermitentes, retroceso)', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 14, 'question': 'Vidrios y parabrisas limpios', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'III - Requisitos', 'order': 15, 'question': 'Gata y llave de rueda disponible', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    # IV - CONDICIONES PARA REQUISITOS COMPLEMENTARIOS
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 16, 'question': 'Baliza y pértiga (funcionando y en condiciones)', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 17, 'question': 'Radio Base funciona en todos los canales', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 18, 'question': 'Limpiaparabrisas funciona correctamente', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 19, 'question': 'Bocina en buen estado', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 20, 'question': 'Orden y Aseo (interior vehículo y pick up)', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 21, 'question': 'Estado de carrocería, parachoques, portalón', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 22, 'question': 'Sello caja de operación invierno en buenas condiciones', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 23, 'question': 'Cuñas de seguridad disponibles (2)', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                    {'section': 'IV - Condiciones para Requisitos Complementarios', 'order': 24, 'question': 'Aire acondicionado/calefacción', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                ]
            },
            # Continúa con las otras plantillas...
        ]
        
        created_templates = []
        for template_data in templates_data:
            template, created = ChecklistTemplate.objects.get_or_create(
                code=template_data['code'],
                defaults={
                    'name': template_data['name'],
                    'vehicle_type': template_data['vehicle_type'],
                    'description': f"Plantilla de checklist para {template_data['name']}",
                    'items': template_data['items'],
                    'is_system_template': True,
                    'passing_score': 80
                }
            )
            if created:
                self.stdout.write(f"  Creada plantilla: {template.code}")
            else:
                self.stdout.write(f"  Plantilla ya existe: {template.code}")
            created_templates.append(template)
        
        self.stdout.write(f"Total plantillas: {len(created_templates)}")
        return created_templates
