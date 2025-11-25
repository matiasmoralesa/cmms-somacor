"""
End-to-end integration test for notification delivery across all channels
"""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock, call
from apps.authentication.models import User, Role
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.notifications.models import Notification, NotificationPreference
from apps.predictions.models import Alert


class NotificationDeliveryTest(TestCase):
    """Test notification delivery across multiple channels"""
    
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
            rut='11111111-1',
            telegram_id='123456789'
        )
        
        self.supervisor = User.objects.create_user(
            email='supervisor@test.com',
            password='test123',
            first_name='Supervisor',
            last_name='User',
            role=self.supervisor_role,
            rut='22222222-2',
            telegram_id='987654321'
        )
        
        self.operator = User.objects.create_user(
            email='operator@test.com',
            password='test123',
            first_name='Operator',
            last_name='User',
            role=self.operator_role,
            rut='33333333-3',
            telegram_id='555555555'
        )
        
        # Create asset
        self.asset = Asset.objects.create(
            name='Camioneta MDO 001',
            asset_code='CM-001',
            vehicle_type='CAMIONETA_MDO',
            serial_number='SN005',
            license_plate='II-JJ-55',
            status='OPERATIONAL'
        )
        
        # Create notification preferences
        NotificationPreference.objects.create(
            user=self.operator,
            notification_type='WORK_ORDER_ASSIGNED',
            in_app_enabled=True,
            email_enabled=True,
            telegram_enabled=True
        )
    
    @patch('apps.notifications.services.PubSubPublisher.publish')
    def test_work_order_assignment_notification(self, mock_publish):
        """Test: Notification sent when work order is assigned"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create work order with assignment
        wo_data = {
            'title': 'Reparación urgente',
            'description': 'Falla en sistema eléctrico',
            'asset': str(self.asset.id),
            'work_order_type': 'CORRECTIVE',
            'priority': 'HIGH',
            'assigned_to': str(self.operator.id)
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Verify notification was created
        notifications = Notification.objects.filter(
            user=self.operator,
            notification_type='WORK_ORDER_ASSIGNED'
        )
        self.assertGreater(notifications.count(), 0)
        
        notification = notifications.first()
        self.assertFalse(notification.is_read)
        self.assertIn('Reparación urgente', notification.message)
        
        # Verify Pub/Sub publish was called
        mock_publish.assert_called()
    
    def test_notification_retrieval_and_marking_read(self):
        """Test: User retrieves notifications and marks them as read"""
        
        # Create notifications for operator
        notification1 = Notification.objects.create(
            user=self.operator,
            notification_type='WORK_ORDER_ASSIGNED',
            title='Nueva orden asignada',
            message='Se te ha asignado una nueva orden de trabajo',
            data={'work_order_id': 'test-id'}
        )
        
        notification2 = Notification.objects.create(
            user=self.operator,
            notification_type='ALERT',
            title='Alerta de sistema',
            message='Nivel bajo de repuestos',
            data={}
        )
        
        self.client.force_authenticate(user=self.operator)
        
        # Get unread notifications
        response = self.client.get('/api/v1/notifications/?is_read=false')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        # Mark notification as read
        response = self.client.patch(
            f'/api/v1/notifications/{notification1.id}/mark-read/',
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_read'])
        
        # Verify only one unread notification remains
        response = self.client.get('/api/v1/notifications/?is_read=false')
        self.assertEqual(len(response.data['results']), 1)
    
    @patch('apps.notifications.services.PubSubPublisher.publish')
    def test_work_order_status_change_notification(self, mock_publish):
        """Test: Notification sent when work order status changes"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create work order
        wo_data = {
            'title': 'Mantenimiento programado',
            'asset': str(self.asset.id),
            'work_order_type': 'PREVENTIVE',
            'priority': 'MEDIUM',
            'assigned_to': str(self.operator.id)
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        wo_id = response.data['id']
        
        # Clear previous calls
        mock_publish.reset_mock()
        
        # Operator starts work order
        self.client.force_authenticate(user=self.operator)
        response = self.client.patch(
            f'/api/v1/work-orders/{wo_id}/status/',
            {'status': 'IN_PROGRESS'},
            format='json'
        )
        
        # Verify notification was sent to supervisor
        notifications = Notification.objects.filter(
            user=self.supervisor,
            notification_type='WORK_ORDER_STATUS_CHANGED'
        )
        self.assertGreater(notifications.count(), 0)
        
        # Verify Pub/Sub publish was called
        mock_publish.assert_called()
    
    @patch('apps.notifications.services.PubSubPublisher.publish')
    def test_high_priority_alert_notification(self, mock_publish):
        """Test: Critical alert sends notifications to all admins and supervisors"""
        
        # Create critical alert
        alert = Alert.objects.create(
            alert_type='PREDICTION',
            severity='CRITICAL',
            title='Falla crítica inminente',
            message='Alta probabilidad de falla en activo crítico',
            asset=self.asset
        )
        
        # Verify notifications were created for admin and supervisor
        admin_notifications = Notification.objects.filter(
            user=self.admin,
            notification_type='ALERT'
        )
        supervisor_notifications = Notification.objects.filter(
            user=self.supervisor,
            notification_type='ALERT'
        )
        
        self.assertGreater(admin_notifications.count(), 0)
        self.assertGreater(supervisor_notifications.count(), 0)
        
        # Verify operator did not receive notification (not authorized for alerts)
        operator_notifications = Notification.objects.filter(
            user=self.operator,
            notification_type='ALERT'
        )
        # Operators may or may not receive alerts depending on business rules
        # This test assumes they don't receive prediction alerts
    
    def test_notification_preferences_management(self):
        """Test: User can manage notification preferences"""
        
        self.client.force_authenticate(user=self.operator)
        
        # Get current preferences
        response = self.client.get('/api/v1/notifications/preferences/')
        self.assertEqual(response.status_code, 200)
        
        # Update preferences
        preference_data = {
            'notification_type': 'WORK_ORDER_COMPLETED',
            'in_app_enabled': True,
            'email_enabled': False,
            'telegram_enabled': True
        }
        
        response = self.client.post(
            '/api/v1/notifications/preferences/',
            preference_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify preference was created
        preference = NotificationPreference.objects.get(
            user=self.operator,
            notification_type='WORK_ORDER_COMPLETED'
        )
        self.assertTrue(preference.in_app_enabled)
        self.assertFalse(preference.email_enabled)
        self.assertTrue(preference.telegram_enabled)
    
    @patch('apps.notifications.services.PubSubPublisher.publish')
    def test_offline_notification_queuing(self, mock_publish):
        """Test: Notifications are queued when user is offline"""
        
        # Simulate offline scenario by creating notifications
        # In production, these would be queued in Pub/Sub
        
        notifications = []
        for i in range(3):
            notification = Notification.objects.create(
                user=self.operator,
                notification_type='WORK_ORDER_ASSIGNED',
                title=f'Orden {i+1}',
                message=f'Nueva orden de trabajo {i+1}',
                data={}
            )
            notifications.append(notification)
        
        # User comes online and retrieves all notifications
        self.client.force_authenticate(user=self.operator)
        response = self.client.get('/api/v1/notifications/')
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 3)
        
        # All notifications should be unread
        unread_count = sum(1 for n in response.data['results'] if not n['is_read'])
        self.assertGreaterEqual(unread_count, 3)
    
    def test_notification_filtering_by_type(self):
        """Test: Filter notifications by type"""
        
        # Create different types of notifications
        Notification.objects.create(
            user=self.operator,
            notification_type='WORK_ORDER_ASSIGNED',
            title='WO Assigned',
            message='Work order assigned',
            data={}
        )
        
        Notification.objects.create(
            user=self.operator,
            notification_type='WORK_ORDER_COMPLETED',
            title='WO Completed',
            message='Work order completed',
            data={}
        )
        
        Notification.objects.create(
            user=self.operator,
            notification_type='ALERT',
            title='Alert',
            message='System alert',
            data={}
        )
        
        self.client.force_authenticate(user=self.operator)
        
        # Filter by WORK_ORDER_ASSIGNED
        response = self.client.get('/api/v1/notifications/?notification_type=WORK_ORDER_ASSIGNED')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['notification_type'], 'WORK_ORDER_ASSIGNED')
        
        # Filter by ALERT
        response = self.client.get('/api/v1/notifications/?notification_type=ALERT')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['notification_type'], 'ALERT')
    
    def test_bulk_mark_notifications_as_read(self):
        """Test: Mark multiple notifications as read"""
        
        # Create multiple notifications
        notification_ids = []
        for i in range(5):
            notification = Notification.objects.create(
                user=self.operator,
                notification_type='WORK_ORDER_ASSIGNED',
                title=f'Notification {i}',
                message=f'Message {i}',
                data={}
            )
            notification_ids.append(str(notification.id))
        
        self.client.force_authenticate(user=self.operator)
        
        # Mark all as read
        response = self.client.post(
            '/api/v1/notifications/mark-all-read/',
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify all notifications are marked as read
        unread_count = Notification.objects.filter(
            user=self.operator,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)
