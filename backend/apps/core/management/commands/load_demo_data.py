"""
Management command to load comprehensive demo data for the CMMS system
Includes data for ML model training
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from apps.assets.models import Asset, Location
from apps.authentication.models import User, Role
from apps.work_orders.models import WorkOrder
from apps.maintenance.models import MaintenancePlan
from apps.inventory.models import SparePart, StockMovement
from apps.checklists.models import ChecklistTemplate, ChecklistItem, Checklist, ChecklistItemResponse


class Command(BaseCommand):
    help = 'Load comprehensive demo data including historical data for ML training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--historical-months',
            type=int,
            default=12,
            help='Number of months of historical data to generate (default: 12)'
        )

    def handle(self, *args, **options):
        historical_months = options['historical_months']
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('  Loading Demo Data for CMMS System'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 1. Create Roles
        self.stdout.write('\n📋 Step 1: Creating Roles...')
        self.create_roles()
        
        # 2. Create Users
        self.stdout.write('\n👥 Step 2: Creating Users...')
        self.create_users()
        
        # 3. Create Locations
        self.stdout.write('\n📍 Step 3: Creating Locations...')
        self.create_locations()
        
        # 4. Create Assets
        self.stdout.write('\n🚛 Step 4: Creating Assets...')
        self.create_assets()
        
        # 5. Create Spare Parts
        self.stdout.write('\n🔧 Step 5: Creating Spare Parts...')
        self.create_spare_parts()
        
        # 6. Create Maintenance Plans
        self.stdout.write('\n📅 Step 6: Creating Maintenance Plans...')
        self.create_maintenance_plans()
        
        # 7. Create Checklist Templates
        self.stdout.write('\n✅ Step 7: Creating Checklist Templates...')
        self.create_checklist_templates()
        
        # 8. Create Historical Work Orders (for ML training)
        self.stdout.write(f'\n📊 Step 8: Creating Historical Work Orders ({historical_months} months)...')
        self.create_historical_work_orders(historical_months)
        
        # 9. Create Historical Checklists
        self.stdout.write(f'\n📝 Step 9: Creating Historical Checklists...')
        self.create_historical_checklists()
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('  ✓ Demo Data Loaded Successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('\n📈 System is now ready for ML model training!')
        self.stdout.write('🎯 You can now use the prediction endpoints to train and test the model.\n')

    def create_roles(self):
        roles_data = [
            {'name': 'ADMIN', 'description': 'Administrator with full access'},
            {'name': 'SUPERVISOR', 'description': 'Supervisor with management access'},
            {'name': 'OPERADOR', 'description': 'Operator with limited access'},
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created role: {role.name}'))
            else:
                self.stdout.write(f'    Role already exists: {role.name}')

    def create_users(self):
        admin_role = Role.objects.get(name='ADMIN')
        supervisor_role = Role.objects.get(name='SUPERVISOR')
        operator_role = Role.objects.get(name='OPERADOR')
        
        users_data = [
            {
                'email': 'supervisor@example.com',
                'username': 'supervisor',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': supervisor_role,
                'rut': '12345678-9',
                'employee_status': 'ACTIVE',
            },
            {
                'email': 'operator1@example.com',
                'username': 'operator1',
                'first_name': 'María',
                'last_name': 'González',
                'role': operator_role,
                'rut': '23456789-0',
                'employee_status': 'ACTIVE',
            },
            {
                'email': 'operator2@example.com',
                'username': 'operator2',
                'first_name': 'Pedro',
                'last_name': 'Rodríguez',
                'role': operator_role,
                'rut': '34567890-1',
                'employee_status': 'ACTIVE',
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    **user_data,
                    'password': 'pbkdf2_sha256$600000$dummy$dummy',  # Will be set properly
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created user: {user.email}'))
            else:
                self.stdout.write(f'    User already exists: {user.email}')

    def create_locations(self):
        locations_data = [
            {
                'name': 'Base Principal',
                'address': 'Av. Principal 123, Santiago',
                'description': 'Ubicación principal de la flota',
            },
            {
                'name': 'Base Norte',
                'address': 'Calle Norte 456, Antofagasta',
                'description': 'Base de operaciones zona norte',
            },
            {
                'name': 'Base Sur',
                'address': 'Av. Sur 789, Puerto Montt',
                'description': 'Base de operaciones zona sur',
            },
        ]
        
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={**loc_data, 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created location: {location.name}'))
            else:
                self.stdout.write(f'    Location already exists: {location.name}')

    def create_assets(self):
        location = Location.objects.first()
        admin_user = User.objects.filter(role__name='ADMIN').first()
        
        assets_data = [
            # Camiones Supersucker
            {
                'name': 'Camión Supersucker 001',
                'asset_code': 'CS-001',
                'vehicle_type': 'CAMION_SUPERSUCKER',
                'serial_number': 'SS2024001',
                'license_plate': 'ABCD-12',
                'manufacturer': 'Volvo',
                'model': 'FM 440',
                'year': 2022,
                'status': 'OPERATIONAL',
            },
            {
                'name': 'Camión Supersucker 002',
                'asset_code': 'CS-002',
                'vehicle_type': 'CAMION_SUPERSUCKER',
                'serial_number': 'SS2024002',
                'license_plate': 'ABCD-13',
                'manufacturer': 'Volvo',
                'model': 'FM 440',
                'year': 2021,
                'status': 'OPERATIONAL',
            },
            # Camionetas MDO
            {
                'name': 'Camioneta MDO 001',
                'asset_code': 'CM-001',
                'vehicle_type': 'CAMIONETA_MDO',
                'serial_number': 'CM2024001',
                'license_plate': 'EFGH-34',
                'manufacturer': 'Toyota',
                'model': 'Hilux',
                'year': 2023,
                'status': 'OPERATIONAL',
            },
            {
                'name': 'Camioneta MDO 002',
                'asset_code': 'CM-002',
                'vehicle_type': 'CAMIONETA_MDO',
                'serial_number': 'CM2024002',
                'license_plate': 'EFGH-35',
                'manufacturer': 'Ford',
                'model': 'Ranger',
                'year': 2022,
                'status': 'OPERATIONAL',
            },
            # Retroexcavadoras
            {
                'name': 'Retroexcavadora MDO 001',
                'asset_code': 'RE-001',
                'vehicle_type': 'RETROEXCAVADORA_MDO',
                'serial_number': 'RE2024001',
                'manufacturer': 'Caterpillar',
                'model': '420F',
                'year': 2021,
                'status': 'OPERATIONAL',
            },
            {
                'name': 'Retroexcavadora MDO 002',
                'asset_code': 'RE-002',
                'vehicle_type': 'RETROEXCAVADORA_MDO',
                'serial_number': 'RE2024002',
                'manufacturer': 'JCB',
                'model': '3CX',
                'year': 2020,
                'status': 'OPERATIONAL',
            },
            # Cargadores Frontales
            {
                'name': 'Cargador Frontal MDO 001',
                'asset_code': 'CF-001',
                'vehicle_type': 'CARGADOR_FRONTAL_MDO',
                'serial_number': 'CF2024001',
                'manufacturer': 'Caterpillar',
                'model': '950M',
                'year': 2022,
                'status': 'OPERATIONAL',
            },
            # Minicargadores
            {
                'name': 'Minicargador MDO 001',
                'asset_code': 'MC-001',
                'vehicle_type': 'MINICARGADOR_MDO',
                'serial_number': 'MC2024001',
                'manufacturer': 'Bobcat',
                'model': 'S650',
                'year': 2023,
                'status': 'OPERATIONAL',
            },
        ]
        
        for asset_data in assets_data:
            asset, created = Asset.objects.get_or_create(
                asset_code=asset_data['asset_code'],
                defaults={
                    **asset_data,
                    'location': location,
                    'created_by': admin_user,
                    'specifications': {'year': asset_data.pop('year', 2022)},
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created asset: {asset.asset_code} - {asset.name}'))
            else:
                self.stdout.write(f'    Asset already exists: {asset.asset_code}')

    def create_spare_parts(self):
        spare_parts_data = [
            {
                'part_number': 'FLT-001',
                'name': 'Filtro de Aceite',
                'description': 'Filtro de aceite para motores diesel',
                'category': 'FILTERS',
                'unit_price': Decimal('25.50'),
                'current_stock': 50,
                'minimum_stock': 10,
                'maximum_stock': 100,
            },
            {
                'part_number': 'FLT-002',
                'name': 'Filtro de Aire',
                'description': 'Filtro de aire para motores',
                'category': 'FILTERS',
                'unit_price': Decimal('35.00'),
                'current_stock': 40,
                'minimum_stock': 10,
                'maximum_stock': 80,
            },
            {
                'part_number': 'FLT-003',
                'name': 'Filtro de Combustible',
                'description': 'Filtro de combustible diesel',
                'category': 'FILTERS',
                'unit_price': Decimal('28.75'),
                'current_stock': 35,
                'minimum_stock': 10,
                'maximum_stock': 70,
            },
            {
                'part_number': 'BRK-001',
                'name': 'Pastillas de Freno',
                'description': 'Juego de pastillas de freno delanteras',
                'category': 'BRAKES',
                'unit_price': Decimal('85.00'),
                'current_stock': 20,
                'minimum_stock': 5,
                'maximum_stock': 40,
            },
            {
                'part_number': 'BRK-002',
                'name': 'Discos de Freno',
                'description': 'Par de discos de freno delanteros',
                'category': 'BRAKES',
                'unit_price': Decimal('150.00'),
                'current_stock': 15,
                'minimum_stock': 5,
                'maximum_stock': 30,
            },
            {
                'part_number': 'ENG-001',
                'name': 'Aceite de Motor 15W-40',
                'description': 'Aceite mineral para motores diesel',
                'category': 'LUBRICANTS',
                'unit_price': Decimal('45.00'),
                'current_stock': 100,
                'minimum_stock': 20,
                'maximum_stock': 200,
            },
            {
                'part_number': 'ENG-002',
                'name': 'Refrigerante',
                'description': 'Refrigerante para sistema de enfriamiento',
                'category': 'LUBRICANTS',
                'unit_price': Decimal('18.50'),
                'current_stock': 60,
                'minimum_stock': 15,
                'maximum_stock': 120,
            },
            {
                'part_number': 'TIR-001',
                'name': 'Neumático 295/80R22.5',
                'description': 'Neumático para camiones',
                'category': 'TIRES',
                'unit_price': Decimal('450.00'),
                'current_stock': 12,
                'minimum_stock': 4,
                'maximum_stock': 24,
            },
            {
                'part_number': 'BAT-001',
                'name': 'Batería 12V 180Ah',
                'description': 'Batería para arranque de motor',
                'category': 'ELECTRICAL',
                'unit_price': Decimal('180.00'),
                'current_stock': 8,
                'minimum_stock': 3,
                'maximum_stock': 15,
            },
            {
                'part_number': 'BLT-001',
                'name': 'Correa de Distribución',
                'description': 'Correa de distribución para motor',
                'category': 'ENGINE',
                'unit_price': Decimal('95.00'),
                'current_stock': 10,
                'minimum_stock': 3,
                'maximum_stock': 20,
            },
        ]
        
        for part_data in spare_parts_data:
            part, created = SparePart.objects.get_or_create(
                part_number=part_data['part_number'],
                defaults=part_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created spare part: {part.part_number} - {part.name}'))
            else:
                self.stdout.write(f'    Spare part already exists: {part.part_number}')

    def create_maintenance_plans(self):
        assets = Asset.objects.all()
        
        for asset in assets:
            # Create preventive maintenance plan
            plan, created = MaintenancePlan.objects.get_or_create(
                asset=asset,
                name=f'Mantenimiento Preventivo - {asset.name}',
                defaults={
                    'description': f'Plan de mantenimiento preventivo para {asset.name}',
                    'frequency_type': 'MONTHLY',
                    'frequency_value': 1,
                    'estimated_duration_hours': 4,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created maintenance plan for: {asset.name}'))

    def create_checklist_templates(self):
        templates_data = [
            {
                'name': 'Inspección Diaria Camión Supersucker',
                'vehicle_type': 'CAMION_SUPERSUCKER',
                'description': 'Checklist de inspección diaria para camiones supersucker',
                'items': [
                    {'order': 1, 'description': 'Verificar nivel de aceite del motor', 'item_type': 'CHECK'},
                    {'order': 2, 'description': 'Verificar nivel de refrigerante', 'item_type': 'CHECK'},
                    {'order': 3, 'description': 'Inspeccionar neumáticos y presión', 'item_type': 'CHECK'},
                    {'order': 4, 'description': 'Verificar luces y señalización', 'item_type': 'CHECK'},
                    {'order': 5, 'description': 'Inspeccionar sistema de frenos', 'item_type': 'CHECK'},
                    {'order': 6, 'description': 'Registrar kilometraje', 'item_type': 'NUMBER'},
                    {'order': 7, 'description': 'Observaciones generales', 'item_type': 'TEXT'},
                ]
            },
            {
                'name': 'Inspección Diaria Camioneta MDO',
                'vehicle_type': 'CAMIONETA_MDO',
                'description': 'Checklist de inspección diaria para camionetas',
                'items': [
                    {'order': 1, 'description': 'Verificar nivel de aceite', 'item_type': 'CHECK'},
                    {'order': 2, 'description': 'Verificar nivel de combustible', 'item_type': 'CHECK'},
                    {'order': 3, 'description': 'Inspeccionar neumáticos', 'item_type': 'CHECK'},
                    {'order': 4, 'description': 'Verificar luces', 'item_type': 'CHECK'},
                    {'order': 5, 'description': 'Registrar kilometraje', 'item_type': 'NUMBER'},
                    {'order': 6, 'description': 'Observaciones', 'item_type': 'TEXT'},
                ]
            },
            {
                'name': 'Inspección Diaria Retroexcavadora',
                'vehicle_type': 'RETROEXCAVADORA_MDO',
                'description': 'Checklist de inspección diaria para retroexcavadoras',
                'items': [
                    {'order': 1, 'description': 'Verificar nivel de aceite hidráulico', 'item_type': 'CHECK'},
                    {'order': 2, 'description': 'Inspeccionar mangueras hidráulicas', 'item_type': 'CHECK'},
                    {'order': 3, 'description': 'Verificar nivel de aceite del motor', 'item_type': 'CHECK'},
                    {'order': 4, 'description': 'Inspeccionar brazos y cucharón', 'item_type': 'CHECK'},
                    {'order': 5, 'description': 'Verificar sistema de frenos', 'item_type': 'CHECK'},
                    {'order': 6, 'description': 'Registrar horómetro', 'item_type': 'NUMBER'},
                    {'order': 7, 'description': 'Observaciones', 'item_type': 'TEXT'},
                ]
            },
        ]
        
        for template_data in templates_data:
            items_data = template_data.pop('items')
            template, created = ChecklistTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                # Create items
                for item_data in items_data:
                    ChecklistItem.objects.create(
                        template=template,
                        **item_data
                    )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created checklist template: {template.name}'))
            else:
                self.stdout.write(f'    Checklist template already exists: {template.name}')

    def create_historical_work_orders(self, months):
        assets = list(Asset.objects.all())
        users = list(User.objects.all())
        spare_parts = list(SparePart.objects.all())
        
        # Failure types and their probabilities
        failure_types = [
            ('PREVENTIVE', 0.40),  # 40% preventive
            ('CORRECTIVE', 0.35),  # 35% corrective
            ('PREDICTIVE', 0.15),  # 15% predictive
            ('EMERGENCY', 0.10),   # 10% emergency
        ]
        
        priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        work_orders_created = 0
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        # Generate work orders
        for asset in assets:
            # Each asset gets 2-4 work orders per month
            num_orders = random.randint(2 * months, 4 * months)
            
            for _ in range(num_orders):
                # Random date within the period
                days_offset = random.randint(0, 30 * months)
                created_date = start_date + timedelta(days=days_offset)
                
                # Select work order type based on probabilities
                wo_type = random.choices(
                    [t[0] for t in failure_types],
                    weights=[t[1] for t in failure_types]
                )[0]
                
                # Priority based on type
                if wo_type == 'EMERGENCY':
                    priority = 'CRITICAL'
                elif wo_type == 'CORRECTIVE':
                    priority = random.choice(['MEDIUM', 'HIGH', 'CRITICAL'])
                elif wo_type == 'PREVENTIVE':
                    priority = random.choice(['LOW', 'MEDIUM'])
                else:
                    priority = random.choice(priorities)
                
                # Generate realistic descriptions
                descriptions = {
                    'PREVENTIVE': [
                        'Mantenimiento preventivo programado',
                        'Cambio de aceite y filtros',
                        'Inspección general de rutina',
                        'Revisión de sistema hidráulico',
                    ],
                    'CORRECTIVE': [
                        'Reparación de fuga de aceite',
                        'Cambio de pastillas de freno',
                        'Reparación de sistema eléctrico',
                        'Ajuste de sistema de dirección',
                    ],
                    'PREDICTIVE': [
                        'Reemplazo preventivo de componente',
                        'Mantenimiento basado en condición',
                        'Actualización de sistema',
                    ],
                    'EMERGENCY': [
                        'Falla crítica de motor',
                        'Avería en sistema hidráulico',
                        'Falla de frenos',
                        'Problema eléctrico grave',
                    ],
                }
                
                title = random.choice(descriptions[wo_type])
                
                # Estimated hours based on type
                if wo_type == 'EMERGENCY':
                    estimated_hours = random.randint(6, 16)
                elif wo_type == 'CORRECTIVE':
                    estimated_hours = random.randint(3, 8)
                else:
                    estimated_hours = random.randint(2, 6)
                
                # Create work order
                wo = WorkOrder.objects.create(
                    asset=asset,
                    title=title,
                    description=f'{title} para {asset.name}',
                    work_order_type=wo_type,
                    priority=priority,
                    status='COMPLETED',  # Historical orders are completed
                    assigned_to=random.choice(users),
                    created_by=random.choice(users),
                    estimated_hours=estimated_hours,
                    actual_hours=estimated_hours + random.uniform(-1, 2),
                    created_at=created_date,
                    updated_at=created_date + timedelta(hours=estimated_hours),
                )
                
                # Add some spare parts used (30% of work orders)
                if random.random() < 0.3 and spare_parts:
                    num_parts = random.randint(1, 3)
                    for _ in range(num_parts):
                        part = random.choice(spare_parts)
                        wo.spare_parts_used.add(part)
                
                work_orders_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {work_orders_created} historical work orders'))

    def create_historical_checklists(self):
        templates = ChecklistTemplate.objects.all()
        assets = Asset.objects.all()
        users = list(User.objects.all())
        
        checklists_created = 0
        
        for asset in assets:
            # Find matching template
            template = templates.filter(vehicle_type=asset.vehicle_type).first()
            if not template:
                continue
            
            # Create 20-30 historical checklists per asset
            num_checklists = random.randint(20, 30)
            
            for i in range(num_checklists):
                days_ago = random.randint(1, 365)
                completed_date = timezone.now() - timedelta(days=days_ago)
                
                checklist = Checklist.objects.create(
                    template=template,
                    asset=asset,
                    completed_by=random.choice(users),
                    status='COMPLETED',
                    completed_at=completed_date,
                    created_at=completed_date - timedelta(hours=1),
                )
                
                # Fill in responses
                for item in template.items.all():
                    if item.item_type == 'CHECK':
                        # 90% pass rate
                        value = 'true' if random.random() < 0.9 else 'false'
                    elif item.item_type == 'NUMBER':
                        # Random number (e.g., kilometraje)
                        value = str(random.randint(10000, 50000))
                    else:  # TEXT
                        value = 'Sin observaciones' if random.random() < 0.8 else 'Requiere atención'
                    
                    ChecklistItemResponse.objects.create(
                        checklist=checklist,
                        item=item,
                        value=value
                    )
                
                checklists_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {checklists_created} historical checklists'))
