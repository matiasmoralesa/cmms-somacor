"""Admin configuration for checklists"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ChecklistTemplate, ChecklistResponse


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'vehicle_type', 'item_count', 'is_system_template', 'response_count']
    list_filter = ['vehicle_type', 'is_system_template']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'vehicle_type', 'description')
        }),
        ('Configuración', {
            'fields': ('items', 'is_system_template', 'passing_score')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return len(obj.items) if obj.items else 0
    item_count.short_description = 'Items'
    
    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = 'Respuestas'
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system_template:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(ChecklistResponse)
class ChecklistResponseAdmin(admin.ModelAdmin):
    list_display = [
        'completed_at', 'template', 'asset', 'operator_name',
        'score_display', 'passed', 'work_order', 'completed_by'
    ]
    list_filter = ['passed', 'template', 'completed_at']
    search_fields = ['operator_name', 'asset__name', 'template__name']
    readonly_fields = [
        'template', 'asset', 'work_order', 'responses', 'score', 'passed',
        'pdf_url', 'signature_url', 'completed_by', 'completed_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('template', 'asset', 'work_order')
        }),
        ('Operador', {
            'fields': ('operator_name', 'shift', 'odometer_reading', 'completed_by')
        }),
        ('Respuestas', {
            'fields': ('responses',)
        }),
        ('Resultados', {
            'fields': ('score', 'passed', 'pdf_url', 'signature_url')
        }),
        ('Metadatos', {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def score_display(self, obj):
        color = 'green' if obj.passed else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/100</span>',
            color, obj.score
        )
    score_display.short_description = 'Puntaje'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
