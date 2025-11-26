"""
Models for image processing and analysis.
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.authentication.models import User
from apps.assets.models import Asset
from apps.checklists.models import ChecklistResponse
from apps.work_orders.models import WorkOrder


class InspectionPhoto(models.Model):
    """
    Photo taken during inspection with metadata and processing status.
    Stores original image in Cloud Storage and tracks analysis progress.
    """
    # Processing status choices
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PROCESSING, 'Procesando'),
        (STATUS_COMPLETED, 'Completado'),
        (STATUS_FAILED, 'Fallido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='inspection_photos',
        verbose_name='Activo'
    )
    checklist_response = models.ForeignKey(
        ChecklistResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name='Checklist'
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name='Orden de Trabajo'
    )
    
    # Image data
    original_url = models.URLField(verbose_name='URL Original')
    thumbnail_url = models.URLField(blank=True, verbose_name='URL Miniatura')
    file_size = models.IntegerField(verbose_name='Tamaño (bytes)')
    width = models.IntegerField(verbose_name='Ancho')
    height = models.IntegerField(verbose_name='Alto')
    format = models.CharField(max_length=10, verbose_name='Formato')  # JPEG, PNG, WEBP
    
    # Metadata from EXIF
    captured_at = models.DateTimeField(verbose_name='Fecha de Captura')
    gps_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud GPS'
    )
    gps_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud GPS'
    )
    gps_altitude = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Altitud GPS (m)'
    )
    compass_heading = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Orientación (grados)'
    )
    device_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Info del Dispositivo'
    )
    # Structure: {"make": "Apple", "model": "iPhone 12", "os": "iOS 15"}
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado de Procesamiento'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Procesamiento'
    )
    processing_error = models.TextField(
        blank=True,
        verbose_name='Error de Procesamiento'
    )
    
    # User info
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_photos',
        verbose_name='Subido por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_photos'
        verbose_name = 'Foto de Inspección'
        verbose_name_plural = 'Fotos de Inspección'
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['asset', '-captured_at']),
            models.Index(fields=['work_order']),
            models.Index(fields=['checklist_response']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return f"Photo {self.id} - {self.asset.name} ({self.captured_at.strftime('%Y-%m-%d %H:%M')})"
    
    def clean(self):
        """Validate inspection photo data"""
        super().clean()
        
        # Validate file size
        max_size = settings.MAX_IMAGE_SIZE_BYTES
        if self.file_size > max_size:
            raise ValidationError({
                'file_size': f'El tamaño del archivo excede el máximo permitido ({settings.MAX_IMAGE_SIZE_MB}MB)'
            })
        
        # Validate format
        if self.format.upper() not in settings.ALLOWED_IMAGE_FORMATS:
            raise ValidationError({
                'format': f'Formato no permitido. Formatos válidos: {", ".join(settings.ALLOWED_IMAGE_FORMATS)}'
            })
    
    def has_gps_data(self):
        """Check if photo has GPS coordinates"""
        return self.gps_latitude is not None and self.gps_longitude is not None
    
    def get_gps_coordinates(self):
        """Get GPS coordinates as tuple"""
        if self.has_gps_data():
            return (float(self.gps_latitude), float(self.gps_longitude))
        return None


class ImageAnalysisResult(models.Model):
    """
    Results from Vision AI and custom ML model analysis.
    Stores labels, objects, text, and custom model predictions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.OneToOneField(
        InspectionPhoto,
        on_delete=models.CASCADE,
        related_name='analysis_result',
        verbose_name='Foto'
    )
    
    # Vision AI results
    labels = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Etiquetas Detectadas'
    )
    # Structure: [{"description": "Vehicle", "score": 0.95, "topicality": 0.92}]
    
    detected_objects = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Objetos Localizados'
    )
    # Structure: [{"name": "Tire", "score": 0.89, "bounding_box": [...]}]
    
    text_annotations = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Texto Detectado (OCR)'
    )
    # Structure: [{"description": "ABC-1234", "bounding_box": [...]}]
    
    dominant_colors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Colores Dominantes'
    )
    # Structure: [{"red": 255, "green": 0, "blue": 0, "score": 0.8}]
    
    safe_search = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Safe Search'
    )
    # Structure: {"adult": "VERY_UNLIKELY", "violence": "UNLIKELY"}
    
    # Custom ML model results
    anomalies_detected = models.BooleanField(
        default=False,
        verbose_name='Anomalías Detectadas'
    )
    anomaly_confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Confianza de Anomalía'
    )
    damage_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de Daño'
    )
    damage_severity = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Severidad del Daño'
    )
    damage_confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Confianza de Daño'
    )
    
    # Processing metadata
    processing_time_ms = models.IntegerField(
        verbose_name='Tiempo de Procesamiento (ms)'
    )
    model_version = models.CharField(
        max_length=50,
        verbose_name='Versión del Modelo'
    )
    vision_ai_used = models.BooleanField(
        default=True,
        verbose_name='Vision AI Usado'
    )
    
    # Caching
    cached_result = models.BooleanField(
        default=False,
        verbose_name='Resultado en Caché'
    )
    cache_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Caché Expira'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'image_analysis_results'
        verbose_name = 'Resultado de Análisis'
        verbose_name_plural = 'Resultados de Análisis'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['photo']),
            models.Index(fields=['anomalies_detected']),
            models.Index(fields=['damage_type']),
        ]
    
    def __str__(self):
        return f"Analysis for {self.photo.id}"
    
    def has_anomalies(self):
        """Check if anomalies were detected"""
        return self.anomalies_detected and self.anomaly_confidence is not None
    
    def has_damage(self):
        """Check if damage was detected"""
        return bool(self.damage_type) and self.damage_confidence is not None
    
    def get_summary(self):
        """Get human-readable summary of analysis"""
        summary = []
        
        if self.labels:
            top_labels = [label['description'] for label in self.labels[:3]]
            summary.append(f"Detectado: {', '.join(top_labels)}")
        
        if self.has_anomalies():
            summary.append(f"Anomalía detectada ({self.anomaly_confidence:.0%} confianza)")
        
        if self.has_damage():
            summary.append(f"Daño: {self.damage_type} - Severidad: {self.damage_severity}")
        
        if self.text_annotations:
            summary.append(f"Texto encontrado: {len(self.text_annotations)} anotaciones")
        
        return " | ".join(summary) if summary else "Sin resultados significativos"


