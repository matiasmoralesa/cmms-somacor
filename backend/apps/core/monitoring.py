"""
Monitoring and alerting utilities
"""
import time
from typing import Dict, Any, Optional
from django.core.mail import send_mail
from django.conf import settings
from apps.core.logging_utils import StructuredLogger

logger = StructuredLogger('monitoring')


class MetricsCollector:
    """
    Collects and tracks application metrics
    """
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric
        
        Args:
            metric_name: Name of the metric
            value: Value to increment by
            tags: Optional tags for the metric
        """
        key = self._get_metric_key(metric_name, tags)
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value
        
        logger.debug(
            f"Metric incremented: {metric_name}",
            metric=metric_name,
            value=self.metrics[key],
            tags=tags or {}
        )
    
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric
        
        Args:
            metric_name: Name of the metric
            value: Current value
            tags: Optional tags for the metric
        """
        key = self._get_metric_key(metric_name, tags)
        self.metrics[key] = value
        
        logger.debug(
            f"Metric set: {metric_name}",
            metric=metric_name,
            value=value,
            tags=tags or {}
        )
    
    def timing(self, metric_name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timing metric
        
        Args:
            metric_name: Name of the metric
            duration_ms: Duration in milliseconds
            tags: Optional tags for the metric
        """
        logger.info(
            f"Timing: {metric_name}",
            metric=metric_name,
            duration_ms=duration_ms,
            tags=tags or {}
        )
    
    def _get_metric_key(self, metric_name: str, tags: Optional[Dict[str, str]]) -> str:
        """Generate unique key for metric with tags"""
        if not tags:
            return metric_name
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_name}[{tag_str}]"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()


class AlertManager:
    """
    Manages system alerts and notifications
    """
    
    ALERT_LEVELS = {
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }
    
    def __init__(self):
        self.logger = StructuredLogger('alerts')
    
    def send_alert(
        self,
        level: str,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        notify_admins: bool = False,
        notify_telegram: bool = False
    ):
        """
        Send an alert
        
        Args:
            level: Alert level (INFO, WARNING, ERROR, CRITICAL)
            title: Alert title
            message: Alert message
            details: Additional details
            notify_admins: Whether to notify admins via email
            notify_telegram: Whether to send to Telegram
        """
        alert_data = {
            'level': level,
            'title': title,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        
        # Log alert
        log_method = getattr(self.logger, level.lower())
        log_method(
            f"Alert: {title}",
            **alert_data
        )
        
        # Send email to admins if critical
        if notify_admins or level == 'CRITICAL':
            self._send_email_alert(alert_data)
        
        # Send to Telegram if configured
        if notify_telegram:
            self._send_telegram_alert(alert_data)
    
    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send alert via email"""
        try:
            subject = f"[{alert_data['level']}] {alert_data['title']}"
            message = f"""
            Nivel: {alert_data['level']}
            Título: {alert_data['title']}
            Mensaje: {alert_data['message']}
            
            Detalles:
            {alert_data['details']}
            
            Timestamp: {alert_data['timestamp']}
            """
            
            # Get admin emails from settings
            admin_emails = [admin[1] for admin in getattr(settings, 'ADMINS', [])]
            
            if admin_emails:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=True
                )
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_telegram_alert(self, alert_data: Dict[str, Any]):
        """Send alert via Telegram"""
        try:
            from apps.notifications.telegram_service import TelegramService
            
            message = f"""
🚨 *{alert_data['level']}*: {alert_data['title']}

{alert_data['message']}
            """
            
            # Send to admin channel or users
            # Implementation depends on Telegram service setup
            telegram_service = TelegramService()
            # telegram_service.send_admin_alert(message)
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram alert: {str(e)}")


class PerformanceMonitor:
    """
    Monitors application performance
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
    
    def check_error_rate(self, window_minutes: int = 5):
        """
        Check error rate and alert if too high
        
        Args:
            window_minutes: Time window to check
        """
        # This would typically query logs or metrics database
        # For now, it's a placeholder
        
        error_rate = 0.05  # 5% error rate (example)
        threshold = 0.10  # 10% threshold
        
        if error_rate > threshold:
            self.alerts.send_alert(
                level='ERROR',
                title='High Error Rate Detected',
                message=f'Error rate is {error_rate*100:.1f}% (threshold: {threshold*100:.1f}%)',
                details={
                    'error_rate': error_rate,
                    'threshold': threshold,
                    'window_minutes': window_minutes
                },
                notify_admins=True
            )
    
    def check_response_time(self, avg_response_time_ms: float):
        """
        Check average response time and alert if too slow
        
        Args:
            avg_response_time_ms: Average response time in milliseconds
        """
        threshold = 1000  # 1 second
        
        if avg_response_time_ms > threshold:
            self.alerts.send_alert(
                level='WARNING',
                title='Slow Response Time',
                message=f'Average response time is {avg_response_time_ms:.0f}ms (threshold: {threshold}ms)',
                details={
                    'avg_response_time_ms': avg_response_time_ms,
                    'threshold': threshold
                }
            )
    
    def check_database_connections(self, active_connections: int, max_connections: int):
        """
        Check database connection pool usage
        
        Args:
            active_connections: Number of active connections
            max_connections: Maximum allowed connections
        """
        usage_percent = (active_connections / max_connections) * 100
        threshold = 80  # 80% threshold
        
        if usage_percent > threshold:
            self.alerts.send_alert(
                level='WARNING',
                title='High Database Connection Usage',
                message=f'Database connections at {usage_percent:.1f}% capacity',
                details={
                    'active_connections': active_connections,
                    'max_connections': max_connections,
                    'usage_percent': usage_percent
                }
            )


# Singleton instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
performance_monitor = PerformanceMonitor()
