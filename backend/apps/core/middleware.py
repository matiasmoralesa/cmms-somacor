"""
Custom middleware for CMMS system
"""
import time
from django.utils.deprecation import MiddlewareMixin


class RateLimitHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add rate limit headers to responses
    """
    
    def process_response(self, request, response):
        """Add rate limit headers to response"""
        
        # Check if throttling was applied
        if hasattr(request, 'throttle_wait'):
            # Request was throttled
            response['X-RateLimit-Limit'] = getattr(request, 'throttle_limit', 'unknown')
            response['X-RateLimit-Remaining'] = 0
            response['X-RateLimit-Reset'] = int(time.time() + request.throttle_wait)
            response['Retry-After'] = int(request.throttle_wait)
        elif hasattr(request, 'throttle_limit'):
            # Request was not throttled, add current limits
            response['X-RateLimit-Limit'] = request.throttle_limit
            response['X-RateLimit-Remaining'] = getattr(request, 'throttle_remaining', 'unknown')
            response['X-RateLimit-Reset'] = getattr(request, 'throttle_reset', int(time.time() + 60))
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for monitoring
    """
    
    def process_request(self, request):
        """Log request start time"""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request completion"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = duration * 1000
            
            # Add duration header
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # Use structured logging
            from apps.core.logging_utils import performance_logger
            
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            
            request_id = getattr(request, 'id', None)
            
            performance_logger.log_request(
                method=request.method,
                path=request.path,
                duration_ms=duration_ms,
                status_code=response.status_code,
                user_id=user_id,
                request_id=request_id
            )
        
        return response



class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses
    """
    
    def process_response(self, request, response):
        """Add security headers"""
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://storage.googleapis.com; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (HSTS)
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # X-Frame-Options (clickjacking protection)
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options (MIME sniffing protection)
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=()'
        )
        
        return response


class InputSanitizationMiddleware(MiddlewareMixin):
    """
    Middleware to sanitize and validate input data
    """
    
    def process_request(self, request):
        """Sanitize request data"""
        import re
        
        # Check for common SQL injection patterns
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(--)",
            r"(;.*--)",
        ]
        
        # Check for XSS patterns
        xss_patterns = [
            r"(<script[^>]*>.*?</script>)",
            r"(javascript:)",
            r"(onerror\s*=)",
            r"(onload\s*=)",
        ]
        
        # Get request data
        data_to_check = []
        if request.method in ['POST', 'PUT', 'PATCH']:
            if hasattr(request, 'body'):
                try:
                    import json
                    body = json.loads(request.body)
                    data_to_check.extend(self._extract_strings(body))
                except:
                    pass
        
        # Check query parameters
        for value in request.GET.values():
            data_to_check.append(value)
        
        # Validate data
        for data in data_to_check:
            if isinstance(data, str):
                # Check SQL injection
                for pattern in sql_patterns:
                    if re.search(pattern, data, re.IGNORECASE):
                        import logging
                        logger = logging.getLogger('security')
                        logger.warning(
                            f"Potential SQL injection attempt detected: "
                            f"{request.method} {request.path} - IP: {self._get_client_ip(request)}"
                        )
                
                # Check XSS
                for pattern in xss_patterns:
                    if re.search(pattern, data, re.IGNORECASE):
                        import logging
                        logger = logging.getLogger('security')
                        logger.warning(
                            f"Potential XSS attempt detected: "
                            f"{request.method} {request.path} - IP: {self._get_client_ip(request)}"
                        )
        
        return None
    
    def _extract_strings(self, obj):
        """Recursively extract strings from nested objects"""
        strings = []
        if isinstance(obj, dict):
            for value in obj.values():
                strings.extend(self._extract_strings(value))
        elif isinstance(obj, list):
            for item in obj:
                strings.extend(self._extract_strings(item))
        elif isinstance(obj, str):
            strings.append(obj)
        return strings
    
    def _get_client_ip(self, request):
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
        request.id = str(uuid.uuid4())
        return None
    
    def process_response(self, request, response):
        """Add request ID to response headers"""
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id
        return response



class CacheMiddleware(MiddlewareMixin):
    """
    Middleware para cachear respuestas de API
    """
    
    # Rutas que deben ser cacheadas
    CACHEABLE_PATHS = [
        '/api/v1/assets/',
        '/api/v1/inventory/spare-parts/',
        '/api/v1/config/',
    ]
    
    # Timeout por defecto (5 minutos)
    DEFAULT_TIMEOUT = 300
    
    def process_request(self, request):
        """Check if response is cached"""
        # Solo cachear GET requests
        if request.method != 'GET':
            return None
        
        # Verificar si la ruta debe ser cacheada
        if not any(request.path.startswith(path) for path in self.CACHEABLE_PATHS):
            return None
        
        # Generar cache key
        cache_key = self._get_cache_key(request)
        
        # Intentar obtener del cache
        from django.core.cache import cache
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # Agregar header indicando que viene del cache
            cached_response['X-Cache'] = 'HIT'
            return cached_response
        
        # Guardar cache key en request para usarlo en process_response
        request._cache_key = cache_key
        return None
    
    def process_response(self, request, response):
        """Cache successful responses"""
        # Solo cachear si hay cache key y la respuesta es exitosa
        if not hasattr(request, '_cache_key'):
            return response
        
        if response.status_code != 200:
            return response
        
        # Cachear respuesta
        from django.core.cache import cache
        cache.set(request._cache_key, response, self.DEFAULT_TIMEOUT)
        
        # Agregar header indicando que no viene del cache
        response['X-Cache'] = 'MISS'
        
        return response
    
    def _get_cache_key(self, request):
        """Generate cache key for request"""
        # Incluir path, query params y usuario
        user_id = request.user.id if request.user.is_authenticated else 'anon'
        query_string = request.META.get('QUERY_STRING', '')
        
        import hashlib
        key_string = f"{request.path}:{query_string}:{user_id}"
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"view_cache:{key_hash}"
