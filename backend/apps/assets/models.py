"""
Asset/Vehicle models for CMMS system
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.authentication.models import User


class Location(models.Model):
    """Physical location for assets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    coordinates = models.JSONField(blank=True, null=True, help_text='{"lat": -33.4489, "lng": -70.6693}')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def can_be_deleted(self):
        """Check if location can be deleted (no assets reference it)"""
        return not self.assets.exists()


class Asset(models.Model):
    """
    Asset/Vehicle model with 5 predefined vehicle types
    """
    # Vehicle types (5 predefined)
    CAMION_SUPERSUCKER = 'CAMION_SUPERSUCKER'
    CAMIONETA_MDO = 'CAMIONETA_MDO'
    RETROEXCAVADORA_MDO = 'RETROEXCAVADORA_MDO'
    CARGADOR_FRONTAL_MDO = 'CARGADOR_FRONTAL_MDO'
    MINICARGADOR_MDO = 'MINICARGADOR_MDO'
    
    VEHICLE_TYPE_CHOICES = [
        (CAMION_SUPERSUCKER, 'Camión Supersucker'),
        (CAMIONETA_MDO, 'Camioneta MDO'),
        (RETROEXCAVADORA_MDO, 'Retroexcavadora MDO'),
        (CARGADOR_FRONTAL_MDO, 'Cargador Frontal MDO'),
        (MINICARGADOR_MDO, 'Minicargador MDO'),
    ]
    
    # Status choices
    STATUS_OPERATIONAL = 'OPERATIONAL'
    STATUS_DOWN = 'DOWN'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_RETIRED = 'RETIRED'
    
    STATUS_CHOICES = [
        (STATUS_OPERATIONAL, 'Operativo'),
        (STATUS_DOWN, 'Fuera de Servicio'),
        (STATUS_MAINTENANCE, 'En Mantenimiento'),
        (STATUS_RETIRED, 'Retirado'),
    ]
    
    # Criticality choices
    CRITICALITY_LOW = 'LOW'
    CRITICALITY_MEDIUM = 'MEDIUM'
    CRITICALITY_HIGH = 'HIGH'
    CRITICALITY_CRITICAL = 'CRITICAL'
    
    CRITICALITY_CHOICES = [
        (CRITICALITY_LOW, 'Baja'),
        (CRITICALITY_MEDIUM, 'Media'),
        (CRITICALITY_HIGH, 'Alta'),
        (CRITICALITY_CRITICAL, 'Crítica'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    asset_code = models.CharField(max_length=50, unique=True, verbose_name='Código de Activo')
    
    # Vehicle type (restricted to 5 types)
    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_TYPE_CHOICES,
        verbose_name='Tipo de Vehículo'
    )
    
    # Location
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='assets',
        verbose_name='Ubicación'
    )
    
    # Vehicle details
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name='Fabricante')
    model = models.CharField(max_length=100, blank=True, verbose_name='Modelo')
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='Número de Serie')
    license_plate = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Patente'
    )
    
    # Dates
    installation_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Instalación')
    last_maintenance_date = models.DateField(null=True, blank=True, verbose_name='Última Mantención')
    
    # Status and criticality
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPERATIONAL,
        verbose_name='Estado'
    )
    criticality = models.CharField(
        max_length=20,
        choices=CRITICALITY_CHOICES,
        default=CRITICALITY_MEDIUM,
        verbose_name='Criticidad'
    )
    
    # Additional specifications (JSON field for flexibility)
    specifications = models.JSONField(default=dict, blank=True, verbose_name='Especificaciones')
    
    # Soft delete
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assets',
        verbose_name='Creado por'
    )
    
    class Meta:
        db_table = 'assets'
        verbose_name = 'Activo/Vehículo'
        verbose_name_plural = 'Activos/Vehículos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle_type']),
            models.Index(fields=['status']),
            models.Index(fields=['asset_code']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['license_plate']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_vehicle_type_display()})"
    
    def clean(self):
        """Validate asset data"""
        super().clean()
        
        # Validate vehicle type is one of the 5 allowed
        if self.vehicle_type not in dict(self.VEHICLE_TYPE_CHOICES):
            raise ValidationError({
                'vehicle_type': 'Tipo de vehículo inválido'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_checklist_code(self):
        """Get checklist code for this vehicle type"""
        checklist_codes = {
            self.CAMION_SUPERSUCKER: 'SUPERSUCKER-CH01',
            self.CAMIONETA_MDO: 'F-PR-020-CH01',
            self.RETROEXCAVADORA_MDO: 'F-PR-034-CH01',
            self.CARGADOR_FRONTAL_MDO: 'F-PR-037-CH01',
            self.MINICARGADOR_MDO: 'F-PR-040-CH01',
        }
        return checklist_codes.get(self.vehicle_type)


class AssetDocument(models.Model):
    """Documents and photos for assets"""
    DOCUMENT_TYPE_MANUAL = 'MANUAL'
    DOCUMENT_TYPE_PHOTO = 'PHOTO'
    DOCUMENT_TYPE_CERTIFICATE = 'CERTIFICATE'
    DOCUMENT_TYPE_DRAWING = 'DRAWING'
    DOCUMENT_TYPE_OTHER = 'OTHER'
    
    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_TYPE_MANUAL, 'Manual'),
        (DOCUMENT_TYPE_PHOTO, 'Fotografía'),
        (DOCUMENT_TYPE_CERTIFICATE, 'Certificado'),
        (DOCUMENT_TYPE_DRAWING, 'Plano'),
        (DOCUMENT_TYPE_OTHER, 'Otro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Activo'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de Documento'
    )
    file_url = models.URLField(verbose_name='URL del Archivo')  # Cloud Storage URL
    file_name = models.CharField(max_length=255, verbose_name='Nombre del Archivo')
    file_size = models.IntegerField(verbose_name='Tamaño (bytes)')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Subido por'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    
    class Meta:
        db_table = 'asset_documents'
        verbose_name = 'Documento de Activo'
        verbose_name_plural = 'Documentos de Activos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.asset.name}"