class VisualAnomaly(models.Model):
    """
    Visual anomaly detected in an inspection photo.
    Includes type, severity, confidence, and bounding box.
    """
    # Anomaly types
    TYPE_CORROSION = 'CORROSION'
    TYPE_CRACK = 'CRACK'
    TYPE_LEAK = 'LEAK'
    TYPE_WEAR = 'WEAR'
    TYPE_DEFORMATION = 'DEFORMATION'
    TYPE_OTHER = 'OTHER'
    
    ANOMALY_TYPE_CHOICES = [
        (TYPE_CORROSION, 'Corrosión'),
        (TYPE_CRACK, 'Grieta'),
        (TYPE_LEAK, 'Fuga'),
        (TYPE_WEAR, 'Desgaste'),
        (TYPE_DEFORMATION, 'Deformación'),
        (TYPE_OTHER, 'Otro'),
    ]
    
    # Severity levels
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, 'Bajo'),
        (SEVERITY_MEDIUM, 'Medio'),
        (SEVERITY_HIGH, 'Alto'),
        (SEVERITY_CRITICAL, 'Crítico'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(
        InspectionPhoto,
        on_delete=models.CASCADE,
        related_name='anomalies',
        verbose_name='Foto'
    )
    analysis_result = models.ForeignKey(
        ImageAnalysisResult,
        on_delete=models.CASCADE,
        related_name='anomalies',
        verbose_name='Resultado de Análisis'
    )
    
    # Anomaly details
    anomaly_type = models.CharField(
        max_length=50,
        choices=ANOMALY_TYPE_CHOICES,
        verbose_name='Tipo de Anomalía'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name='Severidad'
    )
    confidence = models.FloatField(verbose_name='Confianza')
    
    # Location in image (normalized coordinates 0-1)
    bounding_box = models.JSONField(
        verbose_name='Caja Delimitadora'
    )
    # Structure: {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4}
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # User feedback
    confirmed_by_user = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='Confirmado por Usuario'
    )
    user_feedback = models.TextField(
        blank=True,
        verbose_name='Feedback del Usuario'
    )
    feedback_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anomaly_feedbacks',
        verbose_name='Feedback por'
    )
    feedback_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Feedback'
    )
    
    # Actions taken
    work_order_created = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anomalies',
        verbose_name='Orden de Trabajo Creada'
    )
    alert_sent = models.BooleanField(
        default=False,
        verbose_name='Alerta Enviada'
    )
    alert_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Alerta Enviada'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'visual_anomalies'
        verbose_name = 'Anomalía Visual'
        verbose_name_plural = 'Anomalías Visuales'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['photo']),
            models.Index(fields=['anomaly_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['confirmed_by_user']),
        ]
    
    def __str__(self):
        return f"{self.get_anomaly_type_display()} - {self.get_severity_display()} ({self.confidence:.0%})"
    
    def is_critical(self):
        """Check if anomaly is critical"""
        return self.severity == self.SEVERITY_CRITICAL
    
    def needs_work_order(self):
        """Check if anomaly needs a work order"""
        return self.is_critical() and not self.work_order_created


class MeterReading(models.Model):
    """
    Meter reading extracted from photo using OCR.
    Includes validation against historical ranges.
    """
    # Reading types
    TYPE_ODOMETER = 'ODOMETER'
    TYPE_HOUR_METER = 'HOUR_METER'
    TYPE_PRESSURE = 'PRESSURE'
    TYPE_TEMPERATURE = 'TEMPERATURE'
    TYPE_FUEL_LEVEL = 'FUEL_LEVEL'
    TYPE_OTHER = 'OTHER'
    
    READING_TYPE_CHOICES = [
        (TYPE_ODOMETER, 'Odómetro'),
        (TYPE_HOUR_METER, 'Horómetro'),
        (TYPE_PRESSURE, 'Presión'),
        (TYPE_TEMPERATURE, 'Temperatura'),
        (TYPE_FUEL_LEVEL, 'Nivel de Combustible'),
        (TYPE_OTHER, 'Otro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(
        InspectionPhoto,
        on_delete=models.CASCADE,
        related_name='meter_readings',
        verbose_name='Foto'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='meter_readings',
        verbose_name='Activo'
    )
    
    # Reading data
    reading_type = models.CharField(
        max_length=50,
        choices=READING_TYPE_CHOICES,
        verbose_name='Tipo de Lectura'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    unit = models.CharField(
        max_length=20,
        verbose_name='Unidad'
    )
    
    # OCR metadata
    confidence = models.FloatField(verbose_name='Confianza OCR')
    text_detected = models.CharField(
        max_length=100,
        verbose_name='Texto Detectado'
    )
    bounding_box = models.JSONField(
        verbose_name='Caja Delimitadora'
    )
    
    # Validation
    is_valid = models.BooleanField(
        default=True,
        verbose_name='Es Válido'
    )
    is_outlier = models.BooleanField(
        default=False,
        verbose_name='Es Valor Atípico'
    )
    validation_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Validación'
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_readings',
        verbose_name='Validado por'
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Validación'
    )
    
    # Historical context
    previous_reading = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Lectura Anterior'
    )
    expected_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Rango Esperado Mínimo'
    )
    expected_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Rango Esperado Máximo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meter_readings'
        verbose_name = 'Lectura de Medidor'
        verbose_name_plural = 'Lecturas de Medidores'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['reading_type']),
            models.Index(fields=['is_outlier']),
        ]
    
    def __str__(self):
        return f"{self.get_reading_type_display()}: {self.value} {self.unit} - {self.asset.name}"
    
    def is_within_expected_range(self):
        """Check if reading is within expected range"""
        if self.expected_range_min is None or self.expected_range_max is None:
            return True
        return self.expected_range_min <= self.value <= self.expected_range_max


