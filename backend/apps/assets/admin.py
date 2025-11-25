"""Admin configuration for assets"""
from django.contrib import admin
from .models import Asset, AssetDocument, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'asset_count', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    def asset_count(self, obj):
        return obj.assets.filter(is_active=True).count()
    asset_count.short_description = 'Activos'


class AssetDocumentInline(admin.TabularInline):
    model = AssetDocument
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    fields = ['document_type', 'file_name', 'file_url', 'description', 'uploaded_by', 'uploaded_at']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_code',
        'name',
        'vehicle_type',
        'license_plate',
        'status',
        'criticality',
        'location',
        'is_active',
        'created_at'
    ]
    list_filter = ['vehicle_type', 'status', 'criticality', 'location', 'is_active']
    search_fields = ['name', 'asset_code', 'serial_number', 'license_plate']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [AssetDocumentInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'asset_code', 'vehicle_type')
        }),
        ('Detalles del Vehículo', {
            'fields': ('manufacturer', 'model', 'serial_number', 'license_plate')
        }),
        ('Ubicación y Estado', {
            'fields': ('location', 'status', 'criticality')
        }),
        ('Fechas', {
            'fields': ('installation_date', 'last_maintenance_date')
        }),
        ('Especificaciones Adicionales', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'asset', 'document_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['file_name', 'asset__name', 'description']
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
