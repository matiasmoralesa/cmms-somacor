"""
Configuration and Master Data Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()


class BaseConfigModel(models.Model):
    """Base model for configuration data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System records cannot be deleted")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')
    
    class Meta:
        abstract = True
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of system records and records in use"""
        if self.is_system:
            raise ValidationError(f"Cannot delete system {self._meta.verbose_name}: {self.name}")
        
        # Check if record is referenced
        if self._is_referenced():
            raise ValidationError(f"Cannot delete {self._meta.verbose_name} '{self.name}' because it is in use")
        
        super().delete(*args, **kwargs)
    
    def _is_referenced(self):
        """Override in subclasses to check if record is referenced"""
        return False


class AssetCategory(BaseConfigModel):
    """Asset categories for classification"""
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
    
    def _is_referenced(self):
        """Check if category is used by any assets"""
        from apps.assets.models import Asset
        return Asset.objects.filter(category=self).exists()


class Location(BaseConfigModel):
    """Physical locations for assets"""
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Chile')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
    
    def _is_referenced(self):
        """Check if location is used by any assets"""
        from apps.assets.models import Asset
        return Asset.objects.filter(location=self).exists()


class Priority(BaseConfigModel):
    """Priority levels for work orders"""
    level = models.IntegerField(unique=True, help_text="Priority level (1=highest)")
    color = models.CharField(max_length=7, default='#808080', help_text="Hex color code")
    response_time_hours = models.IntegerField(null=True, blank=True, help_text="Expected response time in hours")
    
    class Meta:
        verbose_name = 'Priority'
        verbose_name_plural = 'Priorities'
        ordering = ['level']
    
    def _is_referenced(self):
        """Check if priority is used by any work orders"""
        from apps.work_orders.models import WorkOrder
        return WorkOrder.objects.filter(priority=self.code).exists()


class WorkOrderType(BaseConfigModel):
    """Types of work orders"""
    requires_approval = models.BooleanField(default=False)
    default_priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Work Order Type'
        verbose_name_plural = 'Work Order Types'
    
    def _is_referenced(self):
        """Check if type is used by any work orders"""
        from apps.work_orders.models import WorkOrder
        return WorkOrder.objects.filter(work_order_type=self.code).exists()



class SystemParameter(models.Model):
    """System-wide configuration parameters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('STRING', 'String'),
            ('INTEGER', 'Integer'),
            ('FLOAT', 'Float'),
            ('BOOLEAN', 'Boolean'),
            ('JSON', 'JSON'),
        ],
        default='STRING'
    )
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False, help_text="Hide value in UI")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'System Parameter'
        verbose_name_plural = 'System Parameters'
        ordering = ['key']
    
    def __str__(self):
        return self.key
    
    def get_typed_value(self):
        """Return value converted to appropriate type"""
        if self.data_type == 'INTEGER':
            return int(self.value)
        elif self.data_type == 'FLOAT':
            return float(self.value)
        elif self.data_type == 'BOOLEAN':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.data_type == 'JSON':
            import json
            return json.loads(self.value)
        return self.value


class AuditLog(models.Model):
    """Audit trail for configuration changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What changed
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    
    # Action
    action = models.CharField(
        max_length=20,
        choices=[
            ('CREATE', 'Create'),
            ('UPDATE', 'Update'),
            ('DELETE', 'Delete'),
        ]
    )
    
    # Changes
    changes = models.JSONField(default=dict, help_text="Dictionary of field changes")
    
    # Who and when
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log_change(cls, instance, action, user=None, changes=None, request=None):
        """Create an audit log entry"""
        log = cls(
            model_name=instance._meta.label,
            object_id=str(instance.pk),
            object_repr=str(instance),
            action=action,
            changes=changes or {},
            user=user
        )
        
        if request:
            log.ip_address = cls._get_client_ip(request)
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        log.save()
        return log
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
