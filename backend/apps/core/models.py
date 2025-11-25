"""
Core models for system-wide functionality
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Webhook(models.Model):
    """Webhook subscription for external integrations"""
    
    EVENT_CHOICES = [
        ('work_order.created', 'Orden de Trabajo Creada'),
        ('work_order.updated', 'Orden de Trabajo Actualizada'),
        ('work_order.completed', 'Orden de Trabajo Completada'),
        ('work_order.assigned', 'Orden de Trabajo Asignada'),
        ('asset.created', 'Activo Creado'),
        ('asset.updated', 'Activo Actualizado'),
        ('alert.created', 'Alerta Creada'),
        ('prediction.high_risk', 'Predicción de Alto Riesgo'),
        ('maintenance.due', 'Mantenimiento Vencido'),
        ('inventory.low_stock', 'Stock Bajo'),
        ('checklist.completed', 'Checklist Completado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    url = models.URLField(help_text='URL donde se enviarán las notificaciones')
    events = models.JSONField(
        default=list,
        help_text='Lista de eventos a los que está suscrito'
    )
    secret = models.CharField(
        max_length=64,
        help_text='Secret para firmar los payloads (HMAC SHA256)'
    )
    is_active = models.BooleanField(default=True)
    
    # Retry configuration
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=60)
    
    # Statistics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    last_delivery_at = models.DateTimeField(null=True, blank=True)
    last_delivery_status = models.CharField(max_length=20, blank=True)
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.url}"


class WebhookDelivery(models.Model):
    """Log of webhook delivery attempts"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('success', 'Exitoso'),
        ('failed', 'Fallido'),
        ('retrying', 'Reintentando'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    
    # Delivery info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    http_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Retry info
    attempt_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True, help_text='Duración en milisegundos')
    
    class Meta:
        verbose_name = 'Webhook Delivery'
        verbose_name_plural = 'Webhook Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['status', 'next_retry_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook.name} - {self.event_type} - {self.status}"
