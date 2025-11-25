"""Work Order models"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.authentication.models import User
from apps.assets.models import Asset


class WorkOrder(models.Model):
    """Work Order model"""
    # Work order types
    TYPE_CORRECTIVE = 'CORRECTIVE'
    TYPE_PREVENTIVE = 'PREVENTIVE'
    TYPE_PREDICTIVE = 'PREDICTIVE'
    TYPE_INSPECTION = 'INSPECTION'
    
    TYPE_CHOICES = [
        (TYPE_CORRECTIVE, 'Correctivo'),
        (TYPE_PREVENTIVE, 'Preventivo'),
        (TYPE_PREDICTIVE, 'Predictivo'),
        (TYPE_INSPECTION, 'Inspección'),
    ]
    
    # Priority levels
    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_URGENT = 'URGENT'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Baja'),
        (PRIORITY_MEDIUM, 'Media'),
        (PRIORITY_HIGH, 'Alta'),
        (PRIORITY_URGENT, 'Urgente'),
    ]
    
    # Status
    STATUS_PENDING = 'PENDING'
    STATUS_ASSIGNED = 'ASSIGNED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_ASSIGNED, 'Asignada'),
        (STATUS_IN_PROGRESS, 'En Progreso'),
        (STATUS_COMPLETED, 'Completada'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_number = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,  # Don't delete work orders when asset is deleted
        null=True,  # Allow work orders without assets
        blank=True,  # Allow empty in forms
        related_name='work_orders'
    )
    work_order_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders'
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_work_orders')
    
    scheduled_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'work_orders'
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Órdenes de Trabajo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['work_order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.work_order_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.work_order_number:
            # Generate work order number
            from django.utils import timezone
            now = timezone.now()
            prefix = f"WO-{now.year}{now.month:02d}"
            last_wo = WorkOrder.objects.filter(
                work_order_number__startswith=prefix
            ).order_by('-work_order_number').first()
            
            if last_wo:
                last_num = int(last_wo.work_order_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.work_order_number = f"{prefix}-{new_num:04d}"
        
        super().save(*args, **kwargs)
    
    def has_asset(self):
        """Check if work order has an asset assigned"""
        return self.asset is not None
    
    def get_asset_display(self):
        """Get asset display name"""
        if self.asset:
            return f"{self.asset.name} ({self.asset.asset_code})"
        return "Sin equipo asignado"
    
    def clean(self):
        """Validate work order data"""
        super().clean()
        
        # Log warning if asset is null (for monitoring purposes)
        if not self.asset:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Work order {self.work_order_number or 'NEW'} created without asset. "
                f"Type: {self.work_order_type}, Created by: {self.created_by}"
            )
        
        # Validate completion requires notes and hours
        if self.status == self.STATUS_COMPLETED:
            if not self.completion_notes:
                raise ValidationError({'completion_notes': 'Las notas de completado son requeridas'})
            if not self.actual_hours:
                raise ValidationError({'actual_hours': 'Las horas trabajadas son requeridas'})
