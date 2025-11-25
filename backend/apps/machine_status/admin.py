from django.contrib import admin
from .models import AssetStatus, AssetStatusHistory


@admin.register(AssetStatus)
class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ['asset', 'status_type', 'odometer_reading', 'fuel_level', 'reported_by', 'reported_at']
    list_filter = ['status_type', 'reported_at', 'asset']
    search_fields = ['asset__name', 'asset__asset_code', 'condition_notes']
    readonly_fields = ['id', 'reported_at']
    date_hierarchy = 'reported_at'
    
    fieldsets = (
        ('Activo', {
            'fields': ('asset', 'status_type')
        }),
        ('Lecturas', {
            'fields': ('odometer_reading', 'fuel_level')
        }),
        ('Detalles', {
            'fields': ('condition_notes', 'location')
        }),
        ('Metadata', {
            'fields': ('id', 'reported_by', 'reported_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssetStatusHistory)
class AssetStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'previous_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['new_status', 'changed_at']
    search_fields = ['asset__name', 'asset__asset_code']
    readonly_fields = ['id', 'changed_at']
    date_hierarchy = 'changed_at'
