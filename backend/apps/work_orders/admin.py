"""Admin configuration for work orders"""
from django.contrib import admin
from .models import WorkOrder


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [
        'work_order_number', 'title', 'asset', 'work_order_type',
        'priority', 'status', 'assigned_to', 'scheduled_date', 'created_at'
    ]
    list_filter = ['status', 'priority', 'work_order_type', 'created_at']
    search_fields = ['work_order_number', 'title', 'description', 'asset__name']
    readonly_fields = ['work_order_number', 'created_by', 'created_at', 'updated_at', 'started_at', 'completed_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('work_order_number', 'title', 'description', 'asset')
        }),
        ('Clasificación', {
            'fields': ('work_order_type', 'priority', 'status')
        }),
        ('Asignación', {
            'fields': ('assigned_to', 'scheduled_date')
        }),
        ('Horas', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Completado', {
            'fields': ('completion_notes', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
