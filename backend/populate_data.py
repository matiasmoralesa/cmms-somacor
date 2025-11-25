#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo para el sistema CMMS
Incluye datos suficientes para entrenar modelos de ML de predicción de fallas
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random
from faker import Faker

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.inventory.models import SparePart, StockMovement
from apps.maintenance.models import MaintenancePlan
from apps.checklists.models import ChecklistTemplate, ChecklistResponse

User = get_user_model()
fake = Faker('es_ES')

def create_roles():
    """Crear roles del sistema"""
    print("Creando roles...")
    from apps.authentication.models import Role
    
    roles_data = [
        {'name': 'ADMIN', 'description': 'Administrador del sistema con acceso completo'},
        {'name': 'SUPERVISOR', 'description': 'Supervisor con permisos de gestión'},
        {'name': 'OPERADOR', 'description': 'Operador con permisos básicos'},
    ]
    
    created_roles = {}
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        created_roles[role_data['name']] = role
    
    print(f"Creados/verificados {len(created_roles)} roles")
    return created_roles

def create_users(roles):
    """Crear usuarios del sistema"""
    print("Creando usuarios...")
    
    users_data = [
        {'email': 'admin@cmms.com', 'first_name': 'Admin', 'last_name': 'Sistema', 'rut': '11111111-1', 'role': 'ADMIN', 'is_superuser': True},
        {'email': 'juan.perez@somacor.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'rut': '12345678-9', 'role': 'OPERADOR'},
        {'email': 'maria.gonzalez@somacor.com', 'first_name': 'María', 'last_name': 'González', 'rut': '23456789-0', 'role': 'OPERADOR'},
        {'email': 'carlos.rodriguez@somacor.com', 'first_name': 'Carlos', 'last_name': 'Rodríguez', 'rut': '34567890-1', 'role': 'SUPERVISOR'},
        {'email': 'ana.martinez@somacor.com', 'first_name': 'Ana', 'last_name': 'Martínez', 'rut': '45678901-2', 'role': 'OPERADOR'},
        {'email': 'luis.sanchez@somacor.com', 'first_name': 'Luis', 'last_name': 'Sánchez', 'rut': '56789012-3', 'role': 'ADMIN'},
        {'email': 'sofia.lopez@somacor.com', 'first_name': 'Sofía', 'last_name': 'López', 'rut': '67890123-4', 'role': 'OPERADOR'},
        {'email': 'diego.torres@somacor.com', 'first_name': 'Diego', 'last_name': 'Torres', 'rut': '78901234-5', 'role': 'OPERADOR'},
        {'email': 'elena.ruiz@somacor.com', 'first_name': 'Elena', 'last_name': 'Ruiz', 'rut': '89012345-6', 'role': 'SUPERVISOR'},
    ]
    
    created_users = []
    for user_data in users_data:
        role_obj = roles[user_data['role']]
        
        # Verificar si el usuario ya existe
        try:
            user = User.objects.get(email=user_data['email'])
            print(f"  Usuario {user_data['email']} ya existe, omitiendo...")
        except User.DoesNotExist:
            # Preparar datos del usuario
            user_kwargs = {
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'rut': user_data['rut'],
                'is_active': True,
                'role': role_obj,
                'employee_status': 'ACTIVE',
                'is_superuser': user_data.get('is_superuser', False),
                'is_staff': user_data.get('is_superuser', False)
            }
            
            # Si es operador, agregar datos de licencia
            if user_data['role'] == 'OPERADOR':
                user_kwargs.update({
                    'license_type': 'MUNICIPAL',
                    'license_expiration_date': (timezone.now() + timedelta(days=random.randint(180, 730))).date(),
                    'license_photo_url': f"https://example.com/licenses/{user_data['rut']}.jpg"
                })
            
            # Crear usuario usando el manager
            password = 'admin123' if user_data['email'] == 'admin@cmms.com' else 'password123'
            user = User.objects.create_user(
                password=password,
                **user_kwargs
            )
            print(f"  Creado usuario: {user.email}")
        
        created_users.append(user)
    
    print(f"Total usuarios: {len(created_users)}")
    return created_users

def create_spare_parts():
    """Crear repuestos y partes de inventario"""
    print("Creando repuestos...")
    
    spare_parts_data = [
        # Filtros
        {'part_number': 'FLT-001', 'name': 'Filtro de Aceite Motor', 'category': 'FILTERS', 'unit_cost': 25.50, 'current_stock': 50, 'minimum_stock': 10},
        {'part_number': 'FLT-002', 'name': 'Filtro de Aire Primario', 'category': 'FILTERS', 'unit_cost': 45.00, 'current_stock': 30, 'minimum_stock': 8},
        {'part_number': 'FLT-003', 'name': 'Filtro Hidráulico', 'category': 'FILTERS', 'unit_cost': 85.00, 'current_stock': 25, 'minimum_stock': 5},
        {'part_number': 'FLT-004', 'name': 'Filtro de Combustible', 'category': 'FILTERS', 'unit_cost': 35.00, 'current_stock': 40, 'minimum_stock': 12},
        # Aceites y lubricantes
        {'part_number': 'OIL-001', 'name': 'Aceite Motor 15W-40', 'category': 'OILS', 'unit_cost': 12.50, 'current_stock': 200, 'minimum_stock': 50, 'unit_of_measure': 'LITER'},
        {'part_number': 'OIL-002', 'name': 'Aceite Hidráulico ISO 46', 'category': 'OILS', 'unit_cost': 8.75, 'current_stock': 150, 'minimum_stock': 40, 'unit_of_measure': 'LITER'},
        {'part_number': 'OIL-003', 'name': 'Grasa Multiuso', 'category': 'OILS', 'unit_cost': 15.00, 'current_stock': 80, 'minimum_stock': 20, 'unit_of_measure': 'KILOGRAM'},
        # Componentes mecánicos
        {'part_number': 'BRG-001', 'name': 'Rodamiento 6205-2RS', 'category': 'BEARINGS', 'unit_cost': 18.50, 'current_stock': 35, 'minimum_stock': 10},
        {'part_number': 'BRG-002', 'name': 'Rodamiento 6308-2RS', 'category': 'BEARINGS', 'unit_cost': 32.00, 'current_stock': 20, 'minimum_stock': 8},
        {'part_number': 'SEAL-001', 'name': 'Sello Hidráulico 50x70x10', 'category': 'SEALS', 'unit_cost': 12.00, 'current_stock': 45, 'minimum_stock': 15},
        {'part_number': 'BELT-001', 'name': 'Correa Trapezoidal A-50', 'category': 'BELTS', 'unit_cost': 22.00, 'current_stock': 25, 'minimum_stock': 8},
        {'part_number': 'BELT-002', 'name': 'Correa Dentada HTD-1200', 'category': 'BELTS', 'unit_cost': 65.00, 'current_stock': 15, 'minimum_stock': 5},
        # Componentes eléctricos
        {'part_number': 'ELC-001', 'name': 'Alternador 24V 100A', 'category': 'ELECTRICAL', 'unit_cost': 450.00, 'current_stock': 8, 'minimum_stock': 2},
        {'part_number': 'ELC-002', 'name': 'Motor de Arranque 24V', 'category': 'ELECTRICAL', 'unit_cost': 380.00, 'current_stock': 6, 'minimum_stock': 2},
        {'part_number': 'ELC-003', 'name': 'Batería 12V 100Ah', 'category': 'ELECTRICAL', 'unit_cost': 120.00, 'current_stock': 12, 'minimum_stock': 4},
        {'part_number': 'ELC-004', 'name': 'Sensor de Temperatura', 'category': 'ELECTRICAL', 'unit_cost': 85.00, 'current_stock': 18, 'minimum_stock': 6},
        # Componentes hidráulicos
        {'part_number': 'HYD-001', 'name': 'Bomba Hidráulica Principal', 'category': 'HYDRAULIC', 'unit_cost': 2500.00, 'current_stock': 3, 'minimum_stock': 1, 'is_critical': True},
        {'part_number': 'HYD-002', 'name': 'Cilindro Hidráulico 100x50x500', 'category': 'HYDRAULIC', 'unit_cost': 850.00, 'current_stock': 5, 'minimum_stock': 2},
        {'part_number': 'HYD-003', 'name': 'Válvula de Alivio 250 bar', 'category': 'HYDRAULIC', 'unit_cost': 180.00, 'current_stock': 12, 'minimum_stock': 4},
        {'part_number': 'HYD-004', 'name': 'Manguera Hidráulica 1/2"', 'category': 'HYDRAULIC', 'unit_cost': 25.00, 'current_stock': 100, 'minimum_stock': 30, 'unit_of_measure': 'METER'},
        # Componentes de motor
        {'part_number': 'ENG-001', 'name': 'Pistón con Anillos', 'category': 'ENGINE', 'unit_cost': 320.00, 'current_stock': 12, 'minimum_stock': 4},
        {'part_number': 'ENG-002', 'name': 'Culata Completa', 'category': 'ENGINE', 'unit_cost': 1800.00, 'current_stock': 2, 'minimum_stock': 1, 'is_critical': True},
        {'part_number': 'ENG-003', 'name': 'Turbocompresor', 'category': 'ENGINE', 'unit_cost': 2200.00, 'current_stock': 3, 'minimum_stock': 1, 'is_critical': True},
        {'part_number': 'ENG-004', 'name': 'Radiador Principal', 'category': 'ENGINE', 'unit_cost': 650.00, 'current_stock': 4, 'minimum_stock': 2},
        # Herramientas y consumibles
        {'part_number': 'TOOL-001', 'name': 'Llave Torquímetro 1/2"', 'category': 'TOOLS', 'unit_cost': 180.00, 'current_stock': 8, 'minimum_stock': 3},
        {'part_number': 'CONS-001', 'name': 'Soldadura E6013 3.2mm', 'category': 'CONSUMABLES', 'unit_cost': 3.50, 'current_stock': 500, 'minimum_stock': 100, 'unit_of_measure': 'KILOGRAM'},
        {'part_number': 'CONS-002', 'name': 'Disco de Corte 9"', 'category': 'CONSUMABLES', 'unit_cost': 8.50, 'current_stock': 80, 'minimum_stock': 20},
    ]
    
    created_parts = []
    for part_data in spare_parts_data:
        part, created = SparePart.objects.get_or_create(
            part_number=part_data['part_number'],
            defaults={
                'name': part_data['name'],
                'description': f"Repuesto {part_data['name']} para mantenimiento",
                'category': part_data['category'],
                'unit_cost': Decimal(str(part_data['unit_cost'])),
                'quantity': part_data['current_stock'],
                'minimum_stock': part_data['minimum_stock'],
                'supplier': fake.company(),
                'location': random.choice(['Almacén A', 'Almacén B', 'Almacén C']),
            }
        )
        if created:
            print(f"  Creado repuesto: {part.part_number}")
        created_parts.append(part)
    
    print(f"Total repuestos: {len(created_parts)}")
    return created_parts

def create_locations():
    """Crear ubicaciones para los activos"""
    print("Creando ubicaciones...")
    from apps.assets.models import Location
    
    locations_data = [
        {'name': 'Obra Norte', 'address': 'Av. Norte 1234, Santiago'},
        {'name': 'Obra Sur', 'address': 'Av. Sur 5678, Santiago'},
        {'name': 'Obra Centro', 'address': 'Av. Centro 9012, Santiago'},
        {'name': 'Taller Principal', 'address': 'Calle Taller 3456, Santiago'},
        {'name': 'Patio de Equipos', 'address': 'Calle Patio 7890, Santiago'},
    ]
    
    created_locations = []
    for loc_data in locations_data:
        location, created = Location.objects.get_or_create(
            name=loc_data['name'],
            defaults={'address': loc_data['address']}
        )
        if created:
            print(f"  Creada ubicación: {location.name}")
        created_locations.append(location)
    
    print(f"Total ubicaciones: {len(created_locations)}")
    return created_locations

def create_assets(users, locations):
    """Crear activos/equipos"""
    print("Creando activos...")
    
    # Usar los 5 tipos de vehículos predefinidos
    assets_data = [
        # Camiones Supersucker
        {'name': 'Camión Supersucker 001', 'asset_code': 'CSS-001', 'vehicle_type': 'CAMION_SUPERSUCKER', 'manufacturer': 'Volvo', 'model': 'FMX 440', 'serial_number': 'CSS001', 'criticality': 'HIGH', 'license_plate': 'ABCD12'},
        {'name': 'Camión Supersucker 002', 'asset_code': 'CSS-002', 'vehicle_type': 'CAMION_SUPERSUCKER', 'manufacturer': 'Mercedes-Benz', 'model': 'Actros 2644', 'serial_number': 'CSS002', 'criticality': 'HIGH', 'license_plate': 'EFGH34'},
        {'name': 'Camión Supersucker 003', 'asset_code': 'CSS-003', 'vehicle_type': 'CAMION_SUPERSUCKER', 'manufacturer': 'Scania', 'model': 'R450', 'serial_number': 'CSS003', 'criticality': 'HIGH', 'license_plate': 'IJKL56'},
        # Camionetas MDO
        {'name': 'Camioneta MDO 001', 'asset_code': 'CMD-001', 'vehicle_type': 'CAMIONETA_MDO', 'manufacturer': 'Toyota', 'model': 'Hilux', 'serial_number': 'CMD001', 'criticality': 'MEDIUM', 'license_plate': 'MNOP78'},
        {'name': 'Camioneta MDO 002', 'asset_code': 'CMD-002', 'vehicle_type': 'CAMIONETA_MDO', 'manufacturer': 'Ford', 'model': 'Ranger', 'serial_number': 'CMD002', 'criticality': 'MEDIUM', 'license_plate': 'QRST90'},
        {'name': 'Camioneta MDO 003', 'asset_code': 'CMD-003', 'vehicle_type': 'CAMIONETA_MDO', 'manufacturer': 'Chevrolet', 'model': 'Colorado', 'serial_number': 'CMD003', 'criticality': 'MEDIUM', 'license_plate': 'UVWX12'},
        # Retroexcavadoras MDO
        {'name': 'Retroexcavadora MDO 001', 'asset_code': 'RMD-001', 'vehicle_type': 'RETROEXCAVADORA_MDO', 'manufacturer': 'Caterpillar', 'model': '420F', 'serial_number': 'RMD001', 'criticality': 'HIGH', 'license_plate': 'YZAB34'},
        {'name': 'Retroexcavadora MDO 002', 'asset_code': 'RMD-002', 'vehicle_type': 'RETROEXCAVADORA_MDO', 'manufacturer': 'JCB', 'model': '3CX', 'serial_number': 'RMD002', 'criticality': 'HIGH', 'license_plate': 'CDEF56'},
        {'name': 'Retroexcavadora MDO 003', 'asset_code': 'RMD-003', 'vehicle_type': 'RETROEXCAVADORA_MDO', 'manufacturer': 'Komatsu', 'model': 'WB97R', 'serial_number': 'RMD003', 'criticality': 'HIGH', 'license_plate': 'GHIJ78'},
        # Cargadores Frontales MDO
        {'name': 'Cargador Frontal MDO 001', 'asset_code': 'CFM-001', 'vehicle_type': 'CARGADOR_FRONTAL_MDO', 'manufacturer': 'Caterpillar', 'model': '950M', 'serial_number': 'CFM001', 'criticality': 'HIGH', 'license_plate': 'KLMN90'},
        {'name': 'Cargador Frontal MDO 002', 'asset_code': 'CFM-002', 'vehicle_type': 'CARGADOR_FRONTAL_MDO', 'manufacturer': 'Komatsu', 'model': 'WA380', 'serial_number': 'CFM002', 'criticality': 'HIGH', 'license_plate': 'OPQR12'},
        {'name': 'Cargador Frontal MDO 003', 'asset_code': 'CFM-003', 'vehicle_type': 'CARGADOR_FRONTAL_MDO', 'manufacturer': 'Volvo', 'model': 'L90H', 'serial_number': 'CFM003', 'criticality': 'MEDIUM', 'license_plate': 'STUV34'},
        # Minicargadores MDO
        {'name': 'Minicargador MDO 001', 'asset_code': 'MCM-001', 'vehicle_type': 'MINICARGADOR_MDO', 'manufacturer': 'Bobcat', 'model': 'S650', 'serial_number': 'MCM001', 'criticality': 'MEDIUM', 'license_plate': 'WXYZ56'},
        {'name': 'Minicargador MDO 002', 'asset_code': 'MCM-002', 'vehicle_type': 'MINICARGADOR_MDO', 'manufacturer': 'Caterpillar', 'model': '262D', 'serial_number': 'MCM002', 'criticality': 'MEDIUM', 'license_plate': 'ABCD78'},
        {'name': 'Minicargador MDO 003', 'asset_code': 'MCM-003', 'vehicle_type': 'MINICARGADOR_MDO', 'manufacturer': 'JCB', 'model': '190', 'serial_number': 'MCM003', 'criticality': 'LOW', 'license_plate': 'EFGH90'},
    ]
    
    created_assets = []
    for i, asset_data in enumerate(assets_data):
        # Calcular fechas realistas
        installation_date = fake.date_between(start_date='-5y', end_date='-1y')
        last_maintenance = fake.date_between(start_date=installation_date, end_date='today')
        
        # Determinar estado
        status = random.choices(
            ['OPERATIONAL', 'MAINTENANCE', 'DOWN'],
            weights=[75, 20, 5]
        )[0]
        
        # Seleccionar ubicación aleatoria
        location = random.choice(locations)
        
        # Seleccionar usuario creador
        created_by = random.choice(users)
        
        asset, created = Asset.objects.get_or_create(
            asset_code=asset_data['asset_code'],
            defaults={
                'name': asset_data['name'],
                'serial_number': asset_data['serial_number'],
                'model': asset_data['model'],
                'manufacturer': asset_data['manufacturer'],
                'vehicle_type': asset_data['vehicle_type'],
                'status': status,
                'criticality': asset_data['criticality'],
                'location': location,
                'installation_date': installation_date,
                'last_maintenance_date': last_maintenance,
                'license_plate': asset_data.get('license_plate'),
                'created_by': created_by,
                'is_active': True,
            }
        )
        if created:
            print(f"  Creado activo: {asset.asset_code}")
        created_assets.append(asset)
    
    print(f"Total activos: {len(created_assets)}")
    return created_assets

def create_maintenance_plans(assets, users):
    """Crear planes de mantenimiento preventivo"""
    print("Creando planes de mantenimiento...")
    
    maintenance_plans = []
    
    # Descripciones realistas por tipo de equipo
    plan_descriptions = {
        'EXCAVATOR': [
            'Cambio de aceite motor y filtros',
            'Revisión sistema hidráulico',
            'Mantenimiento de orugas',
            'Inspección general de seguridad'
        ],
        'LOADER': [
            'Cambio de aceite de transmisión',
            'Revisión de frenos',
            'Mantenimiento de sistema hidráulico',
            'Inspección de neumáticos'
        ],
        'TRUCK': [
            'Cambio de aceite motor',
            'Revisión de sistema de frenos',
            'Mantenimiento de suspensión',
            'Inspección general'
        ],
        'CRANE': [
            'Inspección de cables de acero',
            'Mantenimiento de sistema hidráulico',
            'Revisión de ganchos y poleas',
            'Calibración de limitadores de carga'
        ],
        'GENERATOR': [
            'Cambio de aceite y filtros',
            'Revisión de alternador',
            'Mantenimiento de motor diesel',
            'Prueba de carga'
        ],
        'COMPRESSOR': [
            'Cambio de aceite compresor',
            'Revisión de válvulas',
            'Mantenimiento de motor',
            'Cambio de filtros de aire'
        ],
        'PUMP': [
            'Cambio de sellos mecánicos',
            'Revisión de rodamientos',
            'Mantenimiento de motor eléctrico',
            'Calibración de presión'
        ]
    }
    
    for asset in assets:
        # Crear 2-4 planes de mantenimiento por activo
        num_plans = random.randint(2, 4)
        descriptions = plan_descriptions.get(asset.vehicle_type, ['Mantenimiento general'])
        
        for i in range(min(num_plans, len(descriptions))):
            description = descriptions[i]
            
            # Determinar tipo de plan
            plan_type = random.choices(
                ['PREVENTIVE', 'PREDICTIVE'],
                weights=[80, 20]
            )[0]
            
            # Determinar recurrencia
            recurrence_type = random.choice(['WEEKLY', 'MONTHLY'])
            if recurrence_type == 'WEEKLY':
                recurrence_interval = random.choice([1, 2, 4])  # Semanal, quincenal, mensual
                next_due_date = timezone.now().date() + timedelta(weeks=recurrence_interval)
            else:
                recurrence_interval = random.choice([1, 3, 6])  # Mensual, trimestral, semestral
                next_due_date = timezone.now().date() + timedelta(days=30 * recurrence_interval)
            
            # Duración estimada en minutos
            estimated_duration = random.randint(60, 480)  # 1-8 horas
            
            plan = MaintenancePlan.objects.create(
                name=f"{description} - {asset.name}",
                description=f"Plan de mantenimiento {plan_type.lower()} para {asset.name}",
                asset=asset,
                plan_type=plan_type,
                recurrence_type=recurrence_type,
                recurrence_interval=recurrence_interval,
                next_due_date=next_due_date,
                is_active=True,
                estimated_duration=estimated_duration,
                created_by=random.choice(users)
            )
            maintenance_plans.append(plan)
    
    print(f"Creados {len(maintenance_plans)} planes de mantenimiento")
    return maintenance_plans

def create_work_orders(assets, users, spare_parts):
    """Crear órdenes de trabajo"""
    print("Creando órdenes de trabajo...")
    
    work_orders = []
    wo_counter = 1
    
    for asset in assets:
        # Crear entre 5 y 15 órdenes de trabajo por activo
        num_orders = random.randint(5, 15)
        
        for i in range(num_orders):
            # Calcular fechas
            days_ago = random.randint(1, 730)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            # Determinar estado basado en antigüedad
            if days_ago > 30:
                status = random.choices(
                    ['COMPLETED', 'CANCELLED'],
                    weights=[85, 15]
                )[0]
            elif days_ago > 7:
                status = random.choices(
                    ['COMPLETED', 'IN_PROGRESS', 'CANCELLED'],
                    weights=[70, 25, 5]
                )[0]
            else:
                status = random.choices(
                    ['PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'],
                    weights=[30, 20, 30, 20]
                )[0]
            
            # Determinar prioridad y tipo
            priority = random.choices(
                ['LOW', 'MEDIUM', 'HIGH', 'URGENT'],
                weights=[20, 50, 25, 5]
            )[0]
            
            work_type = random.choices(
                ['PREVENTIVE', 'CORRECTIVE', 'PREDICTIVE', 'EMERGENCY', 'INSPECTION'],
                weights=[40, 30, 10, 5, 15]
            )[0]
            
            # Calcular fechas de inicio y finalización
            started_at = None
            completed_at = None
            due_date = created_date + timedelta(days=random.randint(1, 14))
            
            if status in ['IN_PROGRESS', 'COMPLETED', 'ASSIGNED']:
                started_at = created_date + timedelta(hours=random.randint(1, 48)) if status in ['IN_PROGRESS', 'COMPLETED'] else None
            
            if status == 'COMPLETED':
                completed_at = started_at + timedelta(hours=random.randint(2, 72))
            
            # Calcular horas y costos
            estimated_hours = Decimal(str(random.uniform(2, 16)))
            actual_hours = None
            estimated_cost = Decimal(str(random.uniform(300, 3000)))
            actual_cost = None
            
            if status == 'COMPLETED':
                actual_hours = estimated_hours * Decimal(str(random.uniform(0.8, 1.3)))
                actual_cost = estimated_cost * Decimal(str(random.uniform(0.85, 1.25)))
            
            # Crear orden de trabajo
            wo = WorkOrder.objects.create(
                title=f"Mantenimiento {work_type.lower()} - {asset.name}",
                description=f"Orden de trabajo para {asset.name}. {fake.sentence()}",
                asset=asset,
                assigned_to=random.choice(users),
                created_by=random.choice(users),
                status=status,
                priority=priority,
                work_order_type=work_type,
                scheduled_date=due_date,
                started_at=started_at,
                completed_at=completed_at,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                completion_notes=fake.sentence() if status == 'COMPLETED' else ''
            )
            wo.created_at = created_date
            wo.save()
            
            work_orders.append(wo)
            wo_counter += 1
    
    print(f"Creadas {len(work_orders)} órdenes de trabajo")
    return work_orders

def create_stock_movements(spare_parts, users, work_orders):
    """Crear movimientos de inventario"""
    print("Creando movimientos de inventario...")
    
    movements = []
    
    for part in spare_parts:
        try:
            # Crear movimientos de entrada (compras)
            num_purchases = random.randint(2, 4)
            for i in range(num_purchases):
                days_ago = random.randint(30, 730)
                quantity = random.randint(5, 15)
                
                movement = StockMovement.objects.create(
                    spare_part=part,
                    movement_type='IN',
                    quantity=quantity,
                    work_order=None,
                    performed_by=random.choice(users),
                    notes=f"Compra de {quantity} unidades"
                )
                movement.created_at = timezone.now() - timedelta(days=days_ago)
                movement.save()
                movements.append(movement)
                print(f"  Entrada: {part.part_number} +{quantity}")
            
            # Crear movimientos de salida (uso en órdenes de trabajo)
            num_usages = random.randint(1, 5)
            for i in range(num_usages):
                days_ago = random.randint(1, 700)
                
                # Recargar el repuesto para obtener la cantidad actual
                part.refresh_from_db()
                
                # Calcular cantidad segura (máximo 30% del stock actual)
                max_quantity = max(1, int(part.quantity * 0.3))
                quantity = random.randint(1, min(3, max_quantity))
                
                # Seleccionar una orden de trabajo aleatoria
                wo = random.choice(work_orders) if work_orders else None
                
                # Solo crear si hay stock suficiente
                if part.quantity >= quantity + 2:  # Dejar al menos 2 unidades
                    movement = StockMovement.objects.create(
                        spare_part=part,
                        movement_type='OUT',
                        quantity=quantity,
                        work_order=wo,
                        performed_by=random.choice(users),
                        notes=f"Uso en orden de trabajo {wo.work_order_number if wo else 'N/A'}"
                    )
                    movement.created_at = timezone.now() - timedelta(days=days_ago)
                    movement.save()
                    movements.append(movement)
                    print(f"  Salida: {part.part_number} -{quantity}")
        
        except Exception as e:
            print(f"  Error con {part.part_number}: {str(e)}")
            continue
    
    print(f"Total movimientos: {len(movements)}")
    return movements



def create_checklist_templates():
    """Crear plantillas de checklists para los 5 tipos de vehículos"""
    print("Creando plantillas de checklists...")
    
    templates_data = [
        {
            'code': 'CHK-CSS',
            'name': 'Checklist Camión Supersucker',
            'vehicle_type': 'CAMION_SUPERSUCKER',
            'items': [
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Motor', 'order': 2, 'question': 'Nivel de refrigerante', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Sistema Hidráulico', 'order': 3, 'question': 'Nivel de aceite hidráulico', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Sistema Hidráulico', 'order': 4, 'question': 'Fugas en mangueras', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Neumáticos', 'order': 5, 'question': 'Presión de neumáticos', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Seguridad', 'order': 6, 'question': 'Luces funcionando', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
            ]
        },
        {
            'code': 'CHK-CMD',
            'name': 'Checklist Camioneta MDO',
            'vehicle_type': 'CAMIONETA_MDO',
            'items': [
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Frenos', 'order': 2, 'question': 'Nivel de líquido de frenos', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Neumáticos', 'order': 3, 'question': 'Estado de neumáticos', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Seguridad', 'order': 4, 'question': 'Cinturones de seguridad', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
            ]
        },
        {
            'code': 'CHK-RMD',
            'name': 'Checklist Retroexcavadora MDO',
            'vehicle_type': 'RETROEXCAVADORA_MDO',
            'items': [
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Hidráulico', 'order': 2, 'question': 'Nivel de aceite hidráulico', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Hidráulico', 'order': 3, 'question': 'Estado de cilindros', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Estructura', 'order': 4, 'question': 'Estado de brazos y cucharón', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
            ]
        },
        {
            'code': 'CHK-CFM',
            'name': 'Checklist Cargador Frontal MDO',
            'vehicle_type': 'CARGADOR_FRONTAL_MDO',
            'items': [
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Transmisión', 'order': 2, 'question': 'Nivel de aceite transmisión', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Hidráulico', 'order': 3, 'question': 'Sistema hidráulico', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Neumáticos', 'order': 4, 'question': 'Estado de neumáticos', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
            ]
        },
        {
            'code': 'CHK-MCM',
            'name': 'Checklist Minicargador MDO',
            'vehicle_type': 'MINICARGADOR_MDO',
            'items': [
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Hidráulico', 'order': 2, 'question': 'Sistema hidráulico', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
                {'section': 'Orugas/Neumáticos', 'order': 3, 'question': 'Estado de orugas/neumáticos', 'response_type': 'yes_no_na', 'required': True, 'observations_allowed': True},
            ]
        },
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
            print(f"  Creada plantilla: {template.code}")
        created_templates.append(template)
    
    print(f"Total plantillas: {len(created_templates)}")
    return created_templates

def main():
    """Función principal para ejecutar el script"""
    print("=" * 60)
    print("INICIANDO POBLACIÓN DE BASE DE DATOS CMMS")
    print("=" * 60)
    
    try:
        # Crear datos en orden
        roles = create_roles()
        users = create_users(roles)
        spare_parts = create_spare_parts()
        locations = create_locations()
        assets = create_assets(users, locations)
        checklist_templates = create_checklist_templates()
        maintenance_plans = create_maintenance_plans(assets, users)
        work_orders = create_work_orders(assets, users, spare_parts)
        stock_movements = create_stock_movements(spare_parts, users, work_orders)
        
        print("\n" + "=" * 60)
        print("RESUMEN DE DATOS CREADOS")
        print("=" * 60)
        print(f"Roles: {len(roles)}")
        print(f"Usuarios: {len(users)}")
        print(f"Repuestos: {len(spare_parts)}")
        print(f"Ubicaciones: {len(locations)}")
        print(f"Activos: {len(assets)}")
        print(f"Planes de Mantenimiento: {len(maintenance_plans)}")
        print(f"Órdenes de Trabajo: {len(work_orders)}")
        print(f"Movimientos de Inventario: {len(stock_movements)}")
        print("=" * 60)
        print("✓ Base de datos poblada exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error al poblar la base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
