"""
Structured logging utilities for CMMS system
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """
    Utility class for structured JSON logging
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(self, level: str, message: str, **kwargs):
        """
        Log a structured message
        
        Args:
            level: Log level (info, warning, error, etc.)
            message: Log message
            **kwargs: Additional structured data
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.upper(),
            'message': message,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log('critical', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log('debug', message, **kwargs)


class AuditLogger:
    """
    Specialized logger for audit events
    """
    
    def __init__(self):
        self.logger = StructuredLogger('audit')
    
    def log_action(
        self,
        action: str,
        user_id: Optional[str],
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ):
        """
        Log an audit event
        
        Args:
            action: Action performed (create, update, delete, etc.)
            user_id: ID of user performing action
            resource_type: Type of resource (asset, work_order, etc.)
            resource_id: ID of resource
            details: Additional details about the action
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action was successful
        """
        self.logger.info(
            f"Audit: {action} {resource_type}",
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )


class PerformanceLogger:
    """
    Logger for performance metrics
    """
    
    def __init__(self):
        self.logger = StructuredLogger('performance')
    
    def log_request(
        self,
        method: str,
        path: str,
        duration_ms: float,
        status_code: int,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log API request performance
        
        Args:
            method: HTTP method
            path: Request path
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
            user_id: ID of authenticated user
            request_id: Unique request ID
        """
        level = 'warning' if duration_ms > 1000 else 'info'
        
        log_method = getattr(self.logger, level)
        log_method(
            f"Request: {method} {path}",
            method=method,
            path=path,
            duration_ms=duration_ms,
            status_code=status_code,
            user_id=user_id,
            request_id=request_id,
            slow_request=duration_ms > 1000
        )
    
    def log_query(
        self,
        query: str,
        duration_ms: float,
        rows_affected: int = 0
    ):
        """
        Log database query performance
        
        Args:
            query: SQL query (sanitized)
            duration_ms: Query duration in milliseconds
            rows_affected: Number of rows affected
        """
        level = 'warning' if duration_ms > 100 else 'debug'
        
        log_method = getattr(self.logger, level)
        log_method(
            "Database query",
            query=query[:200],  # Truncate long queries
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            slow_query=duration_ms > 100
        )


class SecurityLogger:
    """
    Logger for security events
    """
    
    def __init__(self):
        self.logger = StructuredLogger('security')
    
    def log_authentication_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str] = None
    ):
        """
        Log authentication attempt
        
        Args:
            email: User email
            success: Whether authentication was successful
            ip_address: Client IP
            user_agent: Client user agent
            failure_reason: Reason for failure (if applicable)
        """
        level = 'info' if success else 'warning'
        
        log_method = getattr(self.logger, level)
        log_method(
            f"Authentication {'successful' if success else 'failed'}: {email}",
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
    
    def log_authorization_failure(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str
    ):
        """
        Log authorization failure
        
        Args:
            user_id: ID of user attempting action
            resource_type: Type of resource
            resource_id: ID of resource
            action: Action attempted
            ip_address: Client IP
        """
        self.logger.warning(
            f"Authorization failed: {user_id} attempted {action} on {resource_type}",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        ip_address: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log suspicious activity
        
        Args:
            activity_type: Type of suspicious activity
            description: Description of activity
            ip_address: Client IP
            user_id: ID of user (if authenticated)
            details: Additional details
        """
        self.logger.warning(
            f"Suspicious activity: {activity_type}",
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_id=user_id,
            details=details or {}
        )


class BusinessLogger:
    """
    Logger for business events
    """
    
    def __init__(self):
        self.logger = StructuredLogger('business')
    
    def log_work_order_created(
        self,
        work_order_id: str,
        asset_id: str,
        assigned_to: Optional[str],
        priority: str,
        created_by: str
    ):
        """Log work order creation"""
        self.logger.info(
            "Work order created",
            event_type='work_order_created',
            work_order_id=work_order_id,
            asset_id=asset_id,
            assigned_to=assigned_to,
            priority=priority,
            created_by=created_by
        )
    
    def log_work_order_completed(
        self,
        work_order_id: str,
        asset_id: str,
        completed_by: str,
        actual_hours: float,
        completion_notes: str
    ):
        """Log work order completion"""
        self.logger.info(
            "Work order completed",
            event_type='work_order_completed',
            work_order_id=work_order_id,
            asset_id=asset_id,
            completed_by=completed_by,
            actual_hours=actual_hours,
            has_notes=bool(completion_notes)
        )
    
    def log_prediction_high_risk(
        self,
        asset_id: str,
        failure_probability: float,
        predicted_failure_date: str,
        model_version: str
    ):
        """Log high-risk prediction"""
        self.logger.warning(
            "High-risk failure prediction",
            event_type='prediction_high_risk',
            asset_id=asset_id,
            failure_probability=failure_probability,
            predicted_failure_date=predicted_failure_date,
            model_version=model_version
        )
    
    def log_inventory_low_stock(
        self,
        spare_part_id: str,
        part_number: str,
        current_quantity: int,
        minimum_stock: int
    ):
        """Log low stock alert"""
        self.logger.warning(
            "Low stock alert",
            event_type='inventory_low_stock',
            spare_part_id=spare_part_id,
            part_number=part_number,
            current_quantity=current_quantity,
            minimum_stock=minimum_stock
        )


# Singleton instances
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()
