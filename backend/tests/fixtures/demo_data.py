"""
Demo data generator for user acceptance testing
Creates realistic test data for all user roles and scenarios
"""
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.authentication.models import User, Role
from apps.assets.models import Asset, Location, AssetCategory
from apps.work_orders.models import WorkOrder
from apps.maintenance.models import MaintenancePlan
from apps.inventory.models import SparePart, StockMovement
from apps.checklists.models import ChecklistTemplate, ChecklistResponse
from apps.predictions.models import FailurePrediction, Alert
from apps.notifications.models import Notification


class DemoDataGenerator:
    """Generate comprehensive demo data for UAT"""
    
    def __init__(self):
        self.users = {}
        self.assets = {}
        self.templates = {}
    
    def generate_all(self):
        """Generate all demo data"""
        print("Generating demo data for User Acceptance Testing...")
        
        self.create_roles()
        self.create_users()
        self.create_locations_and_categories()
        self.create_assets()
        self.create_checklist_templates()
        self.create_spare_parts()
        self.create_maintenance_plans()
        self.create_work_orders()
        self.create_predictions_and_alerts()
        self.create_notifications()
        
        print("Demo data generation complete!")
        self.print_summary()
    
    def create_roles(self):
        """Create the three system roles"""
        print("Creating roles...")
        
        Role.objects.get_or_create(
            name='ADMIN',
            defaults={'description': 'System Administrator'}
        )
        Role.objects.get_or_create(
            name='SUPERVISOR',
            defaults={'description': 'Maintenance Supervisor'}
        )
        Role.objects.get_or_create(
            name='OPERADOR',
            defaults={'description': 'Equipment Operator'}
        )
    
    def create_users(self):
        """Create demo users for each role"""
        print("Creating users...")
        
        admin_role = Role.objects.get(name='ADMIN')
        supervisor_role = Role.objects.get(name='SUPERVISOR')
        operator_role = Role.objects.get(name='OPERADOR')
        
        # Admin user
        self.users['admin'] = User.objects.create_user(
            email='admin@somacor.com',
            password='Demo2024!',
            first_name='Carlos',
            last_name='Administrador',
            role=admin_role,
            rut='12345678-9',
            telegram_id='111111111',
            phone='+56912345678'
        )
        
        # Supervisor users
        self.users['supervisor1'] = User.objects.create_user(
            email='supervisor1@somacor.com',
            password='Demo2024!',
            first_name='María',
            last_name='Supervisor',
            role=supervisor_role,
            rut='23456789-0',
            telegram_id='222222222',
            phone='+56923456789'
        )
        
        self.users['supervisor2'] = User.objects.create_user(
            email='supervisor2@somacor.com',
            password='Demo2024!',
            first_name='Juan',
            last_name='Jefe',
            role=supervisor_role,
            rut='34567890-1',
            telegram_id='333333333',
            phone='+56934567890'
        )
        
        # Operator users
        self.users['operator1'] = User.objects.create_user(
            email='operator1@somacor.com',
            password='Demo2024!',
            first_name='Pedro',
            last_name='Operador',
            role=operator_role,
            rut='45678901-2',
            telegram_id='444444444',
            phone='+56945678901',
            license_type='MUNICIPAL',
            license_expiration_date=date.today() + timedelta(days=365)
        )
        
        self.users['operator2'] = User.objects.create_user(
            email='operator2@somacor.com',
            password='Demo2024!',
            first_name='Ana',
            last_name='Técnico',
            role=operator_role,
            rut='56789012-3',
            telegram_id='555555555',
            phone='+56956789012',
            license_type='INTERNAL',
            license_expiration_date=date.today() + timedelta(days=180)
        )
        
        self.users['operator3'] = User.objects.create_user(
            email='operator3@somacor.com',
            password='Demo2024!',
            first_name='Luis',
            last_name='Mecánico',
            role=operator_role,
            rut='67890123-4',
            telegram_id='666666666',
            phone='+56967890123',
            license_type='MUNICIPAL',
            license_expiration_date=date.today() + timedelta(days=90)
        )
    
    def create_locations_and_categories(self):
        """Create locations and asset categories"""
        print("Creating locations and categories...")
        
        Location.objects.get_or_create(
            name='Planta Principal',
            defaults={'address': 'Av. Industrial 1234, Santiago'}
        )
        Location.objects.get_or_create(
            name='Bodega Norte',
            defaults={'address': 'Calle Norte 567, Santiago'}
        )
        Location.objects.get_or_create(
            name='Taller Mantenimiento',
            defaults={'address': 'Av. Taller 890, Santiago'}
        )
        
        AssetCategory.objects.get_or_create(
            name='Vehículos Pesados',
            defaults={'description': 'Camiones y equipos pesados'}
        )
        AssetCategory.objects.get_or_create(
            name='Vehículos Livianos',
            defaults={'description': 'Camionetas y vehículos livianos'}
        )
        AssetCategory.objects.get_or_create(
            name='Maquinaria',
            defaults={'description': 'Equipos de construcción y maquinaria'}
        )
    
    def create_assets(self):
        """Create demo assets for all vehicle types"""
        print("Creating assets...")
        
        location = Location.objects.first()
        
        # Camión Supersucker
        self.assets['supersucker1'] = Asset.objects.create(
            name='Camión Supersucker 001',
            asset_code='CS-001',
            vehicle_type='CAMION_SUPERSUCKER',
            location=location,
            manufacturer='Vacall',
            model='AllJetVac',
            serial_number='VCS2023001',
            license_plate='ABCD-12',
            installation_date=date(2023, 1, 15),
            status='OPERATIONAL',
            criticality='CRITICAL'
        )
        
        # Camionetas MDO
        self.assets['camioneta1'] = Asset.objects.create(
            name='Camioneta MDO 001',
            asset_code='CM-001',
            vehicle_type='CAMIONETA_MDO',
            location=location,
            manufacturer='Toyota',
            model='Hilux 4x4',
            serial_number='THX2023001',
            license_plate='EFGH-34',
            installation_date=date(2023, 3, 10),
            status='OPERATIONAL',
            criticality='MEDIUM'
        )
        
        self.assets['camioneta2'] = Asset.objects.create(
            name='Camioneta MDO 002',
            asset_code='CM-002',
            vehicle_type='CAMIONETA_MDO',
            location=location,
            manufacturer='Ford',
            model='Ranger XLT',
            serial_number='FRG2023002',
            license_plate='IJKL-56',
            installation_date=date(2023, 4, 20),
            status='MAINTENANCE',
            criticality='MEDIUM'
        )
        
        # Retroexcavadora MDO
        self.assets['retro1'] = Asset.objects.create(
            name='Retroexcavadora MDO 001',
            asset_code='RE-001',
            vehicle_type='RETROEXCAVADORA_MDO',
            location=location,
            manufacturer='Caterpillar',
            model='420F2',
            serial_number='CAT2023001',
            license_plate='MNOP-78',
            installation_date=date(2022, 11, 5),
            status='OPERATIONAL',
            criticality='HIGH'
        )
        
        # Cargador Frontal MDO
        self.assets['cargador1'] = Asset.objects.create(
            name='Cargador Frontal MDO 001',
            asset_code='CF-001',
            vehicle_type='CARGADOR_FRONTAL_MDO',
            location=location,
            manufacturer='John Deere',
            model='624K',
            serial_number='JD2023001',
            license_plate='QRST-90',
            installation_date=date(2023, 2, 28),
            status='OPERATIONAL',
            criticality='HIGH'
        )
        
        # Minicargador MDO
        self.assets['mini1'] = Asset.objects.create(
            name='Minicargador MDO 001',
            asset_code='MC-001',
            vehicle_type='MINICARGADOR_MDO',
            location=location,
            manufacturer='Bobcat',
            model='S650',
            serial_number='BOB2023001',
            license_plate='UVWX-12',
            installation_date=date(2023, 5, 15),
            status='OPERATIONAL',
            criticality='MEDIUM'
        )
    
    def create_checklist_templates(self):
        """Create the 5 predefined checklist templates"""
        print("Creating checklist templates...")
        
        # Template for Camioneta MDO
        self.templates['camioneta'] = ChecklistTemplate.objects.create(
            code='F-PR-020-CH01',
            name='Check List Camionetas MDO',
            vehicle_type='CAMIONETA_MDO',
            description='Checklist de inspección para camionetas MDO',
            items=[
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Motor', 'order': 2, 'question': 'Nivel de refrigerante', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Frenos', 'order': 3, 'question': 'Estado de pastillas de freno', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Neumáticos', 'order': 4, 'question': 'Presión de neumáticos', 'response_type': 'numeric', 'required': True},
                {'section': 'Luces', 'order': 5, 'question': 'Funcionamiento de luces', 'response_type': 'yes_no_na', 'required': True},
            ],
            is_system_template=True,
            passing_score=80
        )
        
        # Template for Retroexcavadora MDO
        self.templates['retro'] = ChecklistTemplate.objects.create(
            code='F-PR-034-CH01',
            name='Check Retroexcavadora MDO',
            vehicle_type='RETROEXCAVADORA_MDO',
            description='Checklist de inspección para retroexcavadora MDO',
            items=[
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Hidráulico', 'order': 2, 'question': 'Nivel de aceite hidráulico', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Hidráulico', 'order': 3, 'question': 'Fugas en sistema hidráulico', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Estructura', 'order': 4, 'question': 'Estado de brazo excavador', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Seguridad', 'order': 5, 'question': 'Funcionamiento de alarma de retroceso', 'response_type': 'yes_no_na', 'required': True},
            ],
            is_system_template=True,
            passing_score=80
        )
        
        # Template for Cargador Frontal MDO
        self.templates['cargador'] = ChecklistTemplate.objects.create(
            code='F-PR-037-CH01',
            name='Check List Cargador Frontal MDO',
            vehicle_type='CARGADOR_FRONTAL_MDO',
            description='Checklist de inspección para cargador frontal MDO',
            items=[
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Hidráulico', 'order': 2, 'question': 'Presión sistema hidráulico', 'response_type': 'numeric', 'required': True},
                {'section': 'Balde', 'order': 3, 'question': 'Estado de balde cargador', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Transmisión', 'order': 4, 'question': 'Nivel de aceite transmisión', 'response_type': 'yes_no_na', 'required': True},
            ],
            is_system_template=True,
            passing_score=80
        )
        
        # Template for Minicargador MDO
        self.templates['mini'] = ChecklistTemplate.objects.create(
            code='F-PR-040-CH01',
            name='Check List Minicargador MDO',
            vehicle_type='MINICARGADOR_MDO',
            description='Checklist de inspección para minicargador MDO',
            items=[
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Hidráulico', 'order': 2, 'question': 'Nivel de aceite hidráulico', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Cadenas', 'order': 3, 'question': 'Tensión de cadenas', 'response_type': 'yes_no_na', 'required': True},
            ],
            is_system_template=True,
            passing_score=80
        )
        
        # Template for Camión Supersucker
        self.templates['supersucker'] = ChecklistTemplate.objects.create(
            code='SUPERSUCKER-CH01',
            name='Check List Camión Supersucker',
            vehicle_type='CAMION_SUPERSUCKER',
            description='Checklist de inspección para camión supersucker',
            items=[
                {'section': 'Motor', 'order': 1, 'question': 'Nivel de aceite motor', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Vacío', 'order': 2, 'question': 'Presión de sistema de vacío', 'response_type': 'numeric', 'required': True},
                {'section': 'Tanque', 'order': 3, 'question': 'Estado de tanque de almacenamiento', 'response_type': 'yes_no_na', 'required': True},
                {'section': 'Mangueras', 'order': 4, 'question': 'Estado de mangueras de succión', 'response_type': 'yes_no_na', 'required': True},
            ],
            is_system_template=True,
            passing_score=80
        )
    
    def create_spare_parts(self):
        """Create spare parts inventory"""
        print("Creating spare parts...")
        
        parts_data = [
            {'part_number': 'FLT-001', 'name': 'Filtro de aceite motor', 'category': 'Filtros', 'quantity': 25, 'minimum_stock': 10, 'unit_cost': 15000},
            {'part_number': 'FLT-002', 'name': 'Filtro de aire', 'category': 'Filtros', 'quantity': 8, 'minimum_stock': 15, 'unit_cost': 25000},
            {'part_number': 'BRK-001', 'name': 'Pastillas de freno delanteras', 'category': 'Frenos', 'quantity': 12, 'minimum_stock': 8, 'unit_cost': 45000},
            {'part_number': 'HYD-001', 'name': 'Aceite hidráulico ISO 68', 'category': 'Lubricantes', 'quantity': 50, 'minimum_stock': 20, 'unit_cost': 35000},
            {'part_number': 'TIR-001', 'name': 'Neumático 275/70R18', 'category': 'Neumáticos', 'quantity': 6, 'minimum_stock': 8, 'unit_cost': 180000},
            {'part_number': 'BLT-001', 'name': 'Correa de distribución', 'category': 'Motor', 'quantity': 4, 'minimum_stock': 5, 'unit_cost': 65000},
        ]
        
        for part_data in parts_data:
            SparePart.objects.create(
                location='Bodega Principal',
                supplier='Proveedor General',
                **part_data
            )
    
    def create_maintenance_plans(self):
        """Create maintenance plans"""
        print("Creating maintenance plans...")
        
        # Monthly preventive maintenance for Supersucker
        MaintenancePlan.objects.create(
            name='Mantenimiento Preventivo Mensual - Supersucker',
            asset=self.assets['supersucker1'],
            plan_type='PREVENTIVE',
            recurrence_type='MONTHLY',
            recurrence_interval=1,
            next_due_date=date.today() + timedelta(days=15),
            is_active=True,
            checklist_template=self.templates['supersucker'],
            estimated_duration=180,
            created_by=self.users['supervisor1']
        )
        
        # Weekly inspection for Camioneta
        MaintenancePlan.objects.create(
            name='Inspección Semanal - Camioneta MDO',
            asset=self.assets['camioneta1'],
            plan_type='PREVENTIVE',
            recurrence_type='WEEKLY',
            recurrence_interval=1,
            next_due_date=date.today() + timedelta(days=3),
            is_active=True,
            checklist_template=self.templates['camioneta'],
            estimated_duration=60,
            created_by=self.users['supervisor1']
        )
        
        # Monthly maintenance for Retroexcavadora
        MaintenancePlan.objects.create(
            name='Mantenimiento Mensual - Retroexcavadora',
            asset=self.assets['retro1'],
            plan_type='PREVENTIVE',
            recurrence_type='MONTHLY',
            recurrence_interval=1,
            next_due_date=date.today() + timedelta(days=20),
            is_active=True,
            checklist_template=self.templates['retro'],
            estimated_duration=120,
            created_by=self.users['supervisor2']
        )
    
    def create_work_orders(self):
        """Create work orders in various states"""
        print("Creating work orders...")
        
        # Pending work order
        WorkOrder.objects.create(
            work_order_number='WO-2024-001',
            title='Cambio de aceite - Camioneta MDO 001',
            description='Mantenimiento preventivo programado',
            asset=self.assets['camioneta1'],
            work_order_type='PREVENTIVE',
            priority='MEDIUM',
            status='PENDING',
            created_by=self.users['supervisor1'],
            scheduled_date=date.today() + timedelta(days=2)
        )
        
        # Assigned work order
        WorkOrder.objects.create(
            work_order_number='WO-2024-002',
            title='Inspección sistema hidráulico - Retroexcavadora',
            description='Revisión completa del sistema hidráulico',
            asset=self.assets['retro1'],
            work_order_type='INSPECTION',
            priority='HIGH',
            status='ASSIGNED',
            assigned_to=self.users['operator1'],
            created_by=self.users['supervisor2'],
            scheduled_date=date.today() + timedelta(days=1)
        )
        
        # In progress work order
        WorkOrder.objects.create(
            work_order_number='WO-2024-003',
            title='Reparación de frenos - Camioneta MDO 002',
            description='Cambio de pastillas de freno delanteras',
            asset=self.assets['camioneta2'],
            work_order_type='CORRECTIVE',
            priority='URGENT',
            status='IN_PROGRESS',
            assigned_to=self.users['operator2'],
            created_by=self.users['supervisor1'],
            scheduled_date=date.today(),
            started_at=date.today()
        )
        
        # Completed work order
        WorkOrder.objects.create(
            work_order_number='WO-2024-004',
            title='Mantenimiento preventivo - Cargador Frontal',
            description='Mantenimiento preventivo completo',
            asset=self.assets['cargador1'],
            work_order_type='PREVENTIVE',
            priority='MEDIUM',
            status='COMPLETED',
            assigned_to=self.users['operator3'],
            created_by=self.users['supervisor2'],
            scheduled_date=date.today() - timedelta(days=2),
            started_at=date.today() - timedelta(days=2),
            completed_at=date.today() - timedelta(days=1),
            actual_hours=Decimal('2.5'),
            completion_notes='Mantenimiento completado sin problemas'
        )
    
    def create_predictions_and_alerts(self):
        """Create ML predictions and alerts"""
        print("Creating predictions and alerts...")
        
        # High-risk prediction for Supersucker
        prediction1 = FailurePrediction.objects.create(
            asset=self.assets['supersucker1'],
            failure_probability=Decimal('82.5'),
            confidence_score=Decimal('88.0'),
            predicted_failure_date=date.today() + timedelta(days=10),
            model_version='v1.0',
            input_features={'operating_hours': 4800, 'days_since_maintenance': 85},
            recommendations='Programar mantenimiento inmediato del sistema de vacío',
            risk_level='CRITICAL'
        )
        
        Alert.objects.create(
            alert_type='PREDICTION',
            severity='CRITICAL',
            title='Alta probabilidad de falla - Camión Supersucker 001',
            message='El modelo ML predice una probabilidad de falla del 82.5% en los próximos 10 días',
            asset=self.assets['supersucker1'],
            prediction=prediction1
        )
        
        # Medium-risk prediction for Retroexcavadora
        FailurePrediction.objects.create(
            asset=self.assets['retro1'],
            failure_probability=Decimal('45.0'),
            confidence_score=Decimal('85.0'),
            model_version='v1.0',
            input_features={'operating_hours': 2200, 'days_since_maintenance': 30},
            recommendations='Continuar con mantenimiento programado',
            risk_level='MEDIUM'
        )
        
        # Low stock alert
        Alert.objects.create(
            alert_type='LOW_STOCK',
            severity='WARNING',
            title='Stock bajo - Filtro de aire',
            message='El stock de filtros de aire está por debajo del mínimo (8/15)',
            asset=None
        )
    
    def create_notifications(self):
        """Create notifications for users"""
        print("Creating notifications...")
        
        # Notification for operator1
        Notification.objects.create(
            user=self.users['operator1'],
            notification_type='WORK_ORDER_ASSIGNED',
            title='Nueva orden de trabajo asignada',
            message='Se te ha asignado: Inspección sistema hidráulico - Retroexcavadora',
            data={'work_order_id': 'WO-2024-002'}
        )
        
        # Notification for supervisor1
        Notification.objects.create(
            user=self.users['supervisor1'],
            notification_type='ALERT',
            title='Alerta crítica de predicción',
            message='Alta probabilidad de falla detectada en Camión Supersucker 001',
            data={'asset_id': str(self.assets['supersucker1'].id)}
        )
        
        # Notification for admin
        Notification.objects.create(
            user=self.users['admin'],
            notification_type='ALERT',
            title='Stock bajo detectado',
            message='Filtro de aire por debajo del stock mínimo',
            data={'spare_part': 'FLT-002'}
        )
    
    def print_summary(self):
        """Print summary of generated data"""
        print("\n" + "="*50)
        print("DEMO DATA SUMMARY")
        print("="*50)
        print(f"Users created: {User.objects.count()}")
        print(f"  - Admins: {User.objects.filter(role__name='ADMIN').count()}")
        print(f"  - Supervisors: {User.objects.filter(role__name='SUPERVISOR').count()}")
        print(f"  - Operators: {User.objects.filter(role__name='OPERADOR').count()}")
        print(f"\nAssets created: {Asset.objects.count()}")
        print(f"Checklist templates: {ChecklistTemplate.objects.count()}")
        print(f"Spare parts: {SparePart.objects.count()}")
        print(f"Maintenance plans: {MaintenancePlan.objects.count()}")
        print(f"Work orders: {WorkOrder.objects.count()}")
        print(f"Predictions: {FailurePrediction.objects.count()}")
        print(f"Alerts: {Alert.objects.count()}")
        print(f"Notifications: {Notification.objects.count()}")
        print("\n" + "="*50)
        print("TEST CREDENTIALS")
        print("="*50)
        print("Admin: admin@somacor.com / Demo2024!")
        print("Supervisor: supervisor1@somacor.com / Demo2024!")
        print("Operator: operator1@somacor.com / Demo2024!")
        print("="*50)


# Django management command
class Command(BaseCommand):
    help = 'Generate demo data for user acceptance testing'
    
    def handle(self, *args, **options):
        generator = DemoDataGenerator()
        generator.generate_all()
