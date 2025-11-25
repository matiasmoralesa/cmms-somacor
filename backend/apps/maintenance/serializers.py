"""Serializers for maintenance plans"""
from rest_framework import serializers
from .models import MaintenancePlan


class MaintenancePlanSerializer(serializers.ModelSerializer):
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    recurrence_type_display = serializers.CharField(source='get_recurrence_type_display', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_due = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenancePlan
        fields = [
            'id', 'name', 'description', 'asset', 'asset_name',
            'plan_type', 'plan_type_display', 'recurrence_type', 'recurrence_type_display',
            'recurrence_interval', 'next_due_date', 'is_active', 'estimated_duration',
            'is_due', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_is_due(self, obj):
        return obj.is_due()


class MaintenancePlanCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenancePlan
        fields = [
            'name', 'description', 'asset', 'plan_type',
            'recurrence_type', 'recurrence_interval', 'next_due_date',
            'is_active', 'estimated_duration'
        ]
