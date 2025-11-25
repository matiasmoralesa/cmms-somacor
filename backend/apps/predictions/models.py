"""
Prediction models for ML-based failure prediction
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class FailurePrediction(models.Model):
    """
    Model for storing ML predictions of asset failures
    """
    RISK_LEVELS = [
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    prediction_date = models.DateTimeField(auto_now_add=True)
    failure_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Probability of failure (0-100%)"
    )
    predicted_failure_date = models.DateField(null=True, blank=True)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Model confidence score (0-100%)"
    )
    model_version = models.CharField(max_length=50, default='1.0.0')
    input_features = models.JSONField(
        default=dict,
        help_text="Features used for prediction"
    )
    recommendations = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVELS,
        default='LOW'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['asset', '-prediction_date']),
            models.Index(fields=['risk_level']),
        ]

    def __str__(self):
        return f"Prediction for {self.asset.name} - {self.failure_probability}%"

    def save(self, *args, **kwargs):
        # Auto-calculate risk level based on probability
        if self.failure_probability >= 70:
            self.risk_level = 'CRITICAL'
        elif self.failure_probability >= 50:
            self.risk_level = 'HIGH'
        elif self.failure_probability >= 30:
            self.risk_level = 'MEDIUM'
        else:
            self.risk_level = 'LOW'
        super().save(*args, **kwargs)


class Alert(models.Model):
    """
    Model for system alerts and notifications
    """
    ALERT_TYPES = [
        ('PREDICTION', 'Predicción de Falla'),
        ('LOW_STOCK', 'Stock Bajo'),
        ('OVERDUE_MAINTENANCE', 'Mantenimiento Vencido'),
        ('SYSTEM', 'Sistema'),
    ]

    SEVERITY_LEVELS = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Crítico'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    prediction = models.ForeignKey(
        FailurePrediction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', '-created_at']),
            models.Index(fields=['severity', 'is_resolved']),
            models.Index(fields=['is_read', 'is_resolved']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"

    def mark_as_read(self):
        """Mark alert as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])

    def resolve(self, user):
        """Resolve alert"""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save(update_fields=['is_resolved', 'resolved_by', 'resolved_at'])
