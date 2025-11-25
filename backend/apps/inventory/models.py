"""Inventory models"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.authentication.models import User
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder


class SparePart(models.Model):
    """Spare Part model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    part_number = models.CharField(max_length=100, unique=True, verbose_name='Número de Parte')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.CharField(max_length=100, verbose_name='Categoría')
    
    # Stock
    quantity = models.IntegerField(default=0, verbose_name='Cantidad')
    minimum_stock = models.IntegerField(default=0, verbose_name='Stock Mínimo')
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo Unitario')
    
    # Location
    location = models.CharField(max_length=100, verbose_name='Ubicación en Bodega')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Proveedor')
    
    # Compatible assets
    compatible_assets = models.ManyToManyField(
        Asset,
        blank=True,
        related_name='compatible_spare_parts',
        verbose_name='Activos Compatibles'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'spare_parts'
        verbose_name = 'Repuesto'
        verbose_name_plural = 'Repuestos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['part_number']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.part_number} - {self.name}"
    
    def clean(self):
        """Validate spare part data"""
        super().clean()
        
        if self.quantity < 0:
            raise ValidationError({'quantity': 'La cantidad no puede ser negativa'})
        
        if self.minimum_stock < 0:
            raise ValidationError({'minimum_stock': 'El stock mínimo no puede ser negativo'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_low_stock(self):
        """Check if stock is below minimum"""
        return self.quantity <= self.minimum_stock
    
    def stock_percentage(self):
        """Get stock percentage relative to minimum"""
        if self.minimum_stock == 0:
            return 100
        return (self.quantity / self.minimum_stock) * 100


class StockMovement(models.Model):
    """Stock Movement model for audit trail"""
    MOVEMENT_IN = 'IN'
    MOVEMENT_OUT = 'OUT'
    MOVEMENT_ADJUSTMENT = 'ADJUSTMENT'
    
    MOVEMENT_TYPE_CHOICES = [
        (MOVEMENT_IN, 'Entrada'),
        (MOVEMENT_OUT, 'Salida'),
        (MOVEMENT_ADJUSTMENT, 'Ajuste'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spare_part = models.ForeignKey(
        SparePart,
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name='Repuesto'
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name='Tipo de Movimiento'
    )
    quantity = models.IntegerField(verbose_name='Cantidad')
    
    # Optional work order reference
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
        verbose_name='Orden de Trabajo'
    )
    
    # User who performed the movement
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Realizado por'
    )
    
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    # Stock before and after
    stock_before = models.IntegerField(verbose_name='Stock Anterior')
    stock_after = models.IntegerField(verbose_name='Stock Posterior')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    
    class Meta:
        db_table = 'stock_movements'
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['spare_part', '-created_at']),
            models.Index(fields=['work_order']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.spare_part.name} ({self.quantity})"
    
    def clean(self):
        """Validate stock movement"""
        super().clean()
        
        if self.quantity == 0:
            raise ValidationError({'quantity': 'La cantidad debe ser diferente de 0'})
        
        # For OUT movements, check if there's enough stock
        if self.movement_type == self.MOVEMENT_OUT:
            if abs(self.quantity) > self.spare_part.quantity:
                raise ValidationError({
                    'quantity': f'Stock insuficiente. Disponible: {self.spare_part.quantity}'
                })
    
    def save(self, *args, **kwargs):
        # Store stock before
        self.stock_before = self.spare_part.quantity
        
        # Calculate new stock
        if self.movement_type == self.MOVEMENT_IN:
            new_quantity = self.spare_part.quantity + abs(self.quantity)
        elif self.movement_type == self.MOVEMENT_OUT:
            new_quantity = self.spare_part.quantity - abs(self.quantity)
        else:  # ADJUSTMENT
            new_quantity = self.quantity
        
        self.stock_after = new_quantity
        
        # Validate
        self.full_clean()
        
        # Save movement
        super().save(*args, **kwargs)
        
        # Update spare part quantity
        self.spare_part.quantity = new_quantity
        self.spare_part.save()
