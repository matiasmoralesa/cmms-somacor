"""
Admin configuration for predictions app
"""
from django.contrib import admin
from .models import FailurePrediction, Alert


@admin.register(FailurePrediction)
class FailurePredictionAdmin(admin.ModelAdmin):
    list_display = [
        'asset',
        'failure_probability',
        'risk_level',
        'prediction_date',
        'confidence_score',
    ]
    list_filter = ['risk_level', 'prediction_date']
    search_fields = ['asset__name', 'asset__asset_code']
    readonly_fields = ['id', 'prediction_date', 'created_at', 'risk_level']
    date_hierarchy = 'prediction_date'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'alert_type',
        'severity',
        'is_read',
        'is_resolved',
        'created_at',
    ]
    list_filter = ['alert_type', 'severity', 'is_read', 'is_resolved', 'created_at']
    search_fields = ['title', 'message', 'asset__name']
    readonly_fields = ['id', 'created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_resolved']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marcar como leído"

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
    mark_as_resolved.short_description = "Marcar como resuelto"
