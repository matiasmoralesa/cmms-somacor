"""
End-to-end integration test for complete work order lifecycle
"""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from apps.authentication.models import User, Role
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.checklists.models import ChecklistTemplate, ChecklistResponse


class WorkOrderLifecycleTest(TestCase):
    """Test complete work order lifecycle from creation to completion"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create roles
        self.admin_role = Role.objects.create(name='ADMIN', description='Administrator')
        self.supervisor_role = Role.objects.create(name='SUPERVISOR', description='Supervisor')
        self.operator_role = Role.objects.create(name='OPERADOR', description='Operator')
        
        # Create users
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            last_name='User',
            role=self.admin_role,
            rut='11111111-1'
        )
        
        self.supervisor = User.objects.create_user(
            email='supervisor@test.com',
            password='test123',
            first_name='Supervisor',
            last_name='User',
            role=self.supervisor_role,
            rut='22222222-2'
        )
        
        self.operator = User.objects.create_user(
            email='operator@test.com',
            password='test123',
            first_name='Operator',
            last_name='User',
            role=self.operator_role,
            rut='33333333-3',
            license_type='MUNICIPAL',
            license_expiration_date='2025-12-31'
        )
        
        # Create asset
        self.asset = Asset.objects.create(
            name='Camión Supersucker 001',
            asset_code='CS-001',
            vehicle_type='CAMION_SUPERSUCKER',
            serial_number='SN001',
            license_plate='AA-BB-11',
            status='OPERATIONAL'
        )
    
    def test_complete_work_order_lifecycle(self):
        """Test: Create → Assign → Start → Complete work order"""
        
        # 1. Supervisor creates work order
        self.client.force_authenticate(user=self.supervisor)
        
        wo_data = {
            'title': 'Mantenimiento preventivo mensual',
            'description': 'Revisión general del vehículo',
            'asset': str(self.asset.id),
            'work_order_type': 'PREVENTIVE',
            'priority': 'MEDIUM',
            'assigned_to': str(self.operator.id),
            'scheduled_date': '2024-11-20T09:00:00Z'
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('work_order_number', response.data)
        
        wo_id = response.data['id']
        
        # 2. Operator views assigned work order
        self.client.force_authenticate(user=self.operator)
        
        response = self.client.get('/api/v1/work-orders/my-assignments/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(wo['id'] == wo_id for wo in response.data['results']))
        
        # 3. Operator starts work order
        response = self.client.patch(
            f'/api/v1/work-orders/{wo_id}/status/',
            {'status': 'IN_PROGRESS'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'IN_PROGRESS')
        
        # 4. Operator completes work order
        completion_data = {
            'status': 'COMPLETED',
            'actual_hours': 2.5,
            'completion_notes': 'Mantenimiento completado sin problemas'
        }
        
        response = self.client.post(
            f'/api/v1/work-orders/{wo_id}/complete/',
            completion_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'COMPLETED')
        self.assertIsNotNone(response.data['completed_at'])
        
        # 5. Verify work order is completed
        response = self.client.get(f'/api/v1/work-orders/{wo_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'COMPLETED')
        self.assertEqual(float(response.data['actual_hours']), 2.5)
    
    def test_work_order_with_checklist(self):
        """Test: Work order with checklist execution"""
        
        # Create checklist template
        template = ChecklistTemplate.objects.create(
            code='TEST-CH01',
            name='Test Checklist',
            vehicle_type='CAMION_SUPERSUCKER',
            items=[
                {
                    'section': 'Motor',
                    'order': 1,
                    'question': 'Nivel de aceite',
                    'response_type': 'yes_no_na',
                    'required': True
                }
            ],
            is_system_template=False
        )
        
        # Create work order
        self.client.force_authenticate(user=self.supervisor)
        
        wo_data = {
            'title': 'Inspección con checklist',
            'asset': str(self.asset.id),
            'work_order_type': 'INSPECTION',
            'priority': 'MEDIUM',
            'assigned_to': str(self.operator.id)
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        wo_id = response.data['id']
        
        # Operator completes checklist
        self.client.force_authenticate(user=self.operator)
        
        checklist_data = {
            'template': str(template.id),
            'work_order': wo_id,
            'asset': str(self.asset.id),
            'responses': [
                {
                    'item_order': 1,
                    'response': 'yes',
                    'notes': 'Nivel correcto'
                }
            ]
        }
        
        response = self.client.post('/api/v1/checklists/responses/', checklist_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('score', response.data)
        
        # Complete work order
        response = self.client.post(
            f'/api/v1/work-orders/{wo_id}/complete/',
            {
                'status': 'COMPLETED',
                'actual_hours': 1.0,
                'completion_notes': 'Inspección completada'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