class DamageReport(models.Model):
    """
    Damage report generated from image analysis.
    Links to work orders and maintenance plans.
    """
    # Damage types
    TYPE_CORROSION = 'CORROSION'
    TYPE_MECHANICAL_WEAR = 'MECHANICAL_WEAR'
    TYPE_ELECTRICAL_FAILURE = 'ELECTRICAL_FAILURE'
    TYPE_HYDRAULIC_LEAK = 'HYDRAULIC_LEAK'
    TYPE_STRUCTURAL_CRACK = 'STRUCTURAL_CRACK'
    TYPE_THERMAL_DAMAGE = 'THERMAL_DAMAGE'
    
    DAMAGE_TYPE_CHOICES = [
        (TYPE_CORROSION, 'Corrosión'),
        (TYPE_MECHANICAL_WEAR, 'Desgaste Mecánico'),
        (TYPE_ELECTRICAL_FAILURE, 'Falla Eléctrica'),
        (TYPE_HYDRAULIC_LEAK, 'Fuga Hidráulica'),
        (TYPE_STRUCTURAL_CRACK, 'Grieta Estructural'),
        (TYPE_THERMAL_DAMAGE, 'Daño Térmico'),
    ]
    
    # Severity levels
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, 'Bajo'),
        (SEVERITY_MEDIUM, 'Medio'),
        (SEVERITY_HIGH, 'Alto'),
        (SEVERITY_CRITICAL, 'Crítico'),
    ]
    
    # Status
    STATUS_OPEN = 'OPEN'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CLOSED = 'CLOSED'
    
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Abierto'),
        (STATUS_IN_PROGRESS, 'En Progreso'),
        (STATUS_RESOLVED, 'Resuelto'),
        (STATUS_CLOSED, 'Cerrado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(
        InspectionPhoto,
        on_delete=models.CASCADE,
        related_name='damage_reports',
        verbose_name='Foto'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='damage_reports',
        verbose_name='Activo'
    )
    
    # Damage classification
    damage_type = models.CharField(
        max_length=50,
        choices=DAMAGE_TYPE_CHOICES,
        verbose_name='Tipo de Daño'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name='Severidad'
    )
    confidence = models.FloatField(verbose_name='Confianza')
    
    # Description
    auto_generated_description = models.TextField(
        verbose_name='Descripción Auto-generada'
    )
    user_notes = models.TextField(
        blank=True,
        verbose_name='Notas del Usuario'
    )
    maintenance_recommendation = models.TextField(
        blank=True,
        verbose_name='Recomendación de Mantenimiento'
    )
    
    # Actions
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='damage_reports',
        verbose_name='Orden de Trabajo'
    )
    maintenance_plan_updated = models.BooleanField(
        default=False,
        verbose_name='Plan de Mantenimiento Actualizado'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name='Estado'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Resolución'
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_damage_reports',
        verbose_name='Resuelto por'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'damage_reports'
        verbose_name = 'Reporte de Daño'
        verbose_name_plural = 'Reportes de Daño'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['damage_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_damage_type_display()} - {self.asset.name} ({self.get_severity_display()})"
    
    def is_critical(self):
        """Check if damage is critical"""
        return self.severity == self.SEVERITY_CRITICAL
    
    def needs_immediate_action(self):
        """Check if damage needs immediate action"""
        return self.is_critical() and self.status == self.STATUS_OPEN
