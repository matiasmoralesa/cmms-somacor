"""
Custom middleware for CMMS system
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class PermissionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log permission denials and authentication failures
    """
    
    def process_response(self, request, response):
        """Log permission denials"""
        if response.status_code == 403:
            user = request.user if request.user.is_authenticated else 'Anonymous'
            logger.warning(
                f"Permission denied: {request.method} {request.path} "
                f"by user {user}"
            )
        
        if response.status_code == 401:
            logger.warning(
                f"Authentication failed: {request.method} {request.path}"
            )
        
        return response


class LicenseCheckMiddleware(MiddlewareMixin):
    """
    Middleware to check OPERADOR license on every request
    Adds warning header if license is expiring soon
    """
    
    def process_request(self, request):
        """Check license before processing request"""
        if request.user.is_authenticated and request.user.is_operador():
            # Block request if license is expired
            if not request.user.has_valid_license():
                return JsonResponse(
                    {
                        'error': 'Licencia vencida',
                        'detail': 'Tu licencia está vencida. Contacta al administrador para renovarla.',
                        'expiration_date': request.user.license_expiration_date.isoformat() if request.user.license_expiration_date else None
                    },
                    status=403
                )
    
    def process_response(self, request, response):
        """Add license warning header if expiring soon"""
        if request.user.is_authenticated and request.user.is_operador():
            if request.user.license_expires_soon():
                days = request.user.days_until_license_expiration()
                response['X-License-Warning'] = f'License expires in {days} days'
        
        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all state-changing operations for audit trail
    """
    
    METHODS_TO_LOG = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def process_request(self, request):
        """Store request start time"""
        import time
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """Log state-changing operations"""
        if request.method in self.METHODS_TO_LOG:
            import time
            duration = time.time() - getattr(request, '_start_time', time.time())
            
            user = request.user if request.user.is_authenticated else 'Anonymous'
            
            log_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': str(user),
                'user_id': str(request.user.id) if request.user.is_authenticated else None,
                'role': request.user.role.name if request.user.is_authenticated else None,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
            }
            
            # Log based on status code
            if response.status_code >= 500:
                logger.error(f"Audit log: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"Audit log: {json.dumps(log_data)}")
            else:
                logger.info(f"Audit log: {json.dumps(log_data)}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware to add unique request ID for tracing
    """
    
    def process_request(self, request):
        """Add request ID"""
        import uuid
        request.request_id = str(uuid.uuid4())
    
    def process_response(self, request, response):
        """Add request ID to response header"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        return response


class RoleBasedRateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to apply different rate limits based on user role
    (This is a simple implementation - for production use django-ratelimit or similar)
    """
    
    RATE_LIMITS = {
        'ADMIN': 1000,  # requests per minute
        'SUPERVISOR': 500,
        'OPERADOR': 200,
        'anonymous': 50
    }
    
    def process_request(self, request):
        """Check rate limit based on role"""
        # This is a placeholder - implement actual rate limiting logic
        # using cache backend (Redis) to track request counts
        pass
