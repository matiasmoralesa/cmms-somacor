"""Maintenance Plan models"""
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.assets.models import Asset


class MaintenancePlan(models.Model):
    """Maintenance Plan model"""
    # Plan types
    TYPE_PREVENTIVE = 'PREVENTIVE'
    TYPE_PREDICTIVE = 'PREDICTIVE'
    
    TYPE_CHOICES = [
        (TYPE_PREVENTIVE, 'Preventivo'),
        (TYPE_PREDICTIVE, 'Predictivo'),
    ]
    
    # Recurrence types
    RECURRENCE_DAILY = 'DAILY'
    RECURRENCE_WEEKLY = 'WEEKLY'
    RECURRENCE_MONTHLY = 'MONTHLY'
    RECURRENCE_CUSTOM = 'CUSTOM'
    
    RECURRENCE_CHOICES = [
        (RECURRENCE_DAILY, 'Diario'),
        (RECURRENCE_WEEKLY, 'Semanal'),
        (RECURRENCE_MONTHLY, 'Mensual'),
        (RECURRENCE_CUSTOM, 'Personalizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_plans')
    plan_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES)
    recurrence_interval = models.IntegerField(default=1)
    next_due_date = models.DateField()
    
    is_active = models.BooleanField(default=True)
    estimated_duration = models.IntegerField(help_text='Duración estimada en minutos')
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_maintenance_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_plans'
        verbose_name = 'Plan de Mantenimiento'
        verbose_name_plural = 'Planes de Mantenimiento'
        ordering = ['next_due_date']
    
    def __str__(self):
        return f"{self.name} - {self.asset.name}"
    
    def calculate_next_due_date(self):
        """Calculate next due date based on recurrence"""
        if self.recurrence_type == self.RECURRENCE_DAILY:
            return self.next_due_date + timedelta(days=self.recurrence_interval)
        elif self.recurrence_type == self.RECURRENCE_WEEKLY:
            return self.next_due_date + timedelta(weeks=self.recurrence_interval)
        elif self.recurrence_type == self.RECURRENCE_MONTHLY:
            return self.next_due_date + timedelta(days=30 * self.recurrence_interval)
        return self.next_due_date
    
    def is_due(self):
        """Check if maintenance is due"""
        return self.next_due_date <= timezone.now().date()
