"""
Monitoring middleware for tracking work order metrics
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class WorkOrderMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor work order creation and track asset assignment metrics.
    Logs warnings when work orders are created without assets and tracks patterns.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.work_orders_without_asset_count = 0
        self.total_work_orders_count = 0
        
    def process_response(self, request, response):
        """Process response to monitor work order creation"""
        
        # Only monitor work order creation endpoints
        if not request.path.startswith('/api/v1/work-orders/'):
            return response
        
        # Only monitor POST requests (creation)
        if request.method != 'POST':
            return response
        
        # Only process successful creations
        if response.status_code != 201:
            return response
        
        try:
            # Parse response data
            if hasattr(response, 'data'):
                data = response.data
            else:
                # For non-DRF responses
                data = json.loads(response.content.decode('utf-8'))
            
            # Track work order creation
            self.total_work_orders_count += 1
            
            # Check if asset is assigned
            if not data.get('asset'):
                self.work_orders_without_asset_count += 1
                
                # Log warning
                logger.warning(
                    f"Work order created without asset: {data.get('work_order_number')}",
                    extra={
                        'work_order_id': data.get('id'),
                        'work_order_number': data.get('work_order_number'),
                        'work_order_type': data.get('work_order_type'),
                        'user': request.user.email if hasattr(request, 'user') else 'unknown',
                        'has_asset': False
                    }
                )
                
                # Calculate percentage
                percentage = (self.work_orders_without_asset_count / self.total_work_orders_count) * 100
                
                # Alert if threshold exceeded (e.g., 30%)
                threshold = getattr(settings, 'WORK_ORDER_NO_ASSET_THRESHOLD', 30)
                if percentage > threshold:
                    logger.error(
                        f"Work orders without asset threshold exceeded: {percentage:.2f}% "
                        f"({self.work_orders_without_asset_count}/{self.total_work_orders_count})",
                        extra={
                            'alert_type': 'work_order_no_asset_threshold',
                            'percentage': percentage,
                            'threshold': threshold,
                            'count_without_asset': self.work_orders_without_asset_count,
                            'total_count': self.total_work_orders_count
                        }
                    )
                    
                    # TODO: Send alert via Pub/Sub or email
                    # self._send_alert(percentage, threshold)
            else:
                logger.info(
                    f"Work order created with asset: {data.get('work_order_number')}",
                    extra={
                        'work_order_id': data.get('id'),
                        'work_order_number': data.get('work_order_number'),
                        'asset_id': data.get('asset'),
                        'asset_name': data.get('asset_name'),
                        'has_asset': True
                    }
                )
        
        except Exception as e:
            # Don't break the response if monitoring fails
            logger.error(f"Error in WorkOrderMonitoringMiddleware: {e}")
        
        return response
    
    def _send_alert(self, percentage, threshold):
        """
        Send alert when threshold is exceeded.
        This can be implemented to send notifications via:
        - Email
        - Telegram bot
        - Cloud Pub/Sub
        - Slack webhook
        """
        # TODO: Implement alert mechanism
        pass


class WorkOrderMetricsMiddleware(MiddlewareMixin):
    """
    Middleware to collect and log work order metrics for monitoring dashboards.
    """
    
    def process_request(self, request):
        """Add request start time for performance tracking"""
        import time
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request metrics"""
        
        # Only track work order endpoints
        if not request.path.startswith('/api/v1/work-orders/'):
            return response
        
        try:
            # Calculate request duration
            if hasattr(request, '_start_time'):
                import time
                duration = time.time() - request._start_time
                
                # Log metrics
                logger.info(
                    f"Work Order API Request",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration_ms': round(duration * 1000, 2),
                        'user': request.user.email if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
                    }
                )
                
                # Alert on slow requests (> 2 seconds)
                if duration > 2.0:
                    logger.warning(
                        f"Slow Work Order API request detected: {duration:.2f}s",
                        extra={
                            'method': request.method,
                            'path': request.path,
                            'duration_seconds': duration
                        }
                    )
        
        except Exception as e:
            logger.error(f"Error in WorkOrderMetricsMiddleware: {e}")
        
        return response
