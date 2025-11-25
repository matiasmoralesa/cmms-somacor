"""
Health check utilities for monitoring system health
"""
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
from typing import Dict, Any


class HealthChecker:
    """Utility class for performing health checks"""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """
        Check database connectivity and performance
        
        Returns:
            Dict with status and details
        """
        try:
            start_time = time.time()
            
            # Execute simple query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration_ms, 2),
                'database': connection.settings_dict['NAME']
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def check_cache() -> Dict[str, Any]:
        """
        Check cache (Redis) connectivity
        
        Returns:
            Dict with status and details
        """
        try:
            start_time = time.time()
            
            # Test cache set and get
            test_key = 'health_check_test'
            test_value = 'ok'
            cache.set(test_key, test_value, timeout=10)
            result = cache.get(test_key)
            cache.delete(test_key)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result == test_value:
                return {
                    'status': 'healthy',
                    'response_time_ms': round(duration_ms, 2)
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache read/write mismatch'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def check_storage() -> Dict[str, Any]:
        """
        Check Cloud Storage connectivity
        
        Returns:
            Dict with status and details
        """
        try:
            # Check if GCP credentials are configured
            if not settings.GCP_PROJECT_ID or not settings.GCP_STORAGE_BUCKET_NAME:
                return {
                    'status': 'not_configured',
                    'message': 'GCP Storage not configured'
                }
            
            # Try to import and test GCP storage
            from google.cloud import storage
            
            start_time = time.time()
            client = storage.Client(project=settings.GCP_PROJECT_ID)
            bucket = client.bucket(settings.GCP_STORAGE_BUCKET_NAME)
            
            # Check if bucket exists
            exists = bucket.exists()
            duration_ms = (time.time() - start_time) * 1000
            
            if exists:
                return {
                    'status': 'healthy',
                    'response_time_ms': round(duration_ms, 2),
                    'bucket': settings.GCP_STORAGE_BUCKET_NAME
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Bucket does not exist'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def check_pubsub() -> Dict[str, Any]:
        """
        Check Cloud Pub/Sub connectivity
        
        Returns:
            Dict with status and details
        """
        try:
            # Check if GCP credentials are configured
            if not settings.GCP_PROJECT_ID:
                return {
                    'status': 'not_configured',
                    'message': 'GCP Pub/Sub not configured'
                }
            
            from google.cloud import pubsub_v1
            
            start_time = time.time()
            publisher = pubsub_v1.PublisherClient()
            
            # Try to get topic
            topic_path = publisher.topic_path(
                settings.GCP_PROJECT_ID,
                settings.GCP_PUBSUB_TOPIC_NOTIFICATIONS
            )
            
            # This will raise exception if topic doesn't exist or no permissions
            publisher.get_topic(request={"topic": topic_path})
            
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration_ms, 2),
                'topic': settings.GCP_PUBSUB_TOPIC_NOTIFICATIONS
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get system information
        
        Returns:
            Dict with system details
        """
        import platform
        import sys
        import django
        
        return {
            'python_version': sys.version,
            'django_version': django.get_version(),
            'platform': platform.platform(),
            'debug_mode': settings.DEBUG
        }
    
    @staticmethod
    def perform_full_health_check() -> Dict[str, Any]:
        """
        Perform full health check of all dependencies
        
        Returns:
            Dict with overall status and individual checks
        """
        checks = {
            'database': HealthChecker.check_database(),
            'cache': HealthChecker.check_cache(),
            'storage': HealthChecker.check_storage(),
            'pubsub': HealthChecker.check_pubsub(),
        }
        
        # Determine overall status
        unhealthy_checks = [
            name for name, result in checks.items()
            if result.get('status') == 'unhealthy'
        ]
        
        if unhealthy_checks:
            overall_status = 'unhealthy'
        elif any(result.get('status') == 'not_configured' for result in checks.values()):
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': checks,
            'system': HealthChecker.get_system_info()
        }
