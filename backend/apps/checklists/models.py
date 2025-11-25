"""Checklist models"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.authentication.models import User
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder


class ChecklistTemplate(models.Model):
    """Checklist Template model - 5 predefined templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    vehicle_type = models.CharField(max_length=50, verbose_name='Tipo de Vehículo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Checklist items stored as JSON
    items = models.JSONField(default=list, verbose_name='Items del Checklist')
    # Structure: [
    #   {
    #     "section": "Motor",
    #     "order": 1,
    #     "question": "Nivel de aceite motor",
    #     "response_type": "yes_no_na",
    #     "required": true,
    #     "observations_allowed": true
    #   }
    # ]
    
    # System template protection
    is_system_template = models.BooleanField(default=False, verbose_name='Plantilla del Sistema')
    passing_score = models.IntegerField(default=80, verbose_name='Puntaje Mínimo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'checklist_templates'
        verbose_name = 'Plantilla de Checklist'
        verbose_name_plural = 'Plantillas de Checklist'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """Validate checklist template"""
        super().clean()
        
        # Prevent modification of system templates
        if self.is_system_template and self.pk:
            original = ChecklistTemplate.objects.get(pk=self.pk)
            if original.is_system_template:
                # Only allow updating description and passing_score
                if self.code != original.code or self.name != original.name or self.vehicle_type != original.vehicle_type:
                    raise ValidationError('No se pueden modificar plantillas del sistema')
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of system templates"""
        if self.is_system_template:
            raise ValidationError('No se pueden eliminar plantillas del sistema')
        super().delete(*args, **kwargs)


class ChecklistResponse(models.Model):
    """Checklist Response model - completed checklists"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ChecklistTemplate,
        on_delete=models.PROTECT,
        related_name='responses',
        verbose_name='Plantilla'
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklists',
        verbose_name='Orden de Trabajo'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name='checklist_responses',
        verbose_name='Activo'
    )
    
    # Responses stored as JSON
    responses = models.JSONField(default=list, verbose_name='Respuestas')
    # Structure: [
    #   {
    #     "item_order": 1,
    #     "response": "yes",
    #     "notes": "Oil level normal",
    #     "photo_url": "gs://bucket/photo.jpg"
    #   }
    # ]
    
    # Scoring
    score = models.IntegerField(verbose_name='Puntaje')
    passed = models.BooleanField(verbose_name='Aprobado')
    
    # PDF generation
    pdf_url = models.URLField(null=True, blank=True, verbose_name='URL del PDF')
    
    # Signature
    signature_url = models.URLField(null=True, blank=True, verbose_name='URL de Firma')
    
    # Completion info
    completed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='completed_checklists',
        verbose_name='Completado por'
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Completado')
    
    # Additional fields
    operator_name = models.CharField(max_length=200, verbose_name='Nombre del Operador')
    shift = models.CharField(max_length=50, blank=True, verbose_name='Turno')
    odometer_reading = models.IntegerField(null=True, blank=True, verbose_name='Kilometraje/Horómetro')
    
    class Meta:
        db_table = 'checklist_responses'
        verbose_name = 'Checklist Completado'
        verbose_name_plural = 'Checklists Completados'
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['asset', '-completed_at']),
            models.Index(fields=['work_order']),
            models.Index(fields=['completed_by']),
        ]
    
    def __str__(self):
        return f"{self.template.code} - {self.asset.name} ({self.completed_at.strftime('%Y-%m-%d')})"
    
    def clean(self):
        """Validate checklist response"""
        super().clean()
        
        # Validate asset vehicle_type matches template
        if self.asset and self.template:
            if self.asset.vehicle_type != self.template.vehicle_type:
                raise ValidationError({
                    'template': f'Esta plantilla es para {self.template.get_vehicle_type_display()}, '
                               f'pero el activo es {self.asset.get_vehicle_type_display()}'
                })
    
    def calculate_score(self):
        """Calculate checklist score"""
        if not self.responses or not self.template.items:
            return 0
        
        total_items = len(self.template.items)
        passed_items = 0
        
        for response in self.responses:
            # Count "yes" responses as passed
            if response.get('response') == 'yes':
                passed_items += 1
        
        if total_items == 0:
            return 0
        
        return int((passed_items / total_items) * 100)
    
    def save(self, *args, **kwargs):
        # Calculate score
        self.score = self.calculate_score()
        self.passed = self.score >= self.template.passing_score
        
        # Validate
        self.full_clean()
        
        super().save(*args, **kwargs)
