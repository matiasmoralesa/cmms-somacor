"""
End-to-end integration test for maintenance plan execution
"""
import pytest
from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from apps.authentication.models import User, Role
from apps.assets.models import Asset
from apps.maintenance.models import MaintenancePlan
from apps.work_orders.models import WorkOrder
from apps.checklists.models import ChecklistTemplate


class MaintenancePlanExecutionTest(TestCase):
    """Test complete maintenance plan lifecycle"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create roles
        self.admin_role = Role.objects.create(name='ADMIN', description='Administrator')
        self.supervisor_role = Role.objects.create(name='SUPERVISOR', description='Supervisor')
        
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
        
        # Create asset
        self.asset = Asset.objects.create(
            name='Retroexcavadora MDO 001',
            asset_code='RE-001',
            vehicle_type='RETROEXCAVADORA_MDO',
            serial_number='SN002',
            license_plate='CC-DD-22',
            status='OPERATIONAL'
        )
        
        # Create checklist template
        self.template = ChecklistTemplate.objects.create(
            code='F-PR-034-CH01',
            name='Check Retroexcavadora MDO',
            vehicle_type='RETROEXCAVADORA_MDO',
            items=[
                {
                    'section': 'Motor',
                    'order': 1,
                    'question': 'Nivel de aceite motor',
                    'response_type': 'yes_no_na',
                    'required': True
                },
                {
                    'section': 'Hidráulico',
                    'order': 2,
                    'question': 'Nivel de aceite hidráulico',
                    'response_type': 'yes_no_na',
                    'required': True
                }
            ],
            is_system_template=True
        )
    
    def test_create_maintenance_plan(self):
        """Test: Create preventive maintenance plan"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        plan_data = {
            'name': 'Mantenimiento Preventivo Mensual',
            'asset': str(self.asset.id),
            'plan_type': 'PREVENTIVE',
            'recurrence_type': 'MONTHLY',
            'recurrence_interval': 1,
            'next_due_date': str(date.today() + timedelta(days=30)),
            'checklist_template': str(self.template.id),
            'estimated_duration': 120
        }
        
        response = self.client.post('/api/v1/maintenance-plans/', plan_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], plan_data['name'])
        self.assertTrue(response.data['is_active'])
        
        return response.data['id']
    
    def test_pause_and_resume_maintenance_plan(self):
        """Test: Pause and resume maintenance plan"""
        
        plan_id = self.test_create_maintenance_plan()
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Pause plan
        response = self.client.patch(f'/api/v1/maintenance-plans/{plan_id}/pause/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_active'])
        
        # Resume plan
        response = self.client.patch(f'/api/v1/maintenance-plans/{plan_id}/resume/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_active'])
    
    def test_maintenance_plan_generates_work_order(self):
        """Test: Maintenance plan automatically generates work order (simulated)"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create maintenance plan with due date today
        plan_data = {
            'name': 'Mantenimiento Inmediato',
            'asset': str(self.asset.id),
            'plan_type': 'PREVENTIVE',
            'recurrence_type': 'WEEKLY',
            'recurrence_interval': 1,
            'next_due_date': str(date.today()),
            'checklist_template': str(self.template.id),
            'estimated_duration': 60
        }
        
        response = self.client.post('/api/v1/maintenance-plans/', plan_data, format='json')
        plan_id = response.data['id']
        
        # Simulate Cloud Composer DAG creating work order
        # In production, this would be done by the preventive_maintenance DAG
        wo_data = {
            'title': f"Mantenimiento Programado: {plan_data['name']}",
            'description': f"Generado automáticamente desde plan de mantenimiento",
            'asset': str(self.asset.id),
            'work_order_type': 'PREVENTIVE',
            'priority': 'MEDIUM',
            'scheduled_date': str(date.today())
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('work_order_number', response.data)
        
        # Verify work order was created
        wo_id = response.data['id']
        response = self.client.get(f'/api/v1/work-orders/{wo_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['work_order_type'], 'PREVENTIVE')
    
    def test_complete_maintenance_workflow(self):
        """Test: Complete workflow from plan creation to work order completion"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # 1. Create maintenance plan
        plan_data = {
            'name': 'Mantenimiento Completo',
            'asset': str(self.asset.id),
            'plan_type': 'PREVENTIVE',
            'recurrence_type': 'MONTHLY',
            'recurrence_interval': 1,
            'next_due_date': str(date.today()),
            'checklist_template': str(self.template.id),
            'estimated_duration': 90
        }
        
        response = self.client.post('/api/v1/maintenance-plans/', plan_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # 2. Create work order from plan
        wo_data = {
            'title': 'Mantenimiento Programado',
            'asset': str(self.asset.id),
            'work_order_type': 'PREVENTIVE',
            'priority': 'MEDIUM',
            'assigned_to': str(self.supervisor.id)
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        wo_id = response.data['id']
        
        # 3. Start work order
        response = self.client.patch(
            f'/api/v1/work-orders/{wo_id}/status/',
            {'status': 'IN_PROGRESS'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Complete checklist
        checklist_data = {
            'template': str(self.template.id),
            'work_order': wo_id,
            'asset': str(self.asset.id),
            'responses': [
                {'item_order': 1, 'response': 'yes', 'notes': 'OK'},
                {'item_order': 2, 'response': 'yes', 'notes': 'OK'}
            ]
        }
        
        response = self.client.post('/api/v1/checklists/responses/', checklist_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # 5. Complete work order
        response = self.client.post(
            f'/api/v1/work-orders/{wo_id}/complete/',
            {
                'status': 'COMPLETED',
                'actual_hours': 1.5,
                'completion_notes': 'Mantenimiento completado exitosamente'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'COMPLETED')
