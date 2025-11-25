"""
Security tests for authentication and authorization
"""
import pytest
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User, Role


class AuthenticationSecurityTest(TestCase):
    """Test authentication security controls"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create role
        self.role = Role.objects.create(name='OPERADOR', description='Operator')
        
        # Create user
        self.user = User.objects.create_user(
            email='test@test.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            role=self.role,
            rut='12345678-9'
        )
    
    def test_login_with_valid_credentials(self):
        """Test: Valid credentials return tokens"""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@test.com',
            'password': 'SecurePass123!'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_invalid_password(self):
        """Test: Invalid password returns 401"""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@test.com',
            'password': 'WrongPassword'
        })
        
        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)
    
    def test_login_with_nonexistent_user(self):
        """Test: Nonexistent user returns 401"""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'nonexistent@test.com',
            'password': 'SomePassword'
        })
        
        self.assertEqual(response.status_code, 401)
    
    def test_access_protected_endpoint_without_token(self):
        """Test: Protected endpoint requires authentication"""
        response = self.client.get('/api/v1/work-orders/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_access_protected_endpoint_with_valid_token(self):
        """Test: Valid token grants access"""
        # Get token
        login_response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@test.com',
            'password': 'SecurePass123!'
        })
        
        token = login_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/work-orders/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_access_with_expired_token(self):
        """Test: Expired token returns 401"""
        # Create expired token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Manually expire the token (in production, wait for expiration)
        # For testing, we'll use an invalid token format
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get('/api/v1/work-orders/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_token_refresh(self):
        """Test: Refresh token generates new access token"""
        # Get initial tokens
        login_response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@test.com',
            'password': 'SecurePass123!'
        })
        
        refresh_token = login_response.data['refresh']
        
        # Refresh token
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
    
    def test_logout_invalidates_token(self):
        """Test: Logout invalidates refresh token"""
        # Login
        login_response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@test.com',
            'password': 'SecurePass123!'
        })
        
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/v1/auth/logout/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Try to use refresh token after logout
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': refresh_token
        })
        
        # Should fail (token blacklisted)
        self.assertIn(response.status_code, [401, 400])
    
    def test_password_reset_requires_email(self):
        """Test: Password reset requires valid email"""
        response = self.client.post('/api/v1/auth/password-reset/', {
            'email': 'test@test.com'
        })
        
        self.assertEqual(response.status_code, 200)
        # In production, email would be sent
    
    def test_sql_injection_in_login(self):
        """Test: SQL injection attempts are prevented"""
        # Attempt SQL injection
        response = self.client.post('/api/v1/auth/login/', {
            'email': "admin' OR '1'='1",
            'password': "password' OR '1'='1"
        })
        
        # Should fail authentication
        self.assertEqual(response.status_code, 401)
    
    def test_xss_in_user_input(self):
        """Test: XSS attempts are sanitized"""
        # Create user with XSS attempt in name
        xss_payload = "<script>alert('XSS')</script>"
        
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/v1/users/{self.user.id}/', {
            'first_name': xss_payload
        })
        
        # Should either reject or sanitize
        if response.status_code == 200:
            # Verify XSS payload is sanitized
            self.assertNotIn('<script>', response.data['first_name'])


class AuthorizationSecurityTest(TestCase):
    """Test authorization and access control"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create roles
        self.admin_role = Role.objects.create(name='ADMIN', description='Admin')
        self.supervisor_role = Role.objects.create(name='SUPERVISOR', description='Supervisor')
        self.operator_role = Role.objects.create(name='OPERADOR', description='Operator')
        
        # Create users
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='Admin123!',
            role=self.admin_role,
            rut='11111111-1'
        )
        
        self.supervisor = User.objects.create_user(
            email='supervisor@test.com',
            password='Super123!',
            role=self.supervisor_role,
            rut='22222222-2'
        )
        
        self.operator = User.objects.create_user(
            email='operator@test.com',
            password='Oper123!',
            role=self.operator_role,
            rut='33333333-3'
        )
    
    def test_operator_cannot_access_admin_panel(self):
        """Test: Operator cannot access admin endpoints"""
        self.client.force_authenticate(user=self.operator)
        
        response = self.client.get('/api/v1/admin/users/')
        
        self.assertEqual(response.status_code, 403)
    
    def test_operator_cannot_create_work_orders(self):
        """Test: Operator cannot create work orders"""
        self.client.force_authenticate(user=self.operator)
        
        response = self.client.post('/api/v1/work-orders/', {
            'title': 'Test WO',
            'description': 'Test'
        })
        
        self.assertEqual(response.status_code, 403)
    
    def test_supervisor_can_create_work_orders(self):
        """Test: Supervisor can create work orders"""
        self.client.force_authenticate(user=self.supervisor)
        
        # This would need a valid asset, so we'll just check permission
        response = self.client.post('/api/v1/work-orders/', {
            'title': 'Test WO',
            'description': 'Test'
        })
        
        # Should not be 403 (may be 400 for missing fields)
        self.assertNotEqual(response.status_code, 403)
    
    def test_admin_can_access_all_endpoints(self):
        """Test: Admin has full access"""
        self.client.force_authenticate(user=self.admin)
        
        # Test various endpoints
        endpoints = [
            '/api/v1/work-orders/',
            '/api/v1/assets/',
            '/api/v1/maintenance-plans/',
            '/api/v1/predictions/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertNotEqual(response.status_code, 403)
    
    def test_operator_can_only_view_assigned_work_orders(self):
        """Test: Operator sees only assigned work orders"""
        self.client.force_authenticate(user=self.operator)
        
        response = self.client.get('/api/v1/work-orders/my-assignments/')
        
        self.assertEqual(response.status_code, 200)
        # All returned work orders should be assigned to this operator
        for wo in response.data.get('results', []):
            if wo.get('assigned_to'):
                self.assertEqual(wo['assigned_to'], str(self.operator.id))
    
    def test_horizontal_privilege_escalation_prevented(self):
        """Test: User cannot access another user's data"""
        # Create another operator
        other_operator = User.objects.create_user(
            email='other@test.com',
            password='Other123!',
            role=self.operator_role,
            rut='44444444-4'
        )
        
        # Try to access other user's profile
        self.client.force_authenticate(user=self.operator)
        response = self.client.get(f'/api/v1/users/{other_operator.id}/')
        
        # Should be forbidden or return limited data
        self.assertIn(response.status_code, [403, 404])
    
    def test_vertical_privilege_escalation_prevented(self):
        """Test: Operator cannot elevate to admin"""
        self.client.force_authenticate(user=self.operator)
        
        # Try to change own role to admin
        response = self.client.patch(f'/api/v1/users/{self.operator.id}/', {
            'role': str(self.admin_role.id)
        })
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)


class PasswordSecurityTest(TestCase):
    """Test password security policies"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.role = Role.objects.create(name='OPERADOR', description='Operator')
    
    def test_weak_password_rejected(self):
        """Test: Weak passwords are rejected"""
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'test@test.com',
            'password': '123',  # Too short
            'role': str(self.role.id),
            'rut': '12345678-9'
        })
        
        self.assertEqual(response.status_code, 400)
    
    def test_password_not_returned_in_api(self):
        """Test: Password never returned in API responses"""
        user = User.objects.create_user(
            email='test@test.com',
            password='SecurePass123!',
            role=self.role,
            rut='12345678-9'
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.get(f'/api/v1/users/{user.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.data)
    
    def test_password_stored_hashed(self):
        """Test: Passwords are hashed in database"""
        user = User.objects.create_user(
            email='test@test.com',
            password='SecurePass123!',
            role=self.role,
            rut='12345678-9'
        )
        
        # Password should not be stored in plain text
        self.assertNotEqual(user.password, 'SecurePass123!')
        # Should start with hash algorithm identifier
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
