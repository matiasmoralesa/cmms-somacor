import uuid
from django.db import models
from apps.authentication.models import User
from apps.assets.models import Asset, Location


class AssetStatus(models.Model):
    """
    Model for tracking asset/machine status updates.
    OPERADOR can update status for assigned assets.
    ADMIN/SUPERVISOR can update any asset.
    """
    # Status type choices
    STATUS_OPERANDO = 'OPERANDO'
    STATUS_DETENIDA = 'DETENIDA'
    STATUS_EN_MANTENIMIENTO = 'EN_MANTENIMIENTO'
    STATUS_FUERA_DE_SERVICIO = 'FUERA_DE_SERVICIO'
    
    STATUS_CHOICES = [
        (STATUS_OPERANDO, 'Operando'),
        (STATUS_DETENIDA, 'Detenida'),
        (STATUS_EN_MANTENIMIENTO, 'En Mantenimiento'),
        (STATUS_FUERA_DE_SERVICIO, 'Fuera de Servicio'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='status_updates'
    )
    status_type = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name='Tipo de Estado'
    )
    odometer_reading = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Lectura Odómetro/Horómetro'
    )
    fuel_level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nivel de Combustible (%)',
        help_text='Porcentaje de 0 a 100'
    )
    condition_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Notas de Condición'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_status_updates'
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='status_reports'
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'asset_status'
        verbose_name = 'Estado de Activo'
        verbose_name_plural = 'Estados de Activos'
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['asset', '-reported_at']),
            models.Index(fields=['status_type']),
            models.Index(fields=['reported_by']),
        ]
    
    def __str__(self):
        return f"{self.asset.name} - {self.get_status_type_display()} ({self.reported_at.strftime('%Y-%m-%d %H:%M')})"
    
    def clean(self):
        """Validate fuel level is between 0 and 100"""
        from django.core.exceptions import ValidationError
        if self.fuel_level is not None:
            if self.fuel_level < 0 or self.fuel_level > 100:
                raise ValidationError({
                    'fuel_level': 'El nivel de combustible debe estar entre 0 y 100'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Create history record
        if is_new:
            AssetStatusHistory.objects.create(
                asset=self.asset,
                previous_status=None,
                new_status=self.status_type,
                previous_odometer=None,
                new_odometer=self.odometer_reading,
                changed_by=self.reported_by,
                change_reason=self.condition_notes
            )
            
            # Create alert if status is FUERA_DE_SERVICIO
            if self.status_type == self.STATUS_FUERA_DE_SERVICIO:
                self._create_out_of_service_alert()
    
    def _create_out_of_service_alert(self):
        """Create alert when asset goes out of service"""
        from apps.notifications.models import Notification
        from apps.authentication.models import Role
        
        # Get all ADMIN and SUPERVISOR users
        admin_supervisor_users = User.objects.filter(
            role__name__in=[Role.ADMIN, Role.SUPERVISOR],
            is_active=True
        )
        
        # Create notifications
        for user in admin_supervisor_users:
            Notification.objects.create(
                user=user,
                notification_type='ASSET_OUT_OF_SERVICE',
                title=f'Activo Fuera de Servicio: {self.asset.name}',
                message=f'El activo {self.asset.name} ha sido marcado como fuera de servicio por {self.reported_by.get_full_name()}. '
                        f'Notas: {self.condition_notes or "Sin notas"}',
                data={
                    'asset_id': str(self.asset.id),
                    'asset_name': self.asset.name,
                    'status_id': str(self.id),
                    'reported_by': self.reported_by.get_full_name()
                }
            )


class AssetStatusHistory(models.Model):
    """Audit trail for all status changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    previous_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Estado Anterior'
    )
    new_status = models.CharField(
        max_length=50,
        verbose_name='Nuevo Estado'
    )
    previous_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='status_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'asset_status_history'
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['asset', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.asset.name} - {self.new_status} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"
