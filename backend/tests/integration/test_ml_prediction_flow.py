"""
End-to-end integration test for ML prediction flow
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from apps.authentication.models import User, Role
from apps.assets.models import Asset
from apps.predictions.models import FailurePrediction, Alert
from apps.work_orders.models import WorkOrder


class MLPredictionFlowTest(TestCase):
    """Test complete ML prediction workflow"""
    
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
        
        # Create assets
        self.asset_high_risk = Asset.objects.create(
            name='Cargador Frontal MDO 001',
            asset_code='CF-001',
            vehicle_type='CARGADOR_FRONTAL_MDO',
            serial_number='SN003',
            license_plate='EE-FF-33',
            status='OPERATIONAL',
            criticality='HIGH'
        )
        
        self.asset_low_risk = Asset.objects.create(
            name='Minicargador MDO 001',
            asset_code='MC-001',
            vehicle_type='MINICARGADOR_MDO',
            serial_number='SN004',
            license_plate='GG-HH-44',
            status='OPERATIONAL',
            criticality='MEDIUM'
        )
    
    @patch('apps.predictions.services.VertexAIClient.predict')
    def test_ml_prediction_low_risk(self, mock_predict):
        """Test: ML prediction with low failure probability"""
        
        # Mock Vertex AI response
        mock_predict.return_value = {
            'failure_probability': 25.5,
            'confidence_score': 85.0,
            'predicted_failure_date': None,
            'recommendations': 'Continue normal operation. Monitor regularly.'
        }
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Trigger prediction
        prediction_data = {
            'asset_id': str(self.asset_low_risk.id),
            'features': {
                'operating_hours': 1200,
                'days_since_maintenance': 15,
                'failure_count_30d': 0,
                'avg_temperature': 75
            }
        }
        
        response = self.client.post('/api/v1/predictions/predict/', prediction_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['risk_level'], 'LOW')
        self.assertLess(float(response.data['failure_probability']), 70.0)
        
        # Verify no alert was created for low risk
        alerts = Alert.objects.filter(asset=self.asset_low_risk, alert_type='PREDICTION')
        self.assertEqual(alerts.count(), 0)
    
    @patch('apps.predictions.services.VertexAIClient.predict')
    def test_ml_prediction_high_risk_creates_alert(self, mock_predict):
        """Test: ML prediction with high failure probability creates alert"""
        
        # Mock Vertex AI response with high risk
        mock_predict.return_value = {
            'failure_probability': 85.5,
            'confidence_score': 90.0,
            'predicted_failure_date': str(date.today() + timedelta(days=7)),
            'recommendations': 'Schedule immediate inspection. High risk of hydraulic system failure.'
        }
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Trigger prediction
        prediction_data = {
            'asset_id': str(self.asset_high_risk.id),
            'features': {
                'operating_hours': 5000,
                'days_since_maintenance': 90,
                'failure_count_30d': 3,
                'avg_temperature': 95
            }
        }
        
        response = self.client.post('/api/v1/predictions/predict/', prediction_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['risk_level'], 'CRITICAL')
        self.assertGreater(float(response.data['failure_probability']), 70.0)
        
        # Verify alert was created for high risk
        alerts = Alert.objects.filter(asset=self.asset_high_risk, alert_type='PREDICTION')
        self.assertGreater(alerts.count(), 0)
        
        alert = alerts.first()
        self.assertEqual(alert.severity, 'CRITICAL')
        self.assertFalse(alert.is_resolved)
    
    @patch('apps.predictions.services.VertexAIClient.predict')
    def test_prediction_triggers_preventive_work_order(self, mock_predict):
        """Test: High-risk prediction triggers preventive work order creation"""
        
        # Mock high-risk prediction
        mock_predict.return_value = {
            'failure_probability': 78.0,
            'confidence_score': 88.0,
            'predicted_failure_date': str(date.today() + timedelta(days=5)),
            'recommendations': 'Immediate maintenance required for transmission system.'
        }
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Trigger prediction
        prediction_data = {
            'asset_id': str(self.asset_high_risk.id),
            'features': {
                'operating_hours': 4500,
                'days_since_maintenance': 75,
                'failure_count_30d': 2,
                'avg_temperature': 90
            }
        }
        
        response = self.client.post('/api/v1/predictions/predict/', prediction_data, format='json')
        prediction_id = response.data['id']
        
        # Create predictive work order based on prediction
        wo_data = {
            'title': 'Mantenimiento Predictivo - Alta Probabilidad de Falla',
            'description': f"Predicción ID: {prediction_id}. {response.data['recommendations']}",
            'asset': str(self.asset_high_risk.id),
            'work_order_type': 'PREDICTIVE',
            'priority': 'URGENT',
            'scheduled_date': str(date.today() + timedelta(days=2))
        }
        
        response = self.client.post('/api/v1/work-orders/', wo_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['work_order_type'], 'PREDICTIVE')
        self.assertEqual(response.data['priority'], 'URGENT')
    
    def test_asset_health_score_calculation(self):
        """Test: Asset health score calculation based on predictions"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create multiple predictions for the asset
        FailurePrediction.objects.create(
            asset=self.asset_high_risk,
            failure_probability=Decimal('75.0'),
            confidence_score=Decimal('85.0'),
            model_version='v1.0',
            input_features={},
            recommendations='Monitor closely',
            risk_level='HIGH'
        )
        
        FailurePrediction.objects.create(
            asset=self.asset_high_risk,
            failure_probability=Decimal('80.0'),
            confidence_score=Decimal('88.0'),
            model_version='v1.0',
            input_features={},
            recommendations='Schedule maintenance',
            risk_level='HIGH'
        )
        
        # Get asset health score
        response = self.client.get(f'/api/v1/predictions/asset/{self.asset_high_risk.id}/health-score/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('health_score', response.data)
        self.assertIn('trend', response.data)
        self.assertIn('recent_predictions', response.data)
        
        # Health score should be low due to high failure probabilities
        self.assertLess(response.data['health_score'], 50)
    
    def test_prediction_history_retrieval(self):
        """Test: Retrieve prediction history for an asset"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create predictions
        for i in range(3):
            FailurePrediction.objects.create(
                asset=self.asset_low_risk,
                failure_probability=Decimal(f'{20 + i * 5}.0'),
                confidence_score=Decimal('85.0'),
                model_version='v1.0',
                input_features={'test': i},
                recommendations='Normal operation',
                risk_level='LOW'
            )
        
        # Get predictions
        response = self.client.get(f'/api/v1/predictions/?asset={self.asset_low_risk.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify predictions are ordered by date (newest first)
        predictions = response.data['results']
        self.assertGreaterEqual(
            predictions[0]['prediction_date'],
            predictions[1]['prediction_date']
        )
    
    def test_alert_resolution_workflow(self):
        """Test: Alert creation and resolution workflow"""
        
        self.client.force_authenticate(user=self.supervisor)
        
        # Create prediction with alert
        prediction = FailurePrediction.objects.create(
            asset=self.asset_high_risk,
            failure_probability=Decimal('85.0'),
            confidence_score=Decimal('90.0'),
            model_version='v1.0',
            input_features={},
            recommendations='Immediate action required',
            risk_level='CRITICAL'
        )
        
        alert = Alert.objects.create(
            alert_type='PREDICTION',
            severity='CRITICAL',
            title='High Failure Risk Detected',
            message='Asset requires immediate attention',
            asset=self.asset_high_risk,
            prediction=prediction
        )
        
        # Get active alerts
        response = self.client.get('/api/v1/predictions/alerts/?is_resolved=false')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        
        # Resolve alert
        response = self.client.patch(
            f'/api/v1/predictions/alerts/{alert.id}/resolve/',
            {'resolution_notes': 'Maintenance completed'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_resolved'])
        self.assertIsNotNone(response.data['resolved_at'])
        self.assertEqual(str(response.data['resolved_by']), str(self.supervisor.id))
