"""Admin configuration for inventory"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SparePart, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ['movement_type', 'quantity', 'stock_before', 'stock_after', 'performed_by', 'created_at']
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = [
        'part_number', 'name', 'category', 'quantity_display',
        'minimum_stock', 'unit_cost', 'location', 'created_at'
    ]
    list_filter = ['category']
    search_fields = ['part_number', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['compatible_assets']
    inlines = [StockMovementInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('part_number', 'name', 'description', 'category')
        }),
        ('Stock', {
            'fields': ('quantity', 'minimum_stock')
        }),
        ('Costos y Ubicación', {
            'fields': ('unit_cost', 'location', 'supplier')
        }),
        ('Compatibilidad', {
            'fields': ('compatible_assets',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quantity_display(self, obj):
        if obj.is_low_stock():
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {}</span>',
                obj.quantity
            )
        return obj.quantity
    quantity_display.short_description = 'Cantidad'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'spare_part', 'movement_type', 'quantity',
        'stock_before', 'stock_after', 'work_order', 'performed_by'
    ]
    list_filter = ['movement_type', 'created_at']
    search_fields = ['spare_part__name', 'spare_part__part_number', 'notes']
    readonly_fields = [
        'spare_part', 'movement_type', 'quantity', 'work_order',
        'performed_by', 'notes', 'stock_before', 'stock_after', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
